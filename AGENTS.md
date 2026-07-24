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

- 型・関係・状態機械の正本は [ontology.yaml](ontology.yaml)（人間可読は `ontology.md`）。ツールは
  `tools/ontology.py` 経由でこれを読む。`ontology.yaml` を変更したら人間可読版を再生成する:

  ```bash
  python3 tools/gen_ontology_doc.py         # ontology.yaml → ontology.md
  ```

- 機械生成ビュー（`board`・`list`・`relations`・`index`）はレコードから決定論射影する。レコード（H/ACT/LEARN/DEC）を
  変更したら再生成する（Claude Code では Stop フックが自動再生成。他エージェントは手動で）:

  ```bash
  python3 tools/gen_views.py board          # 現在プロジェクト（--project <slug> で指定可）
  python3 tools/gen_views.py list           # 全仮説リスト（バリューチェーン）
  python3 tools/gen_views.py relations      # 型付き関係グラフ・バックリンク索引
  python3 tools/gen_views.py index          # wiki/index.md（全仮説の確信度・ステータス一覧）
  ```

- 初回クローン後に `git config core.hooksPath .githooks` を一度実行し、コミット時フック（不変ルールの強制）を
  有効にする（Claude Code では SessionStart フックが自動で設定する。他エージェントは手動で）。
- 不変ルール（CLAUDE.md「不変ルール」）は全エージェント共通。特に:
  `sources/` は読み取り専用／確信度・ステータスの変更は必ず学び(LEARN)か意思決定(DEC)に紐づける／
  確信度履歴テーブルは追記専用（frontmatter は同期キャッシュ）／`log.md` は追記のみ／
  検証後の学びは新規 LEARN として積む（既存 ACT のテストカードは検証開始後に書き換えない）。

## 記述言語

すべて日本語。技術用語・ID・frontmatter キーは原文のまま。
