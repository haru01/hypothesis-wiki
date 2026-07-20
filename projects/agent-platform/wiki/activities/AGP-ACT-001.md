---
id: AGP-ACT-001
title: AIエージェントPFのデスクリサーチ（想定ユーザ課題＋競合）
type: desk-research
date: 2026-07-20
stage: CPF
hypotheses: [AGP-H-001, AGP-H-002, AGP-H-003, AGP-H-004, AGP-H-005]
riskiest-assumption: 会話/成果の散逸とナレッジ断絶は、文献の一般論でなく特定の企業チームが実コスト（探し直し・再作成・監査対応）を払っている実在の痛みである
outcome: 起票
---

# AIエージェントPFのデスクリサーチ（想定ユーザ課題＋競合）

対象仮説: [[AGP-H-001]] [[AGP-H-002]] [[AGP-H-003]] [[AGP-H-004]] [[AGP-H-005]]
生データ: [desk-research（ユーザ課題）](../../sources/2026-07-20-desk-research-agent-platform.md) ／ [競合マップ](../../sources/2026-07-20-desk-research-competitors.md)

## テストカード（検証前に記入・後から書き換えない）

### 目的

AIエージェントPF領域で、想定ユーザ（大企業/中小のナレッジワーカー・AI運用担当）の状況・行動と課題の相場観を掴み、
競合の重なる核と決定的な違いを把握して、行動/課題仮説を確信度3-4で起票する（一次インタビュー前の入口）。

### 方法

`WebSearch` で複数角度（観測/エージェント管理/オントロジー/主要ベンダー比較）から調べ、各主張に出典URLを紐づける。
競合は一次比較記事・ベンダー記述を突き合わせ、競合マップ（重なる核／決定的な違い／出典／時点）に整理する。

### 指標

同一の状況・課題を指摘する独立出典の数と一致度。競合マップの比較軸（共創／観測／オントロジー）のカバー。

### 成功基準

複数の独立した信頼できる出典が同一の状況・課題を指摘していれば確信度3-4で起票。単一出典・伝聞のみは確信度3止まり。

## 学習カード（検証後に記入）

### 学びの要点

市場は「共創（作成物支援）」「活動ログ/観測」「オントロジー化」が**別カテゴリに分断**しており、3者を一体で回す製品は見当たらない。核心の痛みは P2（会話→意思決定→組織知の断絶で decision history が失われる）。

### 事実（observed）

- 観測系ツールが乱立（Langfuse/Braintrust/Galileo/Arize/AgentOps）。「エージェント群を横断統治する control plane（AMP）」が新カテゴリ化（[Kore.ai](https://www.kore.ai/blog/best-ai-agent-management-platforms)、[aimultiple](https://aimultiple.com/agentic-monitoring)）。
- オントロジー/KG 論者は「governance metadata・policy・decision history を第一級で持て」と主張（[Enterprise Knowledge](https://enterprise-knowledge.com/ontology-and-knowledge-graph-in-the-age-of-ai-and-agents/)、[Squirro](https://squirro.com/squirro-blog/ai-agents-inference-knowledge-graphs)）。
- Palantir AIP は既にオントロジー×LLMを接続、監査/決定論実行に強いが初期投資が重い（[Rollio](https://www.rollio.ai/blog/top-enterprise-ai-agent-platforms)）。Salesforce Agentforce は監査証跡を2026-04にGA。

### 解釈（inference）

- 課題は4クラスタ（散逸P1／ナレッジ断絶P2／統治・監査P3／SMB非専任P4）に整理できる。核心は P2。
- 差別化の当たり: 3カテゴリ（共創・観測・オントロジー）の統合と「非専任でも回る軽さ」。ただし Palantir が上位互換になりうるため要一次検証。
- P4（SMB非専任）は状況証拠が弱く、確信度3止まり。

### 驚き・想定外

「オブザーバビリティ」市場がこれほど細分化している＝ログ散逸（P1）が現実の痛みである傍証。一方で「共創＋ログ＋オントロジー」を束ねる語り口はまだ薄い（＝空白の可能性）。

### 確信度の更新

| 仮説 | 更新前 | 更新後 | ステータス | 理由 |
|---|---|---|---|---|
| [[AGP-H-001]] | — | 4 | 未検証 | 〈二次〉独立複数出典が「各部門が個別にエージェント常用」を示す |
| [[AGP-H-002]] | — | 4 | 未検証 | 〈二次〉AMP新カテゴリ化＝運用分散の裏返し |
| [[AGP-H-003]] | — | 4 | 未検証 | 〈二次〉decision history 断絶をKG/オントロジー論者が指摘 |
| [[AGP-H-004]] | — | 3 | 未検証 | 〈二次〉SMB非専任は状況証拠が弱く単一寄り |
| [[AGP-H-005]] | — | 3 | 未検証 | 〈二次〉3カテゴリ統合の勝ち筋は当たりのみ（Palantirが脅威） |

### 次のアクション

一次インタビューで「特定の企業チームが散逸・ナレッジ断絶に実コスト（探し直し・再作成・監査対応の工数）を払っているか」を確認する（[[AGP-H-003]] 優先）。SMB非専任（P4）は別セグメントとして分けて聞く。
