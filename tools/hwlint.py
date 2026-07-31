#!/usr/bin/env python3
"""仮説検証Wiki の決定論的 lint。

CLAUDE.md の不変ルールのうち機械検証可能なものだけをチェックする。
意味的チェック（矛盾する仮説・長期放置など）は /lint スキル（LLM）が担い、両者で併用する。
"""
import argparse
import datetime
import re
import sys
from dataclasses import dataclass
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
# 語彙(enum)・型・関係・状態機械の定義は ontology.yaml が唯一の正本。ここには再定義しない。
from ontology import (  # noqa: E402
    STATUSES, STAGES, H_TYPES, TEST_TYPES, LEARN_TYPES, DEC_TYPES, OUTCOMES,
    CONFIDENCE_MIN, CONFIDENCE_MAX, FICTIONAL_CAP, FICTIONAL_MARKERS,
    EVIDENCE_TAGS, EVIDENCE_LADDER, EVIDENCE_RANK, EVIDENCE_FLOOR,
    EVIDENCE_FLOOR_MIN_CONFIDENCE, EVIDENCE_AUX,
    STATUS_BOUNDS, RELATIONS, RELATIONS_BY_FIELD, STAGE_FOCUS, STAGE_ORDER,
    IMPORTANCE_FOCUS, FIELDS, FIELDS_BY_NAME, ENUM_REFS, PROVENANCE,
    STALENESS_CONFIDENCE_DAYS, STALENESS_TEST_DAYS, ENTITY_INFIXES,
    ID_RE, NODE_FIELDS_BY_NAME,
)
# レコードモデル層（frontmatter/履歴/log のパーサと Project）は records.py に集約。
# ここから import することで、lint と gen_views が同じモデルを共有する（linter へのモデル依存の解消）。
from records import (  # noqa: E402
    HISTORY_HEADER, parse_frontmatter, parse_id_array, entity_of,
    strip_frontmatter, strip_comments, parse_history, referenced_ids,
    importance, source_paths, fictional_activities, Project,
    node_kind,
)
from project import resolve_current_project  # noqa: E402
import graph  # noqa: E402  関係グラフの走査層（孤立・連結性の算出）

DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


@dataclass
class Problem:
    level: str    # "error" | "warning"
    where: str    # レコードID または パス
    check: str    # チェック名（kebab-case）
    message: str


def check_id_matches_filename(project) -> list:
    """frontmatter id はファイル名と完全一致（接頭辞つき）。規約外ファイル名も報告。"""
    problems = []
    for stem, (path, fm, _) in project.records.items():
        fid = fm.get("id", "")
        if fid != stem:
            problems.append(Problem("error", stem, "id-filename",
                                    f"frontmatter id '{fid}' がファイル名 '{stem}' と一致しない"))
    for p in project.stray:
        problems.append(Problem("warning", str(p), "id-filename",
                                "レコード名が ID 規約（<PREFIX>-H/TEST/DEC-NNN）にも"
                                "付随物の命名（<親レコードID>-script.md 等）にも合わない"))
    return problems


def check_fields(project) -> list:
    """スキーマ＝契約: frontmatter のキー構成を ontology.yaml の fields 宣言に照らす。

    論文（Knowledge Graph Engineering）の「the schema is the contract」に対応する層。
    entity/relation/state-machine は宣言済みでもフィールド自体の宣言が無かったため、
    必須キーの欠落も未知キー（タイポ）の混入も機械検出できなかった穴を塞ぐ。

    - required なフィールドの欠落／空 → error（例: date 欠落は Project.stage のソートを静かに壊す）
    - 宣言に無いキー → warning（タイポ・旧スキーマの残骸）
    - kind: date が YYYY-MM-DD でない → error

    付随物（スクリプト等）も対象にする。種別の解決は node_kind（付随物優先）で、
    entity_of を先に見ると `-TEST-` を含むステムが実験計画の契約で検証されてしまう。
    """
    problems = []
    for stem, (_, fm, _) in project.nodes.items():
        ent = node_kind(stem)
        declared = NODE_FIELDS_BY_NAME.get(ent)
        if not declared:
            continue
        for name in declared:
            f = declared[name]
            if f.required and not fm.get(name, "").strip():
                problems.append(Problem("error", stem, "fields",
                    f"必須フィールド {name}（{f.kind}）が未指定/空"))
        for key in fm:
            if key not in declared:
                problems.append(Problem("warning", stem, "fields",
                    f"ontology.yaml の {ent}.fields に宣言の無いキー '{key}'"
                    f"（タイポか、スキーマへの宣言漏れ）"))
        for name, f in declared.items():
            value = fm.get(name, "").strip()
            if not value:
                continue
            if f.kind == "date" and not DATE_RE.match(value):
                problems.append(Problem("error", stem, "fields",
                    f"{name} '{value}' は YYYY-MM-DD 形式でない"))
    return problems


def check_vocabulary(project) -> list:
    """status・type・stage・confidence・outcome の語彙/範囲を規約に照らして検証する。"""
    problems = []
    for stem, (_, fm, _) in project.records.items():
        if "-H-" in stem:
            if fm.get("status") not in STATUSES:
                problems.append(Problem("error", stem, "vocab", f"status '{fm.get('status')}' は規約外"))
            c = fm.get("confidence", "")
            if not (c.isdigit() and CONFIDENCE_MIN <= int(c) <= CONFIDENCE_MAX):
                problems.append(Problem("error", stem, "vocab",
                    f"confidence '{c}' は {CONFIDENCE_MIN}-{CONFIDENCE_MAX} の整数でない"))
            if fm.get("type") not in H_TYPES:
                problems.append(Problem("error", stem, "vocab", f"type '{fm.get('type')}' は規約外"))
            imp = fm.get("importance", "auto")
            if imp != "auto" and not (imp.isdigit() and CONFIDENCE_MIN <= int(imp) <= CONFIDENCE_MAX):
                problems.append(Problem("error", stem, "vocab",
                    f"importance '{imp}' は auto か {CONFIDENCE_MIN}-{CONFIDENCE_MAX}"))
        if "-TEST-" in stem and fm.get("type") not in TEST_TYPES:
            problems.append(Problem("error", stem, "vocab", f"type '{fm.get('type')}' は規約外"))
        if "-LEARN-" in stem and fm.get("type") not in LEARN_TYPES:
            problems.append(Problem("error", stem, "vocab", f"type '{fm.get('type')}' は規約外"))
        # LEARN の outcome（検証判定）。board サマリへ射影される正本なので誤記を弾く
        if "-LEARN-" in stem and fm.get("outcome") and fm.get("outcome") not in OUTCOMES:
            problems.append(Problem("error", stem, "vocab",
                f"outcome '{fm.get('outcome')}' は規約外（{'・'.join(sorted(OUTCOMES))}）"))
        if "-DEC-" in stem and fm.get("type") not in DEC_TYPES:
            problems.append(Problem("error", stem, "vocab", f"type '{fm.get('type')}' は規約外"))
        # DEC の to-stage（記入されていれば）は正規のステージ名。現在ステージ導出の正本なので誤記を弾く
        if "-DEC-" in stem and fm.get("to-stage") and fm.get("to-stage") not in STAGES:
            problems.append(Problem("error", stem, "vocab", f"to-stage '{fm.get('to-stage')}' は規約外"))
        if "-H-" in stem or "-TEST-" in stem or "-LEARN-" in stem:
            st = fm.get("stage")
            if st is None:
                problems.append(Problem("error", stem, "vocab", "必須フィールド stage が未指定"))
            elif st not in STAGES:
                problems.append(Problem("error", stem, "vocab", f"stage '{st}' は規約外"))
    return problems


EVIDENCE_RE = re.compile(r"\[\[([A-Z0-9]+-(?:TEST|LEARN|DEC)-\d+)\]\]")


def check_history_consistency(project) -> list:
    """不変ルール2: frontmatter の confidence/status は確信度履歴テーブルの最終行と一致する。"""
    problems = []
    for stem, fm, _, rows in project.hyp_records():
        if not rows:
            problems.append(Problem("error", stem, "history", "確信度履歴テーブルが無い/パースできない"))
            continue
        last = rows[-1]
        if last["confidence"] != fm.get("confidence"):
            problems.append(Problem("error", stem, "history",
                f"frontmatter confidence={fm.get('confidence')} と履歴最終行 {last['confidence']} が不一致"))
        if last["status"] != fm.get("status"):
            problems.append(Problem("error", stem, "history",
                f"frontmatter status={fm.get('status')} と履歴最終行 {last['status']} が不一致"))
    return problems


def check_evidence_links(project) -> list:
    """不変ルール1: 初期行以降の確信度・ステータス変更は必ず実在する TEST/DEC に紐づく。"""
    problems = []
    for stem, _, _, rows in project.hyp_records():
        for i, row in enumerate(rows):
            if i == 0:
                continue  # 初期作成行のみ根拠レコード免除（desk-research を書くのは任意）
            ids = EVIDENCE_RE.findall(row["activity"])
            if not ids:
                problems.append(Problem("error", stem, "evidence",
                    f"履歴 {row['date']} 行（確信度{row['confidence']}）に [[TEST/DEC]] の証拠リンクが無い"))
            for rid in ids:
                if rid not in project.records:
                    problems.append(Problem("error", stem, "evidence",
                        f"履歴の証拠 [[{rid}]] のレコードが存在しない"))
    return problems


WIKILINK_RE = re.compile(r"\[\[([^\]|#]+)(?:[|#][^\]]*)?\]\]")


def check_frontmatter_refs(project) -> list:
    """frontmatter の関係リンクを ontology.yaml の宣言で検証する。

    各関係（derived-from / leads-to / addresses / hypotheses / based-on）について、
    その関係の domain 種別を持つノード（レコード＋付随物）の frontmatter 参照を、接頭辞つき・実在・
    range 種別・（サブタイプ制約があればサブタイプ）・（単一関係の）cardinality で検証する。
    付随物固有の制約（親との一致・親の検証対象の部分集合）は check_attachment_refs が見る。
    """
    problems = []
    prefix = project.prefix
    for stem, (_, fm, _) in project.nodes.items():
        ent = node_kind(stem)
        for rel in RELATIONS:
            if not rel.in_domain(ent):
                continue
            ids = parse_id_array(fm.get(rel.field, ""))
            if not ids:
                continue
            # domain サブタイプ制約（例: addresses はソリューション仮説だけが持てる）
            if rel.domain_subtypes and fm.get("type") not in rel.domain_subtypes:
                problems.append(Problem("error", stem, "refs",
                    f"frontmatter {rel.field} は {'・'.join(sorted(rel.domain_subtypes))} だけが持てる"
                    f"（この仮説は '{fm.get('type')}'）"))
            # cardinality（単一関係に複数）
            if rel.is_single and len(ids) > 1:
                problems.append(Problem("error", stem, "refs",
                    f"frontmatter {rel.field} は単一参照（cardinality one）だが {len(ids)} 件ある"))
            for rid in ids:
                if not rid.startswith(prefix + "-"):
                    problems.append(Problem("error", stem, "refs",
                        f"frontmatter {rel.field} '{rid}' が接頭辞つきでない（{prefix}-… に統一する）"))
                    continue
                if rid not in project.records:
                    problems.append(Problem("error", stem, "refs",
                        f"frontmatter {rel.field} '{rid}' のレコードが存在しない"))
                    continue
                # range 種別（例: hypotheses は H を、learns-from/script-for は TEST を指す）
                target_fm = project.records[rid][1]
                if not rel.in_range(node_kind(rid)):
                    problems.append(Problem("error", stem, "refs",
                        f"frontmatter {rel.field} '{rid}' は {rel.range} を指すべき"
                        f"（{node_kind(rid)} を指している）"))
                elif rel.range_subtypes and target_fm.get("type") not in rel.range_subtypes:
                    problems.append(Problem("error", stem, "refs",
                        f"frontmatter {rel.field} '{rid}' は {'・'.join(sorted(rel.range_subtypes))} を指すべき"
                        f"（'{target_fm.get('type')}' を指している）"))
    return problems


def check_relation_wikilinks(project) -> list:
    """二重表現規約: must-wikilink な関係は frontmatter 参照が本文 wikilink にも現れる。

    frontmatter 配列だけでは Obsidian グラフに辺が出ないため、本文に [[…]] を張る規約。
    新規約のため warning 運用（検出のみ）。"""
    problems = []
    prefix = project.prefix
    for stem, (_, fm, body) in project.nodes.items():
        ent = node_kind(stem)
        body_links = {t.strip() for t in WIKILINK_RE.findall(strip_comments(strip_frontmatter(body)))}
        for rel in RELATIONS:
            if not rel.in_domain(ent) or not rel.must_wikilink:
                continue
            for rid in parse_id_array(fm.get(rel.field, "")):
                if rid.startswith(prefix + "-") and rid in project.records and rid not in body_links:
                    problems.append(Problem("warning", stem, "relation-wikilink",
                        f"frontmatter {rel.field}（{rel.label}）'{rid}' が本文 wikilink [[{rid}]] に無い"
                        f"（二重表現規約: Obsidian グラフに辺を出すため本文にも張る）"))
    return problems


def check_wikilinks(project) -> list:
    """本文の wikilink が当該プロジェクトの wiki 内で解決すること。schema層（/入り）への wikilink は規約違反。

    解決対象は当該プロジェクト配下（`root/wiki/`）に限定する。接頭辞で ID 衝突を防ぐ設計に対し
    親ディレクトリ（＝全プロジェクトの wiki）を走査すると、別プロジェクトに同名があるだけで
    リンクが解決してしまいリンク切れ検出がプロジェクト境界を越えて緩くなるため（共通規約1: lint は現在プロジェクトのみ対象）。"""
    problems = []
    all_names = {p.stem for p in project.root.glob("wiki/**/*.md")}
    for stem, (_, _, body) in project.nodes.items():
        for target in WIKILINK_RE.findall(strip_comments(strip_frontmatter(body))):
            target = target.strip()
            if "/" in target:
                problems.append(Problem("error", stem, "wikilink",
                    f"[[{target}]] — schema層への参照は wikilink でなく相対mdリンクで書く規約"))
            elif target not in all_names:
                problems.append(Problem("error", stem, "wikilink", f"[[{target}]] が解決しない（リンク切れ）"))
    return problems


def check_relative_links(project) -> list:
    """レコード本文の相対リンク（schema層・生データ・生成物への参照）が実在すること（warning）。

    wikilink は check_wikilinks が見ているが、**相対mdリンクは誰も見ていなかった**。
    スキル名の改名（`/ingest` → `/learning` など）やファイル移動でリンクが壊れても検出されず、
    しかもテストカード本文の壊れたリンクは board ビューへ逐語転記されるため、
    再生成しても直らない壊れたリンクが生成物に残り続ける。

    リンク先はリポジトリのどこでもよい（schema層・sources/・prototypes/）ので、
    参照元ファイルのディレクトリを基準に解決してリポジトリ内に収まっているかも併せて見る。"""
    problems = []
    repo = project.root.parent.parent      # projects/<slug> → repo root
    for stem, (path, _, body) in project.nodes.items():
        for target in _md_link_targets(body):
            if not target or target.startswith("/"):
                continue                   # 絶対パスは規約外だが誤検出を避けて素通し（相対で書く規約）
            resolved = (path.parent / target).resolve()
            if not resolved.exists():
                problems.append(Problem("warning", stem, "relative-link",
                    f"相対リンク '{target}' が解決しない（リンク切れ）"))
            elif repo.resolve() not in resolved.parents:
                problems.append(Problem("warning", stem, "relative-link",
                    f"相対リンク '{target}' がリポジトリ外を指している"))
    return problems


def check_attachment_id(project) -> list:
    """付随物の同一性: ファイル名 = 親レコードID + suffix、frontmatter id = ファイル名。

    suffix を剥がした基底が ID_RE を満たし・その ID のレコードが実在し・宣言された親種別である、
    の3点を1つのチェックで担保する（ID_RE を再定義せず流用する＝レコードID規約の正本は1箇所）。
    付随物は独自のID体系を持たないので、この対応が壊れると親から切り離された孤児になる。"""
    problems = []
    for stem, fm, _, a, base in project.iter_attachments():
        fid = fm.get("id", "")
        if fid != stem:
            problems.append(Problem("error", stem, "attachment-id",
                f"frontmatter id '{fid}' がファイル名 '{stem}' と一致しない"))
        if not ID_RE.match(base):
            problems.append(Problem("error", stem, "attachment-id",
                f"'{a.suffix}' を除いた '{base}' がレコードID規約に合わない"
                f"（{a.label}のファイル名は <親レコードID>{a.suffix}.md）"))
        elif base not in project.records:
            problems.append(Problem("error", stem, "attachment-id",
                f"親レコード '{base}' が存在しない（{a.label}は親レコードに従属する）"))
        elif entity_of(base) != a.parent:
            problems.append(Problem("error", stem, "attachment-id",
                f"親 '{base}' は {entity_of(base)} だが、{a.label}の親は {a.parent} でなければならない"))
    return problems


def check_attachment_vocabulary(project) -> list:
    """付随物の type がサブタイプ語彙（＝基にした雛形）に収まること。

    check_vocabulary はエンティティ種別ごとの分岐で書かれており付随物を見ないので、
    ここが無いと type は「空でないか」しか検証されない（check_fields の required 判定のみ）。"""
    problems = []
    for stem, fm, _, a, _ in project.iter_attachments():
        value = fm.get("type", "").strip()
        if value and value not in a.subtypes:
            problems.append(Problem("error", stem, "attachment-vocab",
                f"type '{value}' は {a.name} の語彙にない（{'・'.join(a.subtypes)}）"))
    return problems


def check_attachment_refs(project) -> list:
    """付随物固有の参照制約。型・実在・cardinality の一般検証は check_frontmatter_refs が済ませている。

    制約はオントロジーから導出する（フィールド名をここに書かない＝二重管理を作らない）:
    - **親を指す関係**（domain=付随物・range=親種別・cardinality one）の値が、ファイル名から
      導いた親と一致すること。名前と宣言という二重表現が食い違ったまま残るのを防ぐ。
    - **親と共有する関係**（両者の domain に現れる関係。例 hypotheses）の値が、親の値の
      **部分集合**であること。台本が親の計画に無い仮説を当てるのは計画と実施の乖離。
      逆向き（本文で言及した仮説をすべて宣言せよ）は課さない — 背景として別の仮説に
      言及するのは正当だから。
    """
    problems = []
    for stem, fm, _, a, base in project.iter_attachments():
        if base not in project.records:
            continue                        # 親不在は check_attachment_id が error で報告済み
        parent_fm = project.records[base][1]
        for rel in RELATIONS:
            if not rel.in_domain(a.name):
                continue
            values = parse_id_array(fm.get(rel.field, ""))
            if rel is a.parent_relation:
                if values and values[0] != base:
                    problems.append(Problem("error", stem, "attachment-refs",
                        f"{rel.field}（{rel.label}）'{values[0]}' がファイル名から導いた親 '{base}' と違う"))
            elif rel.in_domain(a.parent):
                parent_values = parse_id_array(parent_fm.get(rel.field, ""))
                extra = [v for v in values if v not in parent_values]
                if extra:
                    problems.append(Problem("error", stem, "attachment-refs",
                        f"{rel.field}（{rel.label}）{extra} が親 {base} の {rel.field} に無い"
                        f"（{a.label}は親の{rel.label}の部分集合でなければならない）"))
    return problems


def check_attachment_backlink(project) -> list:
    """親レコードの本文から付随物への相対mdリンクがあること（warning）。

    付随物は生成ビュー（board/list/index）に集計されないので、親から辿れなければ
    Wiki 上で事実上到達不能になる（ファイル名の規則を知っている人しか開けない）。"""
    problems = []
    for stem, _, _, a, base in project.iter_attachments():
        if base not in project.records:
            continue                        # 親不在は check_attachment_id が error で報告済み
        body = project.records[base][2]
        if not any(Path(t).name == f"{stem}.md" for t in _md_link_targets(body)):
            problems.append(Problem("warning", base, "attachment-backlink",
                f"本文に{a.label} '{stem}.md' への相対mdリンクが無い（親から辿れず到達不能になる）"))
    return problems


SOURCE_LINK_RE = re.compile(r"\[\[([A-Z0-9]+-(?:" + "|".join(map(re.escape, ENTITY_INFIXES))
                            + r")-\d+)\]\]")


def check_source_links(project) -> list:
    """不変層 sources/ 内の wikilink がレコードとして実在すること（warning 固定）。

    lint は従来 sources/ を走査していなかったため、改名・欠番で宙に浮いた参照が見えなかった。
    **sources/ は不変層なので直せない**（不変ルール3）。level は warning 固定にして
    「修正せよ」ではなく「この生データは古い ID を指している」という事実として可視化する
    （読み手が生データを辿るとき、存在しないレコードを探して迷わないために要る）。"""
    problems = []
    d = project.sources_dir
    if not d.is_dir():
        return problems
    for rel in sorted(project.source_files):
        p = d / rel
        if p.suffix != ".md":
            continue
        try:
            text = p.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        for rid in dict.fromkeys(SOURCE_LINK_RE.findall(strip_comments(text))):
            if rid not in project.records:
                problems.append(Problem("warning", f"{PROVENANCE.base_dir}/{rel}", "source-link",
                    f"[[{rid}]] が解決しない（改名・取り下げで宙に浮いた参照）。"
                    f"sources/ は不変層なので修正せず、現在のIDは学び(LEARN)側で辿る"))
    return problems


def check_stage_doc(project) -> list:
    """stage.md 内の playbook 参照が current-stage と一致すること（warning）。

    `/deciding` は「stage.md の移行基準の上書き（あれば優先）」を読むため、
    current-stage と別ステージの playbook を指していると**現在ステージと違う基準で判断される**。
    巻き戻し（rollback）で current-stage だけを直し、本文の playbook 参照が前ステージのまま
    取り残されると起きる。"""
    problems = []
    p = project.wiki / "stage.md"
    if not p.exists():
        return problems
    text = p.read_text(encoding="utf-8")
    m = re.search(r"current-stage:\s*(\w+)", text)
    if not m:
        return problems
    current = m.group(1)
    referenced = {s.upper() for s in re.findall(r"playbooks/(\w+)\.md", text)}
    stray = {s for s in referenced if s in STAGES and s != current}
    for s in sorted(stray):
        problems.append(Problem("warning", "stage.md", "stage-doc",
            f"current-stage は {current} なのに playbooks/{s.lower()}.md（{s} の基準）を参照している"
            f"（/deciding が現在ステージと違う移行基準で判断してしまう）"))
    return problems


INDEX_ROW_RE = re.compile(r"^\|\s*\[\[([A-Z0-9]+-H-\d+)\]\]\s*\|[^|]*\|\s*(\d+)\s*\|\s*([^|]+?)\s*\|")


def check_id_sequence(project) -> list:
    """不変ルール5: ID 重複禁止。欠番は log.md の取り下げ記録があれば正常、なければ warning。"""
    problems = []
    prefix = project.prefix
    seen = {}
    for stem, (_, fm, _) in project.records.items():
        fid = fm.get("id", stem)
        if fid in seen:
            problems.append(Problem("error", stem, "id-seq", f"id '{fid}' が {seen[fid]} と重複"))
        seen[fid] = stem
    log_lines = project.log.splitlines()
    for kind in ("H", "TEST", "LEARN", "DEC"):
        pat = re.compile(rf"^{re.escape(prefix)}-{kind}-(\d+)$")
        nums = sorted(int(m.group(1)) for rid in project.records if (m := pat.match(rid)))
        if not nums:
            continue
        for missing in sorted(set(range(1, max(nums) + 1)) - set(nums)):
            mid = f"{prefix}-{kind}-{missing:03d}"
            # 数字境界つきで照合（例: DEMO-H-002 が DEMO-H-0025 に部分一致しない）
            mid_re = re.compile(rf"(?<![0-9A-Za-z]){re.escape(mid)}(?![0-9])")
            if not any(mid_re.search(line) and "取り下げ" in line for line in log_lines):
                problems.append(Problem("warning", mid, "id-seq",
                                        "欠番だが log.md に取り下げ記録が見当たらない"))
    return problems


def check_log_sync(project) -> list:
    """不変ルール2: 履歴テーブルへの追記（2行目以降）は log.md にも記録される。

    log.md は接頭辞つき ID（SELF-H-001）でも短縮 ID（H-001）でも書かれうる。
    確信度変更は `確信度X→Y` でも短縮 `4→6` でも記録されうるので、両方を許容する。
    """
    problems = []
    log_lines = project.log.splitlines()
    for stem, _, _, rows in project.hyp_records():
        m = re.search(r"(H-\d+)$", stem)
        short = m.group(1) if m else stem
        # 数字境界つきで ID 照合（例: H-001 が H-0012 に部分一致しない）
        stem_re = re.compile(rf"(?<![0-9A-Za-z]){re.escape(stem)}(?![0-9])")
        short_re = re.compile(rf"(?<![0-9A-Za-z]){re.escape(short)}(?![0-9])")
        for row in rows[1:]:
            conf = row["confidence"]
            pattern = rf"(?:→\s*|確信度[^|]*?){re.escape(conf)}(?!\d)"
            if not any((stem_re.search(line) or short_re.search(line)) and re.search(pattern, line)
                       for line in log_lines):
                problems.append(Problem("warning", stem, "log-sync",
                    f"履歴 {row['date']} 行（確信度{conf}）に対応する log.md 記録が見当たらない"))
    return problems


def check_index_sync(project) -> list:
    """index.md の確信度・ステータスがレコード本体と一致する（lint 項目5の機械部分）。"""
    problems = []
    index_path = project.wiki / "index.md"
    if not index_path.exists():
        return [Problem("warning", "index.md", "index-sync", "index.md が無い")]
    for line in index_path.read_text(encoding="utf-8").splitlines():
        m = INDEX_ROW_RE.match(line.strip())
        if not m:
            continue
        rid, conf, status = m.group(1), m.group(2), m.group(3)
        if rid not in project.records:
            problems.append(Problem("error", "index.md", "index-sync", f"[[{rid}]] のレコードが存在しない"))
            continue
        fm = project.records[rid][1]
        if fm.get("confidence") != conf or fm.get("status") != status:
            problems.append(Problem("error", "index.md", "index-sync",
                f"[[{rid}]] index表（確信度{conf}/{status}）とレコード"
                f"（確信度{fm.get('confidence')}/{fm.get('status')}）が不一致"))
    return problems


def check_fictional_cap(project) -> list:
    """架空/シミュレーションデータ由来の確信度は上限 FICTIONAL_CAP（それ超は実観測に限る）。

    履歴の**全行**を走査する（最終行だけでなく、確信度を上限超へ押し上げた中間行の
    架空根拠も取りこぼさない）。行の根拠が架空と判定されるのは、(a) 紐づく TEST/LEARN が
    架空（fictional_activities の判定＝出典の冒頭宣言または本文マーカー）、(b) 根拠セルに
    〈架空〉タグ、のいずれか。根拠セルの地の文に架空マーカー語が出るだけ（例: 架空データに
    言及した注記）では判定しない（構造化シグナルに一本化して誤検出を避ける）。"""
    problems = []
    fictional_acts = fictional_activities(project)
    for stem, _, _, rows in project.hyp_records():
        for row in rows:
            rc = row["confidence"]
            if not rc.isdigit() or int(rc) <= FICTIONAL_CAP:
                continue
            hit = [rid for rid in EVIDENCE_RE.findall(row["activity"]) if rid in fictional_acts]
            tagged = "〈架空〉" in row["reason"]
            if hit or tagged:
                src = "・".join(hit) if hit else "〈架空〉タグ"
                problems.append(Problem("error", stem, "fictional-cap",
                    f"履歴 {row['date']} 行 confidence={rc} だが根拠が架空/シミュレーション"
                    f"（{src}）。上限{FICTIONAL_CAP}"))
    return problems


# 相対mdリンク（schema層・生データへの参照）。外部URL・アンカーのみは対象外。
# 直前が `]` のものは除く: `[[ID]](補足)` のように wikilink の閉じ括弧に括弧書きが続く記述を
# mdリンクと誤読しないため（実データに `[[AIRE-H-003]](b) の対抗` がある）。
MD_LINK_RE = re.compile(r"(?<!\])\]\((?!https?://|mailto:|#)([^)\s]+)\)")


def _md_link_targets(body: str) -> list:
    """本文の相対リンク先（アンカー・クエリを落としたパス文字列）を並べる。"""
    out = []
    for target in MD_LINK_RE.findall(strip_comments(strip_frontmatter(body))):
        out.append(target.split("#", 1)[0].split("?", 1)[0])
    return out


def _learn_sources(project) -> dict:
    """LEARN stem → 宣言された出典パス（相対）のリスト。"""
    return {stem: source_paths(fm) for stem, (_, fm, _) in project.records.items()
            if PROVENANCE.in_domain(entity_of(stem))}


def check_provenance_paths(project) -> list:
    """出典（provenance）のパスが不変層 sources/ に実在すること（error）。

    確信度の根拠鎖 `H の確信度履歴 → [[LEARN-NNN]] → sources/<生データ>` の最後の一歩。
    ここが検証されていないと、生データを改名・削除しても確信度を支えた記録が無言で宙に浮く。"""
    problems = []
    files = project.source_files
    for stem, paths in _learn_sources(project).items():
        for rel in paths:
            if rel.startswith("/") or ".." in Path(rel).parts:
                problems.append(Problem("error", stem, "provenance",
                    f"{PROVENANCE.field} '{rel}' は {PROVENANCE.base_dir}/ 基準の相対パスで書く"
                    f"（絶対パス・'..' は不可）"))
            elif rel not in files:
                problems.append(Problem("error", stem, "provenance",
                    f"{PROVENANCE.field} '{rel}' が {PROVENANCE.base_dir}/ 配下に存在しない（出典切れ）"))
    return problems


def check_provenance_presence(project) -> list:
    """観測を伴う活動種別の学び(LEARN)は出典を持つ（warning）。

    required-for-types（interview/demo/… の正本は ontology.yaml の provenance 節）に限る。
    self-reflection は内省なので出典なしを正当とする。"""
    problems = []
    for stem, (_, fm, _) in project.records.items():
        if not PROVENANCE.in_domain(entity_of(stem)):
            continue
        if fm.get("type") in PROVENANCE.required_for_types and not source_paths(fm):
            problems.append(Problem("warning", stem, "provenance",
                f"type={fm.get('type')} の学びだが {PROVENANCE.field}（出典）が空"
                f"（どの生データから学んだのかを {PROVENANCE.base_dir}/ 配下の相対パスで書く）"))
    return problems


def check_provenance_body_link(project) -> list:
    """二重表現規約: 出典は frontmatter だけでなく本文にも相対mdリンクで置く（warning）。

    生データは接頭辞つきノートでないので wikilink は解決しない（規約どおり相対mdリンクを使う）。"""
    problems = []
    if not PROVENANCE.must_body_link:
        return problems
    for stem, (_, fm, body) in project.records.items():
        if not PROVENANCE.in_domain(entity_of(stem)):
            continue
        targets = _md_link_targets(body)
        for rel in source_paths(fm):
            if not any(t.endswith(rel) for t in targets):
                problems.append(Problem("warning", stem, "provenance",
                    f"{PROVENANCE.field} '{rel}' が本文の相対mdリンクに無い"
                    f"（二重表現規約: 読み手が出典へ辿れるように本文にも張る）"))
    return problems


def check_provenance_chain(project) -> list:
    """確信度を上げた履歴行が指す学び(LEARN)に出典があること（warning）。

    このリポジトリの生命線は「確信度は必ず証拠に紐づく」だが、紐づけが
    `H の履歴 → [[LEARN-NNN]]` で止まっていると「その学びは何を観測したのか」が辿れない。
    根拠鎖を端（生データ）まで繋ぐことを要求する＝出典なき確信度上昇を作らない。"""
    problems = []
    sources_of = _learn_sources(project)
    for stem, _, _, rows in project.hyp_records():
        prev = None
        for row in rows:
            cur = int(row["confidence"]) if row["confidence"].isdigit() else None
            if cur is not None and prev is not None and cur > prev:
                for rid in EVIDENCE_RE.findall(row["activity"]):
                    if rid in sources_of and not sources_of[rid]:
                        problems.append(Problem("warning", stem, "provenance-chain",
                            f"履歴 {row['date']} 行で確信度を {prev}→{cur} に上げているが、根拠の "
                            f"[[{rid}]] に {PROVENANCE.field}（出典）が無い（根拠鎖が生データまで繋がっていない）"))
            if cur is not None:
                prev = cur
    return problems


def check_orphan_sources(project) -> list:
    """sources/ にあるがどの学び(LEARN)からも参照されていない生データ（warning）。

    「記録が散逸し過去の学びが忘れられる」を機械が拾う層。置いたのに取り込まれていない
    生データは、確信度に反映されないまま忘れられる（＝このキットが解こうとしている課題そのもの）。"""
    problems = []
    referenced = {rel for paths in _learn_sources(project).values() for rel in paths}
    for rel in sorted(project.source_files - referenced):
        problems.append(Problem("warning", f"{PROVENANCE.base_dir}/{rel}", "orphan-source",
            f"どの学び(LEARN)の {PROVENANCE.field} からも参照されていない生データ"
            f"（取り込み忘れ。/learning で学びを作るか、参照元の {PROVENANCE.field} に加える）"))
    return problems


def check_evidence_tags(project) -> list:
    """証拠の階梯: 履歴2行目以降の根拠セルには証拠種別タグを付ける（新規約のため warning 運用）。"""
    problems = []
    for stem, _, _, rows in project.hyp_records():
        for row in rows[1:]:
            if not any(tag in row["reason"] for tag in EVIDENCE_TAGS):
                problems.append(Problem("warning", stem, "evidence-tag",
                    f"履歴 {row['date']} 行の根拠に証拠種別タグ（〈自認〉〈実コスト〉等）が無い"))
    return problems


def check_status_confidence(project) -> list:
    """status × confidence の矛盾検出（2軸の食い違い）。ontology.yaml の status-bounds に照らす。"""
    problems = []
    for stem, fm, _, _ in project.hyp_records():
        status, c = fm.get("status"), fm.get("confidence", "")
        if not c.isdigit() or status not in STATUS_BOUNDS:
            continue
        conf, b = int(c), STATUS_BOUNDS[status]
        if "min" in b and conf < b["min"]:
            problems.append(Problem("warning", stem, "status-confidence",
                f"status={status} なのに confidence={conf}（{b['min']} 以上が自然）"))
        if "max" in b and conf > b["max"]:
            problems.append(Problem("warning", stem, "status-confidence",
                f"status={status} なのに confidence={conf}（{b['max']} 以下が自然）"))
    return problems


def _floor_for(conf: int):
    """確信度 conf に要求される証拠の階梯の最低段名を返す（無ければ None）。"""
    for min_conf, name in EVIDENCE_FLOOR:   # min-confidence の降順
        if conf >= min_conf:
            return name
    return None


def check_evidence_floor(project) -> list:
    """確信度の帯に対して証拠の階梯が弱すぎないか（例: confidence 7 を〈発言〉だけで支えていないか）。

    2通りの未達を報告する:
    - 階梯タグが在るのにその最強が要求段未満（例: 7 を〈発言〉止まりで支えている）
    - **階梯タグが1つも無いまま要求域に達している**（＝根拠の強さが不明なまま確信度が高い）

    後者を黙って見送ると（旧実装の `if not ranks: continue`）このチェックは
    「階梯タグを書いた人だけが検査される」ものになり、タグを書かなければ無検査で通る。
    実データではまさにそれが起きていた（self の履歴に階梯タグ0行・ai-reskilling は補助タグ〈二次〉のみで、
    両プロジェクトでこの規律が一度も発火していなかった）。補助タグ〈二次〉〈架空〉は序列を持たないので
    階梯を満たさない。

    evidence-tag（タグの有無）との違い: あちらは履歴**行ごと**の記入漏れ、こちらは仮説の**現在の確信度**が
    証拠の強さに見合っているか。既に確定した過去行は追記専用ルールで直せないので、
    「現在値が支えられていない」という事実の側を鳴らす。"""
    problems = []
    for stem, fm, _, rows in project.hyp_records():
        c = fm.get("confidence", "")
        if not c.isdigit():
            continue
        floor = _floor_for(int(c))
        if floor is None:
            continue
        ranks = [EVIDENCE_RANK[name] for name in EVIDENCE_RANK
                 for row in rows if f"〈{name}〉" in row["reason"]]
        if not ranks:
            aux = sorted({t for t in EVIDENCE_AUX for row in rows if f"〈{t}〉" in row["reason"]})
            aux_note = f"（履歴にあるのは補助タグ {'・'.join(f'〈{t}〉' for t in aux)} のみ＝階梯外）" if aux else ""
            problems.append(Problem("warning", stem, "evidence-floor",
                f"confidence={c} には〈{floor}〉以上の証拠が要るが、確信度履歴に証拠の階梯タグが"
                f"1つも無い{aux_note}（根拠の強さが不明なまま確信度が高い）"))
            continue
        if max(ranks) < EVIDENCE_RANK[floor]:
            problems.append(Problem("warning", stem, "evidence-floor",
                f"confidence={c} には〈{floor}〉以上の証拠が要るが、根拠タグの最強は"
                f"〈{EVIDENCE_LADDER[max(ranks)]}〉止まり（証拠の階梯に対し確信度が高い）"))
    return problems


def check_dec_based_on(project) -> list:
    """DEC は根拠となる活動（based-on）に紐づく。根拠なき意思決定を検出する（warning）。"""
    problems = []
    for stem, (_, fm, _) in project.records.items():
        if "-DEC-" not in stem:
            continue
        if not parse_id_array(fm.get("based-on", "")):
            problems.append(Problem("warning", stem, "dec-based-on",
                "DEC に based-on（根拠活動）が無い（意思決定は実験計画/学び [[TEST-NNN]]・[[LEARN-NNN]] に紐づける）"))
    return problems


def check_untested_focus(project) -> list:
    """OI-F1: 重点仮説なのに検証活動(TEST)の hypotheses 入次数が0のものを検出する（warning）。

    重点＝現ステージの重点タイプ（stage-focus）か、手動 importance>=IMPORTANCE_FOCUS のH。
    「重要なのに検証実験が1本も紐づいていない」を構造事実（入次数0）で拾う。トポロジー由来の
    探索域ギャップ検出（docs/ontology-improvements.md OI-F1）。status が検証中/検証済みなら、
    検証したと主張しているのに TEST からの逆リンクが無い二重表現の破れ（食い違い）でもある。"""
    problems = []
    tested = (referenced_ids(project, "hypotheses", infix="-TEST-")
              | referenced_ids(project, "hypotheses", infix="-LEARN-"))
    for stem, fm, _, _ in project.hyp_records():
        if importance(fm, project.stage) < IMPORTANCE_FOCUS or stem in tested:
            continue
        status = fm.get("status", "")
        if status in ("検証中", "検証済み"):
            problems.append(Problem("warning", stem, "untested-focus",
                f"重点仮説で status={status} なのに検証活動(TEST)・学び(LEARN)の hypotheses から1本も"
                f"参照されていない（二重表現の破れ／検証実態の欠落の疑い）"))
        else:
            problems.append(Problem("warning", stem, "untested-focus",
                "重点仮説だが検証活動(TEST)・学び(LEARN)が1本も紐づいていない（未着手。/planning で検証を計画する）"))
    return problems


def check_addresses_gaps(project) -> list:
    """OI-F2: 課題↔解決の構造ギャップを検出する（warning）。

    addresses（ソリューション仮説→課題仮説）のグラフ欠落を2方向で拾う（トポロジー由来の
    探索域ギャップ検出。docs/ontology-improvements.md OI-F2）:
    - 課題なき解決: addresses を持てる型（ソリューション仮説）なのに addresses が空。
      solution in search of problem／PSF の危険信号。反証は対象外。
    - 未対応の課題: 検証済みの課題仮説を addresses するソリューション仮説（反証を除く）が
      1本も無い＝未開拓の機会。ただし解決設計フェーズ（ソリューション仮説が重点になる
      ステージ以降）でのみ拾う。CPF/FPF で課題に解決が無いのは正常なため。"""
    problems = []
    addr = RELATIONS_BY_FIELD["addresses"]
    sol_types = addr.domain_subtypes
    prob_types = addr.range_subtypes
    # 反証のソリューションは実質的な対応にならないので除いて「対応済みの課題」集合を作る
    addressed = referenced_ids(project, "addresses",
                               where=lambda fm: fm.get("type") in sol_types and fm.get("status") != "反証")
    # 課題なき解決
    for stem, fm, _, _ in project.hyp_records():
        if (fm.get("type") in sol_types and fm.get("status") != "反証"
                and not parse_id_array(fm.get("addresses", ""))):
            problems.append(Problem("warning", stem, "addresses-gap",
                "ソリューション仮説だが addresses（対応課題）が空"
                "（課題なき解決の疑い。どの課題を解くのか frontmatter に明示する）"))
    # 未対応の課題（解決設計フェーズ＝ソリューション仮説が重点になる最早ステージ以降のみ）
    sol_stages = {s for s, types in STAGE_FOCUS.items() if types & sol_types}
    cur = STAGE_ORDER.index(project.stage) if project.stage in STAGE_ORDER else -1
    if any(cur >= STAGE_ORDER.index(s) for s in sol_stages):
        for stem, fm, _, _ in project.hyp_records():
            if (fm.get("type") in prob_types and fm.get("status") == "検証済み"
                    and stem not in addressed):
                problems.append(Problem("warning", stem, "addresses-gap",
                    "検証済みの課題仮説だが、対応するソリューション仮説（addresses）が無い"
                    "（未開拓の機会。解決設計フェーズでは要検討）"))
    return problems


def check_isolated_hypothesis(project) -> list:
    """どの関係も持たない仮説（グラフから浮いている）を検出する（warning）。

    `check_untested_focus` は重点タイプの `hypotheses` 入次数0だけを見るので、非重点の完全孤立
    （系譜も検証活動も無い）は漏れる。論文 §V.E の連結性診断に対応する層。
    誤検知を避けるため**起票直後（履歴1行のみ・status 未検証）は対象外**——立てた直後に系譜が
    無いのは正常で、警告すると /formulating の直後に必ず鳴ってしまう。"""
    problems = []
    for stem in graph.isolated(project):
        fm, rows = project.records[stem][1], project.history.get(stem, [])
        if len(rows) <= 1 and fm.get("status") == "未検証":
            continue
        problems.append(Problem("warning", stem, "isolated-hypothesis",
            "どの関係も持たない孤立仮説（系譜 derived-from/leads-to も検証活動 hypotheses も無い）"
            "。関係を張るか、取り下げを検討する"))
    return problems


def _days_between(a: str, b: str):
    """YYYY-MM-DD 文字列2つの日数差（b - a）。パースできなければ None。"""
    try:
        return (datetime.date.fromisoformat(b) - datetime.date.fromisoformat(a)).days
    except ValueError:
        return None


def check_stale_confidence(project, today: str = None) -> list:
    """検証済み・高確信度なのに確信度履歴の最終行が古い仮説を検出する（warning）。

    論文の締め「the pipeline is not done when it runs; it is done when you can tell, on any given
    morning, whether what it produced overnight was actually right」に対応する時間軸の診断。
    市場・前提が動く仮説検証ドメインでは「半年前の確信度8」と「昨日の8」は同格でない。

    **確信度は自動で下げない**（不変ルール1）。再検証を促す可視化に留める。
    下げたいときは必ず学び(LEARN)か意思決定(DEC)に紐づけて人が動かす。"""
    problems = []
    today = today or datetime.date.today().isoformat()
    for stem, fm, _, rows in project.hyp_records():
        c = fm.get("confidence", "")
        if fm.get("status") != "検証済み" or not c.isdigit():
            continue
        if int(c) < EVIDENCE_FLOOR_MIN_CONFIDENCE or not rows:
            continue
        age = _days_between(rows[-1]["date"], today)
        if age is not None and age > STALENESS_CONFIDENCE_DAYS:
            problems.append(Problem("warning", stem, "stale-confidence",
                f"status=検証済み・confidence={c} だが確信度履歴の最終行が {rows[-1]['date']}"
                f"（{age}日前・閾値{STALENESS_CONFIDENCE_DAYS}日）。前提が動いていないか再検証を検討する"))
    return problems


def check_stale_test(project, today: str = None) -> list:
    """学び(LEARN)が紐づかない実験計画(TEST)が放置されていないか（warning）。

    計画したのに実施されていない＝board に「未実施」で駐機したままになる。
    実データで AIRE-TEST-002/003 が該当し、どのチェックもカバーしていなかった。"""
    problems = []
    today = today or datetime.date.today().isoformat()
    learned = referenced_ids(project, "learns-from", infix="-LEARN-")
    for stem, (_, fm, _) in project.records.items():
        if entity_of(stem) != "TEST" or stem in learned:
            continue
        age = _days_between(fm.get("date", ""), today)
        if age is not None and age > STALENESS_TEST_DAYS:
            problems.append(Problem("warning", stem, "stale-test",
                f"学び(LEARN)が紐づかない実験計画が {fm.get('date')} から {age}日放置"
                f"（閾値{STALENESS_TEST_DAYS}日）。実施して /learning で学びを積むか、取り下げを検討する"))
    return problems


def check_relation_cycles(project) -> list:
    """H→H 関係（derived-from / leads-to）の自己参照・循環を検出する（error）。"""
    problems = []
    for rel in RELATIONS:
        if not (rel.domains == {"H"} and rel.ranges == {"H"}):
            continue
        graph = {}
        for stem, (_, fm, _) in project.records.items():
            if entity_of(stem) != "H":
                continue
            graph[stem] = [r for r in parse_id_array(fm.get(rel.field, "")) if r in project.records]
        for node, outs in graph.items():
            if node in outs:
                problems.append(Problem("error", node, "relation-cycle",
                    f"{rel.field}（{rel.label}）が自己参照している"))
        # DFS で閉路検出（自己参照は上で報告済みなので除く）
        WHITE, GRAY, BLACK = 0, 1, 2
        color = {n: WHITE for n in graph}
        reported = set()

        def visit(n, path):
            color[n] = GRAY
            for m in graph.get(n, []):
                if m == n:
                    continue
                if color.get(m) == GRAY and m in path:
                    cyc = path[path.index(m):] + [m]
                    key = frozenset(cyc)
                    if key not in reported:
                        reported.add(key)
                        problems.append(Problem("error", n, "relation-cycle",
                            f"{rel.field}（{rel.label}）に循環: {' → '.join(cyc)}"))
                elif color.get(m) == WHITE:
                    visit(m, path + [m])
            color[n] = BLACK

        for n in graph:
            if color[n] == WHITE:
                visit(n, [n])
    return problems


CHECKS = [check_id_matches_filename, check_fields, check_vocabulary,
          check_history_consistency, check_evidence_links,
          check_frontmatter_refs, check_wikilinks, check_relation_wikilinks,
          check_provenance_paths, check_provenance_presence, check_provenance_body_link,
          check_provenance_chain, check_orphan_sources,
          check_relative_links, check_source_links, check_stage_doc,
          check_id_sequence, check_log_sync, check_index_sync, check_fictional_cap,
          check_evidence_tags, check_status_confidence, check_evidence_floor,
          check_dec_based_on, check_untested_focus, check_addresses_gaps,
          check_isolated_hypothesis, check_stale_confidence, check_stale_test,
          check_relation_cycles,
          check_attachment_id, check_attachment_vocabulary, check_attachment_refs,
          check_attachment_backlink]


def lint_project(root: Path) -> list:
    project = Project(root)
    problems = []
    for check in CHECKS:
        problems.extend(check(project))
    return problems


def resolve_targets(repo: Path, args) -> list:
    projects_dir = repo / "projects"
    if args.all:
        return [d for d in sorted(projects_dir.iterdir()) if (d / "wiki").is_dir()]
    slug = resolve_current_project(repo, args.project)   # プロジェクト解決は project.py に一元化
    if not slug or not (projects_dir / slug / "wiki").is_dir():
        sys.exit(f"プロジェクトが見つからない: {slug!r}")
    return [projects_dir / slug]


def main() -> int:
    ap = argparse.ArgumentParser(description="仮説検証Wiki の決定論的 lint")
    ap.add_argument("--project", help="対象プロジェクト slug（省略時は .env の CURRENT_PROJECT → self）")
    ap.add_argument("--all", action="store_true", help="全プロジェクトを対象にする")
    ap.add_argument("--repo", default=".", help="リポジトリルート")
    args = ap.parse_args()
    repo = Path(args.repo).resolve()
    exit_code = 0
    for root in resolve_targets(repo, args):
        problems = lint_project(root)
        errors = [p for p in problems if p.level == "error"]
        warnings = [p for p in problems if p.level == "warning"]
        print(f"== {root.name}: error {len(errors)} / warning {len(warnings)}")
        for p in problems:
            print(f"  [{p.level}] {p.check} | {p.where} | {p.message}")
        if errors:
            exit_code = 1
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
