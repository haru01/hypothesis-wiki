#!/usr/bin/env python3
"""ontology.yaml から人間可読な ontology.md を生成する（決定論・手編集禁止）。

正本は ontology.yaml。このスクリプトはそれを Markdown の表に射影するだけ。
`python3 tools/gen_ontology_doc.py` で ../ontology.md を上書きする。
`--check` は生成せずドリフトの有無だけを exit code で返す（pre-commit が使う）。
"""
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import ontology  # noqa: E402

OUT = Path(__file__).resolve().parent.parent / "ontology.md"


def _fields_table(fields) -> list:
    """frontmatter フィールド表の行（エンティティと付随物で同じ形なので共有する）。"""
    lines = ["| フィールド | 必須 | kind | 語彙(enum-ref) |", "|---|---|---|---|"]
    for f in fields:
        lines.append(f"| `{f.name}` | {'必須' if f.required else '省略可'} | {f.kind} | "
                     f"{('`' + f.enum_ref + '`') if f.enum_ref else '—'} |")
    return lines


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

    # 各種別の役割（description を持つものだけ箇条書き）
    ent_descs = [(k, e) for k, e in o["entities"].items() if e.get("description")]
    if ent_descs:
        L += ["**各種別の役割**:", ""]
        for key, ent in ent_descs:
            L.append(f"- **`{key}`（{ent['label']}）** — {ent['description']}")
        L.append("")

    # 凍結（不変ルール6）の適用範囲。教義と実装が同じ宣言を指すための一覧。
    if ontology.IMMUTABLE:
        L += ["### 凍結（不変ルール6）", "",
              "実施済みレコードのうち**後から書き換えてはいけない範囲**の宣言。"
              "「実施済み」＝発火関係でそのレコードを指す相手が在ること。"
              "ここに挙がっていない部分（目的・方法・指標の補正、リンク追加、誤字修正）は実施後も直してよい。"
              "`check_testcard_immutable.py` と `hwlint.py` の `testcard-sections` がこの宣言を読む。", "",
              "| 種別 | 発火（実施済みの判定） | 凍結する本文節 | 凍結する frontmatter キー |", "|---|---|---|---|"]
        for key, im in ontology.IMMUTABLE.items():
            secs = "・".join(f"`{s}`" for s in im.sections) or "—"
            keys = "・".join(f"`{f}`" for f in im.fields) or "—"
            L.append(f"| `{key}` | `{im.trigger_relation}` で指されている | {secs} | {keys} |")
        L.append("")

    # frontmatter フィールド（スキーマ＝契約）。必須欠落は error・未宣言キーは warning として lint が弾く。
    L += ["### frontmatter フィールド（スキーマ＝契約）", "",
          "各レコードが持つ frontmatter キーの宣言。**必須の欠落は error、宣言に無いキーは warning** として "
          "`hwlint.py` の `check_fields` が検出する（`kind` の意味は `ontology.yaml` 冒頭のコメントが正本）。", ""]
    for key, fields in ontology.FIELDS.items():
        if not fields:
            continue
        L += [f"**`{key}`（{o['entities'][key]['label']}）**", ""] + _fields_table(fields) + [""]

    # H の価値連鎖上の役割
    L += ["### 仮説（H）サブタイプの価値連鎖上の役割", "",
          "| サブタイプ | 役割 | 価値連鎖ラベル | 説明 |", "|---|---|---|---|"]
    for s in o["entities"]["H"]["subtypes"]:
        L.append(f"| {s['name']} | {s.get('role', '—')} | {s.get('chain-label', '—')} | "
                 f"{s.get('description', '—')} |")
    L.append("")

    # 付随物（レコードではないが型付きリンクに参加するノード）
    if ontology.ATTACHMENTS:
        L += ["## 付随物（attachments）", "",
              "付随物は**新しいレコード種別ではない**。親レコードに従属する成果物で、独自のID体系を持たず"
              "（ファイル名 = 親レコードID + suffix）、置き場も親と同じディレクトリを使う。"
              "それでいて**関係（型付きリンク）には参加する**ので、`hwlint.py` がリンク切れ・型違反を検出でき、"
              "Obsidian のグラフにも本文 wikilink 経由で現れる。", "",
              "レコード（エンティティ）と分けて持つのは正しさの要請である。ステム "
              "`<PREFIX>-TEST-NNN-script` には `-TEST-` が含まれるため、レコードとして読み込むと "
              "`records.py` の `entity_of` が `TEST` を返し、`\"-TEST-\" in stem` で書かれた箇所"
              "（board/list/index 生成・テストカード不変チェック）が付随物を実験計画として飲み込む。"
              "そのため読み取り層は `records` と `attachments` を別コレクションに保ち、"
              "**付随物は生成ビューに現れない**（board・list・index・relations のいずれも "
              "records だけを射影する）。関係インデックスも、始点・終点がレコードでない関係は"
              "恒久的に0件になるので節を出さない（「（該当なし）」と刻むと"
              "「そんな付随物は存在しない」という誤情報になる）。関係型の一覧そのものは"
              "スキーマの話なのでこのドキュメントが持つ。", "",
              "| 付随物 | 名称 | 親 | ファイル名 | サブタイプ（frontmatter `type`） |", "|---|---|---|---|---|"]
        for a in ontology.ATTACHMENTS.values():
            L.append(f"| `{a.name}` | {a.label} | `{a.parent}` | "
                     f"`wiki/{ontology.ATTACHMENT_DIRS[a.name]}/<親レコードID>{a.suffix}.md` | "
                     f"{'・'.join(a.subtypes)} |")
        L.append("")
        for a in ontology.ATTACHMENTS.values():
            if a.description:
                L += [f"- **`{a.name}`（{a.label}）** — {a.description}", ""]
            L += ([f"**`{a.name}` の frontmatter フィールド**", ""] + _fields_table(a.fields))
            L += ["", f"**`{a.name}` のサブタイプと雛形**", "",
                  "| サブタイプ | 基にする雛形 | 説明 |", "|---|---|---|"]
            for s in o["attachments"][a.name]["subtypes"]:
                tmpl = s.get("template", "")
                L.append(f"| {s['name']} | {f'[{tmpl}]({tmpl})' if tmpl else '—'} | "
                         f"{s.get('description', '—')} |")
            L.append("")
        L += ["`hwlint.py` が検証すること: ファイル名と親レコードIDの対応（**error**）／`type` の語彙"
              "（**error**）／親を指す関係がファイル名から導いた親と一致するか（**error**）／"
              "親と共有する関係（`hypotheses` 等）が親の値の**部分集合**か（**error**）／"
              "親から付随物への相対mdリンクの有無（到達可能性）。", ""]

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

    # プロヴェナンス（出典）。関係(record→record)とは別概念で、グラフの外（不変層）を指す属性。
    p = ontology.PROVENANCE
    L += ["## プロヴェナンス（出典＝生データへの参照）", "",
          "型付きリンク（関係）は record→record だが、**出典はグラフの外（不変層 "
          f"`projects/<slug>/{p.base_dir}/`）を指す属性**として別に宣言する。これが確信度の根拠鎖の"
          "**最後の一歩**にあたる: `H の確信度履歴` → `[[LEARN-NNN]]` → `出典ファイル`。", "",
          "| 項目 | 値 |", "|---|---|",
          f"| frontmatter | `{p.field}`（{'配列' if p.cardinality == 'many' else '単一'}・"
          f"`{p.base_dir}/` 基準の相対パス） |",
          f"| 出典を持つ種別 | {'・'.join(sorted(p.domains))} |",
          f"| 本文の相対mdリンク | {'必須' if p.must_body_link else '任意'} |",
          f"| 出典が必須の活動種別 | {'・'.join(sorted(p.required_for_types)) or '—'} |",
          f"| 架空判定で読む冒頭行数 | {p.fictional_header_scan_lines} 行 |",
          "",
          "`hwlint.py` が検証すること: パスの実在（**error**）／必須種別での欠落／"
          "**確信度を上げた履歴行が指す学び(LEARN)に出典が無い**（根拠鎖の断絶）／"
          "どの学びからも参照されていない生データ（取り込み忘れ）。", ""]

    # 状態機械（射影定数 ontology.py 経由。生 YAML を直読みしない＝単一の入口）
    stage_focus = o["state-machines"]["stage-focus"]   # 順序保持のため元の list を使う
    L += ["## 状態機械", "", "### ステージ", "",
          "検証は次の順に進む（正式名称は `playbooks/<stage>.md` の見出しが正典）。", "",
          "| ステージ | 正式名称 | 重点仮説タイプ（重要度=8） |", "|---|---|---|"]
    for st in ontology.STAGE_ORDER:
        focus = "・".join(stage_focus.get(st, []))
        L.append(f"| {st} | {ontology.STAGE_NAMES.get(st, '')} | {focus} |")
    L.append("")

    status_desc = {s["name"]: s.get("description", "") for s in o["state-machines"]["statuses"]}
    L += ["### ステータス", "", "| ステータス | 記号 | 説明 |", "|---|---|---|"]
    for name in ontology.STATUS_ORDER:
        L.append(f"| {name} | {ontology.STATUS_EMOJI[name]} | {status_desc.get(name) or '—'} |")
    L += ["", "検証の進捗: `未検証` → `検証中` → `検証済み` ／ `反証`。", ""]

    # 学び(LEARN)の検証判定（outcome）
    if ontology.OUTCOME_ORDER:
        L += ["### 検証判定（学び LEARN の `outcome`）", "",
              "実験の成功基準に対する判定。board サマリの outcome 列へ射影する。", "",
              "| 判定 | 意味 |", "|---|---|"]
        for name in ontology.OUTCOME_ORDER:
            L.append(f"| {name} | {ontology.OUTCOME_DESC.get(name) or '—'} |")
        L.append("")

    # データ種別（TEST/LEARN の data）。架空判定（fictional-cap）の正本。
    if ontology.DATA_KIND_ORDER:
        L += [f"### データ種別（実験計画・学びの `{ontology.DATA_FIELD}`）", "",
              "そのレコードが**何のデータで作られたか**（何について書いてあるか、ではない）。"
              "架空判定の正本で、確信度の上限（fictional-cap）が掛かるかを決める。省略可だが、"
              "省くと出典冒頭の宣言・本文マーカー語による推論に戻る。", "",
              "| 種別 | 意味 |", "|---|---|"]
        for name in ontology.DATA_KIND_ORDER:
            L.append(f"| `{name}` | {ontology.DATA_KIND_DESC.get(name) or '—'} |")
        L.append("")

    L += ["### 確信度", "",
          f"- 範囲: **{ontology.CONFIDENCE_MIN}–{ontology.CONFIDENCE_MAX}**（証拠の強さの目安）。"
          "確信度（証拠の強さ）とステータス（検証の進捗）は別軸で管理する。",
          f"- 架空/シミュレーションデータ由来の確信度は上限 **{ontology.FICTIONAL_CAP}**。"
          f"9-10 は実観測に限る。由来の判定は上記 `{ontology.DATA_FIELD}` の宣言が正本で、"
          f"未宣言なら 出典冒頭の宣言 → 本文マーカー語"
          f"（{'・'.join(ontology.FICTIONAL_MARKERS)}。**未宣言かつ出典なし**のときだけ）の順に推論する。",
          ""]

    # 確信度の帯
    if ontology.CONFIDENCE_BANDS:
        L += ["**確信度の帯**（証拠の強さの目安）:", "",
              "| 確信度 | 目安 |", "|---|---|"]
        for b in ontology.CONFIDENCE_BANDS:
            L.append(f"| {b['range']} | {b.get('meaning', '')} |")
        L.append("")

    # 証拠の階梯（各段の説明つき）
    L += ["**証拠の階梯**（弱→強。確信度を上げる根拠の強さの序列。本文の根拠セルには 〈…〉 で書く）:", "",
          "| 段 | 意味 |", "|---|---|"]
    for t in ontology.EVIDENCE_LADDER:
        L.append(f"| 〈{t}〉 | {ontology.EVIDENCE_LADDER_DESC.get(t) or '—'} |")
    for t in ontology.EVIDENCE_AUX:
        L.append(f"| 〈{t}〉（補助） | {ontology.EVIDENCE_AUX_DESC.get(t) or '—'} |")
    L.append("")

    # 確信度×ステータスの整合ルール（linter が検出）
    if ontology.STATUS_BOUNDS or ontology.EVIDENCE_FLOOR:
        L += ["**確信度×ステータス／証拠の整合ルール**（`hwlint.py` が warning として検出）:", ""]
        for status in ontology.STATUS_ORDER:
            b = ontology.STATUS_BOUNDS.get(status)
            if not b:
                continue
            parts = []
            if "min" in b:
                parts.append(f"確信度 ≥ {b['min']}")
            if "max" in b:
                parts.append(f"確信度 ≤ {b['max']}")
            L.append(f"- ステータス **{status}** は {'・'.join(parts)} を期待（外れると矛盾）")
        # EVIDENCE_FLOOR は (min_confidence, floor) の強い順。弱い順に見せる。
        for min_conf, floor in sorted(ontology.EVIDENCE_FLOOR):
            L.append(f"- 確信度 {min_conf} 以上は〈{floor}〉以上の証拠を要する（〈発言〉だけでは上げない）")
        L += [f"- 確信度 {ontology.EVIDENCE_FLOOR_MIN_CONFIDENCE} 以上なのに履歴に階梯タグが"
              "**1つも無い**場合も warning（補助タグ〈二次〉〈架空〉は階梯を満たさない）", ""]

    # 陳腐化（時間軸）。数値は自動で下げない＝再検証を促す可視化のみ。
    L += ["**陳腐化（時間軸）の閾値**（`hwlint.py` が warning として検出。"
          "**確信度は自動で下げない**＝再検証を促す可視化のみ）:", "",
          f"- `status: 検証済み` かつ確信度 {ontology.EVIDENCE_FLOOR_MIN_CONFIDENCE} 以上で、"
          f"確信度履歴の最終行が **{ontology.STALENESS_CONFIDENCE_DAYS} 日**より古い → 再検証を検討",
          f"- 学び(LEARN)が紐づかない実験計画(TEST)が **{ontology.STALENESS_TEST_DAYS} 日**より古い"
          "（計画したのに実施されていない）", ""]

    # リーンキャンバス（仮説検証への写像）。/lean-canvas が使う。レコードでなくビュー。
    if ontology.LEAN_CANVAS_BLOCKS:
        L += ["## リーンキャンバス（仮説検証への写像）", "",
              "リーンキャンバス(Ash Maurya)は新しいレコード種別ではなく、既存の仮説(H)を事業モデル9ブロックへ"
              "射影した**ビュー**（`/lean-canvas` が使う）。各ブロックは H サブタイプの**役割(role)**に対応し、"
              "ブロックの検証状態は対応 role の H の status から導出する。心得は "
              "[playbooks/lean-canvas.md](playbooks/lean-canvas.md)。", "",
              "| ブロック | 英名 | 対応role | 対応Hサブタイプ | 記入順 |", "|---|---|---|---|---|"]
        for b in sorted(ontology.LEAN_CANVAS_BLOCKS, key=lambda x: x.get("sketch-order", 99)):
            subs = "・".join(sorted(ontology.h_types_for_role(b["maps-to-role"]))) or "—"
            L.append(f"| {b['label']} | {b['en']} | {b['maps-to-role']} | {subs} | {b.get('sketch-order', '—')} |")
        L += ["",
              "**ブロック検証状態の射影**（対応 role の H 群から導出。新レコードは作らない）:", ""]
        for s in ontology.LEAN_CANVAS_BLOCK_STATUS:
            L.append(f"- **{s['name']}** — {s['from']}")
        L += ["",
              f"**記入順 vs 検証順**: 記入は上表の順（網羅のため）。検証は `{ontology.LEAN_CANVAS_VALIDATION_ORDER}`"
              "（左→右で埋めず、最もリスキーな前提から。TEST の riskiest-assumption・`/planning` の重要度×証拠マップで決める）。",
              ""]
        if ontology.LEAN_CANVAS_STAGE_LENS:
            label_of = {b["key"]: b["label"] for b in ontology.LEAN_CANVAS_BLOCKS}
            L += ["**ブロックの意味はステージで変わる（stage-lens）**:", "",
                  "| ブロック | early（初期の検証レンズ） | scale（後期のレンズ） |", "|---|---|---|"]
            for bk, lens in ontology.LEAN_CANVAS_STAGE_LENS.items():
                L.append(f"| {label_of.get(bk, bk)} | {lens.get('early', '—')} | {lens.get('scale', '—')} |")
            L.append("")
    return "\n".join(L)


def main() -> int:
    ap = argparse.ArgumentParser(description="ontology.yaml → ontology.md の生成")
    ap.add_argument("--check", action="store_true",
                    help="生成せず、ontology.md が ontology.yaml と同期しているかだけを検査する（差分あれば exit 1）")
    args = ap.parse_args()
    want = build()
    if args.check:
        have = OUT.read_text(encoding="utf-8") if OUT.exists() else ""
        if have == want:
            print(f"同期OK: {OUT.name} は ontology.yaml と一致")
            return 0
        print(f"ドリフト検出: {OUT.name} が ontology.yaml と不一致。"
              f"`python3 tools/gen_ontology_doc.py` で再生成する", file=sys.stderr)
        return 1
    OUT.write_text(want, encoding="utf-8")
    print(f"生成: {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
