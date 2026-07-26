---
id: AGP-LEARN-001
title: デスクリサーチ — AIエージェント本番化の断絶と可観測性/統合の課題
type: desk-research
date: 2026-07-26
stage: CPF
hypotheses: [AGP-H-001, AGP-H-002, AGP-H-003, AGP-H-004]
outcome: 起票
---

# デスクリサーチ — AIエージェント本番化の断絶と可観測性/統合の課題

対象仮説: [[AGP-H-001]] [[AGP-H-002]] [[AGP-H-003]] [[AGP-H-004]]

揺さぶり材料/生データ: [想定ユーザの状況・課題](../../sources/2026-07-26-desk-research-ai-agent-platform.md) ／ [競合マップ](../../sources/2026-07-26-desk-research-competitors-ai-agent-platform.md)

## 学習カード（検証後に記入）

### 学びの要点

AIエージェントは「作れるが本番で動かし続けられない」— PoCは78%が走るのに本番化は14%。停滞の主因はモデル能力でなく
**可観測性（なぜそう動いたか追えない・サイレント失敗）と統合の複雑さ（ツール毎のカスタムコネクタ）**という運用課題。
「本番運用・信頼性の水平レイヤー」がフレームワークと縦特化の間に空白として見える。

### 事実（observed）

- 78%がパイロット、本番スケールは14%（[Shakudo](https://www.shakudo.io/blog/enterprise-ai-agent-production-failures)）。MIT: パイロットの95%が期待収益未達。Gartner: 2027末までにエージェント型AIの40%超が中止（[AI Accelerator Institute](https://www.aiacceleratorinstitute.com/ai-agents-keep-breaking-in-production-heres-why-nobodys-fixed-it-yet/)）。
- 本番投入は「構造化された評価ハーネス・分散トレース・失敗分類なしに」行われがち（[Shakudo](https://www.shakudo.io/blog/enterprise-ai-agent-production-failures)）。「なぜエージェントがそう動いたか」に答えられない／サイレント失敗（[Galileo](https://galileo.ai/blog/debug-multi-agent-ai-systems)）。
- 「ツール毎にカスタムコネクタが要り、各々が障害点、累積で破綻」（[Shakudo](https://www.shakudo.io/blog/enterprise-ai-agent-production-failures)）。スコープ膨張＋データ品質が失敗の61%。
- OSSは自由度が高いが統合・保守が社内エンジニアに移る（[Make](https://www.make.com/en/blog/best-ai-agent-platforms)）。Copilot Studio=16万組織/40万エージェント本番、Microsoft Agent Framework Q1 2026 GA・Fortune100の約40%。
- 競合は OSSフレームワーク / マネージド業務基盤 / 縦特化 / 可観測性特化 に分裂（競合マップ参照）。

### 解釈（inference）

- 課題は「作る」より「本番で動かし続ける」に偏在。**可観測性/信頼性（P1）と統合/保守（P2）**を2大クラスタとして起票する。
- 独立した複数の信頼できる出典が同一の断絶（PoC→本番）と同一の課題を指摘しているため、課題側は確信度4で起票。
  ただし「どの顧客セグメントが実際に実コストを払っているか」は二次情報では確定できず、一次インタビュー待ち。
- 顧客セグメントの具体像（内製チーム）は S1/S2 から推論だが、二次情報のため確信度4止まり。特定企業・特定役割まで
  降ろす具体化は /formulating と一次インタビューで行う。

### 驚き・想定外

- 失敗の主因が「モデル能力」でなく運用（トレース・統合・スコープ）だと出典が口を揃える点。市場が
  「可観測性特化」ベンダー群（LangSmith/Galileo/Latitude等）をすでに生んでいる＝課題の実在の傍証。

### 確信度の更新

| 仮説 | 更新前 | 更新後 | ステータス | 理由 |
|---|---|---|---|---|
| [[AGP-H-001]] | — | 4 | 未検証 | 〈二次〉内製化パターンを複数出典が指摘（起票） |
| [[AGP-H-002]] | — | 4 | 未検証 | 〈二次〉78%→14%の本番化断絶を複数出典が指摘（起票） |
| [[AGP-H-003]] | — | 4 | 未検証 | 〈二次〉可観測性/サイレント失敗を独立複数出典が指摘（起票） |
| [[AGP-H-004]] | — | 4 | 未検証 | 〈二次〉統合の複雑さ/保守コストを指摘（起票） |

### 次のアクション

- 一次の問題インタビューで「特定の内製チームが、可観測性/統合に実際にどれだけの時間・金・手戻り（実コスト）を
  払っているか」を過去の事実として確認する（ソリューションは見せない）。
- /formulating で S1/S2 を特定顧客・特定状況まで具体化し、状況・行動仮説を1本に絞り込む。
