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
- **`LEARN`（学び）** — 学習カード。検証後に新規作成する「実施して学びを得た」出来事。事実(observed)と解釈(inference)を分け、outcome（判定）と確信度更新を記録する。1つの学びが複数の仮説を動かすときは judgments で仮説ごとの判定を、実験計画の success-criteria に対する実測は measurements で持つ（outcome だけでは「どの仮説が崩れたか」がグラフから消える）。計画型は learns-from で TEST を参照し、回顧型（desk-research/self-reflection 等）は TEST を持たず自身が活動種別を名乗る。サブタイプは活動種別（TEST と同じ語彙）。sources で根拠となった生データ（不変層）を指し、確信度の根拠鎖を端まで辿れるようにする。
- **`DEC`（意思決定）** — ステージ移行・ピボット・撤退・巻き戻しなどの節目の判断。based-on で根拠の LEARN/TEST に結び、to-stage を持つ最新 DEC が現在ステージの正本になる。巻き戻しポイントと次の一手を残す。

### 凍結（不変ルール6）

実施済みレコードのうち**後から書き換えてはいけない範囲**の宣言。「実施済み」＝発火関係でそのレコードを指す相手が在ること。ここに挙がっていない部分（目的・方法・指標の補正、リンク追加、誤字修正）は実施後も直してよい。`check_testcard_immutable.py` と `hwlint.py` の `testcard-sections` がこの宣言を読む。

| 種別 | 発火（実施済みの判定） | 凍結する本文節 | 凍結する frontmatter キー |
|---|---|---|---|
| `TEST` | `learns-from` で指されている | `成功基準` | `riskiest-assumption`・`success-criteria` |

### frontmatter フィールド（スキーマ＝契約）

各レコードが持つ frontmatter キーの宣言。**必須の欠落は error、宣言に無いキーは warning** として `hwlint.py` の `check_fields` が検出し、値が語彙・範囲に収まるかは `check_vocabulary` が見る。同じ宣言から機械可読な JSON Schema（`schema/*.schema.json`）も生成される（`tools/gen_schema.py`。Claude Code 以外のエージェント・エディタ向けの可搬な契約で、検証の正本は `hwlint.py` のまま）。

**kind（値の種別）**:

| kind | 意味 | check_fields / check_vocabulary の検証 |
|---|---|---|
| `id` | ファイル名と一致する接頭辞つきID（例 SELF-H-001） | （`id-filename` が担当） |
| `text` | 自由記述の一行 | — |
| `subtype` | 当該 entity の subtypes 名 | `subtype` |
| `enum` | enum-ref が指す状態機械の語彙（stages / statuses / outcomes / data-kinds） | `enum` |
| `date` | YYYY-MM-DD | `date` |
| `confidence` | confidence.min〜max の整数 | `int-range`（1-10） |
| `importance` | auto、または confidence.min〜max の整数（auto は stage-focus から解決する） | `auto-or-int-range`（1-10） |
| `flag` | true / false。true のときだけ意味を持つ省略可フィールド（未記入＝false 扱い） | `flag` |
| `relation` | 関係キー。型（domain/range/cardinality）の正本は下記 relations 節 | （`refs` が担当） |
| `provenance` | 出典キー。仕様の正本は下記 provenance 節 | （`provenance` が担当） |
| `structured` | 行の集まり（配列 of マッピング）。行の形の正本は下記 structured-fields 節 | （`struct-shape` が担当） |

**`H`（仮説）**

| フィールド | 必須 | kind | 語彙(enum-ref) | 既定値 | 説明 |
|---|---|---|---|---|---|
| `id` | 必須 | id | — | — | ファイル名と一致する接頭辞つきID。三者一致（ファイル名＝id＝本文の参照先）が規約。 |
| `title` | 必須 | text | — | — | 仮説の内容が一読で分かる短いタイトル。本文 H1 と一致させる。 |
| `short-title` | 省略可 | text | — | — | list ビューの mermaid ノード用の短ラベル（8字程度）。省略時はタイトルを機械切り詰め。 |
| `falsifier` | 必須 | text | — | — | 何が観測されればこの仮説が反証されるか。仮説文と対で、検証を始める前に確定する。 |
| `type` | 必須 | subtype | — | — | 価値連鎖上のどの仮説か。ステージごとの重点タイプ（stage-focus）と照合され importance に効く。 |
| `status` | 必須 | enum | `statuses` | `未検証` | 検証の進捗。確信度とは別軸で、確信度履歴テーブル最終行の同期キャッシュ。 |
| `confidence` | 必須 | confidence | — | `1` | 証拠の強さの目安。確信度履歴テーブル最終行の同期キャッシュ（正本は本文の表）。 |
| `stage` | 必須 | enum | `stages` | `CPF` | この仮説を主に検証するステージ。プロジェクトの現在ステージとは独立に持つ。 |
| `importance` | 省略可 | importance | — | `auto` | 検証の優先度。auto なら現在ステージの stage-focus から importance-weights で解決する。 |
| `derived-from` | 省略可 | relation | — | — | 枝分かれ元の仮説（1件）。ピボット・巻き戻しの再出発点を系譜として残す。 |
| `leads-to` | 省略可 | relation | — | — | この仮説が成り立つと次に導かれる仮説（複数可）。list ビューの mermaid 矢印になる。 |
| `addresses` | 省略可 | relation | — | — | このソリューション仮説が解こうとする課題仮説（複数可）。relations のフィット表になる。 |
| `core` | 省略可 | flag | — | — | 核心仮説なら true（list ビューで ★ 表示）。未記入は false 扱い。 |

- `falsifier` — 反証条件を言えない文は仮説ではない（/formulating の鉄則）。ここが機械可読だと 「この仮説は何が起きたら崩れるか」を frontmatter から直接引ける — 実験計画(TEST)の 成功基準に事前登録する文言の出どころであり、board が実験ブロックへ射影する。 本文 `## 反証条件` 節にも同じ文言を置く（二重表現）。文言の変更は仮説の意味の変更なので、 確信度履歴に影響する見直しと同じ重さで扱う。
- `confidence` — 直接書き換えない。変更は必ず学び(LEARN)か意思決定(DEC)に紐づけ、本文の確信度履歴に 1行追記してからその値をここへ写す（不変ルール1・2）。
- `derived-from` — 本文「系譜」節にも wikilink を併記する（frontmatter だけでは Obsidian グラフに辺が出ない）。
- `leads-to` — 本文「系譜」節にも wikilink を併記する。この辺の推移閉包が「崩れると波及が大きい背骨」＝ board の「次に検証すべき仮説」の下流依存度になる。
- `addresses` — 本文 wikilink は不要（must-wikilink: false）。フィット表は frontmatter から射影する。

**`TEST`（実験計画）**

| フィールド | 必須 | kind | 語彙(enum-ref) | 既定値 | 説明 |
|---|---|---|---|---|---|
| `id` | 必須 | id | — | — | ファイル名と一致する接頭辞つきID。 |
| `title` | 必須 | text | — | — | 何を誰にどう当てる実験かが一読で分かる短いタイトル。 |
| `type` | 必須 | subtype | — | — | 活動種別。スクリプト雛形の選択（/planning）と log.md の type に対応する。 |
| `date` | 必須 | date | — | — | 計画日。実施日ではない（実施日は紐づく学び LEARN の date が正本）。 |
| `stage` | 必須 | enum | `stages` | `CPF` | この実験がどのステージの問いを検証するか。 |
| `hypotheses` | 必須 | relation | — | — | この実験が検証する仮説（複数可）。仮説側からは「検証活動」として逆引きされる。 |
| `riskiest-assumption` | 必須 | text | — | — | この実験で崩れたら全体が崩れる一点を一文で。board の背骨になる。 |
| `data` | 必須 | enum | `data-kinds` | — | この実験が「何のデータで作られるか」（何について書いてあるかではない）。架空判定 fictional-cap の正本。 |
| `success-criteria` | 省略可 | structured | — | — | 成功基準のうち数えられるものを機械可読にした背骨。本文の散文と二重表現。 |

- `hypotheses` — 本文にも wikilink を書く（must-wikilink。frontmatter だけでは Obsidian グラフに辺が出ない）。
- `riskiest-assumption` — 検証前に確定し、学び(LEARN)が紐づいた後は凍結される（immutable.fields）。 後知恵で「もともとそこは狙っていなかった」と書き換えられないようにするための凍結。
- `data` — 未宣言を許すと本文マーカー語の推論に黙って落ち、宣言漏れが静かに「実データ」扱いになって fictional-cap が効かない（＝架空由来の確信度が上限なく上がる）。黙って劣化させるくらいなら 書かせて弾く。推論経路自体は他 vault・旧レコードのために残す。
- `success-criteria` — 散文を置き換えるものではない（ニュアンスは散文が担う）。数を決めていない基準は載せない ＝ここに無いものは人が判定する、という契約。検証前に確定し、実施後は riskiest-assumption と 同格で凍結される（数値だけ後から動かせるなら節を凍らせた意味が無い）。

**`LEARN`（学び）**

| フィールド | 必須 | kind | 語彙(enum-ref) | 既定値 | 説明 |
|---|---|---|---|---|---|
| `id` | 必須 | id | — | — | ファイル名と一致する接頭辞つきID。 |
| `title` | 必須 | text | — | — | 何から何を学んだかが一読で分かる短いタイトル。 |
| `type` | 必須 | subtype | — | — | 活動種別（TEST と同じ語彙）。回顧型（desk-research/self-reflection）はここで自身の種別を名乗る。 |
| `date` | 必須 | date | — | — | 実施日。計画型ではこちらが実施日の正本で、TEST の date は計画日。 |
| `stage` | 必須 | enum | `stages` | `CPF` | この学びがどのステージの問いに答えたか。 |
| `learns-from` | 省略可 | relation | — | — | 実施した実験計画(TEST)を1つ指す。board が「1実験＝計画＋学び」を1行に束ねる。 |
| `hypotheses` | 必須 | relation | — | — | この学びが確信度を動かした仮説（複数可）。 |
| `outcome` | 必須 | enum | `outcomes` | — | レコード全体の判定を1語で。board サマリの判定列へ射影される。 |
| `judgments` | 条件付き（warning） | structured | — | — | 仮説ごとの判定。hypotheses が複数で結論が分かれるときのレコード内訳。 |
| `measurements` | 省略可 | structured | — | — | 実験計画(TEST)の success-criteria に対して実際に観測した値。metric 名で基準と対応させる。 |
| `sources` | 条件付き（warning） | provenance | — | — | 根拠となった生データ（不変層 sources/ 基準の相対パス）。確信度の根拠鎖の末端。 |
| `data` | 必須 | enum | `data-kinds` | — | この学びが「何のデータで作られたか」（何について書いてあるかではない）。架空判定 fictional-cap の正本。 |

- `learns-from` — 回顧型（desk-research / self-reflection / chabudai）は事前の計画を立てないので持たない。 持たない学びは board で「—（回顧型・事前の実験計画なし）」として表示される。
- `hypotheses` — 本文にも wikilink を書く（must-wikilink）。
- `outcome` — 対象仮説ごとに結論が違うときは、これだけでは「どの仮説が崩れたか」がグラフから消える。 その場合は judgments に仮説ごとの判定を書く。
- `judgments` の条件付き必須 — outcome が真偽判定（judgment-check.truth-outcomes）で、hypotheses が2件以上のとき（warning・judgment-coverage が検出）
- `measurements` — これがあると lint が判定を検算でき、「基準を割ったのに支持」＝ゴールポストの事後移動を error で弾ける（judgment-mismatch）。慎重側（判断保留）へ倒すのは常に許される。
- `sources` の条件付き必須 — type が provenance.required-for-types（観測を伴う活動種別）のとき（warning・provenance が検出）
- `sources` — 本文にも相対mdリンクを置く（二重表現。生データは接頭辞つきノートでないので wikilink は解決しない）。 生データ冒頭の架空/シミュレーション宣言はここから読まれる。
- `data` — 必須の理由は TEST.data と同じ。架空データを**論じた**是正・監査レコードは real である （混同すると実データの実験が架空に誤分類される）。

**`DEC`（意思決定）**

| フィールド | 必須 | kind | 語彙(enum-ref) | 既定値 | 説明 |
|---|---|---|---|---|---|
| `id` | 必須 | id | — | — | ファイル名と一致する接頭辞つきID。 |
| `title` | 必須 | text | — | — | 何をどう決めたかが一読で分かる短いタイトル。 |
| `date` | 必須 | date | — | — | 判断した日。to-stage を持つ DEC の最新性はこの日付で決まる。 |
| `type` | 必須 | subtype | — | — | 判断の種類。ステージを動かすのは主に stage-transition と rollback。 |
| `based-on` | 条件付き（warning） | relation | — | — | 根拠にした学び(LEARN)・実験計画(TEST)（複数可）。判定を持つ LEARN を優先する。 |
| `to-stage` | 省略可 | enum | `stages` | — | この判断の結果ステージ。to-stage を持つ最新 DEC が現在ステージの正本になる。 |

- `based-on` の条件付き必須 — 常に（根拠なき意思決定を作らない）（warning）
- `based-on` — 本文にも wikilink を書く（must-wikilink）。
- `to-stage` — ステージを動かす判断（stage-transition・rollback 等）だけが持つ。空だとビュー・ツールが 現ステージを導出できず、wiki/stage.md のフォールバックに落ちる。

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

| フィールド | 必須 | kind | 語彙(enum-ref) | 既定値 | 説明 |
|---|---|---|---|---|---|
| `id` | 必須 | id | — | — | ファイル名と一致する。付随物なので独自の採番を持たず「親レコードID + suffix」。 |
| `title` | 必須 | text | — | — | どの実験の台本かが分かる短いタイトル。 |
| `type` | 必須 | subtype | — | — | 基にした雛形（templates/<type>-script.md）。/planning の雛形選択がこの語彙に対応する。 |
| `script-for` | 必須 | relation | — | — | 台本化した実験計画(TEST)。ファイル名から導ける対応を frontmatter にも明示する。 |
| `hypotheses` | 省略可 | relation | — | — | 台本が実際に当てる仮説。親 TEST の検証対象の部分集合でなければならない。 |

- `hypotheses` — 省略可なのは**発見型のスクリプトが既存仮説を相手に語らない**設計だから。仮説を宣言すると 台本の意図と食い違う。本文で背景として別の仮説に言及するのは正当なので、逆向き （本文の wikilink をすべて宣言せよ）は課さない。

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

## 構造化フィールド（行の集まり）

平坦な `key: value` でも record→record の関係でもない第三の形。**1レコードに複数行あり、行の中に構造がある**フィールドを宣言する。

必要な理由: `hypotheses` は配列(many)なのに `outcome` はレコードに1つしかない。1つの学びが3仮説を見て「1つは反証・2つは据え置き」と判定しても、frontmatter に残るのは要約1語だけで、**仮説ごとの結論はグラフから消えて散文にしか残らない**。判定の粒度を仮説に合わせ、成功基準と実測を突き合わせられるようにするための層。

| フィールド | 持てる種別 | 名称 | 意味 |
|---|---|---|---|
| `judgments` | LEARN | 仮説ごとの判定 | この学びが対象仮説それぞれをどう判定したか。hypotheses が複数のとき、レコード単位の outcome では表せない結論の違いをここに残す。board が仮説単位に射影し、「反証されたのに誰も判断していない」の機械判定の材料になる。 |
| `success-criteria` | TEST | 成功基準（機械可読な背骨） | 本文「成功基準」節の散文を置き換えるものではなく、検算できる骨だけを取り出したもの。実施前に確定し、実施後は凍結する（immutable.fields）。実測（measurements）と突き合わせて、数値と真逆の判定を弾くために使う。 |
| `measurements` | LEARN | 実測 | 実験計画(TEST)の success-criteria に対して実際に観測した値。metric 名で基準と突き合わせる。判定（judgments・outcome）が実測と真逆でないことを lint が検算する＝ゴールポストの事後移動を数値で弾く。 |

**`judgments` の行のキー**

| キー | 必須 | kind | 参照/語彙 | 説明 |
|---|---|---|---|---|
| `hypothesis` | 必須 | ref | frontmatter `hypotheses` の要素 | 判定した仮説。この学びの hypotheses に含まれていること |
| `outcome` | 必須 | enum | `outcomes` | その仮説に対する判定 |
| `note` | 省略可 | text | — | 判定の一言理由（詳細は本文に書く） |

**`success-criteria` の行のキー**

| キー | 必須 | kind | 参照/語彙 | 説明 |
|---|---|---|---|---|
| `hypothesis` | 必須 | ref | frontmatter `hypotheses` の要素 | この基準が判定する仮説。この実験の hypotheses に含まれていること |
| `metric` | 必須 | text | — | 測る対象の名前。学び(LEARN)の measurements.metric と文字列一致させる |
| `op` | 必須 | enum | `criteria-ops` | 比較演算子。実測値を左辺に置いて評価する |
| `threshold` | 必須 | number | — | 満たすべき閾値 |
| `of` | 省略可 | number | — | 母数（「5名中3名」の5）。実測の n と食い違えば warning |

**`measurements` の行のキー**

| キー | 必須 | kind | 参照/語彙 | 説明 |
|---|---|---|---|---|
| `metric` | 必須 | text | — | 実験計画(TEST)の success-criteria.metric と一致させる名前 |
| `value` | 必須 | number | — | 実際に観測した値 |
| `n` | 省略可 | number | — | 母集団（何人・何件を見たか）。基準の of と食い違えば warning |
| `note` | 省略可 | text | — | 観測条件の補足（詳細は本文に書く） |

**成功基準の演算子**: `>=`・`>`・`<=`・`<`・`==`・`!=`（実測 `value` を左辺、`threshold` を右辺に置いて評価する）。

**判定の検算（`judgment-mismatch`）**: 実測から導いた判定と著者が書いた判定が**真逆のときだけ** error にする。全基準を満たしたのに `反証`／全基準を割ったのに `支持` は弾き、慎重側（`判断保留`）へ倒すのは常に許す。一部だけ満たした場合は導出せず人の解釈に委ねる。検算の対象になる判定は `支持`・`反証`・`判断保留`（起票・是正は仮説の真偽判定ではないので対象外）。

凍結（不変ルール6）との関係: 本文の「成功基準」節を凍らせても、数値だけ後から動かせるなら意味が無い。`success-criteria` は `riskiest-assumption` と同格で凍結する。

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

そのレコードが**何のデータで作られたか**（何について書いてあるか、ではない）。架空判定の正本で、確信度の上限（fictional-cap）が掛かるかを決める。**必須** — 未宣言を許すと出典冒頭の宣言・本文マーカー語による推論に黙って落ち、宣言漏れが静かに「実データ」扱いになって上限が効かない。推論経路は他 vault・旧レコードのために残す。

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
