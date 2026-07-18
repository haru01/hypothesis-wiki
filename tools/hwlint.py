#!/usr/bin/env python3
"""仮説検証Wiki の決定論的 lint。

CLAUDE.md の不変ルールのうち機械検証可能なものだけをチェックする。
意味的チェック（矛盾する仮説・長期放置など）は /lint スキル（LLM）が担い、両者で併用する。
"""
import argparse
import re
import sys
from dataclasses import dataclass
from functools import cached_property
from pathlib import Path

STATUSES = {"未検証", "検証中", "検証済み", "反証"}
STAGES = {"CPF", "FPF", "PSF", "SPF", "PMF"}
H_TYPES = {"状況・行動仮説", "課題仮説", "ソリューション仮説", "買ってもらえる仮説", "自分たち仮説"}
ACT_TYPES = {"interview", "demo", "survey", "mvp-test", "desk-research", "self-reflection"}
DEC_TYPES = {"stage-transition", "pivot", "persevere", "rollback", "kill"}
ID_RE = re.compile(r"^[A-Z0-9]+-(?:H|ACT|DEC)-\d+$")


@dataclass
class Problem:
    level: str    # "error" | "warning"
    where: str    # レコードID または パス
    check: str    # チェック名（kebab-case）
    message: str


def parse_frontmatter(text: str) -> dict:
    m = re.match(r"^---\n(.*?)\n---(?:\n|$)", text, re.DOTALL)
    if not m:
        return {}
    fm = {}
    for line in m.group(1).splitlines():
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        fm[key.strip()] = re.sub(r"\s+#.*$", "", value).strip()
    return fm


def parse_id_array(value: str) -> list:
    return [x.strip() for x in value.strip("[]").split(",") if x.strip()]


def strip_frontmatter(text: str) -> str:
    return re.sub(r"^---\n.*?\n---\n", "", text, count=1, flags=re.DOTALL)


def strip_comments(text: str) -> str:
    """HTMLコメント（<!-- ... -->）を除去する。コメント内の例示 wikilink は
    Obsidian でもグラフ辺を作らないため、リンク検査の対象から外す。"""
    return re.sub(r"<!--.*?-->", "", text, flags=re.DOTALL)


HISTORY_HEADER = "## 確信度履歴"


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


def check_id_matches_filename(project) -> list:
    """frontmatter id はファイル名と完全一致（接頭辞つき）。規約外ファイル名も報告。"""
    problems = []
    for stem, (path, fm, _) in project.records.items():
        fid = fm.get("id", "")
        if fid != stem:
            problems.append(Problem("error", stem, "id-filename",
                                    f"frontmatter id '{fid}' がファイル名 '{stem}' と一致しない"))
    for p in project.stray:
        problems.append(Problem("warning", str(p), "id-filename",
                                "レコード名が ID 規約（<PREFIX>-H/ACT/DEC-NNN）に合わない"))
    return problems


def check_vocabulary(project) -> list:
    """status・type・stage・confidence の語彙/範囲を規約に照らして検証する。"""
    problems = []
    for stem, (_, fm, _) in project.records.items():
        if "-H-" in stem:
            if fm.get("status") not in STATUSES:
                problems.append(Problem("error", stem, "vocab", f"status '{fm.get('status')}' は規約外"))
            c = fm.get("confidence", "")
            if not (c.isdigit() and 1 <= int(c) <= 10):
                problems.append(Problem("error", stem, "vocab", f"confidence '{c}' は 1-10 の整数でない"))
            if fm.get("type") not in H_TYPES:
                problems.append(Problem("error", stem, "vocab", f"type '{fm.get('type')}' は規約外"))
            imp = fm.get("importance", "auto")
            if imp != "auto" and not (imp.isdigit() and 1 <= int(imp) <= 10):
                problems.append(Problem("error", stem, "vocab", f"importance '{imp}' は auto か 1-10"))
        if "-ACT-" in stem and fm.get("type") not in ACT_TYPES:
            problems.append(Problem("error", stem, "vocab", f"type '{fm.get('type')}' は規約外"))
        if "-DEC-" in stem and fm.get("type") not in DEC_TYPES:
            problems.append(Problem("error", stem, "vocab", f"type '{fm.get('type')}' は規約外"))
        if ("-H-" in stem or "-ACT-" in stem) and fm.get("stage") not in STAGES:
            problems.append(Problem("error", stem, "vocab", f"stage '{fm.get('stage')}' は規約外"))
    return problems


EVIDENCE_RE = re.compile(r"\[\[([A-Z0-9]+-(?:ACT|DEC)-\d+)\]\]")


def check_history_consistency(project) -> list:
    """不変ルール2: frontmatter の confidence/status は確信度履歴テーブルの最終行と一致する。"""
    problems = []
    for stem, fm, _, rows in project.hyp_records():
        if not rows:
            problems.append(Problem("error", stem, "history", "確信度履歴テーブルが無い/パースできない"))
            continue
        last = rows[-1]
        if last["confidence"] != fm.get("confidence"):
            problems.append(Problem("error", stem, "history",
                f"frontmatter confidence={fm.get('confidence')} と履歴最終行 {last['confidence']} が不一致"))
        if last["status"] != fm.get("status"):
            problems.append(Problem("error", stem, "history",
                f"frontmatter status={fm.get('status')} と履歴最終行 {last['status']} が不一致"))
    return problems


def check_evidence_links(project) -> list:
    """不変ルール1: 初期行以降の確信度・ステータス変更は必ず実在する ACT/DEC に紐づく。"""
    problems = []
    for stem, _, _, rows in project.hyp_records():
        for i, row in enumerate(rows):
            if i == 0:
                continue  # 初期作成行のみ根拠レコード免除（desk-research を書くのは任意）
            ids = EVIDENCE_RE.findall(row["activity"])
            if not ids:
                problems.append(Problem("error", stem, "evidence",
                    f"履歴 {row['date']} 行（確信度{row['confidence']}）に [[ACT/DEC]] の証拠リンクが無い"))
            for rid in ids:
                if rid not in project.records:
                    problems.append(Problem("error", stem, "evidence",
                        f"履歴の証拠 [[{rid}]] のレコードが存在しない"))
    return problems


WIKILINK_RE = re.compile(r"\[\[([^\]|#]+)(?:[|#][^\]]*)?\]\]")


def check_frontmatter_refs(project) -> list:
    """frontmatter の ID 参照は接頭辞つきで実在するレコードを指す。
    ACT の hypotheses（配列）／ DEC の based-on（配列）／ H の derived-from（単一・省略可）。"""
    problems = []
    prefix = project.prefix
    for stem, (_, fm, _) in project.records.items():
        groups = []
        if "-ACT-" in stem and fm.get("hypotheses"):
            groups.append(("hypotheses", parse_id_array(fm["hypotheses"])))
        if "-DEC-" in stem and fm.get("based-on"):
            groups.append(("based-on", parse_id_array(fm["based-on"])))
        if "-H-" in stem and fm.get("derived-from"):
            groups.append(("derived-from", [fm["derived-from"].strip()]))
        for label, ids in groups:
            for rid in ids:
                if not rid.startswith(prefix + "-"):
                    problems.append(Problem("error", stem, "refs",
                        f"frontmatter {label} '{rid}' が接頭辞つきでない（{prefix}-… に統一する）"))
                elif rid not in project.records:
                    problems.append(Problem("error", stem, "refs",
                        f"frontmatter {label} '{rid}' のレコードが存在しない"))
    return problems


def check_wikilinks(project) -> list:
    """本文の wikilink が vault 内で解決すること。schema層（/入り）への wikilink は規約違反。"""
    problems = []
    all_names = {p.stem for p in project.root.parent.glob("*/wiki/**/*.md")}
    for stem, (_, _, body) in project.records.items():
        for target in WIKILINK_RE.findall(strip_comments(strip_frontmatter(body))):
            target = target.strip()
            if "/" in target:
                problems.append(Problem("error", stem, "wikilink",
                    f"[[{target}]] — schema層への参照は wikilink でなく相対mdリンクで書く規約"))
            elif target not in all_names:
                problems.append(Problem("error", stem, "wikilink", f"[[{target}]] が解決しない（リンク切れ）"))
    return problems


INDEX_ROW_RE = re.compile(r"^\|\s*\[\[([A-Z0-9]+-H-\d+)\]\]\s*\|[^|]*\|\s*(\d+)\s*\|\s*([^|]+?)\s*\|")


def check_id_sequence(project) -> list:
    """不変ルール5: ID 重複禁止。欠番は log.md の取り下げ記録があれば正常、なければ warning。"""
    problems = []
    prefix = project.prefix
    seen = {}
    for stem, (_, fm, _) in project.records.items():
        fid = fm.get("id", stem)
        if fid in seen:
            problems.append(Problem("error", stem, "id-seq", f"id '{fid}' が {seen[fid]} と重複"))
        seen[fid] = stem
    log_lines = project.log.splitlines()
    for kind in ("H", "ACT", "DEC"):
        pat = re.compile(rf"^{re.escape(prefix)}-{kind}-(\d+)$")
        nums = sorted(int(m.group(1)) for rid in project.records if (m := pat.match(rid)))
        if not nums:
            continue
        for missing in sorted(set(range(1, max(nums) + 1)) - set(nums)):
            mid = f"{prefix}-{kind}-{missing:03d}"
            if not any(mid in line and "取り下げ" in line for line in log_lines):
                problems.append(Problem("warning", mid, "id-seq",
                                        "欠番だが log.md に取り下げ記録が見当たらない"))
    return problems


def check_log_sync(project) -> list:
    """不変ルール2: 履歴テーブルへの追記（2行目以降）は log.md にも記録される。

    log.md は接頭辞つき ID（SELF-H-001）でも短縮 ID（H-001）でも書かれうる。
    確信度変更は `確信度X→Y` でも短縮 `4→6` でも記録されうるので、両方を許容する。
    """
    problems = []
    log_lines = project.log.splitlines()
    for stem, _, _, rows in project.hyp_records():
        m = re.search(r"(H-\d+)$", stem)
        short = m.group(1) if m else stem
        for row in rows[1:]:
            conf = row["confidence"]
            pattern = rf"(?:→\s*|確信度[^|]*?){re.escape(conf)}(?!\d)"
            if not any((stem in line or short in line) and re.search(pattern, line)
                       for line in log_lines):
                problems.append(Problem("warning", stem, "log-sync",
                    f"履歴 {row['date']} 行（確信度{conf}）に対応する log.md 記録が見当たらない"))
    return problems


def check_index_sync(project) -> list:
    """index.md の確信度・ステータスがレコード本体と一致する（lint 項目5の機械部分）。"""
    problems = []
    index_path = project.wiki / "index.md"
    if not index_path.exists():
        return [Problem("warning", "index.md", "index-sync", "index.md が無い")]
    for line in index_path.read_text(encoding="utf-8").splitlines():
        m = INDEX_ROW_RE.match(line.strip())
        if not m:
            continue
        rid, conf, status = m.group(1), m.group(2), m.group(3)
        if rid not in project.records:
            problems.append(Problem("error", "index.md", "index-sync", f"[[{rid}]] のレコードが存在しない"))
            continue
        fm = project.records[rid][1]
        if fm.get("confidence") != conf or fm.get("status") != status:
            problems.append(Problem("error", "index.md", "index-sync",
                f"[[{rid}]] index表（確信度{conf}/{status}）とレコード"
                f"（確信度{fm.get('confidence')}/{fm.get('status')}）が不一致"))
    return problems


FICTIONAL_MARKERS = ("架空", "シミュレーション")


def check_fictional_cap(project) -> list:
    """架空/シミュレーションデータ由来の確信度は上限8（9-10 は実観測に限る）。"""
    problems = []
    fictional_acts = {stem for stem, (_, _, body) in project.records.items()
                      if "-ACT-" in stem and any(m in body for m in FICTIONAL_MARKERS)}
    for stem, fm, _, rows in project.hyp_records():
        c = fm.get("confidence", "0")
        if not c.isdigit() or int(c) < 9:
            continue
        last_ids = EVIDENCE_RE.findall(rows[-1]["activity"]) if rows else []
        hit = [rid for rid in last_ids if rid in fictional_acts]
        if hit:
            problems.append(Problem("error", stem, "fictional-cap",
                f"confidence={c} だが直近の根拠 {hit} は架空/シミュレーションデータ（上限8）"))
    return problems


EVIDENCE_TAGS = ("〈発言〉", "〈自認〉", "〈実コスト〉", "〈行動〉", "〈支払い〉", "〈二次〉", "〈架空〉")


def check_evidence_tags(project) -> list:
    """証拠の階梯: 履歴2行目以降の根拠セルには証拠種別タグを付ける（新規約のため warning 運用）。"""
    problems = []
    for stem, _, _, rows in project.hyp_records():
        for row in rows[1:]:
            if not any(tag in row["reason"] for tag in EVIDENCE_TAGS):
                problems.append(Problem("warning", stem, "evidence-tag",
                    f"履歴 {row['date']} 行の根拠に証拠種別タグ（〈自認〉〈実コスト〉等）が無い"))
    return problems


CHECKS = [check_id_matches_filename, check_vocabulary, check_history_consistency, check_evidence_links,
          check_frontmatter_refs, check_wikilinks,
          check_id_sequence, check_log_sync, check_index_sync, check_fictional_cap,
          check_evidence_tags]


def lint_project(root: Path) -> list:
    project = Project(root)
    problems = []
    for check in CHECKS:
        problems.extend(check(project))
    return problems


def resolve_targets(repo: Path, args) -> list:
    projects_dir = repo / "projects"
    if args.all:
        return [d for d in sorted(projects_dir.iterdir()) if (d / "wiki").is_dir()]
    slug = args.project
    if not slug:
        current = (projects_dir / "current.md").read_text(encoding="utf-8")
        m = re.search(r"current-project:\s*(\S+)", current)
        slug = m.group(1) if m else None
    if not slug or not (projects_dir / slug / "wiki").is_dir():
        sys.exit(f"プロジェクトが見つからない: {slug!r}")
    return [projects_dir / slug]


def main() -> int:
    ap = argparse.ArgumentParser(description="仮説検証Wiki の決定論的 lint")
    ap.add_argument("--project", help="対象プロジェクト slug（省略時は projects/current.md の current-project）")
    ap.add_argument("--all", action="store_true", help="全プロジェクトを対象にする")
    ap.add_argument("--repo", default=".", help="リポジトリルート")
    args = ap.parse_args()
    repo = Path(args.repo).resolve()
    exit_code = 0
    for root in resolve_targets(repo, args):
        problems = lint_project(root)
        errors = [p for p in problems if p.level == "error"]
        warnings = [p for p in problems if p.level == "warning"]
        print(f"== {root.name}: error {len(errors)} / warning {len(warnings)}")
        for p in problems:
            print(f"  [{p.level}] {p.check} | {p.where} | {p.message}")
        if errors:
            exit_code = 1
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
