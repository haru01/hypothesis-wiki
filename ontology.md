<!-- 生成物: gen_ontology_doc.py による ontology.yaml からの機械生成。手編集禁止。
     `python3 tools/gen_ontology_doc.py` で再生成する。正本は ontology.yaml。 -->

# 仮説検証Wiki オントロジー

レコードの**型**（エンティティ）と、レコード間の**型付きリンク**（関係）、および検証の**状態機械**を定義する。正本は [ontology.yaml](ontology.yaml)。ツール（`tools/hwlint.py`・`tools/gen_views.py`）は `tools/ontology.py` 経由でここを読む。

## エンティティ（レコード種別）

| 種別 | 名称 | ディレクトリ | サブタイプ（frontmatter `type`） |
|---|---|---|---|
| `H` | 仮説 | `wiki/hypotheses/` | 状況・行動仮説・課題仮説・ソリューション仮説・市場スケール仮説・自分たち仮説 |
| `TEST` | 実験計画 | `wiki/tests/` | interview・demo・survey・mvp-test・desk-research・self-reflection |
| `LEARN` | 学び | `wiki/learnings/` | interview・demo・survey・mvp-test・desk-research・self-reflection |
| `DEC` | 意思決定 | `wiki/decisions/` | stage-transition・pivot・persevere・rollback・kill |

**各種別の役割**:

- **`H`（仮説）** — 反証可能な仮説文。追記専用の確信度履歴テーブルを正本として持ち、TEST/LEARN/DEC から検証・更新される。事業の前提を1つずつ言語化した検証の起点。
- **`TEST`（実験計画）** — テストカード。検証前に記入する計画で、「動いて検証する(Act)→学ぶ(Learn)」の計画側として目的・方法・指標・成功基準・riskiest-assumption を宣言する。学び(LEARN)が紐づくまでは自由に直してよく、紐づいた後は下記 immutable の範囲だけを凍結する（後知恵バイアス防止）。検証後の学びは LEARN（別レコード）に積む。
- **`LEARN`（学び）** — 学習カード。検証後に新規作成する「実施して学びを得た」出来事。事実(observed)と解釈(inference)を分け、outcome（判定）と確信度更新を記録する。計画型は learns-from で TEST を参照し、回顧型（desk-research/self-reflection 等）は TEST を持たず自身が活動種別を名乗る。サブタイプは活動種別（TEST と同じ語彙）。sources で根拠となった生データ（不変層）を指し、確信度の根拠鎖を端まで辿れるようにする。
- **`DEC`（意思決定）** — ステージ移行・ピボット・撤退・巻き戻しなどの節目の判断。based-on で根拠の LEARN/TEST に結び、to-stage を持つ最新 DEC が現在ステージの正本になる。巻き戻しポイントと次の一手を残す。

### 凍結（不変ルール6）

実施済みレコードのうち**後から書き換えてはいけない範囲**の宣言。「実施済み」＝発火関係でそのレコードを指す相手が在ること。ここに挙がっていない部分（目的・方法・指標の補正、リンク追加、誤字修正）は実施後も直してよい。`check_testcard_immutable.py` と `hwlint.py` の `testcard-sections` がこの宣言を読む。

| 種別 | 発火（実施済みの判定） | 凍結する本文節 | 凍結する frontmatter キー |
|---|---|---|---|
| `TEST` | `learns-from` で指されている | `成功基準` | `riskiest-assumption` |

### frontmatter フィールド（スキーマ＝契約）

各レコードが持つ frontmatter キーの宣言。**必須の欠落は error、宣言に無いキーは warning** として `hwlint.py` の `check_fields` が検出する（`kind` の意味は `ontology.yaml` 冒頭のコメントが正本）。

**`H`（仮説）**

| フィールド | 必須 | kind | 語彙(enum-ref) |
|---|---|---|---|
| `id` | 必須 | id | — |
| `title` | 必須 | text | — |
| `short-title` | 省略可 | text | — |
| `type` | 必須 | subtype | — |
| `status` | 必須 | enum | `statuses` |
| `confidence` | 必須 | confidence | — |
| `stage` | 必須 | enum | `stages` |
| `importance` | 省略可 | importance | — |
| `derived-from` | 省略可 | relation | — |
| `leads-to` | 省略可 | relation | — |
| `addresses` | 省略可 | relation | — |
| `core` | 省略可 | flag | — |

**`TEST`（実験計画）**

| フィールド | 必須 | kind | 語彙(enum-ref) |
|---|---|---|---|
| `id` | 必須 | id | — |
| `title` | 必須 | text | — |
| `type` | 必須 | subtype | — |
| `date` | 必須 | date | — |
| `stage` | 必須 | enum | `stages` |
| `hypotheses` | 必須 | relation | — |
| `riskiest-assumption` | 必須 | text | — |
| `data` | 省略可 | enum | `data-kinds` |

**`LEARN`（学び）**

| フィールド | 必須 | kind | 語彙(enum-ref) |
|---|---|---|---|
| `id` | 必須 | id | — |
| `title` | 必須 | text | — |
| `type` | 必須 | subtype | — |
| `date` | 必須 | date | — |
| `stage` | 必須 | enum | `stages` |
| `learns-from` | 省略可 | relation | — |
| `hypotheses` | 必須 | relation | — |
| `outcome` | 必須 | enum | `outcomes` |
| `sources` | 省略可 | provenance | — |
| `data` | 省略可 | enum | `data-kinds` |

**`DEC`（意思決定）**

| フィールド | 必須 | kind | 語彙(enum-ref) |
|---|---|---|---|
| `id` | 必須 | id | — |
| `title` | 必須 | text | — |
| `date` | 必須 | date | — |
| `type` | 必須 | subtype | — |
| `based-on` | 省略可 | relation | — |
| `to-stage` | 省略可 | enum | `stages` |

### 仮説（H）サブタイプの価値連鎖上の役割

| サブタイプ | 役割 | 価値連鎖ラベル | 説明 |
|---|---|---|---|
| 状況・行動仮説 | customer | 状況・行動 | 想定顧客が今どんな状況に置かれ、実際にどう行動しているか（課題の手前の観察可能な事実）。「誰が・どんな文脈で・何をしているか」を捉える。 |
| 課題仮説 | problem | 切実な課題 | その顧客が抱える、対価を払ってでも解きたいほど切実な課題。行動の裏にある痛み。CPF/FPF の中心。 |
| ソリューション仮説 | solution | ソリューション | 課題を解く打ち手と、その独自の価値提案。addresses で対応課題に結ぶ。PSF/SPF の中心。 |
| 市場スケール仮説 | market | 市場スケール | チャネル・収益・コスト・主要指標が成立し反復可能にスケールするか。PMF の中心。個別購買（対価・WTP）は型にせず、ソリューション仮説を〈支払い〉証拠で検証する観点として扱う。 |
| 自分たち仮説 | team | 自分たち | なぜ自分たちがこの課題に取り組むのか、模倣困難な圧倒的優位性（Unfair Advantage）。FPF の一角。 |

## 付随物（attachments）

付随物は**新しいレコード種別ではない**。親レコードに従属する成果物で、独自のID体系を持たず（ファイル名 = 親レコードID + suffix）、置き場も親と同じディレクトリを使う。それでいて**関係（型付きリンク）には参加する**ので、`hwlint.py` がリンク切れ・型違反を検出でき、Obsidian のグラフにも本文 wikilink 経由で現れる。

レコード（エンティティ）と分けて持つのは正しさの要請である。ステム `<PREFIX>-TEST-NNN-script` には `-TEST-` が含まれるため、レコードとして読み込むと `records.py` の `entity_of` が `TEST` を返し、`"-TEST-" in stem` で書かれた箇所（board/list/index 生成・テストカード不変チェック）が付随物を実験計画として飲み込む。そのため読み取り層は `records` と `attachments` を別コレクションに保ち、**付随物は生成ビューに現れない**（board・list・index・relations のいずれも records だけを射影する）。関係インデックスも、始点・終点がレコードでない関係は恒久的に0件になるので節を出さない（「（該当なし）」と刻むと「そんな付随物は存在しない」という誤情報になる）。関係型の一覧そのものはスキーマの話なのでこのドキュメントが持つ。

| 付随物 | 名称 | 親 | ファイル名 | サブタイプ（frontmatter `type`） |
|---|---|---|---|---|
| `SCRIPT` | スクリプト | `TEST` | `wiki/tests/<親レコードID>-script.md` | problem-interview・solution-interview・demo |

- **`SCRIPT`（スクリプト）** — interview/demo の実験計画(TEST)の「方法」を現場の会話に落とした台本。/planning がテストカードと対で生成する。事前登録した反証条件・記録シートを載せ、観測をそのまま受け止める器になる。確信度は動かさない（学びは LEARN に積む）。

**`SCRIPT` の frontmatter フィールド**

| フィールド | 必須 | kind | 語彙(enum-ref) |
|---|---|---|---|
| `id` | 必須 | id | — |
| `title` | 必須 | text | — |
| `type` | 必須 | subtype | — |
| `script-for` | 必須 | relation | — |
| `hypotheses` | 省略可 | relation | — |

**`SCRIPT` のサブタイプと雛形**

| サブタイプ | 基にする雛形 | 説明 |
|---|---|---|
| problem-interview | [templates/problem-interview-script.md](templates/problem-interview-script.md) | 課題の実在・自認・実コストを過去の事実で聞く（CPF/FPF）。ソリューションは見せない・語らない。 |
| solution-interview | [templates/solution-interview-script.md](templates/solution-interview-script.md) | 提示物への反応・乗り換え・〈支払い〉を聞く（PSF/SPF）。 |
| demo | [templates/demo-script.md](templates/demo-script.md) | デモの司会・観察の台本（主に PSF）。作らずに価値の芯を当てる。 |

`hwlint.py` が検証すること: ファイル名と親レコードIDの対応（**error**）／`type` の語彙（**error**）／親を指す関係がファイル名から導いた親と一致するか（**error**）／親と共有する関係（`hypotheses` 等）が親の値の**部分集合**か（**error**）／親から付随物への相対mdリンクの有無（到達可能性）。

## 関係（型付きリンク）

各関係は frontmatter 配列と本文 wikilink の**二重表現**を持つ（`must-wikilink: true` のものは本文にも `[[…]]` を張る＝Obsidian グラフに辺を出すため）。

| 関係 | frontmatter | domain → range | cardinality | 逆方向(inverse) | 本文wikilink | 意味 |
|---|---|---|---|---|---|---|
| **派生元** | `derived-from` | H → H | 単一(one) | derives（派生先） | 必須 | この仮説が枝分かれした元の仮説（親は1つ）。ピボットや巻き戻しの再出発点を系譜として残し、なぜこの仮説に至ったかの履歴を辿れるようにする。過去向きのリンク。 |
| **因果先** | `leads-to` | H → H | 配列(many) | led-from（因果元） | 必須 | この仮説が成り立つと次に導かれる仮説（複数可）。状況→課題→ソリューション→市場という価値連鎖を前向きにつなぎ、list ビューの mermaid バリューチェーン矢印になる。derived-from が過去向きなのに対しこちらは前向き。 |
| **対応課題** | `addresses` | H（ソリューション仮説） → H（課題仮説） | 配列(many) | addressed-by（対応する価値） | 任意 | このソリューション仮説が解こうとする課題仮説（複数可）。打ち手と痛みの対応＝バリュープロポジションのフィットを表し、relations ビューのフィット表になる。始点と終点の型が限定される唯一の関係。フィット表は frontmatter から射影するため本文 wikilink は必須にしない。 |
| **検証対象** | `hypotheses` | LEARN/SCRIPT/TEST → H | 配列(many) | validated-by（検証活動） | 必須 | この実験計画(TEST)が狙う、または学び(LEARN)が確信度を動かした仮説（複数可）。TEST と LEARN の両方が始点になれ、同じ仮説群を指すことで「計画→結果」が1本に束なる。仮説側からは逆引き（検証活動）で「どの活動がこの仮説を検証したか」を辿れる。付随物のスクリプト(SCRIPT)も始点になれるが、台本が実際に当てる仮説は親 TEST の検証対象の部分集合でなければならない（発見型スクリプトは仮説を伏せるので空でよい）。 |
| **対象の実験計画** | `script-for` | SCRIPT → TEST | 単一(one) | script（スクリプト） | 必須 | このスクリプトが台本化した実験計画(TEST)。ファイル名（親ID + suffix）から導ける対応を frontmatter にも明示し、機械可読にする。付随物を始点とする唯一の関係で、親は必ず1つ。 |
| **実験計画** | `learns-from` | LEARN → TEST | 単一(one) | learnings（学び） | 必須 | この学びが実施した実験計画（テストカード）を1つ指す。計画(TEST)と結果(LEARN)を1対1で束ね、board ビューが「1実験＝計画＋学び」を1行にまとめる。回顧型（desk-research/self-reflection 等）は計画を立てず学びだけ作るため持たない。 |
| **根拠活動** | `based-on` | DEC → LEARN/TEST | 配列(many) | informs（導いた判断） | 必須 | この意思決定が根拠にした学び(LEARN)・実験計画(TEST)（複数可）。判定を持つ LEARN を優先する。判断がどの証拠に基づいたかを追跡でき、活動側からは逆引き（導いた判断）でその活動がどの決定を導いたかを辿れる。 |

## プロヴェナンス（出典＝生データへの参照）

型付きリンク（関係）は record→record だが、**出典はグラフの外（不変層 `projects/<slug>/sources/`）を指す属性**として別に宣言する。これが確信度の根拠鎖の**最後の一歩**にあたる: `H の確信度履歴` → `[[LEARN-NNN]]` → `出典ファイル`。

| 項目 | 値 |
|---|---|
| frontmatter | `sources`（配列・`sources/` 基準の相対パス） |
| 出典を持つ種別 | LEARN |
| 本文の相対mdリンク | 必須 |
| 出典が必須の活動種別 | demo・desk-research・interview・mvp-test・survey |
| 架空判定で読む冒頭行数 | 12 行 |

`hwlint.py` が検証すること: パスの実在（**error**）／必須種別での欠落／**確信度を上げた履歴行が指す学び(LEARN)に出典が無い**（根拠鎖の断絶）／どの学びからも参照されていない生データ（取り込み忘れ）。

## 状態機械

### ステージ

検証は次の順に進む（正式名称は `playbooks/<stage>.md` の見出しが正典）。

| ステージ | 正式名称 | 重点仮説タイプ（重要度=8） |
|---|---|---|
| CPF | Customer Problem Fit | 状況・行動仮説・課題仮説 |
| FPF | Founder Problem Fit | 課題仮説・自分たち仮説 |
| PSF | Problem Solution Fit | ソリューション仮説 |
| SPF | Solution Product Fit | ソリューション仮説 |
| PMF | Product Market Fit | 市場スケール仮説 |

### ステータス

| ステータス | 記号 | 説明 |
|---|---|---|
| 検証済み | ✅ | 実験で支持され、確信度も相応に高い（証拠の階梯を満たす）状態 |
| 検証中 | 🔄 | 実験に着手したが結論が出きっていない状態。判断保留（確信度3-4）も手応え（5-6）も正当 |
| 未検証 | ⚪ | まだ実験で確かめていない状態。起票直後の初期値 |
| 反証 | ❌ | 実験で否定された状態。もはや信じていないので確信度も低いはず |

検証の進捗: `未検証` → `検証中` → `検証済み` ／ `反証`。

### 検証判定（学び LEARN の `outcome`）

実験の成功基準に対する判定。board サマリの outcome 列へ射影する。

| 判定 | 意味 |
|---|---|
| 起票 | 仮説を起票した（確信度の初期値を置いた。真偽判定ではない） |
| 支持 | 成功基準を満たし仮説が支持された |
| 反証 | 成功基準を満たさず仮説が否定された |
| 判断保留 | 実験したが結論が出ず証拠が足りない（確信度は原則上げない） |
| 是正 | 記録・運用の誤りを正した（仮説の真偽判定ではないので確信度は動かさない） |

### データ種別（実験計画・学びの `data`）

そのレコードが**何のデータで作られたか**（何について書いてあるか、ではない）。架空判定の正本で、確信度の上限（fictional-cap）が掛かるかを決める。省略可だが、省くと出典冒頭の宣言・本文マーカー語による推論に戻る。

| 種別 | 意味 |
|---|---|
| `real` | 実観測（実在の相手・実際の計測）に由来する |
| `simulated` | 架空/シミュレーション由来（生成データ。確信度は fictional-cap で頭打ち） |

### 確信度

- 範囲: **1–10**（証拠の強さの目安）。確信度（証拠の強さ）とステータス（検証の進捗）は別軸で管理する。
- 架空/シミュレーションデータ由来の確信度は上限 **8**。9-10 は実観測に限る。由来の判定は上記 `data` の宣言が正本で、未宣言なら 出典冒頭の宣言 → 本文マーカー語（架空・シミュレーション。**未宣言かつ出典なし**のときだけ）の順に推論する。

**確信度の帯**（証拠の強さの目安）:

| 確信度 | 目安 |
|---|---|
| 1-2 | 勘・思いつき |
| 3-4 | 二次情報・状況証拠あり |
| 5-6 | 検証中で手応えあり（定性的証拠が集まりつつある） |
| 7-8 | 検証済みで確信度が高い |
| 9 | 反証を試みても崩れなかった |
| 10 | 事実（観測された確定事項） |

**証拠の階梯**（弱→強。確信度を上げる根拠の強さの序列。本文の根拠セルには 〈…〉 で書く）:

| 段 | 意味 |
|---|---|
| 〈発言〉 | 好意的な意見・「いいね」（interest。最も弱い） |
| 〈自認〉 | 自分の言葉で課題を語る（課題の存在を本人が認める） |
| 〈実コスト〉 | 時間・金・手戻りを既に払っている証拠（課題が実在するコスト痕跡） |
| 〈行動〉 | 実際にとった行動・現在の使用（言うだけでなく動いている） |
| 〈支払い〉 | 対価・前払い・導入コミット（intent。最も強い） |
| 〈二次〉（補助） | 二次情報（自分で観測していない外部の調査・記事など） |
| 〈架空〉（補助） | 架空/シミュレーション由来（実観測でない。確信度は fictional-cap で頭打ち） |

**確信度×ステータス／証拠の整合ルール**（`hwlint.py` が warning として検出）:

- ステータス **検証済み** は 確信度 ≥ 5 を期待（外れると矛盾）
- ステータス **未検証** は 確信度 ≤ 4 を期待（外れると矛盾）
- ステータス **反証** は 確信度 ≤ 4 を期待（外れると矛盾）
- 確信度 5 以上は〈自認〉以上の証拠を要する（〈発言〉だけでは上げない）
- 確信度 7 以上は〈実コスト〉以上の証拠を要する（〈発言〉だけでは上げない）
- 確信度 5 以上なのに履歴に階梯タグが**1つも無い**場合も warning（補助タグ〈二次〉〈架空〉は階梯を満たさない）

**陳腐化（時間軸）の閾値**（`hwlint.py` が warning として検出。**確信度は自動で下げない**＝再検証を促す可視化のみ）:

- `status: 検証済み` かつ確信度 5 以上で、確信度履歴の最終行が **180 日**より古い → 再検証を検討
- 学び(LEARN)が紐づかない実験計画(TEST)が **14 日**より古い（計画したのに実施されていない）

## リーンキャンバス（仮説検証への写像）

リーンキャンバス(Ash Maurya)は新しいレコード種別ではなく、既存の仮説(H)を事業モデル9ブロックへ射影した**ビュー**（`/lean-canvas` が使う）。各ブロックは H サブタイプの**役割(role)**に対応し、ブロックの検証状態は対応 role の H の status から導出する。心得は [playbooks/lean-canvas.md](playbooks/lean-canvas.md)。

| ブロック | 英名 | 対応role | 対応Hサブタイプ | 記入順 |
|---|---|---|---|---|
| 顧客セグメント | Customer Segments | customer | 状況・行動仮説 | 1 |
| 課題 | Problem | problem | 課題仮説 | 2 |
| 独自の価値提案 | Unique Value Proposition | solution | ソリューション仮説 | 3 |
| ソリューション | Solution | solution | ソリューション仮説 | 4 |
| チャネル | Channels | market | 市場スケール仮説 | 5 |
| 収益の流れ | Revenue Streams | market | 市場スケール仮説 | 6 |
| コスト構造 | Cost Structure | market | 市場スケール仮説 | 6 |
| 主要指標 | Key Metrics | market | 市場スケール仮説 | 7 |
| 圧倒的優位性 | Unfair Advantage | team | 自分たち仮説 | 8 |

**ブロック検証状態の射影**（対応 role の H 群から導出。新レコードは作らない）:

- **検証済み** — 対応roleのHにstatus=検証済みが1件以上
- **未検証** — 対応roleのHはあるがstatus=検証済みが無い
- **空白** — 対応roleのHが1件も無い（＝未着手の盲点）

**記入順 vs 検証順**: 記入は上表の順（網羅のため）。検証は `riskiest-first`（左→右で埋めず、最もリスキーな前提から。TEST の riskiest-assumption・`/planning` の重要度×証拠マップで決める）。

**ブロックの意味はステージで変わる（stage-lens）**:

| ブロック | early（初期の検証レンズ） | scale（後期のレンズ） |
|---|---|---|
| チャネル | 想定顧客に会って学ぶための経路（Day1から作る「顧客への道」。インタビュー・デモに到達する手段） | 反復可能でスケールする流通チャネル |
| 主要指標 | 顧客工場(AARRR)のどの一歩が詰まっているかを見る少数の学習指標 | 事業の健全性を測る主要指標 |
| 収益の流れ | 価格も仮説。〈支払い〉意思の検証対象（interest ≠ intent） | 反復可能な収益モデル |
