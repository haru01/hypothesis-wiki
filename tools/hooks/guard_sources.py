#!/usr/bin/env python3
"""PreToolUse フック: sources/（不変層）の既存ファイルへの Edit/Write をブロックする。

新規ファイルの Write（/ingest 手順1の初回配置）は許可する。exit 2 でブロックし、
stderr のメッセージが Claude にフィードバックされる。
"""
import json
import re
import sys
from pathlib import Path


def main() -> int:
    data = json.load(sys.stdin)
    tool = data.get("tool_name", "")
    file_path = (data.get("tool_input") or {}).get("file_path", "")
    if not file_path:
        return 0
    p = Path(file_path)
    if not re.search(r"projects/[^/]+/sources/", p.as_posix()):
        return 0
    if tool == "Write" and not p.exists():
        return 0  # 新規配置は許可（/ingest 手順1）
    print(f"{p.name} は sources/（不変層・読み取り専用）の既存ファイル。編集・上書きは禁止。"
          "訂正が必要なら人間に依頼し、解釈の修正は wiki/ 側のレコードで行うこと。", file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main())
