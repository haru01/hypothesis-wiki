# 移行手順: 活動レコード(ACT)を「実験計画(ACT)」と「学び(LEARN)」に分割（2026-07）

## 背景・目的

従来 ACT は1ファイルに **テストカード（検証前・不変）** と **学習カード（検証後）** を同居させ、
`/ingest`・`/chabudai` が既存 ACT を編集して学習カードを追記していた。これを、記入タイミングで
レコードを分ける新モデルへ移行する（狙いは「あとで分析可能なイベントログ」＝更新より新規作成）:

- **ACT**＝実験計画（テストカードのみ・作成後不変）
- **LEARN**（新種別）＝学び（学習カード。検証後に新規作成。計画型は `learns-from` で ACT を参照、回顧型は ACT を持たない）
- 確信度履歴の「活動」列 citation は判定・証拠を持つ **LEARN** を指す。

スキーマ/ツール/テンプレ/スキルの変更は本移行と同じ変更セットに含む。**フォールバックは設けない**
（ツールは新モデルのみを理解する）ため、移行は本変更内で完了させる。

## 分類（既存9レコード）

| プロジェクト | ACT | type | outcome | 区分 | 移行後 |
|---|---|---|---|---|---|
| self | SELF-ACT-001 | desk-research | 起票 | CONVERT（回顧型） | → SELF-LEARN-001、ACT 削除（欠番） |
| self | SELF-ACT-002 | interview | 支持 | SPLIT | ACT 存続（テストカード）＋ SELF-LEARN-002 |
| self | SELF-ACT-003 | interview | 支持 | SPLIT | ACT 存続 ＋ SELF-LEARN-003 |
| self | SELF-ACT-004 | interview | 反証 | SPLIT | ACT 存続（プロトタイプ/スクリプト付き）＋ SELF-LEARN-004 |
| self | SELF-ACT-005 | self-reflection | 是正 | CONVERT（回顧型） | → SELF-LEARN-005、ACT 削除（欠番） |
| ai-reskilling | AIRE-ACT-001 | desk-research | 起票 | CONVERT | → AIRE-LEARN-001、ACT 削除（欠番） |
| ai-reskilling | AIRE-ACT-002 | interview | （未実施） | STRIP | ACT 存続（テストカードのみ）・LEARN なし |
| ai-reskilling | AIRE-ACT-003 | interview | （未実施） | STRIP | ACT 存続（テストカードのみ）・LEARN なし |
| ai-reskilling | AIRE-ACT-004 | self-reflection | 是正 | CONVERT | → AIRE-LEARN-002、ACT 削除（欠番） |

区分の定義:
- **SPLIT**（計画型・学習カード記入済み）: ACT はテストカードのみに縮小（`outcome`・学習カード削除）。学習カードを新規 LEARN に移し `learns-from: <ACT>` を付与。
- **CONVERT**（回顧型 desk-research/self-reflection・学習カード記入済み）: 新規 LEARN に中身を移し、旧 ACT を削除（`learns-from` なし）。ACT 番号は欠番として再利用しない。
- **STRIP**（計画型・学習カード未記入）: ACT はテストカードのみに縮小（LEARN は作らない）。

## 手順（`tools/migrate_act_learn.py` が機械実行）

1. `wiki/learnings/` を作成（`.gitkeep` があれば削除）。
2. 各 ACT を本文の `## 学習カード` 境界で逐語分割（転記誤り防止）。区分に従い LEARN 作成／ACT 縮小／ACT 削除。
   - LEARN frontmatter: `id/title/type/date/stage/(learns-from)/hypotheses/outcome`。本文＝対象仮説 wikilink＋（計画型のみ）`実験計画: [[ACT]]`＋生データ/揺さぶり材料の相対リンク＋学習カード。
   - プロトタイプ/スクリプトの相対リンク行は `activities/` 起点なので LEARN には持ち込まない（ACT 側に残す）。
   - `⚠️架空` 等のマーカーは学び側（LEARN）に必ず残す（`fictional-cap`/board 警告の検出源）。
3. **citation 張り替え**: 仮説(H)の確信度履歴「活動」列・意思決定(DEC)の `based-on` と本文・`stage.md` の `[[ACT]]` を、対応する `[[LEARN]]` へ張り替える（判定/証拠は LEARN に移るため）。削除 ACT を指す全参照も LEARN へ（フォールバックなし＝リンク切れを残さない）。
   - LEARN 自身の由来 ACT（`learns-from` と `実験計画` リンク）は ACT を指したまま残す（LEARN→ACT 関係を壊さない）。
   - 存続 ACT のテストカード内にある「削除された ACT」への参照のみ LEARN へ修復する（例 SELF-ACT-002 目的の `[[SELF-ACT-001]]`→`[[SELF-LEARN-001]]`）。
4. `wiki/log.md` に移行の事実を追記（削除 ACT は「取り下げ・再利用しない」を含め、`id-seq` 警告を回避）。**過去行は編集しない**。
5. `sources/` は不変（触らない）。移行後にビュー（`board/list/relations/index`）を全再生成。

再実行時: 一度きり（冪等でない）。やり直すには `git checkout -- projects/` で復元し、`rm -rf projects/*/wiki/learnings` してから再実行する。

## 注意（テストカード不変チェックとの関係）

存続 ACT のうち、削除 ACT への参照をテストカード内で修復したもの（例 SELF-ACT-002）は、テストカード本文が
base と変わる。これは後知恵バイアスの成功基準書き換えではなく、**移設したレコードへのリンク修復**である。
`tools/check_testcard_immutable.py` は「LEARN が紐づいた ACT のテストカード変更」を検出するため、
**本移行のコミットに限り** この検出は想定内（コミット時にフックが止める場合は移行コミットで `--no-verify`、
またはレビューで本ドキュメントを根拠に許容する）。移行後の通常運用ではテストカードは書き換えない。

## 検証（移行後に必ず実行）

```bash
python3 tools/ontology.py                       # SSoT 自己点検
python3 tools/gen_ontology_doc.py               # ontology.md 再生成
for p in self ai-reskilling; do for v in board list relations index; do
  python3 tools/gen_views.py $v --project $p; done; done
python3 tools/hwlint.py --all                   # error 0 を確認
```

期待: hwlint error 0（`self` の evidence-tag 警告は移行前から存在する既知の warning で、本移行は増減させない）。
board が計画(ACT)＋学び(LEARN)を1実験に束ね、回顧型 LEARN が単独実験として出る。relations に `learns-from`（実験計画）辺が出る。

## ロールバック

移行はコミット単位で行う。取り消すには当該コミットを revert する（`git revert` / `git checkout <前のコミット> -- projects/ tools/ templates/ ontology.yaml ontology.md CLAUDE.md AGENTS.md .claude/`）。
`wiki/learnings/` は新規追加なので revert 後に残ったら削除する。
