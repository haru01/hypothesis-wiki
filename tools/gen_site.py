#!/usr/bin/env python3
"""GitHub Pages 公開用の content ツリー（Quartz に渡す staged ツリー）を組み立てる。

不変層 `projects/*/sources/` を含めず、**オリジナルを一切書き換えずに**コピー側だけで
リンクを Quartz が解決できる形に正規化する。生成物なので手編集せず再生成する。

## 方針

- **リポジトリルートからの相対パスを保って写す**。既存の相対リンクは `../` の深さが
  ファイル位置に対して正しく書かれているので、ディレクトリを再配置しない
- **内部リンクは wikilink 形式に寄せる**。Quartz の `markdownLinkResolution: shortest` は
  「ファイル名で解決」なので、素の `[[SELF-H-001]]` は ID が全体一意である限り確実に通る。
  相対 md リンクも同じ形に寄せてしまえば、解決戦略の差異に晒される面が一つに減る。
  wikilink は位置に依存しないため、スキルをリネーム配置しても深さが壊れない
- 解決先が公開範囲外（`sources/`）ならリンクを外す。解決先の無い wikilink
  （`[[H-NNN]]` のような雛形のプレースホルダ）はコードスパンにする——記法の説明なので
  リンクでないほうが正しく、かつ「壊れリンク0件」のゲートが意味を持つようになる

## 使い方

    python3 tools/gen_site.py [--out .site/staged] [--strict]

`--strict` は想定外の未解決リンクがあれば非ゼロ終了する（CI 用）。
"""
import argparse
import os
import posixpath
import re
import shutil
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent

# ---- 公開範囲（wiki + schema 層）------------------------------------------------
# schema 層の単体ファイル。ontology.yaml は非 md だが CLAUDE.md から 12 箇所参照されており、
# Quartz が静的アセットとして出すのでリンクとして機能する。
TOP_FILES = ["CLAUDE.md", "AGENTS.md", "README.md", "ontology.md", "ontology.yaml"]
TOP_DIRS = ["playbooks", "templates", "docs"]

# .claude/skills/<name>/SKILL.md の staged 先。素の <name>.md だと
# templates/learning.md・playbooks/lean-canvas.md と basename がぶつかるため接頭辞を付ける。
SKILLS_SRC_DIR = ".claude/skills"
SKILL_DEST_DIR = "claude-skills"
SKILL_DEST_PREFIX = "skill-"

# サイトトップ（<out>/index.md として書き出す）
SITE_INDEX_SRC = "site/index.md"

# `.site` は自分自身の出力先。いまは走査対象がリポジトリ直下ではないので実害は無いが、
# 走査範囲を広げた瞬間に前回のビルド出力を再帰的に取り込み始めるので先に閉じておく。
EXCLUDE_DIR_NAMES = {".obsidian", "__pycache__", ".git", ".claude", "node_modules", ".site"}
NON_PUBLIC_RE = re.compile(r"^projects/[^/]+/sources/")

# プレースホルダらしさ（未解決でも警告しない）。
# 接頭辞なしのレコードID（`H-001`・`LEARN-NNN`・`ACT` など）は、実IDが必ずプロジェクト接頭辞つき
# である以上、雛形・設計メモの中の例示でしかありえない。
PLACEHOLDER_RE = re.compile(
    r"NNN|<[^>]*>|\{[^}]*\}|YYYY-MM-DD|\.\.\.|…"
    r"|^(?:H|TEST|LEARN|DEC|ACT)(?:[-/]|$)")


# ---- ステージング対象の列挙 -----------------------------------------------------

def _iter_files(root: Path):
    """root 配下のファイルを列挙する（除外ディレクトリと隠しファイルを飛ばす）。

    除外判定は**リポジトリ相対**で行う。REPO 自体が worktree（`.claude/worktrees/...`）に
    置かれることがあり、絶対パスの部分名で判定すると全件が落ちる。"""
    for p in sorted(root.rglob("*")):
        if not p.is_file():
            continue
        rel = p.relative_to(REPO)
        if any(part in EXCLUDE_DIR_NAMES for part in rel.parts):
            continue
        if p.name.startswith("."):
            continue
        yield p


def iter_included(repo: Path):
    """(元パス, staged 相対パス) を列挙する。staged 相対パスは POSIX 文字列。"""
    for name in TOP_FILES:
        p = repo / name
        if p.is_file():
            yield p, name

    for d in TOP_DIRS:
        root = repo / d
        if root.is_dir():
            for p in _iter_files(root):
                yield p, p.relative_to(repo).as_posix()

    projects = repo / "projects"
    readme = projects / "README.md"
    if readme.is_file():
        yield readme, "projects/README.md"
    for proj in sorted(projects.iterdir()) if projects.is_dir() else []:
        wiki = proj / "wiki"
        if not wiki.is_dir():
            continue
        for p in _iter_files(wiki):
            yield p, p.relative_to(repo).as_posix()

    skills = repo / SKILLS_SRC_DIR
    for skill in sorted(skills.iterdir()) if skills.is_dir() else []:
        p = skill / "SKILL.md"
        if p.is_file():
            yield p, f"{SKILL_DEST_DIR}/{SKILL_DEST_PREFIX}{skill.name}.md"


def source_to_staged_map(pairs) -> dict:
    """リポジトリ相対パス → staged 相対パス。リンク解決に使う。"""
    return {src.relative_to(REPO).as_posix(): dest for src, dest in pairs}


# ---- リンク解決 ---------------------------------------------------------------

class Resolver:
    """リポジトリ相対パス／wikilink ターゲットを staged ツリー上の wikilink 形に解決する。"""

    def __init__(self, staged_map: dict):
        self.staged_map = staged_map                    # repo 相対 → staged 相対
        # ページになるのは md だけ。非 md（ontology.yaml・html・svg）は静的アセットとして
        # 出るだけで wikilink の終点にならないので索引に入れない
        # （入れると ontology.md と ontology.yaml が同じ stem で衝突する）。
        self.pages = {d for d in staged_map.values() if d.endswith(".md")}
        self.by_stem = {}                               # stem → staged 相対の集合
        for dest in self.pages:
            stem = posixpath.splitext(posixpath.basename(dest))[0]
            self.by_stem.setdefault(stem, set()).add(dest)

    def canonical(self, dest: str) -> str:
        """staged 相対パスを wikilink ターゲットにする。

        basename が全体一意ならそれだけ（Quartz の shortest が最も確実に効く形）。
        重複するならフルパスで修飾する。"""
        stem = posixpath.splitext(posixpath.basename(dest))[0]
        if len(self.by_stem.get(stem, ())) == 1:
            return stem
        return posixpath.splitext(dest)[0]

    def resolve_repo_path(self, repo_rel: str):
        """リポジトリ相対パスを staged 相対パスにする（範囲外は None）。"""
        return self.staged_map.get(posixpath.normpath(repo_rel))

    def resolve_by_stem(self, path: str):
        """basename が全体一意ならそれで解決する（パス指定が間違っているリンクの救済）。

        Obsidian も shortest 解決でこう振る舞うので、元の相対パスの深さが間違っていても
        vault 内では辿れてしまう。そのため誤ったパスが温存されがちで、ここで救う必要がある。"""
        stem = posixpath.splitext(posixpath.basename(path))[0]
        hits = self.by_stem.get(stem)
        return next(iter(hits)) if hits and len(hits) == 1 else None

    def resolve_wikilink_target(self, target: str):
        """wikilink のターゲットを staged 相対パスにする（解決不能は None）。

        `SELF-H-001`（basename）と `playbooks/cpf.md`（パス）の両形を受ける。"""
        t = target.strip()
        if not t:
            return None
        t = re.sub(r"\.md$", "", t)
        hits = self.by_stem.get(posixpath.basename(t))
        if hits:
            if len(hits) == 1:
                return next(iter(hits))
            # basename が重複: パス指定なら一致するものを選ぶ
            for dest in sorted(hits):
                if posixpath.splitext(dest)[0].endswith(t):
                    return dest
            return None
        for dest in self.pages:
            if posixpath.splitext(dest)[0] == t:
                return dest
        return None


# ---- コードスパン・フェンスの保護 ------------------------------------------------

FENCE_RE = re.compile(r"^\s*(```|~~~)")
INLINE_CODE_RE = re.compile(r"(`+)(.*?)\1")


def _protect(text: str):
    """フェンス済みブロックとインラインコードをトークンに退避する。

    記法の説明としてバッククォートで囲まれた `[[H-NNN]]` を書き換えてしまわないため。"""
    slots = []

    def stash(s: str) -> str:
        slots.append(s)
        return f"\x00{len(slots) - 1}\x00"

    out, fence, buf = [], None, []
    for line in text.split("\n"):
        m = FENCE_RE.match(line)
        if fence is None and m:
            fence, buf = m.group(1), [line]
            continue
        if fence is not None:
            buf.append(line)
            if line.strip().startswith(fence):
                out.append(stash("\n".join(buf)))
                fence = None
            continue
        out.append(INLINE_CODE_RE.sub(lambda mm: stash(mm.group(0)), line))
    if fence is not None:                      # 閉じ忘れフェンスはそのまま戻す
        out.append("\n".join(buf))
    return "\n".join(out), slots


def _restore(text: str, slots) -> str:
    return re.sub(r"\x00(\d+)\x00", lambda m: slots[int(m.group(1))], text)


# ---- 本文の書き換え -----------------------------------------------------------

WIKILINK_RE = re.compile(r"\[\[([^\[\]|#]+)(#[^\[\]|]*)?(?:\|([^\[\]]*))?\]\]")
MDLINK_RE = re.compile(r"\[([^\]]*)\]\(([^)\s]+)\)")


def rewrite(text: str, src_repo_rel: str, resolver: Resolver, warn, note) -> str:
    """1ファイル分の本文を書き換える。src_repo_rel は**元の**位置（相対リンクの基準）。

    `warn` は直すべき不具合（--strict で落とす）、`note` は設計どおりの報告に使う。"""
    body, slots = _protect(text)
    src_dir = posixpath.dirname(src_repo_rel)

    def on_wikilink(m):
        target, anchor, alias = m.group(1), m.group(2) or "", m.group(3)
        dest = resolver.resolve_wikilink_target(target)
        if dest is None:
            # 解決先が無い（雛形のプレースホルダ等）。リンクでなくコードスパンにする
            if not PLACEHOLDER_RE.search(target):
                warn(f"{src_repo_rel}: 解決できない wikilink [[{target}]] をコードスパンにした")
            return f"`{m.group(0)}`"
        canon = resolver.canonical(dest)
        return f"[[{canon}{anchor}|{alias}]]" if alias is not None else f"[[{canon}{anchor}]]"

    def on_mdlink(m):
        label, target = m.group(1), m.group(2)
        path, _, anchor = target.partition("#")
        if "://" in target or target.startswith("#") or not path:
            return m.group(0)                  # 外部リンク・同一ページ内アンカーはそのまま
        repo_rel = posixpath.normpath(posixpath.join(src_dir, path)) if src_dir else posixpath.normpath(path)

        if not path.endswith(".md"):
            # 非 md（プロトタイプの html・SVG・ontology.yaml）はページでなく静的アセット。
            # ただし相対パスのままだと Quartz が壊す: shortest 解決は複数階層の相対リンクの
            # `../` を落として content ルート絶対パスとして扱うため、
            # `../prototypes/X/index.html` が `prototypes/X/index` に化けて前置が消える。
            # そこで最初から content ルート絶対パスで書いておく。
            dest = resolver.staged_map.get(repo_rel)
            if dest is None:
                # 公開ツリーに無い非 md（tools/・site/・.github/ 等）。相対リンクのままだと
                # Quartz が内部リンクと見なして壊れリンクになる。GitHub の絶対 URL で書くべき。
                if not repo_rel.startswith("..") and not PLACEHOLDER_RE.search(path):
                    warn(f"{src_repo_rel}: 公開ツリーに無い非 md へのリンク {path}"
                         f"（相対リンクのままだと壊れリンクになる。GitHub の絶対 URL で書く）")
                return m.group(0)
            if dest == path:
                return m.group(0)
            suffix = f"#{anchor}" if anchor else ""
            return f"[{label}]({dest}{suffix})"

        suffix = f"#{anchor}" if anchor else ""

        dest = resolver.resolve_repo_path(repo_rel)
        if dest is not None:
            return f"[[{resolver.canonical(dest)}{suffix}|{label}]]"
        if NON_PUBLIC_RE.match(repo_rel):
            return f"{label}（生データ・未公開）"  # 公開範囲外。設計どおりリンクを外す
        if repo_rel.startswith(".."):
            return label                       # 雛形の断片（コピー先を基準に書かれた深さ）
        dest = resolver.resolve_by_stem(path)
        if dest is not None:
            # 救済できているのでサイトは壊れない。オリジナル側の直すべき点の報告に留める
            # （Obsidian も shortest 解決で辿れてしまうため、誤ったパスが温存されがち）。
            note(f"{src_repo_rel}: リンク先 {path} はパスとして辿れないので basename で解決した"
                 f"（オリジナル側のリンク切れ → {dest}）")
            return f"[[{resolver.canonical(dest)}{suffix}|{label}]]"
        if not PLACEHOLDER_RE.search(path):
            warn(f"{src_repo_rel}: 公開ツリーに無いリンク先 {path} のリンクを外した")
        return label

    body = WIKILINK_RE.sub(on_wikilink, body)
    body = MDLINK_RE.sub(on_mdlink, body)
    return _restore(body, slots)


# ---- 組み立て ---------------------------------------------------------------

def build(out: Path, strict: bool) -> int:
    pairs = list(iter_included(REPO))
    site_index = REPO / SITE_INDEX_SRC
    if site_index.is_file():
        pairs.append((site_index, "index.md"))
    else:
        print(f"warning: {SITE_INDEX_SRC} が無いのでサイトトップを作らない", file=sys.stderr)

    resolver = Resolver(source_to_staged_map(pairs))
    warnings, notes = [], []   # warnings=直すべき不具合（--strict で落とす）／notes=設計どおりの報告

    if out.exists():
        shutil.rmtree(out)
    out.mkdir(parents=True)

    for src, dest in pairs:
        target = out / dest
        target.parent.mkdir(parents=True, exist_ok=True)
        if src.suffix != ".md":
            shutil.copy2(src, target)
            continue
        src_repo_rel = src.relative_to(REPO).as_posix()
        text = src.read_text(encoding="utf-8")
        target.write_text(
            rewrite(text, src_repo_rel, resolver, warnings.append, notes.append),
            encoding="utf-8")
        # 更新日時を引き継ぐ。staged は git 管理外なので Quartz は日付を
        # ファイルシステムから取る（コピー時刻だと全ページが「今」になる）。
        st = src.stat()
        os.utime(target, ns=(st.st_atime_ns, st.st_mtime_ns))

    md = sum(1 for _, d in pairs if d.endswith(".md"))
    print(f"staged: {len(pairs)} files ({md} markdown) → {out}")
    for n in notes:
        print(f"note: {n}", file=sys.stderr)
    for w in warnings:
        print(f"warning: {w}", file=sys.stderr)
    if notes:
        print(f"note: 計 {len(notes)} 件（救済済み・サイトは壊れない）", file=sys.stderr)
    if warnings:
        print(f"warning: 計 {len(warnings)} 件（直すべきリンク）", file=sys.stderr)
        if strict:
            return 1
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description="GitHub Pages 公開用の content ツリーを組み立てる")
    ap.add_argument("--out", default=".site/staged", help="出力先（既定 .site/staged）")
    ap.add_argument("--strict", action="store_true",
                    help="直すべきリンク（warning）があれば非ゼロ終了する。"
                         "救済済みの報告（note）では落ちない")
    args = ap.parse_args()
    out = Path(args.out)
    if not out.is_absolute():
        out = REPO / out
    return build(out, args.strict)


if __name__ == "__main__":
    sys.exit(main())
