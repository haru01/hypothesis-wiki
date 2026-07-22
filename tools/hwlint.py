#!/usr/bin/env python3
"""仮説検証Wiki の決定論的 lint。

CLAUDE.md の不変ルールのうち機械検証可能なものだけをチェックする。
意味的チェック（矛盾する仮説・長期放置など）は /lint スキル（LLM）が担い、両者で併用する。
"""
import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
# 語彙(enum)・型・関係・状態機械の定義は ontology.yaml が唯一の正本。ここには再定義しない。
from ontology import (  # noqa: E402
    STATUSES, STAGES, H_TYPES, ACT_TYPES, DEC_TYPES,
    CONFIDENCE_MIN, CONFIDENCE_MAX, FICTIONAL_CAP, FICTIONAL_MARKERS,
    EVIDENCE_TAGS, EVIDENCE_LADDER, EVIDENCE_RANK, EVIDENCE_FLOOR,
    STATUS_BOUNDS, RELATIONS, RELATIONS_BY_FIELD, STAGE_FOCUS, STAGE_ORDER,
    IMPORTANCE_FOCUS,
)
# レコードモデル層（frontmatter/履歴/log のパーサと Project）は records.py に集約。
# ここから import することで、lint と gen_views が同じモデルを共有する（linter へのモデル依存の解消）。
from records import (  # noqa: E402
    HISTORY_HEADER, parse_frontmatter, parse_id_array, entity_of,
    strip_frontmatter, strip_comments, parse_history, referenced_ids,
    importance, current_slug, Project,
)


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
                                "レコード名が ID 規約（<PREFIX>-H/ACT/DEC-NNN）に合わない"))
    return problems


def check_vocabulary(project) -> list:
    """status・type・stage・confidence の語彙/範囲を規約に照らして検証する。"""
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
        if "-ACT-" in stem and fm.get("type") not in ACT_TYPES:
            problems.append(Problem("error", stem, "vocab", f"type '{fm.get('type')}' は規約外"))
        if "-DEC-" in stem and fm.get("type") not in DEC_TYPES:
            problems.append(Problem("error", stem, "vocab", f"type '{fm.get('type')}' は規約外"))
        if ("-H-" in stem or "-ACT-" in stem) and fm.get("stage") not in STAGES:
            problems.append(Problem("error", stem, "vocab", f"stage '{fm.get('stage')}' は規約外"))
    return problems


EVIDENCE_RE = re.compile(r"\[\[([A-Z0-9]+-(?:ACT|DEC)-\d+)\]\]")


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
    """不変ルール1: 初期行以降の確信度・ステータス変更は必ず実在する ACT/DEC に紐づく。"""
    problems = []
    for stem, _, _, rows in project.hyp_records():
        for i, row in enumerate(rows):
            if i == 0:
                continue  # 初期作成行のみ根拠レコード免除（desk-research を書くのは任意）
            ids = EVIDENCE_RE.findall(row["activity"])
            if not ids:
                problems.append(Problem("error", stem, "evidence",
                    f"履歴 {row['date']} 行（確信度{row['confidence']}）に [[ACT/DEC]] の証拠リンクが無い"))
            for rid in ids:
                if rid not in project.records:
                    problems.append(Problem("error", stem, "evidence",
                        f"履歴の証拠 [[{rid}]] のレコードが存在しない"))
    return problems


WIKILINK_RE = re.compile(r"\[\[([^\]|#]+)(?:[|#][^\]]*)?\]\]")


def check_frontmatter_refs(project) -> list:
    """frontmatter の関係リンクを ontology.yaml の宣言で検証する。

    各関係（derived-from / leads-to / addresses / hypotheses / based-on）について、
    その関係の domain 種別を持つレコードの frontmatter 参照を、接頭辞つき・実在・
    range 種別・（サブタイプ制約があればサブタイプ）・（単一関係の）cardinality で検証する。
    """
    problems = []
    prefix = project.prefix
    for stem, (_, fm, _) in project.records.items():
        ent = entity_of(stem)
        for rel in RELATIONS:
            if rel.domain != ent:
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
                # range 種別（例: hypotheses は H を、based-on は ACT を指す）
                target_fm = project.records[rid][1]
                if entity_of(rid) != rel.range:
                    problems.append(Problem("error", stem, "refs",
                        f"frontmatter {rel.field} '{rid}' は {rel.range} を指すべき"
                        f"（{entity_of(rid)} を指している）"))
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
    for stem, (_, fm, body) in project.records.items():
        ent = entity_of(stem)
        body_links = {t.strip() for t in WIKILINK_RE.findall(strip_comments(strip_frontmatter(body)))}
        for rel in RELATIONS:
            if rel.domain != ent or not rel.must_wikilink:
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
    for stem, (_, _, body) in project.records.items():
        for target in WIKILINK_RE.findall(strip_comments(strip_frontmatter(body))):
            target = target.strip()
            if "/" in target:
                problems.append(Problem("error", stem, "wikilink",
                    f"[[{target}]] — schema層への参照は wikilink でなく相対mdリンクで書く規約"))
            elif target not in all_names:
                problems.append(Problem("error", stem, "wikilink", f"[[{target}]] が解決しない（リンク切れ）"))
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
    for kind in ("H", "ACT", "DEC"):
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
    架空根拠も取りこぼさない）。行の根拠が架空と判定されるのは、(a) 紐づく ACT が
    架空マーカーを含む、(b) 根拠セルに 〈架空〉タグ、のいずれか。根拠セルの地の文に
    架空マーカー語が出るだけ（例: 架空データに言及した注記）では判定しない
    （構造化シグナルに一本化して誤検出を避ける）。"""
    problems = []
    fictional_acts = {stem for stem, (_, _, body) in project.records.items()
                      if "-ACT-" in stem and any(m in body for m in FICTIONAL_MARKERS)}
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

    根拠タグに階梯タグが1つも無い場合は evidence-tag / fictional-cap の担当なので二重報告しない。
    階梯タグが在るのにその最強が要求段未満のときだけ warning にする。"""
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
                "DEC に based-on（根拠活動）が無い（意思決定は活動 [[ACT-NNN]] に紐づける）"))
    return problems


def check_untested_focus(project) -> list:
    """OI-F1: 重点仮説なのに検証活動(ACT)の hypotheses 入次数が0のものを検出する（warning）。

    重点＝現ステージの重点タイプ（stage-focus）か、手動 importance>=IMPORTANCE_FOCUS のH。
    「重要なのに検証実験が1本も紐づいていない」を構造事実（入次数0）で拾う。トポロジー由来の
    探索域ギャップ検出（docs/ontology-improvements.md OI-F1）。status が検証中/検証済みなら、
    検証したと主張しているのに ACT からの逆リンクが無い二重表現の破れ（食い違い）でもある。"""
    problems = []
    tested = referenced_ids(project, "hypotheses", infix="-ACT-")
    for stem, fm, _, _ in project.hyp_records():
        if importance(fm, project.stage) < IMPORTANCE_FOCUS or stem in tested:
            continue
        status = fm.get("status", "")
        if status in ("検証中", "検証済み"):
            problems.append(Problem("warning", stem, "untested-focus",
                f"重点仮説で status={status} なのに検証活動(ACT)の hypotheses から1本も"
                f"参照されていない（二重表現の破れ／検証実態の欠落の疑い）"))
        else:
            problems.append(Problem("warning", stem, "untested-focus",
                "重点仮説だが検証活動(ACT)が1本も紐づいていない（未着手。/plan で検証を計画する）"))
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


def check_relation_cycles(project) -> list:
    """H→H 関係（derived-from / leads-to）の自己参照・循環を検出する（error）。"""
    problems = []
    for rel in RELATIONS:
        if not (rel.domain == "H" and rel.range == "H"):
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


CHECKS = [check_id_matches_filename, check_vocabulary, check_history_consistency, check_evidence_links,
          check_frontmatter_refs, check_wikilinks, check_relation_wikilinks,
          check_id_sequence, check_log_sync, check_index_sync, check_fictional_cap,
          check_evidence_tags, check_status_confidence, check_evidence_floor,
          check_dec_based_on, check_untested_focus, check_addresses_gaps,
          check_relation_cycles]


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
    slug = args.project or current_slug(repo)   # プロジェクト解決は records.current_slug に一元化
    if not slug or not (projects_dir / slug / "wiki").is_dir():
        sys.exit(f"プロジェクトが見つからない: {slug!r}")
    return [projects_dir / slug]


def main() -> int:
    ap = argparse.ArgumentParser(description="仮説検証Wiki の決定論的 lint")
    ap.add_argument("--project", help="対象プロジェクト slug（省略時は projects/current.md の current-project）")
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
