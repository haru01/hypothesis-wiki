#!/usr/bin/env python3
"""仮説検証Wiki のレコードモデル層（frontmatter/履歴/log のパーサと Project）。

hwlint.py（lint）・gen_views.py（ビュー生成）・check_testcard_immutable.py（不変チェック）が
共有する「レコードの読み取り」だけをここに集約する。lint と view 生成が同じモデルを使えるよう、
従来 hwlint.py に同居していたモデル層をここへ抽出した（linter へのモデル依存＝密結合の解消）。

- 語彙(enum)・型・関係・状態機械の定義は ontology.yaml が唯一の正本。ここには再定義しない。
- 値は「素の文字列」契約で返す（下流は文字列前提で .isdigit()/parse_id_array を使う）。
"""
import re
import sys
from functools import cached_property
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent))
from ontology import (  # noqa: E402
    ID_RE, STAGE_FOCUS, IMPORTANCE_FOCUS, IMPORTANCE_OTHER,
)

HISTORY_HEADER = "## 確信度履歴"
TESTCARD_RE = re.compile(r"## テストカード.*?(?=## 学習カード|\Z)", re.DOTALL)


def parse_frontmatter(text: str) -> dict:
    """frontmatter（--- で囲まれた YAML ブロック）を dict で返す。

    値は従来どおり「素の文字列」契約で返す（下流は文字列前提で .isdigit()/parse_id_array を使う）。
    yaml.BaseLoader を使うことで、引用符内コロン・複数行値・コメントを正しく扱いつつ、
    型強制（int 化・真偽値化・日付化・いわゆる Norway 問題）を避けて元の文字列表現を保つ。
    空値（None）は ""、配列は "[a, b]" の文字列に正規化して契約を維持する。
    パースできない frontmatter は空 dict を返す（従来同様、寛容に扱う）。
    """
    m = re.match(r"^---\n(.*?)\n---(?:\n|$)", text, re.DOTALL)
    if not m:
        return {}
    try:
        data = yaml.load(m.group(1), Loader=yaml.BaseLoader)
    except yaml.YAMLError:
        return {}
    if not isinstance(data, dict):
        return {}
    fm = {}
    for key, value in data.items():
        if value is None:
            fm[str(key)] = ""
        elif isinstance(value, list):
            fm[str(key)] = "[" + ", ".join(str(v) for v in value) + "]"
        else:
            fm[str(key)] = str(value)
    return fm


def parse_id_array(value: str) -> list:
    return [x.strip() for x in value.strip("[]").split(",") if x.strip()]


def entity_of(stem: str) -> str:
    """レコード stem からエンティティ種別（H/ACT/DEC）を返す。該当なしは空。"""
    for infix in ("H", "ACT", "DEC"):
        if f"-{infix}-" in stem:
            return infix
    return ""


def strip_frontmatter(text: str) -> str:
    return re.sub(r"^---\n.*?\n---\n", "", text, count=1, flags=re.DOTALL)


def strip_comments(text: str) -> str:
    """HTMLコメント（<!-- ... -->）を除去する。コメント内の例示 wikilink は
    Obsidian でもグラフ辺を作らないため、リンク検査の対象から外す。"""
    return re.sub(r"<!--.*?-->", "", text, flags=re.DOTALL)


def testcard(text: str) -> str:
    """ACT 本文からテストカード節（## テストカード〜## 学習カードの手前）を逐語抽出する。"""
    m = TESTCARD_RE.search(text)
    return m.group(0) if m else ""


def parse_history(body: str) -> list:
    rows, in_section = [], False
    for line in body.splitlines():
        if line.startswith("## "):
            in_section = line.strip() == HISTORY_HEADER
            continue
        if in_section and line.lstrip().startswith("|"):
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            if len(cells) >= 5 and re.match(r"\d{4}-\d{2}-\d{2}$", cells[0]):
                rows.append({"date": cells[0], "confidence": cells[1],
                             "status": cells[2], "reason": cells[3], "activity": cells[4]})
    return rows


def referenced_ids(project, field, infix=None, where=None) -> set:
    """`field`（frontmatter の関係キー）で指されている終点IDの集合を返す。

    infix を渡すと始点レコード種別（例 "-ACT-"）で、where(fm)->bool を渡すと始点 frontmatter で
    さらに絞る。関係グラフの入次数（被参照）を「有無」で見る用途の共有ヘルパ。"""
    out = set()
    for stem, (_, fm, _) in project.records.items():
        if infix and infix not in stem:
            continue
        if where and not where(fm):
            continue
        out.update(parse_id_array(fm.get(field, "")))
    return out


def importance(fm, stage) -> int:
    """仮説の重要度。手動指定(1-10)が優先。auto は現ステージの重点タイプ=IMPORTANCE_FOCUS・
    それ以外=IMPORTANCE_OTHER（重みの正本は ontology.yaml の importance-weights）。"""
    imp = fm.get("importance", "auto")
    if imp != "auto" and imp.isdigit():
        return int(imp)
    return IMPORTANCE_FOCUS if fm.get("type") in STAGE_FOCUS.get(stage, set()) else IMPORTANCE_OTHER


def current_slug(repo: Path):
    """projects/current.md の current-project を返す（無ければ None）。プロジェクト解決の共有ヘルパ。"""
    cur = repo / "projects" / "current.md"
    if not cur.exists():
        return None
    m = re.search(r"current-project:\s*(\S+)", cur.read_text(encoding="utf-8"))
    return m.group(1) if m else None


class Project:
    def __init__(self, root: Path):
        self.root = root
        self.slug = root.name
        self.wiki = root / "wiki"
        self.records = {}
        self.history = {}   # H レコードの確信度履歴を読込時に1回だけパースしてキャッシュ
        self.stray = []
        for sub in ("hypotheses", "activities", "decisions"):
            d = self.wiki / sub
            if not d.is_dir():
                continue
            for p in sorted(d.glob("*.md")):
                if not ID_RE.match(p.stem):
                    if not p.stem.endswith("-script"):
                        self.stray.append(p)
                    continue
                text = p.read_text(encoding="utf-8")
                self.records[p.stem] = (p, parse_frontmatter(text), text)
                if "-H-" in p.stem:
                    self.history[p.stem] = parse_history(text)
        log_path = self.wiki / "log.md"
        self.log = log_path.read_text(encoding="utf-8") if log_path.exists() else ""

    @cached_property
    def stage(self) -> str:
        """現在ステージ（stage.md の current-stage）。無ければ空。"""
        p = self.wiki / "stage.md"
        if p.exists():
            m = re.search(r"current-stage:\s*(\w+)", p.read_text(encoding="utf-8"))
            if m:
                return m.group(1)
        return ""

    @cached_property
    def prefix(self) -> str:
        for rid in self.records:
            m = re.match(r"^([A-Z0-9]+)-", rid)
            if m:
                return m.group(1)
        return self.slug.upper()

    def hyp_records(self):
        """仮説レコードを (stem, fm, body, history) で列挙する。history はキャッシュ済み。"""
        for stem, (_, fm, body) in self.records.items():
            if "-H-" in stem:
                yield stem, fm, body, self.history[stem]
