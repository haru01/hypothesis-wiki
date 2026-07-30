# ナレッジグラフ改善バックログ（KG）

論文「**Knowledge Graph Engineering for Multi-Agentic Systems: The Anthropic Playbook**」
（2026年7月・独立編纂の学習用シンセシス。出典は Anthropic の公開 cookbook と agent patterns）に
照らしてこのリポジトリを点検した結果を記録する。接頭辞 `KG-NNN`。
既存の `docs/ontology-improvements.md`（OI＝オントロジーを効かせる）・`docs/skill-improvements.md`（SI）・
`docs/architecture-improvements.md`（AR）とは軸が異なり、本ファイルは
**「このWikiをナレッジグラフとして本番運用に載せるための規律」**を扱う。
各項目は「対象／状態／課題／改善案／根拠」で書く。状態は `未対応` `対応中` `対応済み` `却下`。

## なぜこの軸が要るのか

論文は非構造文書からグラフを組む4段パイプライン（**抽出 → 名寄せ → 組み立て → 照会**）と、
それを本番に載せる規律を提示する。核は Appendix D「Production Readiness Checklist」10項目
——「欠けていれば、いつか必ず表に出る、名前のついたリスク」の一覧——と、締めの一文である。

> the pipeline is not done when it runs; it is done when you can tell, on any given morning,
> whether what it produced overnight was actually right.

**このリポジトリは、まさにそのナレッジグラフである。** H/TEST/LEARN/DEC をノード、6つの型付きリンクをエッジとし、
`ontology.yaml` を SSoT に、`tools/hwlint.py` とフックで規約を機械強制する。論文が「Claude API で自動抽出する
グラフ」を扱うのに対しこちらは「人主体のループが手で育てるグラフ」だが、**必要な規律の一覧は同じ**だった。

## 論文チェックリスト × 充足状況（2026-07-29 点検 → 対応後）

| 論文のチェック項目 | 点検時 | 対応後 | 項目 |
|---|---|---|---|
| Gold set（評価用の正解セット） | ✗ | ✗（見送り） | KG-08 |
| Alias map（表層形→正規形の辞書） | ✗ | △（規約として制定・型は未導入） | KG-07 |
| Schema version（スキーマの版付け） | △ 宣言はあるが誰も読まない | ✓ | KG-02 |
| Extraction cap（1回の抽出量の上限） | — 人手ペースなので該当なし | — | KG-09 |
| Resolution fallback（未マッチ名の単独クラスタ化） | — 名寄せ自体が無い | — | KG-07 |
| **Provenance tracking（全エッジが出典文書を持つか）** | ✗ **構造的に壊れていた** | ✓ | KG-03 |
| Incremental update（差分追加でグラフが育つか） | ✓ 追記専用レコード＋log.md | ✓ | — |
| **Connectivity monitor（連結成分の監視）** | ✗ | ✓ | KG-05 |
| Summarization trigger（変化時のみ再生成） | ✓ mtime 比較 | ✓ | — |
| **Human sample（毎日ノードを1つ無作為に読むか）** | ✗ | ✓ | KG-06 |

チェックリストの外で、論文が繰り返す「**the loop must be run** / a pipeline with a good scorer improves itself,
a pipeline without one drifts」の観点で実データを検査したところ、**チェックリストより深刻な問題**が出た:
`hwlint --all` は error 0 で通るのに、**この repo の看板である規律のいくつかが一度も発火できない状態**だった（KG-04）。
論文の中心主張「**the schema is the contract**」に対応する層（フィールド宣言）も欠けていた（KG-01）。

---

## KG-01: フィールド宣言が無く、スキーマが契約になっていなかった

- **対象**: `ontology.yaml`、`tools/ontology.py`、`tools/hwlint.py`、`CLAUDE.md`
- **状態**: 対応済み（2026-07-29）
- **課題**: `ontology.yaml` は entity・subtype・relation・state-machine を宣言していたが
  **frontmatter フィールド自体の宣言を持たなかった**。そのため `title` `date` `importance` `core`
  `riskiest-assumption` `to-stage` は宣言が `CLAUDE.md` の散文だけで、**必須キーの欠落も未知キー（タイポ）の
  混入も機械検出できなかった**。`date` が欠けると `Project.stage`（`tools/records.py`）と
  `latest_dec_next_move`（`tools/gen_views.py`）のソートが黙って先頭に来る。
  加えて **`outcome` に SSoT が無く**（`ontology.yaml` の散文に「支持/反証/判断保留 等」とあるだけで実運用の
  `起票`・`是正` が漏れていた）、5値の一覧は `CLAUDE.md` にしかなく、`check_vocabulary` は
  status/type/stage/confidence だけを見ていたため**打ち間違いがそのまま `board.md` に流れた**。
- **改善案 / 対応**: `entities.*.fields`（`required` + `kind`）と `state-machines.outcomes` を新設。
  `check_fields`（必須欠落=error・未宣言キー=warning・date 形式=error）と `check_vocabulary` への
  `outcome` 検証を追加。`_selfcheck` に「relations の field が必ず domain 側 entity の fields に現れる」
  不変条件を追加（宣言したのに frontmatter キーとして未登録＝死んだ関係を防ぐ）。
  現データ30レコードは新規 error/warning ゼロ＝宣言が実データと完全一致した（潜在ガードとして機能）。
- **根拠**: 論文 §III.B「the schema is the contract」／§XI.C「structured outputs as the enabling capability」。

## KG-02: スキーマ版（`version`）が死蔵され、`ontology.md` のドリフトに穴があった

- **対象**: `ontology.yaml`、`tools/gen_views.py`、`tools/gen_ontology_doc.py`、`.githooks/pre-commit`
- **状態**: 対応済み（2026-07-29）
- **課題**: `ontology.yaml:version` はどのツールも読んでいなかった。また `ontology.md` の鮮度は
  `tests/test_hwlint.py` の freshness テスト経由でしか守られず、pre-commit がテストを走らせるのは
  `tools/` か `tests/` が staged のときだけなので、**`ontology.yaml` 単独編集のコミットで古い `ontology.md` が
  通る穴**があった。
- **改善案 / 対応**: 生成ビューのヘッダに `ontology-version` を刻む（どのスキーマ版で射影した生成物かを追える）。
  `gen_ontology_doc.py --check`（生成せず差分の有無を exit code で返す）を追加し、pre-commit で
  `ontology.yaml` が staged なら実行する。あわせて `entities.*.dir` のハードコード迂回路2箇所
  （`records.py`・`stop_view_gen.py`）と `entity_of` の種別ハードコードを SSoT 経由に差し替えた。
- **根拠**: 論文 §XI.E「version the schema: the graph built under the old schema and the graph built under
  the new one may not be compatible」。

## KG-03: 出典鎖が最後の一歩で切れ、架空データの蓋が実質機能していなかった

- **対象**: `ontology.yaml`（`provenance` 節）、`tools/records.py`、`tools/hwlint.py`、`tools/gen_views.py`、
  `templates/learning.md`、`CLAUDE.md`、`.claude/skills/{learning,desk-research,chabudai,lint}/SKILL.md`
- **状態**: 対応済み（2026-07-29。移行手順は [migrations/2026-07-provenance-sources.md](migrations/2026-07-provenance-sources.md)）
- **課題**: 生命線である「確信度は必ず証拠に紐づく」の紐づけが **`H の確信度履歴 → [[LEARN-NNN]]`** で止まり、
  **`LEARN → sources/<生データ>`** は本文のコードスパンで書かれていて**どのツールも検証していなかった**。帰結:
  1. **出典切れが検出されない**（生データを改名・削除しても確信度を支えた記録が無言で宙に浮く）。
  2. **架空データの蓋（`fictional-cap: 8`）の連鎖が最初の一歩で切れていた** —
     `templates/project/sources/README.md` は生データ冒頭への架空宣言を要求するのに、
     `check_fictional_cap`・`fictional_records` が見ていたのは **TEST/LEARN 本文の文字列一致**だった。
     つまり**著者が偶然 LEARN 本文にも「架空」と書き写しているときだけ蓋が働く**状態で、
     このキットが自ら最重要と掲げる規律（README「偽の確証で前に進まない」）の土台が偶然に依存していた。
  3. **取り込み忘れが検出されない** — README 冒頭が挙げる課題「記録が散逸し過去の学びが忘れられる」そのもの。
- **改善案 / 対応**: `provenance` 節（`relations` は record→record のままにし、出典は**グラフの外を指す属性**として
  別に宣言）を新設。`check_provenance_paths`(error)／`presence`／`body_link`／**`provenance_chain`**／
  `orphan_sources` の5チェックを追加。`provenance_chain` は「確信度を**上げた**履歴行が指す LEARN に出典が無い」を
  検出する（`competitive-analysis.md` 3-C3「確信度の付け方の規律を型で縛る」の機械化）。
  架空判定は `records.fictional_activities` に集約し**出典冒頭の宣言を一次情報**とした（本文マーカーは
  出典を持たない旧レコード向けフォールバック）。既存 LEARN 7件に backfill 済み。
- **検証**: チェック追加直後は self warning 15→35・aire 0→3 に増え、backfill 後 15/0 に収束。
  連鎖修理の実証として、LEARN 本文から「架空」の語を全て消しても出典冒頭の宣言から4件が架空と判定され続けた。
- **根拠**: 論文 Appendix D「Provenance tracking — Does every edge carry its source document and extraction
  timestamp? Failure if missing: Ungrounded answers; evaluator cannot fact-check」。

## KG-04: 看板の規律が実データ上で一度も発火していなかった（scorer なきループ）

- **対象**: `tools/hwlint.py`（`check_evidence_floor`・`check_relative_links`・`check_source_links`・`check_stage_doc`）
- **状態**: 対応済み（2026-07-29）
- **課題**: `hwlint --all` は error 0 で通るのに、4つの規律が構造的に発火できなかった。
  1. **証拠の階梯ルールが完全に不活性**。`check_evidence_floor` は `if not ranks: continue` で
     「階梯タグが1つも無い行」を黙って見送っていた＝**「階梯タグを書いた人だけが検査される」**チェックで、
     書かなければ無検査で通る。実データでは self の履歴30行のうち階梯タグを持つ行が**0行**（タグ付き5行はすべて
     補助タグ〈架空〉）、ai-reskilling も6/6行が〈二次〉のみ＝**両プロジェクトで一度も発火していなかった**。
  2. **相対mdリンクが誰にも検証されていなかった**。`check_wikilinks` は wikilink 専用。`/ingest`→`/learning` の
     改名で壊れた参照が `AIRE-TEST-002/003` に残り、**テストカード本文は board ビューへ逐語転記されるため
     再生成しても直らない**壊れたリンクが生成物に残り続けていた。
  3. **`sources/` 内のリンク切れが見えなかった**（lint は `sources/` を走査していなかった）。
  4. **`stage.md` の自己矛盾**。`projects/self` は `current-stage: CPF` なのに本文が `playbooks/fpf.md` の
     移行基準を参照しており、`/deciding` は stage.md の上書きを優先して読むため
     **現在ステージと違う基準で判断される**実バグだった。
- **改善案 / 対応**: 1 は階梯タグゼロで要求域に達している仮説を warning にし、補助タグ〈二次〉〈架空〉が
  階梯を満たさないことを明示（self に6件の真の未達が出た）。2〜4 は新チェック
  `check_relative_links`・`check_source_links`（不変層なので **warning 固定**＝修正ではなく可視化）・
  `check_stage_doc` を追加。
- **方針**: これは**意図的に warning を増やす**変更である。「error 0・warning 0」ではなく
  「**error 0・warning は真の未達を正直に映す**」を目標とする（下記 KG-10 のレガシー扱いを参照）。
- **根拠**: 論文 §VIII.A「a pipeline with a good scorer improves itself; a pipeline without one drifts」／
  §XI.C「the evaluation harness gives a feedback loop, but the loop must be run」。

## KG-05: グラフ全体の歪みを誰も見ていなかった（連結性・孤立・ハブ・下流依存度）

- **対象**: `tools/graph.py`（新規）、`tools/gen_views.py`、`tools/hwlint.py`
- **状態**: 対応済み（2026-07-29。既存バックログ OI-F3・OI-D4・OI-G1 の決着）
- **課題**: ビュー生成は全て1ホップの逆引き索引で、走査は `check_relation_cycles` の DFS だけだった。
  型付きリンクを持ち `relations` ビューで可視化までするのに、**グラフ構造そのものを健全性・優先度の判定に
  使っていなかった**。時間軸も同様で、確信度履歴は日付を持つのに lint もビューも見ていなかった
  （半年前の確信度8と昨日の8が同格に扱われる）。
- **改善案 / 対応**: `tools/graph.py`（`edges`/`adjacency`/`degree`/`components`/`descendants`/
  `downstream_counts`/`isolated`/`density`）を新設し、`gen_views.relation_edges` を委譲して
  診断とビューが同じ辺集合を共有するようにした。`relations` ビューに「グラフ診断」節（辺÷ノード＝論文の密度指標・
  連結成分・孤立仮説・ハブ・下流依存度・未取り込み生データ）を追加。`next_to_verify` に**下流依存度**を
  優先度シグナルとして織り込み（OI-D4 の残タスク）、`check_isolated_hypothesis`・`check_stale_confidence`・
  `check_stale_test` を追加（閾値は `ontology.yaml` の `staleness` が正本）。
  **確信度は自動で下げない**（不変ルール1厳守・可視化のみ）。
- **意図的に作らないもの**: ランタイムのグラフ検索（k ホップ照会・部分グラフ直列化）。`ontology-improvements.md`
  「H. あえて採らない」の判断を維持する（現規模では Claude が `wiki/` を直接読む方式より劣化する）。
  `graph.py` は**射影のための計算**であって検索エンジンではない。
- **根拠**: 論文 §V.E「Graph Diagnostics」（連結成分・次数分布・辺/ノード比 1.55 を健全域とする）／
  §IX.F「Monitoring in Production」。

## KG-06: 無作為サンプル点検が儀式として存在しなかった

- **対象**: `.claude/skills/lint/SKILL.md`
- **状態**: 対応済み（2026-07-29）
- **課題**: 機械チェックは「出典が**在るか**」までしか見ない。「出典の内容が主張を**実際に支えているか**」は
  人の目でしか見えないのに、それを回す手順が無かった。
- **改善案 / 対応**: `/lint` に「無作為サンプル点検」を追加。毎回1件（高確信度の H を優先）について
  **活動 → LEARN → `sources` → 生データ本文**まで辿り、根拠セルの主張・引用・証拠種別タグ・架空上限を
  突き合わせる。説明できない行は `/chabudai` の入口として手渡す（その場で確信度を動かさない）。
  点検した対象IDを `log.md` に残す（どのノードを最後に人が読んだかを追えるようにする）。
- **効果の実証**: 導入直後にこの点検を1回回して `SELF-LEARN-006`（`outcome: 是正`）を起票した。
  **機械チェックを全て通り抜ける欠陥が3件出た**（表層形の乱れ・購買意向2/10のうち1名の転記漏れ・
  不変カードと出典のコホート記述の矛盾）。数値はすべて正しく、壊れていたのは追跡可能性だけだった。
- **根拠**: 論文 Appendix D「Human sample — Does someone read a random node profile each day?
  Failure if missing: Comprehension rot — the graph outgrows understanding」／
  §XI.E「the moment you cannot explain why a node has a particular edge, your understanding of the graph
  has fallen behind its contents」。

---

## KG-07: レコード外エンティティ（インタビュイー・セグメント・競合）の第一級化と名寄せ

- **対象**: `ontology.yaml`（`entities`・`relations`）、`tools/ontology.py`（`ID_RE`）、`tools/hwlint.py`
- **状態**: **未対応（要設計合意）**。規約レベルの最小対処のみ実施済み
- **課題**: 論文 §IV の核心は「同一実体が文書ごとに別表層形で現れ、素直にグラフ化すると分裂する」。
  このリポジトリは H/TEST/LEARN/DEC 以外を**一切ノードにしていない**ため散文の表層形が野放しで、
  **実害が出ている**（詳細と原文引用は [[SELF-LEARN-006]]）:
  - インタビュイーのラベル体系が3ラウンドで互換でない（`対象者A`〜`対象者E` ／ `対象F`〜（10名中4名しか命名・`I` が飛ぶ）／
    裸の `K,L,M,N,P,Q,R,S,T`（10名に9文字・`O` が飛ぶ））。
  - `対象B系`・`対象C系` というラウンド跨ぎの曖昧参照が、別人10名のはずのファイルに現れる。
  - 想定セグメントの呼称が5通り以上。ピボット候補側も3通り。
  - 不変のテストカード（`SELF-TEST-004`）と出典でコホートの記述が食い違う（`Miro/Notion` vs `Miro/FigJam`。
    `FigJam` はリポジトリ全体で1箇所のみ）。
  - **コーパス自身が欠けている型を要求している**: `AIRE-LEARN-002`「分析単位を検証済み顧客セグメントに昇格できるか」。
- **改善案（設計選択肢）**:
  1. **新 entity（`SEG` セグメント／`PSN` インタビュイー／`ALT` 既存の代替手段）** — 表現力は最大だが、
     `ID_RE`（`tools/ontology.py`）から `check_wikilinks`・全ビューまで波及する SSoT の設計変更。
     インタビュイーを接頭辞つきノートにすると匿名性・件数（1ラウンド10名）の扱いも設計が要る。
  2. **セグメントだけをノートにする**（`<PREFIX>-SEG-NNN`）— 実害が最も大きいのはセグメント名の揺れで、
     かつ件数が少ない（2〜3）。`addresses` と同じく H から `targets` 関係で結ぶ。範囲が小さく効果が大きい。
  3. **alias 表を schema 層に持つだけ**（型を増やさない）— `ontology.yaml` に `aliases` 節を置き、lint が
     「正規名以外の表記がレコードに現れた」を warning にする。論文の alias map の最小実装。
- **実施済みの最小対処**: `SELF-LEARN-006` の「名寄せ規約」表で**正規名を1つずつ固定**した（案3の人手版）。
  過去の記録（不変層・追記済み履歴）は書き換えないので、この表が対応辞書として機能する。
- **推奨**: **案2 → 案3 の順に検討**。案1（全面的な entity 追加）は `ontology-improvements.md` の E
  （表現力拡張・要設計合意）と同じ土俵なので、E の議論に合流させる。
- **根拠**: 論文 §IV「Entity Resolution」・§IX.B「Resolution at Scale」・Appendix D「Alias map」。

## KG-08: 評価ハーネス（gold set / F1 ループ）

- **対象**: 新規（`tests/gold/` 相当）、`.claude/skills/*/SKILL.md`
- **状態**: **未対応（見送り。規模が大きい）**
- **課題**: 論文 §VIII の中核は「**change the extraction prompt, rerun the scorer, watch the F1 move**」で、
  これが「デモを本番システムにする」機構だとする。このリポジトリには**自分自身の抽出品質を測る手段が無い**。
  スキル（`/learning` 等）が生データからどれだけ忠実に学びを抽出できているかは、
  `docs/skill-improvements.md` に定性的な所見として溜まるだけで、**スキル改訂の効果を測れない**。
  `docs/competitive-analysis.md` 3-C1（「規約に書いた＝守られる、ではない。実効性を仕組みで示さないと
  売りが絵に描いた餅になる」）に直結する。
- **改善案**: 代表的な `sources/` 2〜3件について「そこから作られるべき LEARN の骨格（事実の件数・
  証拠種別タグ・outcome・動かすべき仮説）」を人手で作った**正解セット**を置き、スコアラで突き合わせる。
  スキル文言を変えたらスコアを回して増減を見る。
- **見送る理由**: 正解セットの維持コストが現規模に対して大きく、かつ「正解」の定義自体が主観を含む
  （インタビューの学びは NER のように一意でない）。**KG-06（無作為サンプル点検）が人手による代替**として先に効く。
  実案件が増えて `/learning` の出力揺れが実際に問題になった時点で再検討する。
- **根拠**: 論文 §VIII「The Evaluation Feedback Loop」・Appendix D「Gold set — Failure if missing:
  No feedback loop; prompt changes are blind」。

## KG-09: 抽出量キャップ（Extraction cap）

- **対象**: —
- **状態**: **該当なし（却下）**
- **課題**: 論文は「1回の実行で処理する文書数に上限を置き、コーパス取り込みエラーが無制限のコストを生まないように
  する」ことを求める。
- **却下理由**: このリポジトリの取り込みは**人手ペース**（`/learning` が1回で扱うのは1〜2件の生データ）で、
  無制限の自動取り込みループが存在しない。`stop_view_gen.py` の再生成も mtime 比較で変化した案件だけを回す。
  暴走コストの経路が無いため、キャップを設ける対象がない。将来 `sources/` へのバッチ投入経路を作るなら再検討する。
- **根拠**: 論文 Appendix D「Extraction cap」。

## KG-10: retro-fix 不能なレガシー warning の扱い（`evidence-tag` 15件）

- **対象**: `projects/self/wiki/hypotheses/*`（確信度履歴）、`.claude/skills/lint/SKILL.md`
- **状態**: **対応済み（方針の確定。件数の解消はしない）**
- **課題**: `evidence-tag` warning 15件は `projects/self/wiki/log.md` で「別debtとして据え置き」とされてから
  解消していない。**これは怠慢ではなく構造的に解消不能**である: 証拠種別タグは確信度履歴の過去行に書くもので、
  **確信度履歴は追記専用（不変ルール2）**だから、過去行にタグを足すことは規約違反にあたる。
  KG-04 で `evidence-floor` を発火させたことにより、同種の「解消できない warning」が6件増えた。
- **方針**: **消さない。事実として残す。**
  - `evidence-tag`（15件）= 「当時タグ規約が無かった行がある」という**履歴の事実**。
  - `evidence-floor`（6件）= 「**現在の確信度が証拠の強さに支えられていない**」という**現在の事実**。
    こちらは解消できる——ただし過去を書き換えるのではなく、**新しい検証を回して階梯タグつきの行を追記する**か、
    `/chabudai` で確信度を引き下げるという、規約に沿った方法で。
  - したがって「warning 0 を目指す」運用にはしない。**error 0 を不変条件とし、warning は真の未達を映す計器**として扱う。
- **根拠**: 不変ルール2（追記専用）／論文 §VIII.B「in a production system, this is usually the right tradeoff」
  （＝検出方針は目的に照らして意図的に選ぶもの、という構え）。

---

## 着手順の目安（未対応分）

1. **KG-07 案2（セグメントのノート化）** — 実害が最大かつ範囲が小さい。`ontology-improvements.md` の E と合流して設計する。
2. **KG-07 案3（alias 表 + lint）** — 案2 で解決しない表層形（インタビュイー・代替手段）に対する軽量な受け皿。
3. **KG-08（評価ハーネス）** — 実案件で `/learning` の出力揺れが問題になってから。KG-06 の点検記録が
   「どこが揺れるか」の材料になるので、それが溜まるのを待つ。

> KG-09 は該当なし（却下）、KG-10 は方針確定済みで、いずれも再検討の契機を各項に明記してある。
