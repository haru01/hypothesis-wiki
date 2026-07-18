# デスクリサーチ記録 — 企業活動における仮説検証の「状況・行動」と「課題」

> **データ種別**: デスクリサーチ（二次情報・状況証拠）。一次インタビューは未実施。
> ここに集めた出典は実在する文献・調査であり、**実データとして扱ってよい**（ただし
> 「顧客が実際にそう言った」一次証拠ではなく、文献が指摘する一般的傾向である点に注意）。
> このファイルは [[SELF-ACT-001]] の根拠。CPF仮説 [[SELF-H-001]]〜[[SELF-H-008]] の初期確信度3〜4の裏づけに使う。

実施日: 2026-07-16 ／ 方法: Web検索＋一次文献（書籍公式・学術論文・調査レポート）の突き合わせ

---

## A. 状況・行動（誰が・どんな状況で仮説検証をやるのか）

**S1. スタートアップ/新規事業チームが「建物の外に出て（get out of the building）」作る前に仮説を検証する**
Steve Blank の Customer Development は事業を Customer Discovery → Validation → Creation → Company Building に分け、最初の Discovery で「顧客は誰か・課題は何か・解決策は効くか」を建物の外でテストせよと説く。「No facts exist inside the building, only opinions（建物の中に事実はない、意見だけだ）」。
出典: https://steveblank.com/tag/customer-development/ ／ https://innovation.ucsd.edu/startup/startup-toolkit/Steve-Blank-CustDev.pdf ／ https://en.wikipedia.org/wiki/Customer_development

**S2. プロダクトトリオ（PM・デザイナー・エンジニア）が「継続的ディスカバリー」を回す**
Teresa Torres は (1) 毎週最低1人の顧客インタビュー (2) Opportunity Solution Tree で機会を構造化 (3) 作る前に前提を洗い出しテスト (4) 小さな実験 (5) トリオ全員が毎週関与、の5習慣を提唱。
出典: https://www.producttalk.org/getting-started-with-discovery/ ／ https://www.amazon.com/Continuous-Discovery-Habits-Discover-Products/dp/1736633309

**S3. テストカード/ラーニングカード/アサンプションマッピングで実験を設計・記録する**
Strategyzer（Osterwalder / David Bland『Testing Business Ideas』）は、キャンバス上の前提を Assumption Map（「重要度×エビデンスの薄さ」の右上を優先）で洗い出し、Test Card で「何が真であるべきか／どうテストするか／指標／成功基準」を明示、Learning Card で「We learned that… / Therefore we will…」と学びを意思決定に変換する。
出典: https://www.strategyzer.com/library/validate-your-ideas-with-the-test-card ／ https://www.strategyzer.com/library/testing-business-ideas-book-summary

**S4. インタビューは「セット（3〜5人）→整理→仮説更新→次のセット」の反復で回す（実務の粒度）**
才流の課題探索インタビューは「1セット＝3〜5名＋内容整理」で実施し、共通点・相違点を整理して仮説をブラッシュアップし2セット目・3セット目と反復する。目的は「自社の思い込み」を顧客の生声で排除すること。
出典: https://sairu.co.jp/method/83714/ ／ https://esaura.jp/ux-blog/how-to-test-your-business-idea

**S5. Lean Startup の Build–Measure–Learn＋MVP＋イノベーション会計で進捗を測る**
Eric Ries は最小労力で仮説を試す MVP を作り、Value/Growth 仮説に紐づく actionable metrics を測り pivot or persevere を判断する。イノベーション会計は「①MVPでベースライン→②実験でチューニング→③進捗が出なければピボット」の3段階。
出典: https://en.wikipedia.org/wiki/Lean_startup ／ https://www.amazon.com/Lean-Startup-Entrepreneurs-Continuous-Innovation/dp/0307887898

**S6. 実際のツールは散在型（スプレッドシート/ドキュメント/Slack/フォルダ）で成果が中央に集約されにくい**
UXリサーチ実務ではインサイトが「ファイル・忘れられたフォルダ・無数のSlackメッセージ」に散らばり知識が失われ作業が重複する。これを防ぐため ResearchOps が中央リポジトリ（single source of truth）を構築する、というのが標準的問題認識。
出典: https://www.nngroup.com/articles/research-repositories/ ／ https://www.nngroup.com/articles/research-ops-101/

**S7. 大企業はDX/イノベーション部門でワークショップ・MVPパイロット・研修を回す（ただし「イノベーション演劇」化しやすい）**
大企業では研修やパイロットが phase 1 で停滞し「30人を研修に送るだけでは innovation は生まれず innovation theater に陥る」。経営の本気度と構造改革がないと signalling に終わる。
出典: https://medium.com/result/thoughts-on-meeting-eric-ries-and-moving-corporates-from-innovation-theater-a6347cc56381 ／ https://jbpress.ismedia.jp/articles/-/59152

**S8. 大企業の新規事業担当は検証リソース・インタビュー費用・顧客接点の確保にそもそも苦労する**
才流の整理では大企業は「仮説検証を進めるリソースすら割けない」「顧客インタビューの費用すらままならない」状況に陥りがちで、顧客に会うために既存事業の営業への掛け合いが要るなど検証の入口でつまずく。
出典: https://sairu.co.jp/method/94443/ ／ https://sairu.co.jp/method/98574/

---

## B. 課題（よくある失敗・ペイン／なぜ起きるか）

**P1. 「ニーズがない」まま作ってしまう（検証の飛ばし）** — CB Insights（閉鎖431社）で失敗要因の43%が poor product-market fit。70%の「資金枯渇」は結果であり真因でない。→ 需要を検証する前に構築へ進むため。
出典: https://www.cbinsights.com/research/report/startup-failure-reasons-top/

**P2. 課題検証を飛ばしてソリューションに飛びつく** — 社内の意見（opinions）を検証済み事実と取り違え、顧客の課題を確かめずに解決策を作る（S1「建物の中に事実はない」と表裏）。→ 作りたい欲求が先行するため。
出典: https://steveblank.com/tag/customer-development/

**P3. 確証バイアス（自説を支持する証拠だけ集め反証を軽視）** — リーン実験の典型失敗。「エゴと確証バイアスが結果の客観的解釈を曇らせる」。需要・価値・効果を過大評価させる。→ 仮説への感情的コミットが客観性を歪めるため。
出典: https://www.forbes.com/sites/groupthink/2014/04/28/five-pitfalls-of-running-lean-startup-experiments/ ／ https://www.linkedin.com/advice/1/how-do-you-avoid-confirmation-bias-cognitive-dissonance

**P4. インタビューが誘導的・「褒め言葉」狙いになり、真実でなく賛同を集める** — The Mom Test（Rob Fitzpatrick）。「良いと思う？」「使う？」「いくら払う？」はルール違反で、得られるのは compliments・hypothetical fluff・wishlist の悪いデータ。過去の具体的事実を聞き8割は相手に話させよ。→ 作り手が Yes を聞きたいため質問が無意識に validation 狙いになる。
出典: https://www.momtestbook.com/ ／ https://blog.uxtweak.com/the-mom-test/

**P5. 反証不可能・曖昧な仮説（測定可能な成功基準がない）** — Strategyzer自身が「大量に話したのに学べなかった、バラバラだった」と告白し Test Card で「仮説/テスト方法/指標/成功閾値」を事前明示させた。→ 「何が真なら成立か」を指標・閾値で事前に言語化しないため。
出典: https://www.strategyzer.com/library/validate-your-ideas-with-the-test-card ／ https://www.linkedin.com/advice/3/what-common-mistakes-you-make-lean-startup-methodology

**P6.（★最も根拠が厚い）学び・意思決定の根拠が記録されず散逸・属人化する** — Strategyzer は Learning Card を導入。NN/g は「インサイトがファイル・フォルダ・Slackに散らばり失われ、作業が重複し、新メンバーは文書化された知見でなく tribal knowledge に頼る」と指摘。才流も「属人化させず再現性を持たせる仕組みができていない」を主要課題に挙げる。**独立した複数の一次情報（Strategyzer・NN/g・才流）が同じ問題を指摘**。→ 構造化された記録・単一の集約先がないため。
出典: https://www.nngroup.com/articles/research-repositories/ ／ https://www.strategyzer.com/library/validate-your-ideas-with-the-test-card ／ https://sairu.co.jp/method/94443/

**P7. 定性データの解釈が主観的・場当たり的で n数の扱いを誤る（過信/軽視）** — Torres は「結論だけ見せる（辿り着き方を見せない）のでステークホルダーに簡単に否定される」を典型ミスと指摘。Nielsen の「5ユーザー」は単一・均質群の問題発見にのみ有効で定量的一般化には使えない（定量は約40人〜）。→ 定性/定量の役割混同と合成（synthesis）の型の不在。
出典: https://www.nngroup.com/articles/5-test-users-qual-quant/ ／ https://www.producttalk.org/getting-started-with-discovery/

**P8. バニティメトリクスに頼り進捗を測れず経営層に説明・合意形成できない（イノベーション会計の不在）** — 総売上・ユーザー数・PVは自然に増える vanity metrics で事業モデルの前進を示さない。新規事業は既存KPIがほぼゼロで通常会計では進捗を評価できず経営層説明が困難。→ 既存KPIが機能せず増えるだけの数字を進捗と誤認するため。
出典: https://en.wikipedia.org/wiki/Lean_startup ／ https://www.growthjockey.com/blogs/innovation-accounting-lean-startup

**P9. 検証エビデンスが揃う前に拡大する（早すぎるスケール）** — Startup Genome（3,200社超）で失敗の最大要因は premature scaling、対象の約74%が該当。runway を早く消費し組織的・心理的コミットが増え機動力（方向転換能力）を失う。→ 過信・成長圧力で fit の証拠より先に投資し後戻りしにくくなる。
出典: https://s3.amazonaws.com/startupcompass-public/StartupGenomeReport2_Why_Startups_Fail_v2.pdf ／ https://startupgenome.com/insights/a-deep-dive-into-the-anatomy-of-premature-scaling

**P10. 大企業で「イノベーション演劇」化し検証が成果に結びつかず再現もされない** — innovation theater＝イノベーションが起きているように見せるが事業インパクトのない活動。研修・少数MVPで止まる。日本でも既存KPI達成者が評価されリスクある挑戦のインセンティブがなく再現性・仕組み化が欠ける。→ 評価・権限・予算が既存事業向けのまま、検証を継続・再現する仕組みがないため。
出典: https://medium.com/result/thoughts-on-meeting-eric-ries-and-moving-corporates-from-innovation-theater-a6347cc56381 ／ https://jbpress.ismedia.jp/articles/-/59152

**P11. ディスカバリーを「初期の一度きり」で終わらせる** — Torres「10本インタビューしてその後は顧客と二度と話さない」が典型ミス。市場・課題の変化に追随できない。
出典: https://www.producttalk.org/getting-started-with-discovery/

---

## C. 課題の3クラスタ（CPF仮説設計の軸）

- **入口（やらない/飛ばす）**: P1・P2・P8・P10
- **やり方（検証の質）**: P3・P4・P5・P7
- **記録・継続（学びが残らない）**: P6・P9・P11 ← **P6 は独立2系統以上の一次情報が一致し最も根拠が厚い**

---

## D. 引用フレームワーク・文献

- Eric Ries『The Lean Startup』 https://en.wikipedia.org/wiki/Lean_startup
- Steve Blank / Customer Development https://steveblank.com/tag/customer-development/
- David J. Bland & Alexander Osterwalder『Testing Business Ideas』(Strategyzer) https://www.strategyzer.com/library/testing-business-ideas-book-summary
- Teresa Torres『Continuous Discovery Habits』 https://www.producttalk.org/getting-started-with-discovery/
- Rob Fitzpatrick『The Mom Test』 https://www.momtestbook.com/
- Clayton Christensen, Jobs to Be Done https://hbr.org/2016/09/know-your-customers-jobs-to-be-done
- Camuffo, Cordova, Gambardella, Spina "A Scientific Approach to Entrepreneurial Decision Making" *Management Science* 2020（116社RCT。科学的＝仮説を厳密に検証するチームの方が成果が高くピボット率も高い＝反証を受け入れやすい） https://pubsonline.informs.org/doi/10.1287/mnsc.2018.3249 ／ https://gwern.net/doc/economics/2019-camuffo.pdf
- CB Insights "Why Startups Fail" https://www.cbinsights.com/research/report/startup-failure-reasons-top/
- Startup Genome "Premature Scaling" https://s3.amazonaws.com/startupcompass-public/StartupGenomeReport2_Why_Startups_Fail_v2.pdf
- Nielsen Norman Group（リサーチリポジトリ／定性 vs 定量サンプル） https://www.nngroup.com/articles/research-repositories/ ／ https://www.nngroup.com/articles/5-test-users-qual-quant/
- 才流（大企業の新規事業／課題探索インタビュー） https://sairu.co.jp/method/94443/ ／ https://sairu.co.jp/method/83714/
