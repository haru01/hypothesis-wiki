# 仮説検証Wiki — スキーマ

このリポジトリは、仮説検証活動（CPF→FPF→PSF→SPF→PMF）を通じて育てるLLM-wikiである。
AIはこのファイルの規約に従って「規律あるWikiの保守者」として振る舞う。

## プロジェクト（案件単位）

仮説検証は**案件（プロジェクト）単位**で分ける。各プロジェクトは `projects/<slug>/` 配下に
自分の `sources/`（生データ）と `wiki/`（生成・保守層）を持つ。スキーマ層はリポジトリ全体で共有する。
現在アクティブなプロジェクトは `projects/current.md` の `current-project: <slug>` が持つ。
スキルはまず `projects/current.md` を読み、`projects/<slug>/` 配下を対象に動く（詳細は `projects/README.md`）。

以下このスキーマで `sources/` `wiki/` と書くときは、断りがなければ**現在のプロジェクトの
`projects/<slug>/sources/`・`projects/<slug>/wiki/`** を指す。

## 3層アーキテクチャ

| 層 | 場所 | 編集権 |
|---|---|---|
| Raw Sources（不変層） | `projects/<slug>/sources/` | 人間または `/ingest` が生データを置く。AIは**既存ファイルを改変しない**（新規追加は可・既存の編集禁止） |
| The Wiki（生成・保守層） | `projects/<slug>/wiki/` | AIが規約に従って作成・更新する |
| The Schema（設定層） | `ontology.yaml`（型・関係の正本）・`CLAUDE.md`・`AGENTS.md`（他エージェント向け入口）・`playbooks/`・`templates/`・`.claude/skills/` | 人間が合意の上で変更する（全プロジェクト共有） |

## オントロジー（型・関係の正本）

レコードの**型**（エンティティ H/ACT/DEC とサブタイプ）、レコード間の**型付きリンク**（関係）、
検証の**状態機械**（ステージ・ステータス・確信度・証拠の階梯）は、[ontology.yaml](ontology.yaml)
が唯一の正本（SSoT）である。人間可読な要約は [ontology.md](ontology.md)（`python3 tools/gen_ontology_doc.py`
で生成・手編集禁止）。ツール（`tools/hwlint.py`・`tools/gen_views.py`）は `tools/ontology.py` 経由で
ここを読むため、**語彙(enum)・関係・重点タイプ等をコードや本CLAUDE.mdに再定義しない**（二重管理・ドリフト防止）。

**関係（型付きリンク）** は5種。各々 domain（始点の型）→ range（終点の型）・cardinality・inverse（逆方向の呼称）を
`ontology.yaml` の `relations` で宣言する。`derived-from`（H→H・派生元）／`leads-to`（H→H・因果先）／
`addresses`（ソリューション仮説→課題仮説・対応課題）／`hypotheses`（ACT→H・検証対象）／
`based-on`（DEC→ACT・根拠活動）。関係は frontmatter 配列と本文 wikilink の**二重表現**を持つ（下記「スキル共通規約」3）。
`/lint` は各関係を宣言（domain/range/cardinality）に照らして検証し、`/view` の `relations` ビューが全関係型をグラフ化する。

## スキル共通規約（全スキルが従う入口）

`.claude/skills/` の各スキルは、冒頭でこの節を参照し**そのスキル固有の手順だけ**を書く（下記の規約を各スキルにコピーしない＝二重管理・ドリフト防止）。

1. **プロジェクト解決** — まず `projects/current.md` の `current-project: <slug>` を読み、「プロジェクト一覧」表で接頭辞（PREFIX）を確定する。以降 `sources/` `wiki/` は `projects/<slug>/` 配下を指す。`/lint` `/view` は現在プロジェクトのみを対象にする。ステージが要るスキルは `wiki/stage.md` と対応する `playbooks/<stage>.md` も読む。
2. **ID・接頭辞** — ID＝ファイル名＝frontmatter `id` を三者一致させ、すべてプロジェクト接頭辞つき（例 `SELF-H-001`）。採番は種別×プロジェクトごとの既存最大+1。再利用禁止（取り下げた番号は欠番として残す）。
3. **リンク記法** — 接頭辞つきノート間の相互参照は**必ず本文に wikilink**（`[[SELF-H-001]]`。frontmatter 配列だけではObsidianグラフに辺が出ない）。schema層（`playbooks/`・`CLAUDE.md` 等の非ノート）は**相対mdリンク**で書く（wikilinkは解決せずリンク切れになる）。`../` の深さは**参照元ファイルの位置で変わる**:

   | 参照元の位置 | 深さ | 例 |
   |---|---|---|
   | `wiki/` 直下（`stage.md`・`index.md`） | `../../../` | `[playbooks/cpf.md](../../../playbooks/cpf.md)` |
   | `wiki/<種別>/` 配下（H・ACT・DEC） | `../../../../` | `[playbooks/cpf.md](../../../../playbooks/cpf.md)` |
4. **.gitkeep** — 空ディレクトリ雛形の `.gitkeep` は、そのディレクトリに最初のレコードを作成したら削除してよい（任意）。
5. **承認規律** — 確信度・ステータスの変更は必ず ACT/DEC に紐づけ、**提案 → ユーザー承認 → 反映**する（不変ルール参照）。非対話/バッチ実行では、①成功基準の判定が機械的に〈支持〉/〈反証〉に定まり、②提案する確信度が証拠の階梯（下記「確信度とステータス」）の範囲に収まる場合に限り、提案内容を明示のうえ自動反映してよい。〈判断保留〉や、解釈を要する／証拠の階梯を超える引き上げは、必ず対話で承認を得る。

## レコード種別とスキーマ

すべてのレコードは `templates/` の雛形に従う。ファイル名は**IDそのもの**で、**プロジェクト接頭辞つき**
（例 `SELF-H-001.md`）。Obsidian のwikilinkはファイル名がvault全体で一意でないと解決しないため、
接頭辞 `<PREFIX>-` で衝突を防ぐ。frontmatter の **`id` はファイル名と完全に一致させる**（接頭辞つき。
例 `id: SELF-H-001`）。タイトルはfrontmatter `title` と本文H1に持つ。
相互参照は**必ず本文にwikilink**（`[[SELF-H-001]]`）で書く
（frontmatter配列だけではObsidianグラフに辺が現れないため）。

なお、schema層（`playbooks/`・`CLAUDE.md` など vault 内の接頭辞つきノートでないファイル）への参照は
**wikilinkではなく相対mdリンク**で書く。`../` の深さは参照元ファイルの位置で変わる（上記「スキル共通規約」3を参照。
`wiki/` 直下は `../../../`、`wiki/<種別>/` 配下の H・ACT・DEC は `../../../../`）。

### 仮説レコード `projects/<slug>/wiki/hypotheses/<PREFIX>-H-NNN.md`

```yaml
id: <PREFIX>-H-001                   # ファイル名と一致（接頭辞つき。例 SELF-H-001）
title: 短いタイトル
short-title: 短ラベル                 # 省略可。list の mermaid ノード用（8字程度）。省略時はタイトルを機械切り詰め
type: 状況・行動仮説 | 課題仮説 | ソリューション仮説 | 市場スケール仮説 | 自分たち仮説
status: 未検証 | 検証中 | 検証済み | 反証
confidence: 1-10
stage: CPF | FPF | PSF | SPF | PMF   # この仮説を主に検証するステージ
importance: auto | 1-10              # auto = 現在ステージから自動決定
derived-from: H-NNN                  # 省略可。派生・ピボット・巻き戻し再出発の系譜
leads-to: [H-NNN, ...]               # 省略可。因果的に導く先の仮説（list の mermaid 矢印。本文「系譜」にも wikilink 併記）
addresses: [H-NNN, ...]              # 省略可（ソリューション仮説）。対応する課題仮説（保持。vp 復活時のフィット表に使う）
core: true                           # 省略可。核心仮説なら true（list で ★ 表示）
```

本文: 反証可能な仮説文／前提／系譜リンク／確信度履歴テーブル（日付・確信度・ステータス・根拠・`[[ACT-NNN]]`）。

### 活動レコード `projects/<slug>/wiki/activities/<PREFIX>-ACT-NNN.md`

```yaml
id: <PREFIX>-ACT-001                 # ファイル名と一致（接頭辞つき。例 SELF-ACT-001）
title: 短いタイトル
type: interview | demo | survey | mvp-test | desk-research | self-reflection
date: YYYY-MM-DD
stage: CPF | FPF | PSF | SPF | PMF
hypotheses: [H-NNN, ...]
riskiest-assumption: 一文                  # 最もリスクの高い前提（この実験で崩れたら全体が崩れる一点）。検証前に記入。board の背骨
outcome: 起票|支持|反証|判断保留|是正       # 検証後に記入（検証前は空＝未実施）。board サマリへ射影
```

本文は2部構成（Strategyzer流）:
- **テストカード**（検証前に記入・後から書き換えない）: 目的／方法／指標／成功基準
- **学習カード**（検証後に記入）: **学びの要点**（board へ射影する一行の見出し的学び）／事実（observed）／解釈（inference）／驚き・想定外／確信度の更新テーブル／次のアクション

### 意思決定レコード `projects/<slug>/wiki/decisions/<PREFIX>-DEC-NNN.md`

```yaml
id: <PREFIX>-DEC-001                 # ファイル名と一致（接頭辞つき。例 SELF-DEC-001）
title: 短いタイトル
date: YYYY-MM-DD
type: stage-transition | pivot | persevere | rollback | kill
based-on: [ACT-NNN, ...]
```

本文: 確信度スナップショット（全重要仮説の当時の値）／選択肢と判断理由／巻き戻しポイント
（この判断が誤りと判明したときどの仮説状態・どの問いに戻るか）／次の一手（前向きの戦略的現在地。board の「現在地」へ射影）。

### プロトタイプ生成物 `projects/<slug>/wiki/prototypes/<PREFIX>-ACT-NNN/index.html`

`/prototype` が仮説から生成する自己完結HTML（LP／2〜3画面モックアップ）。レコードではなく**生成物**で、
demo/interview の活動（ACT）に紐づく（ACTのテストカードから相対mdリンクで参照し、対象仮説の本文にも
`[[<PREFIX>-ACT-NNN]]` を張る）。`views/` と同格に扱い、**手編集せず再生成で上書きする**。生成しても
確信度・ステータスは動かさない（見せて反応を得たあとの学習カード記入・確信度更新は `/ingest` に委ねる）。

## 確信度とステータス（2軸・別管理）

**確信度（1〜10）** — 証拠の強さの目安:

| 確信度 | 目安 |
|---|---|
| 1-2 | 勘・思いつき |
| 3-4 | 二次情報・状況証拠あり |
| 5-6 | 検証中で手応えあり（定性的証拠が集まりつつある） |
| 7-8 | 検証済みで確信度が高い |
| 9 | 反証を試みても崩れなかった |
| 10 | 事実（観測された確定事項） |

**ステータス** — 検証の進捗: `未検証` → `検証中` → `検証済み` ／ `反証`

**証拠の階梯** — 確信度を上げる根拠には強さの序列がある（弱→強。語彙・序列の正本は
[ontology.md](ontology.md) の `evidence-ladder`）:

〈発言〉好意的な意見・「いいね」 ＜ 〈自認〉自分の言葉で課題を語る ＜ 〈実コスト〉時間・金・手戻りを払っている証拠 ＜ 〈行動〉実際にとった行動・現在の使用 ＜ 〈支払い〉対価・前払い・導入コミット

- 確信度 5-6 に上げるには〈自認〉以上、7-8 には〈実コスト〉か〈行動〉以上の証拠を要する。〈発言〉だけで上げない（interest ≠ intent）。
- **架空/シミュレーションデータ由来の確信度は上限8**。9-10 は実観測に限る。
- 確信度履歴テーブルの「根拠」列は、先頭に証拠種別タグを付けて書く（例 `〈自認〉〈実コスト〉5名中3名が…`）。使える証拠種別タグ（階梯5段＋補助 〈二次〉〈架空〉）の正本は [ontology.md](ontology.md)（`evidence-ladder` ＋ `evidence-aux`）。
- 「検証中なのに確信度 3-4」は異常ではない。**検証したが証拠が集まっていない**正当な状態（判断保留）であり、次の検証を計画する対象になる。

### 不変ルール（AIが必ず守ること）

1. **確信度・ステータスの変更は必ず活動（ACT）か意思決定（DEC）に紐づける**。根拠レコードなしに書き換えない
2. 変更時は仮説レコードの確信度履歴テーブルに1行追記し、`projects/<slug>/wiki/log.md` にも追記する
3. `projects/<slug>/sources/` の既存ファイルは改変・削除しない（`/ingest` による新規生データの追加は可。一度置いた観測データは後から書き換えない）。`projects/<slug>/wiki/log.md` は追記のみ（過去行の編集禁止）
4. `projects/<slug>/wiki/views/` と `projects/<slug>/wiki/prototypes/` は生成物。記録の修正はレコード側で行い、生成物は再生成する
5. ID採番は**種別×プロジェクトごと**に既存最大値+1で、プロジェクト接頭辞つき（例 `SELF-H-001`）。IDの再利用禁止（取り下げた番号は欠番として残す）
6. テストカードの成功基準は検証開始後に書き換えない（後知恵バイアス防止）

## ステージと重要度

現在ステージは（プロジェクトごとに）`projects/<slug>/wiki/stage.md` が持つ。各ステージの詳細
（問いかけバンク・検証手法・移行基準）は共有の `playbooks/<stage>.md` を参照。インタビュー共通の心得
（確証バイアス・反証質問・発見型の選択権）は `playbooks/interviewing.md` を参照。

**ステージの正式名称**: CPF = Customer Problem Fit ／ FPF = Founder Problem Fit ／ PSF = Problem Solution Fit ／
SPF = Solution Product Fit ／ PMF = Product Market Fit（各 `playbooks/<stage>.md` の見出しが正典）。

**ステージ→重点仮説タイプ**（`importance: auto` の解決に使う）は [ontology.md](ontology.md)
（正本 [ontology.yaml](ontology.yaml) の `stage-focus`）の「状態機械 > ステージ」表を参照する。
ここには再掲しない（語彙・マッピングの二重管理・ドリフト防止。本CLAUDE.md冒頭「オントロジー」節の方針）。

重点タイプは**重要度 高=8** として扱い、それ以外の `auto` は重要度4として扱う。手動指定（1-10）があればそれが優先。

**次に検証すべき仮説** = 重要度が高く、確信度が低く、ステータスが未検証/検証中のもの
（アサンプションマッピングの「重要×証拠なし」象限）。

## log.md の形式（追記専用・grep可能）

```
## [YYYY-MM-DD] <type> | <ID> <要約> → <影響仮説と確信度変化>
```

type は `hypothesis` `interview` `demo` `survey` `mvp-test` `desk-research` `self-reflection` `decision` `lint` のいずれか。
例: `grep "decision" projects/<slug>/wiki/log.md` で意思決定だけを抽出できる。

## ワークフロー（スキルとの対応）

| やりたいこと | スキル |
|---|---|
| 新しいプロジェクト（案件）を雛形から作成する | `/new-project` |
| 対象ドメイン・競合を実Web検索で調べ、想定ユーザの行動/課題仮説を起票し競合を比較する | `/desk-research` |
| 曖昧なアイデアを仮説レコードに精錬する（1問ずつ深掘り） | `/formulate` |
| 次に検証すべき仮説の抽出とテストカード立案 | `/plan` |
| 検証用のHTMLプロトタイプ（LP／モックアップ）を仮説から生成しdemo/interviewのACTに紐づける | `/prototype` |
| インタビュー録・デモ記録の取り込みと学習カード作成・確信度更新 | `/ingest` |
| 一覧／ボードのビュー生成 | `/view` |
| ステージ移行・ピボット・巻き戻しの意思決定 | `/decide` |
| Wikiの確信度に揺さぶり（ちゃぶ台返し）をかけ、バイアスを突いて根拠づけて引き下げ、新しい探索域を発見する | `/chabudai` |
| Wikiの健全性チェック | `/lint` |

## 記述言語

すべて日本語。技術用語・ID・frontmatterキーは原文のまま。
