# 移行手順: 学び(LEARN)に出典 `sources` を導入し、確信度の根拠鎖を端まで機械検証する（2026-07）

## 背景・目的

このリポジトリの生命線は「確信度は必ず証拠に紐づく」だが、紐づけの実装は
**`H の確信度履歴 → [[LEARN-NNN]]`** で止まっていた。その先の
**`LEARN → projects/<slug>/sources/<生データ>`** は本文のコードスパン
（例 ``生データ: `sources/2026-07-16-....md` ``）で書かれており、リンクでもなく frontmatter にも無く、
**どのツールも検証していなかった**。帰結は3つ:

1. **出典切れが検出されない** — 生データを改名・削除しても、確信度を支えた記録が無言で宙に浮く。
2. **架空データの蓋（`fictional-cap: 8`）の連鎖が最初の一歩で切れていた** —
   `templates/project/sources/README.md` は生データ冒頭への「架空・実証拠として扱わない」明記を要求するが、
   `check_fictional_cap`・`fictional_records` が見ていたのは **TEST/LEARN 本文の文字列一致**だった。
   生データ側の宣言は誰も読んでいなかったため、**著者が偶然 LEARN 本文にも「架空」と書き写している場合にだけ
   蓋が働く**という状態だった（規約が実質機能していない）。
3. **取り込み忘れが検出されない** — `sources/` に置いたのに LEARN にならなかった生データを機械が拾えない。
   これは README 冒頭が挙げる課題「記録が散逸し過去の学びが忘れられる」そのもの。

## 変更の内容

### スキーマ（SSoT）

`ontology.yaml` に **`provenance` 節**を新設した。型付きリンク（`relations`）は record→record なので、
**グラフの外（不変層 `sources/`）を指す出典はレコードの属性**として別に宣言する
（relation にすると `domain/range ⊆ entities` の不変条件が壊れる）。

```yaml
provenance:
  field: sources
  domain: [LEARN]
  cardinality: many
  base-dir: sources
  must-body-link: true
  required-for-types: [interview, demo, survey, mvp-test, desk-research]
  fictional-header-scan-lines: 12
```

あわせて `entities.LEARN.fields` に `{name: sources, required: false, kind: provenance}` を登録した
（フィールド宣言そのものも同時に導入。`docs/kg-improvements.md` の KG-01 を参照）。

### レコードの書き方（frontmatter と本文の二重表現）

```yaml
sources: [2026-07-17-problem-interviews-sim.md]     # sources/ 基準の相対パス配列
```

```markdown
生データ: [2026-07-17-problem-interviews-sim.md](../../sources/2026-07-17-problem-interviews-sim.md)
```

生データは接頭辞つきノートではないので **wikilink は解決しない**。本文側は相対mdリンクで書く
（`wiki/learnings/` からの深さは `../../sources/`）。

### 機械検証（`tools/hwlint.py`）

| チェック | level | 検出内容 |
|---|---|---|
| `provenance`（paths） | **error** | `sources` のパスが `sources/` 配下に実在しない／絶対パス・`..` を含む |
| `provenance`（presence） | warning | `required-for-types` の LEARN で `sources` が空 |
| `provenance`（body-link） | warning | frontmatter にあるのに本文の相対mdリンクに無い |
| `provenance-chain` | warning | **確信度を上げた履歴行が指す LEARN に出典が無い**（根拠鎖の断絶） |
| `orphan-source` | warning | どの LEARN からも参照されていない生データ（取り込み忘れ） |

`check_fictional_cap` は判定を **出典の冒頭宣言を一次情報**とするよう修理した（本文マーカーは、出典を持たない
旧レコード向けの後方互換フォールバックとして残す）。導出は `records.fictional_activities` に集約し、
ビューの警告バナー（`gen_views.fictional_records`）も同じ導出を共有する。

## 実施した移行（backfill）

既存 LEARN 7件の frontmatter に `sources` を追記し、本文のコードスパンを相対mdリンクへ置き換えた。

| レコード | 出典 |
|---|---|
| `SELF-LEARN-001` | `2026-07-16-desk-research-corporate-hypothesis-testing.md` |
| `SELF-LEARN-002` | `2026-07-17-problem-interviews-sim.md` |
| `SELF-LEARN-003` | `2026-07-18-followup-interviews-sim.md` |
| `SELF-LEARN-004` | `2026-07-18-lp-interviews-sim.md` |
| `SELF-LEARN-005` | `2026-07-19-chabudai-self.md` |
| `AIRE-LEARN-001` | `2026-07-19-desk-research-ai-reskilling.md` |
| `AIRE-LEARN-002` | `2026-07-19-chabudai-ai-reskilling.md` |

**確信度・ステータス・確信度履歴テーブル・`log.md` は一切変更していない**（不変ルール1・2・3）。
frontmatter へのキー追加と本文リンク記法の変更のみ。`sources/` の既存ファイルは読むだけで触っていない。

TEST には `sources` を入れない。テストカードは検証**前**の計画であり、観測データを持たないため
（`provenance.domain` は `[LEARN]`）。

## 移行前後の lint

- 移行前（チェック追加直後）: self warning 15 → **35**（provenance 4・provenance-chain 11・orphan-source 5）、
  ai-reskilling 0 → **3**。
- backfill 後: **self warning 15（レガシーの `evidence-tag` のみ）・ai-reskilling 0・error 0**。

## 後方互換・フォールバック

- `sources` は `required: false`。出典を持たない旧 LEARN は `provenance`（presence）warning になるだけで error にはならない。
- 架空判定は本文マーカーのフォールバックを残すため、`sources` 未記入の旧レコードでも従来どおり蓋が働く。
- `self-reflection` は `required-for-types` の外（内省は出典なしを正当とする）。
