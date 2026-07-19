# デスクリサーチ: AI時代のリスキリング（2名＋専門エージェント前提）

**データ種別: デスクリサーチ（二次情報・状況証拠）。一次インタビューは未実施。**
収集日: 2026-07-19 ／ 方法: WebSearch＋主要ソースの WebFetch による突き合わせ。各項目に出典URLを付す。
確信度の扱い: 二次情報のため起票する仮説は**確信度上限3-4**。不在系の主張（「〜が無い」）は断定しない。

対象＝**2名＋専門エージェントでプロダクトを作る「作り手」**（自分の専門・専門外を問わず）。
焦点＝**認知的降伏シナリオ**: 専門外は分からず丸投げ／専門内も次第に理解せず承認を繰り返す（ラバースタンプ化）
→ 成果物が累積的に歪む → 顧客の混乱、さらに歪みがAI文脈へ再流入し誤りを増幅。

---

## A. 状況・行動（S）

- **S1｜「2〜3名＋AIエージェント」の超少人数チームが現実化している。** VC James Currier「3人の優秀なチームで$100M+規模のソフト事業が可能」、Benhamou Global Ventures「10/100/3」フレーム、Cursor/Lovable の少人数×急成長が例。ソロ創業者は人件費の70-80%を月$200-500のAIツールに置換し資本効率10-50倍という論も。
  - 出典: [Fortune](https://fortune.com/2026/05/18/solo-founders-ai-automation-entire-teams-entrepreneurs/) ／ [The Bonsai Labs Dispatch (Medium)](https://medium.com/the-bonsai-labs-dispatch/the-next-10-person-startup-is-actually-a-3-person-team-50-ai-agents-7f6c8b1c4a6a) ／ [The VC Corner](https://www.thevccorner.com/p/the-billion-dollar-startup-formula)
- **S2｜AI生成コードが相当割合を占め、多くが十分なレビューを経ずに出荷される。** Ox Security 調査（オープンソース300プロジェクト中50件が全部/一部AI生成）で、AI生成コードは「機能的だが設計判断を欠く」パターン（教科書固執・リファクタ回避・過剰仕様・同一バグ再生成）が80-90%の頻度。
  - 出典: [InfoQ（Ox Security 調査の報道）](https://www.infoq.com/news/2025/11/ai-code-technical-debt/) ／ [DEV Community](https://dev.to/alexcloudstar/ai-generated-code-is-creating-a-technical-debt-crisis-nobody-is-auditing-4cjc) ／ [arXiv 2603.28592（野生のAI生成コード大規模実証）](https://arxiv.org/html/2603.28592v2)
- **S3｜週1以上GenAIを業務利用する知識労働者が一般化。** Microsoft/CMU 調査は週1以上利用者319名・936の実例を分析。
  - 出典: [Microsoft/CMU, CHI 2025 (Lee et al.)](https://www.microsoft.com/en-us/research/wp-content/uploads/2025/01/lee_2025_ai_critical_thinking_survey.pdf) ／ [ACM DL (CHI '25)](https://dl.acm.org/doi/full/10.1145/3706598.3713778)
- **S4｜人間の価値が「実行速度」から「判断・方向づけ・文脈」へ移りつつある。** MIT Sloan Management Review の第9回グローバルAI調査は、戦略的監督・倫理的ガバナンス・人×AIのオーケストレーション能力を最重要の人間スキルとする。
  - 出典: [Built In（MIT Sloan 調査の解説）](https://builtin.com/articles/ai-managers-job-skills) ／ [SocialLab](https://sociallab.ai/ai-orchestration-new-management-skill-2026/)

## B. 課題（P）

- **P1（核）｜理解せず承認する「ラバースタンプ化」。** 人はAI出力を十分理解しないまま承認し、監督が形骸化する。認知的疲労（大量の判断を捌くと精査が鈍る）と文化的圧力（システムの方が正しいという前提・異議を唱えにくさ）が原因。「HITL がしばしば人間でもループでもなくなる」。
  - 出典: [Cybermaniacs](https://cybermaniacs.com/cm-blog/rubber-stamp-risk-why-human-oversight-can-become-false-confidence) ／ [MIT Sloan MR（rubber-stamping回避）](https://sloanreview.mit.edu/article/ai-explainability-how-to-avoid-rubber-stamping-recommendations/) ／ [TianPan.co（HITL rubber stamp）](https://tianpan.co/blog/2026-04-15-human-in-the-loop-rubber-stamp)
  - なぜ起きるか: AIの出力速度・量に人のレビューが追いつかず、既定回答として受容してしまう。
- **P2｜オートメーション・バイアスは専門家でも避けられない。** 2023年の医療クロスオーバーRCTで全専門レベルの臨床医がバイアスに脆弱、誤りの約半分がAIの誤誘導に関連（AIは全体精度は改善）。
  - 出典: [Springer AI and Ethics（automation complacency）](https://link.springer.com/article/10.1007/s43681-025-00825-2) ／ [Mediate.com（human oversight の幻想）](https://mediate.com/the-meaning-and-illusion-of-human-oversight-of-ai/)
  - なぜ起きるか: 監視のみで能動的に関与しないと状況認識が下がり、失敗時の回復が遅れる。
- **P3｜過信は批判的思考を低下させる。** Microsoft/CMU（CHI 2025）: 62%が特に定型・低リスク作業で批判的思考が減ると回答。**AIへの信頼が高いほど批判的思考は減り、自己信頼が高いほど増える**。GenAI利用者は同一課題での成果の多様性が低下。
  - 出典: [Microsoft/CMU PDF](https://www.microsoft.com/en-us/research/wp-content/uploads/2025/01/lee_2025_ai_critical_thinking_survey.pdf) ／ [Gizmodo](https://gizmodo.com/microsoft-study-finds-relying-on-ai-kills-your-critical-thinking-skills-2000561788) ／ [Forbes](https://www.forbes.com/sites/larsdaniel/2025/02/14/your-brain-on-ai-atrophied-and-unprepared-warns-microsoft-study/)
  - なぜ起きるか: 認知的負荷を下げるほど自分で吟味しなくなる（metacognitive laziness）。
- **P4｜技能劣化（deskilling）は専門家でも起きる。** 使わない技能は萎縮。内視鏡医はAI併用後、AIオフ時の腺腫発見率が28%→22%へ低下。看護70%・医師77%が過依存による技能喪失を懸念。航空でも手動操縦技能の劣化が規制上の課題。
  - 出典: [AI For Human Expertise（領域横断の証拠）](https://aiforhumanexpertise.com/blog/deskilling-across-domains/) ／ [Springer（医療のdeskilling総説）](https://link.springer.com/article/10.1007/s10462-025-11352-1) ／ [Scientific American](https://www.scientificamerican.com/article/is-ai-ruining-our-skills-early-results-are-in-and-theyre-not-good/)
  - なぜ起きるか: 認知タスクを自動系に委ね続けると手続き的・認知的技能が反復されず衰える。
- **P5｜専門外の丸投げは「never-skilling」を招く。** 反省・批判的吟味なしにAI出力へ依存すると、そもそも必要な技能が最初から育たない（deskilling より深刻）。
  - 出典: [PMC（deskilling dilemma）](https://pmc.ncbi.nlm.nih.gov/articles/PMC12909220/) ／ [Springer（医療のdeskilling総説）](https://link.springer.com/article/10.1007/s10462-025-11352-1)
  - なぜ起きるか: 目利き（出力の良し悪しを判断する力）は自分で手を動かす経験からしか育ちにくい。
- **P6｜理解せず出荷した成果物は累積的に歪む（技術的・認知的負債）。** 自分で書かず深く理解していないコードを承認するたび「comprehension/intent debt」が積み上がる。AI技術的負債は「複利で増える（it compounds）」。
  - 出典: [InfoQ（Ox Security / Ana Bildea）](https://www.infoq.com/news/2025/11/ai-code-technical-debt/) ／ [arXiv 2603.22106（cognitive/intent debt）](https://arxiv.org/pdf/2603.22106) ／ [Tembo](https://www.tembo.io/blog/ai-technical-debt)
  - なぜ起きるか: 表層的にもっともらしい出力が設計上の欠陥を隠し、気づかぬまま冗長・歪みが蓄積する。
- **P7｜AI生成物の再流入は誤りを世代で増幅する（model collapse / feedback loop）。** AI出力がAIの入力に戻ると、統計的近似誤差が世代を経て複利的に増幅し、希少情報が消え出力が均質化・劣化する。
  - 出典: [Nature 2024（recursively generated data で崩壊）](https://www.nature.com/articles/s41586-024-07566-y) ／ [VentureBeat](https://venturebeat.com/ai/the-ai-feedback-loop-researchers-warn-of-model-collapse-as-ai-trains-on-ai-generated-content) ／ [IBM（model collapse とは）](https://www.ibm.com/think/topics/model-collapse)
  - なぜ起きるか: 歪んだ成果物がコンテキスト・データとして再投入されると、AIの現実認識がさらにずれる。
- **P8｜少人数化＋AI速度で相互レビュー・牽制が形骸化する。** 手動のピアレビューはAI生成コードの速度・量に追いつけず、主要防御として機能しにくくなる。2名では4-6名チームなら効いた相互チェックが構造的に消える。
  - 出典: [InfoQ](https://www.infoq.com/news/2025/11/ai-code-technical-debt/) ／ [arXiv 2607.07980（AI時代のコードレビュー 3100意見）](https://arxiv.org/pdf/2607.07980) ／ [arXiv 2601.21276（AI生成PRの品質とレビュー感情）](https://arxiv.org/pdf/2601.21276)
  - なぜ起きるか: レビュー容量（人手）が一定なのに生成速度だけ跳ね上がり、精査が追いつかない。

## C. 課題のクラスタ

- **C1 入口の罠（丸投げ・never-skilling）**: P1, P5 — 分からないまま/理解を放棄して承認し、目利きが育たない。
- **C2 侵食（過信 → 批判的思考低下 → deskilling）**: P2, P3, P4 — 使わない・吟味しない技能が個人の中で衰える。
- **C3 累積と波及（ドリフト → 再流入 → 顧客/AIの混乱、レビュー消失）**: P6, P7, P8 — 歪みが成果物に蓄積し、顧客とAI双方の混乱に波及する。相互レビューの消失がこれを止められない。

> 波及先の「**顧客の混乱**」は本デスクリサーチでは直接の一次証拠を確認できていない（C3は P6–P8 からの因果的推論を含む）。一次検証の対象とする。

## D. リスキリングで価値が上がるスキル（示唆）

- **分析的思考**（WEF 2025: 雇用主の7/10が最重要）、**AIリテラシー/AI・ビッグデータ**（90%が2030までに需要増と予測、最速成長スキル）、**創造的思考**・**レジリエンス/好奇心・生涯学習**。2030までに労働者の中核スキルの39%が変化。
  - 出典: [WEF Future of Jobs Report 2025 — Skills outlook](https://www.weforum.org/publications/the-future-of-jobs-report-2025/in-full/3-skills-outlook/) ／ [WEF（記事版）](https://www.weforum.org/stories/2025/01/future-of-jobs-report-2025-jobs-of-the-future-and-the-skills-you-need-to-get-them/)
- **オーケストレーション**（委任設計・ワークフロー設計・説明責任の維持・性能ガバナンス・エスカレーション判断）と**評価/目利き（taste）**。「Taste is the new bottleneck」。エージェント出力の評価はデバッグと違い領域専門性と文脈判断を要する。
  - 出典: [MIT Sloan（via Built In）](https://builtin.com/articles/ai-managers-job-skills) ／ [Designative（Taste is the new bottleneck）](https://www.designative.info/2026/02/01/taste-is-the-new-bottleneck-design-strategy-and-judgment-in-the-age-of-agents-and-vibe-coding/) ／ [SocialLab（orchestration）](https://sociallab.ai/ai-orchestration-new-management-skill-2026/)

## E. 誠実な但し書き

- 出典は査読論文（Nature, CHI, Springer）から一次ベンダー/ブログ（InfoQ, Medium, 各社ブログ）まで強度に幅がある。ブログ・オピニオンは方向性の傍証にとどめ、確信度を上げすぎない。
- 「相互レビューが必ず消える」「手段が存在しない」等の**不在系・断定は避ける**。本資料は一般的傾向であり、特定の作り手が実際にそう行動した一次証拠ではない。
- Microsoft/CMU PDF は本収集時にバイナリで直接本文抽出できず、62%等の数値は複数の独立報道（Gizmodo/Forbes 等）で三角測量した。
