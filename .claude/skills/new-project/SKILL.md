---
name: new-project
description: 新しい仮説検証プロジェクト（案件）を projects/<slug>/ に雛形から作成し、現在のプロジェクトに設定する。ユーザーが「新しいプロジェクトを作りたい」「別案件を始めたい」「new-project」「プロジェクトを追加」と言ったときに使う。
---

# /new-project — 新しいプロジェクト（案件）の作成

`templates/project/` の雛形から `projects/<slug>/` を作り、現在のプロジェクトに設定する。

## 手順

1. **slug と接頭辞を決める** — ユーザーに確認する（`AskUserQuestion` 可）:
   - `<slug>`: ディレクトリ名（小文字・ハイフン。例 `acme-app`）。既存の `projects/` と重複しないこと。
   - `<PREFIX>`: ID接頭辞（大文字。例 `ACME`）。他プロジェクトと重複しないこと（Obsidianのリンク一意性のため）。`projects/current.md` の一覧と照合する。

2. **雛形をコピーする** — `templates/project/` の中身を `projects/<slug>/` に複製する:
   `cp -r templates/project/. projects/<slug>/`
   これで `sources/`（README付き）と `wiki/`（`hypotheses/` `activities/` `decisions/`＝空・`.gitkeep`、`views/`＝README、`index.md`・`log.md`・`stage.md`）が揃う。

3. **雛形のプレースホルダを埋める** — `projects/<slug>/wiki/stage.md` の `updated:` とステージ履歴の `YYYY-MM-DD` を今日の日付にする。必要なら `index.md` の見出し等はそのままでよい（空表）。

4. **現在のプロジェクトに登録する** — `projects/current.md` を更新:
   - `current-project: <slug>` に切り替える。
   - 「プロジェクト一覧」テーブルに `| <slug> | <PREFIX> | <説明> |` を1行追加する。

5. **確認して終了** — 作成したパスと、以後 `/grill` などが `projects/<slug>/` を対象に動くことを伝える。最初の仮説起票は `/grill` へ誘導する。

## 守ること

- 接頭辞は**全プロジェクトで一意**にする（ファイル名がvault全体で衝突しないため）。既存 `projects/*/wiki/hypotheses/` の接頭辞を確認する。
- 雛形（`templates/project/`）自体は編集しない（スキーマ層）。コピー先だけを編集する。
- 既存プロジェクトを上書きしない。`projects/<slug>/` が既にあれば中止してユーザーに確認する。
- このスキルはレコード（H/ACT/DEC）を作らない。器を用意するだけ。中身は `/grill` 以降で作る。
- 雛形の空ディレクトリ（`hypotheses/` `activities/` `decisions/`）の `.gitkeep` は、最初のレコードを作成した後は削除してよい（任意。`/grill` `/plan` `/ingest` `/decide` の作成手順が削除する）。
