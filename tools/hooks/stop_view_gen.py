#!/usr/bin/env python3
"""Stop フック: 現在プロジェクトのレコードが機械ビューより新しければ再生成する。

gen_views は決定論・ゼロトークンなので、ターン終了時に `Project` を1回だけ構築して
全ビュー（board/list）をインプロセス生成する（サブプロセスを分けず全レコードの再読込を避ける）。
生成対象・出力ファイル名は gen_views.VIEWS を単一の真実源にする。非ブロック（常に exit 0）。
"""
import json
import sys
from pathlib import Path

TOOLS = Path(__file__).resolve().parent.parent


def newest_mtime(paths) -> float:
    return max((p.stat().st_mtime for p in paths if p.exists()), default=0.0)


def main() -> int:
    try:
        data = json.load(sys.stdin)
    except Exception:
        data = {}
    if data.get("stop_hook_active"):
        return 0  # このフック起因の続行中は素通し
    repo = Path.cwd()
    if not (repo / "projects" / "current.md").exists():
        return 0  # 仮説検証Wiki のリポジトリでなければ何もしない

    sys.path.insert(0, str(TOOLS))
    from gen_views import VIEWS, resolve_slug  # noqa: E402
    from records import Project  # noqa: E402

    slug = resolve_slug(repo, None)
    root = repo / "projects" / (slug or "")
    wiki = root / "wiki"
    if not slug or not wiki.is_dir():
        return 0

    records = []
    for sub in ("hypotheses", "activities", "learnings", "decisions"):
        d = wiki / sub
        if d.is_dir():
            records.extend(d.glob("*.md"))
    log = wiki / "log.md"
    if log.exists():
        records.append(log)

    # 出力先は wiki/ からの相対パス（board/list/relations は views/ 配下、index は wiki 直下）
    existing = [wiki / relpath for relpath, _ in VIEWS.values() if (wiki / relpath).exists()]
    if existing and newest_mtime(records) <= min(p.stat().st_mtime for p in existing):
        return 0  # 既存の機械ビューがレコードより新しい＝最新。再生成不要

    try:
        project = Project(root)
        for relpath, fn in VIEWS.values():
            out = fn(project)
            if out is not None:  # 生成条件を満たさないビュー（gen が None を返す）はスキップ
                (wiki / relpath).write_text(out, encoding="utf-8")
    except Exception as e:  # ビュー生成の失敗でターンを止めない
        print(f"gen_views 失敗: {e}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
