#!/usr/bin/env python3
"""ontology.yaml → schema/*.schema.json（JSON Schema 2020-12）の生成。

## 何のためにあるか

`ontology.yaml` は正本だが、読むには「kind とは何か」「enum-ref は何を指すか」という
このリポジトリ固有の語彙を知っている必要がある。JSON Schema は**可搬な契約**で、
Claude Code 以外のエージェント・エディタ・CI がそのまま frontmatter を検証できる。

**検証の正本は `hwlint.py` のまま**。JSON Schema が表せるのは1レコード内の形だけで、
このリポジトリの規律の大半（確信度履歴テーブルとの一致・関係の実在・凍結・根拠鎖）は
レコードをまたぐ。ここで出すのは「フィールドの契約」の射影であって、lint の代替ではない。
そのため jsonschema ライブラリは依存に入れない（出力するだけで、検証には使わない）。

## 使い方

    python3 tools/gen_schema.py                    # schema/*.schema.json を生成
    python3 tools/gen_schema.py --check            # 生成物が ontology.yaml と同期しているか（差分あれば exit 1）
    python3 tools/gen_schema.py --check-templates  # templates/*.md の frontmatter と宣言の照合

`--check` は `gen_ontology_doc.py --check` と同じドリフトゲート（pre-commit が呼ぶ）。
"""
import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import ontology  # noqa: E402
from ontology import (  # noqa: E402
    ATTACHMENTS, ENUM_REFS, FIELD_KINDS, NODE_FIELDS_BY_NAME, NODE_SUBTYPES, RANGE_REFS,
    STRUCTURED_FIELDS,
)

REPO = Path(__file__).resolve().parent.parent
OUT_DIR = REPO / "schema"
TEMPLATE_DIR = REPO / "templates"

SCHEMA_URL = "https://json-schema.org/draft/2020-12/schema"

# ノード種別 → その種別のレコードを書く雛形（--check-templates が照合する）。
# 付随物のサブタイプ別雛形は ontology.yaml の attachments.*.subtypes[].template が正本なので
# ここには書かない（下の _template_targets が導出する）。
ENTITY_TEMPLATES = {"H": "templates/hypothesis.md", "TEST": "templates/testcard.md",
                    "LEARN": "templates/learning.md", "DEC": "templates/decision.md"}


def _value_schema(node: str, f) -> dict:
    """フィールド1件の値スキーマ。kind の validate（field-kinds）から機械的に決める。

    frontmatter は「素の文字列」契約で読まれる（records.parse_frontmatter が BaseLoader を
    使い型強制を避ける）ので、数値も真偽値も string として宣言する — スキーマだけ int と
    言い張ると、実際の読み取り層と食い違う契約になる。"""
    fk = FIELD_KINDS[f.kind]
    s = {"description": f.description}
    if f.guidance:
        s["$comment"] = f.guidance
    if fk.validate == "enum":
        s["type"] = "string"
        s["enum"] = sorted(ENUM_REFS.get(f.enum_ref, set()))
    elif fk.validate == "subtype":
        s["type"] = "string"
        s["enum"] = sorted(NODE_SUBTYPES.get(node, set()))
    elif fk.validate == "flag":
        s["type"] = ["string", "boolean"]
        s["enum"] = ["true", "false", True, False]
    elif fk.validate in ("int-range", "auto-or-int-range"):
        lo, hi = RANGE_REFS[fk.range_ref]
        pattern = "|".join(str(n) for n in range(lo, hi + 1))
        if fk.validate == "auto-or-int-range":
            pattern = "auto|" + pattern
        s["type"] = ["string", "integer"]
        s["pattern"] = f"^({pattern})$"
    elif fk.validate == "date":
        s["type"] = "string"
        s["pattern"] = r"^\d{4}-\d{2}-\d{2}$"
    elif f.kind == "id":
        s["type"] = "string"
        s["pattern"] = _id_pattern(node)
    elif f.kind == "relation":
        rel = ontology.RELATIONS_BY_FIELD[f.name]
        s["type"] = ["string", "array", "null"] if rel.is_single else ["array", "string", "null"]
        s["items"] = {"type": "string"}
    elif f.kind == "provenance":
        s["type"] = ["array", "null"]
        s["items"] = {"type": "string"}
    elif f.kind == "structured":
        s.update(_structured_schema(f.name))
    else:
        s["type"] = "string"
    if f.example:
        s["examples"] = [f.example]
    if f.default:
        s["default"] = f.default
    if f.required_when:
        s["$comment"] = ((s.get("$comment", "") + "\n") if s.get("$comment") else "") + \
            f"条件付き必須（{f.required_when.severity}）: {f.required_when.condition}"
    return s


def _id_pattern(node: str) -> str:
    """レコードID／付随物IDの正規表現。ID 規約の正本は ontology.ID_RE（と attachments の suffix）。"""
    a = ATTACHMENTS.get(node)
    if a:
        return r"^[A-Z0-9]+-" + re.escape(a.parent) + r"-\d+" + re.escape(a.suffix) + r"$"
    return r"^[A-Z0-9]+-" + re.escape(node) + r"-\d+$"


def _structured_schema(name: str) -> dict:
    """構造化フィールド（行の集まり）のスキーマ。行のキー宣言 structured-fields.*.keys から作る。"""
    sf = STRUCTURED_FIELDS[name]
    props, required = {}, []
    for k in sf.keys:
        ks = {"description": k.description}
        if k.kind == "enum":
            ks["type"] = "string"
            ks["enum"] = sorted(ENUM_REFS.get(k.enum_ref, set()))
        elif k.kind == "number":
            ks["type"] = ["number", "string"]
        else:                                    # ref / text はどちらも文字列
            ks["type"] = "string"
        if k.kind == "ref":
            ks["$comment"] = f"同じレコードの {k.ref_field} が指す集合の要素であること"
        props[k.name] = ks
        if k.required:
            required.append(k.name)
    row = {"type": "object", "properties": props, "additionalProperties": False}
    if required:
        row["required"] = required
    return {"type": ["array", "null"], "items": row}


def build_one(node: str) -> dict:
    """ノード種別1つ分の JSON Schema。"""
    fields = NODE_FIELDS_BY_NAME[node]
    a = ATTACHMENTS.get(node)
    meta = a if a else _entity(node)
    return {
        "$schema": SCHEMA_URL,
        "$id": f"https://github.com/haru01/hypothesis-wiki/schema/{node}.schema.json",
        "title": f"{node}（{meta.get('label', node) if isinstance(meta, dict) else meta.label}）",
        "description": (meta.get("description", "") if isinstance(meta, dict) else meta.description),
        "$comment": ("ontology.yaml から機械生成（tools/gen_schema.py）。手編集禁止。"
                     "検証の正本は tools/hwlint.py で、これは1レコード内の形の射影にすぎない。"),
        "type": "object",
        "properties": {name: _value_schema(node, f) for name, f in fields.items()},
        "required": [name for name, f in fields.items() if f.required],
        "additionalProperties": False,
    }


def _entity(node: str) -> dict:
    return ontology.load()["entities"][node]


def build() -> dict:
    """出力ファイル名 → JSON 本文（末尾改行つき）。"""
    out = {}
    for node in list(NODE_FIELDS_BY_NAME):
        text = json.dumps(build_one(node), ensure_ascii=False, indent=2) + "\n"
        out[f"{node}.schema.json"] = text
    return out


# ---- 雛形の frontmatter と宣言の照合 -------------------------------------------
# 雛形本文（散文の手順）は生成しない。人が書いた説明として残す価値があるので、
# ここで見るのは「宣言済みフィールドが漏れなく在り、宣言に無いキーが無い」ことだけ。

FM_RE = re.compile(r"^---\n(.*?)\n---", re.DOTALL)
KEY_RE = re.compile(r"^([A-Za-z][A-Za-z0-9-]*):")


def _template_targets() -> dict:
    """雛形パス → 検証するノード種別。付随物側は attachments の template 宣言から導出する。"""
    targets = {path: node for node, path in ENTITY_TEMPLATES.items()}
    for a in ATTACHMENTS.values():
        for tmpl in a.templates.values():
            targets[tmpl] = a.name
    return targets


def _template_keys(text: str) -> list:
    """雛形の frontmatter に現れるトップレベルキー（コメント行・入れ子行は無視）。"""
    m = FM_RE.match(text)
    if not m:
        return []
    keys = []
    for line in m.group(1).split("\n"):
        if line.startswith((" ", "\t", "#", "-")):
            continue
        km = KEY_RE.match(line)
        if km:
            keys.append(km.group(1))
    return keys


def check_templates() -> int:
    problems = []
    for rel, node in sorted(_template_targets().items()):
        path = REPO / rel
        if not path.is_file():
            problems.append(f"{rel}: 雛形が存在しない（{node} の雛形）")
            continue
        keys = _template_keys(path.read_text(encoding="utf-8"))
        declared = NODE_FIELDS_BY_NAME[node]
        for name, f in declared.items():
            if name not in keys:
                problems.append(f"{rel}: 宣言済みフィールド '{name}'"
                                f"（{'必須' if f.required else '省略可'}）が雛形に無い")
        for key in keys:
            if key not in declared:
                problems.append(f"{rel}: ontology.yaml の {node}.fields に宣言の無いキー '{key}'")
    for p in problems:
        print(f"[drift] {p}", file=sys.stderr)
    if problems:
        print(f"雛形と宣言のドリフト {len(problems)} 件", file=sys.stderr)
        return 1
    print(f"同期OK: 雛形 {len(_template_targets())} 本の frontmatter は fields 宣言と一致")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description="ontology.yaml → schema/*.schema.json の生成")
    ap.add_argument("--check", action="store_true",
                    help="生成せず、schema/ が ontology.yaml と同期しているかだけを検査する（差分あれば exit 1）")
    ap.add_argument("--check-templates", action="store_true",
                    help="templates/*.md の frontmatter が fields 宣言と一致するかを検査する")
    args = ap.parse_args()
    if args.check_templates:
        return check_templates()
    want = build()
    if args.check:
        stale = [name for name, text in want.items()
                 if not (OUT_DIR / name).exists()
                 or (OUT_DIR / name).read_text(encoding="utf-8") != text]
        extra = sorted(p.name for p in OUT_DIR.glob("*.schema.json")) if OUT_DIR.is_dir() else []
        extra = [n for n in extra if n not in want]
        if not stale and not extra:
            print(f"同期OK: schema/ ({len(want)}件) は ontology.yaml と一致")
            return 0
        print(f"ドリフト検出: schema/ が ontology.yaml と不一致（古い: {stale or '—'} / "
              f"余分: {extra or '—'}）。`python3 tools/gen_schema.py` で再生成する", file=sys.stderr)
        return 1
    OUT_DIR.mkdir(exist_ok=True)
    for name, text in want.items():
        (OUT_DIR / name).write_text(text, encoding="utf-8")
    print(f"生成: {OUT_DIR}/ ({len(want)}件: {', '.join(sorted(want))})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
