# 現在のプロジェクト

```yaml
current-project: nostradamus-uso800
```

現在アクティブなプロジェクトは **nostradamus-uso800**（ノストラダムス風の“大嘘予言”を生成するエンタメ的プロダクトの仮説検証）。

スキル（一覧は [CLAUDE.md「ワークフロー」節](../CLAUDE.md) が正典）は、まずこのファイルで
現在のプロジェクト `<slug>` を確認し、`projects/<slug>/` 配下の `sources/`・`wiki/` を対象に動く。
別のプロジェクトに切り替えるときは `current-project` を書き換える（または対話で対象を指定する）。

## プロジェクト一覧

| slug | 接頭辞 | 説明 |
|---|---|---|
| self | SELF | このツール自体（仮説検証Wiki）を題材にしたドッグフーディング |
| ai-reskilling | AIRE | AI時代のリスキリング（2名＋専門エージェント前提）の `/desk-research` テスト検証 |
| nostradamus-uso800 | NOST | ノストラダムス風の“大嘘予言”を生成するエンタメ的プロダクトの仮説検証 |
