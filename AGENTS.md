# AGENTS.md — 仮説検証Wiki（エージェント共通の入口）

このリポジトリの規約の正典は [CLAUDE.md](CLAUDE.md)。**どのエージェントも、まず CLAUDE.md を読み、
「規律あるWikiの保守者」として振る舞うこと。** 本ファイルには Claude Code 以外のエージェント向けの差分だけを書く
（内容を二重管理しない）。

## Claude Code 以外での使い方

- `.claude/skills/` のスキル（`/formulate` `/plan` `/ingest` …）は Claude Code 用の入口にすぎない。
  各スキルの実体はただの Markdown 手順書なので、**スキル機構がないエージェントは
  `.claude/skills/<name>/SKILL.md` を読み、その手順に従って作業する**（対応表は CLAUDE.md「ワークフロー」）。
- 変更後は必ず決定論 lint を実行し、error を残さない:

  ```bash
  python3 tools/hwlint.py
  ```

- 機械生成ビュー（現状 `board`）はレコードから決定論射影する。レコード（ACT/DEC/H）を変更したら再生成する
  （Claude Code では Stop フックが自動再生成。他エージェントは手動で）:

  ```bash
  python3 tools/gen_views.py board          # 現在プロジェクト（--project <slug> で指定可）
  ```

- 初回クローン後に `git config core.hooksPath .githooks` を一度実行し、コミット時フック（不変ルールの強制）を
  有効にする（Claude Code では SessionStart フックが自動で設定する。他エージェントは手動で）。
- 不変ルール（CLAUDE.md「不変ルール」）は全エージェント共通。特に:
  `sources/` は読み取り専用／確信度・ステータスの変更は必ず ACT/DEC に紐づける／`log.md` は追記のみ／
  テストカードの成功基準は検証開始後に書き換えない。

## 記述言語

すべて日本語。技術用語・ID・frontmatter キーは原文のまま。
