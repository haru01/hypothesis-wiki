#!/usr/bin/env python3
"""ontology.yaml から人間可読な ontology.md を生成する（決定論・手編集禁止）。

正本は ontology.yaml。このスクリプトはそれを Markdown の表に射影するだけ。
`python3 tools/gen_ontology_doc.py` で ../ontology.md を上書きする。
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import ontology  # noqa: E402

OUT = Path(__file__).resolve().parent.parent / "ontology.md"


def build() -> str:
    o = ontology.load()
    L = ["<!-- 生成物: gen_ontology_doc.py による ontology.yaml からの機械生成。手編集禁止。",
         "     `python3 tools/gen_ontology_doc.py` で再生成する。正本は ontology.yaml。 -->",
         "",
         "# 仮説検証Wiki オントロジー",
         "",
         "レコードの**型**（エンティティ）と、レコード間の**型付きリンク**（関係）、および"
         "検証の**状態機械**を定義する。正本は [ontology.yaml](ontology.yaml)。"
         "ツール（`tools/hwlint.py`・`tools/gen_views.py`）は `tools/ontology.py` 経由でここを読む。",
         ""]

    # エンティティ
    L += ["## エンティティ（レコード種別）", "",
          "| 種別 | 名称 | ディレクトリ | サブタイプ（frontmatter `type`） |",
          "|---|---|---|---|"]
    for key, ent in o["entities"].items():
        subs = "・".join(s["name"] for s in ent["subtypes"])
        L.append(f"| `{key}` | {ent['label']} | `wiki/{ent['dir']}/` | {subs} |")
    L.append("")

    # H の価値連鎖上の役割
    L += ["### 仮説（H）サブタイプの価値連鎖上の役割", "",
          "| サブタイプ | 役割 | 価値連鎖ラベル |", "|---|---|---|"]
    for s in o["entities"]["H"]["subtypes"]:
        L.append(f"| {s['name']} | {s.get('role', '—')} | {s.get('chain-label', '—')} |")
    L.append("")

    # 関係
    L += ["## 関係（型付きリンク）", "",
          "各関係は frontmatter 配列と本文 wikilink の**二重表現**を持つ"
          "（`must-wikilink: true` のものは本文にも `[[…]]` を張る＝Obsidian グラフに辺を出すため）。", "",
          "| 関係 | frontmatter | domain → range | cardinality | 逆方向(inverse) | 本文wikilink | 意味 |",
          "|---|---|---|---|---|---|---|"]
    for r in ontology.RELATIONS:
        dom = r.domain + (f"（{'・'.join(sorted(r.domain_subtypes))}）" if r.domain_subtypes else "")
        rng = r.range + (f"（{'・'.join(sorted(r.range_subtypes))}）" if r.range_subtypes else "")
        card = "単一(one)" if r.is_single else "配列(many)"
        wl = "必須" if r.must_wikilink else "任意"
        L.append(f"| **{r.label}** | `{r.field}` | {dom} → {rng} | {card} | "
                 f"{r.inverse}（{r.inverse_label}） | {wl} | {r.description} |")
    L.append("")

    # 状態機械（射影定数 ontology.py 経由。生 YAML を直読みしない＝単一の入口）
    stage_focus = o["state-machines"]["stage-focus"]   # 順序保持のため元の list を使う
    L += ["## 状態機械", "", "### ステージ", "",
          "検証は次の順に進む（正式名称は `playbooks/<stage>.md` の見出しが正典）。", "",
          "| ステージ | 正式名称 | 重点仮説タイプ（重要度=8） |", "|---|---|---|"]
    for st in ontology.STAGE_ORDER:
        focus = "・".join(stage_focus.get(st, []))
        L.append(f"| {st} | {ontology.STAGE_NAMES.get(st, '')} | {focus} |")
    L.append("")

    L += ["### ステータス", "", "| ステータス | 記号 |", "|---|---|"]
    for name in ontology.STATUS_ORDER:
        L.append(f"| {name} | {ontology.STATUS_EMOJI[name]} |")
    L.append("")

    L += ["### 確信度", "",
          f"- 範囲: **{ontology.CONFIDENCE_MIN}–{ontology.CONFIDENCE_MAX}**（証拠の強さの目安）",
          f"- 架空/シミュレーションデータ由来の確信度は上限 **{ontology.FICTIONAL_CAP}**"
          f"（本文マーカー: {'・'.join(ontology.FICTIONAL_MARKERS)}）",
          "- 証拠の階梯（弱→強）: " + " ＜ ".join(f"〈{t}〉" for t in ontology.EVIDENCE_LADDER),
          "- 階梯外の補助タグ: " + "・".join(f"〈{t}〉" for t in ontology.EVIDENCE_AUX),
          ""]
    return "\n".join(L)


def main() -> int:
    OUT.write_text(build(), encoding="utf-8")
    print(f"生成: {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
