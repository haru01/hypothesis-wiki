# アーキテクチャ改善バックログ

アーキテクチャ分析（2026-07-22）で見つかった、**ツール実装の堅牢性・コード保守性・残存ドリフト**の
改善余地を記録する。既存の `docs/ontology-improvements.md`（OI＝オントロジーを効かせる）・
`docs/skill-improvements.md`（SI＝スキルの運用）とは軸が異なり、本ファイル（AR＝Architecture／
接頭辞 `AR-NNN`）は主に `tools/` の解析層の脆さ・重複・テスト空白と、規約の二重管理に起因する
ドリフトを扱う。各項目は「対象／状態／課題／改善案／根拠」で書く。状態は `未対応` `対応中` `対応済み`。

## 現状評価（サマリ）

設計思想（`ontology.yaml` を SSoT に、規約をフックと決定論 lint で機械強制、生成物は純射影）は
**際立って良く出来ている**。SSoT のドリフトをテスト（`OntologyDerivationTest`）で `assertIs` まで
検証している点、sources/ 不変性をライブ（PreToolUse）とコミット時（pre-commit）で二重防御する点は模範的。

一方、リスクは3層に集約される:

1. **残存ドリフト** — 「一覧を1箇所に集約する」思想が徹底されず、`projects/current.md` のスキル一覧が
   既に古い（chabudai 欠落）。休眠機能（vp ビュー・addresses）の残骸がスキルとオントロジーの不整合を生む。
2. **解析層の構造的脆さ** — frontmatter/テストカードを手書きパーサ・部分一致で解析しており、
   この1層が lint・全ビュー・フックを支えている。誤検出・取りこぼしの余地がある。
3. **保守性** — レコードモデルが linter に同居し、view 生成が linter に密結合。同一ロジックが複数箇所に
   重複。最も複雑な view 生成層のテストが最も薄い。

**P1（即修正・低リスク・実害明確）→ P2（構造的脆さ）→ P3（保守性）** の順に着手を推奨する。

---

## P1. 残存ドリフト（即修正・低リスク）

### AR-01: `projects/current.md` のスキル一覧が `chabudai` を欠く（実ドリフト）

- **対象**: `projects/current.md`
- **状態**: 対応済み（2026-07-22。current.md:9 のスキル逐一列挙を `../CLAUDE.md`「ワークフロー」節への1行参照に置換し、一覧の正本を CLAUDE.md 1箇所に一本化）
- **課題**: `current.md:9` がスキルを9個列挙（`/new-project /desk-research /formulate /plan /prototype
  /ingest /view /decide /lint`）するが **`/chabudai` を欠いている**。`CLAUDE.md` のワークフロー表・
  `README.md` のクイックスタート表には chabudai が含まれる。SI-012 で共通規約は集約したが、
  スキルの**一覧自体**が current.md・CLAUDE.md・README の3箇所に重複しており、current.md が既に乖離した。
  まさに本アーキテクチャが警告する「一覧を複数箇所に持って1箇所が古くなる」ドリフトが発生済み。
- **改善案**: current.md からスキルの逐一列挙を削り、「スキル一覧は [CLAUDE.md ワークフロー節] が正典」への
  1行参照に置換する（一覧の正本を1箇所に一本化）。current.md はプロジェクト解決に必要な
  `current-project` とプロジェクト一覧表だけを持つ。
- **根拠**: `projects/current.md:9`（9個）、`CLAUDE.md` ワークフロー表（chabudai あり）、
  `README.md` クイックスタート表。SI-012 の「規約はN箇所に散らすとドリフトする」と同じ構図。

### AR-02: `/formulate` の addresses 記述と ontology（must-wikilink:false）・休眠 vp ビューの不整合

- **対象**: `.claude/skills/formulate/SKILL.md`、`ontology.yaml`、`tools/gen_views.py`（`gen_vp`）
- **状態**: 対応済み（2026-07-22。全整合で対応。formulate:24 の不要な本文 wikilink 要求を削除し、`addresses` の表記を template:12・CLAUDE.md:79・CLAUDE.md:35・ontology.yaml:104 コメントで「relations のフィット表（frontmatter から射影）」に統一。フィット表は休眠でなく登録済み relations ビューがライブ生成しているという実態に合わせた。vp ビュー自体の復活は見送り＝案1採用。挙動変更なし）
- **課題**: `addresses` 関係は `ontology.yaml:104` で `must-wikilink: false`（「現在フィット表は休眠」と注記）、
  それを描画する `vp` ビュー（`gen_vp`、`gen_views.py:364`）も `VIEWS`(:556) に未登録の死んだ経路。
  にもかかわらず `formulate/SKILL.md:24` は今も「ソリューション仮説なら addresses に対応課題を列挙し、
  **本文にも `[[H-NNN]]` を併記する**」と指示している。ユーザーは、オントロジーが要求せず・どのビューも
  描画しない本文 wikilink を張らされる。formulate ↔ ontology ↔ view の三者で addresses の要否が食い違う。
- **改善案**: 次のどちらかに寄せて三者を整合させる。
  1. **休眠を正とする**: formulate の「本文 wikilink 併記」指示を「frontmatter `addresses` のみ（本文併記は不要）」に
     直す。addresses は relations ビューのフィット表（`gen_relations`）で既に活用されているので、
     frontmatter 記入は残す。
  2. **vp を復活させる**: `gen_vp` を `VIEWS` に再登録し、`addresses` を `must-wikilink: true` に戻す。
     この場合は formulate の現記述が正となる。
  現状フィット表は `relations` ビュー（休眠でない）で足りているため **案1（低コスト）を推奨**。
- **根拠**: `ontology.yaml:96-107`（`must-wikilink: false`＋「フィット表は休眠」注記）、
  `gen_views.py:358-364`（vp 休眠）、`formulate/SKILL.md:24`。OI-C3（addresses 候補提案・対応済み）の残課題。

> **既存バックログで追跡済み（本分析でも再確認。ここでは重複記録しない）**
> - **`templates/demo-script.md` 未整備** → `SI-019`（＝`SI-002` 改善案3の積み残し・未対応）。
>   `/plan` の demo 系テストカードに台本雛形が無い件。
> - **アクティブプロジェクトの切り替えスキルが無い** → `SI-017`（未対応）。current.md 手編集頼み。

---

## P2. 解析層の構造的脆さ

### AR-03: 手書き frontmatter パーサが systemic な脆弱性

- **対象**: `tools/hwlint.py`（`parse_frontmatter`）
- **状態**: 対応済み（2026-07-22。`yaml.load(..., Loader=yaml.BaseLoader)` に置換。BaseLoader で型強制（int/bool/date 化・Norway 問題）を避け、None→""・list→"[a, b]" の正規化で従来の文字列契約を完全維持。引用符内コロン・複数行・コメントを正しく処理。実データで hwlint --all バイト一致・既存74テスト不変、`ParseFrontmatterTest` 5ケース追加）
- **課題**: `parse_frontmatter`(`hwlint.py:33`) は本物の YAML ではなく行ベースの近似（最初の `:` で split・
  末尾 `#…` を正規表現で除去）。ネスト構造・複数行値・引用符内コロン・ブロックリストは誤パースする。
  現状フラットな `key: value` / `key: [a, b]` 規約でたまたま成立しているだけ。しかも **この1つのパーサが
  lint・全ビュー（gen_views は Project 経由で同じ解析を使う）・フックすべてを支えている**単一障害点。
- **改善案**: `ontology.py` が既に依存している **PyYAML で frontmatter ブロックをパース**する
  （`yaml.safe_load` の再利用。新規依存は増えない）。移行時は既存レコードで出力差分ゼロを確認し、
  `tests/` に引用符・配列・コメント付き値の回帰ケースを追加する。優先度は高（全解析の土台）。
- **根拠**: `tools/hwlint.py:33-43`、`tools/ontology.py:14`（PyYAML 既存依存）、gen_views は
  `Project` を hwlint から import（`gen_views.py:24`）し同じ解析を共用。

### AR-04: 架空検出・log/id 照合が部分一致依存で誤検出しうる

- **対象**: `tools/hwlint.py`（`check_fictional_cap`／`check_log_sync`／`check_id_sequence`）
- **状態**: 対応済み（2026-07-22。(1) `check_fictional_cap` の根拠セル地の文マーカー検出を外し、構造化シグナル（`〈架空〉` タグ＋紐づく架空 ACT）に一本化。(2) `check_log_sync`・`check_id_sequence` の ID 照合を数字境界つき正規表現 `(?<![0-9A-Za-z])…(?![0-9])` に。`FictionalCapProseTest` 2ケース・`IdSequenceBoundaryTest` 1ケース追加）
- **課題**: 3つのチェックが素朴な文字列包含に依存する:
  - `check_fictional_cap` は本文に「架空/シミュレーション」の語があれば架空 ACT 扱い。架空データを
    **説明・注意喚起しているだけ**のレコードでも誤検出しうる。
  - `check_log_sync`/`check_id_sequence` は log.md の行に対し `stem in line`／取り下げ語の部分一致。
    `H-1` と `H-10` の混同や、無関係な行にトークンが含まれるケースで誤ヒット/取りこぼしの余地がある
    （確信度の正規表現は `(?!\d)` で守るが、ID 照合は語境界を取っていない）。
- **改善案**:
  1. 架空判定は本文の任意箇所ではなく、**確信度履歴の該当行の根拠セルの `〈架空〉` タグ**か、紐づく ACT の
     所定フィールドに限定する（`check_fictional_cap` は既に `〈架空〉` タグを見ているので、本文全体の語検出を
     外し、タグ＋紐づけ ACT に一本化）。
  2. log/id の ID 照合を語境界つき正規表現（`\b`＋接頭辞つき ID）に置き換える。
- **根拠**: `hwlint.py`（`check_fictional_cap`:393-）、（`check_log_sync`:350-）、（`check_id_sequence`:326-）。
  OI-B4（fictional-cap 中間行取りこぼし・対応済み）の隣接領域。

### AR-05: `check_wikilinks` がリポジトリ親を glob しクロスプロジェクト解決になっている

- **対象**: `tools/hwlint.py`（`check_wikilinks`）
- **状態**: 対応済み（2026-07-22。解決対象を `project.root.parent.glob("*/wiki/**/*.md")` から当該プロジェクト配下 `project.root.glob("wiki/**/*.md")` に限定。クロスプロジェクト解決を排除し共通規約1と整合。`WikilinkScopeTest` 2ケース追加。実データで新規 wikilink エラーなし）
- **課題**: `check_wikilinks`(`hwlint.py:308`) は解決可能名の集合を
  `project.root.parent.glob("*/wiki/**/*.md")`(`:311`) で作る。これは**現在プロジェクトの兄弟ディレクトリ
  （＝他プロジェクトの `wiki/`）まで走査**するため、`[[AIRE-H-001]]` のようなリンクが**別プロジェクトに
  その名前が存在すれば解決してしまう**。接頭辞で ID 衝突を防いでいる設計と裏腹に、リンク切れ検出が
  プロジェクト境界を越えて緩くなっており、ディレクトリ構造への暗黙結合でもある。lint は「現在プロジェクト
  のみ対象」という共通規約1とも食い違う。
- **改善案**: 解決可能名の集合を **当該プロジェクトの `project.root` 配下に限定**する
  （`project.root.glob("wiki/**/*.md")`）。プロジェクト横断リンクを将来サポートするなら、接頭辞で
  対象プロジェクトを特定してから解決する明示ロジックにする。
- **根拠**: `tools/hwlint.py:308-311`、`CLAUDE.md` スキル共通規約1（「lint は現在プロジェクトのみ対象」）。

---

## P3. 保守性（構造リファクタ）

### AR-06: レコードモデル層が linter に同居し、view 生成が linter に密結合

- **対象**: `tools/hwlint.py`、`tools/gen_views.py`、`tools/check_testcard_immutable.py`
- **状態**: 対応済み（2026-07-22。新規 `tools/records.py` にレコードモデル（`Project`・parse/strip 系・`entity_of`・`referenced_ids`・`importance`・`testcard` 抽出・`current_slug` 解決）を抽出。hwlint/gen_views/check_testcard_immutable/hooks が records から import し、gen_views は linter への依存を持たなくなった。`testcard` を records に一元化（gen_views と不変チェックで共有）、`next_to_verify` 描画を `next_to_verify_bullets` に共通化、プロジェクト解決を `current_slug` に一元化。挙動不変（全テストパス・ビュー内容バイト不変・hwlint 出力不変）。`RecordsModuleTest` で共有実装の同一性を assertIs 検証）
- **課題**: レコードモデル（`Project`・`parse_frontmatter`・`parse_id_array`・`parse_history` 等）が
  `hwlint.py` に置かれ、`gen_views.py:24` がそれを直接 import する。つまり **linter が事実上の
  レコードモデルライブラリ**になっており、lint のリファクタが黙って view 生成を壊しうる。加えて重複が散在:
  - `testcard()` が `gen_views.py:59` と `check_testcard_immutable.py:22` に別実装（正規表現が微妙に異なりドリフトしうる）。
  - `next_to_verify` の描画ブロックが `gen_board`(`:235-237`) と `gen_list`(`:335-337`) に重複。
  - プロジェクト解決が `resolve_slug`(`gen_views.py:563`) と `resolve_targets`(`hwlint.py:607`) で
    同じ `current-project` 正規表現を二重に持つ。
- **改善案**: 中立な第3モジュール（例 `tools/records.py`）にレコードモデル（`Project`・parse 系・
  プロジェクト解決）を抽出し、hwlint / gen_views / check_testcard_immutable がそこから import する。
  `testcard` と `next_to_verify` 描画も共有ヘルパに寄せる。既存テストの全パスと生成物のバイト不変を確認。
- **根拠**: `gen_views.py:24`（hwlint から import）、重複＝`gen_views.py:59` vs `check_testcard_immutable.py:22`、
  `gen_views.py:235-237` vs `:335-337`、`gen_views.py:563` vs `hwlint.py:607`。

### AR-07: 最も複雑な view 生成層のテストが最も薄い

- **対象**: `tests/`、`tools/gen_views.py`、`tools/gen_ontology_doc.py`、`tools/hooks/stop_view_gen.py`
- **状態**: 対応済み（2026-07-22。`GenViewsTest` 7ケースを追加。`field_value` の二形式（見出し／箇条書き）抽出、`next_to_verify`＋`next_to_verify_bullets`（⚠️未着手マーカー・並び）、`gen_board`/`gen_list`/`gen_relations` の主要節、addresses フィット表（対応・課題なき解決）、`is_executed` のプレースホルダ判別を fixture ベースで検証。gen_ontology_doc は ontology.md 差分ゼロを検証フローで担保。残: `stop_view_gen.py` 専用テストは今後）
- **課題**: `test_hwlint.py` は lint の各チェックとフック（`stop_lint`/`guard_sources`）に肯定・否定
  両ケースを持つ一方、`gen_views.py` の出力（board/list/relations の生成、テストカード/学習カードの
  正規表現抽出、mermaid 描画）は `importance()` を除きほぼ未テスト。**脆い正規表現に依存する最も複雑な層の
  カバレッジが最も薄い**。`gen_ontology_doc.py`・`stop_view_gen.py` にも専用テストが無い。
- **改善案**: 小さな固定プロジェクト（fixture）から各ビューを生成し、既知の期待出力（またはスナップショット）と
  照合するテストを追加。テストカード dual-format 抽出（`field_value`）・`next_to_verify`・mermaid ノード生成の
  境界ケースを重点的に。AR-06（モデル抽出）後だと fixture が組みやすい。
- **根拠**: `tests/test_hwlint.py`（gen_views は `importance` のみ）、`tools/gen_views.py` の正規表現群、
  `tools/gen_ontology_doc.py`・`tools/hooks/stop_view_gen.py` に対応テスト無し。

---

## 着手順の目安

1. **AR-01（current.md ドリフト）** — 1ファイル修正。実ドリフトが既に発生済みで最優先。
2. **AR-02（formulate↔addresses 整合）** — 案1なら formulate 1行修正で三者整合。低コスト。
3. **AR-03（frontmatter を PyYAML 化）** — 全解析の土台の堅牢化。新規依存ゼロ・回帰テスト必須。
4. **AR-04 / AR-05（部分一致・クロスプロジェクト解決の是正）** — lint の誤検出/取りこぼしを塞ぐ。
   AR-03 と同層なのでまとめて着手すると効率的。
5. **AR-06（レコードモデル抽出）** — 構造リファクタ。挙動不変を担保して行う。
6. **AR-07（view 生成のテスト追加）** — AR-06 の後に fixture ベースで。以降のリファクタの安全網になる。

> 本バックログは 2026-07-22 のアーキテクチャ分析（`tools/`・`.claude/skills/`・オントロジー・規約の
> 突き合わせ）に基づく。既存で追跡済みの項目（demo-script=SI-019、切替スキル=SI-017、addresses 候補提案=
> OI-C3 済）は重複記録せず参照に留めた。
