#!/usr/bin/env python3
"""一度きりの移行: レコード種別 ACT を TEST に改名し、ディレクトリ activities を tests に移す。
（docs/migrations/2026-07-act-to-test-rename.md 参照）

日本語ラベルは「活動」→「実験計画」に統一済み（本文名は テストカード のまま）。ID接頭辞と
ディレクトリ名だけが構造的に変わる。

置換は単一の正規表現 `(?<![A-Za-z])ACT(?![A-Za-z])` → `TEST` で行う。前後がラテン文字でない
`ACT` だけを捕捉するので
  - `SELF-ACT-002`（ID・ハイフン境界）
  - 裸の `ACT-003` / `[ACT-NNN]`
  - 散文の `ACT`（「テストカード=ACT」「はACT」「のACT」「ACT表」「desk-research ACT」等）
を一度に捕捉し、英単語（IMP**ACT**・CONT**ACT**・F**ACT**・**ACT**ION・RE**ACT**）や小文字 `act`
は対象外になる（日本語文字は隣接しても捕捉できる＝`\\b` では取りこぼす和文隣接を拾う）。
加えてパス表記 `wiki/activities/` → `wiki/tests/`。

最大クリーン方針: 各 projects/<slug>/ 配下の全 *.md / *.html（wiki・sources 観測データ・
skill-improvements を含む）を対象にする。純粋な機械リネームで確信度・ステータス・出来事の
意味は変えない（識別子の付け替えのみ）。この一度きりの移行に限り、不変ルール2（log 追記専用）・
3（sources 改変禁止）を機械リネームの範囲で全テキストに例外適用する。

除外（歴史として凍結）: docs/migrations/** ・ docs/superpowers/** ・ tools/migrate_act_learn.py
（本スクリプトは projects/ と templates/ のみ対象なので自然に除外される）。
冪等ではない（1回だけ実行）。実行後は hwlint とビュー再生成で検証すること。
"""
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
PROJECTS = ["self", "ai-reskilling"]
MIGRATION_DATE = "2026-07-25"
ACT_RE = re.compile(r"(?<![A-Za-z])ACT(?![A-Za-z])")


def rewrite(p: Path) -> bool:
    """ファイル内の ACT トークンとパス表記を新表記へ置換する。変更があれば True。"""
    text = p.read_text(encoding="utf-8")
    new = ACT_RE.sub("TEST", text).replace("wiki/activities/", "wiki/tests/")
    if new != text:
        p.write_text(new, encoding="utf-8")
        return True
    return False


def main() -> int:
    summary = []
    for slug in PROJECTS:
        proj = REPO / "projects" / slug

        # 1. テキスト置換（projects/<slug>/ 配下の全 md/html。wiki・sources・skill-improvements 含む）
        for p in sorted(list(proj.rglob("*.md")) + list(proj.rglob("*.html"))):
            if rewrite(p):
                summary.append(f"[text] {p.relative_to(REPO)}")

        # 2. プロトタイプ dir のリネーム（<PREFIX>-ACT-NNN/ → <PREFIX>-TEST-NNN/）
        proto = proj / "wiki" / "prototypes"
        if proto.is_dir():
            for d in sorted(proto.iterdir()):
                if d.is_dir() and "-ACT-" in d.name:
                    nd = d.with_name(d.name.replace("-ACT-", "-TEST-"))
                    d.rename(nd)
                    summary.append(f"[dir] {d.relative_to(REPO)} → {nd.name}")

        # 3. activities 内のレコード/スクリプトを改名し、dir を tests へ
        acts = proj / "wiki" / "activities"
        if acts.is_dir():
            for f in sorted(acts.iterdir()):
                if f.is_file() and "-ACT-" in f.name:
                    nf = f.with_name(f.name.replace("-ACT-", "-TEST-"))
                    f.rename(nf)
                    summary.append(f"[file] {f.relative_to(REPO)} → {nf.name}")
            tests_dir = proj / "wiki" / "tests"
            if tests_dir.exists():
                sys.exit(f"移行中止: {tests_dir} が既に存在する")
            acts.rename(tests_dir)
            summary.append(f"[dir] {acts.relative_to(REPO)} → tests")

        # 4. 置換パスの後に log.md へ移行記録を追記（ノート内の "ACT" を保持するため順序が重要）
        log_p = proj / "wiki" / "log.md"
        if log_p.exists():
            with log_p.open("a", encoding="utf-8") as f:
                f.write(
                    f"\n## [{MIGRATION_DATE}] self-reflection | レコード種別 ACT を TEST に改名"
                    "（ディレクトリ activities→tests・日本語ラベル『実験計画』に統一）。"
                    "純粋な機械リネームで確信度・ステータス・出来事の意味は不変\n")
            summary.append(f"[log] {log_p.relative_to(REPO)} に移行記録を追記")

    # 5. テンプレートの空 dir も activities → tests へ
    tmpl = REPO / "templates" / "project" / "wiki" / "activities"
    if tmpl.is_dir():
        tmpl_new = tmpl.with_name("tests")
        if tmpl_new.exists():
            sys.exit(f"移行中止: {tmpl_new} が既に存在する")
        tmpl.rename(tmpl_new)
        summary.append(f"[dir] {tmpl.relative_to(REPO)} → tests")

    print("移行完了:")
    for s in summary:
        print("  " + s)
    return 0


if __name__ == "__main__":
    sys.exit(main())
