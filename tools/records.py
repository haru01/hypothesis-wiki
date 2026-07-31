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
)

HISTORY_HEADER = "## 確信度履歴"
TESTCARD_RE = re.compile(r"## テストカード.*?(?=## 学習カード|\Z)", re.DOTALL)


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
    """TEST 本文からテストカード節（## テストカード〜## 学習カードの手前）を逐語抽出する。"""
    m = TESTCARD_RE.search(text)
    return m.group(0) if m else ""


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


def fictional_activities(project) -> set:
    """架空/シミュレーション由来と判定される TEST/LEARN の stem 集合（lint とビューで共有）。

    判定は2経路で、**出典（provenance）が一次情報**:
    (a) 学び(LEARN)の `sources` が指す生データの**冒頭**に架空マーカーがある
        — `sources/README.md` は生データ冒頭への架空宣言を要求している。その宣言を実際に読む。
    (b) TEST/LEARN 本文に架空マーカーがある — 出典を持たないレコード向けの後方互換フォールバック。

    (a) が無いと連鎖が最初の一歩で切れる: 生データ側の宣言を誰も読まないので、
    著者が偶然 LEARN 本文にも「架空」と書き写しているときだけ蓋（fictional-cap）が働く、
    という状態になる（＝規約が実質機能しない）。"""
    out = set()
    for stem, (_, fm, body) in project.records.items():
        if not ("-TEST-" in stem or "-LEARN-" in stem):
            continue
        if any(m in body for m in FICTIONAL_MARKERS):
            out.add(stem)
            continue
        for rel in source_paths(fm):
            if any(m in project.source_header(rel) for m in FICTIONAL_MARKERS):
                out.add(stem)
                break
    return out


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
