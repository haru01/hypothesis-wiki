# デスクリサーチ: AI時代のスクラムマスター（SM）のリスキリング

**データ種別: デスクリサーチ（二次情報・状況証拠）。一次インタビューは未実施。**
収集日: 2026-07-20 ／ 方法: WebSearch による多角的検索と独立出典の三角測量。各項目に出典URLを付す。
（注: scrum.org・humanizingwork・age-of-product・theagileforum 等は WebFetch がボット保護で 403。本文抽出はできず、検索エンジンのスニペット引用に基づく。数値は複数スニペットで突き合わせた。一次本文での再確認を次アクションとする。）
確信度の扱い: 二次情報のため起票する仮説は**確信度上限3-4**。不在系の主張（「〜が無い」）は断定しない。

対象＝**AI時代のスクラムマスター（SM）**。既存プロジェクト（2名＋専門エージェントの「作り手」が対象）の
**範囲拡張**として、少人数×AIエージェントのチームにおける SM ロールを想定ユーザに加える。
焦点＝(a) SM の役割・スキルがどう変わるか、(b) SM が既存プロジェクトの**認知的降伏シナリオ**
（AI出力の盲信・ラバースタンプ → 成果物ドリフト）に対してどんな位置を占めるか。

---

## A. 状況・行動（S）

- **S1｜SMの定型・儀式業務がAI/エージェントで自動化されつつある。** 進捗追い・議事録・チケット起票/整理・レポート・アジェンダ生成が対象。「アジャンティックAIがSM業務の約70%を自動化」「儀式の準備時間を最大60%削減」「スプリント計画を3倍速く」といった主張が複数の実務メディアで流通。Jira/Confluence連携で標準業務・ボトルネック検知まで自動化する SaaS（Agent Scrum 等）も登場。
  - 出典: [aidevdayindia（Impact of Agentic AI on Scrum Masters: 70% Tasks Dead）](https://aidevdayindia.org/blogs/generative-ai-for-scrum-master/impact-of-agentic-ai-on-the-scrum-master-role.html) ／ [scaledagile（How AI Empowers Scrum Masters）](https://scaledagile.com/blog/ai-empowers-scrum-masters/) ／ [Agent Scrum（AWS Marketplace）](https://aws.amazon.com/marketplace/pp/prodview-3ot66gehevrjq)
  - なぜ起きるか: SM業務の相当部分が「儀式の運営・記録・可視化」という定型作業で、LLM/エージェントの得意領域と重なる。
- **S2｜「儀式ファシリテーター/障害ロガー」としての専任SM職が現に削減・統合されている。** Capital One（2023）がアジャイル系 約1,100ロールをエンジニア/プロダクトへ統合、ある大手通信は2024にSM/POを廃し「Product Delivery Manager」へ集約、Meta 等でも純SM職の削減報道。求人・受講の縮小データもある（下記S参照）。
  - 出典: [Big Agile（Why the Scrum Master Role Is Being Cut）](https://big-agile.com/blog/why-the-scrum-master-role-is-being-cut-and-whats-actually-replacing-it) ／ [Humanizing Work（Agile Jobs Are Vanishing）](https://www.humanizingwork.com/agile-jobs-are-vanishing/) ／ [Humanizing Work（Making Sense of the ScrumMaster & Agile Coach Layoffs）](https://www.humanizingwork.com/making-sense-of-the-scrummaster-agile-coach-layoffs/)
  - なぜ起きるか: 定型運営が可視化され「これがSMの仕事ならAIで代替できる」と経営に判断されやすい（"What's dying is the Scrum Master as ceremony facilitator and impediment logger"）。
- **S3｜SM需要の縮小を示す定量シグナル。** SM面接ガイドのDL数が2022年 2,428→2024年 1,236 へほぼ半減。入門SMクラスの受講者比率は2020年 49%→2021年 26%→2022年 24%→2023年 17%→2024年 5%未満、2025年に公開講座取りやめの講師も。求人でも "Scrum Master" 表記を "Team Coach"/"Enterprise Coach" に置換する動き。
  - 出典: [Age-of-Product（Scrum Master: Is an Era Coming to an End?）](https://age-of-product.com/scrum-master-decline/) ／ [Humanizing Work（Agile Jobs Are Vanishing）](https://www.humanizingwork.com/agile-jobs-are-vanishing/)
  - なぜ起きるか: 定型業務の自動化と役割の統合が同時に進み、入門〜定型レイヤの需要が先に縮む。
- **S4｜超少人数×AIエージェントのチームでは専任SMを置かない構成が現実化。** 「AIエージェントが進捗追跡・タスク配分・フィードバック分析を担い、専任スクラムマスターやデータアナリストの必要性を減らす」。2〜3名の人間＋AIエージェントでコード/テスト/デプロイ/分析を横断的にこなす MVP 向けの構成が語られる。既存デスクリサーチのS1（3人＋50エージェント論）と地続き。
  - 出典: [AKF Partners（Engineering Team Sizes Are Evolving with Agentic AI）](https://akfpartners.com/growth-blog/engineering-team-sizes-are-evolving-rapidly-with-agentic-AI-platforms-the-limits-challenges-and-principles-we-must-consider) ／ [Scrum.org（AI-Augmented Scrum: When Half Your Team is Autonomous Agents）](https://www.scrum.org/resources/blog/ai-augmented-scrum-framework-when-half-your-team-autonomous-agents) ／ [The Bonsai Labs Dispatch（3-Person Team + 50 AI Agents）](https://medium.com/the-bonsai-labs-dispatch/the-next-10-person-startup-is-actually-a-3-person-team-50-ai-agents-7f6c8b1c4a6a)
  - なぜ起きるか: 少人数では専任の調整役を置く固定費が重く、定型調整をAIに寄せる誘因が強い。
- **S5｜SMに求める価値が「調整・管理」から「AI活用コーチング/オーケストレーション/判断」へ移行し、リスキリングの受け皿（認定）も生まれている。** Scrum.org「Professional Scrum Master – AI Essentials（PSM-AI Essentials）」、Scrum Alliance「AI for Scrum Masters」マイクロクレデンシャルなど。SMは「チームにAIとの働き方（有効なプロンプト・AI出力の批判的評価・ワークフロー統合）をコーチする」役へ。
  - 出典: [Scrum.org（Launches New AI Training for Scrum Masters）](https://www.scrum.org/resources/scrumorg-launches-new-ai-training-scrum-masters) ／ [Scrum Alliance（AI for Scrum Masters microcredential）](https://www.scrumalliance.org/microcredentials/ai-for-scrum-masters) ／ [Cprime（From Scrum Master to AI Enabler）](https://www.cprime.com/blog/agile-practitioners-embracing-ai-from-scrum-master-to-ai-enabler/)

## B. 課題（P）

- **P1｜定型業務が消え、「目に見える価値」を示せないSMが最初に切られる。** 立ち上げ運営・カードの移動・レトロの設定という可視作業＝仕事の実体だと見なされていると、それはAIで代替できてしまう。真のアジリティへの貢献が経営に理解されていない組織ほど、SM/アジャイルコーチが削減リストの上位に来る。
  - 出典: [Big Agile（role being cut）](https://big-agile.com/blog/why-the-scrum-master-role-is-being-cut-and-whats-actually-replacing-it) ／ [Humanizing Work（layoffs）](https://www.humanizingwork.com/making-sense-of-the-scrummaster-agile-coach-layoffs/) ／ [Scrum.org（The Job Got Cut. The Work Did Not.）](https://www.scrum.org/resources/blog/job-got-cut-work-did-not)
  - なぜ起きるか: 高価値な部分（信頼構築・文化変革・判断のファシリテーション）は成果が可視化されにくく、定型運営と混同されて評価される。
- **P2（核・接続）｜少人数×AIチームでは、AI出力の盲信（ラバースタンプ）を止める人間のファシリテーター/ガードレール役が構造的に不在化しやすい。** 専任SMを置かない構成が選ばれる一方、既存デスクリサーチのP8（少人数×AI速度で相互レビューが形骸化）と重なり、認知的降伏の歯止めが弱くなる。SMこそがこの歯止め役になりうるが、そのレイヤが先に削られている。
  - 出典: [AKF Partners（dedicated scrum master の必要性が減る）](https://akfpartners.com/growth-blog/engineering-team-sizes-are-evolving-rapidly-with-agentic-AI-platforms-the-limits-challenges-and-principles-we-must-consider) ／ 既存: `2026-07-19-desk-research-ai-reskilling.md` P8（相互レビューの形骸化）
  - なぜ起きるか: 調整コストを嫌う少人数チームが専任の「問い直し役」を置かず、AI出力への批判的吟味を担う構造的ポジションが消える。**「AI出力を盲信するな／人間が最終判断」という規範を誰が維持するか**が空白になる。
  - ※ この「歯止めが実際に効かず成果物ドリフトに至った」因果は本デスクリサーチでは一次証拠なし（推論）。一次検証の対象。
- **P3｜SM自身のリスキリング（AI活用の新スキル）が追いつかない。** 必要とされるのは AIリテラシー／エージェントのオーケストレーション（委任設計・エスカレーション判断）／プロンプトコーチング／**AI出力の批判的評価**／システム思考。だが儀式運営中心の従来型SMではこれらが不足しがちで、定型業務の自動化に価値の再定義が間に合わない。
  - 出典: [Cprime（AI Enabler）](https://www.cprime.com/blog/agile-practitioners-embracing-ai-from-scrum-master-to-ai-enabler/) ／ [Refonte Learning（Scrum Master in 2026: High-Demand Skills）](https://www.refontelearning.com/blog/scrum-master-in-2026-future-trends-high-demand-skills-and-career-outlook) ／ [Edstellar（10 Essential Scrum Master Skills for 2026）](https://www.edstellar.com/blog/scrum-master-skills)
  - なぜ起きるか: 従来のSM育成が儀式運営・ファシリテーション作法に偏り、AI協働・批判的評価の訓練を含んでこなかった。
- **P4｜SMの新しい高価値像「ガーディアン」は言語化・評価が難しく、切られやすい定型業務と混同される。** ガーディアン＝アジャンティックAIの出力が安全・正確・準拠・事業意図と整合しているかを担保し、リクエストの質・プロンプトの堅牢性・AI出力の信頼性・リワーク削減・リスク低減・全社AI戦略との整合に集中する役。「AI出力を盲信するな」という批判的思考の担保と、異議を言える心理的安全性の維持が中核。
  - 出典: [Scrum.org（Ethical AI in Agile: Four Guardrails Every Scrum Master Needs）](https://www.scrum.org/resources/blog/ethical-ai-agile-four-guardrails-every-scrum-master-needs-establish-now) ／ [Medium/Jakub Giza（Scrum Masters — the Guardian role is your future）](https://medium.com/@giza.jakub/scrum-masters-the-guardian-role-is-your-future-41608c0fc9fe) ／ [Scrum.org（AI Is Rewiring Scrum Teams, But Not Scrum — David Sabine）](https://www.scrum.org/resources/blog/ai-rewiring-scrum-teams-not-scrum)
  - なぜ起きるか: 「防いだ事故」は数えられず、ガーディアンの成果は不可視。ROIを示しにくいため定型運営と一括りに評価される。

## C. 課題のクラスタ

- **C1 役割の空洞化（定型自動化 → 職の消失）**: P1・P3 — 可視の定型業務がAIに移り、価値を再定義できないSMが職を失う。
- **C2 歯止めの不在（少人数×AIでガードレール役が消える）**: P2 — 認知的降伏を止める人間のファシリテーター/批判的吟味役が構造的に不在化する。既存プロジェクトのC3（累積と波及）に直結する新しい探索域。
- **C3 価値の不可視（ガーディアンの評価困難）**: P4 — 高価値な役割ほど成果が見えず、切られやすい定型業務と混同される。

> C2 の「歯止めが効かず成果物ドリフト・顧客混乱に至る」因果は本デスクリサーチでは一次証拠を確認できていない（既存プロジェクトの C3 と同じく推論を含む）。一次検証の対象とする。

## D. リスキリングで価値が上がるスキル（SM向け・示唆）

- **AI出力の批判的評価（目利き）＋チームへのコーチング**（有効なプロンプト設計・AI出力の吟味・ワークフロー統合の指導）。既存デスクリサーチの D（taste／評価が新たなボトルネック）と一致し、SMはこれを**チーム規範として広める**ハブになりうる。
  - 出典: [Scrum.org（AI Training for Scrum Masters）](https://www.scrum.org/resources/scrumorg-launches-new-ai-training-scrum-masters) ／ [Cprime](https://www.cprime.com/blog/agile-practitioners-embracing-ai-from-scrum-master-to-ai-enabler/)
- **エージェントのオーケストレーション**（委任設計・自律プロセス管理・エスカレーション判断）と**予測的フロー分析**（ボトルネック/ベロシティ・ドリフト検知）。
  - 出典: [ScaledAgile](https://scaledagile.com/blog/ai-empowers-scrum-masters/) ／ [Refonte Learning](https://www.refontelearning.com/blog/scrum-master-in-2026-future-trends-high-demand-skills-and-career-outlook)
- **人間固有スキル**（対立解決・「空気を読む」・心理的安全性・倫理的監督）はAIで代替されず、むしろ希少価値が上がる（"human empathy remains your competitive advantage"）。
  - 出典: [Scrum.org（AI Taking My Job?）](https://www.scrum.org/resources/blog/scrum-master-ai-taking-my-job) ／ [Edstellar](https://www.edstellar.com/blog/scrum-master-skills)

## E. 誠実な但し書き

- SM関連は**実務ブログ・研修ベンダー・認定機関のマーケ色が強い出典**が多い（scrum.org, scaledagile, cprime, refonte, 各研修サイト）。方向性の傍証にとどめ、確信度を上げすぎない。査読論文は本トピックでは乏しい。
- 「70%自動化」「準備60%削減」「3倍速」等の数値は**ベンダー/実務メディア由来の主張**で、独立検証された統計ではない。オーダー感の把握にとどめる。
- 縮小の定量（DL 2,428→1,236、受講 49%→<5%、Capital One 1,100ロール）は Age-of-Product/Humanizing Work という特定アナリストの集計で、業界全体の代表性は限定的。一方で「アジャイル実践は依然86%以上・Scrum採用81–87%」という反対向きのデータもあり、**役割の消滅ではなく再編/二極化**と読むのが妥当。
- WebFetch がボット保護で 403 のため一次本文を直接確認できず、検索スニペットの引用に依存した。数値・固有名は一次本文で再確認する必要がある（次アクション）。
- 本資料は「AI時代のSM一般」の傾向であり、「2名＋専門エージェントの特定チームのSM（不在含む）が実際にそう行動した」一次証拠ではない。→ 起票は確信度3-4に留める。
