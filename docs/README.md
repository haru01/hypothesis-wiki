# docs/ — スキーマ層の付随ドキュメント

レコード（`projects/<slug>/wiki/`）でもスキーマの正本（`ontology.yaml`・`CLAUDE.md`）でもない、
補助的な文書を置く。

| ファイル | 中身 |
|---|---|
| [backlog.md](backlog.md) | **改善バックログ**。いま実害が出ているもの／保留／方針確定・不採用の3節 |
| [competitive-analysis.md](competitive-analysis.md) | 競合マップと差別化の論点（2026-07-18 時点）。`/desk-research` が調査の書き方の模範として参照する |

## 改善項目の起票

`backlog.md` に書く。ID は軸ごとに既存最大+1で採番し、**再利用しない**
（**OI**＝オントロジー ／ **SI**＝スキル ／ **KG**＝ナレッジグラフ ／ **AR**＝アーキテクチャ）。

対応が済んだ項目は**本文から消す**。何をなぜ直したかはコミットメッセージと差分が正本で、
バックログに完了記録を積み増さない（積むと現役の項目が埋もれ、記述自体が実態から古びる）。

## 消えた記録の辿り方

2026-08-01 に、完了済みの記録を本文から外して git 履歴へ送った。以下は履歴から読める。

| 消したもの | 中身 |
|---|---|
| `docs/ontology-improvements.md` | オントロジー改善バックログ OI-A1〜H（A〜D・F・G1 は対応済み） |
| `docs/skill-improvements.md` | スキル改善バックログ SI-001〜029 ＋ 一巡テストの記録2件 |
| `docs/kg-improvements.md` | ナレッジグラフ改善バックログ KG-01〜10（論文チェックリストとの対照表つき） |
| `docs/architecture-improvements.md` | アーキテクチャ改善バックログ AR-01〜12 |
| `docs/migrations/` | 完了済みの移行手順3本（ACT→TEST 改名・ACT/LEARN 分割・出典の型化） |
| `docs/superpowers/` | 実装済みの設計書2本・実行済みの実装計画3本 |

```bash
git log --oneline -- docs/                       # 履歴を辿る
git show <整理コミット>^:docs/kg-improvements.md   # 削除直前の全文を読む
```
