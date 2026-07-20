# デスクリサーチ: 競合マップ（AIエージェントプラットフォーム）

**データ種別: デスクリサーチ（二次情報）。時点: 2026-07-20。** 機能は急速に陳腐化する点に注意。
一次ベンダーページはマーケ色を帯びる。不在系の主張（「Xが無い」）は機能ページから断定できない。

## 競合マップ

| 競合 | 系統 | 重なる核 | 決定的な違い | 出典（時点2026-07） |
|---|---|---|---|---|
| Palantir AIP/Foundry | オントロジー駆動 | オントロジーで会話/LLMを組織の業務実体に接続、監査/決定履歴を重視 | フルスタック前提・構築/維持の初期投資が重い。共創（作成物支援）より「運用の決定論的実行」寄り | [Rollio](https://www.rollio.ai/blog/top-enterprise-ai-agent-platforms) |
| Microsoft Copilot Studio | 生産性統合 | 会話でエージェント構築、M365にログ埋め込み | M365/Graph/Entra 前提の生産性オーケストレーション。オントロジー化・横断ナレッジ蓄積は主眼でない | [Rollio](https://www.rollio.ai/blog/top-enterprise-ai-agent-platforms) |
| Salesforce Agentforce | CRM/業務自動化 | 顧客対応の自律ワークフロー、監査証跡（Operations 2026-04 GA） | CRMネイティブ。作成物共創や汎用ナレッジ化ではない | [Rollio](https://www.rollio.ai/blog/top-enterprise-ai-agent-platforms)、[RoyalCyber: Agentforce vs Copilot Studio](https://www.royalcyber.com/blogs/salesforce/salesforce-agentforce-vs-microsoft-copilot-studio-ai-agents/) |
| Langfuse / Braintrust / Galileo / Arize / AgentOps | エージェント観測（Observability） | 会話/エージェントのトレース・評価・コスト分析 | 「後から分析」に強いが、作成物の共創支援やオントロジー接続は範囲外（計測特化） | [aimultiple](https://aimultiple.com/agentic-monitoring)、[Galileo](https://galileo.ai/blog/best-ai-agent-observability-platforms)、[Confident AI](https://www.confident-ai.com/knowledge-base/compare/best-ai-observability-tools-2026) |
| Squirro / TopQuadrant / 知識グラフ系 | ナレッジグラフ/オントロジー | 会話知見を推論可能なKGへ | エージェント実行・共創UXより KG 基盤側。作成物支援は主眼でない | [Squirro](https://squirro.com/squirro-blog/ai-agents-inference-knowledge-graphs)、[TopQuadrant](https://www.topquadrant.com/resources/knowledge-graphs-help-build-scalable-ai-agents/) |

## 差別化の論点（勝ち筋の仮説・要検証）

- 既存は「**共創（作成物支援）**」「**活動ログ/観測**」「**オントロジー化/組織知**」が別カテゴリに分断している。
- 本テーマの狙いは**この3つを一体で回す**こと（対話で作る→自然にログが残る→CLAUDE×LLM-wikiでオントロジーに結びつく）。
- ただしPalantirはオントロジーとLLMを既に接続済み。「共創UXの軽さ＋非専任でも回る運用」で差別化できるかは**要一次検証**（現時点は勝ち筋の当たりをつけただけ）。
