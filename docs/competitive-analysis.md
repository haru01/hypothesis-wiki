# 競合分析と差別化の論点 — 仮説検証Wiki

> 作成日: 2026-07-18 ／ 方法: `deep-research` 2ラウンド（5角度の並列Web検索→出典取得→3票の敵対的検証→統合）。
> ラウンド1は全エージェントを Opus 4.8、ラウンド2は Scope/Synthesize=Sonnet 5・Search/Fetch/Verify=Haiku 4.5 で実行。
> **本メモは競合の一次ページ／READMEに基づく相対マップであり、有効性の第三者検証ではない。**
> 併読: [../projects/self/sources/2026-07-16-desk-research-corporate-hypothesis-testing.md](../projects/self/sources/2026-07-16-desk-research-corporate-hypothesis-testing.md)（方法論の系譜＝Blank/Ries/Strategyzer/Torres/Mom Test/Camuffo は調査済み）。

## 0. 結論（ひとこと）

**仮説検証Wiki は「①LLMネイティブなプレーンテキスト/Git/Obsidian の規約統治型Wiki」×「②リーンスタートアップ仮説検証の CPF→PMF ステージゲート」×「③証拠に機械的に強制紐づけされる単一の1〜10確信度」の三点の交差点に立つ。この交差点をまるごと占める既存プロダクトは、2ラウンドの調査で確認されなかった。**
ただし三要素は**個別には既存**（①=Karpathy LLM Wiki 派生、②=Ash Maurya/GLIDR、③=Strategyzer の証拠→仮説バインディング＋学術の EviBound）。新規性は「組み合わせ」と、**とりわけ③の"単一の物差し"を全記録の背骨にする点**にある。

## 1. 競合マップ（ラウンド1・確信度high中心）

| 競合 | 系統 | 重なる核 | 決定的な違い | 出典 |
|---|---|---|---|---|
| **LEANSpark / LEANSTACK**（Ash Maurya） | ドメインSaaS（軸A/C）。**最も近い単一競合** | AIで実験設計・BMストレステスト・進捗追跡。「何を信じ/検証し/証拠が語るか」を追跡。3段階の Continuous Innovation Framework | 独自AI SaaS。プレーンテキスト/Git/Obsidian層なし | leanstack.com, leanfoundry.com/ci-framework |
| **GLIDR**（旧LaunchPad Central、Steve Blank系） | ドメインSaaS（軸A/C） | 「AI Co-Founder」。成功基準つき実験プランをAI生成、仮説に証拠を紐づけ検証/棄却する"エビデンスベース・イノベーション" | canvas中心＋アサンプションマッピングUI。ページ上に1〜10確信度なし。ファイルベースでない | glidr.io/product-discovery-validation |
| **Strategyzer** | 方法論の源流（軸A） | 本Wikiの**テストカード/ラーニングカードの直接の出典**。Learning Card が学びを仮説に紐づけ | 確信度は**数値でない**（重要度×証拠の2値／定性ティア Directional-Moderate-Strong／Valid-Invalid-Unknown）。慣行であり機械強制でない | strategyzer.com/library/the-learning-card |
| **Aurelius**（UXリサーチリポジトリ） | ドメイン隣接（軸A） | 生データ→key insight→recommendation→action の証拠連鎖 | 確信度メトリクスも仮説検証もステージゲートも無い。「洞察の捕捉・整理」モデル | aureliuslab.com/features |
| **Icanpreneur** | AI顧客開発（軸C） | 「AI共同創業者」。合成/AI主導インタビュー→洞察→ペルソナ→意思決定テスト→GTM を一気通貫 | クローズドなSaaSワークフロー | icanpreneur.com |
| **SyntheticUsers** | AI顧客開発（軸C） | AIによる合成ユーザーインタビュー | 検証手法の一部品。蓄積・確信度層でない | syntheticusers.com |
| **Karpathy「LLM Wiki」gist** | アーキテクチャ源流（軸B） | **3層（raw/wiki/schema）の直接の出典**。RAGとの対比も共有 | アイデアファイル。ドメイン・確信度・ステージなし | gist.github.com/karpathy/442a6bf… |
| **claude-obsidian** | LLMネイティブPKM（軸B） | 「自己組織化AIセカンドブレイン」。**明示的にKarpathyパターン派生**。`.raw/`着地→`/wiki-ingest`抽出→index/log自動更新 | 汎用PKM。確信度・仮説検証・ADR・ステージなし | github.com/AgriciDaniel/claude-obsidian |
| **obsidian-wiki** | LLMネイティブPKM（軸B） | CLAUDE.md/AGENTS.md＋frontmatter＋Git の同一基盤を多エージェントへ一般化。信頼性は `extracted/inferred/ambiguous` タグ＋lint | 汎用PKM。**自己記述で "no confidence scoring / no hypothesis validation / no ADR"** | github.com/ar9av/obsidian-wiki |

## 2. 追加リサーチで判明したこと（ラウンド2）

**Gap 2: 仕様駆動開発ツール（Spec Kit / Tessl / Kiro）** — アーキテクチャ的に本Wikiに最も近い隣接領域。
- **GitHub Spec Kit** = Constitution→Specification→Planning→Tasks の型付きMarkdown4フェーズ＋逐次ゲート。**35以上のエージェントに対応**（インストール時にエージェント別ディレクトリへコマンドを書き込む agent-agnostic 設計）。v0.13.0 は 2026-07-17 付でごく最新。出典: github.com/github/spec-kit
- **Tessl** = 要件収集→Markdown仕様→**人間承認ゲート**→実装・全要件充足の検証、の4段階。`[@test]` 構文でテストを仕様に紐づけ。出典: docs.tessl.io
- **共通の空白**: どのツールにも**確信度・信念強度のスコアリングや仮説検証メカニズムは無い**（＝本Wikiの③は spec-driven 界隈にも存在しない）。

**Gap 4: 「証拠なしに状態遷移を許さない」機械的ゲートの実例** — 学術レベルで実在。
- **EviBound**（arXiv 2511.05524）= Phase 4（実行前の契約チェック）＋Phase 6（実行後の成果物チェック）の**二段階ゲート**と、成功を証明する成果物を定義する「**エビデンス契約**」。本Wikiの「確信度変更は必ずACT/DECに紐づける」不変ルールと**概念的に同型**。ただし**商用でなく学術プロトタイプ**で、「0%ハルシネーション」等の強い定量主張は検証で棄却。

**現実的な限界（重要な傍証）** — Thoughtworks の Birgitta Böckeler による Kiro/spec-kit/Tessl 実地評価（2025-10, martinfowler.com）:
- **「エージェントは既存クラスを記述した構造化ノートを無視し、新規仕様として全部再生成して重複を作った」「ウィンドウが大きくてもAIがそこにある全てを適切に拾うとは限らない」**。
- 含意: **規約に書いた＝守られる、ではない。** 型付きMarkdown＋規約層という構造的厳格さだけでは実行信頼性は保証されない。本Wikiの `/lint`・強制紐づけが"実際に効くか"は要検証。

## 3. 差別化の論点（本メモの主眼）

### 3-A. 独自で、守り・磨くべき（＝競合に一貫して欠落）
1. **単一の1〜10確信度を全記録の背骨にする**。Strategyzer=Valid/Invalid/Unknown＋定性ティア、GLIDR=露出なし、Aurelius=なし、spec-driven系=なし。**"証拠の強さを1本の数直線で表し、次に検証すべき仮説（重要×確信度低）を機械的に選べる"**のは調査範囲で本Wikiのみ。→ **旗印にすべき第一の軸。**
2. **証拠への機械的な強制紐づけ（勘で動かさない不変ルール）**。競合の証拠→仮説バインディングは概ね"テンプレ上の慣行"。**"証拠レコードなしにステータス・確信度を変えられない制約"**という思想は、学術（EviBound の二段階ゲート／エビデンス契約）では実在パターンとして検証済みだが、**商用の仮説検証ツールでの機械強制は確認されなかった**。→ ここが最も薄い空白。
3. **三要素の同時成立**（①×②×③）。個々でなく組み合わせが立ち位置。

### 3-B. あって当たり前（磨いても差別化にならない＝地力として持てばよい）
- **LLM Wiki の3層アーキテクチャそのもの**（Karpathy 由来。claude-obsidian / obsidian-wiki が独立実装済み）。
- **テストカード/ラーニングカード**（Strategyzer 由来）、**「AI Co-Founderが証拠で仮説検証」思想**（GLIDR/LEANSpark）。
- **型付きMarkdown＋規約層＋逐次ゲート**（Spec Kit / Tessl / Kiro が実装済み）。
- **ステージゲート（CPF→PMF）** も Ash Maurya CIF（3段階）や Lean LaunchPad と重なる。→ **差別化の主役にはしにくい。**

### 3-C. 弱点・埋めるべき
1. **「規約を守らせる」実効性**。Böckeler 評価が示す通り、エージェントは構造化参照を無視して重複生成する。**"CLAUDE.mdに書いた不変ルールが実際に強制されているか"** を検証・可視化する仕組み（`/lint` の網羅性、確信度変更の証拠リンク検査）を本気で作らないと、③②の売りが"絵に描いた餅"になる。**最優先の弱点。**
2. **単一エージェント/Claude Code 特化**。obsidian-wiki は Cursor/Codex/Gemini/Kiro など多エージェント、Spec Kit は35+に対応。本キットの「所有・可搬」を旗印にするなら、**agent-agnostic 化**（AGENTS.md 併存など）が論点。
3. **確信度の主観性の裏打ちが弱い**。1〜10は結局AI/人間の判断。インタビューは機械検証しづらく、EviBound 的な"機械検証可能な成果物での裏打ち"が効きにくい。**"確信度の付け方の規律"（誰が・何を根拠に・どう反証したか）を型で縛る**のが差別化の深掘りポイント。
4. **効果の第三者検証がゼロ**（本キット含め全競合）。ドッグフーディング（self）を超えた実案件での効果実証が、いずれ最大の説得材料になる。

### 3-D. 戦う軸の推奨（優先順）
1. **「確信度という単一の物差し × 証拠への強制紐づけ」を前面に**（3-A①②）。最も空白で、最も"この規律が要る"という課題（偽の確証・散逸）に直結する。
2. **「規約が実際に守られる」実効性で裏打ち**（3-C①）。売り文句でなく仕組みで示す。
3. **「プレーンテキスト＋Git＋所有・監査可能」は魅力的だが、業界言説での裏付けが今回取れなかった**（Gap 5 は確証ゼロ）。**主張として出す前に裏取りが要る**。可搬性・ロックイン回避・LLMとの相性を、一次的な言説（local-first ムーブメント等）で補強してから旗に掲げる。

## 4. 誠実な但し書き

- **「棄却（refuted）＝実在しない」ではない**。ラウンド2は Haiku 検証が「不確かなら棄却」に振れ、Gap 1/3/5 の主張が軒並み 0-3〜1-2 で落ちた（確証6 : 棄却19 の非対称）。**"今回の情報源・主張の組み立てが検証基準を満たさなかった"**にとどまる。Gap 1・3・5 は**事実上未解決**。
- ラウンド1で棄却された"重なりの誤認"2件（誠実さのため明記）:
  - ❌ Strategyzer Test Card の4フィールドが本Wikiのテストカード（目的/方法/指標/成功基準）と1:1一致 → **0-3で棄却**（構造は近いが厳密一致でない）。
  - ❌ Karpathy gist が Ingest/Query/Lint という操作名を定義 → **0-3で棄却**（gist にその操作名はない）。
- **時点情報**: LEANFoundry は 2026-06-25 に retiring→leanspark.ai へ統合（枠組みは存続）。Karpathy gist は 2026-04、Spec Kit は日々更新。**機能の主張は急速に陳腐化しうる。**
- ソースは大半が一次ベンダーページ／README（自己ポジショニングに権威的だがマーケ色あり）。「確信度スケールが無い」等の不在系主張は機能ページから絶対証明できない。

## 5. 未解決の問い（次のリサーチ候補）

1. **UXリサーチ／ディスカバリー系（Dovetail・Condens・Productboard・Maze 等）** が確信度指標／強制的エビデンス紐づけ／ステージゲートのいずれかを露出しているか（Gap 1 未解決）。※ Dovetail AI に確信度スコアリングが無いという主張は棄却＝断定不可。
2. **LEANSpark の内部データモデル** — 数値確信度を持つか、検証データをプレーンテキスト/Git へエクスポート可能か。※ ラウンド2で「7次元 0-10 スコアリングを持つ／持たない」双方の主張が棄却。**最も近い競合の肝が依然不明**。
3. **合成ユーザー／AI共同創業者系**（SyntheticUsers・Listen Labs・Outset 等）が単発インタビュー生成を超えて**証拠蓄積・確信度管理**まで踏み込むか（Gap 3 未解決）。
4. **EviBound 以外に、商用レベルで「証拠なしに仮説ステータスを変えられない」を機械強制するツール**は実在するか（Gap 4 の商用側 未解決）。
5. **「プレーンテキスト＋Git＋LLMネイティブ」の持続的差別化論**の業界言説での裏付け（Gap 5 未解決＝3-D③の前提）。
