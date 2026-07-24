---
name: lint
description: Wikiの健全性をチェックし、矛盾・不整合・放置レコードを検出してレポートする。ユーザーが「健全性チェック」「lint」「矛盾がないか確認」「整合性チェック」「Wikiをチェック」と言ったとき、または定期点検をしたいときに使う。
---

# /lint — Wiki健全性チェック

記録の矛盾・不整合を検出してレポートする。**検出のみで自動修正はしない**（修正はレコード側で人と相談して行う）。

> **共通規約**（プロジェクト解決・ID/接頭辞・リンク記法・.gitkeep・承認規律）は [CLAUDE.md「スキル共通規約」](../../../CLAUDE.md) が正典。lint は現在プロジェクトのレコードのみを対象にする（共通規約1）。以下は本スキル固有の手順。

## 手順0 — 決定論チェックを先に実行する

まず機械検証を走らせ、その結果をレポートの土台にする:

```bash
python3 tools/hwlint.py            # 現在のプロジェクト
python3 tools/hwlint.py --all      # 全プロジェクト
python3 tools/check_testcard_immutable.py --base origin/main   # 成功基準の事後書き換え（項目7）
```

hwlint が機械的に担う部分（下記チェック項目のうち **1 の証拠リンク・5 の index/log 同期・6 の status↔confidence 矛盾（`status-confidence`）と証拠の階梯×確信度（`evidence-floor`）・8 の ID 整合・9 の架空上限の機械判定（履歴全行走査）・10 の関係の型検証と H→H 循環（`relation-cycle`）・2 の DEC 根拠欠落（`dec-based-on`）**、および status/type/stage/confidence の語彙・範囲などのスキーマ整合）と、`check_testcard_immutable.py` が担う **7 の成功基準の事後書き換え**は、スクリプトの出力をそのまま報告に転記する（再点検に時間を使わない）。LLM は残りの**意味的チェック**（2 の孤立の文脈判断・3 矛盾する仮説・4 長期放置・6 の機械判定を超える解釈・7 の機械検出が拾えない文脈判断・9 の「明示が十分か」の判断）に集中する。

関係の型検証・二重表現は [ontology.yaml](../../../ontology.yaml) の宣言（domain/range/cardinality/inverse/must-wikilink）を単一の真実源とする。語彙(enum)も同様（`tools/ontology.py` 経由で hwlint が読む）。

## チェック項目

`wiki/` 全体を走査し、以下を検出する。

1. **証拠リンクのない「検証済み」** — status が `検証済み` なのに、確信度履歴テーブルに `[[LEARN-NNN]]`（または `[[ACT-NNN]]`）の裏付けがない仮説。
2. **孤立レコード** — どこからも wikilink で参照されていない仮説／活動／学び／意思決定。ACT が対象仮説にリンクしていない、LEARN が対象仮説・実験計画(learns-from)にリンクしていない、DEC が根拠 LEARN/ACT にリンクしていない等。
   - **DEC の判定**: 意思決定レコードは、根拠となる学び/活動への外向きリンク `[[LEARN-NNN]]`・`[[ACT-NNN]]` を持ち、`wiki/log.md`・relations ビューのバックリンク索引・board の「現在地」から辿れれば**孤立扱いしない**（index.md は生成物で DEC 節を持たないので判定材料にしない）。仮説からの内向き参照は必須にしない（persevere/pivot/kill/rollback も log・relations で辿れれば正常）。なお **frontmatter `based-on` の欠落は hwlint が `dec-based-on`（warning）で機械検出する**ので、LLM は本文リンクの文脈判断に集中する。
3. **矛盾する仮説** — 同じ対象について反対の主張を持つ仮説が両方「検証済み」になっている等。
4. **長期放置の「検証中」** — status が `検証中` のまま一定期間（目安 30日、`wiki/log.md` の最終更新日から判断）動いていない仮説。
5. **log の不整合** — `wiki/log.md` に記録のない確信度変更がある（確信度履歴テーブルの追記に対応する log 行が無い）。なお `wiki/index.md` は生成物（レコードからの射影）なので手編集の食い違いは起きない。hwlint の `index-sync`（生成 index とレコードの一致）と `log-sync`（履歴と log の一致）が機械検出する。
6. **確信度とステータスの不整合**（機械判定） — hwlint が [ontology.yaml](../../../ontology.yaml) の `status-bounds`（例: `反証`/`未検証` は上限4、`検証済み` は下限5）で **`status-confidence`（warning）** を、`evidence-floor`（例: confidence 7-8 は〈実コスト〉以上）で **`evidence-floor`（warning）** を検出する。LLM はこの機械判定を超える解釈（証拠の質の妥当性など）を補う。
7. **成功基準の事後書き換え疑い** — 学び(LEARN)が紐づいた（＝実施済みの）ACT のテストカードが後から変更された痕跡。**手順0の `check_testcard_immutable.py` が機械検出する**（`--base` にレビュー基点を渡す。pre-commit でも `--staged` で強制済み）。機械検出が拾えないケース（成功基準の意味だけ変えて字面が近い等）の文脈判断のみ LLM が補う。
8. **ID の不整合** — 重複、種別ごとの最大値との齟齬。**欠番は一律に異常としない**: `wiki/log.md` に対応する「取り下げ」記録がある欠番は正常（取り下げ運用の結果）。記録のない欠番・ID重複のみを異常として検出する。あわせて **ファイル名と frontmatter `id` の整合** を確認する: `id` はファイル名と完全一致（接頭辞つき。例 `SELF-H-001.md` → `id: SELF-H-001`）であるべきで、接頭辞なし（`id: H-001`）やファイル名と異なる `id` は不整合として報告する。
9. **架空/デモデータの未明示** — 確信度・「検証済み」の根拠が架空/デモ・シミュレーションデータ（`sources/` 冒頭に「架空」明記があるもの）なのに、仮説レコード・LEARN・ビューに「実データ未検証」の注記/フラグが無いもの。実証拠と誤認されうるため要対応として報告する。**確信度が上限（8）を超える行の架空根拠は hwlint が履歴全行を走査して `fictional-cap`（error）で検出する**（最終行だけでなく中間行の架空根拠も取りこぼさない）。LLM は「明示が十分か」の判断に集中する。
10. **関係の型違反・二重表現の欠落**（機械判定） — frontmatter の関係リンクが [ontology.yaml](../../../ontology.yaml) の宣言に反するもの: 接頭辞なし・不在参照・range 種別違反（例: `hypotheses` が H でなく ACT を指す、`learns-from` が ACT 以外を指す）・cardinality 違反（単一関係 `derived-from`・`learns-from` に複数）・domain/range サブタイプ違反（例: 課題仮説が `addresses` を持つ／`addresses` が課題仮説以外を指す）を **error**（`refs`）で検出する。加えて `must-wikilink` な関係が frontmatter にあるのに本文 wikilink `[[…]]` に無いものを **warning**（`relation-wikilink`）で検出する（二重表現規約: Obsidian グラフに辺を出すため本文にも張る）。さらに H→H 関係（`derived-from`/`leads-to`）の自己参照・循環を **error**（`relation-cycle`）で検出する。

## 出力

- 見つかった問題を種別ごとにまとめ、各項目に「対象ID・何が問題か・推奨対応」を書く。
- 問題がなければ「健全」と報告する。
- `wiki/log.md` に追記:
  `## [YYYY-MM-DD] lint | 健全性チェック実施（hwlint: error N/warning M・意味チェック: 問題K件） → 内訳`

## 守ること

- lint は検出役。確信度・ステータス・レコードを勝手に書き換えない。
- 修正が必要なら、どのスキル（`/ingest` `/decide` など）で直すべきかを提案する。
