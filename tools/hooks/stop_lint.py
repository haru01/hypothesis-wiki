#!/usr/bin/env python3
"""Stop フック: ターン終了時に現在プロジェクトへ hwlint を実行し、
error が残っていれば終了をブロックして修正させる（stderr が Claude に渡る）。
"""
import json
import subprocess
import sys
from pathlib import Path


def main() -> int:
    data = json.load(sys.stdin)
    if data.get("stop_hook_active"):
        return 0  # このフック起因の続行中は素通し（無限ループ防止）
    repo = Path.cwd()
    if not (repo / "projects" / "current.md").exists():
        return 0  # 仮説検証Wiki のリポジトリでなければ何もしない
    hwlint = Path(__file__).resolve().parent.parent / "hwlint.py"
    result = subprocess.run(
        [sys.executable, str(hwlint), "--repo", str(repo)],
        capture_output=True, text=True)
    if result.returncode != 0:
        print("hwlint が error を検出。ターンを終える前に修正すること:\n" + result.stdout,
              file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
