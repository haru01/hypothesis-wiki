#!/usr/bin/env python3
"""仮説検証Wiki のビュー機械生成（board / list）。

レコード（SSoT）からビューを決定論的に生成する。/view（LLM）と違い推論・要約・因果の
キュレーションは行わず、frontmatter・固定見出し・リンクの射影/逐語転記だけで組む。
「読ませる鋭さ」はレコード側に構造化フィールドとして書いてある前提で読む:
  - 最もリスクの高い前提 = ACT frontmatter `riskiest-assumption`
  - 結果の一行要約       = 学習カード `### 学びの要点`
  - 結果の判定           = ACT frontmatter `outcome`（起票/支持/反証/判断保留/是正）
  - 判断                 = その ACT を `based-on` に含む DEC の type/title
  - 戦略的現在地         = 最新 DEC 本文の `## 次の一手`
  - 因果・核心・対応課題 = H frontmatter `leads-to` / `core` / `addresses`
確信度・ステータス・log は一切変更しない（読み取り専用）。

hwlint.py の Project クラス（records/history/log のパーサ）と共有ヘルパをそのまま再利用する。
"""
import argparse
import datetime
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from hwlint import Project, parse_id_array, strip_comments, entity_of  # noqa: E402
# 型・関係・状態機械の定義は ontology.yaml が唯一の正本（ここに再定義しない）。
from ontology import (  # noqa: E402
    CUSTOMER_TYPES, PROBLEM_TYPES, SOLUTION_TYPES, VALUE_TYPES, WILLING_TYPES, TEAM_TYPES,
    STAGE_FOCUS, STATUS_EMOJI, STATUS_ORDER, LIST_GROUPS, RELATIONS, FICTIONAL_MARKERS,
    STAGE_NAMES, STAGE_ORDER, IMPORTANCE_FOCUS, IMPORTANCE_OTHER,
)


# ---- 共通ヘルパ ----

def read_stage(project) -> str:
    p = project.wiki / "stage.md"
    if p.exists():
        m = re.search(r"current-stage:\s*(\w+)", p.read_text(encoding="utf-8"))
        if m:
            return m.group(1)
    return "?"


def importance(fm, stage) -> int:
    """手動指定(1-10)が優先。auto は重点タイプ=IMPORTANCE_FOCUS・それ以外=IMPORTANCE_OTHER
    （重みの正本は ontology.yaml の importance-weights）。"""
    imp = fm.get("importance", "auto")
    if imp != "auto" and imp.isdigit():
        return int(imp)
    return IMPORTANCE_FOCUS if fm.get("type") in STAGE_FOCUS.get(stage, set()) else IMPORTANCE_OTHER


def fictional_acts(project) -> list:
    """本文に架空/シミュレーションマーカーを含む ACT の stem を並べる。"""
    return sorted(s for s in project.records if "-ACT-" in s
                  and any(m in project.records[s][2] for m in FICTIONAL_MARKERS))


def next_to_verify(hyps, stage) -> list:
    """アサンプションマッピング「重要×証拠なし」象限＝重要度8 × 確信度低 × 未検証/検証中。"""
    nxt = [(s, fm) for s, fm, *_ in hyps
           if importance(fm, stage) >= IMPORTANCE_FOCUS and fm.get("status") in {"未検証", "検証中"}]
    return sorted(nxt, key=lambda x: (int(x[1].get("confidence", "0") or 0), x[0]))


def testcard(text: str) -> str:
    m = re.search(r"## テストカード.*?(?=## 学習カード|\Z)", text, re.DOTALL)
    return m.group(0) if m else ""


def learning(text: str) -> str:
    m = re.search(r"## 学習カード.*\Z", text, re.DOTALL)
    return m.group(0) if m else ""


def collapse(text: str) -> str:
    """複数行・箇条書きを1行に畳む（インライン項目用）。HTMLコメントは除去。"""
    # 行頭のリストマーカー（- / * / + の後に空白）だけを除去する。太字 **…** の * は食わない。
    parts = [re.sub(r"^\s*[-*+]\s+", "", ln).strip()
             for ln in strip_comments(text).strip().splitlines() if ln.strip()]
    return " ".join(parts) if parts else "—"


def field_value(section: str, label: str) -> str:
    """テストカードのフィールドを逐語抽出。見出し形式（### 方法）と箇条書き形式
    （- **方法**: …、成功基準（開始前に確定）等の接尾辞・多行ネストも可）の両方に対応する。"""
    m = re.search(rf"^###\s*{label}[^\n]*\n(.*?)(?=\n##|\Z)", section, re.DOTALL | re.MULTILINE)
    if not m:
        # 箇条書き形式。太字の内外どちらの接尾辞（**方法**: / **成功基準**（開始前に確定）:）にも対応。
        m = re.search(rf"^-\s*\*\*{label}[^*\n]*\*\*[^:：\n]*[:：]\s*(.*?)(?=\n-\s*\*\*|\n###|\n##|\Z)",
                      section, re.DOTALL | re.MULTILINE)
    if not m:
        return "—"
    block = re.split(r"\n\s*\|", m.group(1), maxsplit=1)[0]   # 表はサマリから落とす（詳細はレコード参照）
    return collapse(block)


def h3_block(section: str, header: str) -> str:
    """学習カードの `### <header>` ブロックを次の見出しまで逐語抽出する。"""
    m = re.search(rf"###\s*{re.escape(header)}[^\n]*\n(.*?)(?=\n### |\n## |\Z)", section, re.DOTALL)
    return m.group(1).strip() if m else ""


def is_executed(lc: str) -> bool:
    """学習カードが実際に記入済みか（未実施の計画 ACT はプレースホルダのみ）を判定する。"""
    real = [ln.strip() for ln in strip_comments(h3_block(lc, "事実（observed）")).splitlines()
            if ln.strip() and not ln.strip().startswith("（") and "記入" not in ln
            and not ln.strip().startswith("観測した事実")]
    return bool(real)


def learning_point(lc: str) -> str:
    return collapse(h3_block(lc, "学びの要点"))


def hyp_links(project, ids, types) -> str:
    out = [f"[[{rid}]]" for rid in ids
           if (rec := project.records.get(rid)) and rec[1].get("type") in types]
    return " ".join(out) if out else "—"


def index_by(project, kind, key_field) -> dict:
    """`kind`（例 "-ACT-" / "-DEC-"）のレコードの key_field 配列を逆引き辞書にする。
    値は参照している当該レコード stem のリスト（挿入順）。"""
    idx = {}
    for stem, (_, fm, _) in project.records.items():
        if kind in stem:
            for ref in parse_id_array(fm.get(key_field, "")):
                idx.setdefault(ref, []).append(stem)
    return idx


def latest_dec_next_move(project):
    """最新 DEC（date 昇順の末尾）の `## 次の一手` を返す。無ければ (None, None)。"""
    decs = sorted((s for s in project.records if "-DEC-" in s),
                  key=lambda s: (project.records[s][1].get("date", ""), s))
    if not decs:
        return None, None
    stem = decs[-1]
    m = re.search(r"##\s*次の一手\s*\n(.*?)(?=\n##|\Z)", project.records[stem][2], re.DOTALL)
    return stem, (collapse(m.group(1)) if m else None)


def header_lines(view: str, stage: str, today: str, fictional: list) -> list:
    """生成物マーカー＋架空データ警告。fictional は架空 ACT の stem リスト。"""
    lines = [f"<!-- 生成物: gen_views.py {view} による機械生成。手編集禁止。"
             f"`python3 tools/gen_views.py {view}` で再生成する。生成基準日: {today}（ステージ {stage}） -->"]
    if fictional:
        links = " ".join(f"[[{s}]]" for s in fictional)
        lines.append(f"<!-- ⚠️ 架空/シミュレーションデータを含む活動: {links}。"
                     f"これら由来の確信度・判断は実データ未検証。 -->")
    return lines


# ---- board ビュー ----

def gen_board(project) -> str:
    stage = read_stage(project)
    today = datetime.date.today().isoformat()
    hyps = list(project.hyp_records())
    acts = sorted((s for s in project.records if "-ACT-" in s),
                  key=lambda s: (project.records[s][1].get("date", ""), s))

    # ACT→DEC 逆引きを1回だけ構築（判断列。全レコード再走査を避ける）
    dec_by_act = {}
    for stem, (_, fm, _) in project.records.items():
        if "-DEC-" in stem:
            label = f"{fm.get('type', '')}: {fm.get('title', '')} [[{stem}]]"
            for a in parse_id_array(fm.get("based-on", "")):
                dec_by_act.setdefault(a, []).append(label)

    def entry(stem) -> dict:
        _, fm, text = project.records[stem]
        lc = learning(text)
        executed = is_executed(lc)
        tc = testcard(text)
        return {
            "fm": fm, "ids": parse_id_array(fm.get("hypotheses", "")),
            "risk": fm.get("riskiest-assumption", "—") or "—",
            "method": field_value(tc, "方法"), "criteria": field_value(tc, "成功基準"),
            "result": (learning_point(lc) or "—") if executed else "（未実施・計画のみ）",
            "outcome": fm.get("outcome", "").strip() or ("—" if executed else "未実施"),
            "judgment": " / ".join(dec_by_act.get(stem, [])) or "—",
        }

    entries = {s: entry(s) for s in acts}

    L = header_lines("board", stage, today, fictional_acts(project))
    L += ["", f"# ジャベリン実験ボード（{project.slug}）", ""]
    L.append("各 ACT を1実験として date 昇順に並べる。「最もリスクの高い前提」「結果（学びの要点）」「判定」は"
             "レコード（ACT frontmatter `riskiest-assumption`/`outcome`・学習カード `学びの要点`）、"
             "「判断」は当該 ACT を `based-on` に持つ DEC 由来。すべて射影・逐語転記。")
    L.append("")

    # サマリ
    L += ["## サマリ", "", "| # | 実験 | 最もリスクの高い前提 | 判定 | 判断（DEC） |", "|---|---|---|---|---|"]
    for i, s in enumerate(acts, 1):
        e = entries[s]
        L.append(f"| {i} | [[{s}]] {e['fm'].get('title', '')} | {e['risk']} | {e['outcome']} | {e['judgment']} |")
    L += ["", "---", ""]

    # 各実験（1 ACT = 1 エントリ・鋭い一行に集約）
    for i, s in enumerate(acts, 1):
        e = entries[s]
        fm = e["fm"]
        L.append(f"## 実験{i} — {fm.get('title', '')}"
                 f"（{fm.get('date', '')}・{fm.get('type', '')}） [[{s}]]")
        target = (f"- **対象仮説**: 顧客/行動 {hyp_links(project, e['ids'], CUSTOMER_TYPES)}"
                  f" ｜ 課題 {hyp_links(project, e['ids'], PROBLEM_TYPES)}"
                  f" ｜ 解決策 {hyp_links(project, e['ids'], SOLUTION_TYPES)}")
        team = hyp_links(project, e['ids'], TEAM_TYPES)   # 自分たち仮説は該当時のみ表示（役割の取りこぼし防止）
        if team != "—":
            target += f" ｜ 自分たち {team}"
        L += [
            "",
            target,
            f"- **最もリスクの高い前提**: {e['risk']}",
            f"- **検証方法**: {e['method']}",
            f"- **成功基準**: {e['criteria']}",
            f"- **結果（学びの要点）**: {e['result']}",
            f"- **判定 / 判断**: {e['outcome']} ／ {e['judgment']}",
            "",
            "---",
            "",
        ]

    # 現在地（機械集計＋最新DECの戦略的現在地）
    progress = " → ".join(f"**{st}**" if st == stage else st for st in STAGE_ORDER)
    L += ["## 現在地", "",
          f"- ステージ: **{stage}** {STAGE_NAMES.get(stage, '')}",
          f"- 進捗: {progress}"]
    dec_stem, next_move = latest_dec_next_move(project)
    if next_move:
        L.append(f"- 次の一手（[[{dec_stem}]] より）: {next_move}")
    L.append("")
    L += ["| 仮説 | タイプ | 確信度 | ステータス | 重要度 |", "|---|---|---|---|---|"]
    for stem, fm, _, _ in sorted(hyps, key=lambda r: (-importance(r[1], stage),
                                                       int(r[1].get("confidence", "0") or 0))):
        emo = STATUS_EMOJI.get(fm.get("status", ""), "")
        L.append(f"| [[{stem}]] {fm.get('title', '')} | {fm.get('type', '')} | "
                 f"{fm.get('confidence', '')} | {emo}{fm.get('status', '')} | {importance(fm, stage)} |")
    L += ["", f"**次に検証すべき仮説**（重要度{IMPORTANCE_FOCUS} × 確信度低 × 未検証/検証中）:", ""]
    for stem, fm in next_to_verify(hyps, stage):
        L.append(f"- [[{stem}]] {fm.get('title', '')}"
                 f"（確信度{fm.get('confidence', '')}・{fm.get('status', '')}）")
    L.append("")
    return "\n".join(L)


# ---- list ビュー ----
# mermaid subgraph / タイプ別テーブルのグループ（key, 見出し, subgraph ラベル, 該当タイプ）は
# ontology.yaml の H サブタイプ（key / chain-label）から LIST_GROUPS として供給される。


def mermaid_id(stem: str) -> str:
    return stem.replace("-", "_")


def short_id(stem: str) -> str:
    m = re.search(r"((?:H|ACT|DEC)-\d+)$", stem)
    return m.group(1) if m else stem


def trunc(s: str, n: int = 16) -> str:
    return s if len(s) <= n else s[:n] + "…"


def latest_reason(history) -> str:
    """確信度履歴の最終行の根拠セル（list の「直近の根拠」列に射影）。"""
    return history[-1]["reason"] if history else ""


def is_core(fm) -> bool:
    return fm.get("core", "").strip() == "true"


def related_links(stem, fm, act_by_hyp) -> str:
    """派生元(←)・因果先(→ leads-to)・検証活動(ACT逆引き) を1セルに畳む。"""
    parts = []
    if (df := fm.get("derived-from", "").strip()):
        parts.append(f"← [[{df}]]")
    if (lt := parse_id_array(fm.get("leads-to", ""))):
        parts.append("→ " + " ".join(f"[[{t}]]" for t in lt))
    if (acts := sorted(act_by_hyp.get(stem, []))):
        parts.append(" ".join(f"[[{a}]]" for a in acts))
    return " ・ ".join(parts) if parts else "—"


def gen_list(project) -> str:
    stage = read_stage(project)
    today = datetime.date.today().isoformat()
    hyps = list(project.hyp_records())  # (stem, fm, body, history)
    stems = {s for s, _, _, _ in hyps}
    act_by_hyp = index_by(project, "-ACT-", "hypotheses")  # H→ACT 逆引きを1回だけ構築

    L = header_lines("list", stage, today, fictional_acts(project))
    L += ["", f"# 全仮説リスト（{project.slug}）", ""]
    L.append(f"現在ステージ: **{stage}**。重要度は {stage} 重点タイプ=8・その他=4 で算出（frontmatter 射影）。"
             "★=核心仮説（`core`）。関連列は ← 派生元／→ 因果先（`leads-to`）／検証活動（ACT）。")

    # mermaid バリューチェーン（ノード=frontmatter、矢印=leads-to）
    L += ["", "## バリューチェーン（行動 → 切実な課題 → 解決策 → 市場）", "", "```mermaid", "flowchart TB"]
    for key, _, sublabel, types in LIST_GROUPS:
        members = [(s, fm) for s, fm, _, _ in hyps if fm.get("type") in types]
        if not members:
            continue
        L.append(f'    subgraph {key}["{sublabel}"]')
        for s, fm in members:
            core = "★" if is_core(fm) else ""
            status = fm.get("status", "")
            emo = STATUS_EMOJI.get(status, "")
            label = fm.get("short-title", "").strip() or trunc(fm.get("title", ""))
            lbl = f'{short_id(s)}{core} {label}<br/>確信度{fm.get("confidence", "")} {emo}{status}'
            L.append(f'      {mermaid_id(s)}["{lbl}"]')
        L.append("    end")
    for s, fm, _, _ in hyps:
        for t in parse_id_array(fm.get("leads-to", "")):
            if t in stems:
                L.append(f"    {mermaid_id(s)} --> {mermaid_id(t)}")
    L += ["```", ""]

    # タイプ別テーブル（確信度降順）
    for _, heading, _, types in LIST_GROUPS:
        members = sorted([(s, fm, hist) for s, fm, _, hist in hyps if fm.get("type") in types],
                         key=lambda x: -int(x[1].get("confidence", "0") or 0))
        if not members:
            continue
        L += [f"## {heading}", "", "| ID | タイトル | 確信度 | ステータス | 重要度 | 関連 | 直近の根拠 |",
              "|---|---|---|---|---|---|---|"]
        for s, fm, hist in members:
            core = "★" if is_core(fm) else ""
            emo = STATUS_EMOJI.get(fm.get("status", ""), "")
            L.append(f"| [[{s}]]{core} | {fm.get('title', '')} | {fm.get('confidence', '')} | "
                     f"{emo}{fm.get('status', '')} | {importance(fm, stage)} | {related_links(s, fm, act_by_hyp)} | "
                     f"{trunc(latest_reason(hist), 44)} |")
        L.append("")

    # 次に検証すべき
    L += ["## 次に検証すべき仮説（重要度8 × 確信度低 × 未検証/検証中）", ""]
    for s, fm in next_to_verify(hyps, stage):
        L.append(f"- [[{s}]] {fm.get('title', '')}（確信度{fm.get('confidence', '')}・{fm.get('status', '')}）")
    L.append("")

    # タイプ別サマリ（クロス集計）
    L += ["## タイプ別サマリ", "", "| タイプ | 件数 | 検証済み | 検証中 | 未検証 | 反証 |",
          "|---|---|---|---|---|---|"]
    for _, heading, _, types in LIST_GROUPS:
        members = [fm for s, fm, _, _ in hyps if fm.get("type") in types]
        if not members:
            continue
        c = {st: sum(1 for fm in members if fm.get("status") == st) for st in STATUS_ORDER}
        L.append(f"| {heading} | {len(members)} | {c['検証済み']} | {c['検証中']} | "
                 f"{c['未検証']} | {c['反証']} |")
    L.append("")
    return "\n".join(L)


# ---- vp（バリュープロポジション）ビュー ----
# vp は現在 VIEWS 未登録・生成停止中（「直近の根拠」は list へ統合済み）。
# 復活させるときは VIEWS に "vp": ("value-proposition.md", gen_vp) を再登録するだけでよい。
# VALUE_TYPES（ソリューション仮説）/ WILLING_TYPES（市場スケール仮説）は ontology.yaml の
# H サブタイプ role（solution / market）から供給される。


def gen_vp(project):
    """ソリューション仮説が無ければ None（vp は組めない＝生成しない）。"""
    hyps = list(project.hyp_records())
    values = [(s, fm) for s, fm, _, _ in hyps if fm.get("type") in VALUE_TYPES]
    if not values:
        return None
    stage = read_stage(project)
    today = datetime.date.today().isoformat()
    jobs = [(s, fm) for s, fm, _, _ in hyps if fm.get("type") in CUSTOMER_TYPES]
    pains = sorted([(s, fm, hist) for s, fm, _, hist in hyps if fm.get("type") in PROBLEM_TYPES],
                   key=lambda x: -int(x[1].get("confidence", "0") or 0))
    willing = [(s, fm) for s, fm, _, _ in hyps if fm.get("type") in WILLING_TYPES]

    # ソリューション→対応課題を1回だけ走査し、被対応ペインと pain→values の両方を作る
    addressed, values_by_pain = set(), {}
    for s, fm in values:
        for t in parse_id_array(fm.get("addresses", "")):
            addressed.add(t)
            values_by_pain.setdefault(t, []).append(s)

    L = header_lines("vp", stage, today, fictional_acts(project))
    L += ["", f"# バリュープロポジション・ビュー（{project.slug}）", ""]
    L.append("顧客プロファイル（ジョブ・ペイン）と価値マップ（ソリューション）を frontmatter から射影し、"
             "`addresses`（ソリューション→対応課題）で突き合わせる。フィットの空白は機械集計。")

    L += ["", "## 顧客のジョブ（状況・行動仮説）", ""]
    for s, fm in jobs:
        L.append(f"- [[{s}]] {fm.get('title', '')}（確信度{fm.get('confidence', '')}・{fm.get('status', '')}）")
    if not jobs:
        L.append("- （状況・行動仮説なし）")

    L += ["", "## ペイン（切実度＝確信度順）", "",
          "| 順位 | ペイン | 確信度 | ステータス | 対応する価値 | 直近の根拠 |", "|---|---|---|---|---|---|"]
    for i, (s, fm, hist) in enumerate(pains, 1):
        vs = values_by_pain.get(s, [])
        cov = " ".join(f"[[{v}]]" for v in vs) if vs else "**空白**"
        emo = STATUS_EMOJI.get(fm.get("status", ""), "")
        L.append(f"| {i} | [[{s}]] {fm.get('title', '')} | {fm.get('confidence', '')} | "
                 f"{emo}{fm.get('status', '')} | {cov} | {trunc(latest_reason(hist), 44)} |")

    L += ["", "## 価値マップ（ソリューション → 対応ペイン）", "",
          "| 価値（ソリューション仮説） | 確信度 | ステータス | 対応ペイン（addresses） |", "|---|---|---|---|"]
    for s, fm in values:
        addr = parse_id_array(fm.get("addresses", ""))
        addr_s = " ".join(f"[[{t}]]" for t in addr) if addr else "**未指定**"
        emo = STATUS_EMOJI.get(fm.get("status", ""), "")
        L.append(f"| [[{s}]] {fm.get('title', '')} | {fm.get('confidence', '')} | "
                 f"{emo}{fm.get('status', '')} | {addr_s} |")
    if willing:
        L += ["", "**市場スケール（規模・チャネル・プル）**: "
              + " ".join(f"[[{s}]]（確信度{fm.get('confidence', '')}・{fm.get('status', '')}）"
                         for s, fm in willing)]

    uncovered = [s for s, fm, _ in pains if s not in addressed]
    refuted = [s for s, fm in values if fm.get("status") == "反証"]
    L += ["", "## フィット所見（機械集計）", ""]
    L.append("- **未カバーのペイン**（対応する価値がない）: "
             + (" ".join(f"[[{s}]]" for s in uncovered) if uncovered else "なし"))
    if refuted:
        L.append("- **反証された価値**（価値マップの再設計が要る）: " + " ".join(f"[[{s}]]" for s in refuted))
    L.append("")
    return "\n".join(L)


# ---- relations（関係グラフ）ビュー ----
# オントロジーの型付き関係（derived-from/leads-to/addresses/hypotheses/based-on）を
# frontmatter から射影する。list の mermaid が leads-to だけなのに対し、こちらは全関係型を
# 1枚のグラフに描き、逆方向(inverse)のバックリンク索引と addresses フィットも出す。

def node_label(project, stem) -> str:
    """関係グラフのノードラベル（H は核心★・ステータス、ACT/DEC はタイトル）。"""
    fm = project.records[stem][1]
    if entity_of(stem) == "H":
        core = "★" if is_core(fm) else ""
        emo = STATUS_EMOJI.get(fm.get("status", ""), "")
        label = fm.get("short-title", "").strip() or trunc(fm.get("title", ""))
        return (f'{short_id(stem)}{core} {label}<br/>'
                f'確信度{fm.get("confidence", "")} {emo}{fm.get("status", "")}')
    return f'{short_id(stem)} {trunc(fm.get("title", ""), 20)}'


def relation_edges(project) -> list:
    """(relation, 始点stem, 終点stem) を frontmatter から収集する。
    終点が同一プロジェクトに実在し range 種別が一致する辺だけを返す。"""
    edges = []
    for stem, (_, fm, _) in project.records.items():
        ent = entity_of(stem)
        for rel in RELATIONS:
            if rel.domain != ent:
                continue
            for tgt in parse_id_array(fm.get(rel.field, "")):
                if tgt in project.records and entity_of(tgt) == rel.range:
                    edges.append((rel, stem, tgt))
    return edges


def gen_relations(project):
    if not project.records:
        return None
    stage = read_stage(project)
    today = datetime.date.today().isoformat()
    edges = relation_edges(project)

    L = header_lines("relations", stage, today, fictional_acts(project))
    L += ["", f"# 関係グラフ（{project.slug}）", ""]
    L.append("レコード間の型付きリンク（オントロジーの関係）を frontmatter から射影する。"
             "ノード=レコード、矢印=関係（ラベル=関係名）。関係の定義は "
             "[ontology.md](../../../../ontology.md) を参照。")

    # 型付き関係グラフ（全関係型を1枚に）
    L += ["", "## 型付き関係グラフ", "", "```mermaid", "flowchart LR"]
    for ent, sub_label in (("H", "仮説 H"), ("ACT", "活動 ACT"), ("DEC", "意思決定 DEC")):
        members = sorted(s for s in project.records if entity_of(s) == ent)
        if not members:
            continue
        L.append(f'    subgraph {ent}["{sub_label}"]')
        for s in members:
            L.append(f'      {mermaid_id(s)}["{node_label(project, s)}"]')
        L.append("    end")
    for rel, s, t in edges:
        L.append(f"    {mermaid_id(s)} -->|{rel.label}| {mermaid_id(t)}")
    L += ["```", ""]

    # 関係インデックス（forward・全関係型を必ず節として出す。0件でも「該当なし」で存在を示す）
    L += ["## 関係インデックス", ""]
    for rel in RELATIONS:
        rel_edges = [(s, t) for r, s, t in edges if r.name == rel.name]
        L += [f"### {rel.label}（`{rel.field}`: {rel.domain}→{rel.range}）", ""]
        if not rel_edges:
            L += ["（該当なし）", ""]
            continue
        L += ["| 始点 | 関係 | 終点 |", "|---|---|---|"]
        for s, t in rel_edges:
            L.append(f"| [[{s}]] | {rel.label} → | [[{t}]] |")
        L.append("")

    # バックリンク索引（inverse・誰から参照されているか）
    incoming = {}
    for rel, s, t in edges:
        incoming.setdefault(t, {}).setdefault(rel.inverse_label, []).append(s)
    L += ["## バックリンク索引（誰から・どの関係で参照されているか）", ""]
    referenced = [s for s in sorted(project.records) if s in incoming]
    for stem in referenced:
        seg = " ／ ".join(f"{lbl}: " + " ".join(f"[[{x}]]" for x in srcs)
                          for lbl, srcs in incoming[stem].items())
        L.append(f"- [[{stem}]] ← {seg}")
    if not referenced:
        L.append("（被参照リンクがまだ無い）")
    L.append("")

    # 課題↔ソリューション フィット（addresses の復活）
    pains = [(s, project.records[s][1]) for s in sorted(project.records)
             if project.records[s][1].get("type") in PROBLEM_TYPES]
    values = [s for s in sorted(project.records)
              if project.records[s][1].get("type") in SOLUTION_TYPES]
    if pains and values:
        values_by_pain = {}
        for r, s, t in edges:
            if r.name == "addresses":
                values_by_pain.setdefault(t, []).append(s)
        def refuted(v):
            return project.records[v][1].get("status") == "反証"

        L += ["## 課題↔ソリューション フィット（addresses）", "",
              "ソリューション仮説の `addresses`（対応課題）で突き合わせる。"
              "反証された価値は ⚠️反証 を付す（実質的な対応にならない）。", "",
              "| 課題 | 対応する価値（ソリューション） |", "|---|---|"]
        for s, fm in pains:
            vs = values_by_pain.get(s, [])
            cov = " ".join(f"[[{v}]]{'⚠️反証' if refuted(v) else ''}" for v in vs) if vs else "**空白**"
            L.append(f"| [[{s}]] {fm.get('title', '')} | {cov} |")
        uncovered = [s for s, _ in pains if s not in values_by_pain]
        # 値はあるが全て反証＝実質未カバー（反証された価値でしか対応されていない）
        effectively = [s for s, _ in pains
                       if values_by_pain.get(s) and all(refuted(v) for v in values_by_pain[s])]
        L += ["", "- **未カバーの課題**（対応する価値がない）: "
              + (" ".join(f"[[{s}]]" for s in uncovered) if uncovered else "なし")]
        L.append("- **実質未カバー**（反証された価値でしか対応されていない）: "
                 + (" ".join(f"[[{s}]]" for s in effectively) if effectively else "なし"))
        if not values_by_pain:
            L.append("- ※ どの課題にも `addresses` が張られていない"
                     "（ソリューション仮説の frontmatter に `addresses: [課題ID]` を書くとフィットが埋まる）")
        L.append("")
    return "\n".join(L)


VIEWS = {
    "board": ("board.md", gen_board),
    "list": ("hypotheses-list.md", gen_list),
    "relations": ("relations.md", gen_relations),
}


def resolve_slug(repo: Path, project):
    if project:
        return project
    cur = (repo / "projects" / "current.md").read_text(encoding="utf-8")
    m = re.search(r"current-project:\s*(\S+)", cur)
    return m.group(1) if m else None


def main() -> int:
    ap = argparse.ArgumentParser(description="仮説検証Wiki のビュー機械生成（board / list）")
    ap.add_argument("view", choices=list(VIEWS))
    ap.add_argument("--project", help="対象プロジェクト slug（省略時は projects/current.md）")
    ap.add_argument("--repo", default=".", help="リポジトリルート")
    ap.add_argument("--out", help="出力先パス（省略時は wiki/views/<既定名> に書き込む）")
    args = ap.parse_args()
    repo = Path(args.repo).resolve()
    slug = resolve_slug(repo, args.project)
    root = repo / "projects" / (slug or "")
    if not slug or not (root / "wiki").is_dir():
        sys.exit(f"プロジェクトが見つからない: {slug!r}")
    filename, fn = VIEWS[args.view]
    out = fn(Project(root))
    if out is None:
        print(f"{slug}/{args.view}: 生成条件を満たさずスキップ（例: ソリューション仮説が未起票）")
        return 0
    dest = Path(args.out) if args.out else (root / "wiki" / "views" / filename)
    dest.write_text(out, encoding="utf-8")
    print(f"生成: {dest}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
