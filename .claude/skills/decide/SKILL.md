---
name: decide
description: ステージ移行・ピボット・撤退・巻き戻しなどの意思決定を記録する（DEC-NNN）。ユーザーが「次のステージに進みたい」「ピボットしたい」「この方針で続ける」「撤退」「巻き戻したい」「decide」「意思決定を記録」と言ったときに使う。
---

# /decide — ステージ移行・ピボット・巻き戻しの意思決定

重要な岐路の判断を、確信度スナップショットと巻き戻しポイント付きで記録する。

> **共通規約**（プロジェクト解決・ID/接頭辞・リンク記法と `../` 深さ・.gitkeep・承認規律）は [CLAUDE.md「スキル共通規約」](../../../CLAUDE.md) が正典。以下は本スキル固有の手順。

## 手順

1. **達成度をチェックする** — `wiki/stage.md` の移行基準の上書き（あれば優先）、なければ `playbooks/<stage>.md` の移行基準に照らし、現ステージの重点仮説の確信度・ステータスが基準を満たすか確認する。`wiki/index.md` の値を根拠にする。本文で playbook を引くときは wikilink ではなく**相対mdリンク**で書く（例 `[playbooks/psf.md](../../../../playbooks/psf.md)`。playbook は vault内ノートでないため wikilink は解決しない）。

2. **意思決定タイプを決める** — `stage-transition`（次ステージへ）/ `pivot`（仮説の方向転換）/ `persevere`（現方針を継続）/ `rollback`（過去の判断を巻き戻す）/ `kill`（撤退）のいずれか。

3. **確信度スナップショットを作る** — 判断時点の全重要仮説の確信度・ステータス・重要度を記録する（後から歴史を辿れるように）。

4. **選択肢を比較する** — 取りうる選択肢を並べ、根拠となる学び `[[LEARN-NNN]]`（判定を持つ学びを優先。実験計画 `[[ACT-NNN]]` も可）を挙げて選択理由を書く。

5. **DEC レコードを作る** — `wiki/decisions/` の既存最大+1で `DEC-NNN` を採番、`templates/decision.md` で作成。frontmatter の `id` は**ファイル名と同じ接頭辞つき**にする（例 `id: SELF-DEC-001`）。**frontmatter `based-on` に根拠となった学び/活動を接頭辞つきで列挙し**（must-wikilink・LEARN を優先、ACT も可）、本文にも根拠 `[[LEARN-NNN]]` と影響を受ける `[[H-NNN]]` を必ず wikilink で書く（`based-on` 空の DEC は hwlint が `dec-based-on` で警告する）。**巻き戻しポイント**（誤りのシグナルと戻り先の仮説状態・問い）と **`## 次の一手`**（前を向いて次に何を検証・実行するか＝戦略的現在地。board の「現在地」に最新DECのここが射影される）を必ず明記する。ディレクトリに `.gitkeep` が残っていれば削除してよい。

   - **ステージを動かす判断（stage-transition・rollback など）は frontmatter `to-stage` に結果ステージを必ず書く**（例 移行 `to-stage: FPF`／巻き戻し `to-stage: CPF`）。現在ステージの正本は「`to-stage` を持つ最新DEC（date 昇順の末尾）」であり、ここが空だとビュー・ツールが現ステージを正しく導出できない。persevere/kill などステージを変えない判断は書かない。
   - **pivot / rollback で新しい仮説を派生させる場合** — その新仮説の frontmatter `derived-from` に巻き戻し元・派生元の `H-NNN` を接頭辞つきで書き（cardinality one）、本文「系譜」にも `[[H-NNN]]` を併記する（`/formulate` の手順5と同じ。派生の系譜が切れると list/relations の派生グラフに辺が出ない）。

6. **stage-transition なら stage.md も更新する** — 現在ステージの正本は DEC の `to-stage` だが、フォールバック用に `wiki/stage.md` の `current-stage` と `updated` も書き換え、ステージ履歴テーブルに1行追加（意思決定列に DEC-NNN）。

7. **rollback の手順** — `rollback` のときは、戻り先の過去 DEC の「巻き戻しポイント」を読み、そこに記された仮説状態・問いへ復元する手順を提示する。復元により確信度・ステータスを戻す場合も、この DEC に紐づけて履歴テーブルに追記する。

8. **log を更新する** — `wiki/log.md` に追記する（`wiki/index.md` は生成物なので手編集しない。DEC は board の「現在地」・relations ビューのバックリンク索引・log から辿れる）:
   `## [YYYY-MM-DD] decision | DEC-NNN <要約> → <影響仮説・ステージ変化>`

## 守ること

- 意思決定は必ず根拠となる学び(LEARN)／活動(ACT)に紐づける。感覚だけで stage を進めない。
- 巻き戻しポイントは必ず書く。「この判断が誤りならどこに戻るか」を残すことが歴史性の核心。
- `persevere` も立派な意思決定。記録する価値がある（なぜ続けると決めたか）。
