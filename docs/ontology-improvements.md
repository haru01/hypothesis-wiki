# オントロジー改善バックログ

オントロジー層（`ontology.yaml` を SSoT とする型・関係・状態機械。コミット `6183e1c` で導入）を
運用に効かせるための改善余地を記録する。各項目は「対象／状態／課題／改善案／根拠」で書く。
状態は `未対応` `対応中` `対応済み`。

## 現状評価（サマリ）

土台（`ontology.yaml` を SSoT に、`ontology.py` がローダ、`hwlint`/`gen_views` が駆動、`relations`
ビュー新設）は正しく敷けている。ただし全体として **「宣言したが、機械もスキルもまだ使い切っていない」**
状態にある。3つの症状が出ている:

1. **SSoT が二重化している** — `CLAUDE.md` が状態機械（stage-focus・statuses・confidence・
   evidence-ladder・ステージ正式名称）を丸ごと再定義し、スキルがそちら経由で参照する連鎖ができている。
   `CLAUDE.md:30` の「語彙(enum)・関係・重点タイプ等をコードや本CLAUDE.mdに再定義しない」宣言と矛盾。
2. **関係が張られていない** — 実データで `addresses` は13仮説中1本（SELF-H-009のみ）、`derived-from` は
   5/13、ai-reskilling は系譜(derived-from)が全滅。frontmatter記入を明示したスキル手順が無いのが主因。
3. **オントロジーがあるのに機械検証・射影に活きていない** — 証拠の階梯・確信度の整合・逆参照を
   lint も view も十分使っていない。

改善を A〜E の5カテゴリに整理する。**A・B・C・D は「導入したオントロジーを効かせる」直接の続き**で
リスクが低く効果が大きい。E は表現力の拡張で設計合意を要する。

さらに F・G を追加する。これは外部調査（「LLM Wiki × オントロジー/ナレッジグラフ」統合リポジトリ群の設計パターン
分析）から、このrepoにまだ無く哲学（決定論・SSoT・証拠強制）に馴染む2点を取り込んだもの:
**F. トポロジー駆動の探索域ギャップ検出**（infranodus/nashsu の「構造的知識ギャップ・孤立ノード・ブリッジ」検出の適用）、
**G. 時間軸＝確信度の陳腐化**（LLM Wiki v2 の忘却曲線・staleness の適用。ただし自動減衰はせず可視化に留める）。
逆に、調査が挙げるベクトル検索・BFS検索ツール・GUI は現規模（十数レコード）で過剰と判断し採らない（末尾「H. あえて採らない」参照）。

## 実装状況（2026-07-21）

A〜D を実装済み（各項目の「状態」を参照）。E は設計合意を要するため未着手（提案のまま）。
テストは 46 → 64 件に増加、全パス。ビューは意図した差分（D-2/D-3）以外バイト不変、lint は
既存の evidence-tag warning 15件のみで新規誤検知ゼロ（B の新チェックは潜在ガードとして機能）。

| カテゴリ | 実装コミット（要旨） |
|---|---|
| A-2/A-3/A-4 | `feat(ontology): 証拠タグ・架空マーカー語彙を ontology.yaml へ一元化` |
| A-1 | `docs(ontology): CLAUDE.md の重複表を ontology.md 参照へ一本化` |
| B-1〜B-5 | `feat(lint): status↔confidence・証拠の階梯・DEC根拠・循環の機械検証を追加` |
| C-1〜C-4 | `docs(skills): 関係リンクの作成手順を補強し張り忘れを塞ぐ` |
| D-1〜D-4 | `feat(views): team役割の取りこぼし修正・現在地の充実・関係節の完全化` |
| E-1〜E-4 | 未着手（要設計合意） |
| F-1 | `feat(lint,views): 未検証の重点仮説（hypotheses入次数0）を検出・最優先表示`（2026-07-21） |
| F-2 | `feat(lint,views): 課題↔解決の構造ギャップ（課題なき解決／未対応の課題）を検出`（2026-07-21） |
| F-3 | 未着手（調査由来・要設計。孤立/ブリッジ/下流依存度の算出） |
| G-1〜G-2 | 未着手（調査由来。G1 は staleness 可視化で低リスク、G2 は E4 と統合） |

---

## A. SSoT一本化 ／ ドリフト解消

導入の「完遂」に相当。放置すると `ontology.yaml` を直しても効かない箇所が残る。

### OI-A1: `CLAUDE.md` の状態機械表が `ontology.yaml` と二重定義

- **対象**: `CLAUDE.md`、`.claude/skills/{plan,ingest,chabudai,prototype}/SKILL.md`
- **状態**: 対応済み（2026-07-21・上表のコミット参照）
- **課題**: `CLAUDE.md:122-176` が状態機械を `ontology.yaml` と別実体で持つ:
  - ステージ→重点仮説タイプ表（`CLAUDE.md:164-172`）＝ `ontology.yaml:144-149` の `stage-focus` の重複
  - ステータス遷移（`CLAUDE.md:135`）＝ `ontology.yaml:152-156` の `statuses` の重複
  - 確信度表・架空上限8（`CLAUDE.md:124-142`）＝ `ontology.yaml:159-162` の `confidence` の重複
  - 証拠の階梯（`CLAUDE.md:137-143`）＝ `ontology.yaml:165` の `evidence-ladder` の重複
  - ステージ正式名称（`CLAUDE.md:161-162`）＝ `ontology.yaml:134-141` の `stages` の重複

  そして plan/ingest/chabudai/prototype は「**CLAUDE.md の**表」を読む（`plan:16`「CLAUDE.md の…で解決」、
  `ingest:27`「CLAUDE.md の確信度目安表」、`chabudai:24`「CLAUDE.md のステージ→重点タイプ表」、
  `prototype:21,33`）。**skills → CLAUDE.md →（ontology.yaml と別実体）** という、正本を迂回する参照連鎖が
  できている。`ontology.yaml` を直しても CLAUDE.md の表が古いままだとスキルは古い方を読む。
- **改善案**:
  1. `CLAUDE.md:122-176` の重複表を削り、生成物 `ontology.md` へのリンクに置換する（正式名称・重点タイプ・
     ステータス・確信度上限は「[ontology.md](ontology.md) 参照」に一本化）。確信度の「目安」表や証拠の階梯の
     運用ルール（interest≠intent 等、機械化しにくい規律）は CLAUDE.md に残してよいが、**enum・数値・列挙は
     ontology を正本にする**。
  2. plan/ingest/chabudai/prototype の参照先を CLAUDE.md の表から `ontology.md` に付け替える。
- **根拠**: `CLAUDE.md:30` の自己宣言と `CLAUDE.md:122-176` の実態の矛盾。スキル参照連鎖は上記行番号。

### OI-A2: 証拠タグ語彙が hwlint と ontology でドリフト

- **対象**: `ontology.yaml`、`tools/hwlint.py`、`tools/ontology.py`
- **状態**: 対応済み（2026-07-21・上表のコミット参照）
- **課題**: `hwlint.py:376` が証拠タグ語彙をハードコードしている:
  ```
  EVIDENCE_TAGS = ("〈発言〉", "〈自認〉", "〈実コスト〉", "〈行動〉", "〈支払い〉", "〈二次〉", "〈架空〉")
  ```
  これは `ontology.yaml:165` の `evidence-ladder: [発言, 自認, 実コスト, 行動, 支払い]` と別物で、
  (a) `〈二次〉〈架空〉` が余分、(b) 序列（弱→強）情報を捨てている、(c) 括弧の有無が違う。
  `ontology.py:92` は `EVIDENCE_LADDER` を export しているのに **どのツールも import していない**（デッドコード）。
  実運用では両プロジェクトが `〈二次〉〈架空〉` を使っており（self は履歴に〈架空〉、aire は全行〈二次〉）、
  SSoT に無いタグが現場で流通している。
- **改善案**:
  1. `ontology.yaml` の evidence-ladder を「階梯5段（序列あり）＋補助タグ（〈二次〉〈架空〉。序列外）」の構造に
     拡張し、`〈二次〉〈架空〉` を正式に取り込む。
  2. `hwlint.py:376` の `EVIDENCE_TAGS` を廃し、`ontology.py` の `EVIDENCE_LADDER`（＋補助タグ）から生成する。
  3. 序列情報を OI-B2 の確信度整合チェックに使う。
- **根拠**: `hwlint.py:376`、`ontology.yaml:165`、`ontology.py:92`、`self/wiki/log.md` 末尾の
  「残 evidence-tag 15件は別debtとして据え置き」記述。

### OI-A3: 架空マーカー語彙がオントロジー外

- **対象**: `ontology.yaml`、`tools/hwlint.py`
- **状態**: 対応済み（2026-07-21・上表のコミット参照）
- **課題**: `hwlint.py:356` の `FICTIONAL_MARKERS = ("架空", "シミュレーション")` は `ontology.yaml` に無く
  hwlint 側定義。fictional-cap=8 は `ontology.yaml:162` にあるのにマーカー語彙だけコード側という非対称。
  gen_views は hwlint から import（`gen_views.py:24`）しており密結合。
- **改善案**: `FICTIONAL_MARKERS` を `ontology.yaml` の confidence 節（fictional-cap の隣）へ移し、
  `ontology.py` 経由で読ませる。
- **根拠**: `hwlint.py:356`、`ontology.yaml:159-162`、`gen_views.py:24`。

### OI-A4: `ontology.py` のデッドコード整理

- **対象**: `tools/ontology.py`、`tools/gen_ontology_doc.py`
- **状態**: 対応済み（2026-07-21・上表のコミット参照）
- **課題**: `STAGE_ORDER`(:80)／`STAGE_NAMES`(:81)／`EVIDENCE_LADDER`(:92)／`RELATIONS_BY_FIELD`(:96) は
  export されるが未消費。さらに `gen_ontology_doc.py` は `ontology.py` の射影定数を使わず生 YAML を直読み
  （`sm["stages"]["names"]` 等）しており、「ontology.py を唯一の入口とする」建付けと矛盾する第2アクセス経路。
- **改善案**:
  1. `STAGE_ORDER`/`STAGE_NAMES` は OI-D2（時系列・現在地ビュー）で消費させる。`EVIDENCE_LADDER` は OI-A2/B2 で
     消費させる。使い道が無いものは削る。
  2. `gen_ontology_doc.py` を `ontology.py` の定数経由に統一し、生 YAML 直読みを排除する。
- **根拠**: `ontology.py:80,81,92,96`、`gen_ontology_doc.py:66,78`。

---

## B. lint の検証強化

オントロジーがあるからこそ機械化できる不整合の穴。現状 `tools/hwlint.py` の12チェック
（`CHECKS`: `hwlint.py:390-393`）はカバーしていない。

### OI-B1: status ↔ confidence の矛盾検出

- **対象**: `tools/hwlint.py`
- **状態**: 対応済み（2026-07-21・上表のコミット参照）
- **課題**: `check_vocabulary`(`hwlint.py:135`) は status と confidence を**各々独立に**しか見ない。
  「`status: 反証` なのに confidence が高い」「`検証済み` なのに confidence が低い」「`未検証` なのに
  初期値を超える」といった 2軸間の矛盾を拾えない。
- **改善案**: status↔confidence の許容域を定義（例: 反証→低位、検証済み→7以上目安）し、逸脱を warning に。
  許容域の閾値は `ontology.yaml` の confidence 節に持たせる（マジックナンバーをコードに散らさない）。
- **根拠**: `hwlint.py:135`。

### OI-B2: 証拠の階梯 × 確信度の整合

- **対象**: `tools/hwlint.py`、`tools/ontology.py`
- **状態**: 対応済み（2026-07-21・上表のコミット参照）
- **課題**: `check_evidence_tags`(`hwlint.py:379`) はタグの**存在**しか見ない。`EVIDENCE_LADDER` の序列を
  使っていないため、確信度7-8を `〈発言〉`（最弱）だけで支えていても検出できない。CLAUDE.md の規約
  （「5-6 には〈自認〉以上、7-8 には〈実コスト〉か〈行動〉以上」）が機械化されていない。
- **改善案**: `EVIDENCE_LADDER` の順位を使い「確信度域ごとに要求される最低証拠強度」を検証（warning）。
  OI-A2（語彙一本化）が前提。
- **根拠**: `hwlint.py:379`、`CLAUDE.md` 証拠の階梯節、`ontology.yaml:165`。

### OI-B3: DEC の `based-on` 欠落検出

- **対象**: `tools/hwlint.py`
- **状態**: 対応済み（2026-07-21・上表のコミット参照）
- **課題**: `check_frontmatter_refs`(`hwlint.py:202`) は based-on が空だと `continue`（`hwlint.py:216-217`）で
  素通りする。based-on 無しの DEC（根拠なき意思決定）や、pivot/rollback が何も参照しない状態を許す。
- **改善案**: DEC に based-on が最低1件あることを warning（type によっては error）で要求する。
- **根拠**: `hwlint.py:202,216-217`、実データ ai-reskilling は DEC 0件だが self の DEC は充足。

### OI-B4: fictional-cap の中間行取りこぼし

- **対象**: `tools/hwlint.py`
- **状態**: 対応済み（2026-07-21・上表のコミット参照）
- **課題**: `check_fictional_cap`(`hwlint.py:359`) は履歴の **最終行**（`rows[-1]`）の根拠しか見ない。
  確信度を8超へ押し上げた架空ACTが中間行にあり最終行が別根拠だと素通りする。また `〈架空〉` タグと
  fictional-cap 判定が連動していない。
- **改善案**: 履歴全行を走査し、確信度が8を超えた時点の根拠に架空マーカー/〈架空〉タグがあれば error。
- **根拠**: `hwlint.py:359-368`。

### OI-B5: `leads-to`/`derived-from` の循環・自己参照検出（任意）

- **対象**: `tools/hwlint.py`
- **状態**: 対応済み（2026-07-21・上表のコミット参照）
- **課題**: H→H の関係にサイクル・自己参照が入っても検出しない。
- **改善案**: 関係グラフの閉路検出を追加（warning）。優先度は低め。
- **根拠**: `check_frontmatter_refs` は個別辺の型のみ検証。グラフ全体の健全性は未検査。

---

## C. 関係の張り忘れをスキル手順で塞ぐ

実データが実害を裏付けている（`addresses` 1/13、`derived-from` 5/13、aire 系譜全滅）。

### OI-C1: `derived-from` の frontmatter 記入手順が全スキルに無い

- **対象**: `.claude/skills/{formulate,decide}/SKILL.md`
- **状態**: 対応済み（2026-07-21・上表のコミット参照）
- **課題**: `formulate/SKILL.md:24` は「派生元があれば**本文の系譜**に `[[H-NNN]]`」としか言わず、frontmatter
  `derived-from`（cardinality:one・must-wikilink:true）への記入を指示しない。派生が最も起きる
  **pivot/rollback を扱う `decide/SKILL.md` は derived-from に一切言及しない**。ピボットで新仮説を派生させても
  系譜フィールドが繋がらない。
- **改善案**:
  1. `formulate` の手順に「派生元があれば frontmatter `derived-from` と本文 wikilink の両方を書く」を明記。
  2. `decide` に「pivot/rollback で新仮説を起票する場合、その仮説の `derived-from` に巻き戻し元を張る」を追加。
- **根拠**: `formulate/SKILL.md:24`、`decide/SKILL.md` に derived-from 記述なし、実データ
  ai-reskilling H-001/002/003 全て derived-from 空。

### OI-C2: `leads-to` が desk-research と ingest創発仮説で抜ける

- **対象**: `.claude/skills/{desk-research,ingest}/SKILL.md`
- **状態**: 対応済み（2026-07-21・上表のコミット参照）
- **課題**: leads-to を書く手順があるのは `formulate:24` だけ。`desk-research/SKILL.md:36-42` は行動/課題仮説を
  複数起票するのに leads-to（状況→課題のバリューチェーン矢印）に触れない。`ingest/SKILL.md:25` の
  「取り込み中に創発した仮説の起票」も同様。結果、list の mermaid バリューチェーン矢印が desk-research
  起票分で欠落する。
- **改善案**: desk-research と ingest の仮説起票手順に「状況→課題→…の因果が見えたら `leads-to` を張る」を追加。
- **根拠**: `desk-research/SKILL.md:36-42`、`ingest/SKILL.md:25`、実データ self H-005/007/010 の leads-to 空。

### OI-C3: `addresses` の候補自動提案

- **対象**: `.claude/skills/{formulate,plan}/SKILL.md`
- **状態**: 対応済み（2026-07-21・上表のコミット参照）
- **課題**: `ontology.yaml:96-107` は addresses に domain-subtypes=[ソリューション/買ってもらえる]・
  range-subtypes=[課題仮説] を宣言済み。型があるので機械的に候補列挙できるのに、`formulate:24` は
  「addresses に対応課題を列挙する」と言うだけで自動提案しない。結果 addresses は13仮説中1本の死蔵状態
  （relations ビューのフィット表が恒久的に空白）。
- **改善案**: ソリューション/買ってもらえる仮説を作る/計画するとき、既存の課題仮説を一覧提示して
  `addresses` の対応先を選ばせる手順を formulate/plan に追加。
- **根拠**: `ontology.yaml:96-107`、`formulate/SKILL.md:24`、実データ addresses 充足 1/2（SELF-H-009のみ、
  SELF-H-010 空）。

### OI-C4: `based-on` の frontmatter 記入を decide が明示していない

- **対象**: `.claude/skills/decide/SKILL.md`
- **状態**: 対応済み（2026-07-21・上表のコミット参照）
- **課題**: `decide/SKILL.md:22` は「本文に根拠 `[[ACT-NNN]]`」としか書かず、frontmatter `based-on`
  （must-wikilink:true）の配列記入を指示しない。テンプレート `templates/decision.md` は持つが、スキル手順が
  本文側しか指さないため二重表現の frontmatter 側が抜けやすい。
- **改善案**: decide の手順に frontmatter `based-on` 配列記入を明記。
- **根拠**: `decide/SKILL.md:22`、`templates/decision.md`。

---

## D. ビュー・自動抽出の高度化

### OI-D1: 自分たち仮説（team role）がビューから構造的に欠落

- **対象**: `tools/ontology.py`、`tools/gen_views.py`
- **状態**: 対応済み（2026-07-21・上表のコミット参照）
- **課題**: `ontology.yaml:40-43` は `role: team` を宣言するが、`ontology.py` の `_h_role` 呼び出しは
  customer/problem/solution/market の4つだけ（`ontology.py:67-70`）で `TEAM_TYPES` に相当する定数が無い。
  結果、board の「対象仮説」分類（`gen_views.py:208-210` は CUSTOMER/PROBLEM/SOLUTION の3バケツ）から
  自分たち仮説が落ちる（list には LIST_GROUPS 経由で出るので、role を使う経路だけ欠落）。
- **改善案**: `ontology.py` に `TEAM_TYPES = _h_role("team")` を追加し、board の分類に team バケツを足す。
- **根拠**: `ontology.yaml:40-43`、`ontology.py:67-70`、`gen_views.py:208-210`。

### OI-D2: 時系列ビュー ／ 現在地の充実

- **対象**: `tools/gen_views.py`、`tools/ontology.py`
- **状態**: 対応済み（2026-07-21・上表のコミット参照）
- **課題**: 確信度履歴（`Project.history`、日付付き）・log.md・DEC の date が揃っているのに、確信度の時間推移や
  検証イベントのタイムラインを出すビューが無い。board の「現在地」(`gen_views.py:222`) は `stage` の生記号
  （例 "CPF"）のみで、`STAGE_NAMES`/`STAGE_ORDER`（未使用定数）を使えば正式名称と CPF→…→PMF の進捗位置を
  出せる。
- **改善案**:
  1. board の現在地に `STAGE_NAMES` の正式名称と進捗位置（●○表現等）を追加。
  2. 確信度推移／ステージ遷移（DEC の stage-transition）のタイムラインビューを新設。
- **根拠**: `gen_views.py:222`、`ontology.py:80-81`（未使用）。

### OI-D3: ai-reskilling の `relations.md` が薄い ／ DEC節欠落

- **対象**: `tools/gen_views.py`
- **状態**: 対応済み（2026-07-21・上表のコミット参照）
- **課題**: `ai-reskilling/wiki/views/relations.md` は5関係のうち leads-to(2辺) と hypotheses しか出ず、
  based-on/derived-from/addresses の節がまるごと欠落。DEC 0件が原因だが、空でも節の見出しと
  「該当なし」を出さないと「そもそもその関係が存在する」ことが読者に伝わらない。board の「判断(DEC)」列も
  是正ACT（AIRE-ACT-004 は outcome:是正）にDEC未接続で全行「—」。
- **改善案**: 関係が0件でも節見出し＋「該当なし」を出す。是正/反証ACTに対応DECが無い場合の警告的表示を検討。
- **根拠**: `ai-reskilling/wiki/views/relations.md`、`ai-reskilling/wiki/views/board.md`。

### OI-D4: 「次に検証すべき仮説」の高度化

- **対象**: `tools/gen_views.py`
- **状態**: 対応済み（2026-07-21・上表のコミット参照）
- **課題**: `next_to_verify`(`gen_views.py:57`) は importance>=8 × 低確信度 × 未検証/検証中 の2軸のみ。
  未カバー課題（addresses、relations で算出済み）や関係グラフ上の依存度（崩れると波及が大きい「背骨」）を
  優先度に織り込んでいない。閾値 8/4 も `ontology.yaml` に無くコード側の暗黙値（`gen_views.py:48,60` 等に散在）。
- **改善案**:
  1. 未カバー課題・下流依存度を優先度シグナルに追加。
  2. 重点=8/その他=4 の閾値を `ontology.yaml` の stage-focus 節に明示して一元化。
- **根拠**: `gen_views.py:48,57,60`、`ontology.yaml:143-149`。

---

## E. オントロジーの表現力拡張（要設計合意）

実データのプローズには存在するのに、現5関係（derived-from/leads-to/addresses/hypotheses/based-on）では
表せない構造。新関係・新属性の導入は SSoT の設計変更なので、人間の合意を要する。

### OI-E1: 仮説クラスタ（グルーピング）

- **状態**: 未対応（要設計）
- **課題**: 「核心クラスタ」（SELF-H-004/002/006/008/001）が index.md・board.md・stage.md・ACT-003/005 で
  繰り返し第一級概念として扱われるのに、表現手段が単一Hの `core: true` しか無い。aire も「認知的降伏＝
  単一物語の子」（AIRE-ACT-004）というグルーピングが表現不可。
- **改善案（案）**: `cluster` 属性（名前付きグループ）か、H→H の `sibling`/`part-of` 関係を検討。
- **根拠**: `SELF-DEC-002.md` 本文の核心クラスタ列挙、`AIRE-ACT-004`。

### OI-E2: ACT→H の支持/反証の極性

- **状態**: 未対応（要設計）
- **課題**: `hypotheses`(ACT→H) は無極性。支持/反証は ACT の `outcome`（活動単位・1個）にしか無く、
  **1活動が複数仮説を別結果で検証する**場合を仮説単位で表せない（SELF-ACT-004 は H-009 反証・H-010 反証、
  SELF-ACT-002 は H-004 支持）。
- **改善案（案）**: hypotheses 関係に per-link の極性（支持/反証/判断保留）を持たせる、または
  supports/refutes の2関係に分ける。
- **根拠**: `SELF-ACT-004.md`、`SELF-ACT-002.md`。

### OI-E3: DEC→H 直接参照

- **状態**: 未対応（要設計）
- **課題**: 決定がどの仮説を動かしたかが型で表せない（based-on は DEC→ACT のみ）。`SELF-DEC-002.md` は本文で
  全8仮説の確信度スナップショットと巻き戻し対象の核心クラスタを列挙するが、frontmatter は
  based-on:[SELF-ACT-005] のみ。
- **改善案（案）**: DEC→H の `affects`/`revisits` 関係を検討。
- **根拠**: `SELF-DEC-002.md`。

### OI-E4: DEC→DEC（取り消し/後継）・対抗仮説・反証の連鎖

- **状態**: 未対応（要設計）
- **課題**:
  - DEC→DEC: `SELF-DEC-002` が `SELF-DEC-001` を reverse/supersede する関係が frontmatter に無い。
  - 対抗仮説: `AIRE-ACT-004` の「対抗仮説の種」3件が既存Hの対抗として記録されるが、型が無くプローズ止まり。
  - 反証の連鎖: SELF-H-009(反証)→leads-to→SELF-H-010(反証) の反証伝播が leads-to（因果の型）では表せない。
- **改善案（案）**: DEC→DEC の `supersedes`、H→H の `counters`（対抗）を検討。反証伝播は極性(OI-E2)＋
  leads-to の合成でビュー側に表現する手もある。
- **根拠**: `SELF-DEC-002.md`、`AIRE-ACT-004`、SELF-H-009/010。

---

## F. トポロジー駆動の探索域ギャップ検出（調査由来）

**出所**: infranodus/nashsu 系の「ネットワークトポロジーを計算して、孤立ノード・ブリッジ・
構造的知識ギャップを算出し、能動的に探索域を提案する」パターン。

**現状の穴**: このrepoは型付きリンク（5関係）を持ち `relations` ビューで可視化までするが、
**グラフ構造そのものを健全性・優先度の判定に使っていない**。`next_to_verify`(`gen_views.py:59`) は
importance × confidence × status の2軸のみで、関係グラフ上の位置（入次数0＝未検証・課題↔解決の断絶・
下流依存度）を見ていない。B（lint強化）が「個別の辺の型」を検証するのに対し、F は「グラフ全体の欠落・
歪み」を検出する層。実データの弱点（`addresses` 1/13、`derived-from` 5/13、aire 系譜全滅）は
まさにこのトポロジー的空隙であり、検出対象そのもの。C は「張り忘れをスキル手順で予防」、F は
「張られていない構造を機械が事後検出して探索域として提示」で相補的。

### OI-F1: 検証されていない重要仮説（入次数0）の検出

- **対象**: `tools/hwlint.py`（検出）、`tools/gen_views.py`（探索域への射影）
- **状態**: 対応済み（2026-07-21）
- **課題**: 「重要 × 証拠なし」象限は現状 status（未検証/検証中）で近似しているが、`hypotheses`(ACT→H) の
  **入次数0**（＝どの活動もこの仮説を検証対象にしていない）という構造事実で厳密化できる。status:検証中でも
  実は紐づく ACT が1本も無い、という食い違いも拾える。
- **改善案**: importance=focus かつ `hypotheses` 入次数0 のHを「未着手の重点仮説」として warning／
  `next_to_verify` の最優先シグナルに加える。
- **実装**:
  1. `hwlint.py` に `check_untested_focus` を追加（`CHECKS` に登録）。重点＝現ステージの重点タイプ
     （`STAGE_FOCUS`）か手動 `importance>=IMPORTANCE_FOCUS`。入次数0で status が検証中/検証済みなら
     「二重表現の破れ」、未検証なら「未着手」として warning。stage は `Project.stage`（stage.md）で解決。
  2. `gen_views.py` の `next_to_verify` を入次数込み `(stem, fm, indeg)` に拡張し、入次数0を最優先に
     ソート。board/list の「次に検証すべき仮説」で入次数0に `⚠️未着手` マーカー＋凡例を出す。
  3. `tests/test_hwlint.py` に `UntestedFocusTest`（5ケース）を追加。テスト 64→69 件・全パス。
  4. 現データは全重点仮説が入次数≥2 のため lint 新規警告ゼロ・ビュー**バイト不変**（潜在ガードとして機能）。
- **根拠**: `gen_views.py:59`、`ontology.yaml:109-118`（hypotheses 関係）、実データ leads-to/addresses の空欄群。

### OI-F2: 課題↔解決の構造ギャップ（未対応課題・課題なき解決）

- **対象**: `tools/hwlint.py`、`tools/gen_views.py`
- **状態**: 対応済み（2026-07-21）
- **課題**: `addresses`（ソリューション仮説→課題仮説）は型として宣言済み（`ontology.yaml:96-107`）だが、
  グラフとして見ると2種のギャップが算出できるのに誰も出していない:
  - **未対応の課題**: 確信度の高い課題仮説を `addresses` するソリューション仮説が1本も無い＝未開拓の機会
    （ブリッジを張るべき箇所）。
  - **課題なき解決**: `addresses` 先を持たないソリューション仮説＝solution in search of problem（PSFの危険信号）。
- **改善案**: 上記2ギャップを lint warning ＋ `relations` ビューの「フィット表」に空セルとして明示する
  （OI-D3 の「0件でも節を出す」と同じ思想）。`/chabudai`（探索域の発見）が読む素材にもなる。
- **実装**:
  1. `hwlint.py` に `check_addresses_gaps` を追加。関係定義は `RELATIONS_BY_FIELD["addresses"]` から
     domain/range サブタイプを引く（語彙を再定義しない）。
     - **課題なき解決**: addresses を持てる型（ソリューション仮説）で addresses が空・非反証 → warning。
     - **未対応の課題**: 検証済み課題仮説を非反証ソリューションが1本も addresses していない → warning。
       ただし**解決設計フェーズのみ**（`STAGE_FOCUS` にソリューション仮説が重点として現れる最早ステージ=
       PSF 以降を `STAGE_ORDER` で判定）。CPF/FPF では課題に解決が無いのは正常なので拾わない。
  2. `gen_views.py` の `relations` フィット表に「**課題なき解決**（addresses 先が無いソリューション仮説）」行を
     追加（既存の「未カバーの課題」＝逆側と対になる）。
  3. `tests/test_hwlint.py` に `AddressesGapTest`（5ケース）追加。テスト 69→74 件・全パス。
  4. 現データは lint 新規警告ゼロ（self のソリューション仮説は2本とも反証で対象外、両案件とも CPF で
     未対応課題の判定フェーズ外）。ビュー差分は self `relations.md` の「課題なき解決: なし」1行のみ（意図した差分）。
- **根拠**: `ontology.yaml:96-107`、実データ addresses 1/13、`relations` ビューのフィット表が恒常的に空白。

### OI-F3: 孤立ノード・ブリッジ・下流依存度の算出

- **対象**: `tools/gen_views.py`
- **状態**: 未対応（要設計）
- **課題**: 系譜（derived-from/leads-to）と検証（hypotheses）を合成した仮説グラフ上で、(a) どの関係も
  持たない**孤立仮説**、(b) 系譜クラスタ間をつなぐ**ブリッジ仮説**、(c) `leads-to` の下流被参照数＝
  「崩れると波及が大きい背骨」（OI-D4 が未カバーと明記した依存度シグナル）を機械算出できる。
- **改善案（案）**: これらをトポロジー指標として `relations` ビュー末尾に要約表で出す。優先度は F1/F2 より低い
  （表現力より運用実感が先）。
- **根拠**: `gen_views.py`（`relation_edges`:446 は辺を持つが次数・中心性を算出していない）、OI-D4。

---

## G. 時間軸 ／ 確信度の陳腐化（調査由来）

**出所**: LLM Wiki v2 の「各主張に確証度＋タイムスタンプを持たせ、裏付けの無い主張は時間経過で減衰、
対立ソース搬入時は消さず Supersession でアーカイブ」パターン。

**現状の穴**: 確信度履歴テーブルは日付を持つ（`parse_history`:70 → `Project.history`）のに、
**時間軸を lint もビューも見ていない**。半年前に確信度8で「検証済み」にした仮説と昨日のそれが同格に扱われ、
再検証が促されない。市場・前提が動く仮説検証ドメインでは、これは無視できない盲点。CLAUDE.md が
`/lint`（LLM）に委ねる「長期放置」検出を、機械側に降ろす余地がある。

### OI-G1: 検証済み高確信度の staleness 検出

- **対象**: `tools/hwlint.py`、`ontology.yaml`
- **状態**: 未対応（要設計・閾値合意）
- **課題**: `status:検証済み` かつ高確信度のHで、確信度履歴の**最終行の日付が古い**ものを「陳腐化の疑い＝
  再検証を検討」として出せるのに出していない。
- **改善案（案）**:
  1. `ontology.yaml` の confidence 節に `staleness-days`（例: 180）を追加（マジックナンバーをコードに置かない）。
  2. hwlint に基準日（`--today` 引数 or `datetime.date.today()`）を渡し、最終履歴日付が閾値超のHを warning。
  3. **数値は自動で下げない**（不変ルール1「証拠なしに確信度を動かさない」を厳守）。あくまで再検証を促す
     可視化のみ。減衰させたい場合は必ず ACT/DEC（例: self-reflection や再検証）に紐づけて人が動かす。
- **根拠**: `hwlint.py:70`（履歴日付は取得済み・未活用）、CLAUDE.md「長期放置は /lint（LLM）が担う」記述、
  不変ルール1。

### OI-G2: Supersession（旧主張のアーカイブ）の型表現

- **対象**: `ontology.yaml`（要設計）
- **状態**: 未対応（要設計・E と統合検討）
- **課題**: 調査の Supersession（旧版を消さず「継承・上書き」エッジでアーカイブ）は、このrepoでは
  `derived-from`（系譜）＋履歴テーブルで部分的に実現済み。ただし「この仮説はこの新仮説に置き換えられ古い(Stale)」
  という明示状態は無い。これは OI-E4（DEC→DEC supersedes、反証の連鎖）と同じ設計空間。
- **改善案（案）**: 独立の新関係は増やさず、OI-E4 の検討に「H の stale/superseded 状態」を合流させる。
  G は G1（低リスク・可視化のみ）を先行させ、G2 は E とまとめて設計する。
- **根拠**: `ontology.yaml` relations（現5関係）、OI-E4。

---

## H. あえて採らない（調査パターンのうち現規模で過剰なもの）

将来の再検討時に「検討済みで見送った」と分かるよう、却下判断も記録する。

- **ベクトル検索／ハイブリッド検索（LanceDB・BM25・埋め込み・2ホップ拡張）** — 1プロジェクト十数〜数十
  レコードの規模では、Claude が `wiki/` を直接読む現方式より精度・保守性ともに劣化する。導入コスト過大。
- **確証度付き BFS 検索ツール（MAX_DEPTH/MIN_CONFIDENCE/MAX_NODES）** — 同上。この規模でグラフ探索の
  ランタイムを持つ必要が無い。関係の可視化は `relations` ビューで足りる。
- **デスクトップ GUI（Tauri/React/Rust）** — 可視化要件は Obsidian＋Dataview＋mermaid ビューで充足。
- **多シグナル関連度モデル＋コミュニティ検出（Louvain・Adamic-Adar の類似度行列）** — 規模的に過剰。
  「共有 sources を持つのに無関係なH対」を提示する軽量版なら OI-C3（addresses 候補提案）の延長で足り、
  行列計算・クラスタリングは不要。E1（クラスタ）は人手のグルーピングで扱う。

> 注: 調査の出典は Karpathy gist に集約されており、個別リポジトリ名・数式（4シグナルの重み等）は
> 裏取りが弱い。F・G は具体実装ではなく**設計パターン**として採用している。

---

## 着手順の目安

1. **A（SSoT一本化）** — 低リスク・ドリフトの元を断つ。他の前提になる（A-2 は B-2 の前提）。
2. **C（関係の張り忘れ）** — スキル文言の追記中心で、実データの実害が明確。
3. **B（lint強化）** — A-2 完了後に B-2 を含めて機械検証を厚くする。
4. **D（ビュー高度化）** — D-1(team欠落) は小さく効く。D-2/D-4 は設計含む。
5. **F（トポロジー・ギャップ検出）** — 調査由来。F1/F2 は lint＋ビュー追加で低リスク・実データの弱点に直撃。
   B（lint強化）と同層なので B の運用実感を踏まえて着手する。閾値（focus 判定・ギャップの定義）の合意が前提。
6. **G1（staleness 可視化）** — 調査由来。`staleness-days` 閾値の合意だけで着手でき、低リスク（可視化のみ・
   数値は動かさない）。G2 は E4 と統合して設計。
7. **E（表現力拡張）** — 設計合意を要するため、A〜D の運用実感を踏まえて別途議論する（G2 を合流）。

> F・G の推奨着手は **F1（未検証の重点仮説＝入次数0）→ F2（課題↔解決ギャップ）→ G1（staleness）** の順。
> いずれも hwlint への warning チェック追加＋`ontology.yaml` への閾値追加＋既存テスト様式（tests/）への
> ケース追加で収まり、A〜D と同じ規律で実装できる。
