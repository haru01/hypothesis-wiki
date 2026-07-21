<!-- 生成物: gen_ontology_doc.py による ontology.yaml からの機械生成。手編集禁止。
     `python3 tools/gen_ontology_doc.py` で再生成する。正本は ontology.yaml。 -->

# 仮説検証Wiki オントロジー

レコードの**型**（エンティティ）と、レコード間の**型付きリンク**（関係）、および検証の**状態機械**を定義する。正本は [ontology.yaml](ontology.yaml)。ツール（`tools/hwlint.py`・`tools/gen_views.py`）は `tools/ontology.py` 経由でここを読む。

## エンティティ（レコード種別）

| 種別 | 名称 | ディレクトリ | サブタイプ（frontmatter `type`） |
|---|---|---|---|
| `H` | 仮説 | `wiki/hypotheses/` | 状況・行動仮説・課題仮説・ソリューション仮説・個別購買仮説・自分たち仮説 |
| `ACT` | 活動 | `wiki/activities/` | interview・demo・survey・mvp-test・desk-research・self-reflection |
| `DEC` | 意思決定 | `wiki/decisions/` | stage-transition・pivot・persevere・rollback・kill |

### 仮説（H）サブタイプの価値連鎖上の役割

| サブタイプ | 役割 | 価値連鎖ラベル |
|---|---|---|
| 状況・行動仮説 | customer | 状況・行動 |
| 課題仮説 | problem | 切実な課題 |
| ソリューション仮説 | solution | ソリューション |
| 個別購買仮説 | market | 個別購買 |
| 自分たち仮説 | team | 自分たち |

## 関係（型付きリンク）

各関係は frontmatter 配列と本文 wikilink の**二重表現**を持つ（`must-wikilink: true` のものは本文にも `[[…]]` を張る＝Obsidian グラフに辺を出すため）。

| 関係 | frontmatter | domain → range | cardinality | 逆方向(inverse) | 本文wikilink | 意味 |
|---|---|---|---|---|---|---|
| **派生元** | `derived-from` | H → H | 単一(one) | derives（派生先） | 必須 | 派生・ピボット・巻き戻し再出発の系譜（この仮説の派生元） |
| **因果先** | `leads-to` | H → H | 配列(many) | led-from（因果元） | 必須 | 因果的に導く先の仮説。list の mermaid バリューチェーン矢印になる |
| **対応課題** | `addresses` | H（ソリューション仮説・個別購買仮説） → H（課題仮説） | 配列(many) | addressed-by（対応する価値） | 任意 | ソリューション仮説→対応する課題仮説（バリュープロポジションのフィット） |
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
| SPF | Solution Product Fit | ソリューション仮説・個別購買仮説 |
| PMF | Product Market Fit | 個別購買仮説 |

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
