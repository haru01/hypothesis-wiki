import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

TOOLS = Path(__file__).resolve().parent.parent / "tools"
sys.path.insert(0, str(TOOLS))
import hwlint  # noqa: E402
import ontology  # noqa: E402
import records  # noqa: E402


def with_fm(record: str, line: str) -> str:
    """テスト用ヘルパ: hyp()/act() の frontmatter に1行足す（importance 行の直後に挿入）。"""
    return record.replace("importance: auto\n", f"importance: auto\n{line}\n")


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


def learn(id="DEMO-LEARN-001", learns_from="DEMO-ACT-001", hypotheses="[DEMO-H-001]",
          outcome="支持", body=None):
    lf = f"learns-from: {learns_from}\n" if learns_from else ""
    lf_link = f"実験計画: [[{learns_from}]]\n" if learns_from else ""
    body = body if body is not None else f"対象仮説: [[DEMO-H-001]]\n{lf_link}"
    return f"""---
id: {id}
title: テスト学び
type: interview
date: 2026-07-02
stage: CPF
{lf}hypotheses: {hypotheses}
outcome: {outcome}
---

# テスト学び

{body}
## 学習カード（検証後に記入）

### 事実（observed）

観測した事実。
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

    def test_unprefixed_derived_from_detected(self):
        # hyp() テンプレには derived-from が無いので frontmatter に明示的に足す
        rec = hyp(id="DEMO-H-002").replace("importance: auto\n", "importance: auto\nderived-from: H-001\n")
        with tempfile.TemporaryDirectory() as tmp:
            root = make_project(tmp, {
                "wiki/hypotheses/DEMO-H-001.md": hyp(),
                "wiki/hypotheses/DEMO-H-002.md": rec,
            })
            self.assertTrue(any(p.check == "refs" and "derived-from" in p.message
                                for p in hwlint.lint_project(root)))

    def test_missing_derived_from_record_detected(self):
        rec = hyp(id="DEMO-H-002").replace("importance: auto\n", "importance: auto\nderived-from: DEMO-H-404\n")
        with tempfile.TemporaryDirectory() as tmp:
            root = make_project(tmp, {"wiki/hypotheses/DEMO-H-002.md": rec})
            self.assertTrue(any(p.check == "refs" and "DEMO-H-404" in p.message
                                for p in hwlint.lint_project(root)))

    def test_prefixed_derived_from_ok(self):
        rec = hyp(id="DEMO-H-002").replace("importance: auto\n", "importance: auto\nderived-from: DEMO-H-001\n")
        with tempfile.TemporaryDirectory() as tmp:
            root = make_project(tmp, {
                "wiki/hypotheses/DEMO-H-001.md": hyp(),
                "wiki/hypotheses/DEMO-H-002.md": rec,
            })
            self.assertEqual([p for p in hwlint.lint_project(root) if p.check == "refs"], [])

    def test_empty_derived_from_ok(self):
        # テンプレの空 derived-from は許可
        rec = hyp(id="DEMO-H-002").replace("importance: auto\n", "importance: auto\nderived-from:\n")
        with tempfile.TemporaryDirectory() as tmp:
            root = make_project(tmp, {"wiki/hypotheses/DEMO-H-002.md": rec})
            self.assertEqual([p for p in hwlint.lint_project(root) if p.check == "refs"], [])

    def test_wikilink_in_html_comment_ignored(self):
        # テンプレの履歴コメントに例示 [[ACT-NNN]] が入っていてもリンク切れにしない
        body = hyp() + "\n<!--\n- 活動列に [[ACT-NNN]] を書く。派生元 [[H-NNN]] も例示。\n-->\n"
        with tempfile.TemporaryDirectory() as tmp:
            root = make_project(tmp, {"wiki/hypotheses/DEMO-H-001.md": body})
            self.assertEqual([p for p in hwlint.lint_project(root) if p.check == "wikilink"], [])


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


BASE_ACT_FOR_GIT = """---
id: DEMO-ACT-001
title: テスト活動
type: interview
date: 2026-07-01
stage: CPF
hypotheses: [DEMO-H-001]
riskiest-assumption: 実践者は実コストを払っている
---

# テスト活動

対象仮説: [[DEMO-H-001]]

## テストカード（検証前に記入・後から書き換えない）

- **成功基準**: 5名中3名以上が実コストを払っている。
"""

# この ACT を learns-from で指す学び（LEARN）。これが在ると ACT テストカードは不変になる。
LEARN_FOR_GIT = """---
id: DEMO-LEARN-001
title: テスト活動の学び
type: interview
date: 2026-07-02
stage: CPF
learns-from: DEMO-ACT-001
hypotheses: [DEMO-H-001]
outcome: 反証
---

# テスト活動の学び

対象仮説: [[DEMO-H-001]]
実験計画: [[DEMO-ACT-001]]

## 学習カード（検証後に記入）

### 事実（observed）

5名に実施し、2名が実コストを払っていた。
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
        # ACT を learns-from で指す LEARN が在れば、ACT テストカードの変更は検出される。
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            run = self._init_repo(repo)
            write(repo, "projects/demo/wiki/activities/DEMO-ACT-001.md", BASE_ACT_FOR_GIT)
            write(repo, "projects/demo/wiki/learnings/DEMO-LEARN-001.md", LEARN_FOR_GIT)
            run("git", "add", "-A"); run("git", "commit", "-m", "base")
            write(repo, "projects/demo/wiki/activities/DEMO-ACT-001.md",
                  BASE_ACT_FOR_GIT.replace("3名以上", "1名以上"))
            run("git", "add", "-A"); run("git", "commit", "-m", "rewrite")
            result = self._run_checker(repo, "--base", "HEAD~1")
            self.assertEqual(result.returncode, 1, result.stdout + result.stderr)

    def test_testcard_edit_before_learning_allowed(self):
        # LEARN がまだ紐づかない（検証開始前）ACT はテストカードを直してよい。
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            run = self._init_repo(repo)
            write(repo, "projects/demo/wiki/activities/DEMO-ACT-001.md", BASE_ACT_FOR_GIT)
            run("git", "add", "-A"); run("git", "commit", "-m", "base")
            write(repo, "projects/demo/wiki/activities/DEMO-ACT-001.md",
                  BASE_ACT_FOR_GIT.replace("3名以上", "1名以上"))
            run("git", "add", "-A"); run("git", "commit", "-m", "edit before learning")
            result = self._run_checker(repo, "--base", "HEAD~1")
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_staged_rewrite_detected(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            run = self._init_repo(repo)
            write(repo, "projects/demo/wiki/activities/DEMO-ACT-001.md", BASE_ACT_FOR_GIT)
            write(repo, "projects/demo/wiki/learnings/DEMO-LEARN-001.md", LEARN_FOR_GIT)
            run("git", "add", "-A"); run("git", "commit", "-m", "base")
            write(repo, "projects/demo/wiki/activities/DEMO-ACT-001.md",
                  BASE_ACT_FOR_GIT.replace("3名以上", "1名以上"))
            run("git", "add", "-A")  # コミットせずステージのみ（pre-commit 相当）
            result = self._run_checker(repo, "--staged")
            self.assertEqual(result.returncode, 1, result.stdout + result.stderr)


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


class OntologyLoaderTest(unittest.TestCase):
    def test_selfcheck_passes(self):
        self.assertEqual(ontology._selfcheck(), 0)

    def test_constants_derived_from_yaml(self):
        self.assertEqual(ontology.STATUS_ORDER, ["検証済み", "検証中", "未検証", "反証"])
        self.assertIn("課題仮説", ontology.PROBLEM_TYPES)
        self.assertEqual(ontology.SOLUTION_TYPES, ontology.VALUE_TYPES | ontology.WILLING_TYPES)
        self.assertEqual({r.field for r in ontology.RELATIONS},
                         {"derived-from", "leads-to", "addresses", "hypotheses", "learns-from", "based-on"})
        # hypotheses は ACT/LEARN 両方を domain に、based-on は ACT/LEARN 両方を range に取る（多種別）
        self.assertEqual(ontology.RELATIONS_BY_FIELD["hypotheses"].domains, {"ACT", "LEARN"})
        self.assertEqual(ontology.RELATIONS_BY_FIELD["based-on"].ranges, {"ACT", "LEARN"})
        self.assertEqual(ontology.RELATIONS_BY_FIELD["learns-from"].domains, {"LEARN"})
        self.assertTrue(ontology.ID_RE.match("SELF-LEARN-001"))
        self.assertTrue(ontology.ID_RE.match("SELF-H-001"))
        self.assertFalse(ontology.ID_RE.match("SELF-X-001"))

    def test_hwlint_uses_ontology_values(self):
        # 二重管理をやめ ontology を単一の真実源にしている
        self.assertEqual(hwlint.H_TYPES, ontology.H_TYPES)
        self.assertEqual(hwlint.STATUSES, ontology.STATUSES)
        self.assertIs(hwlint.RELATIONS, ontology.RELATIONS)


class RelationOntologyTest(unittest.TestCase):
    """ontology 駆動の関係検証（domain/range/cardinality/サブタイプ）。"""

    def test_range_violation_based_on_points_to_hypothesis(self):
        dec = ("---\nid: DEMO-DEC-001\ntitle: t\ndate: 2026-07-01\ntype: pivot\n"
               "based-on: [DEMO-H-001]\n---\n\n# t\n\n根拠: [[DEMO-H-001]]\n")
        with tempfile.TemporaryDirectory() as tmp:
            root = make_project(tmp, {
                "wiki/hypotheses/DEMO-H-001.md": hyp(),
                "wiki/decisions/DEMO-DEC-001.md": dec,
            })
            self.assertTrue(any(p.check == "refs" and "ACT/LEARN を指すべき" in p.message
                                for p in hwlint.lint_project(root)))


def dec(id="DEMO-DEC-001", date="2026-07-01", type="stage-transition", to_stage="FPF"):
    ts = f"to-stage: {to_stage}\n" if to_stage else ""
    return (f"---\nid: {id}\ntitle: t\ndate: {date}\ntype: {type}\n"
            f"based-on: [DEMO-LEARN-001]\n{ts}---\n\n# t\n\n根拠: [[DEMO-LEARN-001]]\n")


class StageDerivationTest(unittest.TestCase):
    """現在ステージは to-stage を持つ最新DEC から導出（type では絞らない＝rollback も反映）。"""

    def test_fallback_to_stage_md_when_no_dec(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = make_project(tmp, {"wiki/stage.md": "current-stage: PSF\n"})
            self.assertEqual(records.Project(root).stage, "PSF")

    def test_invalid_to_stage_flagged(self):
        # DEC の to-stage が規約外なら vocab error（誤記でステージ導出が壊れるのを防ぐ）
        with tempfile.TemporaryDirectory() as tmp:
            root = make_project(tmp, {
                "wiki/decisions/DEMO-DEC-001.md": dec("DEMO-DEC-001", "2026-07-01", "stage-transition", "FFP"),
            })
            self.assertTrue(any(p.check == "vocab" and "to-stage" in p.message
                                for p in hwlint.lint_project(root)))

    def test_latest_to_stage_wins_including_rollback(self):
        # 移行(→FPF) の後に巻き戻し(→CPF)。type によらず最新の to-stage=CPF が現ステージ。
        with tempfile.TemporaryDirectory() as tmp:
            root = make_project(tmp, {
                "wiki/stage.md": "current-stage: FPF\n",
                "wiki/decisions/DEMO-DEC-001.md": dec("DEMO-DEC-001", "2026-07-01", "stage-transition", "FPF"),
                "wiki/decisions/DEMO-DEC-002.md": dec("DEMO-DEC-002", "2026-07-05", "rollback", "CPF"),
            })
            self.assertEqual(records.Project(root).stage, "CPF")


class LearnRecordTest(unittest.TestCase):
    """LEARN（学び）レコードと learns-from / hypotheses(ACT・LEARN) の関係検証。"""

    def test_valid_learn_passes(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = make_project(tmp, {
                "wiki/hypotheses/DEMO-H-001.md": hyp(),
                "wiki/activities/DEMO-ACT-001.md": act(),
                "wiki/learnings/DEMO-LEARN-001.md": learn(),
            })
            errs = [p for p in hwlint.lint_project(root) if p.level == "error"]
            self.assertEqual(errs, [], errs)

    def test_learns_from_must_point_to_act(self):
        # learns-from が ACT でなく H を指すと range 違反
        with tempfile.TemporaryDirectory() as tmp:
            root = make_project(tmp, {
                "wiki/hypotheses/DEMO-H-001.md": hyp(),
                "wiki/learnings/DEMO-LEARN-001.md": learn(
                    learns_from="DEMO-H-001",
                    body="対象仮説: [[DEMO-H-001]]\n実験計画: [[DEMO-H-001]]\n"),
            })
            self.assertTrue(any(p.check == "refs" and "ACT を指すべき" in p.message
                                for p in hwlint.lint_project(root)))

    def test_retrospective_learn_without_learns_from_passes(self):
        # 回顧型（desk-research 等）は learns-from を持たなくてよい
        with tempfile.TemporaryDirectory() as tmp:
            root = make_project(tmp, {
                "wiki/hypotheses/DEMO-H-001.md": hyp(),
                "wiki/learnings/DEMO-LEARN-001.md": learn(
                    learns_from="", body="対象仮説: [[DEMO-H-001]]\n"),
            })
            errs = [p for p in hwlint.lint_project(root) if p.level == "error"]
            self.assertEqual(errs, [], errs)

    def test_cardinality_violation_derived_from_multiple(self):
        rec = with_fm(hyp(id="DEMO-H-003"), "derived-from: [DEMO-H-001, DEMO-H-002]")
        with tempfile.TemporaryDirectory() as tmp:
            root = make_project(tmp, {
                "wiki/hypotheses/DEMO-H-001.md": hyp(),
                "wiki/hypotheses/DEMO-H-002.md": hyp(id="DEMO-H-002"),
                "wiki/hypotheses/DEMO-H-003.md": rec,
            })
            self.assertTrue(any(p.check == "refs" and "単一参照" in p.message
                                for p in hwlint.lint_project(root)))

    def test_addresses_domain_subtype_violation(self):
        # 課題仮説 は addresses を持てない（domain サブタイプ違反）
        rec = with_fm(hyp(id="DEMO-H-002", type="課題仮説"), "addresses: [DEMO-H-001]")
        with tempfile.TemporaryDirectory() as tmp:
            root = make_project(tmp, {
                "wiki/hypotheses/DEMO-H-001.md": hyp(type="課題仮説"),
                "wiki/hypotheses/DEMO-H-002.md": rec,
            })
            self.assertTrue(any(p.check == "refs" and "だけが持てる" in p.message
                                for p in hwlint.lint_project(root)))

    def test_addresses_range_subtype_violation(self):
        # ソリューション仮説 の addresses は 課題仮説 を指すべき
        rec = with_fm(hyp(id="DEMO-H-002", type="ソリューション仮説"), "addresses: [DEMO-H-001]")
        with tempfile.TemporaryDirectory() as tmp:
            root = make_project(tmp, {
                "wiki/hypotheses/DEMO-H-001.md": hyp(type="ソリューション仮説"),
                "wiki/hypotheses/DEMO-H-002.md": rec,
            })
            self.assertTrue(any(p.check == "refs" and "課題仮説 を指すべき" in p.message
                                for p in hwlint.lint_project(root)))

    def test_addresses_valid_ok(self):
        rec = with_fm(hyp(id="DEMO-H-002", type="ソリューション仮説"),
                      "addresses: [DEMO-H-001]") + "\n対応課題: [[DEMO-H-001]]\n"
        with tempfile.TemporaryDirectory() as tmp:
            root = make_project(tmp, {
                "wiki/hypotheses/DEMO-H-001.md": hyp(type="課題仮説"),
                "wiki/hypotheses/DEMO-H-002.md": rec,
            })
            self.assertEqual([p for p in hwlint.lint_project(root) if p.check == "refs"], [])

    def test_leads_to_missing_record_now_validated(self):
        # leads-to も一般化により実在検証の対象になった
        rec = with_fm(hyp(id="DEMO-H-002"), "leads-to: [DEMO-H-404]")
        with tempfile.TemporaryDirectory() as tmp:
            root = make_project(tmp, {"wiki/hypotheses/DEMO-H-002.md": rec})
            self.assertTrue(any(p.check == "refs" and "DEMO-H-404" in p.message
                                for p in hwlint.lint_project(root)))


class RelationWikilinkTest(unittest.TestCase):
    def test_missing_body_wikilink_warned(self):
        rec = with_fm(hyp(id="DEMO-H-002"), "leads-to: [DEMO-H-001]")
        with tempfile.TemporaryDirectory() as tmp:
            root = make_project(tmp, {
                "wiki/hypotheses/DEMO-H-001.md": hyp(),
                "wiki/hypotheses/DEMO-H-002.md": rec,
            })
            hits = [p for p in hwlint.lint_project(root) if p.check == "relation-wikilink"]
            self.assertTrue(any("DEMO-H-001" in p.message and p.level == "warning" for p in hits))

    def test_present_body_wikilink_ok(self):
        rec = with_fm(hyp(id="DEMO-H-002"), "leads-to: [DEMO-H-001]") + "\n因果先: [[DEMO-H-001]]\n"
        with tempfile.TemporaryDirectory() as tmp:
            root = make_project(tmp, {
                "wiki/hypotheses/DEMO-H-001.md": hyp(),
                "wiki/hypotheses/DEMO-H-002.md": rec,
            })
            self.assertEqual([p for p in hwlint.lint_project(root)
                              if p.check == "relation-wikilink"], [])


class StatusConfidenceTest(unittest.TestCase):
    def _one(self, tmp, status, confidence):
        rows = [f"| 2026-07-01 | {confidence} | {status} | 初期作成 | — |"]
        return make_project(tmp, {"wiki/hypotheses/DEMO-H-001.md":
                                  hyp(status=status, confidence=confidence, rows=rows)})

    def _hits(self, root):
        return [p for p in hwlint.lint_project(root) if p.check == "status-confidence"]

    def test_refuted_high_confidence_warned(self):
        with tempfile.TemporaryDirectory() as tmp:
            self.assertTrue(self._hits(self._one(tmp, "反証", "8")))

    def test_unverified_high_confidence_warned(self):
        with tempfile.TemporaryDirectory() as tmp:
            self.assertTrue(self._hits(self._one(tmp, "未検証", "7")))

    def test_verified_low_confidence_warned(self):
        with tempfile.TemporaryDirectory() as tmp:
            self.assertTrue(self._hits(self._one(tmp, "検証済み", "3")))

    def test_consistent_pairs_ok(self):
        with tempfile.TemporaryDirectory() as tmp:
            self.assertEqual(self._hits(self._one(tmp, "反証", "2")), [])
        with tempfile.TemporaryDirectory() as tmp:
            self.assertEqual(self._hits(self._one(tmp, "未検証", "3")), [])
        with tempfile.TemporaryDirectory() as tmp:
            self.assertEqual(self._hits(self._one(tmp, "検証中", "5")), [])   # 検証中は境界なし


class EvidenceFloorTest(unittest.TestCase):
    def _proj(self, tmp, confidence, tag):
        rows = ["| 2026-07-01 | 1 | 未検証 | 初期作成 | — |",
                f"| 2026-07-05 | {confidence} | 検証中 | {tag}手応え | [[DEMO-ACT-001]] |"]
        return make_project(tmp, {
            "wiki/hypotheses/DEMO-H-001.md": hyp(status="検証中", confidence=str(confidence), rows=rows),
            "wiki/activities/DEMO-ACT-001.md": act(),
        })

    def _hits(self, root):
        return [p for p in hwlint.lint_project(root) if p.check == "evidence-floor"]

    def test_high_confidence_weak_evidence_warned(self):
        with tempfile.TemporaryDirectory() as tmp:   # conf 7 を〈発言〉だけで支える
            self.assertTrue(self._hits(self._proj(tmp, 7, "〈発言〉")))

    def test_high_confidence_strong_evidence_ok(self):
        with tempfile.TemporaryDirectory() as tmp:   # conf 7 を〈実コスト〉で支える
            self.assertEqual(self._hits(self._proj(tmp, 7, "〈実コスト〉")), [])

    def test_no_ladder_tag_not_double_reported(self):
        with tempfile.TemporaryDirectory() as tmp:   # 階梯タグ無し → evidence-tag の担当（二重報告しない）
            self.assertEqual(self._hits(self._proj(tmp, 7, "〈二次〉")), [])


class DecBasedOnTest(unittest.TestCase):
    def _dec(self, based):
        return (f"---\nid: DEMO-DEC-001\ntitle: テスト決定\ndate: 2026-07-02\n"
                f"type: pivot\nbased-on: {based}\n---\n\n# テスト決定\n\n"
                f"根拠: [[DEMO-ACT-001]]\n")

    def test_missing_based_on_warned(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = make_project(tmp, {"wiki/decisions/DEMO-DEC-001.md": self._dec("")})
            self.assertTrue(any(p.check == "dec-based-on" for p in hwlint.lint_project(root)))

    def test_present_based_on_ok(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = make_project(tmp, {
                "wiki/decisions/DEMO-DEC-001.md": self._dec("[DEMO-ACT-001]"),
                "wiki/activities/DEMO-ACT-001.md": act(),
            })
            self.assertEqual([p for p in hwlint.lint_project(root) if p.check == "dec-based-on"], [])


class RelationCycleTest(unittest.TestCase):
    def _hits(self, root):
        return [p for p in hwlint.lint_project(root) if p.check == "relation-cycle"]

    def test_self_reference_detected(self):
        rec = with_fm(hyp(id="DEMO-H-001"), "derived-from: DEMO-H-001")
        with tempfile.TemporaryDirectory() as tmp:
            root = make_project(tmp, {"wiki/hypotheses/DEMO-H-001.md": rec})
            self.assertTrue(self._hits(root))

    def test_cycle_detected(self):
        h1 = with_fm(hyp(id="DEMO-H-001"), "leads-to: [DEMO-H-002]") + "\n因果先: [[DEMO-H-002]]\n"
        h2 = with_fm(hyp(id="DEMO-H-002"), "leads-to: [DEMO-H-001]") + "\n因果先: [[DEMO-H-001]]\n"
        with tempfile.TemporaryDirectory() as tmp:
            root = make_project(tmp, {"wiki/hypotheses/DEMO-H-001.md": h1,
                                      "wiki/hypotheses/DEMO-H-002.md": h2})
            self.assertTrue(self._hits(root))

    def test_acyclic_ok(self):
        h1 = with_fm(hyp(id="DEMO-H-001"), "leads-to: [DEMO-H-002]") + "\n因果先: [[DEMO-H-002]]\n"
        h2 = hyp(id="DEMO-H-002")
        with tempfile.TemporaryDirectory() as tmp:
            root = make_project(tmp, {"wiki/hypotheses/DEMO-H-001.md": h1,
                                      "wiki/hypotheses/DEMO-H-002.md": h2})
            self.assertEqual(self._hits(root), [])


class OntologyDerivationTest(unittest.TestCase):
    """語彙が ontology.yaml から一元導出され、コード側に再定義が残っていないこと（ドリフト防止）。"""

    def test_evidence_tags_derived_from_ladder_and_aux(self):
        # 山括弧つきタグ = 階梯（序列）＋補助タグ。ハードコードでなく導出。
        expected = tuple(f"〈{t}〉" for t in ontology.EVIDENCE_LADDER + ontology.EVIDENCE_AUX)
        self.assertEqual(ontology.EVIDENCE_TAGS, expected)
        # 補助タグ 〈二次〉〈架空〉が SSoT に取り込まれている。
        self.assertIn("〈二次〉", ontology.EVIDENCE_TAGS)
        self.assertIn("〈架空〉", ontology.EVIDENCE_TAGS)

    def test_evidence_rank_orders_ladder(self):
        self.assertEqual(ontology.EVIDENCE_RANK["発言"], 0)
        self.assertLess(ontology.EVIDENCE_RANK["自認"], ontology.EVIDENCE_RANK["実コスト"])
        self.assertLess(ontology.EVIDENCE_RANK["実コスト"], ontology.EVIDENCE_RANK["支払い"])

    def test_fictional_markers_from_ontology(self):
        self.assertIn("架空", ontology.FICTIONAL_MARKERS)
        self.assertIn("シミュレーション", ontology.FICTIONAL_MARKERS)

    def test_hwlint_uses_ontology_vocab(self):
        # hwlint はローカル再定義でなく ontology の定数を参照する。
        self.assertIs(hwlint.EVIDENCE_TAGS, ontology.EVIDENCE_TAGS)
        self.assertIs(hwlint.FICTIONAL_MARKERS, ontology.FICTIONAL_MARKERS)

    def test_team_role_not_dropped(self):
        # 自分たち仮説(role: team)が role マッピングに存在する（従来は欠落していた）。
        self.assertEqual(ontology.TEAM_TYPES, {"自分たち仮説"})

    def test_importance_weights_from_ontology(self):
        self.assertEqual(ontology.IMPORTANCE_FOCUS, 8)
        self.assertEqual(ontology.IMPORTANCE_OTHER, 4)
        # gen_views の importance() が ontology の重みを使う（マジックナンバーの再定義なし）。
        import gen_views
        self.assertEqual(gen_views.importance({"type": "課題仮説", "importance": "auto"}, "CPF"),
                         ontology.IMPORTANCE_FOCUS)   # CPF の重点タイプ
        self.assertEqual(gen_views.importance({"type": "ソリューション仮説", "importance": "auto"}, "CPF"),
                         ontology.IMPORTANCE_OTHER)   # CPF では非重点


class UntestedFocusTest(unittest.TestCase):
    """OI-F1: 重点仮説なのに検証活動(ACT)の hypotheses 入次数が0（未着手）の検出。"""
    STAGE = "current-stage: CPF\n"

    def _hits(self, root):
        return [p for p in hwlint.lint_project(root) if p.check == "untested-focus"]

    def test_focus_without_activity_detected(self):
        # CPF の重点タイプ(課題仮説)で検証活動が1本も無い → 未着手として警告
        with tempfile.TemporaryDirectory() as tmp:
            root = make_project(tmp, {
                "wiki/stage.md": self.STAGE,
                "wiki/hypotheses/DEMO-H-001.md": hyp(type="課題仮説"),
            })
            self.assertTrue(any("未着手" in p.message for p in self._hits(root)))

    def test_focus_with_activity_ok(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = make_project(tmp, {
                "wiki/stage.md": self.STAGE,
                "wiki/hypotheses/DEMO-H-001.md": hyp(type="課題仮説"),
                "wiki/activities/DEMO-ACT-001.md": act(),   # hypotheses:[DEMO-H-001]
            })
            self.assertEqual(self._hits(root), [])

    def test_in_progress_focus_without_activity_flags_mismatch(self):
        # status:検証中 なのに紐づく ACT が無い → 二重表現の破れとして警告
        rows = ["| 2026-07-01 | 1 | 検証中 | 初期作成 | — |"]
        with tempfile.TemporaryDirectory() as tmp:
            root = make_project(tmp, {
                "wiki/stage.md": self.STAGE,
                "wiki/hypotheses/DEMO-H-001.md": hyp(type="課題仮説", status="検証中", rows=rows),
            })
            self.assertTrue(any("二重表現の破れ" in p.message for p in self._hits(root)))

    def test_non_focus_type_without_activity_ok(self):
        # CPF では ソリューション仮説 は非重点 → 未着手警告は出ない
        with tempfile.TemporaryDirectory() as tmp:
            root = make_project(tmp, {
                "wiki/stage.md": self.STAGE,
                "wiki/hypotheses/DEMO-H-001.md": hyp(type="ソリューション仮説"),
            })
            self.assertEqual(self._hits(root), [])

    def test_manual_importance_makes_focus(self):
        # 非重点タイプでも手動 importance>=IMPORTANCE_FOCUS なら重点扱い
        rec = hyp(type="ソリューション仮説").replace("importance: auto", "importance: 8")
        with tempfile.TemporaryDirectory() as tmp:
            root = make_project(tmp, {
                "wiki/stage.md": self.STAGE,
                "wiki/hypotheses/DEMO-H-001.md": rec,
            })
            self.assertTrue(self._hits(root))


class AddressesGapTest(unittest.TestCase):
    """OI-F2: 課題↔解決の構造ギャップ（課題なき解決／未対応の課題）の検出。"""

    def _hits(self, root):
        return [p for p in hwlint.lint_project(root) if p.check == "addresses-gap"]

    def _verified_problem(self, id="DEMO-H-001"):
        rows = [f"| 2026-07-01 | 7 | 検証済み | 初期作成 | — |"]
        return hyp(id=id, type="課題仮説", status="検証済み", confidence="7", rows=rows)

    def test_solution_without_addresses_detected(self):
        # ソリューション仮説で addresses が空 → 課題なき解決
        with tempfile.TemporaryDirectory() as tmp:
            root = make_project(tmp, {
                "wiki/hypotheses/DEMO-H-001.md": hyp(type="ソリューション仮説"),
            })
            self.assertTrue(any("課題なき解決" in p.message for p in self._hits(root)))

    def test_refuted_solution_without_addresses_ok(self):
        # 反証されたソリューション仮説は対象外
        with tempfile.TemporaryDirectory() as tmp:
            rows = ["| 2026-07-01 | 2 | 反証 | 初期作成 | — |"]
            root = make_project(tmp, {
                "wiki/hypotheses/DEMO-H-001.md": hyp(type="ソリューション仮説",
                                                     status="反証", confidence="2", rows=rows),
            })
            self.assertEqual(self._hits(root), [])

    def test_solution_with_addresses_ok(self):
        sol = with_fm(hyp(id="DEMO-H-002", type="ソリューション仮説"), "addresses: [DEMO-H-001]")
        with tempfile.TemporaryDirectory() as tmp:
            root = make_project(tmp, {
                "wiki/stage.md": "current-stage: PSF\n",
                "wiki/hypotheses/DEMO-H-001.md": self._verified_problem(),
                "wiki/hypotheses/DEMO-H-002.md": sol,
            })
            self.assertEqual(self._hits(root), [])

    def test_verified_problem_unaddressed_in_solution_phase_detected(self):
        # 解決設計フェーズ(PSF)で検証済み課題に対応する解決が無い → 未対応の課題
        with tempfile.TemporaryDirectory() as tmp:
            root = make_project(tmp, {
                "wiki/stage.md": "current-stage: PSF\n",
                "wiki/hypotheses/DEMO-H-001.md": self._verified_problem(),
            })
            self.assertTrue(any("未対応" in p.message or "未開拓" in p.message
                                for p in self._hits(root)))

    def test_verified_problem_unaddressed_in_cpf_ok(self):
        # CPF では課題に解決が無いのは正常 → 未対応の課題は出ない
        with tempfile.TemporaryDirectory() as tmp:
            root = make_project(tmp, {
                "wiki/stage.md": "current-stage: CPF\n",
                "wiki/hypotheses/DEMO-H-001.md": self._verified_problem(),
            })
            self.assertEqual(self._hits(root), [])


class ParseFrontmatterTest(unittest.TestCase):
    """AR-03: frontmatter を PyYAML(BaseLoader) でパースしつつ「素の文字列」契約を保つ。"""

    def test_flat_scalars_and_array_contract(self):
        # スカラーは文字列、配列は "[a, b]" 文字列、空値は "" に正規化される（従来契約）。
        text = ("---\n"
                "id: DEMO-H-001\n"
                "confidence: 5\n"
                "importance: auto\n"
                "leads-to: [DEMO-H-002, DEMO-H-003]\n"
                "derived-from:\n"
                "---\n\n# body\n")
        fm = hwlint.parse_frontmatter(text)
        self.assertEqual(fm["id"], "DEMO-H-001")
        self.assertEqual(fm["confidence"], "5")          # int でなく文字列
        self.assertEqual(fm["leads-to"], "[DEMO-H-002, DEMO-H-003]")
        self.assertEqual(hwlint.parse_id_array(fm["leads-to"]), ["DEMO-H-002", "DEMO-H-003"])
        self.assertEqual(fm["derived-from"], "")         # 空値は ""

    def test_bool_like_kept_as_string(self):
        # core: true は真偽値化せず文字列 "true"（gen_views は == "true" で判定）。
        fm = hwlint.parse_frontmatter("---\ncore: true\n---\n")
        self.assertEqual(fm["core"], "true")

    def test_inline_comment_stripped(self):
        fm = hwlint.parse_frontmatter("---\nid: DEMO-H-001   # コメント\n---\n")
        self.assertEqual(fm["id"], "DEMO-H-001")

    def test_quoted_colon_value_handled(self):
        # 手書きパーサでは崩れうる引用符内コロンを正しく扱う（robustness の主目的）。
        fm = hwlint.parse_frontmatter('---\ntitle: "課題: 記録の散逸"\n---\n')
        self.assertEqual(fm["title"], "課題: 記録の散逸")

    def test_no_frontmatter_returns_empty(self):
        self.assertEqual(hwlint.parse_frontmatter("# 本文だけ\n"), {})


class WikilinkScopeTest(unittest.TestCase):
    """AR-05: wikilink の解決対象は当該プロジェクト配下に限定（クロスプロジェクト解決を防ぐ）。"""

    def test_cross_project_link_is_broken(self):
        with tempfile.TemporaryDirectory() as tmp:
            # demo プロジェクト（対象）の本文に、別プロジェクトの ID へのリンクを張る。
            rec = hyp().replace("> テスト。", "> テスト。\n\n関連: [[OTHER-H-001]]")
            root = make_project(tmp, {"wiki/hypotheses/DEMO-H-001.md": rec})
            # 兄弟プロジェクト other に OTHER-H-001 を作る（親を走査すると解決してしまう配置）。
            write(Path(tmp) / "projects" / "other", "wiki/hypotheses/OTHER-H-001.md",
                  hyp(id="OTHER-H-001"))
            self.assertTrue(any(p.check == "wikilink" and "OTHER-H-001" in p.message
                                for p in hwlint.lint_project(root)))

    def test_same_project_link_ok(self):
        with tempfile.TemporaryDirectory() as tmp:
            rec = hyp().replace("> テスト。", "> テスト。\n\n関連: [[DEMO-H-002]]")
            root = make_project(tmp, {
                "wiki/hypotheses/DEMO-H-001.md": rec,
                "wiki/hypotheses/DEMO-H-002.md": hyp(id="DEMO-H-002"),
            })
            self.assertEqual([p for p in hwlint.lint_project(root) if p.check == "wikilink"], [])


class FictionalCapProseTest(unittest.TestCase):
    """AR-04: 架空判定は構造化シグナル（〈架空〉タグ／紐づく架空ACT）に限定。地の文の語だけでは判定しない。"""

    def test_prose_marker_in_reason_without_tag_not_flagged(self):
        # 根拠セルに「架空」の語が地の文で出るが、〈架空〉タグも架空ACTも無い → 誤検出しない。
        rows = ["| 2026-07-01 | 1 | 未検証 | 初期作成 | — |",
                "| 2026-07-05 | 9 | 検証済み | 〈行動〉架空データではなく実観測 | [[DEMO-ACT-001]] |"]
        with tempfile.TemporaryDirectory() as tmp:
            root = make_project(tmp, {
                "wiki/hypotheses/DEMO-H-001.md": hyp(status="検証済み", confidence="9", rows=rows),
                "wiki/activities/DEMO-ACT-001.md": act(),   # 架空マーカーを含まない実 ACT
            })
            self.assertEqual([p for p in hwlint.lint_project(root) if p.check == "fictional-cap"], [])

    def test_fictional_tag_still_flagged(self):
        # 〈架空〉タグがあれば従来どおり上限超を検出する。
        rows = ["| 2026-07-01 | 1 | 未検証 | 初期作成 | — |",
                "| 2026-07-05 | 9 | 検証済み | 〈架空〉シミュレーション由来 | [[DEMO-ACT-001]] |"]
        with tempfile.TemporaryDirectory() as tmp:
            root = make_project(tmp, {
                "wiki/hypotheses/DEMO-H-001.md": hyp(status="検証済み", confidence="9", rows=rows),
                "wiki/activities/DEMO-ACT-001.md": act(),
            })
            self.assertTrue(any(p.check == "fictional-cap" for p in hwlint.lint_project(root)))


class IdSequenceBoundaryTest(unittest.TestCase):
    """AR-04: 欠番の取り下げ照合は数字境界つき（長い数字 ID への部分一致で誤って満たされない）。"""

    def test_longer_numeric_id_does_not_satisfy_withdrawal(self):
        # 欠番 DEMO-H-002 だが log の取り下げ記録は別 ID(DEMO-H-0025 相当)。部分一致で満たさない。
        log = "## [2026-07-02] hypothesis | DEMO-H-0025 取り下げ → レコード削除\n"
        with tempfile.TemporaryDirectory() as tmp:
            root = make_project(tmp, {
                "wiki/hypotheses/DEMO-H-001.md": hyp(),
                "wiki/hypotheses/DEMO-H-003.md": hyp(id="DEMO-H-003"),
                "wiki/log.md": log,
            })
            self.assertTrue(any(p.check == "id-seq" and "DEMO-H-002" in p.where
                                for p in hwlint.lint_project(root)))


class GenViewsTest(unittest.TestCase):
    """AR-07: ビュー生成（gen_views）の射影ロジックを fixture ベースで検証する。

    最も複雑で脆い正規表現層（テストカード抽出・next_to_verify・mermaid・addresses フィット）を
    カバーする。厳密なバイト一致でなく、主要な射影が出力に現れることを部分文字列で確認する。"""

    def _views_project(self, tmp, extra=None):
        import gen_views
        sol = hyp(id="DEMO-H-002", type="ソリューション仮説").replace(
            "importance: auto\n", "importance: auto\naddresses: [DEMO-H-001]\n")
        files = {
            "wiki/stage.md": "current-stage: CPF\n",
            "wiki/hypotheses/DEMO-H-001.md": hyp(),                 # 課題仮説（CPF 重点）
            "wiki/hypotheses/DEMO-H-002.md": sol,                   # ソリューション仮説（H-001 に addresses）
            "wiki/activities/DEMO-ACT-001.md": act(),
        }
        files.update(extra or {})
        root = make_project(tmp, files)
        return gen_views, gen_views.Project(root)

    def test_field_value_heading_and_bullet_forms(self):
        import gen_views
        heading = "## テストカード\n\n### 方法\n\n5名に問題インタビュー。\n\n### 指標\n\n該当数。\n"
        bullet = "## テストカード\n\n- **方法**: 5名に問題インタビュー。\n- **成功基準**（開始前に確定）: 3名以上。\n"
        self.assertEqual(gen_views.field_value(heading, "方法"), "5名に問題インタビュー。")
        self.assertEqual(gen_views.field_value(bullet, "方法"), "5名に問題インタビュー。")
        self.assertEqual(gen_views.field_value(bullet, "成功基準"), "3名以上。")
        self.assertEqual(gen_views.field_value(heading, "存在しない"), "—")

    def test_next_to_verify_marks_untested_focus_first(self):
        with tempfile.TemporaryDirectory() as tmp:
            # ACT を置かず、重点仮説(課題仮説)を未検証で1本だけにする → has_act=False。
            import gen_views
            root = make_project(tmp, {
                "wiki/stage.md": "current-stage: CPF\n",
                "wiki/hypotheses/DEMO-H-001.md": hyp(),
            })
            proj = gen_views.Project(root)
            nxt = gen_views.next_to_verify(proj, list(proj.hyp_records()), "CPF")
            self.assertEqual([(s, has_act) for s, _, has_act in nxt], [("DEMO-H-001", False)])
            bullets = gen_views.next_to_verify_bullets(nxt)
            self.assertTrue(any("⚠️未着手" in b for b in bullets))

    def test_gen_board_contains_core_sections(self):
        with tempfile.TemporaryDirectory() as tmp:
            gen_views, proj = self._views_project(tmp)
            out = gen_views.gen_board(proj)
            self.assertIn("# ジャベリン実験ボード", out)
            self.assertIn("DEMO-ACT-001", out)
            self.assertIn("次に検証すべき仮説", out)

    def test_gen_list_has_mermaid_and_next_to_verify(self):
        with tempfile.TemporaryDirectory() as tmp:
            gen_views, proj = self._views_project(tmp)
            out = gen_views.gen_list(proj)
            self.assertIn("```mermaid", out)
            self.assertIn("DEMO-H-001", out)
            self.assertIn("次に検証すべき仮説", out)

    def test_gen_relations_addresses_fit_table(self):
        with tempfile.TemporaryDirectory() as tmp:
            gen_views, proj = self._views_project(tmp)
            out = gen_views.gen_relations(proj)
            self.assertIn("課題↔ソリューション フィット", out)
            # 課題 H-001 の行に、addresses で対応するソリューション H-002 が現れる。
            fit_rows = [ln for ln in out.splitlines() if ln.startswith("| [[DEMO-H-001]]")]
            self.assertTrue(fit_rows and "[[DEMO-H-002]]" in fit_rows[0], out)

    def test_gen_relations_solution_without_problem_flagged(self):
        with tempfile.TemporaryDirectory() as tmp:
            # addresses を持たないソリューション仮説 → 「課題なき解決」に載る。
            lonely = hyp(id="DEMO-H-003", type="ソリューション仮説")
            gen_views, proj = self._views_project(
                tmp, {"wiki/hypotheses/DEMO-H-003.md": lonely})
            out = gen_views.gen_relations(proj)
            no_pain = [ln for ln in out.splitlines() if "課題なき解決" in ln]
            self.assertTrue(no_pain and "DEMO-H-003" in no_pain[0], out)

class RecordsModuleTest(unittest.TestCase):
    """AR-06: レコードモデルが records.py に集約され、hwlint/gen_views が同一実装を共有すること。"""

    def test_shared_model_is_same_object(self):
        import records
        import gen_views
        # hwlint と gen_views は records の Project/パーサを再利用する（重複実装でない）。
        self.assertIs(hwlint.Project, records.Project)
        self.assertIs(gen_views.Project, records.Project)
        self.assertIs(hwlint.parse_frontmatter, records.parse_frontmatter)
        self.assertIs(gen_views.importance, records.importance)
        # testcard 抽出は records に一元化され、不変チェックと gen_views で共有される。
        import check_testcard_immutable
        self.assertIs(check_testcard_immutable.testcard, records.testcard)
        self.assertIs(gen_views.testcard, records.testcard)


if __name__ == "__main__":
    unittest.main()
