import json
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


if __name__ == "__main__":
    unittest.main()
