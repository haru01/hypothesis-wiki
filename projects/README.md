# projects/ — 仮説検証プロジェクト（案件単位）

仮説検証は**案件（プロジェクト）単位**で分ける。各プロジェクトは自分の生データ（`sources/`）と
Wiki（`wiki/`）を1フォルダに持つ。スキーマ層（`CLAUDE.md`・`playbooks/`・`templates/`・
`.claude/skills/`）はリポジトリ全体で共有する。

```
projects/
├── current.md            # 現在アクティブなプロジェクト（slug）を指すポインタ
├── <slug>/
│   ├── sources/          # このプロジェクトの生データ（不変層・AIは読むだけ）
│   └── wiki/
│       ├── hypotheses/<PREFIX>-H-NNN.md
│       ├── activities/<PREFIX>-ACT-NNN.md（＋ <PREFIX>-ACT-NNN-script.md）
│       ├── decisions/<PREFIX>-DEC-NNN.md
│       ├── views/        # 生成物
│       ├── index.md ├── log.md └── stage.md
└── ...
```

## ID は接頭辞つき（Obsidian のリンク一意性のため）

- ファイル名＝ID で、**プロジェクト接頭辞つき**（例 `SELF-H-001.md`、`SELF-ACT-001.md`）。
- Obsidian のwikilinkはファイル名がvault全体で一意でないと解決しないため、接頭辞で衝突を防ぐ。
- 採番は**種別×プロジェクトごと**の既存最大+1（プロジェクトごとに `-H-001` から始まる）。ID再利用禁止。

## 新しいプロジェクトの作り方

1. `projects/<slug>/` に `sources/` と `wiki/{hypotheses,activities,decisions,views}` を作る。
2. `wiki/index.md`（タイプ別カタログの空表）・`wiki/log.md`（見出しのみ）・`wiki/stage.md`（`current-stage: CPF`）を置く。既存の `projects/self/wiki/` の3ファイルを雛形として流用してよい。
3. 接頭辞（大文字）を決め、`projects/current.md` の一覧に追記して `current-project` を切り替える。

## 現在のプロジェクト

- **self**（接頭辞 `SELF`）: このツール自体のドッグフーディング実例。詳細は `projects/self/wiki/`。
