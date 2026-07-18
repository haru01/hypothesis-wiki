#!/usr/bin/env python3
"""仮説検証Wiki の決定論的 lint。

CLAUDE.md の不変ルールのうち機械検証可能なものだけをチェックする。
意味的チェック（矛盾する仮説・長期放置など）は /lint スキル（LLM）が担い、両者で併用する。
"""
import argparse
import re
import sys
from dataclasses import dataclass
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


class Project:
    def __init__(self, root: Path):
        self.root = root
        self.slug = root.name
        self.wiki = root / "wiki"
        self.records = {}
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
        log_path = self.wiki / "log.md"
        self.log = log_path.read_text(encoding="utf-8") if log_path.exists() else ""

    @property
    def prefix(self) -> str:
        for rid in self.records:
            m = re.match(r"^([A-Z0-9]+)-", rid)
            if m:
                return m.group(1)
        return self.slug.upper()


def check_id_matches_filename(project) -> list:
    """frontmatter id はファイル名と完全一致（接頭辞つき）。規約外ファイル名も報告。"""
    problems = []
    for stem, (path, fm, _) in project.records.items():
        fid = fm.get("id", "")
        if fid != stem:
            problems.append(Problem("error", str(path), "id-filename",
                                    f"frontmatter id '{fid}' がファイル名 '{stem}' と一致しない"))
    for p in project.stray:
        problems.append(Problem("warning", str(p), "id-filename",
                                "レコード名が ID 規約（<PREFIX>-H/ACT/DEC-NNN）に合わない"))
    return problems


def check_vocabulary(project) -> list:
    """status・type・stage・confidence の語彙/範囲を規約に照らして検証する。"""
    problems = []
    for stem, (path, fm, _) in project.records.items():
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


CHECKS = [check_id_matches_filename, check_vocabulary]


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
