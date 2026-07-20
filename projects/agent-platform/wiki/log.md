# 活動ログ（追記専用・grep可能）

形式: `## [YYYY-MM-DD] <type> | <ID> <要約> → <影響仮説と確信度変化>`

type は `hypothesis` `interview` `demo` `survey` `mvp-test` `desk-research` `self-reflection` `decision` `lint` のいずれか。

過去行は編集しない（追記のみ）。例: `grep "decision" log.md` で意思決定だけを抽出できる。

---

## [2026-07-20] desk-research | AGP-ACT-001 AIエージェントPFのデスクリサーチ（ユーザ課題＋競合） → AGP-H-001..005 新規起票 確信度3-4/未検証
## [2026-07-20] hypothesis | AGP-H-006 手作業wiki転記の陳腐化（代替手段） → 新規作成 確信度2/未検証
## [2026-07-20] interview | AGP-ACT-002 テストカード作成（AGP-H-001/003/006・反証型スクリプト付） → 検証計画
## [2026-07-20] survey | AGP-ACT-003 価値提案LP生成（先取りプレビュー） → AGP-H-005/H-003 確信度変更なし
## [2026-07-20] interview | AGP-ACT-002 問題IV取り込み（架空6名・支持） → AGP-H-001 4→6/検証中・AGP-H-003 4→6/検証中・AGP-H-006 2→4/検証中（実データ未検証）
## [2026-07-20] hypothesis | AGP-H-007 切実さのセグメント依存（取り込み中に創発） → 新規作成 確信度3/検証中
## [2026-07-20] decision | AGP-DEC-001 CPF継続（persevere） → 移行基準未達・架空根拠のため実データ再実施を最優先。ステージ変化なし
## [2026-07-20] lint | 健全性チェック実施（hwlint: error 0/warning 0・testcard-immutable: 0・意味チェック: 問題0件） → 健全（架空データは全レコードで明示済み）
## [2026-07-20] self-reflection | AGP-ACT-004 揺さぶり監査 → AGP-H-003 確信度6→5（確証バイアス減点）／AGP-H-001 据え置き（反証耐性確認）
