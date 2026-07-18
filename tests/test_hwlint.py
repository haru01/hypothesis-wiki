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


if __name__ == "__main__":
    unittest.main()
