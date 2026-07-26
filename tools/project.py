#!/usr/bin/env python3
"""現在アクティブなプロジェクト（slug）の解決を一箇所に集約する（SSoT・ドリフト防止）。

選択は各自ローカルの `.env`（gitignore 対象・キー CURRENT_PROJECT）が持つ。
解決順は override（--project）→ .env の CURRENT_PROJECT → "self"（既定）。
PREFIX（接頭辞）はここでは扱わない——レコードID／slug.upper() から records.Project.prefix が導出する。

外部依存（python-dotenv 等）は使わず、必要な最小の .env 行パーサだけを持つ（ゼロ依存の決定論方針）。
"""
import re
from pathlib import Path

DEFAULT_PROJECT = "self"


def read_env_value(repo: Path, key: str):
    """repo/.env から key の値を返す（無ければ None）。

    `KEY=VALUE` 形式のみ対応。`#` から始まる行・空行は無視し、キー/値の前後空白と
    値を囲む単一/二重引用符を剥がす。`export KEY=VALUE` も受ける。
    """
    env = repo / ".env"
    if not env.exists():
        return None
    for line in env.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("export "):
            line = line[len("export "):].lstrip()
        m = re.match(r"([A-Za-z_][A-Za-z0-9_]*)\s*=\s*(.*)$", line)
        if not m or m.group(1) != key:
            continue
        val = m.group(2).strip()
        if len(val) >= 2 and val[0] == val[-1] and val[0] in "\"'":
            val = val[1:-1]
        return val
    return None


def resolve_current_project(repo: Path, override: str = None) -> str:
    """対象プロジェクトの slug を解決する: override → .env の CURRENT_PROJECT → "self"。"""
    if override:
        return override
    env_val = read_env_value(repo, "CURRENT_PROJECT")
    if env_val:
        return env_val
    return DEFAULT_PROJECT
