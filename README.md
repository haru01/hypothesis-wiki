# 仮説検証Wiki（Hypothesis Wiki）

仮説検証活動（**CPF → FPF → PSF → SPF → PMF** の5ステージ）を、**単一の確信度（1〜10）という一本の物差し**と、
**証拠なしには確信度を動かせない強制紐づけ**で育てる LLM-wiki キット。
曖昧なアイデアを反証可能な仮説にし、インタビューやプロトタイプで検証し、学びと意思決定を
「後から歴史を追える記録」として積み上げる。不変ルールは規約（CLAUDE.md）に書くだけでなく、
決定論 lint（`tools/hwlint.py`）とフック（git pre-commit＋Claude Code フック）が機械的に守らせる。

## これは何か（目的）

仮説検証の現場では、こういうことが起こりがちだ。

- 学びが Slack・スプレッドシート・議事録に散らばり、**過去の検証が忘れられる**。
- 「いいですね」と言われただけで購買意向と取り違え、**偽の確証**で前に進んでしまう。
- なぜその判断をしたのか**経営層に説明できず**、合意形成が滞る。

このキットは、検証の「学び」と「判断」を1か所に構造化して積み上げることでこれに抗う。

- 4+1タイプの仮説（状況・行動／課題／ソリューション／買ってもらえる／自分たち）の**確信度**を、
  インタビューやプロトタイプデモという**証拠（活動・意思決定レコード）に紐づけて**段階的に高める。
- 「確信度が低く、いま重要な仮説」をAIが選び、検証計画（テストカード）まで立てる。
- ピボット・巻き戻しの意思決定をログに残し、歴史を後から学べるようにする。

Karpathy の「LLM Wiki」パターンを仮説検証ドメインに適用したもので、規約（[CLAUDE.md](CLAUDE.md)）に従う
AIが「規律あるWikiの保守者」として運用する。

### なぜこのキットか（競合の中での立ち位置）

2ラウンドの競合調査（[docs/competitive-analysis.md](docs/competitive-analysis.md)）では、
①プレーンテキスト/Git/Obsidian の LLM-wiki、②CPF→PMF のステージゲート、③証拠に強制紐づけされる
単一の1〜10確信度——の三点を同時に満たす既存プロダクトは確認できなかった。

- **単一の確信度が全記録の背骨** — Strategyzer は定性ティア（Valid/Invalid/Unknown）、GLIDR は確信度を露出しない。
  「重要 × 確信度低」の仮説を機械的に選べるのは、一本の数直線があるからだ。
- **証拠なしに確信度・ステータスを変えられない** — 競合ではテンプレ上の慣行に留まる紐づけを、
  ここでは決定論 lint と git/Claude Code フック（テストカード事後書き換え検出・sources/ 書き込みガードを含む）が
  機械的に強制する。
- 3層アーキテクチャやテストカード自体は既存パターン（Karpathy / Strategyzer）の適用であり、発明ではない。
  立ち位置は「組み合わせ」にある。

> 注: 上記は競合の一次ページ/README にもとづく相対比較であり、効果の第三者検証はまだ無い。
> 詳細な但し書きは競合分析メモ §4 を参照。

## 仕組み（3層・5ステージ・確信度）

**3層アーキテクチャ** — 生データ・生成物・規約を分けて管理する。

| 層 | 場所 | 編集権 |
|---|---|---|
| Raw Sources（不変層） | `projects/<slug>/sources/` | 人間または `/ingest`・`/desk-research` が生データを置く。AIは既存ファイルを改変しない（新規追加は可） |
| The Wiki（生成・保守層） | `projects/<slug>/wiki/` | AIが規約に従って作成・更新 |
| The Schema（設定層） | `ontology.yaml`（型・関係の正本）・`CLAUDE.md`・`AGENTS.md`・`playbooks/`・`templates/`・`.claude/skills/` | 人間が合意の上で変更（全案件で共有） |

**オントロジー（型・関係の正本）** — レコードの型（仮説 H／活動 ACT／意思決定 DEC とサブタイプ）、
レコード間の型付きリンク（`derived-from`／`leads-to`／`addresses`／`hypotheses`／`based-on` の5関係）、
検証の状態機械（ステージ・ステータス・確信度・証拠の階梯）は、[ontology.yaml](ontology.yaml) を唯一の正本（SSoT）とする。
人間可読な要約は [ontology.md](ontology.md)（`python3 tools/gen_ontology_doc.py` で生成・手編集禁止）。
lint やビュー生成ツールは `tools/ontology.py` 経由でここを読むため、語彙をコードや規約に再定義しない（二重管理・ドリフト防止）。

**5ステージ** — 顧客と課題から市場まで、段階的に確信度を上げる。詳細は `playbooks/<stage>.md`。

| ステージ | 正式名称 | 問うこと |
|---|---|---|
| CPF | Customer Problem Fit | 顧客と課題は実在するか |
| FPF | Founder Problem Fit | 自分たちが取り組む理由があるか |
| PSF | Problem Solution Fit | 解決策は課題の芯を捉えるか |
| SPF | Solution Product Fit | 繰り返し使うプロダクトになるか |
| PMF | Product Market Fit | 市場が引き寄せるか |

**確信度は2軸で別管理** — 確信度（1〜10、証拠の強さ）とステータス（未検証 → 検証中 → 検証済み ／ 反証）。
確信度・ステータスの変更は**必ず活動（ACT）か意思決定（DEC）に紐づける**（勘で書き換えない）。

**案件（プロジェクト）単位** — 仮説検証は `projects/<slug>/` 単位で分け、各案件が自分の `sources/` と `wiki/` を持つ。
スキーマ層は全案件で共有。規約の詳細は [CLAUDE.md](CLAUDE.md)、案件分割の考え方は [projects/README.md](projects/README.md) を参照。

## クイックスタート（チュートリアル）

Claude Code でこのリポジトリを開き、スキルを呼ぶ。新しい案件を1本まわす流れはこうだ。

| やりたいこと | スキル |
|---|---|
| 新しい案件（プロジェクト）を雛形から作る | `/new-project` |
| 対象ドメイン・競合を実Web検索で調べ、想定ユーザの課題仮説を起票する | `/desk-research` |
| 曖昧なアイデアを反証可能な仮説に精錬する（1問ずつ深掘り） | `/formulate` |
| 次に検証すべき仮説を選び、テストカードを立案する | `/plan` |
| 仮説から LP／モックアップの HTML プロトタイプを生成する | `/prototype` |
| インタビュー録・デモ記録を取り込み、学習カード作成・確信度更新 | `/ingest` |
| 一覧／ボードのビューを生成する | `/view` |
| ステージ移行・ピボット・巻き戻しの意思決定を記録する | `/decide` |
| 確信度に揺さぶり（ちゃぶ台返し）をかけ、バイアスを突いて根拠づけ引き下げる | `/chabudai` |
| Wiki の健全性をチェックする | `/lint` |

典型的な流れ:

0. `projects/current.md` で対象案件を確認（新規なら次の手順で作る）。
1. **`/new-project`** — 案件を `projects/<slug>/` に作り、接頭辞（例 `ACME`）と現在案件を設定する。
2. **`/desk-research`**（任意・初期リサーチ） — 対象ドメインと競合を実Web検索で調べ、想定ユーザの状況・行動仮説と課題仮説を出典付きで起票する（確信度3-4）。相場観を掴んでから `/formulate` に入りたいときに。
3. **`/formulate`** — アイデアを反証可能な仮説（`<PREFIX>-H-NNN`）にする。タイプ・初期確信度・ステータスを付けて起票。
4. **`/plan`** — 「重要 × 確信度低」の仮説を選び、検証前のテストカード（目的・方法・指標・成功基準）を持つ活動（`<PREFIX>-ACT-NNN`）を計画する。
5. **`/prototype`** — 見せて反応を得たい仮説から、自己完結の HTML プロトタイプ（LP／2〜3画面モックアップ）を `wiki/prototypes/` に生成し、demo/interview の ACT に紐づける。
6. **検証を実施** — インタビュー録やデモ記録などの生データを `projects/<slug>/sources/` に置く（不変層。AIは読むだけ）。
7. **`/ingest`** — 生データから活動の学習カード（事実・解釈・驚き）を書き、確信度・ステータスの更新を承認フロー付きで反映する。
8. **俯瞰と岐路** — `/view list` で現状を俯瞰、岐路で `/decide`（ステージ移行・ピボット・巻き戻し）、ときどき `/lint` で健全性チェック。高確信度の仮説が甘くないか疑いたいときは `/chabudai` で揺さぶり（ちゃぶ台返し）をかけ、バイアスを突いて根拠づけて引き下げる。

## チャットで頼む・聞く（自然言語でOK）

スラッシュコマンドを覚える必要はない。**やりたいことを日本語でチャットに書けば、Claude Code が適切なスキルを選ぶ**。
そして、このWikiについて**分からないことはそのままチャットで質問すればいい**——AIが規約（[CLAUDE.md](CLAUDE.md)）と
`wiki/` の中身を読んで答える。困ったらまず「このリポジトリは何をするもの？どう使う？」と聞いてみるとよい。

サンプルプロンプト:

| 言いたいこと（チャットにこう書く） | 起きること |
|---|---|
| 「このリポジトリは何をするもの？どう使い始めればいい？」 | 使い方を説明してくれる（読むだけ） |
| 「新しい案件『◯◯』を始めたい」 | `/new-project` が走り、案件を作る |
| 「この分野の競合と想定ユーザの課題を調べて仮説にして」 | `/desk-research` が実Web検索で調べ、課題仮説を出典付きで起票する |
| 「『AIが検証記録を自動でまとめてくれると助かるはず』を仮説にしたい」 | `/formulate` が反証可能な仮説に精錬する |
| 「次に何を検証すべき？計画を立てて」 | `/plan` が重要×確信度低の仮説を選びテストカードを作る |
| 「この仮説を試すためのLPを作って」 | `/prototype` が HTML の LP を生成し ACT に紐づける |
| 「インタビュー結果を `sources/` に置いたので取り込んで」 | `/ingest` が学習カードを書き、確信度更新を提案する |
| 「今の仮説の状況を一覧（ボード）で見せて」 | `/view` が最新のビューを生成する |
| 「CPF から FPF に進んでいい？判断を記録したい」 | `/decide` が意思決定レコードを作る |
| 「この確信度は甘くないか揺さぶって（ちゃぶ台返し）」 | `/chabudai` がバイアス・根拠不足を突いて確信度を根拠づけ引き下げる |
| 「Wiki に矛盾や放置がないか点検して」 | `/lint` が健全性レポートを出す |
| 「`SELF-H-006` の確信度がなぜ8なのか、根拠を教えて」 | 記録を読んで根拠を説明してくれる（読むだけ） |
| 「重要なのに確信度が低い仮説はどれ？」 | 現状を分析して答えてくれる（読むだけ） |

> 「読むだけ」の質問は記録を書き換えない。確信度・ステータスを動かす操作（`/ingest`・`/decide` など）は
> 必ず根拠レコードに紐づけ、承認フローを挟む。

## 実例で見る（同梱のドッグフーディング: self）

このリポジトリには、キット自体を題材にスキルを一巡させた実例が入っている（`projects/self/`、接頭辞 `SELF`）。
**この案件のインタビュー等はすべて動作デモ用の架空シミュレーションデータ**で、各 `sources/` と `index.md` の
冒頭に明記している。

たどれるストーリー:

- **CPF** — 「作る前に検証を反復する実践者」を想定顧客に、核心となる3つの課題仮説を検証した:
  記録が散逸し過去の学びが忘れられる（`SELF-H-004`）／好反応を購買意向と取り違え偽の確証で進む（`SELF-H-006`）／
  根拠を経営層に説明できず合意が滞る（`SELF-H-008`）。いずれも確信度8・検証済み。
- **`/decide`** — 核心クラスタが移行基準を満たしたので、`SELF-DEC-001` で **CPF→FPF** に移行（`stage.md` は現在 FPF）。
- **`/prototype`** — FPF から先取りして「確信度Wiki」の LP（`SELF-ACT-004`、`wiki/prototypes/SELF-ACT-004/index.html`）を
  生成し、提示インタビューにかけた。
- **反証も学び** — LP は好反応でも、乗り換え・対価という**行動**の意向は出ず、ソリューション仮説 `SELF-H-009` と
  買ってもらえる仮説 `SELF-H-010` は**反証**（interest ≠ intent）。「いいね」を確証と取り違えない、という
  このキットの狙いを自ら実演した形になっている。

`/view` が生成した俯瞰は `projects/self/wiki/views/`（`board.md`・`hypotheses-list.md`）にある。
運用で得た改善は `docs/skill-improvements.md`（SI-NNN）に蓄積し、スキル定義へ反映している。

> ⚠️ self は**架空データによるデモ**。新しい案件で使うときは下記「新しいプロジェクトの追加」で、実データに置き換えること。

## ディレクトリ構成

```
hypothesis-wiki/
├── ontology.yaml           # 型・関係・状態機械の正本（SSoT・全案件で共有）
├── ontology.md             # 上記の人間可読版（gen_ontology_doc.pyで生成・手編集禁止）
├── CLAUDE.md               # スキーマ層（規約・レコードスキーマ・ワークフロー）
├── AGENTS.md               # 非Claudeエージェント向けの入口（正典はCLAUDE.md）
├── README.md               # このファイル（目的・使い方）
├── .claude/skills/         # AgentSkills 10つ（new-project/desk-research/formulate/plan/prototype/ingest/view/decide/chabudai/lint・共有）
├── .claude/settings.json   # Claude Codeフック（sourcesガード・Stop時lint/view再生成・hooksPath自動設定）
├── .githooks/              # git pre-commitフック（有効化: git config core.hooksPath .githooks）
├── tools/                  # オントロジーローダ（ontology.py）・決定論lint（hwlint.py）・ビュー生成（gen_views.py）・ontology.md生成（gen_ontology_doc.py）・テストカード不変チェック・フック実体
├── tests/                  # 上記ツールのunittest
├── templates/              # 雛形（hypothesis/activity/decision/interview-script/prototype-lp.html/prototype-mockup.html/project・共有）
├── playbooks/              # ステージプレイブック（cpf/fpf/psf/spf/pmf）＋インタビュー心得（interviewing・共有）
├── docs/
│   ├── skill-improvements.md        # スキル改善バックログ（SI-NNN）
│   ├── ontology-improvements.md     # オントロジー改善バックログ
│   ├── competitive-analysis.md      # 競合調査メモ
│   └── superpowers/{specs,plans}/   # 設計・計画ドキュメント
└── projects/               # 案件単位の仮説検証（各案件が sources と wiki を持つ）
    ├── current.md          # 現在アクティブな案件（slug）を指すポインタ
    └── <slug>/             # 例: self（このツール自体のドッグフーディング。接頭辞 SELF）
        ├── sources/        # 生データ（読み取り専用）
        └── wiki/
            ├── hypotheses/<PREFIX>-H-NNN.md
            ├── activities/<PREFIX>-ACT-NNN.md          # ＋ <PREFIX>-ACT-NNN-script.md（インタビュー台本）
            ├── decisions/<PREFIX>-DEC-NNN.md
            ├── prototypes/<PREFIX>-ACT-NNN/index.html  # /prototype の生成物
            ├── views/      # 生成物（手編集禁止。例: hypotheses-list.md）
            ├── index.md    # 仮説カタログ
            ├── log.md      # 活動タイムライン（追記専用）
            └── stage.md    # 現在ステージと移行基準
```

ファイル名＝ID は**プロジェクト接頭辞つき**（例 `SELF-H-001.md`）。Obsidian のwikilinkは vault 全体で
ファイル名が一意でないと解決しないため、接頭辞で衝突を防ぐ。

## Obsidian で開く（探索ネットワークの可視化）

リポジトリのルートを Obsidian vault として開くと、仮説の系譜（派生・ピボット・巻き戻し）と
仮説↔活動↔意思決定の参照がグラフビューで一望できる。

- ファイル名は ID そのもの＋プロジェクト接頭辞（`SELF-H-004.md` 等）なので `[[SELF-H-004]]` のwikilinkが vault 全体で一意に解決する（プロジェクト間の ID 衝突を防ぐ）。
- 相互参照は本文にwikilinkで書く規約（frontmatter配列だけではグラフに辺が出ない）。
- グラフビューでは `wiki/views/`（生成物）をフィルタで除外すると仮説ネットワークが見やすい。
- frontmatter は Dataview の動的テーブル（確信度一覧など）にもそのまま使える。
- `.obsidian/` は `.gitignore` 済み。

## 新しいプロジェクト（案件）の追加

同じリポジトリ内に案件を並べられる。**`/new-project` スキル**が `templates/project/` の雛形から
`projects/<slug>/`（`sources/` と空の `wiki/` 一式）を作り、`projects/current.md` を切り替えるところまで行う。

手動で作る場合の要点（詳細は [projects/README.md](projects/README.md)）:

1. `templates/project/` を `projects/<slug>/` にコピーする。
2. `wiki/stage.md` の日付プレースホルダを埋める。
3. 大文字の接頭辞（他案件と重複しない）を決め、`projects/current.md` の一覧に追記して `current-project` を切り替える。
4. `ontology.yaml`・`CLAUDE.md`・`AGENTS.md`・`playbooks/`・`templates/`・`.claude/skills/` は全案件共有なのでそのまま使う。

リポジトリごと別案件へ複製したい場合は、`projects/` 以下を空にして上記で案件を新規作成すればよい。

## 記述言語

すべて日本語。技術用語・ID・frontmatterキーは原文のまま。
