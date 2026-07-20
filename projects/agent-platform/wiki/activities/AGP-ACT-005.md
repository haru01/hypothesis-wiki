---
id: AGP-ACT-005
title: デスクリサーチv2（仮説検証の一般化・ピボット後の再ベースライン）
type: desk-research
date: 2026-07-20
stage: CPF
hypotheses: [AGP-H-001, AGP-H-003, AGP-H-008]
riskiest-assumption: 「AIが試行錯誤の航跡からゴール・制約・使命を継続合成する」需要は、既存の方法論（DDP/effectuation）やツール（Strategyzer/OKR/second brain）では満たされない実在の空白である
outcome: 起票
---

# デスクリサーチv2（仮説検証の一般化・ピボット後の再ベースライン）

対象仮説: [[AGP-H-001]] [[AGP-H-003]] ／ 新規起票 [[AGP-H-008]]
生データ: [想定ユーザ・学術裏付け](../../sources/2026-07-20-desk-research-generalized-validation.md) ／ [競合マップv2](../../sources/2026-07-20-desk-research-competitors-validation.md)

## テストカード（検証前に記入・後から書き換えない）

### 目的

テーマピボット（Decision Record → 仮説検証の一般化）後、想定ユーザの状況・課題と競合を二次情報で調べ直し、
「暫定」だった核心仮説の確信度を二次情報の水準へ**再ベースライン**する。差別化の空白と最大の脅威を把握する。

### 方法

`WebSearch` で3方向（①effectuation/DDP/emergent strategy の学術・方法論 ②社内探索組織/イントレプレナーの痛み ③競合＝Strategyzer/OKR/second brain）から調べ、各主張に出典URLを紐づける。

### 指標

同一の状況・課題を指摘する独立出典の数と一致度。競合の重なる核／決定的な違いのカバー。差別化の空白が名指しできるか。

### 成功基準

複数の独立した信頼できる出典が同一の状況・課題を指摘していれば確信度3-4で（再）起票。単一出典・伝聞のみは3止まり。

## 学習カード（検証後に記入）

### 学びの要点

テーゼは学術的に妥当（effectuation＝不確実性下でゴールは事後創発／DDP＝前提を知識へ変換）。**だが最大の脅威は Strategyzer**——Test/Learning Card＋AI＋アプリ内検証を既に提供し、本wikiの実装とほぼ同型。差別化は「人がカードを回す」対「AIが航跡から方向を合成する」の一点に集約される。

### 事実（observed）

- effectuation では不確実性は**存在論的**（未来は原理的に不可知）、目的は手段から事後創発（[Springer 比較論文](https://link.springer.com/article/10.1007/s11187-019-00153-w)）。DDP は「前提を知識へ変換し理解の創発に応じ軌道修正」（[Soren Kaplan](https://www.sorenkaplan.com/discovery-driven-planning-template-for-business-strategy/)）。
- 探索的取り組みは**非線形に前後循環**（[Big Bang Partnership](https://bigbangpartnership.co.uk/the-intrapreneurship-process/)）。Horizon 3 にステージゲートを当てるのは**category error**（[Umbrex](https://umbrex.com/resources/corporate-innovation-playbook/innovation-operating-model/)）。
- イントレプレナーは**肯定的アイデンティティの構築に苦労**（2026査読・[JPIM](https://onlinelibrary.wiley.com/doi/10.1111/jpim.12798)）。
- 競合3系統: Strategyzer（人が回すフレーム＋AI）／OKR（ゴール先行＝逆思想・83%がAI活用）／second brain（capture中心・[Iwo 2026](https://www.iwoszapar.com/p/best-ai-second-brain-solutions)）。

### 解釈（inference）

- 空白は「試行錯誤の航跡から**ゴール・制約・使命をAIが継続合成**する」層（capture と goal-first の中間）。
- ただし Strategyzer が近接しすぎ＝差別化が「合成」の一点に賭かる。薄ければ再パッケージに堕ちる。
- beachhead は**社内探索組織（イントレプレナー）**が有力（P2の痛みが査読で相対的に強く、ビジョン先行の統治との摩擦が鋭い）→ [[AGP-H-008]] 起票。

### 驚き・想定外

「仮説検証の一般化」という新規のつもりが、Strategyzer が方法論もAIも実装済みで**思ったより混んでいた**。新規性の主張を「方向の自動合成」に絞らないと弱い。

### 確信度の更新

新テーマの二次情報水準で核心仮説を確認（4）。※ 当初はここで旧テーマ由来の暫定 5-6 からの再ベースラインを記録したが、後にその暫定値の源だった仮想インタビューを削除したため、根拠はデスクリサーチのみ（二次水準4）に一本化した（2026-07-20）。

| 仮説 | 更新前 | 更新後 | ステータス | 理由 |
|---|---|---|---|---|
| [[AGP-H-001]] | 4 | 4 | 未検証 | 〈二次〉effectuation/DDP/非線形循環が現象を支持。二次水準4で確認 |
| [[AGP-H-003]] | 4 | 4 | 未検証 | 〈二次〉中間の空白＋ステージゲートcategory error＋イントレ痛みが支持。二次水準4で確認 |
| [[AGP-H-008]] | — | 4 | 未検証 | 〈二次〉2026査読＋category error で社内探索組織の摩擦を支持（新規起票） |

### 次のアクション

- beachhead＝社内探索組織で一次インタビュー（[[AGP-H-008]] の実コストを確認）。
- 旧フレーム由来の [[AGP-H-002]]（ログ分断）・[[AGP-H-006]]（手コピペ転記）は新テーマで浮いている → 次に**reframe or 取り下げ**を検討。
- スコープは現在**行動仮説・課題仮説の段階まで**（解決策・LP・意思決定は範囲外として削除済み）。
