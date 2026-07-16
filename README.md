# 仮説検証Wiki（Hypothesis Wiki）

仮説検証活動（**CPF → FPF → PSF → SPF → PMF** の5ステージ）を通じて育てる LLM-wiki キット。
Karpathy の「LLM Wiki」パターンを仮説検証ドメインに適用し、Claude Code の AgentSkills で運用する。

- 4+1タイプの仮説（状況・行動／課題／ソリューション／買ってもらえる／自分たち）の**確信度**を、インタビューやプロトタイプデモを通じて段階的に高める
- 「確信度が低く、かつ現ステージで重要な仮説」の検証計画立案をAIが支援する
- 意思決定ログにより歴史性を後から学べ、ピボット・巻き戻しの判断を支援する

## 3層アーキテクチャ

| 層 | 場所 | 編集権 |
|---|---|---|
| Raw Sources（不変層） | `projects/<slug>/sources/` | 人間が置く。AIは読むだけ |
| The Wiki（生成・保守層） | `projects/<slug>/wiki/` | AIが規約に従って作成・更新 |
| The Schema（設定層） | `CLAUDE.md`・`playbooks/`・`templates/`・`.claude/skills/` | 人間が合意の上で変更（全プロジェクト共有） |

規約の詳細は [CLAUDE.md](CLAUDE.md) を参照。**仮説検証は案件（プロジェクト）単位で分ける**（[projects/README.md](projects/README.md)）。

## ディレクトリ構成

```
hypothesis-wiki/
├── CLAUDE.md               # スキーマ層（規約・ルール・ワークフロー）
├── README.md               # このファイル
├── .claude/skills/         # AgentSkills 6つ（grill/plan/ingest/view/decide/lint・共有）
├── templates/              # 雛形（hypothesis / activity / decision / interview-script・共有）
├── playbooks/              # ステージプレイブック（cpf〜pmf・共有）
├── docs/
│   ├── skill-improvements.md  # スキル改善バックログ（SI-NNN）
│   └── superpowers/specs/     # 設計ドキュメント
└── projects/               # 案件単位の仮説検証（各プロジェクトが sources と wiki を持つ）
    ├── current.md          # 現在アクティブなプロジェクト（slug）を指すポインタ
    └── <slug>/             # 例: self（このツール自体のドッグフーディング。接頭辞 SELF）
        ├── sources/        # このプロジェクトの生データ（読み取り専用）
        └── wiki/
            ├── hypotheses/<PREFIX>-H-NNN.md
            ├── activities/<PREFIX>-ACT-NNN.md   # ＋ <PREFIX>-ACT-NNN-script.md
            ├── decisions/<PREFIX>-DEC-NNN.md
            ├── views/      # 生成物（手編集禁止。例: hypotheses-list.md）
            ├── index.md    # 仮説カタログ
            ├── log.md      # 活動タイムライン（追記専用）
            └── stage.md    # 現在ステージと移行基準
```

ファイル名＝ID は**プロジェクト接頭辞つき**（例 `SELF-H-001.md`）。Obsidian のwikilinkは
vault全体でファイル名が一意でないと解決しないため、接頭辞で衝突を防ぐ。

## 使い始め方

Claude Code でこのリポジトリを開き、スキルを呼び出す。

| やりたいこと | スキル |
|---|---|
| 新しいプロジェクト（案件）を雛形から作成する | `/new-project` |
| 曖昧なアイデアを仮説レコードに精錬する（1問ずつ深掘り） | `/grill` |
| 次に検証すべき仮説の抽出とテストカード立案 | `/plan` |
| インタビュー録・デモ記録の取り込みと学習カード作成・確信度更新 | `/ingest` |
| バリュープロポジション／一覧／ボードのビュー生成 | `/view` |
| ステージ移行・ピボット・巻き戻しの意思決定 | `/decide` |
| Wikiの健全性チェック | `/lint` |

典型的な流れ:

0. `projects/current.md` で対象プロジェクトを確認・切り替える（新規なら `projects/<slug>/` を作る）
1. `/grill` — アイデアを反証可能な仮説（`<PREFIX>-H-NNN`）にする
2. `/plan` — 重要×確信度低の仮説を選び、テストカード付きの活動（`<PREFIX>-ACT-NNN`）を計画
3. 検証を実施し、生データを `projects/<slug>/sources/` に置く
4. `/ingest` — 学習カードを書き、確信度・ステータスを更新（承認フロー付き）
5. `/view list` / `/view vp` — 現状を俯瞰
6. 岐路で `/decide` — ステージ移行・ピボット・巻き戻しを記録
7. ときどき `/lint` — 健全性チェック

## 同梱の実例（このリポジトリ自体のドッグフーディング）

このリポジトリには、キット自体を題材に実際にスキルを回した実例が入っている（`/grill`→`/plan`→`/ingest`→`/view` の一巡）。

- 置き場所: `projects/self/`（接頭辞 `SELF`）。
- **仮説**: 状況・行動／課題／ソリューション／買ってもらえるの各タイプにまたがる `SELF-H-001`〜`SELF-H-013`（欠番 `SELF-H-002`・`SELF-H-003` は取り下げ済み。`log.md` に記録）。
- **活動**: 問題インタビューのテストカード＋現場用スクリプト（`SELF-ACT-001*`）、追加インタビュー（`SELF-ACT-002`）。
- **ビュー**: `projects/self/wiki/views/hypotheses-list.md`（関連リンク列＋バリューチェーン図つき）。
- **バリューチェーン**: 「繰り返す行動 → 切実な課題 → 解決策 → 市場で買ってもらえる」が CPF→PSF→SPF を貫く筋として繋がっている。

> ⚠️ ACT-001／ACT-002 のインタビューは**動作デモ用の架空データ**で、各 `sources/` ファイル冒頭に明記している。実プロジェクトでは実データに置き換えること。新規案件で使うときは下記「別案件へのキット複製」で実例を空にする。

運用で得た改善は `docs/skill-improvements.md`（SI-NNN）に蓄積し、スキル定義へ反映している。

## Obsidian で開く（探索ネットワークの可視化）

リポジトリのルートを Obsidian vault として開くと、仮説の系譜（派生・ピボット・巻き戻し）と
仮説↔活動↔意思決定の参照がグラフビューで一望できる。

- ファイル名は ID そのもの＋プロジェクト接頭辞（`SELF-H-021.md` 等）なので `[[SELF-H-021]]` のwikilinkがvault全体で一意に解決する（プロジェクト間のID衝突を防ぐ）。
- 相互参照は本文にwikilinkで書く規約（frontmatter配列だけではグラフに辺が出ない）。
- グラフビューでは `wiki/views/`（生成物）をフィルタで除外すると仮説ネットワークが見やすい。
- frontmatter は Dataview の動的テーブル（確信度一覧など）にもそのまま使える。
- `.obsidian/` は `.gitignore` 済み。

## 新しいプロジェクト（案件）の追加

同じリポジトリ内に案件を並べられる。**`/new-project` スキル**が `templates/project/` の雛形から
`projects/<slug>/`（`sources/` と空の `wiki/`）を作り、`projects/current.md` を切り替える。

手動で作る場合の要点（詳細は [projects/README.md](projects/README.md)）:

1. `templates/project/` を `projects/<slug>/` にコピー（`sources/`＋空の `wiki/` 一式が入っている）。
2. `wiki/stage.md` の日付プレースホルダを埋める。
3. 大文字の接頭辞（他プロジェクトと重複しない）を決め、`projects/current.md` の一覧に追記して `current-project` を切り替える。
4. `CLAUDE.md`・`playbooks/`・`templates/`・`.claude/skills/` は全プロジェクト共有なのでそのまま使う。

リポジトリごと別案件へ複製したい場合は、`projects/` 以下を空にして上記でプロジェクトを新規作成すればよい。

## 記述言語

すべて日本語。技術用語・ID・frontmatterキーは原文のまま。
