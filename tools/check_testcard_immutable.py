#!/usr/bin/env python3
"""不変ルール6の git 検出: 学習カード記入済み ACT のテストカードが base と比べて
書き換えられていないかをチェックする（pre-commit は --staged、レビュー時は --base <ref>）。

学習カードが未記入（検証開始前）の ACT はテストカードを直してよい。
判定はヒューリスティック（「### 事実（observed）」節に本文があるか）なので、
false positive 時は人間がレビューで判断する。
"""
import argparse
import re
import subprocess
import sys

TEST_SECTION_RE = re.compile(r"## テストカード.*?(?=## 学習カード|\Z)", re.DOTALL)
FACTS_RE = re.compile(r"### 事実（observed）(.*?)(?=###|\Z)", re.DOTALL)


def git(*args) -> subprocess.CompletedProcess:
    return subprocess.run(["git", *args], capture_output=True, text=True, check=False)


def testcard(text: str) -> str:
    m = TEST_SECTION_RE.search(text)
    return m.group(0) if m else ""


def learning_filled(text: str) -> bool:
    m = FACTS_RE.search(text)
    if not m:
        return False
    body = re.sub(r"<!--.*?-->", "", m.group(1), flags=re.DOTALL)
    lines = [l for l in body.splitlines()
             if l.strip() and not l.strip().startswith("観測した事実")]
    return bool(lines)


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
        if not learning_filled(base_text):
            continue  # 検証開始前はテストカードを直してよい
        if testcard(base_text) != testcard(head_text):
            failures.append(f)
    for f in failures:
        print(f"[error] testcard-immutable | {f} | "
              "学習カード記入済みACTのテストカードが変更されている（不変ルール6・後知恵バイアス防止）")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
