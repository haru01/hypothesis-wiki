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

**推奨: `/new-project` スキル**を使う。`templates/project/` の雛形から `projects/<slug>/`
（`sources/` と空の `wiki/` 一式）を作り、`projects/current.md` を切り替えるところまで行う。

手動で作る場合:

1. `templates/project/` を `projects/<slug>/` にコピーする（`cp -r templates/project/. projects/<slug>/`）。`sources/`（README付き）と `wiki/{hypotheses,activities,decisions,views}`＋`index.md`・`log.md`・`stage.md` が揃う。
2. `wiki/stage.md` の `updated:` とステージ履歴の `YYYY-MM-DD` を今日の日付にする。
3. 接頭辞（大文字・他プロジェクトと重複しない）を決め、`projects/current.md` の一覧に追記して `current-project` を切り替える。

## 現在のプロジェクト

- **self**（接頭辞 `SELF`）: このツール自体のドッグフーディング実例。詳細は `projects/self/wiki/`。
