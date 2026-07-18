# 競合分析にもとづく強化（machine-enforced 化）実装計画

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 競合分析（[docs/competitive-analysis.md](../../competitive-analysis.md)）が挙げた最優先の弱点——「規約に書いた＝守られる、ではない」——を潰し、差別化の核（単一確信度×証拠への強制紐づけ）を**仕組みで**裏打ちする。

**Architecture:** 3フェーズ構成。①決定論 lint スクリプト `tools/hwlint.py`（Python標準ライブラリのみ・単一ファイル）と git diff ベースのテストカード不変チェッカーを作り、**git pre-commit フック**（`.githooks/`、`core.hooksPath` で有効化）と **Claude Code フック**（`.claude/settings.json`: sources/ 書き込みガード・ターン終了時 lint・フック自動有効化）の二層で強制する。**CI は使わない（ユーザー方針）**。②確信度の付け方の規律（証拠の階梯・架空データ上限8・判断保留の正当化）をスキーマに型として入れる。③AGENTS.md 併存と README のポジショニング刷新で到達範囲と旗印を整える。

**Tech Stack:** Python 3.9+（標準ライブラリのみ）、unittest、git hooks（core.hooksPath）、Claude Code hooks（.claude/settings.json）、Markdown。

## 背景 — 競合分析 → 強化ポイントの対応表

| # | 競合分析の指摘 | 強化ポイント | 対応タスク |
|---|---|---|---|
| A1 | 3-C① 最優先の弱点: 規約の実効性（Böckeler: エージェントは規約を無視しうる） | 不変ルールの機械検証（決定論 lint） | Task 1–5 |
| A2 | 3-C① 同上 | /lint をハイブリッド化（機械＋意味） | Task 6 |
| A3 | 3-A② EviBound 型「証拠なしに状態遷移させない」の商用空白 | コミット時（git pre-commit）とセッション内（Claude Code フック）の二層で不変ルールを強制（テストカード事後書き換え検出・sources/ ガード・log 追記のみ含む） | Task 7–8 |
| B1 | 3-C③ 確信度1〜10の主観性の裏打ちが弱い | 証拠の階梯（発言<自認<実コスト<行動<支払い）を型に | Task 9 |
| B2 | self #3 架空データ上限8が規約化されていない | 上限8をスキーマ＋lintに | Task 5, 9 |
| B3 | self #2 「検証したが上がらない」状態が表現できない | 判断保留の正当化を明文化 | Task 9 |
| B4 | B1 の機械化 | 証拠種別タグの lint（warning 運用） | Task 10 |
| C1 | 3-C② 単一エージェント特化（obsidian-wiki は多エージェント、Spec Kit は35+） | AGENTS.md 併存（agent-agnostic の第一歩） | Task 11 |
| C2 | 3-D① 「確信度×強制紐づけ」を旗印に／3-D③ Gap 5 主張は裏取りまで抑える | README ポジショニング刷新（誠実な但し書き付き） | Task 12 |

**計画外（別トラック）:** 3-C④ 実案件での効果実証（運用課題であり本計画の成果物でない）／競合分析 §5 の未解決リサーチ（`/deep-research` 第3ラウンドとして別途）／多エージェント完全対応（AGENTS.md 以降は需要を見て判断）。

## Global Constraints

- Python 3.9+ **標準ライブラリのみ**。pip 依存・requirements 追加は禁止（リポジトリのゼロ依存・プレーンテキスト性を保つ）。
- **CI（GitHub Actions 等）は使わない**（ユーザー方針）。強制はローカルの git pre-commit フックと Claude Code フックの二層で行う。`--no-verify` 等での迂回は技術的に可能だが、規律の道具として許容する。
- 記述はすべて日本語。ID・frontmatter キー・コード識別子は原文のまま。
- `projects/<slug>/sources/` は読み取り専用。`wiki/log.md` は追記のみ。
- **Task 8（CLAUDE.md・templates/ の変更）は schema 層の変更**。適用前に diff をユーザーに提示し、承認を得てからコミットする。
- 既存 self レコードの確信度・ステータスには触れない。機械修正してよいのはリンク切れ・`id` 表記などの整合のみ。確信度に関わる違反が見つかったら修正せずユーザーへ報告する。
- 新規約（証拠種別タグ）は既存レコードに遡及適用しない。lint では error でなく **warning** として扱う。
- コミットメッセージは種別接頭辞つき日本語（例 `feat(lint): …`、`docs: …`）。既存履歴のスタイルに合わせる。

## File Structure

| ファイル | 責務 |
|---|---|
| `tools/hwlint.py` | 決定論 lint 本体（新規・単一ファイル）。frontmatter/履歴テーブルのパースとチェック関数群＋CLI |
| `tools/check_testcard_immutable.py` | git diff ベースのテストカード不変チェック（新規・PR 用） |
| `tests/test_hwlint.py` | 上記2ツールの unittest（新規） |
| `.githooks/pre-commit` | コミット時の強制: hwlint・テストカード不変・log 追記のみ・sources 不変・（tools/tests 変更時のみ）unittest（新規） |
| `.claude/settings.json` | Claude Code フック: SessionStart で hooksPath 自動設定／sources/ 書き込みガード／Stop 時 hwlint（新規） |
| `tools/hooks/guard_sources.py`・`tools/hooks/stop_lint.py` | Claude Code フックの実体（新規） |
| `.claude/skills/lint/SKILL.md` | ハイブリッド化（改訂） |
| `CLAUDE.md` / `templates/hypothesis.md` / `templates/activity.md` / `templates/decision.md` / `.claude/skills/ingest/SKILL.md` | 証拠の階梯・上限8・判断保留・タグ書式（改訂、承認ゲート付き） |
| `AGENTS.md` | 非 Claude エージェント向け入口（新規） |
| `README.md` | ポジショニング刷新（改訂） |

---

## フェーズ1 — 規約の機械的強制

### Task 1: hwlint 骨格 — パーサ・CLI・ID/語彙チェック

**Files:**
- Create: `tools/hwlint.py`
- Create: `tests/test_hwlint.py`

**Interfaces:**
- Consumes: なし（初回タスク）
- Produces: `Problem(level, where, check, message)` dataclass ／ `parse_frontmatter(text) -> dict` ／ `parse_id_array(value) -> list[str]` ／ `class Project`（`.records: dict[stem, (path, fm, body)]`・`.log: str`・`.prefix: str`・`.wiki: Path`・`.root: Path`・`.stray: list[Path]`）／ `lint_project(root: Path) -> list[Problem]` ／ `CHECKS: list`（後続タスクはここに関数を追加する）

- [ ] **Step 1: 失敗するテストを書く**

`tests/test_hwlint.py` を新規作成:

```python
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

TOOLS = Path(__file__).resolve().parent.parent / "tools"
sys.path.insert(0, str(TOOLS))
import hwlint  # noqa: E402


def write(root: Path, rel: str, text: str):
    p = root / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding="utf-8")


def make_project(tmp: str, files: dict) -> Path:
    root = Path(tmp) / "projects" / "demo"
    if "wiki/log.md" not in files:
        write(root, "wiki/log.md", "")
    for rel, text in files.items():
        write(root, rel, text)
    return root


def hyp(id="DEMO-H-001", status="未検証", confidence="1", rows=None, type="課題仮説"):
    rows_text = "\n".join(rows or ["| 2026-07-01 | 1 | 未検証 | 初期作成 | — |"])
    return f"""---
id: {id}
title: テスト仮説
type: {type}
status: {status}
confidence: {confidence}
stage: CPF
importance: auto
---

# テスト仮説

## 仮説文（反証可能な形式で）

> テスト。

## 確信度履歴

| 日付 | 確信度 | ステータス | 根拠 | 活動 |
|---|---|---|---|---|
{rows_text}
"""


def act(id="DEMO-ACT-001", type="interview", hypotheses="[DEMO-H-001]", body="対象仮説: [[DEMO-H-001]]"):
    return f"""---
id: {id}
title: テスト活動
type: {type}
date: 2026-07-01
stage: CPF
hypotheses: {hypotheses}
---

# テスト活動

{body}
"""


class IdFilenameTest(unittest.TestCase):
    def test_mismatch_detected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = make_project(tmp, {"wiki/hypotheses/DEMO-H-001.md": hyp(id="H-001")})
            self.assertTrue(any(p.check == "id-filename" for p in hwlint.lint_project(root)))

    def test_match_ok(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = make_project(tmp, {"wiki/hypotheses/DEMO-H-001.md": hyp()})
            self.assertEqual([p for p in hwlint.lint_project(root) if p.check == "id-filename"], [])


class VocabularyTest(unittest.TestCase):
    def test_bad_status_and_confidence_detected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = make_project(tmp, {"wiki/hypotheses/DEMO-H-001.md": hyp(status="確認中", confidence="11")})
            checks = [p.check for p in hwlint.lint_project(root)]
            self.assertGreaterEqual(checks.count("vocab"), 2)

    def test_valid_record_ok(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = make_project(tmp, {
                "wiki/hypotheses/DEMO-H-001.md": hyp(),
                "wiki/activities/DEMO-ACT-001.md": act(),
            })
            self.assertEqual([p for p in hwlint.lint_project(root) if p.check == "vocab"], [])


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: テストが失敗することを確認する**

Run: `python3 -m unittest discover -s tests -v`
Expected: FAIL（`ModuleNotFoundError: No module named 'hwlint'`）

- [ ] **Step 3: `tools/hwlint.py` を実装する**

```python
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
```

- [ ] **Step 4: テストが通ることを確認する**

Run: `python3 -m unittest discover -s tests -v`
Expected: PASS（4 tests OK）

- [ ] **Step 5: コミット**

```bash
git add tools/hwlint.py tests/test_hwlint.py
git commit -m "feat(lint): 決定論lint hwlint.py の骨格（ID/語彙チェック・CLI・テスト）"
```

### Task 2: 証拠なき確信度変更の機械検出（差別化の心臓部）

**Files:**
- Modify: `tools/hwlint.py`（関数追加）
- Modify: `tests/test_hwlint.py`（テスト追加）

**Interfaces:**
- Consumes: Task 1 の `Project`・`Problem`・`CHECKS`・`hyp()`/`act()` フィクスチャ
- Produces: `parse_history(body) -> list[dict]`（keys: `date, confidence, status, reason, activity`）／ `EVIDENCE_RE`（`[[<PREFIX>-ACT/DEC-NNN]]` 抽出）／ `check_history_consistency` ／ `check_evidence_links`

- [ ] **Step 1: 失敗するテストを書く**

`tests/test_hwlint.py` に追加:

```python
class HistoryConsistencyTest(unittest.TestCase):
    def test_frontmatter_history_mismatch_detected(self):
        rows = ["| 2026-07-01 | 1 | 未検証 | 初期作成 | — |",
                "| 2026-07-05 | 5 | 検証中 | 〈自認〉手応え | [[DEMO-ACT-001]] |"]
        with tempfile.TemporaryDirectory() as tmp:
            root = make_project(tmp, {
                "wiki/hypotheses/DEMO-H-001.md": hyp(status="未検証", confidence="1", rows=rows),
                "wiki/activities/DEMO-ACT-001.md": act(),
            })
            self.assertTrue(any(p.check == "history" for p in hwlint.lint_project(root)))


class EvidenceLinkTest(unittest.TestCase):
    def test_change_without_evidence_detected(self):
        rows = ["| 2026-07-01 | 1 | 未検証 | 初期作成 | — |",
                "| 2026-07-05 | 5 | 検証中 | 手応え | — |"]
        with tempfile.TemporaryDirectory() as tmp:
            root = make_project(tmp, {
                "wiki/hypotheses/DEMO-H-001.md": hyp(status="検証中", confidence="5", rows=rows)})
            self.assertTrue(any(p.check == "evidence" for p in hwlint.lint_project(root)))

    def test_evidence_record_must_exist(self):
        rows = ["| 2026-07-01 | 1 | 未検証 | 初期作成 | — |",
                "| 2026-07-05 | 5 | 検証中 | 〈自認〉 | [[DEMO-ACT-999]] |"]
        with tempfile.TemporaryDirectory() as tmp:
            root = make_project(tmp, {
                "wiki/hypotheses/DEMO-H-001.md": hyp(status="検証中", confidence="5", rows=rows)})
            self.assertTrue(any(p.check == "evidence" and "DEMO-ACT-999" in p.message
                                for p in hwlint.lint_project(root)))

    def test_change_with_existing_evidence_ok(self):
        rows = ["| 2026-07-01 | 1 | 未検証 | 初期作成 | — |",
                "| 2026-07-05 | 5 | 検証中 | 〈自認〉 | [[DEMO-ACT-001]] |"]
        with tempfile.TemporaryDirectory() as tmp:
            root = make_project(tmp, {
                "wiki/hypotheses/DEMO-H-001.md": hyp(status="検証中", confidence="5", rows=rows),
                "wiki/activities/DEMO-ACT-001.md": act(),
            })
            self.assertEqual([p for p in hwlint.lint_project(root) if p.check == "evidence"], [])
```

- [ ] **Step 2: テストが失敗することを確認する**

Run: `python3 -m unittest discover -s tests -v`
Expected: FAIL（history / evidence の Problem が検出されない）

- [ ] **Step 3: `tools/hwlint.py` に実装を追加する**

`CHECKS = [...]` の**手前**に追加し、`CHECKS` を `CHECKS = [check_id_matches_filename, check_vocabulary, check_history_consistency, check_evidence_links]` に更新:

```python
HISTORY_HEADER = "## 確信度履歴"
EVIDENCE_RE = re.compile(r"\[\[([A-Z0-9]+-(?:ACT|DEC)-\d+)\]\]")


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


def check_history_consistency(project) -> list:
    """不変ルール2: frontmatter の confidence/status は確信度履歴テーブルの最終行と一致する。"""
    problems = []
    for stem, (path, fm, body) in project.records.items():
        if "-H-" not in stem:
            continue
        rows = parse_history(body)
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
    for stem, (path, fm, body) in project.records.items():
        if "-H-" not in stem:
            continue
        for i, row in enumerate(parse_history(body)):
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
```

- [ ] **Step 4: テストが通ることを確認する**

Run: `python3 -m unittest discover -s tests -v`
Expected: PASS（8 tests OK）

- [ ] **Step 5: コミット**

```bash
git add tools/hwlint.py tests/test_hwlint.py
git commit -m "feat(lint): 証拠なき確信度変更・履歴/frontmatter不一致の機械検出"
```

### Task 3: 参照整合 — frontmatter 配列・wikilink 解決・schema層参照違反

**Files:**
- Modify: `tools/hwlint.py`
- Modify: `tests/test_hwlint.py`

**Interfaces:**
- Consumes: Task 1–2 の全インターフェース
- Produces: `WIKILINK_RE` ／ `check_frontmatter_refs` ／ `check_wikilinks`

- [ ] **Step 1: 失敗するテストを書く**

`tests/test_hwlint.py` に追加:

```python
class RefsTest(unittest.TestCase):
    def test_unprefixed_frontmatter_ref_detected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = make_project(tmp, {
                "wiki/hypotheses/DEMO-H-001.md": hyp(),
                "wiki/activities/DEMO-ACT-001.md": act(hypotheses="[H-001]"),
            })
            self.assertTrue(any(p.check == "refs" for p in hwlint.lint_project(root)))

    def test_broken_wikilink_detected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = make_project(tmp, {
                "wiki/hypotheses/DEMO-H-001.md": hyp(),
                "wiki/activities/DEMO-ACT-001.md": act(body="対象仮説: [[DEMO-H-404]]"),
            })
            self.assertTrue(any(p.check == "wikilink" and "DEMO-H-404" in p.message
                                for p in hwlint.lint_project(root)))

    def test_schema_layer_wikilink_detected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = make_project(tmp, {
                "wiki/hypotheses/DEMO-H-001.md": hyp(),
                "wiki/activities/DEMO-ACT-001.md": act(
                    body="対象仮説: [[DEMO-H-001]]\n\n根拠: [[playbooks/cpf.md]]"),
            })
            self.assertTrue(any(p.check == "wikilink" and "playbooks" in p.message
                                for p in hwlint.lint_project(root)))

    def test_valid_refs_ok(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = make_project(tmp, {
                "wiki/hypotheses/DEMO-H-001.md": hyp(),
                "wiki/activities/DEMO-ACT-001.md": act(),
            })
            problems = [p for p in hwlint.lint_project(root) if p.check in ("refs", "wikilink")]
            self.assertEqual(problems, [])
```

- [ ] **Step 2: テストが失敗することを確認する**

Run: `python3 -m unittest discover -s tests -v`
Expected: FAIL（refs / wikilink の Problem が検出されない）

- [ ] **Step 3: `tools/hwlint.py` に実装を追加する**

`CHECKS` の手前に追加し、`CHECKS` 末尾に `check_frontmatter_refs, check_wikilinks` を追加:

```python
WIKILINK_RE = re.compile(r"\[\[([^\]|#]+)(?:[|#][^\]]*)?\]\]")


def check_frontmatter_refs(project) -> list:
    """ACT の hypotheses / DEC の based-on は接頭辞つきで実在するレコードを指す。"""
    problems = []
    for stem, (path, fm, body) in project.records.items():
        refs = []
        if "-ACT-" in stem and fm.get("hypotheses"):
            refs = parse_id_array(fm["hypotheses"])
        if "-DEC-" in stem and fm.get("based-on"):
            refs = parse_id_array(fm["based-on"])
        for rid in refs:
            if not rid.startswith(project.prefix + "-"):
                problems.append(Problem("error", stem, "refs",
                    f"frontmatter 参照 '{rid}' が接頭辞つきでない（{project.prefix}-… に統一する）"))
            elif rid not in project.records:
                problems.append(Problem("error", stem, "refs",
                    f"frontmatter 参照 '{rid}' のレコードが存在しない"))
    return problems


def check_wikilinks(project) -> list:
    """本文の wikilink が vault 内で解決すること。schema層（/入り）への wikilink は規約違反。"""
    problems = []
    all_names = {p.stem for p in project.root.parent.glob("*/wiki/**/*.md")}
    for stem, (path, fm, body) in project.records.items():
        for target in WIKILINK_RE.findall(strip_frontmatter(body)):
            target = target.strip()
            if "/" in target:
                problems.append(Problem("error", stem, "wikilink",
                    f"[[{target}]] — schema層への参照は wikilink でなく相対mdリンクで書く規約"))
            elif target not in all_names:
                problems.append(Problem("error", stem, "wikilink", f"[[{target}]] が解決しない（リンク切れ）"))
    return problems
```

- [ ] **Step 4: テストが通ることを確認する**

Run: `python3 -m unittest discover -s tests -v`
Expected: PASS（12 tests OK）

- [ ] **Step 5: コミット**

```bash
git add tools/hwlint.py tests/test_hwlint.py
git commit -m "feat(lint): frontmatter配列・wikilink解決・schema層参照違反のチェック"
```

### Task 4: ID 採番・log 同期・index 同期

**Files:**
- Modify: `tools/hwlint.py`
- Modify: `tests/test_hwlint.py`

**Interfaces:**
- Consumes: Task 1–3 の全インターフェース
- Produces: `check_id_sequence` ／ `check_log_sync` ／ `check_index_sync`（`INDEX_ROW_RE` 使用）

- [ ] **Step 1: 失敗するテストを書く**

`tests/test_hwlint.py` に追加:

```python
class IdSequenceTest(unittest.TestCase):
    def test_gap_without_withdrawal_warned(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = make_project(tmp, {
                "wiki/hypotheses/DEMO-H-001.md": hyp(),
                "wiki/hypotheses/DEMO-H-003.md": hyp(id="DEMO-H-003"),
            })
            self.assertTrue(any(p.check == "id-seq" and "DEMO-H-002" in p.where
                                for p in hwlint.lint_project(root)))

    def test_gap_with_withdrawal_ok(self):
        log = "## [2026-07-02] hypothesis | DEMO-H-002 取り下げ（ユーザー判断） → レコード削除\n"
        with tempfile.TemporaryDirectory() as tmp:
            root = make_project(tmp, {
                "wiki/hypotheses/DEMO-H-001.md": hyp(),
                "wiki/hypotheses/DEMO-H-003.md": hyp(id="DEMO-H-003"),
                "wiki/log.md": log,
            })
            self.assertEqual([p for p in hwlint.lint_project(root) if p.check == "id-seq"], [])


class LogSyncTest(unittest.TestCase):
    def test_history_change_missing_in_log_warned(self):
        rows = ["| 2026-07-01 | 1 | 未検証 | 初期作成 | — |",
                "| 2026-07-05 | 5 | 検証中 | 〈自認〉 | [[DEMO-ACT-001]] |"]
        with tempfile.TemporaryDirectory() as tmp:
            root = make_project(tmp, {
                "wiki/hypotheses/DEMO-H-001.md": hyp(status="検証中", confidence="5", rows=rows),
                "wiki/activities/DEMO-ACT-001.md": act(),
            })
            self.assertTrue(any(p.check == "log-sync" for p in hwlint.lint_project(root)))

    def test_history_change_recorded_in_log_ok(self):
        rows = ["| 2026-07-01 | 1 | 未検証 | 初期作成 | — |",
                "| 2026-07-05 | 5 | 検証中 | 〈自認〉 | [[DEMO-ACT-001]] |"]
        log = "## [2026-07-05] interview | DEMO-ACT-001 実施 → DEMO-H-001 確信度1→5/検証中\n"
        with tempfile.TemporaryDirectory() as tmp:
            root = make_project(tmp, {
                "wiki/hypotheses/DEMO-H-001.md": hyp(status="検証中", confidence="5", rows=rows),
                "wiki/activities/DEMO-ACT-001.md": act(),
                "wiki/log.md": log,
            })
            self.assertEqual([p for p in hwlint.lint_project(root) if p.check == "log-sync"], [])


class IndexSyncTest(unittest.TestCase):
    def test_index_mismatch_detected(self):
        index = ("# 仮説カタログ\n\n## 課題仮説\n\n"
                 "| ID | タイトル | 確信度 | ステータス | ステージ |\n|---|---|---|---|---|\n"
                 "| [[DEMO-H-001]] | テスト仮説 | 9 | 検証済み | CPF |\n")
        with tempfile.TemporaryDirectory() as tmp:
            root = make_project(tmp, {
                "wiki/hypotheses/DEMO-H-001.md": hyp(),
                "wiki/index.md": index,
            })
            self.assertTrue(any(p.check == "index-sync" for p in hwlint.lint_project(root)))
```

- [ ] **Step 2: テストが失敗することを確認する**

Run: `python3 -m unittest discover -s tests -v`
Expected: FAIL（id-seq / log-sync / index-sync が検出されない）

- [ ] **Step 3: `tools/hwlint.py` に実装を追加する**

`CHECKS` の手前に追加し、`CHECKS` 末尾に `check_id_sequence, check_log_sync, check_index_sync` を追加:

```python
INDEX_ROW_RE = re.compile(r"^\|\s*\[\[([A-Z0-9]+-H-\d+)\]\]\s*\|[^|]*\|\s*(\d+)\s*\|\s*([^|]+?)\s*\|")


def check_id_sequence(project) -> list:
    """不変ルール5: ID 重複禁止。欠番は log.md の取り下げ記録があれば正常、なければ warning。"""
    problems = []
    seen = {}
    for stem, (path, fm, _) in project.records.items():
        fid = fm.get("id", stem)
        if fid in seen:
            problems.append(Problem("error", stem, "id-seq", f"id '{fid}' が {seen[fid]} と重複"))
        seen[fid] = stem
    log_lines = project.log.splitlines()
    for kind in ("H", "ACT", "DEC"):
        nums = sorted(int(m.group(1)) for rid in project.records
                      if (m := re.match(rf"^{re.escape(project.prefix)}-{kind}-(\d+)$", rid)))
        if not nums:
            continue
        for missing in sorted(set(range(1, max(nums) + 1)) - set(nums)):
            mid = f"{project.prefix}-{kind}-{missing:03d}"
            if not any(mid in line and "取り下げ" in line for line in log_lines):
                problems.append(Problem("warning", mid, "id-seq",
                                        "欠番だが log.md に取り下げ記録が見当たらない"))
    return problems


def check_log_sync(project) -> list:
    """不変ルール2: 履歴テーブルへの追記（2行目以降）は log.md にも記録される。"""
    problems = []
    log_lines = project.log.splitlines()
    for stem, (path, fm, body) in project.records.items():
        if "-H-" not in stem:
            continue
        related = [l.split(stem, 1)[1] for l in log_lines if stem in l]
        for row in parse_history(body)[1:]:
            if not any("確信度" in tail and row["confidence"] in tail for tail in related):
                problems.append(Problem("warning", stem, "log-sync",
                    f"履歴 {row['date']} 行（確信度{row['confidence']}）に対応する log.md 記録が見当たらない"))
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
```

- [ ] **Step 4: テストが通ることを確認する**

Run: `python3 -m unittest discover -s tests -v`
Expected: PASS（17 tests OK）

- [ ] **Step 5: コミット**

```bash
git add tools/hwlint.py tests/test_hwlint.py
git commit -m "feat(lint): ID採番・log同期・index同期のチェック"
```

### Task 5: 架空/シミュレーションデータの確信度上限8

**Files:**
- Modify: `tools/hwlint.py`
- Modify: `tests/test_hwlint.py`

**Interfaces:**
- Consumes: Task 1–4 の全インターフェース
- Produces: `FICTIONAL_MARKERS` ／ `check_fictional_cap`

- [ ] **Step 1: 失敗するテストを書く**

`tests/test_hwlint.py` に追加:

```python
class FictionalCapTest(unittest.TestCase):
    def _project(self, tmp, confidence):
        rows = ["| 2026-07-01 | 1 | 未検証 | 初期作成 | — |",
                f"| 2026-07-05 | {confidence} | 検証済み | 〈行動〉 | [[DEMO-ACT-001]] |"]
        return make_project(tmp, {
            "wiki/hypotheses/DEMO-H-001.md": hyp(status="検証済み", confidence=str(confidence), rows=rows),
            "wiki/activities/DEMO-ACT-001.md": act(
                body="対象仮説: [[DEMO-H-001]]\n\n> ⚠️ 架空のシミュレーションデータ。実証拠として扱わない。"),
        })

    def test_confidence_9_on_fictional_act_detected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = self._project(tmp, 9)
            self.assertTrue(any(p.check == "fictional-cap" for p in hwlint.lint_project(root)))

    def test_confidence_8_on_fictional_act_ok(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = self._project(tmp, 8)
            self.assertEqual([p for p in hwlint.lint_project(root) if p.check == "fictional-cap"], [])
```

- [ ] **Step 2: テストが失敗することを確認する**

Run: `python3 -m unittest discover -s tests -v`
Expected: FAIL（fictional-cap が検出されない）

- [ ] **Step 3: `tools/hwlint.py` に実装を追加する**

`CHECKS` の手前に追加し、`CHECKS` 末尾に `check_fictional_cap` を追加:

```python
FICTIONAL_MARKERS = ("架空", "シミュレーション")


def check_fictional_cap(project) -> list:
    """架空/シミュレーションデータ由来の確信度は上限8（9-10 は実観測に限る）。"""
    problems = []
    fictional_acts = {stem for stem, (_, _, body) in project.records.items()
                      if "-ACT-" in stem and any(m in body for m in FICTIONAL_MARKERS)}
    for stem, (path, fm, body) in project.records.items():
        if "-H-" not in stem:
            continue
        c = fm.get("confidence", "0")
        if not c.isdigit() or int(c) < 9:
            continue
        rows = parse_history(body)
        last_ids = EVIDENCE_RE.findall(rows[-1]["activity"]) if rows else []
        hit = [rid for rid in last_ids if rid in fictional_acts]
        if hit:
            problems.append(Problem("error", stem, "fictional-cap",
                f"confidence={c} だが直近の根拠 {hit} は架空/シミュレーションデータ（上限8）"))
    return problems
```

- [ ] **Step 4: テストが通ることを確認する**

Run: `python3 -m unittest discover -s tests -v`
Expected: PASS（19 tests OK）

- [ ] **Step 5: コミット**

```bash
git add tools/hwlint.py tests/test_hwlint.py
git commit -m "feat(lint): 架空/シミュレーションデータ由来の確信度上限8チェック"
```

### Task 6: /lint スキルのハイブリッド化と self でのベースライン実行

**Files:**
- Modify: `.claude/skills/lint/SKILL.md`

**Interfaces:**
- Consumes: `tools/hwlint.py` CLI（Task 1–5）
- Produces: /lint の新しい手順（機械チェック→意味チェックの2段構成）

- [ ] **Step 1: SKILL.md に「手順0」を追加する**

`.claude/skills/lint/SKILL.md` の「## チェック項目」の**直前**に挿入:

````markdown
## 手順0 — 決定論チェックを先に実行する

まず機械検証を走らせ、その結果をレポートの土台にする:

```bash
python3 tools/hwlint.py            # 現在のプロジェクト
python3 tools/hwlint.py --all      # 全プロジェクト
```

hwlint が機械的に担う部分（下記チェック項目のうち **1 の証拠リンク・5 の index/log 同期・8 の ID 整合・9 の架空上限の機械判定**、および status/type/stage/confidence の語彙・範囲などのスキーマ整合）は、スクリプトの出力をそのまま報告に転記する（再点検に時間を使わない）。LLM は残りの**意味的チェック**（2 孤立レコード・3 矛盾する仮説・4 長期放置・6 確信度とステータスの不整合・7 成功基準の事後書き換えの文脈判断・9 の「明示が十分か」の判断）に集中する。
````

あわせて「## 出力」の log 追記例を次に差し替える:

```markdown
- `wiki/log.md` に追記:
  `## [YYYY-MM-DD] lint | 健全性チェック実施（hwlint: error N/warning M・意味チェック: 問題K件） → 内訳`
```

- [ ] **Step 2: self 案件でベースラインを実行する**

Run: `python3 tools/hwlint.py --all`
Expected: self の実レコードに対する error/warning の一覧（0件とは限らない）。

- [ ] **Step 3: 検出結果をトリアージして機械修正だけ直す**

- **直してよいもの**: リンク切れ・`id` 表記・index の転記ミスなどの機械的整合（レコードの意味を変えない）。
- **直してはいけないもの**: 確信度・ステータスに関わる違反。これは修正せず、検出結果を最終報告に含めてユーザーの判断を仰ぐ。
- 修正した場合は `wiki/log.md` に `## [YYYY-MM-DD] lint | hwlint導入ベースライン → 機械的整合N件修正` を追記する。

- [ ] **Step 4: 再実行して機械修正分が消えたことを確認する**

Run: `python3 tools/hwlint.py --all`
Expected: 機械修正した項目が出力から消えている（確信度系の残件はそのまま）。

- [ ] **Step 5: コミット**

```bash
git add .claude/skills/lint/SKILL.md projects/
git commit -m "feat(lint): /lintをhwlint併用のハイブリッドに変更・selfベースライン適用"
```

### Task 7: テストカード不変チェッカーと git pre-commit フック

**Files:**
- Create: `tools/check_testcard_immutable.py`
- Create: `.githooks/pre-commit`
- Modify: `tests/test_hwlint.py`

**Interfaces:**
- Consumes: `tools/hwlint.py` CLI ／ git（`diff --name-only`・`show <ref>:<path>`・`show :<path>`）
- Produces: `check_testcard_immutable.py [--base <ref>] [--staged]`（exit 1 = 学習カード記入済み ACT のテストカード変更あり。`--staged` は base とステージ済み内容を比較する pre-commit モード。base 省略時 HEAD）／ `.githooks/pre-commit`（有効化: `git config core.hooksPath .githooks`）

- [ ] **Step 1: 失敗するテストを書く**

`tests/test_hwlint.py` に追加:

```python
BASE_ACT_FOR_GIT = """---
id: DEMO-ACT-001
title: テスト活動
type: interview
date: 2026-07-01
stage: CPF
hypotheses: [DEMO-H-001]
---

# テスト活動

## テストカード（検証前に記入・後から書き換えない）

- **成功基準**: 5名中3名以上が実コストを払っている。

## 学習カード（検証後に記入）

### 事実（observed）

5名に実施し、2名が実コストを払っていた。

### 解釈（inference）

成功基準は未達。
"""


class TestcardImmutableTest(unittest.TestCase):
    def _init_repo(self, repo: Path):
        run = lambda *a: subprocess.run(a, cwd=repo, check=True, capture_output=True, text=True)
        run("git", "init", "-b", "main")
        run("git", "config", "user.email", "t@example.com")
        run("git", "config", "user.name", "t")
        return run

    def _run_checker(self, repo: Path, *argv):
        return subprocess.run(
            [sys.executable, str(TOOLS / "check_testcard_immutable.py"), *argv],
            cwd=repo, capture_output=True, text=True)

    def test_rewrite_after_learning_detected(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            run = self._init_repo(repo)
            write(repo, "projects/demo/wiki/activities/DEMO-ACT-001.md", BASE_ACT_FOR_GIT)
            run("git", "add", "-A"); run("git", "commit", "-m", "base")
            write(repo, "projects/demo/wiki/activities/DEMO-ACT-001.md",
                  BASE_ACT_FOR_GIT.replace("3名以上", "1名以上"))
            run("git", "add", "-A"); run("git", "commit", "-m", "rewrite")
            result = self._run_checker(repo, "--base", "HEAD~1")
            self.assertEqual(result.returncode, 1, result.stdout + result.stderr)

    def test_learning_card_edit_allowed(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            run = self._init_repo(repo)
            write(repo, "projects/demo/wiki/activities/DEMO-ACT-001.md", BASE_ACT_FOR_GIT)
            run("git", "add", "-A"); run("git", "commit", "-m", "base")
            write(repo, "projects/demo/wiki/activities/DEMO-ACT-001.md",
                  BASE_ACT_FOR_GIT + "\n### 次のアクション\n\n- 再検証を計画する。\n")
            run("git", "add", "-A"); run("git", "commit", "-m", "learning update")
            result = self._run_checker(repo, "--base", "HEAD~1")
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_staged_rewrite_detected(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            run = self._init_repo(repo)
            write(repo, "projects/demo/wiki/activities/DEMO-ACT-001.md", BASE_ACT_FOR_GIT)
            run("git", "add", "-A"); run("git", "commit", "-m", "base")
            write(repo, "projects/demo/wiki/activities/DEMO-ACT-001.md",
                  BASE_ACT_FOR_GIT.replace("3名以上", "1名以上"))
            run("git", "add", "-A")  # コミットせずステージのみ（pre-commit 相当）
            result = self._run_checker(repo, "--staged")
            self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
```

- [ ] **Step 2: テストが失敗することを確認する**

Run: `python3 -m unittest discover -s tests -v`
Expected: FAIL（`check_testcard_immutable.py` が存在しない）

- [ ] **Step 3: `tools/check_testcard_immutable.py` を実装する**

```python
#!/usr/bin/env python3
"""不変ルール6の git 検出: 学習カード記入済み ACT のテストカードが base と比べて
書き換えられていないかをチェックする（pre-commit は --staged、レビュー時は --base <ref>）。

学習カードが未記入（検証開始前）の ACT はテストカードを直してよい。
判定はヒューリスティック（「### 事実（observed）」節に本文があるか）なので、
false positive 時は人間がレビューで判断する。
"""
import argparse
import re
import subprocess
import sys

TEST_SECTION_RE = re.compile(r"## テストカード.*?(?=## 学習カード|\Z)", re.DOTALL)
FACTS_RE = re.compile(r"### 事実（observed）(.*?)(?=###|\Z)", re.DOTALL)


def git(*args) -> subprocess.CompletedProcess:
    return subprocess.run(["git", *args], capture_output=True, text=True, check=False)


def testcard(text: str) -> str:
    m = TEST_SECTION_RE.search(text)
    return m.group(0) if m else ""


def learning_filled(text: str) -> bool:
    m = FACTS_RE.search(text)
    if not m:
        return False
    body = re.sub(r"<!--.*?-->", "", m.group(1), flags=re.DOTALL)
    lines = [l for l in body.splitlines()
             if l.strip() and not l.strip().startswith("観測した事実")]
    return bool(lines)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", default="HEAD", help="比較先の git ref（既定 HEAD）")
    ap.add_argument("--staged", action="store_true",
                    help="pre-commit モード: base とステージ済み内容（index）を比較する")
    args = ap.parse_args()
    if args.staged:
        diff = git("diff", "--cached", "--name-only", args.base)
    else:
        diff = git("diff", "--name-only", f"{args.base}...HEAD")
    changed = [f for f in diff.stdout.splitlines()
               if "/wiki/activities/" in f and f.endswith(".md")]
    failures = []
    for f in changed:
        base_show = git("show", f"{args.base}:{f}")
        if base_show.returncode != 0:
            continue  # 新規ファイルは対象外
        if args.staged:
            head_show = git("show", f":{f}")
            if head_show.returncode != 0:
                continue  # 削除は対象外
            head_text = head_show.stdout
        else:
            try:
                head_text = open(f, encoding="utf-8").read()
            except FileNotFoundError:
                continue  # 削除されたファイルは対象外
        base_text = base_show.stdout
        if not learning_filled(base_text):
            continue  # 検証開始前はテストカードを直してよい
        if testcard(base_text) != testcard(head_text):
            failures.append(f)
    for f in failures:
        print(f"[error] testcard-immutable | {f} | "
              "学習カード記入済みACTのテストカードが変更されている（不変ルール6・後知恵バイアス防止）")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 4: テストが通ることを確認する**

Run: `python3 -m unittest discover -s tests -v`
Expected: PASS（22 tests OK）

- [ ] **Step 5: `.githooks/pre-commit` を作成して有効化する**

`.githooks/pre-commit` を新規作成:

```sh
#!/bin/sh
# 仮説検証Wiki の不変ルールをコミット時に強制する。
# 有効化: git config core.hooksPath .githooks（Claude Code は SessionStart フックが自動設定）
set -e

# 1) tools/tests を変更したときだけユニットテスト
if git diff --cached --name-only | grep -qE '^(tools|tests)/'; then
  python3 -m unittest discover -s tests || exit 1
fi

# 2) 決定論 lint（全プロジェクト）
python3 tools/hwlint.py --all || exit 1

# 3) テストカード不変（学習カード記入済み ACT の成功基準書き換え検出）
python3 tools/check_testcard_immutable.py --staged || exit 1

# 4) log.md は追記のみ（既存行の変更・削除を禁止）
if git diff --cached -U0 -- 'projects/*/wiki/log.md' | grep -E '^-[^-]' >/dev/null; then
  echo "[error] log-append-only | projects/*/wiki/log.md の既存行が変更/削除されている（不変ルール3）" >&2
  exit 1
fi

# 5) sources/ は不変層（既存ファイルの変更・削除を禁止。新規追加のみ許可）
if git diff --cached --name-only --diff-filter=MD -- 'projects/*/sources/*' | grep -q .; then
  echo "[error] sources-immutable | projects/*/sources/ の既存ファイルが変更/削除されている（不変層）" >&2
  exit 1
fi
```

作成後に実行:

```bash
chmod +x .githooks/pre-commit
git config core.hooksPath .githooks
```

- [ ] **Step 6: 違反コミットが実際に弾かれることを確認する**

```bash
sed -i '' 's/成功基準/成功基準(改)/' projects/self/wiki/activities/SELF-ACT-001.md
git add projects/self/wiki/activities/SELF-ACT-001.md
git commit -m "test: 違反コミット" ; echo "exit=$?"
git restore --staged projects/self/wiki/activities/SELF-ACT-001.md
git restore projects/self/wiki/activities/SELF-ACT-001.md
```

Expected: `testcard-immutable` の error が出てコミットが失敗する（exit≠0）。restore 後、次の Step 7 の正常なコミットが通ることも確認になる。

- [ ] **Step 7: コミット**

```bash
git add tools/check_testcard_immutable.py tests/test_hwlint.py .githooks/pre-commit
git commit -m "feat(hooks): テストカード不変チェックとpre-commitフックを追加"
```

### Task 8: Claude Code フック — sources/ ガードとターン終了時 lint

**Files:**
- Create: `tools/hooks/guard_sources.py`
- Create: `tools/hooks/stop_lint.py`
- Create: `.claude/settings.json`
- Modify: `tests/test_hwlint.py`

**Interfaces:**
- Consumes: `tools/hwlint.py` CLI ／ Claude Code hooks 仕様（stdin に JSON `{tool_name, tool_input, ...}`、exit 2 = PreToolUse はツール実行をブロック・Stop はターン終了をブロックし、stderr が Claude にフィードバックされる）
- Produces: `guard_sources.py`（sources/ の既存ファイルへの Edit/Write を exit 2 でブロック。新規 Write は許可）／ `stop_lint.py`（cwd をリポジトリとみなし現在プロジェクトへ hwlint。error があれば exit 2。`stop_hook_active` なら素通し）／ `.claude/settings.json`（SessionStart・PreToolUse・Stop の3フック）

> 注記: Stop フックは Task 6 のベースライン（hwlint error 0）が前提。error が残ったまま入れると毎ターン終了がブロックされるので、Task 6 完了後に着手する。

- [ ] **Step 1: 失敗するテストを書く**

`tests/test_hwlint.py` の冒頭 import 群に `import json` を追加し、末尾に追加:

```python
class GuardSourcesTest(unittest.TestCase):
    def _run(self, payload):
        return subprocess.run(
            [sys.executable, str(TOOLS / "hooks" / "guard_sources.py")],
            input=json.dumps(payload), capture_output=True, text=True)

    def test_edit_existing_source_blocked(self):
        with tempfile.TemporaryDirectory() as tmp:
            src = Path(tmp) / "projects" / "demo" / "sources" / "2026-07-01-interview.md"
            src.parent.mkdir(parents=True)
            src.write_text("生データ", encoding="utf-8")
            r = self._run({"tool_name": "Edit", "tool_input": {"file_path": str(src)}})
            self.assertEqual(r.returncode, 2)
            self.assertIn("不変層", r.stderr)

    def test_new_source_write_allowed(self):
        with tempfile.TemporaryDirectory() as tmp:
            d = Path(tmp) / "projects" / "demo" / "sources"
            d.mkdir(parents=True)
            r = self._run({"tool_name": "Write", "tool_input": {"file_path": str(d / "new.md")}})
            self.assertEqual(r.returncode, 0, r.stderr)

    def test_wiki_write_allowed(self):
        r = self._run({"tool_name": "Edit",
                       "tool_input": {"file_path": "/x/projects/demo/wiki/hypotheses/DEMO-H-001.md"}})
        self.assertEqual(r.returncode, 0, r.stderr)


class StopLintTest(unittest.TestCase):
    def _repo(self, tmp, record):
        write(Path(tmp), "projects/current.md", "current-project: demo\n")
        make_project(tmp, {"wiki/hypotheses/DEMO-H-001.md": record})
        return Path(tmp)

    def _run(self, repo, payload):
        return subprocess.run(
            [sys.executable, str(TOOLS / "hooks" / "stop_lint.py")],
            input=json.dumps(payload), cwd=repo, capture_output=True, text=True)

    def test_clean_project_allows_stop(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = self._repo(tmp, hyp())
            r = self._run(repo, {})
            self.assertEqual(r.returncode, 0, r.stderr)

    def test_error_blocks_stop(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = self._repo(tmp, hyp(id="H-001"))  # id-filename の error を仕込む
            r = self._run(repo, {})
            self.assertEqual(r.returncode, 2)
            self.assertIn("hwlint", r.stderr)

    def test_stop_hook_active_passes_through(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = self._repo(tmp, hyp(id="H-001"))
            r = self._run(repo, {"stop_hook_active": True})
            self.assertEqual(r.returncode, 0, r.stderr)
```

- [ ] **Step 2: テストが失敗することを確認する**

Run: `python3 -m unittest discover -s tests -v`
Expected: FAIL（スクリプト不在。blocked 系は stderr の文言 assert で落ち、allowed 系は returncode≠0 で落ちる）

- [ ] **Step 3: フック実体と settings.json を実装する**

`tools/hooks/guard_sources.py`:

```python
#!/usr/bin/env python3
"""PreToolUse フック: sources/（不変層）の既存ファイルへの Edit/Write をブロックする。

新規ファイルの Write（/ingest 手順1の初回配置）は許可する。exit 2 でブロックし、
stderr のメッセージが Claude にフィードバックされる。
"""
import json
import re
import sys
from pathlib import Path


def main() -> int:
    data = json.load(sys.stdin)
    tool = data.get("tool_name", "")
    file_path = (data.get("tool_input") or {}).get("file_path", "")
    if not file_path:
        return 0
    p = Path(file_path)
    if not re.search(r"projects/[^/]+/sources/", p.as_posix()):
        return 0
    if tool == "Write" and not p.exists():
        return 0  # 新規配置は許可（/ingest 手順1）
    print(f"{p.name} は sources/（不変層・読み取り専用）の既存ファイル。編集・上書きは禁止。"
          "訂正が必要なら人間に依頼し、解釈の修正は wiki/ 側のレコードで行うこと。", file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main())
```

`tools/hooks/stop_lint.py`:

```python
#!/usr/bin/env python3
"""Stop フック: ターン終了時に現在プロジェクトへ hwlint を実行し、
error が残っていれば終了をブロックして修正させる（stderr が Claude に渡る）。
"""
import json
import subprocess
import sys
from pathlib import Path


def main() -> int:
    data = json.load(sys.stdin)
    if data.get("stop_hook_active"):
        return 0  # このフック起因の続行中は素通し（無限ループ防止）
    repo = Path.cwd()
    if not (repo / "projects" / "current.md").exists():
        return 0  # 仮説検証Wiki のリポジトリでなければ何もしない
    hwlint = Path(__file__).resolve().parent.parent / "hwlint.py"
    result = subprocess.run(
        [sys.executable, str(hwlint), "--repo", str(repo)],
        capture_output=True, text=True)
    if result.returncode != 0:
        print("hwlint が error を検出。ターンを終える前に修正すること:\n" + result.stdout,
              file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

`.claude/settings.json`（新規。プロジェクト共有設定としてコミットする — キット利用者全員に効く）:

```json
{
  "hooks": {
    "SessionStart": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "git config core.hooksPath .githooks"
          }
        ]
      }
    ],
    "PreToolUse": [
      {
        "matcher": "Edit|Write",
        "hooks": [
          {
            "type": "command",
            "command": "python3 tools/hooks/guard_sources.py",
            "timeout": 10
          }
        ]
      }
    ],
    "Stop": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "python3 tools/hooks/stop_lint.py",
            "timeout": 30
          }
        ]
      }
    ]
  }
}
```

- [ ] **Step 4: テストが通ることを確認する**

Run: `python3 -m unittest discover -s tests -v`
Expected: PASS（28 tests OK）

- [ ] **Step 5: フックをパイプテストで確認する**

Run:

```bash
echo '{"tool_name":"Edit","tool_input":{"file_path":"'$PWD'/projects/self/sources/2026-07-16-desk-research-corporate-hypothesis-testing.md"}}' | python3 tools/hooks/guard_sources.py; echo "exit=$?"
echo '{}' | python3 tools/hooks/stop_lint.py; echo "exit=$?"
```

Expected: 前者は exit=2 でブロック文言、後者は self が健全なら exit=0。
なお settings.json のフックが実際に発火するのは**次回セッション起動時**（または `/hooks` を開いて再読込したとき）から。ユーザーにその旨を伝える。

- [ ] **Step 6: コミット**

```bash
git add tools/hooks/guard_sources.py tools/hooks/stop_lint.py .claude/settings.json tests/test_hwlint.py
git commit -m "feat(hooks): Claude Codeフック（sourcesガード・Stop時lint・hooksPath自動設定）"
```

---

## フェーズ2 — 確信度の規律（証拠の階梯）

### Task 9: スキーマに「証拠の階梯」を型として入れる（承認ゲート付き）

**Files:**
- Modify: `CLAUDE.md`（「確信度とステータス（2軸・別管理）」節）
- Modify: `templates/hypothesis.md`（履歴コメント）
- Modify: `templates/activity.md`・`templates/decision.md`（frontmatter 配列例）
- Modify: `.claude/skills/ingest/SKILL.md`（手順5）

**Interfaces:**
- Consumes: なし（Markdown のみ）
- Produces: 証拠種別タグの正典語彙 `〈発言〉〈自認〉〈実コスト〉〈行動〉〈支払い〉〈二次〉〈架空〉`（Task 10 の lint がこの7語を参照する）

- [ ] **Step 1: CLAUDE.md の変更案を作る**

「**ステータス** — 検証の進捗」の段落の**直後**、「### 不変ルール」の前に挿入:

```markdown
**証拠の階梯** — 確信度を上げる根拠には強さの序列がある（弱→強）:

〈発言〉好意的な意見・「いいね」 ＜ 〈自認〉自分の言葉で課題を語る ＜ 〈実コスト〉時間・金・手戻りを払っている証拠 ＜ 〈行動〉実際にとった行動・現在の使用 ＜ 〈支払い〉対価・前払い・導入コミット

- 確信度 5-6 に上げるには〈自認〉以上、7-8 には〈実コスト〉か〈行動〉以上の証拠を要する。〈発言〉だけで上げない（interest ≠ intent）。
- **架空/シミュレーションデータ由来の確信度は上限8**。9-10 は実観測に限る。
- 確信度履歴テーブルの「根拠」列は、先頭に証拠種別タグ（〈発言〉〈自認〉〈実コスト〉〈行動〉〈支払い〉〈二次〉〈架空〉のいずれか、複数可）を付けて書く（例 `〈自認〉〈実コスト〉5名中3名が…`）。
- 「検証中なのに確信度 3-4」は異常ではない。**検証したが証拠が集まっていない**正当な状態（判断保留）であり、次の検証を計画する対象になる。
```

- [ ] **Step 2: テンプレ・ingest の変更案を作る**

`templates/hypothesis.md` の履歴コメント `<!-- 不変ルール: ... -->` に1行追加:

```markdown
- 「根拠」列は先頭に証拠種別タグ（〈発言〉〈自認〉〈実コスト〉〈行動〉〈支払い〉〈二次〉〈架空〉）を付ける。
```

`templates/activity.md` の frontmatter を `hypotheses: [<PREFIX>-H-NNN]   # 接頭辞つきで書く（例 [SELF-H-001]）` に、
`templates/decision.md` の frontmatter を `based-on: [<PREFIX>-ACT-NNN]   # 接頭辞つきで書く（例 [SELF-ACT-001]）` に、本文の `[[ACT-NNN]]`・`[[H-NNN]]` プレースホルダはそのまま。

`.claude/skills/ingest/SKILL.md` 手順5の第1文を次に差し替え:

```markdown
5. **承認後に反映する** — 承認された仮説レコード（`wiki/hypotheses/H-NNN.md`）の frontmatter `confidence`/`status` を更新し、確信度履歴テーブルに1行追記（活動列に `[[ACT-NNN]]`、根拠列の先頭に証拠種別タグ〈発言〉〈自認〉〈実コスト〉〈行動〉〈支払い〉〈二次〉〈架空〉）。ACT の学習カードの確信度更新テーブルも埋める。
```

- [ ] **Step 3: ユーザー承認を得る（schema層の変更ゲート）**

Step 1–2 の diff をまとめて提示し、承認を得る。修正指示があれば反映してから次へ。**承認なしにコミットしない。**

- [ ] **Step 4: 適用して既存テストが壊れていないことを確認する**

Run: `python3 -m unittest discover -s tests -v && python3 tools/hwlint.py --all`
Expected: すべて PASS／hwlint の結果が Task 7 時点から悪化していない（テンプレ変更はレコードに影響しない）。

- [ ] **Step 5: コミット**

```bash
git add CLAUDE.md templates/hypothesis.md templates/activity.md templates/decision.md .claude/skills/ingest/SKILL.md
git commit -m "docs(schema): 証拠の階梯・架空上限8・判断保留の正当化をスキーマに明文化"
```

### Task 10: 証拠種別タグの lint（warning 運用）

**Files:**
- Modify: `tools/hwlint.py`
- Modify: `tests/test_hwlint.py`

**Interfaces:**
- Consumes: Task 9 のタグ語彙 ／ Task 2 の `parse_history`
- Produces: `EVIDENCE_TAGS` ／ `check_evidence_tags`（warning のみ・遡及適用しない方針のため error にしない）

- [ ] **Step 1: 失敗するテストを書く**

`tests/test_hwlint.py` に追加:

```python
class EvidenceTagTest(unittest.TestCase):
    def test_untagged_reason_warned(self):
        rows = ["| 2026-07-01 | 1 | 未検証 | 初期作成 | — |",
                "| 2026-07-05 | 5 | 検証中 | 手応えがあった | [[DEMO-ACT-001]] |"]
        with tempfile.TemporaryDirectory() as tmp:
            root = make_project(tmp, {
                "wiki/hypotheses/DEMO-H-001.md": hyp(status="検証中", confidence="5", rows=rows),
                "wiki/activities/DEMO-ACT-001.md": act(),
            })
            hits = [p for p in hwlint.lint_project(root) if p.check == "evidence-tag"]
            self.assertEqual(len(hits), 1)
            self.assertEqual(hits[0].level, "warning")

    def test_tagged_reason_ok(self):
        rows = ["| 2026-07-01 | 1 | 未検証 | 初期作成 | — |",
                "| 2026-07-05 | 5 | 検証中 | 〈自認〉〈実コスト〉3名が該当 | [[DEMO-ACT-001]] |"]
        with tempfile.TemporaryDirectory() as tmp:
            root = make_project(tmp, {
                "wiki/hypotheses/DEMO-H-001.md": hyp(status="検証中", confidence="5", rows=rows),
                "wiki/activities/DEMO-ACT-001.md": act(),
            })
            self.assertEqual([p for p in hwlint.lint_project(root) if p.check == "evidence-tag"], [])
```

- [ ] **Step 2: テストが失敗することを確認する**

Run: `python3 -m unittest discover -s tests -v`
Expected: FAIL（evidence-tag が検出されない）

- [ ] **Step 3: `tools/hwlint.py` に実装を追加する**

`CHECKS` の手前に追加し、`CHECKS` 末尾に `check_evidence_tags` を追加:

```python
EVIDENCE_TAGS = ("〈発言〉", "〈自認〉", "〈実コスト〉", "〈行動〉", "〈支払い〉", "〈二次〉", "〈架空〉")


def check_evidence_tags(project) -> list:
    """証拠の階梯: 履歴2行目以降の根拠セルには証拠種別タグを付ける（新規約のため warning 運用）。"""
    problems = []
    for stem, (path, fm, body) in project.records.items():
        if "-H-" not in stem:
            continue
        for row in parse_history(body)[1:]:
            if not any(tag in row["reason"] for tag in EVIDENCE_TAGS):
                problems.append(Problem("warning", stem, "evidence-tag",
                    f"履歴 {row['date']} 行の根拠に証拠種別タグ（〈自認〉〈実コスト〉等）が無い"))
    return problems
```

- [ ] **Step 4: テストが通ることを確認する**

Run: `python3 -m unittest discover -s tests -v`
Expected: PASS（30 tests OK）。`python3 tools/hwlint.py --all` で self の既存レコードに warning が出るのは想定どおり（遡及修正しない。warning は Stop フック・pre-commit を落とさない）。

- [ ] **Step 5: コミット**

```bash
git add tools/hwlint.py tests/test_hwlint.py
git commit -m "feat(lint): 証拠種別タグのwarningチェックを追加"
```

---

## フェーズ3 — 到達範囲とポジショニング

### Task 11: AGENTS.md 併存（agent-agnostic の第一歩）

**Files:**
- Create: `AGENTS.md`
- Modify: `CLAUDE.md`（3層アーキテクチャ表の Schema 行に AGENTS.md を追記）

**Interfaces:**
- Consumes: `CLAUDE.md`（正典として参照）／ `tools/hwlint.py`
- Produces: 非 Claude エージェントの入口ファイル

- [ ] **Step 1: `AGENTS.md` を作成する**

````markdown
# AGENTS.md — 仮説検証Wiki（エージェント共通の入口）

このリポジトリの規約の正典は [CLAUDE.md](CLAUDE.md)。**どのエージェントも、まず CLAUDE.md を読み、
「規律あるWikiの保守者」として振る舞うこと。** 本ファイルには Claude Code 以外のエージェント向けの差分だけを書く
（内容を二重管理しない）。

## Claude Code 以外での使い方

- `.claude/skills/` のスキル（`/formulate` `/plan` `/ingest` …）は Claude Code 用の入口にすぎない。
  各スキルの実体はただの Markdown 手順書なので、**スキル機構がないエージェントは
  `.claude/skills/<name>/SKILL.md` を読み、その手順に従って作業する**（対応表は CLAUDE.md「ワークフロー」）。
- 変更後は必ず決定論 lint を実行し、error を残さない:

  ```bash
  python3 tools/hwlint.py
  ```

- 初回クローン後に `git config core.hooksPath .githooks` を一度実行し、コミット時フック（不変ルールの強制）を
  有効にする（Claude Code では SessionStart フックが自動で設定する。他エージェントは手動で）。
- 不変ルール（CLAUDE.md「不変ルール」）は全エージェント共通。特に:
  `sources/` は読み取り専用／確信度・ステータスの変更は必ず ACT/DEC に紐づける／`log.md` は追記のみ／
  テストカードの成功基準は検証開始後に書き換えない。

## 記述言語

すべて日本語。技術用語・ID・frontmatter キーは原文のまま。
````

- [ ] **Step 2: CLAUDE.md の3層表を1か所更新する**

「The Schema（設定層）」行の場所セルを
`CLAUDE.md（正典）・AGENTS.md（他エージェント向け入口）・playbooks/・templates/・.claude/skills/` に差し替える。
（schema層の変更だが正典の内容自体は変えない追記のため、コミット前にユーザーへ diff を見せ一言確認を取る。）

- [ ] **Step 3: hwlint とテストに影響がないことを確認する**

Run: `python3 -m unittest discover -s tests -v && python3 tools/hwlint.py --all`
Expected: PASS／結果に変化なし。

- [ ] **Step 4: コミット**

```bash
git add AGENTS.md CLAUDE.md
git commit -m "docs: AGENTS.mdを追加しagent-agnosticの入口を用意"
```

### Task 12: README ポジショニング刷新（旗印の一本化・誠実な但し書き）

**Files:**
- Modify: `README.md`

**Interfaces:**
- Consumes: `docs/competitive-analysis.md`（3-A/3-D・§4 の但し書き）／ Task 1–7 の成果（機械強制の実在）
- Produces: 差別化軸を前面に出した README

- [ ] **Step 1: 冒頭の説明文を差し替える**

現在の冒頭2〜5行目:

```markdown
仮説検証活動（**CPF → FPF → PSF → SPF → PMF** の5ステージ）を、**確信度**という一本の物差しで育てる LLM-wiki キット。
Claude Code の AgentSkills を使い、曖昧なアイデアを反証可能な仮説にし、インタビューやプロトタイプで検証し、
その学びと意思決定を「後から歴史を追える記録」として積み上げる。
```

を次に差し替える:

```markdown
仮説検証活動（**CPF → FPF → PSF → SPF → PMF** の5ステージ）を、**単一の確信度（1〜10）という一本の物差し**と、
**証拠なしには確信度を動かせない強制紐づけ**で育てる LLM-wiki キット。
曖昧なアイデアを反証可能な仮説にし、インタビューやプロトタイプで検証し、学びと意思決定を
「後から歴史を追える記録」として積み上げる。不変ルールは規約（CLAUDE.md）に書くだけでなく、
決定論 lint（`tools/hwlint.py`）とフック（git pre-commit＋Claude Code フック）が機械的に守らせる。
```

- [ ] **Step 2: 「なぜこのキットか」節を追加する**

「## これは何か（目的）」節の**末尾**（「Karpathy の…」段落の後）に追加:

```markdown
### なぜこのキットか（競合の中での立ち位置）

2ラウンドの競合調査（[docs/competitive-analysis.md](docs/competitive-analysis.md)）では、
①プレーンテキスト/Git/Obsidian の LLM-wiki、②CPF→PMF のステージゲート、③証拠に強制紐づけされる
単一の1〜10確信度——の三点を同時に満たす既存プロダクトは確認できなかった。

- **単一の確信度が全記録の背骨** — Strategyzer は定性ティア（Valid/Invalid/Unknown）、GLIDR は確信度を露出しない。
  「重要 × 確信度低」の仮説を機械的に選べるのは、一本の数直線があるからだ。
- **証拠なしに確信度・ステータスを変えられない** — 競合ではテンプレ上の慣行に留まる紐づけを、
  ここでは決定論 lint と git/Claude Code フック（テストカード事後書き換え検出・sources/ 書き込みガードを含む）が
  機械的に強制する。
- 3層アーキテクチャやテストカード自体は既存パターン（Karpathy / Strategyzer）の適用であり、発明ではない。
  立ち位置は「組み合わせ」にある。

> 注: 上記は競合の一次ページ/README にもとづく相対比較であり、効果の第三者検証はまだ無い。
> 詳細な但し書きは競合分析メモ §4 を参照。
```

- [ ] **Step 3: リンクと表記を全文点検する**

Run: `grep -n "hwlint\|competitive-analysis" README.md`
Expected: 追加した2箇所が正しい相対パスで出る。あわせて「ディレクトリ構成」の木に `tools/`・`AGENTS.md`・`.github/` を追記する:

```
├── AGENTS.md               # 非Claudeエージェント向けの入口（正典はCLAUDE.md）
├── tools/                  # 決定論lint（hwlint.py）・テストカード不変チェック・フック実体
├── tests/                  # 上記ツールのunittest
├── .githooks/              # git pre-commitフック（有効化: git config core.hooksPath .githooks）
```

- [ ] **Step 4: コミット**

```bash
git add README.md
git commit -m "docs: READMEを「確信度×強制紐づけ」の旗印に刷新し競合上の立ち位置を明記"
```

---

## 完了条件（計画全体）

1. `python3 -m unittest discover -s tests -v` が全 PASS。
2. `python3 tools/hwlint.py --all` が self で error 0（確信度系のユーザー判断待ちを除く。残る場合は報告済み）。
3. 不変ルール違反（証拠なき確信度変更・テストカード書き換え・log 既存行の改変・sources 改変）を含むコミットは pre-commit フックで fail する。Claude Code セッションでは sources/ の既存ファイルへの書き込みがブロックされ、hwlint error が残ったままターンを終了できない。
4. CLAUDE.md に証拠の階梯・架空上限8・判断保留の正当化が明文化され（ユーザー承認済み）、AGENTS.md と刷新 README が存在する。
