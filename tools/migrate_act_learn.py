#!/usr/bin/env python3
"""一度きりの移行スクリプト: 活動レコード(ACT)を「実験計画(ACT=テストカード)」と
「学び(LEARN=学習カード)」に分割する（docs/migrations/2026-07-act-learn-split.md 参照）。

分類（明示・データ駆動）:
  SPLIT   計画型で学習カード記入済み  → ACT はテストカードのみに縮小し、新規 LEARN を作成（learns-from=ACT）
  CONVERT 回顧型（desk-research/self-reflection） → 新規 LEARN を作成し、旧 ACT を削除（番号は欠番）
  STRIP   計画型で学習カード未記入      → ACT はテストカードのみに縮小（LEARN は作らない）

副作用:
  - 仮説(H)・意思決定(DEC)・stage.md の確信度履歴/根拠 citation を [[ACT]]→[[LEARN]] に張り替える。
  - 削除 ACT を指す全参照を LEARN へ張り替え（フォールバックを残さない完全移行）。
  - log.md に移行の事実を追記（欠番の取り下げ記録を含む）。
本文は `## 学習カード` 境界で逐語分割し、転記誤りを避ける。sources/ は不変なので触らない。
冪等ではない（1回だけ実行する）。実行後は hwlint とビュー再生成で検証すること。
"""
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent

# ── 移行計画（プロジェクトごと。ACT id → LEARN id） ──────────────────────
PLAN = {
    "self": {
        "convert": {"SELF-ACT-001": "SELF-LEARN-001", "SELF-ACT-005": "SELF-LEARN-005"},
        "split":   {"SELF-ACT-002": "SELF-LEARN-002", "SELF-ACT-003": "SELF-LEARN-003",
                    "SELF-ACT-004": "SELF-LEARN-004"},
        "strip":   [],
    },
    "ai-reskilling": {
        "convert": {"AIRE-ACT-001": "AIRE-LEARN-001", "AIRE-ACT-004": "AIRE-LEARN-002"},
        "split":   {},
        "strip":   ["AIRE-ACT-002", "AIRE-ACT-003"],
    },
}

TESTCARD_MARK = "## テストカード"
LEARNING_MARK = "## 学習カード"


def fm_and_body(text):
    m = re.match(r"^(---\n.*?\n---\n)(.*)$", text, re.DOTALL)
    return m.group(1), m.group(2)


def fm_get(fm, key):
    m = re.search(rf"^{re.escape(key)}:\s*(.*?)\s*$", fm, re.MULTILINE)
    return m.group(1) if m else ""


def split_body(body):
    """body を (title_headers, testcard, learning) に分ける。"""
    parts = re.split(rf"\n(?={re.escape(TESTCARD_MARK)})", body, maxsplit=1)
    if len(parts) != 2:
        return body, "", ""
    title_headers, rest = parts
    rp = re.split(rf"\n(?={re.escape(LEARNING_MARK)})", rest, maxsplit=1)
    if len(rp) == 2:
        return title_headers, rp[0], rp[1]
    return title_headers, rp[0], ""


def remap(text, mapping):
    """[[ACT]] も frontmatter 配列の素の ACT id も LEARN へ張り替える（後続数字は保護）。"""
    for act, learn in mapping.items():
        text = re.sub(re.escape(act) + r"(?!\d)", learn, text)
    return text


def drop_fm_key(fm, key):
    return re.sub(rf"^{re.escape(key)}:.*\n", "", fm, flags=re.MULTILINE)


def drop_proto_script_lines(headers):
    """LEARN のヘッダに持ち込まない行（プロトタイプ/スクリプトの相対リンクは activities/ 起点のため）。"""
    out = []
    for ln in headers.splitlines():
        if ln.startswith("プロトタイプ:") or "スクリプト草稿:" in ln or ln.startswith("スクリプト:"):
            continue
        out.append(ln)
    return "\n".join(out)


def build_learn(act_fm, headers, learning, learn_id, act_id, full_map, is_split):
    stage = fm_get(act_fm, "stage")
    fm_lines = [
        "---",
        f"id: {learn_id}",
        f"title: {fm_get(act_fm, 'title')}",
        f"type: {fm_get(act_fm, 'type')}",
        f"date: {fm_get(act_fm, 'date')}",
        f"stage: {stage}",
    ]
    if is_split:
        fm_lines.append(f"learns-from: {act_id}")
    fm_lines.append(f"hypotheses: {fm_get(act_fm, 'hypotheses')}")
    fm_lines.append(f"outcome: {fm_get(act_fm, 'outcome')}")
    fm_lines.append("---")
    fm = "\n".join(fm_lines) + "\n"

    headers = drop_proto_script_lines(headers)
    # 計画型は「実験計画: [[ACT]]」を対象仮説行の直後に挿入（回顧型は入れない）
    if is_split:
        lines = headers.splitlines()
        insert_at = next((i for i, ln in enumerate(lines) if ln.startswith("対象仮説:")), 0)
        lines.insert(insert_at + 1, f"実験計画: [[{act_id}]]")
        headers = "\n".join(lines)
    body = headers.rstrip() + "\n\n" + learning.strip() + "\n"
    # 本文は他の移行 ACT のみ LEARN へ張り替える。自身の由来 ACT（learns-from・実験計画リンク）は
    # ACT を指したまま残す（LEARN→ACT の関係を壊さない）。frontmatter は張り替えない。
    self_excluded = {k: v for k, v in full_map.items() if k != act_id}
    return fm + "\n" + remap(body, self_excluded)


def main():
    summary = []
    for slug, plan in PLAN.items():
        wiki = REPO / "projects" / slug / "wiki"
        acts = wiki / "activities"
        learns = wiki / "learnings"
        learns.mkdir(exist_ok=True)
        gk = learns / ".gitkeep"
        if gk.exists():
            gk.unlink()

        full_map = {**plan["convert"], **plan["split"]}       # 全移行 ACT→LEARN（LEARN 本文/他レコード用）
        deleted_map = dict(plan["convert"])                   # 削除される ACT のみ（残す ACT のリンク修復用）

        # CONVERT: LEARN 作成 → ACT 削除
        for act_id, learn_id in plan["convert"].items():
            p = acts / f"{act_id}.md"
            fm, body = fm_and_body(p.read_text(encoding="utf-8"))
            headers, _tc, learning = split_body(body)
            (learns / f"{learn_id}.md").write_text(
                build_learn(fm, headers, learning, learn_id, act_id, full_map, is_split=False),
                encoding="utf-8")
            p.unlink()
            summary.append(f"[convert] {act_id} → {learn_id}（ACT 削除）")

        # SPLIT: LEARN 作成 ＋ ACT をテストカードのみに縮小
        for act_id, learn_id in plan["split"].items():
            p = acts / f"{act_id}.md"
            fm, body = fm_and_body(p.read_text(encoding="utf-8"))
            headers, testcard, learning = split_body(body)
            (learns / f"{learn_id}.md").write_text(
                build_learn(fm, headers, learning, learn_id, act_id, full_map, is_split=True),
                encoding="utf-8")
            new_fm = drop_fm_key(fm, "outcome")
            new_act = new_fm + "\n" + headers.rstrip() + "\n\n" + testcard.strip() + "\n"
            p.write_text(remap(new_act, deleted_map), encoding="utf-8")   # 削除ACTへの参照のみ修復
            summary.append(f"[split] {act_id}（テストカードのみ）＋ {learn_id}（学び・learns-from）")

        # STRIP: ACT をテストカードのみに縮小（LEARN なし）
        for act_id in plan["strip"]:
            p = acts / f"{act_id}.md"
            fm, body = fm_and_body(p.read_text(encoding="utf-8"))
            headers, testcard, _learning = split_body(body)
            new_fm = drop_fm_key(fm, "outcome")
            new_act = new_fm + "\n" + headers.rstrip() + "\n\n" + testcard.strip() + "\n"
            p.write_text(remap(new_act, deleted_map), encoding="utf-8")
            summary.append(f"[strip] {act_id}（テストカードのみ・LEARN なし）")

        # 他レコード（H・DEC）と stage.md の citation を張り替え（全移行 ACT→LEARN）
        for sub in ("hypotheses", "decisions"):
            d = wiki / sub
            for rp in sorted(d.glob("*.md")):
                t = rp.read_text(encoding="utf-8")
                nt = remap(t, full_map)
                if nt != t:
                    rp.write_text(nt, encoding="utf-8")
        stage_p = wiki / "stage.md"
        if stage_p.exists():
            t = stage_p.read_text(encoding="utf-8")
            nt = remap(t, full_map)
            if nt != t:
                stage_p.write_text(nt, encoding="utf-8")

        # log.md に移行の事実を追記（欠番の取り下げ記録を含む＝id-seq 警告回避）
        log_p = wiki / "log.md"
        lines = ["", f"## [2026-07-24] self-reflection | ACT/LEARN 分割の移行（テストカード=ACT と 学習カード=LEARN を分離）"]
        for act_id, learn_id in plan["convert"].items():
            lines.append(f"## [2026-07-24] self-reflection | {act_id} → {learn_id} に移行（回顧型・学び分離）。"
                         f"{act_id} は欠番として取り下げ・再利用しない")
        for act_id, learn_id in plan["split"].items():
            lines.append(f"## [2026-07-24] self-reflection | {act_id} を学び {learn_id} に分割（"
                         f"{act_id} はテストカードとして存続。確信度の根拠 citation は {learn_id} へ張替）")
        with log_p.open("a", encoding="utf-8") as f:
            f.write("\n".join(lines) + "\n")

    print("移行完了:")
    for s in summary:
        print("  " + s)


if __name__ == "__main__":
    sys.exit(main())
