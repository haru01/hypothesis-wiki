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


@lru_cache(maxsize=1)
def load() -> dict:
    """ontology.yaml をパースして dict で返す（プロセス内で1回だけ読む）。"""
    return yaml.safe_load(ONTOLOGY_PATH.read_text(encoding="utf-8"))


def _as_set(value) -> set:
    """domain/range を集合に正規化する（文字列単一 or 配列の両方を許す）。"""
    return set(value) if isinstance(value, (list, tuple, set)) else {value}


class Relation:
    """関係型1件。domain→range・cardinality・inverse を保持する。

    domain/range は複数エンティティ種別を許す（例 hypotheses は ACT/LEARN）。
    集合は `domains`/`ranges`、表示用の文字列は `domain`/`range`（"ACT/LEARN"）で持つ。
    種別判定は `in_domain(ent)`/`in_range(ent)` を使う。"""
    __slots__ = ("name", "field", "domains", "ranges", "domain", "range",
                 "domain_subtypes", "range_subtypes",
                 "cardinality", "inverse", "must_wikilink", "label", "inverse_label", "description")

    def __init__(self, d: dict):
        self.name = d["name"]
        self.field = d["field"]
        self.domains = _as_set(d["domain"])             # エンティティ種別の集合 {"ACT"} / {"ACT","LEARN"}
        self.ranges = _as_set(d["range"])
        self.domain = "/".join(sorted(self.domains))    # 表示用（例 "ACT/LEARN"）
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


def _subtype_names(entity: str) -> list:
    return [s["name"] for s in load()["entities"][entity]["subtypes"]]


def _h_role(role: str) -> set:
    return {s["name"] for s in load()["entities"]["H"]["subtypes"] if s.get("role") == role}


# ── エンティティ種別ごとの type 語彙(enum) ───────────────────────────
H_TYPES = set(_subtype_names("H"))
ACT_TYPES = set(_subtype_names("ACT"))
LEARN_TYPES = set(_subtype_names("LEARN"))
DEC_TYPES = set(_subtype_names("DEC"))

# エンティティ種別 → dir / id-infix
ENTITY_INFIXES = list(load()["entities"].keys())           # ["H", "ACT", "DEC"]
ID_RE = re.compile(r"^[A-Z0-9]+-(?:" + "|".join(map(re.escape, ENTITY_INFIXES)) + r")-\d+$")

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

CONFIDENCE_MIN = _SM["confidence"]["min"]
CONFIDENCE_MAX = _SM["confidence"]["max"]
FICTIONAL_CAP = _SM["confidence"].get("fictional-cap", 8)
FICTIONAL_MARKERS = tuple(_SM["confidence"].get("fictional-markers", ("架空", "シミュレーション")))
# status → 確信度の許容域 {status: {"min"/"max": n}}（status↔confidence 矛盾検出に使う）
STATUS_BOUNDS = {k: dict(v) for k, v in _SM["confidence"].get("status-bounds", {}).items()}
# 確信度の帯 → 要求する証拠の階梯の最低段 [(min_confidence, floor_name), ...]（強い順に評価）
EVIDENCE_FLOOR = sorted(
    ((e["min-confidence"], e["floor"]) for e in _SM["confidence"].get("evidence-floor", [])),
    reverse=True)

# 証拠の階梯（序列あり）＋補助タグ（序列外）。本文タグは 〈…〉 で書く。
EVIDENCE_LADDER = list(_SM["evidence-ladder"])
EVIDENCE_AUX = list(_SM.get("evidence-aux", []))
# 階梯上の順位（0=最弱）。0件は補助タグ。確信度×証拠の整合チェック（hwlint）に使う。
EVIDENCE_RANK = {name: i for i, name in enumerate(EVIDENCE_LADDER)}
# 本文の根拠セルで許容される証拠種別タグ（山括弧つき。階梯＋補助）。
EVIDENCE_TAGS = tuple(f"〈{t}〉" for t in EVIDENCE_LADDER + EVIDENCE_AUX)

# ── 関係 ────────────────────────────────────────────────────────────
RELATIONS = [Relation(d) for d in load()["relations"]]
RELATIONS_BY_FIELD = {r.field: r for r in RELATIONS}

# ── リーンキャンバス（仮説検証への写像。レコードでなくビュー） ──────────
# 各 block は H サブタイプの役割(role)へ対応。ブロック検証状態は対応 role の H から射影する。
_LC = load().get("lean-canvas", {})
LEAN_CANVAS_BLOCKS = list(_LC.get("blocks", []))                 # [{key,label,en,maps-to-role,sketch-order}]
LEAN_CANVAS_BLOCK_STATUS = list(_LC.get("block-status", []))     # [{name,from}]
LEAN_CANVAS_STAGE_LENS = dict(_LC.get("stage-lens", {}))         # {block-key: {early,scale}}
LEAN_CANVAS_VALIDATION_ORDER = _LC.get("validation-order", "")
# role → H サブタイプ名（写像ドキュメント生成・整合チェック用）。role の正本は entities.H.subtypes.role。
H_ROLES = {s.get("role") for s in load()["entities"]["H"]["subtypes"] if s.get("role")}


def h_types_for_role(role: str) -> set:
    """指定 role を持つ H サブタイプ名の集合（写像の解決に使う）。"""
    return _h_role(role)


def _selfcheck() -> int:
    """ontology.yaml がパースでき、期待どおりの定数を導出できるか点検する。"""
    load()
    assert H_TYPES and ACT_TYPES and DEC_TYPES, "type enum が空"
    assert STATUS_ORDER and set(STATUS_ORDER) == STATUSES, "status 定義の不整合"
    assert STAGE_FOCUS.keys() == STAGES, "stage-focus と stages が不一致"
    assert len(LIST_GROUPS) == len(H_TYPES), "LIST_GROUPS の件数不一致"
    for r in RELATIONS:
        assert r.domains <= set(ENTITY_INFIXES) and r.ranges <= set(ENTITY_INFIXES), \
            f"{r.name} の domain/range 不正"
        assert r.cardinality in ("one", "many"), f"{r.name} の cardinality 不正"
    # リーンキャンバス写像: 各 block の maps-to-role が実在する H role か（role ドリフト検出）
    for b in LEAN_CANVAS_BLOCKS:
        assert b.get("maps-to-role") in H_ROLES, f"lean-canvas block {b.get('key')} の maps-to-role 不正"
    for bk in LEAN_CANVAS_STAGE_LENS:
        assert bk in {b["key"] for b in LEAN_CANVAS_BLOCKS}, f"stage-lens の未知ブロック {bk}"
    print(f"ontology.yaml OK: entities={list(load()['entities'])} "
          f"relations={[r.name for r in RELATIONS]} stages={STAGE_ORDER} statuses={STATUS_ORDER} "
          f"lean-canvas-blocks={[b['key'] for b in LEAN_CANVAS_BLOCKS]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(_selfcheck())
