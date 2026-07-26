# スキル一巡ドッグフーディング — 問題記録

テーマ **AIエージェントプラットフォームビジネス**（slug=`agent-platform`, PREFIX=`AGP`）で全10スキルを
一巡実行し、指示どおり動かして踏んだ問題点を記録する。修正はあとで人間が行う。

- 実行日: 2026-07-26
- 進め方: グリル型スキルは私（AI）が創業者を演じ、定性データは架空/シミュレーション（`〈架空〉`・確信度≤8）。
- 記録フォーマット: 症状 / 原因・推測 / 重大度（致命的・中・軽微）/ 修正案。
- 「問題ゼロ」のスキルもその旨を明記する。

---

## 0. /new-project

### [new-project] 選んだ PREFIX を保存する場所が無く、ハイフン入り slug では自動導出が不整合
- **症状**: 手順1で「slug と PREFIX をユーザーと決める」とあるが、決めた PREFIX を保存する設定ファイル・
  frontmatter・stage.md 欄がどこにも無い。実際の PREFIX は `tools/records.py` の `Project.prefix` が
  **既存レコードIDから導出、無ければ `slug.upper()`** で決める。slug=`agent-platform` の空プロジェクトで
  `Project.prefix` を評価すると **`AGENT-PLATFORM`**（ハイフン込みの大文字）を返す。ところが最初のレコード
  `AGENT-PLATFORM-H-001` を作ると、導出正規表現 `^([A-Z0-9]+)-` はハイフンで止まり **`AGENT`** を返す。
  → **レコードの有無で PREFIX がブレる**（空: `AGENT-PLATFORM` / 1件以降: `AGENT`）。ハイフンを含む
  多語 slug すべてで発生。
- **原因/推測**: `tools/records.py:170-175` の `prefix` プロパティ。フォールバック `slug.upper()` が
  ハイフンをそのまま残すのに、抽出正規表現 `[A-Z0-9]+` はハイフンを prefix 文字に含めない。加えて
  new-project スキル（手順1）が「PREFIX を決める」と言いながら永続化しないため、slug と別の PREFIX
  （例 slug=`agent-platform` に対し PREFIX=`AGP`）を選んでも、ツール側はそれを知りようがない
  （最初のレコードIDを人手で `AGP-` にして初めて確定する）。
- **重大度**: 中（単語1つの slug なら顕在化しないが、推奨例 `acme-app` のようなハイフン slug で不整合。
  空プロジェクト期間に Stop フックが走ると `AGENT-PLATFORM` 混じりのビューが生成されうる）。
- **修正案**: いずれか。(a) new-project 手順で「PREFIX は英数字1トークン（ハイフン不可）」を必須化し、
  ハイフン入り slug には別 PREFIX を強制する旨をスキルに明記。(b) 選んだ PREFIX を stage.md か
  専用 frontmatter に永続化し、`Project.prefix` がそれを最優先で読む。(c) 最低限、`slug.upper()`
  フォールバックを `re.split(r'[^A-Z0-9]', slug.upper())[0]` 等に合わせ、抽出正規表現と一致させる。
- **回避**: 本試走では単一トークン `AGP` を採用したため、最初の `AGP-*` レコード作成後は一貫して `AGP`。

### [new-project] 良かった点
- `cp -r templates/project/. projects/<slug>/` は素直に通り、雛形ツリー（sources・wiki 各種）が揃った。
- stage.md のプレースホルダ（`updated:` と履歴行の `YYYY-MM-DD`）は2箇所で明快。手順3の指示どおり埋められた。
- `index.md` を手編集しない規律・`.env` gitignore の注意書きも明確だった。

---

## 1. /desk-research

### [desk-research] LEARN の `stage` 欠落を lint が「規約外」と誤ラベル、スキルの記入チェックリストも stage を落としている
- **症状**: 手順5の「frontmatter」列挙（id / type / learns-from / hypotheses / outcome）に `stage` が無い。
  そのまま LEARN を書くと `stage` を落としやすい（実際に落とした）。`hwlint` は
  `[error] vocab | AGP-LEARN-001 | stage 'None' は規約外` と出す。**必須フィールドの欠落**なのに
  **値が語彙外**であるかのようなメッセージで、原因が分かりにくい。
- **原因/推測**: (a) desk-research SKILL.md 手順5の frontmatter 列挙が `stage` を明記していない
  （テンプレ `templates/learning.md` には `stage:` があるが、プローズを追うと漏れる）。
  (b) `tools/hwlint.py` の `check_vocabulary` が「未指定(None)」と「不正値」を区別せず同じ
  「規約外」メッセージにしている。
- **重大度**: 中（必須フィールド欠落は error で確実に止まるが、メッセージが誤誘導的で修正に手間取る）。
- **修正案**: (a) 手順5の列挙に `stage`（現在ステージ）を明記。(b) `check_vocabulary` で欠落時は
  「必須フィールド `stage` が未指定」、値不正時は「`stage 'xxx'` は規約外」と別メッセージにする。

### [desk-research] スキルが WebFetch 前提だが本環境では全ドメイン403でフォールバック指示が無い
- **症状**: 手順3が「競合の一次ページ・ドキュメント・READMEを `WebFetch` する」ことを求めるが、本環境では
  arxiv も含め **WebFetch が全ドメインで HTTP 403**（proxy は正常＝サイト側のbotブロック）。一次ページ精読が
  できず、WebSearch の要約（二次の二次）に依存せざるを得なかった。スキルには WebFetch 失敗時の代替手順が無い。
- **原因/推測**: SKILL.md 手順3・「守ること」が WebSearch/WebFetch 併用を前提。環境によって WebFetch が
  使えないケースの明示的なフォールバック（WebSearch 要約での三角測量＋但し書き強化）が書かれていない。
- **重大度**: 軽微〜中（環境依存。ただし「出典URLを必ず残す」規律と衝突しかける。実際は WebSearch の
  複数独立ドメインで三角測量し、sources に但し書きを明記して回避した）。
- **修正案**: 「守ること」に『WebFetch が使えない環境では WebSearch の複数独立出典で三角測量し、
  sources 冒頭に取得手段と限界を明記する』フォールバックを追記。

### [desk-research] 良かった点
- 確信度の上限規律（二次情報3-4）が明快で、全 H を確信度4で起票できた。`〈二次〉`タグの付与も自然。
- `leads-to` バリューチェーン配線（H-001→H-002→H-003/H-004）が list ビューの mermaid 矢印・
  relations ビューの逆リンクに正しく反映。sources 不変ガード（`guard_sources.py`）も新規追加を通した。
- LEARN→H の wikilink 二重表現、確信度履歴の初期行への `[[AGP-LEARN-001]]` 明記も指示どおり機能。

---

## 2. /formulating

### [formulating] 良かった点 — ほぼ健全
- 1問1答で「特定顧客・特定状況・特定行動」まで降ろす誘導が明快。generic な H-001 を核心の状況・行動仮説
  AGP-H-005（`derived-from: AGP-H-001`・`core: true`・`leads-to: [AGP-H-003]`）に具体化できた。
- 新規具体化仮説を確信度3（状況証拠止まり）で正直に付けられた。初期行の活動列 `—` はテンプレ規約どおりで
  hwlint の evidence-link チェックにも抵触せず。
- 作成後 `hwlint` が `untested-focus | AGP-H-005` を warning で出し、「重点仮説だが未着手 → /planning で計画」と
  次スキルへ正しく橋渡し。**期待どおりの挙動（バグではない）**。

### [formulating] 軽微 — desk-research と手順が大きく重複
- **症状**: CPF での H 起票手順（状況・行動→課題の順序・確信度3-4・leads-to 配線）が desk-research とほぼ同一。
  どちらを使うべきかの使い分けが、初見だと曖昧になりうる（desk-research=Web出典起点、formulating=対話起点、
  という差はあるが明文の線引きは薄い）。
- **重大度**: 軽微（実害なし。ワークフロー図で入口/反復ループの位置づけは示されている）。
- **修正案**: 各 SKILL.md 冒頭に一文「desk-research は二次情報からの一括起票、formulating は対話で1本を精錬」
  のような役割の線引きを添えると迷いにくい。

---

## 3. /planning

### [planning] 良かった点 — 健全
- 2軸マップ（重要度×確信度）→ 最優先の核心仮説 AGP-H-005 抽出 → 問題インタビュー（反証型）の流れが明快。
- `templates/testcard.md` の `riskiest-assumption`・目的/方法/指標/成功基準、`templates/problem-interview-script.md`
  ベースの反証型スクリプト（各仮説に反証質問を対で登録）を指示どおり作成できた。
- スクリプトからの schema 層リンク `../../../../playbooks/interviewing.md`（wiki/tests/ 配下＝深さ4）が規約どおり。
- **AGP-TEST-001 が AGP-H-005/H-003/H-004 を hypotheses に取った結果、formulating 後に出ていた
  `untested-focus` warning が解消**。未着手→計画済みの状態遷移が lint に正しく反映される（良い設計）。

### [planning] 軽微 — テストカードの `date` の意味が計画日/実施日で曖昧
- **症状**: 未実施のインタビュー計画なのに `date:` を記入する。計画日か実施予定日か実施日かが判然としない
  （本試走では作成日 2026-07-26 を入れた）。実施は将来で、学びは別途 LEARN が自分の date を持つ。
- **重大度**: 軽微（実害なし。既存プロジェクトも同パターン）。
- **修正案**: testcard テンプレの `date` コメントに「＝計画作成日。実施日ではない」を明記すると誤解が減る。

---

## 4. /building

### [building] ループ位置と CPF の「ソリューションを見せない」規律が衝突しうる
- **症状**: ワークフロー図では /planning の次が /building だが、**CPF ではソリューションを見せない**（問題インタビュー）。
  一方 /building は「demo/interview で見せる LP/モックを作る」スキル。CPF 段階では (a) 見せるべき
  **ソリューション仮説が1本も無い**（課題仮説から価値提案を"発明"して描くことになる）、(b) step5「対象仮説に
  紐づく計画済み demo/interview TEST（LEARN未紐づけ）があれば再利用」を素直に適用すると、**CPFの問題インタビュー
  TEST（AGP-TEST-001、ソリューション非提示）に、ソリューション LP を貼り付けてしまう**危険がある。
- **原因/推測**: /building の step5 の TEST 再利用条件が「demo/interview で LEARN 未紐づけ」だけを見ており、
  **その interview が CPF の"見せない"問題インタビューか、PSF の"見せる"ソリューションインタビューかを区別しない**。
  また `先取りプレビュー` の stage 判定は「対象仮説のステージ > 現ステージ」で発火するが、CPF では対象仮説も CPF
  なので発火せず、ソリューション先取りという実態と噛み合わない。
- **重大度**: 中（証拠汚染につながりうる。本試走では AGP-TEST-001 に触れず、新規 survey TEST(AGP-TEST-002,
  stage=PSF)を「先取りプレビュー」として明示作成し回避した）。
- **修正案**: (a) step5 の再利用条件に「**CPF の問題インタビュー TEST は対象外**（ソリューション非提示の TEST に
  プロトタイプを紐づけない）」を明記。(b) /building 冒頭に「ソリューション仮説が未形成/現ステージが CPF のときは
  先取りプレビュー扱いにし、専用 TEST を新設する」ガイドを追加。(c) 先取り判定を「生成物がソリューション提示を
  含むか」でも見るようにする。

### [building] 良かった点
- LP 骨格 `templates/building-lp.html` から**外部依存ゼロ**の自己完結HTMLを生成（CDN・外部画像・fetch なし、
  `file://` 起動可を grep で確認）。インラインSVGで画面イメージも描けた。
- **「検証済みタグは検証済み課題のみ」規律が正しく効いた**: 全課題が確信度3-4/未検証なので `検証済み` タグを
  一つも付けず、代わりに「未検証・検証中」と明示。証言・料金も「デモ用ダミー/仮の表示」を明記。
- 確信度・ステータスを一切動かさない責務境界を守れた（検証前の小道具）。プロダクト名は仮称と明示し実在を装わない。

---

## 5. /learning

### [learning] 確信度更新の直後、Stopフック前に hwlint すると index-sync が一時的に error になる
- **症状**: /learning で仮説の確信度を更新した直後（3件を 3→6, 4→6, 4→3）、`hwlint` が
  `index-sync | index.md | ... 不一致` を **error 3** で出す。`index.md` は生成物で、再生成
  （`gen_views.py index`）すれば解消。Stopフックが毎ターン末に再生成するので実運用では収束する。
- **原因/推測**: `index-sync` チェックがレコードと生成物 `index.md` の一致を error で求めるが、確信度更新と
  ビュー再生成の間にタイムラグがある。/lint の step0 が hwlint を呼ぶため、**Stopフック発火前に /lint を
  回すと偽陽性の index-sync error が出る**。
- **重大度**: 軽微（Stopフックで自動収束。ただし手動 hwlint／CI順序次第で誤警報）。
- **修正案**: /learning 手順6の直後に「`gen_views.py index` を再生成してから lint」を明記するか、
  hwlint に「index 再生成の要否」を促す注記を出す（index-sync を warning へ格下げする案もあるが、
  実際のドリフト検出力が落ちるのでトレードオフ）。

### [learning] 設計論点 — 架空データで確信度6まで上げられる（fictional-cap=8）
- **症状**: 純粋な架空インタビューデータで [[AGP-H-003]]/[[AGP-H-005]] を確信度**6**（検証中）まで上げられた。
  `fictional-cap` は8なので lint は通る。`〈架空〉`タグ・「実データ未検証」明記は徹底したが、**ゼロ実証拠で
  6という中程度の確信度が付く**のは、`self` プロジェクトが陥って巻き戻した罠（架空データで"検証済み"化）と同型。
- **原因/推測**: `ontology.yaml` の `fictional-cap: 8`。架空でも8まで許容する設計。マーキングで担保する方針。
- **重大度**: 中（設計判断の是非。バグではないが、事故りやすい）。
- **修正案（要検討）**: 架空/シミュレーション由来の上限を8より低く（例4-5＝状況証拠相当）に締めると、
  「実データで置換するまで中確信度に到達しない」規律が効く。少なくとも /learning の「守ること」に
  「架空データでの確信度は状況証拠上限（3-4目安）に留め、5以上は実観測を要する」旨を強調すると安全。
  ※本試走ではこの罠を意図的に踏み、次の /chabudai で揺さぶって引き下げる素材にする。

### [learning] 良かった点
- 成功基準の3値判定（支持/反証/判断保留）に沿って、支持（H-003/H-005 引き上げ）・判断保留（H-004 引き下げ）を
  同一 LEARN で正直に扱えた。反証寄りシグナルを都合よく無視しなかった。
- 創発課題（回帰/評価テスト欠如）を [[AGP-H-006]] としてその場で起票し、`derived-from`・LEARN の `hypotheses` に
  紐づけ、事後発見のため確信度を低く（3）保つ規律も機能。
- `learns-from: AGP-TEST-001` の紐付け、確信度履歴への追記＋frontmatter同期、evidence-floor（6には〈自認〉必要）を
  満たすタグ付けが指示どおり通った。
