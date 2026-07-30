#!/usr/bin/env python3
"""Stop フック: レコードが機械ビューより新しいプロジェクトのビューを再生成する。

gen_views は決定論・ゼロトークンなので、ターン終了時に `Project` を1回だけ構築して
全ビュー（board/list/relations/index）をインプロセス生成する（サブプロセスを分けず全レコードの再読込を避ける）。
生成対象・出力ファイル名は gen_views.VIEWS を単一の真実源にする。非ブロック（常に exit 0）。

対象は**全プロジェクト**。現在プロジェクトだけを見ていると、案件を切り替えた後に非アクティブ案件の
ビューが静かに古びる（生成基準日が食い違う）ため。mtime 比較で変化の無い案件はスキップするので
案件が増えてもコストはほぼ変わらない。
"""
import json
import sys
from pathlib import Path

TOOLS = Path(__file__).resolve().parent.parent


def newest_mtime(paths) -> float:
    return max((p.stat().st_mtime for p in paths if p.exists()), default=0.0)


def regen(root: Path, views, project_cls, record_dirs) -> None:
    """1プロジェクト分。レコードがビューより新しいときだけ再生成する。"""
    wiki = root / "wiki"
    if not wiki.is_dir():
        return
    records = []
    for sub in record_dirs:
        d = wiki / sub
        if d.is_dir():
            records.extend(d.glob("*.md"))
    log = wiki / "log.md"
    if log.exists():
        records.append(log)

    # 出力先は wiki/ からの相対パス（board/list/relations は views/ 配下、index は wiki 直下）
    existing = [wiki / relpath for relpath, _ in views.values() if (wiki / relpath).exists()]
    if existing and newest_mtime(records) <= min(p.stat().st_mtime for p in existing):
        return  # 既存の機械ビューがレコードより新しい＝最新。再生成不要

    project = project_cls(root)
    for relpath, fn in views.values():
        out = fn(project)
        if out is not None:  # 生成条件を満たさないビュー（gen が None を返す）はスキップ
            (wiki / relpath).write_text(out, encoding="utf-8")


def main() -> int:
    try:
        data = json.load(sys.stdin)
    except Exception:
        data = {}
    if data.get("stop_hook_active"):
        return 0  # このフック起因の続行中は素通し
    repo = Path.cwd()
    if not (repo / "ontology.yaml").exists():
        return 0  # 仮説検証Wiki のリポジトリでなければ何もしない

    sys.path.insert(0, str(TOOLS))
    from gen_views import VIEWS  # noqa: E402
    from records import Project  # noqa: E402
    from ontology import RECORD_DIRS  # noqa: E402  レコード置き場の正本は ontology.yaml

    projects_dir = repo / "projects"
    if not projects_dir.is_dir():
        return 0
    for root in sorted(projects_dir.iterdir()):
        try:
            regen(root, VIEWS, Project, RECORD_DIRS)
        except Exception as e:  # ビュー生成の失敗でターンを止めない
            print(f"gen_views 失敗（{root.name}）: {e}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
