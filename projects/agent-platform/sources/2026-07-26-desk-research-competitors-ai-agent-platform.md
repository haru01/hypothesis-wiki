# デスクリサーチ: AIエージェントプラットフォーム — 競合マップ

**データ種別: デスクリサーチ（二次情報）。時点: 2026-07-26。機能は急速に陳腐化する点に注意。**
手法: WebSearch による複数出典。WebFetch は本環境で全ドメイン403のため競合一次ページ未取得（要裏取り）。

## 競合マップ（3つの部族）

| 競合 | 系統 | 重なる核 | 決定的な違い | 出典 |
|---|---|---|---|---|
| LangGraph / LangChain | OSSフレームワーク | エージェント構築・オーケストレーション | 最大の自由度。統合・運用は自前。LangSmithで可観測性は別課金 | [Kore.ai](https://www.kore.ai/blog/7-best-agentic-ai-platforms) / [Awesome Agents pricing](https://awesomeagents.ai/pricing/agent-platform-pricing/) |
| CrewAI | OSSフレームワーク | 役割ベースのマルチエージェント協調 | 47K+ GitHub star。Hosted visual editorは$99/月〜（Basicは月50実行） | [Kore.ai](https://www.kore.ai/blog/7-best-agentic-ai-platforms) / [Lindy: CrewAI pricing](https://www.lindy.ai/blog/crew-ai-pricing) |
| Microsoft Agent Framework (AutoGen+Semantic Kernel) / Copilot Studio | マネージド（Azure/M365） | 業務ワークフロー自動化 | Q1 2026 GA、Fortune 100の約40%が採用。16万組織・40万エージェント本番 | [Make](https://www.make.com/en/blog/best-ai-agent-platforms) |
| Salesforce Agentforce 360 | マネージド（CRM-native） | CRM連携エージェント | CRMデータ密結合。Salesforce顧客が前提 | [Kore.ai](https://www.kore.ai/blog/7-best-agentic-ai-platforms) |
| Kore.ai / Rasa | マネージド（ガバナンス重視） | エンタープライズ管理・規制業界 | Kore.ai=Gartner Leader 3x・450+ Global 2000。Rasa=セルフホスト/規制対応 | [Kore.ai](https://www.kore.ai/blog/7-best-agentic-ai-platforms) |
| Sierra / Decagon / Cognigy / Moveworks / Aisera | 縦特化（顧客サービス等） | 特定業務のエージェント | 用途特化で即効性。汎用構築基盤ではない | [Kore.ai](https://www.kore.ai/blog/7-best-agentic-ai-platforms) |
| LangSmith / Galileo / Latitude / TrueFoundry | 可観測性特化（隣接） | エージェントのトレース・評価・デバッグ | 「作る」より「監視・評価」に特化。構築基盤の補完財 | [Latitude](https://latitude.so/blog/ai-agent-observability-tools-developer-comparison-guide-2026-devto) / [TrueFoundry](https://www.truefoundry.com/blog/ai-agent-observability-tools) |

## 価格の相場観（時点 2026-07-26）

- LangChain: 無料〜$39/seat/月（LangSmith・LangGraph Cloudは別課金）。
- CrewAI: $99/月〜（OSSセルフホストは無料）。
- Lindy: 無料〜$10.59/月（ノーコード、SMB向け、3,000+連携）。
- 一般に評価は無料で始まり、エンタープライズ本番は$10k+/月へ。
- 出典: [Awesome Agents pricing](https://awesomeagents.ai/pricing/agent-platform-pricing/) / [Lindy](https://www.lindy.ai/blog/crew-ai-pricing)。
- 但し書き: Lindy/Relevance等はLLMコストをプラットフォーム価格に内包し単位経済が不透明との指摘あり
  （[TPipe: The Open Source Lie](https://www.tentrilliontriangles.com/blog/2026-06-15-the-open-source-lie-2026-pricing/)）。

## 差別化の論点（勝ち筋の候補・仮説段階）

- 市場は「OSSフレームワーク」「マネージド業務基盤」「縦特化」「可観測性特化」に分裂。**PoC→本番の断絶
  （78%→14%）に効く"本番運用・信頼性"の水平レイヤー**が、フレームワークと縦特化の間に空白として見える。
- ただしこれは二次情報からの推論であり、FPFの自分たち仮説・PSFで検証すべき論点。CPFの現段階では起票しない。
