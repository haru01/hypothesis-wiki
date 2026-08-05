#!/usr/bin/env python3
"""仮説検証Wiki オントロジーのローダ（唯一の正本 ontology.yaml を読む）。

語彙(enum)・型・関係・状態機械の定義はすべて ../ontology.yaml に集約し、
このモジュールがそれを Python 側の定数（hwlint.py・gen_views.py が使う形）に射影する。
コード側に enum を再定義しない＝二重管理・ドリフトを防ぐための単一の入口。

依存は PyYAML のみ（hwlint / gen_views を import しない＝循環回避）。
"""
import re
from functools import lru_cache
from pathlib import Path

import yaml

ONTOLOGY_PATH = Path(__file__).resolve().parent.parent / "ontology.yaml"


def version() -> int:
    """スキーマ版（ontology.yaml の version）。生成ビューのヘッダに刻む。"""
    return load().get("version", 0)


@lru_cache(maxsize=1)
def load() -> dict:
    """ontology.yaml をパースして dict で返す（プロセス内で1回だけ読む）。"""
    return yaml.safe_load(ONTOLOGY_PATH.read_text(encoding="utf-8"))


def _as_set(value) -> set:
    """domain/range を集合に正規化する（文字列単一 or 配列の両方を許す）。"""
    return set(value) if isinstance(value, (list, tuple, set)) else {value}


class Relation:
    """関係型1件。domain→range・cardinality・inverse を保持する。

    domain/range は複数エンティティ種別を許す（例 hypotheses は TEST/LEARN）。
    集合は `domains`/`ranges`、表示用の文字列は `domain`/`range`（"TEST/LEARN"）で持つ。
    種別判定は `in_domain(ent)`/`in_range(ent)` を使う。"""
    __slots__ = ("name", "field", "domains", "ranges", "domain", "range",
                 "domain_subtypes", "range_subtypes",
                 "cardinality", "inverse", "must_wikilink", "label", "inverse_label", "description")

    def __init__(self, d: dict):
        self.name = d["name"]
        self.field = d["field"]
        self.domains = _as_set(d["domain"])             # エンティティ種別の集合 {"TEST"} / {"TEST","LEARN"}
        self.ranges = _as_set(d["range"])
        self.domain = "/".join(sorted(self.domains))    # 表示用（例 "TEST/LEARN"）
        self.range = "/".join(sorted(self.ranges))
        self.domain_subtypes = set(d.get("domain-subtypes", []))
        self.range_subtypes = set(d.get("range-subtypes", []))
        self.cardinality = d.get("cardinality", "many")  # "one" | "many"
        self.inverse = d.get("inverse", "")
        self.must_wikilink = bool(d.get("must-wikilink", False))
        self.label = d.get("label", self.name)
        self.inverse_label = d.get("inverse-label", self.inverse)
        self.description = d.get("description", "")

    def in_domain(self, ent: str) -> bool:
        return ent in self.domains

    def in_range(self, ent: str) -> bool:
        return ent in self.ranges

    @property
    def is_single(self) -> bool:
        return self.cardinality == "one"


class Field:
    """frontmatter フィールド1件。required（必須か）と kind（値の種別）を保持する。

    kind の意味は ontology.yaml 冒頭のコメントが正本。`enum` は enum-ref が指す
    状態機械の語彙（stages/statuses/outcomes）で検証する。"""
    __slots__ = ("name", "required", "kind", "enum_ref")

    def __init__(self, d: dict):
        self.name = d["name"]
        self.required = bool(d.get("required", False))
        self.kind = d.get("kind", "text")
        self.enum_ref = d.get("enum-ref", "")


class StructuredField:
    """構造化フィールド1件（行の集まりを持つ frontmatter キー）の宣言。

    平坦な key: value でも record→record の relation でもない第三の形。行のキー（必須か・値の種別）を
    宣言し、hwlint がこの宣言に照らして行の形を検証する。判定(judgments)・成功基準(success-criteria)・
    実測(measurements) が該当する。仕様の正本は ontology.yaml の structured-fields 節。"""
    __slots__ = ("name", "domains", "label", "description", "keys", "keys_by_name")

    def __init__(self, name: str, d: dict):
        self.name = name
        self.domains = _as_set(d.get("domain", []))
        self.label = d.get("label", name)
        self.description = d.get("description", "")
        self.keys = [StructuredKey(k) for k in d.get("keys", [])]
        self.keys_by_name = {k.name: k for k in self.keys}

    def in_domain(self, ent: str) -> bool:
        return ent in self.domains


class StructuredKey:
    """構造化フィールドの行1キー分の宣言。

    kind は ref（同レコードの ref-field が指す集合の要素）／enum（enum-ref の語彙）／number／text。"""
    __slots__ = ("name", "required", "kind", "enum_ref", "ref_field")

    def __init__(self, d: dict):
        self.name = d["name"]
        self.required = bool(d.get("required", False))
        self.kind = d.get("kind", "text")
        self.enum_ref = d.get("enum-ref", "")
        self.ref_field = d.get("ref-field", "")


class Attachment:
    """付随物1種。親レコードに従属し、独自のID体系を持たない成果物の宣言。

    ファイル名は `<親レコードID><suffix>.md`、置き場は親エンティティの dir（宣言せず導出する）。
    レコード(entities)ではないので board/list/index の集計には現れないが、relations には参加する。
    種別の解決は suffix でおこなう（ID_RE は緩めない）。

    `parent_relation` は「親を指す関係」（domain=自身・range=親種別・cardinality one）を
    relations から解決したもの。RELATIONS の構築後に束ねる（下記 _bind_parent_relations）。
    フィールド名をコードに書かずに済ませつつ、候補が1本に定まることは _selfcheck が担保する。"""
    __slots__ = ("name", "label", "parent", "suffix", "description", "fields", "subtypes",
                 "templates", "parent_relation")

    def __init__(self, name: str, d: dict):
        self.name = name
        self.label = d.get("label", name)
        self.parent = d["parent"]
        self.suffix = d["suffix"]
        self.description = d.get("description", "")
        self.fields = [Field(f) for f in d.get("fields", [])]
        self.subtypes = [s["name"] for s in d.get("subtypes", [])]
        # サブタイプ → 基にした雛形パス（/planning の雛形選択の正本）
        self.templates = {s["name"]: s.get("template", "") for s in d.get("subtypes", [])}
        self.parent_relation = None         # RELATIONS 構築後に _bind_parent_relations が入れる

    def parent_of(self, stem: str) -> str:
        """付随物のステムから親レコードIDを返す（suffix を剥がす）。"""
        return stem[: -len(self.suffix)] if stem.endswith(self.suffix) else ""


class Provenance:
    """出典（不変層 sources/ への参照）の宣言。relation ではなくレコードの属性。

    確信度の根拠鎖 `H の履歴 → LEARN → sources/<file>` の最後の一歩を機械可読にする。"""
    __slots__ = ("field", "domains", "cardinality", "base_dir", "must_body_link",
                 "required_for_types", "fictional_header_scan_lines")

    def __init__(self, d: dict):
        self.field = d.get("field", "sources")
        self.domains = _as_set(d.get("domain", ["LEARN"]))
        self.cardinality = d.get("cardinality", "many")
        self.base_dir = d.get("base-dir", "sources")
        self.must_body_link = bool(d.get("must-body-link", False))
        self.required_for_types = set(d.get("required-for-types", []))
        self.fictional_header_scan_lines = int(d.get("fictional-header-scan-lines", 12))

    def in_domain(self, ent: str) -> bool:
        return ent in self.domains


class Immutability:
    """凍結（不変ルール6）の適用範囲の宣言。

    「実施済み」の判定（trigger_relation でこのレコードを指す相手が在るか）と、実施後に
    書き換えを禁じる本文節・frontmatter キーを持つ。教義（CLAUDE.md 不変ルール6）と実装が
    同じ宣言を指すようにするための型 — 凍結範囲をコードに直書きすると、規約文だけ直して
    実装が置き去りになる（実際そうなっていた）。"""
    __slots__ = ("trigger_relation", "sections", "fields")

    def __init__(self, d: dict):
        self.trigger_relation = d.get("trigger-relation", "")
        self.sections = list(d.get("sections", []))
        self.fields = list(d.get("fields", []))


def _subtype_names(entity: str) -> list:
    return [s["name"] for s in load()["entities"][entity]["subtypes"]]


def _h_role(role: str) -> set:
    return {s["name"] for s in load()["entities"]["H"]["subtypes"] if s.get("role") == role}


# ── エンティティ種別ごとの type 語彙(enum) ───────────────────────────
H_TYPES = set(_subtype_names("H"))
TEST_TYPES = set(_subtype_names("TEST"))
LEARN_TYPES = set(_subtype_names("LEARN"))
DEC_TYPES = set(_subtype_names("DEC"))

# エンティティ種別 → dir / id-infix
ENTITY_INFIXES = list(load()["entities"].keys())           # ["H", "TEST", "LEARN", "DEC"]
ID_RE = re.compile(r"^[A-Z0-9]+-(?:" + "|".join(map(re.escape, ENTITY_INFIXES)) + r")-\d+$")
# エンティティ種別 → レコード置き場（wiki/ 配下のサブディレクトリ）。records.py の探索が使う。
ENTITY_DIRS = {ent: e["dir"] for ent, e in load()["entities"].items()}
RECORD_DIRS = tuple(ENTITY_DIRS.values())                  # ("hypotheses","tests","learnings","decisions")

# ── frontmatter フィールド（スキーマ＝契約） ─────────────────────────
FIELDS = {ent: [Field(f) for f in e.get("fields", [])] for ent, e in load()["entities"].items()}
FIELDS_BY_NAME = {ent: {f.name: f for f in fs} for ent, fs in FIELDS.items()}
REQUIRED_FIELDS = {ent: [f.name for f in fs if f.required] for ent, fs in FIELDS.items()}

# ── 付随物（レコードではないが型付きリンクに参加するノード） ──────────
# FIELDS を entities 限定のまま保つのは意図的（gen_ontology_doc がキーで entities を引くため）。
# 両者を束ねた NODE_* を別に用意し、種別非依存の検証はそちらを引く。
ATTACHMENTS = {name: Attachment(name, d) for name, d in (load().get("attachments") or {}).items()}
ATTACHMENT_NAMES = list(ATTACHMENTS)                       # ["SCRIPT"]
ATTACHMENT_SUFFIXES = {a.suffix: a.name for a in ATTACHMENTS.values()}
# 付随物 → 置き場（親エンティティの dir を導出。宣言しない＝ドリフト防止）
ATTACHMENT_DIRS = {a.name: ENTITY_DIRS[a.parent] for a in ATTACHMENTS.values()}

# ノード種別 = エンティティ ∪ 付随物（関係の domain/range に書ける種別）
NODE_NAMES = ENTITY_INFIXES + ATTACHMENT_NAMES
NODE_FIELDS_BY_NAME = {**FIELDS_BY_NAME,
                       **{a.name: {f.name: f for f in a.fields} for a in ATTACHMENTS.values()}}

# ── H サブタイプの価値連鎖上の役割 ──────────────────────────────────
CUSTOMER_TYPES = _h_role("customer")     # {状況・行動仮説}
PROBLEM_TYPES = _h_role("problem")       # {課題仮説}
VALUE_TYPES = _h_role("solution")        # {ソリューション仮説}
WILLING_TYPES = _h_role("market")        # {市場スケール仮説}
TEAM_TYPES = _h_role("team")             # {自分たち仮説}
SOLUTION_TYPES = VALUE_TYPES | WILLING_TYPES

# list の mermaid subgraph / タイプ別テーブル: (key, heading, chain-label, {type})
LIST_GROUPS = [(s["key"], s["name"], s["chain-label"], {s["name"]})
               for s in load()["entities"]["H"]["subtypes"]]

# ── 状態機械 ────────────────────────────────────────────────────────
_SM = load()["state-machines"]
STAGES = set(_SM["stages"]["order"])
STAGE_ORDER = list(_SM["stages"]["order"])
STAGE_NAMES = dict(_SM["stages"]["names"])
STAGE_FOCUS = {stage: set(types) for stage, types in _SM["stage-focus"].items()}
_IW = _SM.get("importance-weights", {})
IMPORTANCE_FOCUS = _IW.get("focus", 8)      # 重点タイプの重要度
IMPORTANCE_OTHER = _IW.get("other", 4)      # 非重点タイプの重要度

_STATUS_LIST = _SM["statuses"]
STATUSES = {s["name"] for s in _STATUS_LIST}
STATUS_ORDER = [s["name"] for s in _STATUS_LIST]
STATUS_EMOJI = {s["name"]: s["emoji"] for s in _STATUS_LIST}

# 学び(LEARN)の検証判定（frontmatter outcome）。
_OUTCOME_LIST = _SM.get("outcomes", [])
OUTCOMES = {o["name"] for o in _OUTCOME_LIST}
OUTCOME_ORDER = [o["name"] for o in _OUTCOME_LIST]
OUTCOME_DESC = {o["name"]: o.get("description", "") for o in _OUTCOME_LIST}

# TEST/LEARN のデータ種別（frontmatter data）。架空判定の正本。
_DATA_KIND_LIST = _SM.get("data-kinds", [])
DATA_KINDS = {d["name"] for d in _DATA_KIND_LIST}
DATA_KIND_ORDER = [d["name"] for d in _DATA_KIND_LIST]
DATA_KIND_DESC = {d["name"]: d.get("description", "") for d in _DATA_KIND_LIST}
# 判定コードが生文字列を撒かないための定数（語彙自体の正本は上の data-kinds）
DATA_REAL = "real"
DATA_SIMULATED = "simulated"
# データ種別を宣言できるレコード種別（fields 宣言から導出＝二重管理を作らない）
DATA_FIELD = "data"

# 成功基準の比較演算子（success-criteria.op の語彙）。実測を左辺に置いて評価する。
CRITERIA_OPS = list(_SM.get("criteria-ops", []))
_OPS = {">=": lambda a, b: a >= b, ">": lambda a, b: a > b,
        "<=": lambda a, b: a <= b, "<": lambda a, b: a < b,
        "==": lambda a, b: a == b, "!=": lambda a, b: a != b}


def satisfies(value: float, op: str, threshold: float) -> bool:
    """実測 value が基準（op threshold）を満たすか。未知の演算子は False（語彙は _selfcheck が担保）。"""
    fn = _OPS.get(op)
    return bool(fn and fn(value, threshold))


# 実測から導いた判定と著者の判定を突き合わせる方針（judgment-check）。方針の正本は ontology.yaml。
_JC = _SM.get("judgment-check", {})
TRUTH_OUTCOMES = set(_JC.get("truth-outcomes", []))   # 真偽判定を名乗る outcome（検算・被覆の対象）
OUTCOME_SUPPORTED = _JC.get("supported", "支持")
OUTCOME_REFUTED = _JC.get("refuted", "反証")

# enum フィールドの enum-ref → 語彙集合（check_fields・構造化フィールドの行検証が引く）
ENUM_REFS = {"stages": STAGES, "statuses": STATUSES, "outcomes": OUTCOMES,
             "data-kinds": DATA_KINDS, "criteria-ops": set(CRITERIA_OPS)}

CONFIDENCE_MIN = _SM["confidence"]["min"]
CONFIDENCE_MAX = _SM["confidence"]["max"]
# 確信度の帯 [{range, meaning}, ...]（確信度スケールの目安。ontology.md 生成に使う）
CONFIDENCE_BANDS = list(_SM["confidence"].get("bands", []))
FICTIONAL_CAP = _SM["confidence"].get("fictional-cap", 8)
FICTIONAL_MARKERS = tuple(_SM["confidence"].get("fictional-markers", ("架空", "シミュレーション")))
# status → 確信度の許容域 {status: {"min"/"max": n}}（status↔confidence 矛盾検出に使う）
STATUS_BOUNDS = {k: dict(v) for k, v in _SM["confidence"].get("status-bounds", {}).items()}
# 確信度の帯 → 要求する証拠の階梯の最低段 [(min_confidence, floor_name), ...]（強い順に評価）
EVIDENCE_FLOOR = sorted(
    ((e["min-confidence"], e["floor"]) for e in _SM["confidence"].get("evidence-floor", [])),
    reverse=True)
# evidence-floor を要求される最小の確信度（これ未満の帯は階梯タグを要求しない）
EVIDENCE_FLOOR_MIN_CONFIDENCE = min((c for c, _ in EVIDENCE_FLOOR), default=CONFIDENCE_MAX + 1)

# ── 陳腐化（時間軸）の閾値。数値は自動で下げない＝可視化のみ ──────────
_STALE = _SM.get("staleness", {})
STALENESS_CONFIDENCE_DAYS = int(_STALE.get("confidence-days", 180))
STALENESS_TEST_DAYS = int(_STALE.get("test-days", 14))

# 証拠の階梯（序列あり）＋補助タグ（序列外）。本文タグは 〈…〉 で書く。
# YAML 要素は {name, desc} 辞書でも name のみの文字列でも読める（後方互換）。


def _tag_name(x):
    return x["name"] if isinstance(x, dict) else x


def _tag_desc(x):
    return x.get("desc", "") if isinstance(x, dict) else ""


EVIDENCE_LADDER = [_tag_name(x) for x in _SM["evidence-ladder"]]
EVIDENCE_AUX = [_tag_name(x) for x in _SM.get("evidence-aux", [])]
# 証拠種別 → 説明（ontology.md 生成に使う。説明が無ければ空文字）。
EVIDENCE_LADDER_DESC = {_tag_name(x): _tag_desc(x) for x in _SM["evidence-ladder"]}
EVIDENCE_AUX_DESC = {_tag_name(x): _tag_desc(x) for x in _SM.get("evidence-aux", [])}
# 階梯上の順位（0=最弱）。0件は補助タグ。確信度×証拠の整合チェック（hwlint）に使う。
EVIDENCE_RANK = {name: i for i, name in enumerate(EVIDENCE_LADDER)}
# 本文の根拠セルで許容される証拠種別タグ（山括弧つき。階梯＋補助）。
EVIDENCE_TAGS = tuple(f"〈{t}〉" for t in EVIDENCE_LADDER + EVIDENCE_AUX)

# ── 関係 ────────────────────────────────────────────────────────────
RELATIONS = [Relation(d) for d in load()["relations"]]
RELATIONS_BY_FIELD = {r.field: r for r in RELATIONS}


def _parent_relation_candidates(a: Attachment) -> list:
    """付随物 a の「親を指す関係」候補（domain=自身のみ・range=親種別のみ・cardinality one）。"""
    return [r for r in RELATIONS
            if r.domains == {a.name} and r.ranges == {a.parent} and r.is_single]


def _bind_parent_relations() -> None:
    """付随物に親を指す関係を束ねる（RELATIONS 構築後に1回）。候補が1本かは _selfcheck が検証する。"""
    for a in ATTACHMENTS.values():
        candidates = _parent_relation_candidates(a)
        a.parent_relation = candidates[0] if len(candidates) == 1 else None


_bind_parent_relations()

# ── プロヴェナンス（出典）────────────────────────────────────────────
PROVENANCE = Provenance(load().get("provenance", {}))

# ── 構造化フィールド（行の集まりを持つ frontmatter キー）──────────────
STRUCTURED_FIELDS = {name: StructuredField(name, d)
                     for name, d in (load().get("structured-fields") or {}).items()}
# エンティティ種別 → その種別が持てる構造化フィールド（宣言の domain から導出）
STRUCTURED_BY_ENTITY = {ent: [s for s in STRUCTURED_FIELDS.values() if s.in_domain(ent)]
                        for ent in ENTITY_INFIXES}

# ── 凍結（不変ルール6）の適用範囲。宣言の無いエンティティは凍結しない ──────
IMMUTABLE = {ent: Immutability(e["immutable"])
             for ent, e in load()["entities"].items() if e.get("immutable")}

# ── リーンキャンバス（仮説検証への写像。レコードでなくビュー） ──────────
# 各 block は H サブタイプの役割(role)へ対応。ブロック検証状態は対応 role の H から射影する。
_LC = load().get("lean-canvas", {})
LEAN_CANVAS_BLOCKS = list(_LC.get("blocks", []))                 # [{key,label,en,maps-to-role,sketch-order}]
LEAN_CANVAS_BLOCK_STATUS = list(_LC.get("block-status", []))     # [{name,from}]
LEAN_CANVAS_STAGE_LENS = dict(_LC.get("stage-lens", {}))         # {block-key: {early,scale}}
LEAN_CANVAS_VALIDATION_ORDER = _LC.get("validation-order", "")
LEAN_CANVAS_DIR = _LC.get("artifact-dir", "lean-canvas")         # SVG 成果物の置き場（wiki/ からの相対）
# role → H サブタイプ名（写像ドキュメント生成・整合チェック用）。role の正本は entities.H.subtypes.role。
H_ROLES = {s.get("role") for s in load()["entities"]["H"]["subtypes"] if s.get("role")}


def h_types_for_role(role: str) -> set:
    """指定 role を持つ H サブタイプ名の集合（写像の解決に使う）。"""
    return _h_role(role)


def _selfcheck() -> int:
    """ontology.yaml がパースでき、期待どおりの定数を導出できるか点検する。"""
    load()
    assert H_TYPES and TEST_TYPES and DEC_TYPES, "type enum が空"
    assert STATUS_ORDER and set(STATUS_ORDER) == STATUSES, "status 定義の不整合"
    assert STAGE_FOCUS.keys() == STAGES, "stage-focus と stages が不一致"
    assert len(LIST_GROUPS) == len(H_TYPES), "LIST_GROUPS の件数不一致"
    assert OUTCOMES, "outcomes 定義が空"
    # データ種別（架空判定の正本）。コード側の定数が語彙から外れていないこと
    assert DATA_KINDS, "data-kinds 定義が空"
    assert {DATA_REAL, DATA_SIMULATED} <= DATA_KINDS, "DATA_REAL/DATA_SIMULATED が data-kinds に無い"
    for r in RELATIONS:
        assert r.domains <= set(NODE_NAMES) and r.ranges <= set(NODE_NAMES), \
            f"{r.name} の domain/range 不正"
        assert r.cardinality in ("one", "many"), f"{r.name} の cardinality 不正"
    # フィールド宣言（スキーマ＝契約）の整合。エンティティと付随物は同じ契約に従うので
    # 1つのループで見る（種別ごとに書き分けると、付随物側だけ検査が1つ欠ける等の穴が空く）。
    declared_fields = list(FIELDS.items()) + [(a.name, a.fields) for a in ATTACHMENTS.values()]
    for ent, fields in declared_fields:
        assert fields, f"{ent} に fields 宣言が無い"
        names = [f.name for f in fields]
        assert len(names) == len(set(names)), f"{ent} の fields に重複キー"
        assert "id" in names, f"{ent} の fields に id が無い"
        for f in fields:
            if f.kind == "enum":
                assert f.enum_ref in ENUM_REFS, f"{ent}.{f.name} の enum-ref '{f.enum_ref}' が未知"
            if f.kind == "relation":
                assert f.name in RELATIONS_BY_FIELD, f"{ent}.{f.name} は relations に宣言が無い"
            if f.kind == "provenance":
                assert f.name == PROVENANCE.field, f"{ent}.{f.name} は provenance.field と不一致"
            if f.kind == "structured":
                sf = STRUCTURED_FIELDS.get(f.name)
                assert sf, f"{ent}.{f.name} は structured-fields に宣言が無い"
                assert sf.in_domain(ent), f"structured-fields.{f.name} の domain に {ent} が無い"
    # 関係は必ずどこかの fields に現れる（宣言したのに frontmatter キーとして未登録＝死んだ関係を防ぐ）
    for r in RELATIONS:
        for ent in r.domains:
            assert r.field in NODE_FIELDS_BY_NAME.get(ent, {}), \
                f"関係 {r.name} の field '{r.field}' が {ent} の fields に無い"
    # 付随物: 親が実在エンティティか／suffix が正しい形か／ID_RE と衝突しないか
    assert not (set(ATTACHMENT_NAMES) & set(ENTITY_INFIXES)), "付随物名がエンティティ種別と衝突"
    assert len(ATTACHMENT_SUFFIXES) == len(ATTACHMENT_NAMES), "付随物の suffix が重複"
    for a in ATTACHMENTS.values():
        assert a.parent in ENTITY_INFIXES, f"付随物 {a.name} の parent '{a.parent}' が未知のエンティティ"
        assert a.suffix.startswith("-") and len(a.suffix) > 1, f"付随物 {a.name} の suffix 不正"
        assert a.subtypes, f"付随物 {a.name} に subtypes が無い"
        # 宣言した雛形が実在すること。この検証があってはじめて `template:` が「正本」を名乗れる
        # （雛形をリネームしても誰も気づかない、という状態を作らない）。
        for subtype, tmpl in a.templates.items():
            assert tmpl, f"{a.name}.{subtype} に template の宣言が無い"
            assert (ONTOLOGY_PATH.parent / tmpl).is_file(), \
                f"{a.name}.{subtype} の template '{tmpl}' が存在しない"
        # 付随物のステムがレコードIDとして解釈されないこと（records/attachments の分離の前提）
        assert not ID_RE.match(f"PREFIX-{a.parent}-001{a.suffix}"), \
            f"付随物 {a.name} の suffix がレコードID(ID_RE)と衝突する"
        # 「親を指す関係」が一意に定まること。lint はフィールド名を書かずこの導出に頼るので、
        # 候補が0本（親への関係の宣言漏れ）でも2本以上（どちらが親ポインタか曖昧）でも壊れる。
        candidates = _parent_relation_candidates(a)
        assert len(candidates) == 1, \
            (f"付随物 {a.name} の親を指す関係（{a.name}→{a.parent}・cardinality one）が"
             f"{len(candidates)}本ある（1本に定める）")
    # プロヴェナンス
    assert PROVENANCE.domains <= set(ENTITY_INFIXES), "provenance の domain 不正"
    for ent in PROVENANCE.domains:
        assert PROVENANCE.field in FIELDS_BY_NAME[ent], \
            f"provenance.field '{PROVENANCE.field}' が {ent} の fields に無い"
        assert PROVENANCE.required_for_types <= set(_subtype_names(ent)), \
            f"provenance.required-for-types に {ent} のサブタイプでない値がある"
    # 構造化フィールド: domain が実在種別か／行のキー宣言が引ける参照先を持つか／
    # フィールド自体が entities.*.fields に kind: structured で登録されているか（死んだ宣言を防ぐ）
    for name, sf in STRUCTURED_FIELDS.items():
        assert sf.domains <= set(ENTITY_INFIXES), f"structured-fields.{name} の domain 不正"
        assert sf.keys, f"structured-fields.{name} に keys 宣言が無い"
        for ent in sf.domains:
            f = FIELDS_BY_NAME[ent].get(name)
            assert f and f.kind == "structured", \
                f"structured-fields.{name} が {ent}.fields に kind: structured で登録されていない"
        for k in sf.keys:
            assert k.kind in ("ref", "enum", "number", "text"), \
                f"structured-fields.{name}.{k.name} の kind '{k.kind}' が未知"
            if k.kind == "enum":
                assert k.enum_ref in ENUM_REFS, \
                    f"structured-fields.{name}.{k.name} の enum-ref '{k.enum_ref}' が未知"
            if k.kind == "ref":
                assert k.ref_field in RELATIONS_BY_FIELD, \
                    f"structured-fields.{name}.{k.name} の ref-field '{k.ref_field}' が relations に無い"
                for ent in sf.domains:
                    assert k.ref_field in FIELDS_BY_NAME[ent], \
                        f"structured-fields.{name}.{k.name} の ref-field が {ent}.fields に無い"
    # 判定の検算（judgment-check）で使う語彙が outcomes の部分集合であること
    assert TRUTH_OUTCOMES <= OUTCOMES, "judgment-check.truth-outcomes に outcomes 外の値がある"
    assert {OUTCOME_SUPPORTED, OUTCOME_REFUTED} <= TRUTH_OUTCOMES, \
        "judgment-check の supported/refuted が truth-outcomes に無い"
    assert CRITERIA_OPS and set(CRITERIA_OPS) <= set(_OPS), "criteria-ops に評価器の無い演算子がある"
    # 凍結範囲: 宣言したキー・関係が実在すること（規約文だけ直して実装が置き去りになるのを防ぐ）
    for ent, im in IMMUTABLE.items():
        assert ent in ENTITY_INFIXES, f"immutable を宣言した '{ent}' が未知のエンティティ"
        assert im.sections or im.fields, f"{ent}.immutable が何も凍結していない"
        rel = RELATIONS_BY_FIELD.get(im.trigger_relation)
        assert rel, f"{ent}.immutable の trigger-relation '{im.trigger_relation}' が relations に無い"
        assert ent in rel.ranges, \
            f"{ent}.immutable の trigger-relation '{im.trigger_relation}' は {ent} を指さない"
        for key in im.fields:
            assert key in FIELDS_BY_NAME[ent], f"{ent}.immutable の fields '{key}' が {ent} の fields に無い"
    # リーンキャンバス写像: 各 block の maps-to-role が実在する H role か（role ドリフト検出）
    for b in LEAN_CANVAS_BLOCKS:
        assert b.get("maps-to-role") in H_ROLES, f"lean-canvas block {b.get('key')} の maps-to-role 不正"
    for bk in LEAN_CANVAS_STAGE_LENS:
        assert bk in {b["key"] for b in LEAN_CANVAS_BLOCKS}, f"stage-lens の未知ブロック {bk}"
    print(f"ontology.yaml OK (version={load().get('version')}): entities={list(load()['entities'])} "
          f"attachments={ATTACHMENT_NAMES} "
          f"relations={[r.name for r in RELATIONS]} provenance={PROVENANCE.field} "
          f"stages={STAGE_ORDER} statuses={STATUS_ORDER} outcomes={OUTCOME_ORDER} "
          f"lean-canvas-blocks={[b['key'] for b in LEAN_CANVAS_BLOCKS]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(_selfcheck())
