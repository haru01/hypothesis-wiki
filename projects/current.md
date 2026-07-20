# 現在のプロジェクト

```yaml
current-project: agent-platform
```

現在アクティブなプロジェクトは **agent-platform**（仮説検証の一般化＝不確実性下で試行錯誤からゴール・制約・使命が事後創発する過程をAIが伴走支援する、を題材にしたスキル動作確認用ステージング案件）。

スキル（`/new-project` `/desk-research` `/formulate` `/plan` `/prototype` `/ingest` `/view` `/decide` `/lint`）は、まずこのファイルで
現在のプロジェクト `<slug>` を確認し、`projects/<slug>/` 配下の `sources/`・`wiki/` を対象に動く。
別のプロジェクトに切り替えるときは `current-project` を書き換える（または対話で対象を指定する）。

## プロジェクト一覧

| slug | 接頭辞 | 説明 |
|---|---|---|
| self | SELF | このツール自体（仮説検証Wiki）を題材にしたドッグフーディング |
| ai-reskilling | AIRE | AI時代のリスキリング（2名＋専門エージェント前提）の `/desk-research` テスト検証 |
| agent-platform | AGP | 仮説検証の一般化 — 不確実性下で、試行錯誤からゴール・制約・使命が事後創発する過程をAIが伴走合成する（エフェクチュエーション／創発的戦略のコパイロット）。スキル動作確認用ステージング |
