# デスクリサーチ: AIエージェントプラットフォーム（想定ユーザの状況・課題）

**データ種別: デスクリサーチ（二次情報・状況証拠）。一次インタビューは未実施。**
実観測ではないため、これ由来の確信度は上限3-4。実データで裏を取るまで「弱い」。

対象ドメイン: 対話でAIエージェントが作成物（資料・コード・分析）の作成を支援し、会話・エージェント・企業活動のログが自然に残り、
後からインサイト/分析ができるプラットフォーム。大企業・中小向け。CLAUDE×LLM-wiki×オントロジーの接続を想定。

調査日: 2026-07-20。検索は US ロケール（`WebSearch`）。

## 想定ユーザの状況・行動（S）

- **S1｜大企業のナレッジワーカーはAIエージェント/チャットで日々の作成物を作っている** — 出典: [Rasa: 10 Best AI Agent Platforms for Enterprise 2026](https://rasa.com/blog/10-best-ai-agent-platforms-for-enterprise-in-2026)、[Dust: Top AI Agent Builder Platforms for Enterprises 2026](https://dust.tt/blog/top-ai-agent-builder-platforms-enterprises)。なぜ起きるか: 生成AIの業務組み込みが「実験」から「常用」へ移行し、各部門が個別にエージェントを立てている。
- **S2｜企業のAI導入担当は複数チーム・複数エージェントを運用し始めている** — 出典: [Kore.ai: Best AI Agent Management Platforms 2026](https://www.kore.ai/blog/best-ai-agent-management-platforms)、[Futurum: Agentic AI Leading Vendors 2026](https://futurumgroup.com/press-release/agentic-ai-the-leading-vendors-winning-the-enterprise-in-2026/)。なぜ: 「エージェント群を横断統治する control plane（AMP）」が新カテゴリとして立ち上がっている＝運用が分散している裏返し。
- **S3｜運用チームは production のエージェントの挙動をトレース/評価しようとしている** — 出典: [Confident AI: Best Agent Observability Tools 2026](https://www.confident-ai.com/knowledge-base/compare/best-ai-agent-observability-tools-2026)、[Arize: Best AI Observability Tools 2026](https://arize.com/blog/best-ai-observability-tools-for-autonomous-agents-in-2026/)。なぜ: 会話/意思決定の「全経路」を後から追う需要（監査・改善）が生まれている。

## 想定ユーザの課題（P）

- **P1｜会話・成果が個々のツールに散逸し、横断で残らない** — 観測系が乱立（Langfuse/Braintrust/Galileo/Arize/AgentOps）している事実は、裏を返せば「ログが分断され、後から横断分析しにくい」状況の傍証。出典: [aimultiple: 15 AI Agent Observability Tools 2026](https://aimultiple.com/agentic-monitoring)、[Galileo: Best Agent Observability Platforms 2026](https://galileo.ai/blog/best-ai-agent-observability-platforms)。
- **P2｜会話から生まれた意思決定・知見が組織のナレッジ（オントロジー）に接続されず、「なぜそう決めたか」を後で辿れない** — 出典: [Enterprise Knowledge: Ontology and Knowledge Graph in the Age of AI and Agents](https://enterprise-knowledge.com/ontology-and-knowledge-graph-in-the-age-of-ai-and-agents/)、[Squirro: AI Agents Need an Inference-Bearing Knowledge Graph](https://squirro.com/squirro-blog/ai-agents-inference-knowledge-graphs)。なぜ: 「governance metadata・policy・decision history を第一級で持つオントロジー」が要ると論じられている＝現状は decision history が失われている。
- **P3｜監査・コンプライアンスのために会話/成果の証跡を残す必要がある（規制業種）** — 出典: [Rollio: Top Enterprise AI Agent Platforms 2026](https://www.rollio.ai/blog/top-enterprise-ai-agent-platforms)（Salesforce Agentforce Operations が2026-04にGA、監査証跡/コンプラ検証を追加）。
- **P4｜中小企業は専任のAI運用/オブザーバビリティ人材がおらず、ログ分析・改善に手が回らない** — 直接の一次出典は薄い（弱い＝要一次確認）。観測系ツールの多くが大企業/開発者向けで、非専任前提のSMB向けは手薄という状況証拠にとどまる。出典: [Braintrust: AI Observability Buyer's Guide 2026](https://www.braintrust.dev/articles/best-ai-observability-tools-2026)。

## 課題のクラスタ

1. **散逸クラスタ（P1）**: ログ/成果がツールごとに分断され横断で残らない。
2. **ナレッジ断絶クラスタ（P2）**: 会話→意思決定→組織知（オントロジー）の接続が切れ、decision history が失われる。★本テーマの核心に最も近い。
3. **統治/監査クラスタ（P3）**: 規制・監査のための証跡要求。
4. **非専任クラスタ（P4）**: SMB は運用人材不在で分析が回らない。

## 誠実な但し書き

- ベンダーページ・比較記事はマーケ色を帯びる。「不在（競合にXが無い）」は機能ページから断定できない。
- P4（SMB非専任）は状況証拠が弱い。一次で「実際に払えていないコスト」を確認するまで確信度3止まり。
- 機能・GA時期は陳腐化が速い（時点: 2026-07-20 の検索結果）。
