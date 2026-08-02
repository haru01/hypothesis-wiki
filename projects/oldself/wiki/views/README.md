# views/ — 生成物（手編集禁止）

このディレクトリのファイルは Stop フック（`tools/hooks/stop_view_gen.py` → `tools/gen_views.py`）が
レコード変更時に**自動生成する再生成可能な生成物**である。

- **手で編集しない。** 記録の修正は仮説・活動・意思決定の各レコード側で行い、ビューは再生成する。
- `hypotheses-list.md` — 全仮説テーブル（関連リンク列・直近の根拠列＋バリューチェーン図）
- `board.md` — ジャベリンボード風・実験の変遷
- `relations.md` — 型付き関係グラフ・バックリンク索引・課題↔ソリューションフィット
- 手動で作り直したいときは `python3 tools/gen_views.py <view>`（`list`／`board`／`relations`。`--project <slug>` で対象指定可）。

md ビュー（`board.md`・`hypotheses-list.md`・`relations.md`）はフックがデフォルトで自動生成する正の生成物。
`index.html`（HTMLダッシュボード）を置く場合のみ**任意・手動保守のスナップショット**として扱う——`index.html` は
フックの自動生成対象外なので、レコード更新時に手動で更新し、乖離しうる点に注意する。

Obsidianのグラフビューを使うときは、このフォルダをフィルタで除外すると仮説ネットワークが見やすい。
