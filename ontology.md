<!-- 生成物: gen_ontology_doc.py による ontology.yaml からの機械生成。手編集禁止。
     `python3 tools/gen_ontology_doc.py` で再生成する。正本は ontology.yaml。 -->

# 仮説検証Wiki オントロジー

レコードの**型**（エンティティ）と、レコード間の**型付きリンク**（関係）、および検証の**状態機械**を定義する。正本は [ontology.yaml](ontology.yaml)。ツール（`tools/hwlint.py`・`tools/gen_views.py`）は `tools/ontology.py` 経由でここを読む。

## エンティティ（レコード種別）

| 種別 | 名称 | ディレクトリ | サブタイプ（frontmatter `type`） |
|---|---|---|---|
| `H` | 仮説 | `wiki/hypotheses/` | 状況・行動仮説・課題仮説・ソリューション仮説・市場スケール仮説・自分たち仮説 |
| `ACT` | 活動 | `wiki/activities/` | interview・demo・survey・mvp-test・desk-research・self-reflection |
| `DEC` | 意思決定 | `wiki/decisions/` | stage-transition・pivot・persevere・rollback・kill |

### 仮説（H）サブタイプの価値連鎖上の役割

| サブタイプ | 役割 | 価値連鎖ラベル |
|---|---|---|
| 状況・行動仮説 | customer | 状況・行動 |
| 課題仮説 | problem | 切実な課題 |
| ソリューション仮説 | solution | ソリューション |
| 市場スケール仮説 | market | 市場スケール |
| 自分たち仮説 | team | 自分たち |

## 関係（型付きリンク）

各関係は frontmatter 配列と本文 wikilink の**二重表現**を持つ（`must-wikilink: true` のものは本文にも `[[…]]` を張る＝Obsidian グラフに辺を出すため）。

| 関係 | frontmatter | domain → range | cardinality | 逆方向(inverse) | 本文wikilink | 意味 |
|---|---|---|---|---|---|---|
| **派生元** | `derived-from` | H → H | 単一(one) | derives（派生先） | 必須 | 派生・ピボット・巻き戻し再出発の系譜（この仮説の派生元） |
| **因果先** | `leads-to` | H → H | 配列(many) | led-from（因果元） | 必須 | 因果的に導く先の仮説。list の mermaid バリューチェーン矢印になる |
| **対応課題** | `addresses` | H（ソリューション仮説） → H（課題仮説） | 配列(many) | addressed-by（対応する価値） | 任意 | ソリューション仮説→対応する課題仮説（バリュープロポジションのフィット） |
| **検証対象** | `hypotheses` | ACT → H | 配列(many) | validated-by（検証活動） | 必須 | この活動が検証する仮説 |
| **根拠活動** | `based-on` | DEC → ACT | 配列(many) | informs（導いた判断） | 必須 | この意思決定の根拠となった活動 |

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

| ステータス | 記号 |
|---|---|
| 検証済み | ✅ |
| 検証中 | 🔄 |
| 未検証 | ⚪ |
| 反証 | ❌ |

### 確信度

- 範囲: **1–10**（証拠の強さの目安）
- 架空/シミュレーションデータ由来の確信度は上限 **8**（本文マーカー: 架空・シミュレーション）
- 証拠の階梯（弱→強）: 〈発言〉 ＜ 〈自認〉 ＜ 〈実コスト〉 ＜ 〈行動〉 ＜ 〈支払い〉
- 階梯外の補助タグ: 〈二次〉・〈架空〉

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

**記入順 vs 検証順**: 記入は上表の順（網羅のため）。検証は `riskiest-first`（左→右で埋めず、最もリスキーな前提から。ACT の riskiest-assumption・`/plan` の重要度×証拠マップで決める）。

**ブロックの意味はステージで変わる（stage-lens）**:

| ブロック | early（初期の検証レンズ） | scale（後期のレンズ） |
|---|---|---|
| チャネル | 想定顧客に会って学ぶための経路（Day1から作る「顧客への道」。インタビュー・デモに到達する手段） | 反復可能でスケールする流通チャネル |
| 主要指標 | 顧客工場(AARRR)のどの一歩が詰まっているかを見る少数の学習指標 | 事業の健全性を測る主要指標 |
| 収益の流れ | 価格も仮説。〈支払い〉意思の検証対象（interest ≠ intent） | 反復可能な収益モデル |
