#!/usr/bin/env python3
"""仮説検証Wiki の関係グラフ走査層（診断のための最小限）。

これまでビュー生成は全て1ホップの逆引き索引で、走査は hwlint の閉路検出（DFS）だけだった。
グラフ全体の歪み——断片化・孤立・ハブ・下流依存度——を出すには走査が要るので、
**診断に必要な分だけ**をこのモジュールに閉じる。

意図的に作らないもの: ランタイムのグラフ検索ツール（k ホップ照会・部分グラフ直列化）。
現規模（1案件十数〜数十レコード）では Claude が `wiki/` を直接読む方式より劣化するので採らない、と
判断済み（docs/backlog.md「方針確定・不採用」）。ここは**射影のための計算**であって
検索エンジンではない。

型・関係の定義は ontology.yaml が唯一の正本（ここに再定義しない）。
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from records import parse_id_array, entity_of  # noqa: E402
from ontology import RELATIONS  # noqa: E402


def edges(project) -> list:
    """(Relation, 始点stem, 終点stem) を frontmatter から収集する。

    終点が同一プロジェクトに実在し range 種別が一致する辺だけを返す（壊れた参照は lint の担当）。
    ビュー生成（relations）と診断が同じ辺集合を見るための単一の入口。"""
    out = []
    for stem, (_, fm, _) in project.records.items():
        ent = entity_of(stem)
        for rel in RELATIONS:
            if not rel.in_domain(ent):
                continue
            for tgt in parse_id_array(fm.get(rel.field, "")):
                if tgt in project.records and rel.in_range(entity_of(tgt)):
                    out.append((rel, stem, tgt))
    return out


def adjacency(project, undirected: bool = True) -> dict:
    """全関係を辺とした隣接リスト（既定は無向＝連結性・次数の算出用）。

    孤立レコードも空リストのキーとして必ず含める（「辺を持たない」ことを表現するため）。"""
    adj = {stem: set() for stem in project.records}
    for _, s, t in edges(project):
        adj[s].add(t)
        if undirected:
            adj[t].add(s)
        else:
            adj.setdefault(t, set())
    return {k: sorted(v) for k, v in adj.items()}


def degree(project) -> dict:
    """レコードごとの次数（全関係を無向とみなす）。ハブ＝コーパスを束ねているレコード。"""
    return {stem: len(nbrs) for stem, nbrs in adjacency(project).items()}


def components(project) -> list:
    """弱連結成分（大きい順）。

    論文 §V.E の診断: 単一成分であること自体が「関係が張れている」証拠で、
    島に割れているのは系譜(derived-from/leads-to)や検証(hypotheses)の張り忘れの構造的サイン。"""
    adj = adjacency(project)
    seen, out = set(), []
    for start in sorted(adj):
        if start in seen:
            continue
        comp, stack = set(), [start]
        while stack:
            n = stack.pop()
            if n in comp:
                continue
            comp.add(n)
            stack.extend(m for m in adj.get(n, ()) if m not in comp)
        seen |= comp
        out.append(comp)
    return sorted(out, key=lambda c: (-len(c), sorted(c)[0]))


def descendants(project, stem: str, field: str) -> set:
    """`field`（例 "leads-to"）を辿った推移閉包（自身は含まない）。

    leads-to の下流被参照数＝「崩れると波及が大きい背骨」。OI-D4 が「未カバー」と
    自認していた依存度シグナルにあたる。"""
    out, stack = set(), [stem]
    while stack:
        n = stack.pop()
        for tgt in parse_id_array(project.records.get(n, (None, {}, None))[1].get(field, "")):
            if tgt in project.records and tgt not in out and tgt != stem:
                out.add(tgt)
                stack.append(tgt)
    return out


def downstream_counts(project, field: str = "leads-to") -> dict:
    """H ごとの下流依存度（`field` の推移閉包のサイズ）。"""
    return {stem: len(descendants(project, stem, field))
            for stem in project.records if entity_of(stem) == "H"}


def isolated(project) -> list:
    """どの関係も持たない仮説（系譜も検証活動も無い＝グラフから浮いている）。

    hypotheses（TEST/LEARN→H）も辺に含まれるので、次数0は「検証活動からも参照されていない」を含む。"""
    deg = degree(project)
    return sorted(s for s in project.records if entity_of(s) == "H" and deg.get(s, 0) == 0)


def density(project) -> tuple:
    """(ノード数, 辺数, 辺/ノード比)。論文の密度指標（1.0未満=疎・2.0超=密。中間が健全）。"""
    n = len(project.records)
    m = len(edges(project))
    return n, m, (m / n if n else 0.0)
