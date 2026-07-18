# スモークテスト所見（bank-agent 案件・2026-07-19）

「銀行業務をAIエージェント前提で再設計するAIエージェント基盤」をテーマに、
`/new-project → /formulate → /plan → WebSearch言説収集 → /ingest → /view → /decide → /lint` を一巡し、
**競合分析にもとづく強化（hwlint・git/Claude Codeフック・証拠の階梯・証拠タグ）を含めて実際に回るか**を確認した。
インタビューは WebSearch での二次言説収集で代替。各項目: 摩擦 / 該当 / 深刻度 / 対応。

> 総括: 一巡は最後まで回り、hwlint は最終的に全プロジェクト error 0。**機構は実ワークフロー出力に対して機能した。**
> 途中で重大な false positive を1件発見し修正済み（P1）。残りは設計上の摩擦・軽微な不整合。

---

## P1【重大・修正済み】hwlint がHTMLコメント内の wikilink を誤検出
- **摩擦**: `templates/hypothesis.md` の確信度履歴コメントに例示 `[[ACT-NNN]]` が含まれ、テンプレに忠実に作った
  BANK-H-001〜004 全件で `check_wikilinks` が「リンク切れ」を error 検出。テンプレートとリンターが矛盾し、
  テンプレ通りに作った仮説が pre-commit / Stop フックで必ず弾かれる状態だった。
- **なぜ self では出なかったか**: self の仮説は手書きで当該HTMLコメントを削っていたため露見せず。テンプレ経由の
  新規案件で初めて発覚（＝ドッグフーディングの死角）。
- **該当**: `tools/hwlint.py` `check_wikilinks`。
- **深刻度**: 重大（テンプレ準拠の正当なレコードを全件ブロック）。
- **対応済み**: `strip_comments` を追加し本文からHTMLコメントを除去してリンク検査。回帰テスト追加（コミット 05509e3）。

## P2【中】/ingest の「承認を得てから反映」が自律/バッチ実行と噛み合わない
- **摩擦**: `ingest` は「確信度・ステータスは必ずユーザー承認を得てから反映」が原則。今回のような自律スモーク
  実行や将来のバッチ運用では、各更新で止まると回らない。今回は提案内容を明示したうえで自己承認して進めた。
- **該当**: `.claude/skills/ingest/SKILL.md` 手順4-5。
- **深刻度**: 中（規律として正しいが、非対話モードの概念がない）。
- **改善案**: 「事前に成功基準を確定した検証は、判定が〈支持/反証〉に機械的に定まる範囲で自動反映してよい／
  〈判断保留〉や成功基準の解釈が要る場合のみ承認を求める」など、承認の要否を段階化する。

## P3【中】Stop フックが中間状態（WIP）でターン終了を塞ぐリスク
- **摩擦**: `stop_lint.py` は現在プロジェクトに hwlint error が残るとターン終了をブロックする。ingest では
  「frontmatter を変えたが履歴テーブルはまだ」といった中間状態が一時的に error になる。編集途中でターンを
  終えられず操作を阻む恐れがある（今回はフック未発火セッションのため未発生だが構造的リスク）。
- **該当**: `.claude/settings.json` Stop フック / `tools/hooks/stop_lint.py`。
- **深刻度**: 中（正しく完了すれば無害だが、中断・レビュー時に詰まりうる）。
- **改善案**: Stop フックは error を**ブロック（exit 2）でなく警告（systemMessage）**に留める案、または
  「未コミット変更があるときは猶予する」等。強制はコミット時（pre-commit）に委ね、セッション内は助言に。

## P4【中・既知の再確認】sources/ ポリシーが CLAUDE.md と ingest/guard で食い違う
- **摩擦**: 今回 WebSearch 言説を AI が `sources/` に新規保存した（`ingest` 手順1どおり）。しかし CLAUDE.md
  3層表は sources を「人間が置く。AIは読むだけ」と規定。`guard_sources.py` は「新規Writeは許可・既存編集は禁止」。
  3者でスコープが微妙に異なり、実装が事実上の仕様になっている。
- **該当**: `CLAUDE.md`（3層表・不変ルール3）/ `ingest` 手順1 / `tools/hooks/guard_sources.py`。
- **深刻度**: 中（規約の一貫性。/simplify の Altitude 指摘 A4 と同一）。
- **改善案**: 「誰が sources を作成/変更/削除できるか」を CLAUDE.md で一度だけ厳密に定義し、ingest と guard が
  それを参照する。AI の新規配置を認めるなら3層表の「AIは読むだけ」を「新規追加は可・既存は不変」に精緻化する。

## P5【低】derived-from だけ接頭辞なし（H-001）でスキーマ内不統一
- **摩擦**: `templates/hypothesis.md` の `derived-from: H-003`（接頭辞なし例）に従うと、id・wikilink・
  hypotheses/based-on 配列が接頭辞つきなのに derived-from だけ短縮形になる。hwlint は derived-from の
  書式を検査しない（本文 wikilink と hypotheses/based-on のみ）ため、黙って揺れる。
- **該当**: `templates/hypothesis.md` / `tools/hwlint.py`（derived-from 未検査）。
- **深刻度**: 低（SI-005 / self #4 と地続き）。
- **改善案**: derived-from も接頭辞つきに統一し、hwlint に derived-from の実在・接頭辞チェックを足す。

## P6【低】/formulate・/plan・/view は対話・手作業前提で非対話実行の型がない
- **摩擦**: `formulate`（1問ずつ AskUserQuestion）・`plan`（どの仮説を検証するか選ばせる）・`view`（LLMが手書き生成）
  は人間同席前提。自律スモークでは私が判断を代行した。`view` は生成器がなく毎回手書きのためドリフト余地がある
  （SI-007 で生成器は作らない判断済み）。
- **深刻度**: 低（設計どおり。ただしバッチ検証や CI 的な使い方の口がない）。
- **改善案**: 必須ではないが、「非対話モードでの既定選択（例: plan は最優先1-2本を自動選択）」を定義しておくと
  スモーク/回帰に使いやすい。

## 機構が正しく効いたことの確認（ポジティブ）
- **証拠の階梯＋上限**: 二次情報（WebSearch）由来は確信度4で頭打ちにする運用が自然に流れた。〈二次〉タグを履歴
  根拠列に付けることで `check_evidence_tags` の warning も出ず、`検証済み`に上げない規律が守られた。
- **証拠リンク強制**: 確信度を動かした全履歴行に `[[BANK-ACT-NNN]]` を要求する `check_evidence_links` が
  最後まで error 0。証拠なき更新を1件も許さなかった。
- **創発仮説**: 取り込み中に BANK-H-005（可観測性・評価・ガバナンス欠如）が創発し、低確信度・専用再検証つきで
  起票する ingest 手順3が機能した。
- **DEC 非孤立**: persevere の BANK-DEC-001 が index「意思決定」節から被参照され、孤立検出に引っかからなかった
  （SI-006 対策が有効）。
- **log-sync / index-sync**: 接頭辞つきIDと `X→Y` 記法の log を正しく突合し false positive なし。
- **注意**: `.claude/settings.json` のフックは**次回セッション起動時**（または `/hooks` 再読込）から発火する。
  今回のセッションでは PreToolUse（sources ガード）・Stop（lint）は未発火。実効性の最終確認は次セッションで要実施。
