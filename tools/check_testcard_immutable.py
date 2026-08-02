#!/usr/bin/env python3
"""不変ルール6の git 検出: 実施済み実験計画(TEST)の**凍結範囲**が base と比べて
書き換えられていないかをチェックする（pre-commit は --staged、レビュー時は --base <ref>）。

ある TEST を `learns-from` で指す LEARN が存在する＝その実験は実施され学びが記録された、とみなす。
LEARN がまだ無い（検証開始前）TEST は自由に直してよい — 実施前に計画を練り直す機会はよくある。

**凍結するのはテストカード全体ではない。** 後知恵バイアス防止に必要なのは「事後に成功基準と
riskiest-assumption を改竄させない」ことだけなので、目的・方法・指標の補正、スクリプトや
プロトタイプへのリンク追加、誤字修正は実施後も許す。凍結範囲の正本は ontology.yaml の
`entities.TEST.immutable`（コードにも規約文にも再定義しない）。

雛形逸脱で凍結節が本文から取れないときは、従来どおりテストカード節全体を比較する
（フェイルクローズ。保護が静かに外れるより、広く弾いて雛形へ誘導するほうがよい）。
"""
import argparse
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import subprocess  # noqa: E402
# 抽出/パースは records に一元化（gen_views と共有）、凍結範囲の宣言は ontology.yaml が正本。
from records import testcard, frozen_parts, parse_frontmatter  # noqa: E402
from ontology import IMMUTABLE, ENTITY_DIRS  # noqa: E402


def git(*args) -> subprocess.CompletedProcess:
    return subprocess.run(["git", *args], capture_output=True, text=True, check=False)


def test_has_learning(test_path: str) -> bool:
    """この TEST を learns-from で指す LEARN がワークツリーに存在するか（＝実施済みか）。

    test_path は `projects/<slug>/wiki/tests/<TEST>.md`。同プロジェクトの
    `wiki/learnings/*.md` を走査し、frontmatter learns-from が当該 TEST id を含むかを見る。
    関係名・ディレクトリ名は ontology.yaml から引く（ここに書かない）。"""
    p = Path(test_path)
    test_id = p.stem
    learnings_dir = p.parent.parent / ENTITY_DIRS["LEARN"]
    if not learnings_dir.is_dir():
        return False
    trigger = IMMUTABLE["TEST"].trigger_relation
    for lp in learnings_dir.glob("*.md"):
        try:
            text = lp.read_text(encoding="utf-8")
        except OSError:
            continue
        # frontmatter の learns-from のみを見る（本文・コメントの言及で誤検出しない）。配列/素どちらも可。
        lf = parse_frontmatter(text).get(trigger, "")
        if test_id in re.findall(r"[A-Z0-9]+-TEST-\d+", lf):
            return True
    return False


def violations(base_text: str, head_text: str) -> list:
    """凍結範囲のうち base と head で食い違う項目名のリスト（空なら違反なし）。

    凍結節が両側とも取れない雛形逸脱では、テストカード節全体を比較する（フェイルクローズ）。"""
    base_parts, head_parts = frozen_parts(base_text), frozen_parts(head_text)
    if base_parts is None and head_parts is None:
        if testcard(base_text) != testcard(head_text):
            return ["テストカード全体（凍結節が見つからないため全体比較にフォールバック）"]
        return []
    if base_parts is None or head_parts is None:
        # 片側だけ取れない＝凍結節の追加・削除・見出し改名。改名してから中身を書き換える迂回を塞ぐ。
        return ["・".join(IMMUTABLE["TEST"].sections) + "（節の追加・削除・見出しの改名）"]
    return [k for k, v in base_parts.items() if head_parts.get(k) != v]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", default="HEAD", help="比較先の git ref（既定 HEAD）")
    ap.add_argument("--staged", action="store_true",
                    help="pre-commit モード: base とステージ済み内容（index）を比較する")
    args = ap.parse_args()
    if args.staged:
        diff = git("diff", "--cached", "--name-only", args.base)
    else:
        diff = git("diff", "--name-only", f"{args.base}...HEAD")
    changed = [f for f in diff.stdout.splitlines()
               if "/wiki/tests/" in f and f.endswith(".md")]
    failures = []
    for f in changed:
        base_show = git("show", f"{args.base}:{f}")
        if base_show.returncode != 0:
            continue  # 新規ファイルは対象外
        if args.staged:
            head_show = git("show", f":{f}")
            if head_show.returncode != 0:
                continue  # 削除は対象外
            head_text = head_show.stdout
        else:
            try:
                head_text = open(f, encoding="utf-8").read()
            except FileNotFoundError:
                continue  # 削除されたファイルは対象外
        base_text = base_show.stdout
        if not test_has_learning(f):
            continue  # 学びがまだ紐づかない（検証開始前）TEST は自由に直してよい
        changed_parts = violations(base_text, head_text)
        if changed_parts:
            failures.append((f, changed_parts))
    for f, changed_parts in failures:
        print(f"[error] testcard-immutable | {f} | "
              f"実施済み（学び LEARN が紐づいた）実験計画(TEST)の凍結範囲が変更されている: "
              f"{'、'.join(changed_parts)}"
              "（不変ルール6・後知恵バイアス防止）。目的・方法・指標の補正やリンク追加は許可されている。"
              "実際の手順が計画と違ったなら、TEST を書き換えず LEARN の事実(observed)に差分として書く。")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
