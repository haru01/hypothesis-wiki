#!/usr/bin/env python3
"""PreToolUse フック: sources/（不変層）の**コミット済み**ファイルへの Edit/Write をブロックする。

不変性の要は「観測した生データを**後から**書き換えない」ことなので、境界は「コミット済みかどうか」に置く。
まだコミットしていない下書き（今このターンで置いたばかりの生データ）は誤字修正も追記もしてよい。
`.githooks/pre-commit` の sources ゲートは `git diff --cached --diff-filter=M`（＝HEAD に在るファイルの
改変だけを弾く）なので、`git ls-tree HEAD` による判定はそれと**厳密に同じ境界**になる。
かつてここが `p.exists()` を境界にしていたため、フックのほうが pre-commit より厳しく、
自分が直前に書いた未コミットの生データすら直せない非対称があった。

判定できないとき（リポジトリ外・git 不在・タイムアウト）は凍結側に倒す
（フェイルクローズ。保護が静かに外れるより広く弾くほうがよい）。

新規ファイルの Write（/learning 手順1の初回配置）は許可する。exit 2 でブロックし、
stderr のメッセージが Claude にフィードバックされる。

`sources/README.md` は例外（不変層の**説明文**であって観測データではない）。ディレクトリの使い方を
説明する README を凍結すると、雛形（templates/project/sources/README.md）を直しても既存案件の README が
陳腐化したまま残り続ける（実際 `/ingest` 等の旧スキル名が残っていた）。
records.Project.source_files も README.md を生データとして数えない（同じ扱い）。
"""
import json
import re
import subprocess
import sys
from pathlib import Path

# 不変層の中で「観測データではない」もの＝凍結の対象外
SOURCES_EXEMPT = ("README.md",)
GIT_TIMEOUT = 5


def is_committed(p: Path):
    """p が HEAD に存在する（＝コミット済み）か。判定できなければ None を返す。

    `git ls-files`（追跡済みか）ではなく `ls-tree HEAD` を使うのは、pre-commit の
    `--diff-filter=M` と境界をそろえるため（`git add` しただけではまだ凍らせない）。
    フックの cwd はリポジトリ内とは限らないので、対象ファイルの位置で `-C` を効かせる。"""
    def git(*args):
        try:
            return subprocess.run(["git", "-C", str(p.parent), *args],
                                  capture_output=True, text=True, timeout=GIT_TIMEOUT)
        except (OSError, subprocess.SubprocessError):
            return None

    r = git("ls-tree", "--name-only", "HEAD", "--", str(p))
    if r is not None and r.returncode == 0:
        return bool(r.stdout.strip())
    # ls-tree が失敗する理由は2つあり、片方は「未コミット」と断定できる:
    # HEAD が無い（コミットが1つも無いリポジトリ）なら、そのファイルは当然まだコミットされていない。
    # リポジトリ外・git 不在は判定不能なので None（呼び手が凍結側に倒す）。
    inside = git("rev-parse", "--is-inside-work-tree")
    if inside is not None and inside.returncode == 0 and inside.stdout.strip() == "true":
        return False
    return None


def main() -> int:
    data = json.load(sys.stdin)
    tool = data.get("tool_name", "")
    file_path = (data.get("tool_input") or {}).get("file_path", "")
    if not file_path:
        return 0
    p = Path(file_path)
    if not re.search(r"projects/[^/]+/sources/", p.as_posix()):
        return 0
    if p.name in SOURCES_EXEMPT:
        return 0  # 不変層の説明文（観測データでない）
    if tool == "Write" and not p.exists():
        return 0  # 新規配置は許可（/learning 手順1）。親ディレクトリごと新規のケースもここで抜ける

    committed = is_committed(p)
    if committed is False:
        return 0  # 未コミットの下書き。まだ「観測データを後から書き換える」には当たらない
    if committed is None:
        print(f"{p.name} は sources/（不変層）のファイルだが、git でコミット状態を判定できなかったため"
              "凍結側に倒した。編集は控え、必要なら人間に依頼すること。", file=sys.stderr)
        return 2
    print(f"{p.name} は sources/（不変層）の**コミット済み**の生データ。一度記録した観測は後から"
          "書き換えない。訂正が必要なら人間に依頼し、解釈の修正は wiki/ 側のレコードで行うこと"
          "（まだコミットしていない下書きなら編集できる。`git status` で確認）。", file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main())
