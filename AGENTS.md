# AGENTS.md — 仮説検証Wiki（エージェント共通の入口）

このリポジトリの規約の正典は [CLAUDE.md](CLAUDE.md)。**どのエージェントも、まず CLAUDE.md を読み、
「規律あるWikiの保守者」として振る舞うこと。** 不変ルールも全エージェント共通（CLAUDE.md「不変ルール」）。
本ファイルには Claude Code 以外のエージェント向けの差分だけを書く（内容を二重管理しない）。

## Claude Code 以外での使い方

- `.claude/skills/` のスキル（`/formulating` `/planning` `/learning` …）は Claude Code 用の入口にすぎない。
  各スキルの実体はただの Markdown 手順書なので、**スキル機構がないエージェントは
  `.claude/skills/<name>/SKILL.md` を読み、その手順に従って作業する**（対応表は CLAUDE.md「ワークフロー」）。
- フィールドの書き方を知るのに散文は要らない。**frontmatter の各フィールドは宣言側に `description`・
  `guidance`・`example`・既定値を持つ**ので、[ontology.md](ontology.md)「frontmatter フィールド」か
  `schema/*.schema.json` を読む。
- `schema/*.schema.json` は **JSON Schema 2020-12 の可搬な契約**で、スキル機構も `hwlint` も持たない
  エージェント・エディタが frontmatter をそのまま検証できる。ただし**検証の正本は `tools/hwlint.py`**で、
  JSON Schema が表せるのは1レコード内の形だけ（確信度履歴テーブルとの一致・関係の実在・凍結・根拠鎖は
  レコードをまたぐので lint にしかない）。
- Claude Code ではフックが自動実行する処理を、他エージェントは手動で実行する:

  ```bash
  git config core.hooksPath .githooks       # 初回クローン後に一度。コミット時フック（不変ルールの強制）
  python3 tools/hwlint.py                   # 変更後は必ず実行し error を残さない
  python3 tools/gen_views.py board          # レコード変更後に再生成（--project <slug> で指定可）
  python3 tools/gen_views.py list           # 全仮説リスト（バリューチェーン）
  python3 tools/gen_views.py relations      # 型付き関係グラフ・バックリンク索引
  python3 tools/gen_views.py index          # wiki/index.md（全仮説の確信度・ステータス一覧）
  python3 tools/gen_ontology_doc.py         # ontology.yaml 変更後: → ontology.md（人間可読）
  python3 tools/gen_schema.py               # ontology.yaml 変更後: → schema/*.schema.json（機械可読）
  python3 tools/gen_schema.py --check-templates   # 雛形と宣言のドリフト検査
  ```

## 記述言語

すべて日本語。技術用語・ID・frontmatter キーは原文のまま。
