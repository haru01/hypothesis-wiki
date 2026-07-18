# 活動ログ（追記専用・grep可能）

形式: `## [YYYY-MM-DD] <type> | <ID> <要約> → <影響仮説と確信度変化>`

type は `hypothesis` `interview` `demo` `survey` `mvp-test` `desk-research` `self-reflection` `decision` `lint` のいずれか。

過去行は編集しない（追記のみ）。例: `grep "decision" log.md` で意思決定だけを抽出できる。

---

## [2026-07-19] hypothesis | BANK-H-001 事務部門は定型業務を手続き書＋複数システム＋人手で処理 → 新規作成 確信度3/未検証
## [2026-07-19] hypothesis | BANK-H-002 規制対応・接続の壁でAIがPoC止まり（核心候補） → 新規作成 確信度3/未検証
## [2026-07-19] hypothesis | BANK-H-003 誤り時の説明責任・是正フロー未設計で人手確認を外せない → 新規作成 確信度2/未検証
## [2026-07-19] hypothesis | BANK-H-004 個別AIツール乱立で横展開できずコスト分散 → 新規作成 確信度2/未検証
## [2026-07-19] desk-research | BANK-ACT-001 テストカード作成（BANK-H-001） → 検証計画
## [2026-07-19] desk-research | BANK-ACT-002 テストカード作成（BANK-H-002/003/004） → 検証計画
## [2026-07-19] desk-research | BANK-ACT-001 WebSearch言説取り込み（二次） → BANK-H-001 確信度3→4/検証中
## [2026-07-19] desk-research | BANK-ACT-002 WebSearch言説取り込み（二次） → BANK-H-002 3→4, BANK-H-003 2→3, BANK-H-004 2→3（検証中・二次のため上限4）
## [2026-07-19] hypothesis | BANK-H-005 可観測性・評価・ガバナンス欠如で本番移行できない → 取り込み中に創発・新規作成 確信度2/未検証
## [2026-07-19] decision | BANK-DEC-001 CPF継続（persevere）移行基準未達・次は一次インタビュー → ステージ変化なし（CPF）
## [2026-07-19] lint | 健全性チェック実施（hwlint: error0/warning0・意味チェック: 問題0件） → 健全。H-002とH-005の切り分けは一次検証の宿題（欠陥でない）


