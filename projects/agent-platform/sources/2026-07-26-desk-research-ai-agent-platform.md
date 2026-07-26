# デスクリサーチ: AIエージェントプラットフォーム — 想定ユーザの状況・課題

**データ種別: デスクリサーチ（二次情報・状況証拠）。一次インタビューは未実施。**
調査日: 2026-07-26 ／ 手法: WebSearch による複数出典の三角測量（WebFetch は本環境で全ドメイン403のため未使用。下記「但し書き」参照）。

## 状況・行動（S）

- **S1: エンタープライズ/ミッドマーケットのエンジニアリングチームが、AIエージェントをOSSフレームワーク
  （LangChain/LangGraph/CrewAI/AutoGen）で内製し、各ツール連携を自前で実装・保守している。**
  - なぜ起きるか: OSSは自由度が高く制御を握れる一方、統合・保守の負担がすべて社内エンジニアに移る。
  - 出典: [Make: Best AI agent platforms 2026](https://www.make.com/en/blog/best-ai-agent-platforms)（「open-source tooling gives full control but shifts every integration and maintenance burden to internal engineers」）／[Kore.ai: best agentic AI platforms 2026](https://www.kore.ai/blog/7-best-agentic-ai-platforms)（LangGraph=stateful multi-agent, CrewAI=role-based 47K+ GitHub stars, AutoGen=Microsoft-centric）。

- **S2: 業務チームはノーコード/Microsoft系（Copilot Studio, Gumloop）で、開発チームはLangGraph/CrewAIで、と
  チーム構成で使い分けている。Microsoft Copilot Studio は 16万組織・40万エージェントが本番稼働と報告。**
  - 出典: [Make 2026](https://www.make.com/en/blog/best-ai-agent-platforms)（「160,000 organizations and 400,000+ custom agents in production」「Microsoft Agent Framework GA since Q1 2026, ~40% of Fortune 100」）。

- **S3: チームは高レベルのオーケストレーションライブラリでPoCを立ち上げた後、本番投入
  （安定稼働・スケール・安全なロールバック）の段階で停滞する。**
  - 出典: [Make 2026](https://www.make.com/en/blog/best-ai-agent-platforms)（「Shipping agents so they stay up, scales under load, and rolls back safely is where most teams stall」）／[Latitude: AI Agent Observability 2026](https://latitude.so/blog/ai-agent-observability-tools-developer-comparison-guide-2026-devto)（「Teams often start with high-level orchestration libraries like Crew AI before realizing that debugging distributed autonomy requires far deeper observability」）。

## 課題（P）

- **P1: 本番で「なぜエージェントがそう動いたか」を追跡できない（分散トレース・評価ハーネス・失敗分類が不在）。
  エージェントはサイレントに失敗する。**
  - なぜ起きるか: 実行が複数モデル・ツール・サービスに跨り、テレメトリが断片化。非決定的で同一プロンプトでも
    出力が変わり、従来のデバッグ手法が崩壊する。
  - 出典（独立複数）: [Shakudo: Why 80% of Enterprise AI Agents Fail](https://www.shakudo.io/blog/enterprise-ai-agent-production-failures)（「go into production without structured evaluation harnesses, distributed tracing, or systematic failure classification」）／[TrueFoundry: AI Agent Observability](https://www.truefoundry.com/blog/ai-agent-observability-tools)／[Galileo: 7 Multi-Agent Debugging Challenges](https://galileo.ai/blog/debug-multi-agent-ai-systems)（「Most teams running agents in production can't answer: why did the agent do that?」「agents often fail quietly」）。

- **P2: ツールごとにカスタムコネクタを実装する統合の複雑さと保守コスト。各コネクタが障害点になり、
  累積して破綻する。**
  - なぜ起きるか: 標準化された接続層が無く、エージェント×ツールの掛け算で連結が増える。
  - 出典: [Shakudo](https://www.shakudo.io/blog/enterprise-ai-agent-production-failures)（「Every agent needs a custom connector for every tool, every connector is a point of failure, and the cumulative weight of custom integrations eventually collapses the project」）。

- **P3: スコープの膨張とデータ品質の問題が失敗の61%を占める。**
  - 出典: [Shakudo](https://www.shakudo.io/blog/enterprise-ai-agent-production-failures)（「Scope creep and data quality issues cause 61% of all failures combined」）。

## 課題のクラスタ

1. **可観測性/信頼性**（P1）— 本番でのトレース・評価・失敗検知の欠如。
2. **統合/保守**（P2）— ツール連携の実装・維持コスト。
3. **スコープ/データ**（P3）— 適用範囲とデータ整備。

## 相場観（市場の広がり・断絶）

- 78%の企業がAIエージェントのパイロットを走らせるが、本番までスケールするのは14%。
  出典: [Shakudo](https://www.shakudo.io/blog/enterprise-ai-agent-production-failures)。
- MIT研究: 企業AIパイロットの95%が期待収益を出せず。Gartner: 2027末までにエージェント型AIプロジェクトの
  40%超が中止（理由はほぼモデル能力ではない）。出典: [AI Accelerator Institute](https://www.aiacceleratorinstitute.com/ai-agents-keep-breaking-in-production-heres-why-nobodys-fixed-it-yet/)／[dbreunig: Enterprise Agents Have a Reliability Problem](https://www.dbreunig.com/2025/12/06/the-state-of-agents.html)。
- 市場規模: 2025年に$7.6B、2033年まで年49.6%成長の予測。出典: [Kore.ai](https://www.kore.ai/blog/7-best-agentic-ai-platforms)。

## 但し書き（誠実な限界）

- WebFetch が本環境で全ドメイン403のため、競合一次ページの直接取得ができず、**検索結果の要約（二次の二次）に依存**。
  各主張は独立した複数ドメインで確認したが、原典の時点情報・原文引用の精度は一次取得に劣る。一次インタビュー・
  一次ページ精読で裏取りが必要。
- 「不在系の主張」（例: 競合にトレース機能が無い）は機能ページから断定していない。
- ベンダー系ブログはマーケ色を帯びる。数値（78%/14%, 40%, 95%）は出典元がさらに二次引用している可能性がある。
