# 仮説検証Wiki（Hypothesis Wiki）

仮説検証活動（**CPF → FPF → PSF → SPF → PMF** の5ステージ）を通じて育てる LLM-wiki キット。
Karpathy の「LLM Wiki」パターンを仮説検証ドメインに適用し、Claude Code の AgentSkills で運用する。

- 4+1タイプの仮説（状況・行動／課題／ソリューション／買ってもらえる／自分たち）の**確信度**を、インタビューやプロトタイプデモを通じて段階的に高める
- 「確信度が低く、かつ現ステージで重要な仮説」の検証計画立案をAIが支援する
- 意思決定ログにより歴史性を後から学べ、ピボット・巻き戻しの判断を支援する

## 3層アーキテクチャ

| 層 | 場所 | 編集権 |
|---|---|---|
| Raw Sources（不変層） | `sources/` | 人間が置く。AIは読むだけ |
| The Wiki（生成・保守層） | `wiki/` | AIが規約に従って作成・更新 |
| The Schema（設定層） | `CLAUDE.md`・`playbooks/`・`templates/` | 人間が合意の上で変更 |

規約の詳細は [CLAUDE.md](CLAUDE.md) を参照。

## ディレクトリ構成

```
hypothesis-wiki/
├── CLAUDE.md               # スキーマ層（規約・ルール・ワークフロー）
├── README.md               # このファイル
├── .claude/skills/         # AgentSkills 6つ
│   ├── grill/  ├── plan/  ├── ingest/
│   ├── view/   ├── decide/ └── lint/
├── templates/              # 雛形（hypothesis / activity / decision / interview-script）
├── playbooks/              # ステージプレイブック（cpf〜pmf）
├── sources/                # 不変層（生データ置き場・読み取り専用）
└── wiki/
    ├── hypotheses/H-NNN.md   ├── activities/ACT-NNN.md   ├── decisions/DEC-NNN.md
    ├── views/        # 生成物（手編集禁止）
    ├── index.md      # 仮説カタログ
    ├── log.md        # 活動タイムライン（追記専用）
    └── stage.md      # 現在ステージと移行基準
```

## 使い始め方

Claude Code でこのリポジトリを開き、スキルを呼び出す。

| やりたいこと | スキル |
|---|---|
| 曖昧なアイデアを仮説レコードに精錬する（1問ずつ深掘り） | `/grill` |
| 次に検証すべき仮説の抽出とテストカード立案 | `/plan` |
| インタビュー録・デモ記録の取り込みと学習カード作成・確信度更新 | `/ingest` |
| バリュープロポジション／一覧／ボードのビュー生成 | `/view` |
| ステージ移行・ピボット・巻き戻しの意思決定 | `/decide` |
| Wikiの健全性チェック | `/lint` |

典型的な流れ:

1. `/grill` — アイデアを反証可能な仮説（H-NNN）にする
2. `/plan` — 重要×確信度低の仮説を選び、テストカード付きの活動（ACT-NNN）を計画
3. 検証を実施し、生データを `sources/` に置く
4. `/ingest` — 学習カードを書き、確信度・ステータスを更新（承認フロー付き）
5. `/view list` / `/view vp` — 現状を俯瞰
6. 岐路で `/decide` — ステージ移行・ピボット・巻き戻しを記録
7. ときどき `/lint` — 健全性チェック

## Obsidian で開く（探索ネットワークの可視化）

リポジトリのルートを Obsidian vault として開くと、仮説の系譜（派生・ピボット・巻き戻し）と
仮説↔活動↔意思決定の参照がグラフビューで一望できる。

- ファイル名は ID そのもの（`H-021.md` 等）なので `[[H-021]]` のwikilinkが常に解決する。
- 相互参照は本文にwikilinkで書く規約（frontmatter配列だけではグラフに辺が出ない）。
- グラフビューでは `wiki/views/`（生成物）をフィルタで除外すると仮説ネットワークが見やすい。
- frontmatter は Dataview の動的テーブル（確信度一覧など）にもそのまま使える。
- `.obsidian/` は `.gitignore` 済み。

## 別案件へのキット複製

このリポジトリはキットとして再利用できる。

1. リポジトリをコピーする。
2. `wiki/hypotheses/` `wiki/activities/` `wiki/decisions/` の中身と `sources/` の中身を空にする（`.gitkeep`・各 `README.md` は残す）。
3. `wiki/index.md` を初期状態（各表「まだない」）に戻し、`wiki/log.md` を見出しだけに、`wiki/stage.md` を `CPF` に戻す。
4. `wiki/views/` の生成物を削除する。
5. `CLAUDE.md`・`playbooks/`・`templates/` はスキーマ層としてそのまま流用（プロジェクト固有に調整する場合は合意の上で変更）。

## 記述言語

すべて日本語。技術用語・ID・frontmatterキーは原文のまま。
