#!/usr/bin/env python3
"""仮説検証Wiki のレコードモデル層（frontmatter/履歴/log のパーサと Project）。

hwlint.py（lint）・gen_views.py（ビュー生成）・check_testcard_immutable.py（不変チェック）が
共有する「レコードの読み取り」だけをここに集約する。lint と view 生成が同じモデルを使えるよう、
従来 hwlint.py に同居していたモデル層をここへ抽出した（linter へのモデル依存＝密結合の解消）。

- 語彙(enum)・型・関係・状態機械の定義は ontology.yaml が唯一の正本。ここには再定義しない。
- 値は「素の文字列」契約で返す（下流は文字列前提で .isdigit()/parse_id_array を使う）。
"""
import re
import sys
from functools import cached_property
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent))
from ontology import (  # noqa: E402
    ID_RE, STAGE_FOCUS, IMPORTANCE_FOCUS, IMPORTANCE_OTHER,
    ENTITY_INFIXES, RECORD_DIRS, PROVENANCE, FICTIONAL_MARKERS,
    ATTACHMENTS, ATTACHMENT_SUFFIXES, ATTACHMENT_DIRS,
    DATA_FIELD, DATA_SIMULATED, IMMUTABLE,
)

HISTORY_HEADER = "## 確信度履歴"
# テストカード節は次の `##` 見出しの手前まで（旧形式の `## 学習カード` はその特殊形）。
# 終端を `## 学習カード` に限っていた頃は、学習カードが LEARN に分離された現行モデルで
# 終端に到達せず本文末尾までを飲み込んでいた（凍結範囲が過剰に広がる原因だった）。
TESTCARD_RE = re.compile(r"## テストカード.*?(?=^## |\Z)", re.DOTALL | re.MULTILINE)


def parse_frontmatter(text: str) -> dict:
    """frontmatter（--- で囲まれた YAML ブロック）を dict で返す。

    値は従来どおり「素の文字列」契約で返す（下流は文字列前提で .isdigit()/parse_id_array を使う）。
    yaml.BaseLoader を使うことで、引用符内コロン・複数行値・コメントを正しく扱いつつ、
    型強制（int 化・真偽値化・日付化・いわゆる Norway 問題）を避けて元の文字列表現を保つ。
    空値（None）は ""、配列は "[a, b]" の文字列に正規化して契約を維持する。
    パースできない frontmatter は空 dict を返す（従来同様、寛容に扱う）。
    """
    m = re.match(r"^---\n(.*?)\n---(?:\n|$)", text, re.DOTALL)
    if not m:
        return {}
    try:
        data = yaml.load(m.group(1), Loader=yaml.BaseLoader)
    except yaml.YAMLError:
        return {}
    if not isinstance(data, dict):
        return {}
    fm = {}
    for key, value in data.items():
        if value is None:
            fm[str(key)] = ""
        elif isinstance(value, list):
            fm[str(key)] = "[" + ", ".join(str(v) for v in value) + "]"
        else:
            fm[str(key)] = str(value)
    return fm


def parse_id_array(value: str) -> list:
    return [x.strip() for x in value.strip("[]").split(",") if x.strip()]


def struct_field(text: str, key: str) -> list:
    """構造化フィールド（配列 of マッピング）を**入れ子を保ったまま**読む。

    parse_frontmatter は「素の文字列」契約なので、入れ子は str() に潰れて読めない。判定(judgments)・
    成功基準(success-criteria)・実測(measurements) のように「1レコードに複数行・行の中に構造」がある
    フィールドはこちらで読む（宣言の正本は ontology.yaml の structured-fields 節）。

    BaseLoader を使うので葉は全部 str（数値の型強制を避ける＝frontmatter 全体の契約と揃える）。
    **形の誤りは落とさずそのまま返す**（dict でない行も含める）。捨ててしまうと lint が
    「書いたのに無視された行」を報告できず、書き損じが黙って消える。
    """
    m = re.match(r"^---\n(.*?)\n---(?:\n|$)", text, re.DOTALL)
    if not m:
        return []
    try:
        data = yaml.load(m.group(1), Loader=yaml.BaseLoader)
    except yaml.YAMLError:
        return []
    if not isinstance(data, dict):
        return []
    value = data.get(key)
    if value is None:
        return []
    return value if isinstance(value, list) else [value]


def as_number(value):
    """構造化フィールドの数値キーを float で返す（数値でなければ None）。

    BaseLoader は葉を str で返すので、比較の前にここで一度だけ通す。"""
    try:
        return float(str(value).strip())
    except (TypeError, ValueError):
        return None


def entity_of(stem: str) -> str:
    """レコード stem からエンティティ種別（H/TEST/LEARN/DEC）を返す。該当なしは空。

    種別の一覧は ontology.yaml の entities が正本（ENTITY_INFIXES 経由。ここに再定義しない）。"""
    for infix in ENTITY_INFIXES:
        if f"-{infix}-" in stem:
            return infix
    return ""


def attachment_of(stem: str) -> str:
    """付随物のステムから種別（SCRIPT 等）を返す。該当なしは空。

    識別は suffix でおこなう（付随物は独自のID体系を持たないので ID_RE は使えない）。
    種別・suffix の正本は ontology.yaml の attachments。"""
    for suffix, name in ATTACHMENT_SUFFIXES.items():
        if stem.endswith(suffix):
            return name
    return ""


def node_kind(stem: str) -> str:
    """ステムからノード種別（エンティティ または 付随物）を返す。該当なしは空。

    **付随物を先に判定する順序が本質的**。`SELF-TEST-006-script` には `-TEST-` が含まれるため
    entity_of は "TEST" という真値を返してしまい、逆順にすると付随物が実験計画として
    検証され（date/stage/riskiest-assumption の欠落 error が湧く）、分離の意味が消える。"""
    return attachment_of(stem) or entity_of(stem)


def source_paths(fm: dict) -> list:
    """frontmatter の出典キー（provenance.field＝sources）を相対パス配列で返す。

    値は parse_frontmatter の契約どおり "[a, b]" 形式の文字列なので parse_id_array を流用する
    （ID でなくパスだが、カンマ区切り配列の解析としては同一）。"""
    return parse_id_array(fm.get(PROVENANCE.field, ""))


def strip_frontmatter(text: str) -> str:
    return re.sub(r"^---\n.*?\n---\n", "", text, count=1, flags=re.DOTALL)


def strip_comments(text: str) -> str:
    """HTMLコメント（<!-- ... -->）を除去する。コメント内の例示 wikilink は
    Obsidian でもグラフ辺を作らないため、リンク検査の対象から外す。"""
    return re.sub(r"<!--.*?-->", "", text, flags=re.DOTALL)


def testcard(text: str) -> str:
    """TEST 本文からテストカード節（## テストカード〜次の ## 見出しの手前）を逐語抽出する。"""
    m = TESTCARD_RE.search(text)
    return m.group(0) if m else ""


def card_section(section: str, label: str):
    """テストカードの1項目（例 `成功基準`）の中身を**逐語**抽出する。無ければ None。

    見出し形式（`### 成功基準`）と箇条書き形式（`- **成功基準**（開始前に確定）: …`）の
    両方に対応する。表示都合の整形（表落とし・空白畳み）は呼び手（gen_views）の責務なので
    ここではしない — ビュー生成と不変チェックが同じ抽出を共有できるようにするため。

    節はカードの末尾まで伸びうる（markdown には節の終端記号が無い）。したがって最後の節の
    直後への追記はその節への変更として読める。リンク等は雛形どおり `## テストカード` の
    手前に置くこと。"""
    m = re.search(rf"^###\s*{label}[^\n]*\n(.*?)(?=\n##|\Z)", section, re.DOTALL | re.MULTILINE)
    if not m:
        # 箇条書き形式。太字の内外どちらの接尾辞（**方法**: / **成功基準**（開始前に確定）:）にも対応。
        m = re.search(rf"^-\s*\*\*{label}[^*\n]*\*\*[^:：\n]*[:：]\s*(.*?)(?=\n-\s*\*\*|\n###|\n##|\Z)",
                      section, re.DOTALL | re.MULTILINE)
    return m.group(1) if m else None


def frozen_parts(text: str):
    """TEST のうち実施後に凍結する部分（`ontology.yaml` の `entities.TEST.immutable` 宣言）を返す。

    `{節名: 逐語ブロック, frontmatterキー: 値}` の dict。宣言された節が本文から1つも取れなければ
    None を返し、呼び手（check_testcard_immutable）がテストカード全体比較へフォールバックできるようにする
    （雛形逸脱で保護が静かに外れるのを避ける＝フェイルクローズ）。"""
    spec = IMMUTABLE.get("TEST")
    if not spec:
        return None
    card = strip_comments(testcard(text))
    parts = {}
    for name in spec.sections:
        block = card_section(card, name)
        if block is None:
            return None
        parts[name] = block.strip()
    fm = parse_frontmatter(text)
    for key in spec.fields:
        parts[key] = fm.get(key, "").strip()
    return parts


def parse_history(body: str) -> list:
    rows, in_section = [], False
    for line in body.splitlines():
        if line.startswith("## "):
            in_section = line.strip() == HISTORY_HEADER
            continue
        if in_section and line.lstrip().startswith("|"):
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            if len(cells) >= 5 and re.match(r"\d{4}-\d{2}-\d{2}$", cells[0]):
                rows.append({"date": cells[0], "confidence": cells[1],
                             "status": cells[2], "reason": cells[3], "activity": cells[4]})
    return rows


def referenced_ids(project, field, infix=None, where=None) -> set:
    """`field`（frontmatter の関係キー）で指されている終点IDの集合を返す。

    infix を渡すと始点レコード種別（例 "-TEST-"）で、where(fm)->bool を渡すと始点 frontmatter で
    さらに絞る。関係グラフの入次数（被参照）を「有無」で見る用途の共有ヘルパ。"""
    out = set()
    for stem, (_, fm, _) in project.records.items():
        if infix and infix not in stem:
            continue
        if where and not where(fm):
            continue
        out.update(parse_id_array(fm.get(field, "")))
    return out


def fictional_source(project, fm) -> str:
    """出典のうち、冒頭に架空マーカーを宣言している最初の生データの相対パス（無ければ空）。

    `sources/README.md` は生データ冒頭への架空宣言を要求している。その宣言を実際に読む
    （不変層の一次情報なので、レコード側の宣言では上書きさせない）。"""
    for rel in source_paths(fm):
        if any(m in project.source_header(rel) for m in FICTIONAL_MARKERS):
            return rel
    return ""


def fictional_reason(project, stem) -> str:
    """TEST/LEARN 1件が架空/シミュレーション由来と判定される**理由**を返す。該当なしは空。

    強い順に3経路。返り値は "declared"（frontmatter data の宣言）／"source"（出典冒頭の宣言）／
    "marker"（本文マーカー語のフォールバック）:

    1. `data` の宣言 — **宣言が正本**。「そのレコードが何のデータで作られたか」を著者が明示する。
       `simulated` なら架空、`real` なら**以降の推論を見ない**。
    2. 出典（provenance）冒頭の架空宣言 — 不変層の一次情報。宣言が無いときの推論。
    3. 本文マーカー語 — **`data` 未宣言 かつ 出典を1件も持たない**レコードだけに効く後方互換の
       フォールバック。

    2 も 3 も語の出現を見る推論なので、「何のデータで作られたか」でなく「何について書いてあるか」を
    拾ってしまう（旧 AR-12）。3 は本文が、2 は生データ冒頭が、他レコードの架空性に言及しただけで
    当たる（例: 架空データを論じた揺さぶり監査メモ）。**不変層は書き換えられない**（不変ルール3）ので
    2 の誤検出は出典側では直せない。だから `data: real` は 2 も打ち消せる必要がある。
    宣言と出典が食い違うときは lint の data-provenance が warning で鳴らし、上書きを不可視にしない。"""
    _, fm, body = project.records[stem]
    declared = fm.get(DATA_FIELD, "").strip()
    if declared:
        return "declared" if declared == DATA_SIMULATED else ""
    if fictional_source(project, fm):
        return "source"
    return "marker" if not source_paths(fm) and any(m in body for m in FICTIONAL_MARKERS) else ""


def fictional_activities(project) -> set:
    """架空/シミュレーション由来と判定される TEST/LEARN の stem 集合（lint とビューで共有）。

    判定の正本は fictional_reason（宣言 → 出典 → 本文マーカーの順）。ここはそれを畳むだけ。"""
    return {stem for stem in project.records
            if ("-TEST-" in stem or "-LEARN-" in stem) and fictional_reason(project, stem)}


def importance(fm, stage) -> int:
    """仮説の重要度。手動指定(1-10)が優先。auto は現ステージの重点タイプ=IMPORTANCE_FOCUS・
    それ以外=IMPORTANCE_OTHER（重みの正本は ontology.yaml の importance-weights）。"""
    imp = fm.get("importance", "auto")
    if imp != "auto" and imp.isdigit():
        return int(imp)
    return IMPORTANCE_FOCUS if fm.get("type") in STAGE_FOCUS.get(stage, set()) else IMPORTANCE_OTHER


class Project:
    def __init__(self, root: Path):
        self.root = root
        self.slug = root.name
        self.wiki = root / "wiki"
        self.records = {}
        self.attachments = {}    # 付随物。records と分ける理由は node_kind の docstring を見よ
        self.history = {}   # H レコードの確信度履歴を読込時に1回だけパースしてキャッシュ
        self.stray = []
        for sub in RECORD_DIRS:            # 置き場の正本は ontology.yaml の entities.*.dir
            d = self.wiki / sub
            if not d.is_dir():
                continue
            for p in sorted(d.glob("*.md")):
                if not ID_RE.match(p.stem):
                    kind = attachment_of(p.stem)
                    if kind and ATTACHMENT_DIRS[kind] == sub:
                        text = p.read_text(encoding="utf-8")
                        self.attachments[p.stem] = (p, parse_frontmatter(text), text)
                    else:
                        self.stray.append(p)
                    continue
                text = p.read_text(encoding="utf-8")
                self.records[p.stem] = (p, parse_frontmatter(text), text)
                if "-H-" in p.stem:
                    self.history[p.stem] = parse_history(text)
        # レコード ∪ 付随物。**リンク系のチェックだけ**がこれを使う（射影・集計は records のみ）。
        self.nodes = {**self.records, **self.attachments}
        log_path = self.wiki / "log.md"
        self.log = log_path.read_text(encoding="utf-8") if log_path.exists() else ""

    @cached_property
    def stage(self) -> str:
        """現在ステージ。ステージを動かした意思決定(DEC)の `to-stage` のうち最新（date 昇順の末尾）を
        正本とし、無ければ stage.md の current-stage にフォールバックする。

        ステージ移行は DEC（追記される出来事）として記録されるので、そのイベント列の末尾から
        現在地を導出する（update より create の思想）。`to-stage` はステージを変える判断
        （stage-transition・rollback など）が記入する結果ステージで、type では絞らない
        （rollback もステージを戻すため）。`to-stage` を持つ DEC がまだ無いプロジェクトは stage.md を読む。"""
        moves = sorted(
            ((fm.get("date", ""), stem, fm.get("to-stage", "").strip())
             for stem, (_, fm, _) in self.records.items()
             if "-DEC-" in stem and fm.get("to-stage")),
            key=lambda x: (x[0], x[1]))
        if moves:
            return moves[-1][2]
        p = self.wiki / "stage.md"
        if p.exists():
            m = re.search(r"current-stage:\s*(\w+)", p.read_text(encoding="utf-8"))
            if m:
                return m.group(1)
        return ""

    @cached_property
    def prefix(self) -> str:
        # ① プロジェクトが明示した PREFIX を最優先（slug と異なる PREFIX・空プロジェクトに対応）
        p = self.wiki / "stage.md"
        if p.exists():
            m = re.search(r"prefix:\s*([A-Z0-9]+)", p.read_text(encoding="utf-8"))
            if m:
                return m.group(1)
        # ② 既存レコードIDの先頭トークン（後方互換: prefix 未記入の既存プロジェクト）
        for rid in self.records:
            m = re.match(r"^([A-Z0-9]+)-", rid)
            if m:
                return m.group(1)
        # ③ slug から単一トークンを正規化（ハイフン等の非英数を落とす。ID_RE と整合）
        return re.split(r"[^A-Z0-9]+", self.slug.upper())[0]

    @property
    def sources_dir(self) -> Path:
        """不変層（生データ）のディレクトリ。基準名の正本は ontology.yaml の provenance.base-dir。"""
        return self.root / PROVENANCE.base_dir

    @cached_property
    def source_files(self) -> set:
        """sources/ 配下の生データの相対パス集合（README.md と隠しファイルは除く）。

        出典の実在検証・取り込み忘れ（orphan）検出に使う。**読むだけ**で不変層は触らない。"""
        d = self.sources_dir
        if not d.is_dir():
            return set()
        return {str(p.relative_to(d)) for p in sorted(d.rglob("*"))
                if p.is_file() and p.name != "README.md" and not p.name.startswith(".")}

    def source_header(self, rel: str) -> str:
        """生データ冒頭 N 行（N の正本は provenance.fictional-header-scan-lines）。

        架空/シミュレーション宣言（`sources/README.md` が冒頭に明記させるもの）を
        fictional-cap 判定の一次情報として読むために使う。存在しないパスは空文字。"""
        p = self.sources_dir / rel
        if not p.is_file():
            return ""
        try:
            lines = p.read_text(encoding="utf-8").splitlines()
        except (OSError, UnicodeDecodeError):
            return ""
        return "\n".join(lines[:PROVENANCE.fictional_header_scan_lines])

    def hyp_records(self):
        """仮説レコードを (stem, fm, body, history) で列挙する。history はキャッシュ済み。"""
        for stem, (_, fm, body) in self.records.items():
            if "-H-" in stem:
                yield stem, fm, body, self.history[stem]

    def iter_attachments(self):
        """付随物を (stem, fm, body, 種別宣言, 親レコードID) で列挙する。

        付随物の解決（suffix → 種別 → 親ID）は付随物を見る全チェックが冒頭で必ず行うので、
        hyp_records と同じくここに1回だけ書く。親レコード自体は用途がまちまち（frontmatter が
        要る／本文が要る／存在の有無だけ要る）なので、呼び手が `project.records` を引く。"""
        for stem, (_, fm, body) in self.attachments.items():
            a = ATTACHMENTS[attachment_of(stem)]
            yield stem, fm, body, a, a.parent_of(stem)
