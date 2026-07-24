# 活動ログ（追記専用・grep可能）

形式: `## [YYYY-MM-DD] <type> | <ID> <要約> → <影響仮説と確信度変化>`

type は `hypothesis` `interview` `demo` `survey` `mvp-test` `desk-research` `self-reflection` `decision` `lint` のいずれか。

過去行は編集しない（追記のみ）。例: `grep "decision" log.md` で意思決定だけを抽出できる。

---

## [2026-07-16] desk-research | SELF-ACT-001 企業の仮説検証の状況・課題を文献調査 → CPF仮説8本を起票、初期確信度3〜4/未検証で確定
## [2026-07-16] hypothesis | SELF-H-001 実践者は作る前に検証を反復する → 新規作成 確信度4/未検証
## [2026-07-16] hypothesis | SELF-H-002 学びが複数ツールに散在し集約されない → 新規作成 確信度4/未検証
## [2026-07-16] hypothesis | SELF-H-003 仮説の更新は報告サイクルに駆動される → 新規作成 確信度3/未検証
## [2026-07-16] hypothesis | SELF-H-004 記録が残らず散逸・属人化（★核心） → 新規作成 確信度4/未検証
## [2026-07-16] hypothesis | SELF-H-005 確証バイアスで反証を軽視 → 新規作成 確信度4/未検証
## [2026-07-16] hypothesis | SELF-H-006 好意的反応を購買意向と取り違え偽の確証 → 新規作成 確信度4/未検証
## [2026-07-16] hypothesis | SELF-H-007 反証不能な曖昧仮説を成功基準なしで検証 → 新規作成 確信度4/未検証
## [2026-07-16] hypothesis | SELF-H-008 検証の根拠を経営層に説明できず合意形成が停滞 → 新規作成 確信度4/未検証
## [2026-07-17] interview | SELF-ACT-002 問題インタビュー5名（架空） → H-001 4→6, H-002 4→6, H-003 3→5, H-004 4→6, H-006 4→6, H-008 4→6（検証中）／H-005・H-007 は自認あるも実コスト0で据え置き4
## [2026-07-18] interview | SELF-ACT-003 核心クラスタの反証テスト10名（架空） → H-004 6→8, H-006 6→8, H-008 6→8, H-002 6→7, H-001 6→7（検証済み・架空ゆえ上限8）
## [2026-07-18] decision | SELF-DEC-001 CPF→FPF 移行（核心クラスタが移行基準を充足） → ステージ FPF へ
## [2026-07-18] hypothesis | SELF-H-009 AI支援＋構造化記録が既存ツールより核心課題を解決する（ソリューション・先取り） → 新規作成 確信度2/未検証
## [2026-07-18] hypothesis | SELF-H-010 実践者は対価を払い既存ツールから乗り換える（買ってもらえる・先取り） → 新規作成 確信度2/未検証
## [2026-07-18] interview | SELF-ACT-004 確信度WikiのLP生成（lp・SPF先取りプレビュー） → SELF-H-009/010 確信度変更なし
## [2026-07-18] interview | SELF-ACT-004 LP提示インタビュー10名（架空・interest8/intent2） → SELF-H-009 反証, SELF-H-010 反証（確信度2据え置き・実データ未検証）
## [2026-07-18] lint | 健全性チェック実施 → 問題0件（9項目すべて健全）。助言2件（FPF重点の自分たち仮説が未起票／ACT-004はSPF先取りプレビュー）

## [2026-07-19] self-reflection | SELF-ACT-005 揺さぶり監査（ちゃぶ台返し）。架空データは〈実コスト〉〈行動〉に乗らず「検証済み」を満たさない → SELF-H-001 7→6, SELF-H-002 7→6, SELF-H-004 8→6, SELF-H-006 8→6, SELF-H-008 8→6（いずれも検証済み→検証中）。SELF-DEC-001 の巻き戻しシグナル1が点灯、CPF巻き戻しを /decide 候補として記録
## [2026-07-19] decision | SELF-DEC-002 FPF→CPF巻き戻し（架空依存の偽検証済みを是正・DEC-001シグナル1点灯） → ステージ CPF へ。核心クラスタは検証中6のまま実データ再検証を最優先

## [2026-07-21] lint | 二重表現の補完（relation-wikilink 警告9件）。H-001/002/003/004/006/008/009 の leads-to 因果先を系譜節に本文 wikilink で追記し Obsidian グラフに辺を出す → 確信度・ステータス変更なし（残 evidence-tag 15件は別debtとして据え置き）

## [2026-07-24] self-reflection | ACT/LEARN 分割の移行（テストカード=ACT と 学習カード=LEARN を分離）
## [2026-07-24] self-reflection | SELF-ACT-001 → SELF-LEARN-001 に移行（回顧型・学び分離）。SELF-ACT-001 は欠番として取り下げ・再利用しない
## [2026-07-24] self-reflection | SELF-ACT-005 → SELF-LEARN-005 に移行（回顧型・学び分離）。SELF-ACT-005 は欠番として取り下げ・再利用しない
## [2026-07-24] self-reflection | SELF-ACT-002 を学び SELF-LEARN-002 に分割（SELF-ACT-002 はテストカードとして存続。確信度の根拠 citation は SELF-LEARN-002 へ張替）
## [2026-07-24] self-reflection | SELF-ACT-003 を学び SELF-LEARN-003 に分割（SELF-ACT-003 はテストカードとして存続。確信度の根拠 citation は SELF-LEARN-003 へ張替）
## [2026-07-24] self-reflection | SELF-ACT-004 を学び SELF-LEARN-004 に分割（SELF-ACT-004 はテストカードとして存続。確信度の根拠 citation は SELF-LEARN-004 へ張替）
