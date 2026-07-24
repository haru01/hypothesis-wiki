#!/usr/bin/env python3
"""不変ルール6の git 検出: 学び(LEARN)が紐づいた実験計画(ACT)のテストカードが
base と比べて書き換えられていないかをチェックする（pre-commit は --staged、レビュー時は --base <ref>）。

新モデルでは学習カードは ACT ではなく別レコード LEARN に積むため、テストカードの不変性は
ほぼ構造的に保証される（ACT は作成後ふつう触らない）。本チェックはその安全網:
ある ACT を `learns-from` で指す LEARN が存在する＝その実験は実施され学びが記録された、
とみなし、以後その ACT のテストカードの変更を後知恵バイアスとして弾く。
LEARN がまだ無い（検証開始前）ACT はテストカードを直してよい。
"""
import argparse
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import subprocess  # noqa: E402
from records import testcard  # noqa: E402  テストカード節の抽出は records に一元化（gen_views と共有）

LEARNS_FROM_RE = re.compile(r"^\s*learns-from:\s*(.+?)\s*$", re.MULTILINE)


def git(*args) -> subprocess.CompletedProcess:
    return subprocess.run(["git", *args], capture_output=True, text=True, check=False)


def act_has_learning(act_path: str) -> bool:
    """この ACT を learns-from で指す LEARN がワークツリーに存在するか。

    act_path は `projects/<slug>/wiki/activities/<ACT>.md`。同プロジェクトの
    `wiki/learnings/*.md` を走査し、frontmatter learns-from が当該 ACT id を含むかを見る。"""
    p = Path(act_path)
    act_id = p.stem
    learnings_dir = p.parent.parent / "learnings"
    if not learnings_dir.is_dir():
        return False
    for lp in learnings_dir.glob("*.md"):
        try:
            text = lp.read_text(encoding="utf-8")
        except OSError:
            continue
        for m in LEARNS_FROM_RE.finditer(text):
            # 配列 [X, Y] でも素の X でも当該 id を含めば真
            if act_id in re.findall(r"[A-Z0-9]+-ACT-\d+", m.group(1)):
                return True
    return False


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
               if "/wiki/activities/" in f and f.endswith(".md")]
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
        if not act_has_learning(f):
            continue  # 学びがまだ紐づかない（検証開始前）ACT はテストカードを直してよい
        if testcard(base_text) != testcard(head_text):
            failures.append(f)
    for f in failures:
        print(f"[error] testcard-immutable | {f} | "
              "学び(LEARN)が紐づいた実験計画(ACT)のテストカードが変更されている"
              "（不変ルール6・後知恵バイアス防止）")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
