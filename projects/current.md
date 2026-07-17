# 現在のプロジェクト

```yaml
current-project: self
```

現在アクティブなプロジェクトは **self**（このツール自体のドッグフーディング）。

スキル（`/refine` `/plan` `/ingest` `/view` `/decide` `/lint`）は、まずこのファイルで
現在のプロジェクト `<slug>` を確認し、`projects/<slug>/` 配下の `sources/`・`wiki/` を対象に動く。
別のプロジェクトに切り替えるときは `current-project` を書き換える（または対話で対象を指定する）。

## プロジェクト一覧

| slug | 接頭辞 | 説明 |
|---|---|---|
| self | SELF | このツール自体（仮説検証Wiki）を題材にしたドッグフーディング |
