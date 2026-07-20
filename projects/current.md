# 現在のプロジェクト

```yaml
current-project: agent-platform
```

現在アクティブなプロジェクトは **agent-platform**（意思決定の航跡＝Decision Record／ADRの経営・事業版を題材にしたスキル動作確認用ステージング案件）。

スキル（`/new-project` `/desk-research` `/formulate` `/plan` `/prototype` `/ingest` `/view` `/decide` `/lint`）は、まずこのファイルで
現在のプロジェクト `<slug>` を確認し、`projects/<slug>/` 配下の `sources/`・`wiki/` を対象に動く。
別のプロジェクトに切り替えるときは `current-project` を書き換える（または対話で対象を指定する）。

## プロジェクト一覧

| slug | 接頭辞 | 説明 |
|---|---|---|
| self | SELF | このツール自体（仮説検証Wiki）を題材にしたドッグフーディング |
| ai-reskilling | AIRE | AI時代のリスキリング（2名＋専門エージェント前提）の `/desk-research` テスト検証 |
| agent-platform | AGP | 意思決定の航跡（Decision Record）— AIと決めると決定・選択肢・却下理由・根拠が副産物で残る（ADRの経営・事業版）。スキル動作確認用ステージング |
