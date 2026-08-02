#!/usr/bin/env python3
"""PreToolUse フック: sources/（不変層）の既存ファイルへの Edit/Write をブロックする。

新規ファイルの Write（/learning 手順1の初回配置）は許可する。exit 2 でブロックし、
stderr のメッセージが Claude にフィードバックされる。

`sources/README.md` は例外（不変層の**説明文**であって観測データではない）。不変ルール3の意図は
「一度置いた観測データを後から書き換えない」ことなので、ディレクトリの使い方を説明する README を
凍結する理由はない。むしろ凍結すると、雛形（templates/project/sources/README.md）を直しても
既存案件の README が陳腐化したまま残り続ける（実際 `/ingest` 等の旧スキル名が残っていた）。
records.Project.source_files も README.md を生データとして数えない（同じ扱い）。
"""
import json
import re
import sys
from pathlib import Path

# 不変層の中で「観測データではない」もの＝凍結の対象外
SOURCES_EXEMPT = ("README.md",)


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
        return 0  # 新規配置は許可（/learning 手順1）
    print(f"{p.name} は sources/（不変層・読み取り専用）の既存ファイル。編集・上書きは禁止。"
          "訂正が必要なら人間に依頼し、解釈の修正は wiki/ 側のレコードで行うこと。", file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main())
