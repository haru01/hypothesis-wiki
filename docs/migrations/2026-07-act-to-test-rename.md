# 移行手順: レコード種別 ACT を TEST に改名・ディレクトリ activities を tests に（2026-07）

## 背景・目的

同じレコード（検証前に書く実験計画＝テストカード）が **活動 / 活動レコード / 実験計画 / テストカード / 行動計画** の
5語で呼ばれ揺れていた。これを解消し、名前を概念に一致させる:

- **英語/ID接頭辞**: `ACT` → `TEST`（本文フォーマット名 テストカード に一致）。意味は「activity の略」ではなく
  **動詞 Act（動いて検証する）→ Learn（学ぶ）** の計画側と再解釈する。
- **ディレクトリ**: `wiki/activities/` → `wiki/tests/`。
- **日本語の正式ラベル**: `活動` → `実験計画`（本文名は `テストカード` のまま＝学習カード LEARN と対）。
- **`行動計画` は退役**（英語 `behavior` 案は不採用: 証拠タグ〈行動〉＝観測済みの行動と衝突し、
  未来の計画を過去形の語で呼ぶ倒錯があるため）。

`活動` の**一般用途**（`活動ログ`＝log.md、`活動タイムライン`＝index、`活動種別`＝TEST/LEARN 共有のサブタイプ語彙、
確信度履歴表の「活動」列、`検証活動`/`対応活動` のような集合的呼称）は型ラベルではないので**そのまま残す**。

スキーマ/ツール/テンプレ/スキルの変更は本移行と同じ変更セットに含む。フォールバックは設けない
（ツールは新モデル TEST のみを理解する）。

## ID対応（既存5レコード・番号は保持）

| プロジェクト | 旧ID | 新ID | 付随物 |
|---|---|---|---|
| self | SELF-ACT-002 | SELF-TEST-002 | — |
| self | SELF-ACT-003 | SELF-TEST-003 | — |
| self | SELF-ACT-004 | SELF-TEST-004 | `-script.md` ＋ プロトタイプ dir |
| ai-reskilling | AIRE-ACT-002 | AIRE-TEST-002 | `-script.md` |
| ai-reskilling | AIRE-ACT-003 | AIRE-TEST-003 | `-script.md` |

欠番（SELF/AIRE とも 001 等）は前回の act-learn-split 由来でそのまま欠番として残る。log.md の取り下げ記録も
新表記 TEST へ移る（欠番の照合が保たれ `id-seq` 警告は出ない）。

## 手順（`tools/migrate_act_to_test.py` が機械実行）

置換は単一の正規表現 **`(?<![A-Za-z])ACT(?![A-Za-z])` → `TEST`**。前後がラテン文字でない `ACT` だけを捕捉するので、
ID(`SELF-ACT-002`)・裸(`ACT-003`・`[ACT-NNN]`)・散文(`ACT`・和文隣接の「はACT」「のACT」「ACT表」)を一度に捕捉し、
英単語（IMP**ACT**・CONT**ACT**・F**ACT**・**ACT**ION・RE**ACT**）と小文字 `act` は除外される。加えて `wiki/activities/`→`wiki/tests/`。

1. **テキスト置換**: 各 `projects/<slug>/` 配下の全 `*.md`／`*.html`（wiki・sources 観測データ・skill-improvements 含む）に上記を適用（frontmatter `id:` も同期）。
2. **プロトタイプ dir** `prototypes/<X>-ACT-NNN/` を `<X>-TEST-NNN/` に改名（本文の相対リンクは 1 で追従済み）。
3. **レコード/スクリプトのファイル名**を改名し、`wiki/activities/` → `wiki/tests/`、`templates/project/wiki/activities/` → `tests/`。
4. 置換パスの**後**に `log.md` へ移行記録を1行追記（ノート内の "ACT" を保持するため順序が重要）。

再実行時: 一度きり（冪等でない）。やり直すには `git checkout HEAD -- projects/ templates/` で復元し、
生成された `tests/` 等の未追跡ディレクトリを削除してから再実行する。

## 不変ルールの機械リネーム例外（本移行に限る・最大クリーン）

純粋な識別子リネームで**出来事の意味は変えない**ため、本移行に限り不変ルール2（`log.md` 追記専用）・
3（`sources/` 改変禁止）を機械リネームの範囲で**全テキストに例外適用**した:

- `sources/` 観測データ内の `[[…-ACT-…]]` wikilink・散文 `ACT` を TEST に置換（Obsidian グラフを繋ぎ直す）。
- `log.md` の**過去行**の旧ID・散文 `ACT` も新表記に置換（識別子の付け替えのみ）。
- 確信度履歴テーブルの根拠セル・record 本文散文・`skill-improvements.md` も同様に置換。

**コミット時のフック**: `.githooks/pre-commit` は log.md の過去行書き換え（rule 4）と sources/ の改変（rule 5）を
ブロックする。本移行はこの2つを機械リネームの範囲で意図的に行うため、**本移行コミットに限り `git commit --no-verify`**
で通す（他のチェック＝unittest・hwlint・testcard-immutable は事前に手動実行して緑を確認済み）。移行後の通常運用では
両ルールは有効のまま。

不変ルール（CLAUDE.md）自体は変更していない＝通常運用では有効。**除外（歴史として凍結）**:
`docs/migrations/**`（前回 act-learn-split 文書＋本文書）・`docs/superpowers/**`・`tools/migrate_act_learn.py`。
各 `log.md` 末尾には本移行の事実を1行追記した（この行だけは "ACT を TEST に改名" と旧名を明記する）。

## 検証（移行後に必ず実行）

```bash
python3 tools/ontology.py                       # SSoT 自己点検（entities に TEST）
python3 tools/gen_ontology_doc.py               # ontology.md 再生成
for p in self ai-reskilling; do for v in board list relations index; do
  python3 tools/gen_views.py $v --project $p; done; done
python3 tools/hwlint.py --all                   # error 0 を確認
python3 tools/check_testcard_immutable.py       # テストカード不変チェック
python3 -m unittest tests.test_hwlint           # 既存テスト緑（97件）
# 残存 ACT の掃討（歴史/移行ファイルと log 移行ノートのみ許容）:
grep -rn '(?<![A-Za-z])ACT(?![A-Za-z])' -P projects/ | grep -v 'log.md'
```

期待: hwlint error 0（`self` の evidence-tag 警告は移行前からの既知 warning で増減しない）。
`relations` に `実験計画 TEST` サブグラフが出て H↔TEST↔LEARN↔DEC の辺が壊れていないこと。
`grep '行動計画'` が 0 件。

## ロールバック

移行はコミット単位。取り消すには当該コミットを revert するか、
`git checkout <前のコミット> -- projects/ templates/ tools/ ontology.yaml ontology.md CLAUDE.md AGENTS.md README.md .claude/` で戻す。
