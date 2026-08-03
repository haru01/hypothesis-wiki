# projects/ — 仮説検証プロジェクト（案件単位）

仮説検証は**案件（プロジェクト）単位**で分ける。各プロジェクトは自分の生データ（`sources/`）と
Wiki（`wiki/`）を1フォルダに持つ。スキーマ層（`ontology.yaml`・`CLAUDE.md`・`AGENTS.md`・
`playbooks/`・`templates/`・`.claude/skills/`）はリポジトリ全体で共有する。

現在アクティブなプロジェクトは各自ローカルの `.env` の `CURRENT_PROJECT=<slug>`（未設定なら `self`）が指す
（`.env` は gitignore・書式はリポ直下の `.env.example`）。プロジェクト一覧ファイルは持たない——slug はこの
ディレクトリ名、接頭辞（PREFIX）は各プロジェクトの既存レコードID（無ければ `slug` の大文字）から導出する。

```
projects/
├── <slug>/
│   ├── sources/          # このプロジェクトの生データ（不変層・AIは読むだけ）
│   └── wiki/
│       ├── hypotheses/<PREFIX>-H-NNN.md          # 仮説を立てた
│       ├── tests/<PREFIX>-TEST-NNN.md（＋ <PREFIX>-TEST-NNN-script.md）  # 実験計画を立てた（テストカード）
│       ├── learnings/<PREFIX>-LEARN-NNN.md       # 実施して学びを得た（学習カード）
│       ├── decisions/<PREFIX>-DEC-NNN.md         # 意思決定した
│       ├── prototypes/<PREFIX>-TEST-NNN/index.html  # /building の生成物
│       ├── lean-canvas/<PREFIX>-lean-canvas-<YYYY-MM-DD>.svg  # /lean-canvas の生成物（最新1枚を index が埋め込む）
│       ├── views/        # 生成物（board/list/relations）
│       ├── index.md（生成物） ├── log.md └── stage.md
└── ...
```

## ID は接頭辞つき（Obsidian のリンク一意性のため）

- ファイル名＝ID で、**プロジェクト接頭辞つき**（例 `SELF-H-001.md`、`SELF-TEST-001.md`）。
- Obsidian のwikilinkはファイル名がvault全体で一意でないと解決しないため、接頭辞で衝突を防ぐ。
- 採番は**種別×プロジェクトごと**の既存最大+1（プロジェクトごとに `-H-001` から始まる）。ID再利用禁止。

## 新しいプロジェクトの作り方

**推奨: `/new-project` スキル**を使う。`templates/project/` の雛形から `projects/<slug>/`
（`sources/` と空の `wiki/` 一式）を作り、`.env` の `CURRENT_PROJECT` を切り替えるところまで行う。

手動で作る場合:

1. `templates/project/` を `projects/<slug>/` にコピーする（`cp -r templates/project/. projects/<slug>/`）。`sources/`（README付き）と `wiki/{hypotheses,tests,learnings,decisions,views}`＋`index.md`（生成物の雛形）・`log.md`・`stage.md` が揃う。
2. `wiki/stage.md` の `updated:` とステージ履歴の `YYYY-MM-DD` を今日の日付にする。
3. 接頭辞（大文字・他プロジェクトのレコードID接頭辞と重複しない。既定は `slug` の大文字）を決める。切り替えは `.env` に `CURRENT_PROJECT=<slug>` を書く（無ければ `cp .env.example .env` して作成）。

## 現在のプロジェクト

- 切り替えは `.env` の `CURRENT_PROJECT`（未設定なら `self`）。
- **self**（接頭辞 `SELF`）: このツール自体のドッグフーディング実例。デスクリサーチ →
  反証可能な仮説5件 → 最初の検証計画（CPF）まで。詳細は `projects/self/wiki/`。
- **ai-reskilling**（接頭辞 `AIRE`）: AI時代のリスキリングを題材にした `/desk-research` のテスト検証。
