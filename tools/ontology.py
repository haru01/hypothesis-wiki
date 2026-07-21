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


class Relation:
    """関係型1件。domain→range・cardinality・inverse を保持する。"""
    __slots__ = ("name", "field", "domain", "range", "domain_subtypes", "range_subtypes",
                 "cardinality", "inverse", "must_wikilink", "label", "inverse_label", "description")

    def __init__(self, d: dict):
        self.name = d["name"]
        self.field = d["field"]
        self.domain = d["domain"]                       # エンティティ種別 "H"/"ACT"/"DEC"
        self.range = d["range"]
        self.domain_subtypes = set(d.get("domain-subtypes", []))
        self.range_subtypes = set(d.get("range-subtypes", []))
        self.cardinality = d.get("cardinality", "many")  # "one" | "many"
        self.inverse = d.get("inverse", "")
        self.must_wikilink = bool(d.get("must-wikilink", False))
        self.label = d.get("label", self.name)
        self.inverse_label = d.get("inverse-label", self.inverse)
        self.description = d.get("description", "")

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
DEC_TYPES = set(_subtype_names("DEC"))

# エンティティ種別 → dir / id-infix
ENTITY_INFIXES = list(load()["entities"].keys())           # ["H", "ACT", "DEC"]
ID_RE = re.compile(r"^[A-Z0-9]+-(?:" + "|".join(map(re.escape, ENTITY_INFIXES)) + r")-\d+$")

# ── H サブタイプの価値連鎖上の役割 ──────────────────────────────────
CUSTOMER_TYPES = _h_role("customer")     # {状況・行動仮説}
PROBLEM_TYPES = _h_role("problem")       # {課題仮説}
VALUE_TYPES = _h_role("solution")        # {ソリューション仮説}
WILLING_TYPES = _h_role("market")        # {買ってもらえる仮説}
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

_STATUS_LIST = _SM["statuses"]
STATUSES = {s["name"] for s in _STATUS_LIST}
STATUS_ORDER = [s["name"] for s in _STATUS_LIST]
STATUS_EMOJI = {s["name"]: s["emoji"] for s in _STATUS_LIST}

CONFIDENCE_MIN = _SM["confidence"]["min"]
CONFIDENCE_MAX = _SM["confidence"]["max"]
FICTIONAL_CAP = _SM["confidence"].get("fictional-cap", 8)
EVIDENCE_LADDER = list(_SM["evidence-ladder"])

# ── 関係 ────────────────────────────────────────────────────────────
RELATIONS = [Relation(d) for d in load()["relations"]]
RELATIONS_BY_FIELD = {r.field: r for r in RELATIONS}


def _selfcheck() -> int:
    """ontology.yaml がパースでき、期待どおりの定数を導出できるか点検する。"""
    load()
    assert H_TYPES and ACT_TYPES and DEC_TYPES, "type enum が空"
    assert STATUS_ORDER and set(STATUS_ORDER) == STATUSES, "status 定義の不整合"
    assert STAGE_FOCUS.keys() == STAGES, "stage-focus と stages が不一致"
    assert len(LIST_GROUPS) == len(H_TYPES), "LIST_GROUPS の件数不一致"
    for r in RELATIONS:
        assert r.domain in ENTITY_INFIXES and r.range in ENTITY_INFIXES, f"{r.name} の domain/range 不正"
        assert r.cardinality in ("one", "many"), f"{r.name} の cardinality 不正"
    print(f"ontology.yaml OK: entities={list(load()['entities'])} "
          f"relations={[r.name for r in RELATIONS]} stages={STAGE_ORDER} statuses={STATUS_ORDER}")
    return 0


if __name__ == "__main__":
    raise SystemExit(_selfcheck())
