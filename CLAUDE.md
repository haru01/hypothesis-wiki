# 仮説検証Wiki — スキーマ

このリポジトリは、仮説検証活動（CPF→FPF→PSF→SPF→PMF）を通じて育てるLLM-wikiである。
AIはこのファイルの規約に従って「規律あるWikiの保守者」として振る舞う。

## プロジェクト（案件単位）

仮説検証は**案件（プロジェクト）単位**で分ける。各プロジェクトは `projects/<slug>/` 配下に
自分の `sources/`（生データ）と `wiki/`（生成・保守層）を持つ。スキーマ層はリポジトリ全体で共有する。
現在アクティブなプロジェクトは `projects/current.md` の `current-project: <slug>` が持つ。
スキルはまず `projects/current.md` を読み、`projects/<slug>/` 配下を対象に動く（詳細は `projects/README.md`）。

以下このスキーマで `sources/` `wiki/` と書くときは、断りがなければ**現在のプロジェクトの
`projects/<slug>/sources/`・`projects/<slug>/wiki/`** を指す。

## 3層アーキテクチャ

| 層 | 場所 | 編集権 |
|---|---|---|
| Raw Sources（不変層） | `projects/<slug>/sources/` | 人間が置く。AIは**読むだけ。編集・削除禁止** |
| The Wiki（生成・保守層） | `projects/<slug>/wiki/` | AIが規約に従って作成・更新する |
| The Schema（設定層） | `CLAUDE.md`・`playbooks/`・`templates/`・`.claude/skills/` | 人間が合意の上で変更する（全プロジェクト共有） |

## レコード種別とスキーマ

すべてのレコードは `templates/` の雛形に従う。ファイル名は**IDそのもの**で、**プロジェクト接頭辞つき**
（例 `SELF-H-001.md`）。Obsidian のwikilinkはファイル名がvault全体で一意でないと解決しないため、
接頭辞 `<PREFIX>-` で衝突を防ぐ。タイトルはfrontmatter `title` と本文H1に持つ。
相互参照は**必ず本文にwikilink**（`[[SELF-H-001]]`）で書く
（frontmatter配列だけではObsidianグラフに辺が現れないため）。

### 仮説レコード `projects/<slug>/wiki/hypotheses/<PREFIX>-H-NNN.md`

```yaml
id: H-001
title: 短いタイトル
type: 状況・行動仮説 | 課題仮説 | ソリューション仮説 | 買ってもらえる仮説 | 自分たち仮説
status: 未検証 | 検証中 | 検証済み | 反証
confidence: 1-10
stage: CPF | FPF | PSF | SPF | PMF   # この仮説を主に検証するステージ
importance: auto | 1-10              # auto = 現在ステージから自動決定
derived-from: H-NNN                  # 省略可。派生・ピボット・巻き戻し再出発の系譜
```

本文: 反証可能な仮説文／前提／系譜リンク／確信度履歴テーブル（日付・確信度・ステータス・根拠・`[[ACT-NNN]]`）。

### 活動レコード `projects/<slug>/wiki/activities/<PREFIX>-ACT-NNN.md`

```yaml
id: ACT-001
title: 短いタイトル
type: interview | demo | survey | mvp-test | desk-research | self-reflection
date: YYYY-MM-DD
stage: CPF | FPF | PSF | SPF | PMF
hypotheses: [H-NNN, ...]
```

本文は2部構成（Strategyzer流）:
- **テストカード**（検証前に記入・後から書き換えない）: 目的／方法／指標／成功基準
- **学習カード**（検証後に記入）: 事実（observed）／解釈（inference）／驚き・想定外／確信度の更新テーブル／次のアクション

### 意思決定レコード `projects/<slug>/wiki/decisions/<PREFIX>-DEC-NNN.md`

```yaml
id: DEC-001
title: 短いタイトル
date: YYYY-MM-DD
type: stage-transition | pivot | persevere | rollback | kill
based-on: [ACT-NNN, ...]
```

本文: 確信度スナップショット（全重要仮説の当時の値）／選択肢と判断理由／巻き戻しポイント
（この判断が誤りと判明したときどの仮説状態・どの問いに戻るか）。

## 確信度とステータス（2軸・別管理）

**確信度（1〜10）** — 証拠の強さの目安:

| 確信度 | 目安 |
|---|---|
| 1-2 | 勘・思いつき |
| 3-4 | 二次情報・状況証拠あり |
| 5-6 | 検証中で手応えあり（定性的証拠が集まりつつある） |
| 7-8 | 検証済みで確信度が高い |
| 9 | 反証を試みても崩れなかった |
| 10 | 事実（観測された確定事項） |

**ステータス** — 検証の進捗: `未検証` → `検証中` → `検証済み` ／ `反証`

### 不変ルール（AIが必ず守ること）

1. **確信度・ステータスの変更は必ず活動（ACT）か意思決定（DEC）に紐づける**。根拠レコードなしに書き換えない
2. 変更時は仮説レコードの確信度履歴テーブルに1行追記し、`projects/<slug>/wiki/log.md` にも追記する
3. `projects/<slug>/sources/` は読み取り専用。`projects/<slug>/wiki/log.md` は追記のみ（過去行の編集禁止）
4. `projects/<slug>/wiki/views/` は生成物。記録の修正はレコード側で行い、ビューは再生成する
5. ID採番は**種別×プロジェクトごと**に既存最大値+1で、プロジェクト接頭辞つき（例 `SELF-H-001`）。IDの再利用禁止（取り下げた番号は欠番として残す）
6. テストカードの成功基準は検証開始後に書き換えない（後知恵バイアス防止）

## ステージと重要度

現在ステージは（プロジェクトごとに）`projects/<slug>/wiki/stage.md` が持つ。各ステージの詳細
（問いかけバンク・検証手法・移行基準）は共有の `playbooks/<stage>.md` を参照。

**ステージ→重点仮説タイプ**（`importance: auto` の解決に使う）:

| ステージ | 重点仮説タイプ（重要度 高=8 として扱う） |
|---|---|
| CPF | 状況・行動仮説、課題仮説 |
| FPF | 課題仮説、自分たち仮説 |
| PSF | ソリューション仮説 |
| SPF | ソリューション仮説、買ってもらえる仮説 |
| PMF | 買ってもらえる仮説 |

重点タイプ以外の `auto` は重要度4として扱う。手動指定（1-10）があればそれが優先。

**次に検証すべき仮説** = 重要度が高く、確信度が低く、ステータスが未検証/検証中のもの
（アサンプションマッピングの「重要×証拠なし」象限）。

## log.md の形式（追記専用・grep可能）

```
## [YYYY-MM-DD] <type> | <ID> <要約> → <影響仮説と確信度変化>
```

type は `hypothesis` `interview` `demo` `survey` `mvp-test` `desk-research` `self-reflection` `decision` `lint` のいずれか。
例: `grep "decision" projects/<slug>/wiki/log.md` で意思決定だけを抽出できる。

## ワークフロー（スキルとの対応）

| やりたいこと | スキル |
|---|---|
| 新しいプロジェクト（案件）を雛形から作成する | `/new-project` |
| 曖昧なアイデアを仮説レコードに精錬する（1問ずつ深掘り） | `/grill` |
| 次に検証すべき仮説の抽出とテストカード立案 | `/plan` |
| インタビュー録・デモ記録の取り込みと学習カード作成・確信度更新 | `/ingest` |
| バリュープロポジション／一覧／ボードのビュー生成 | `/view` |
| ステージ移行・ピボット・巻き戻しの意思決定 | `/decide` |
| Wikiの健全性チェック | `/lint` |
| 判断（確信度・検証済み・移行）を能動的にゆさぶり認知不協和とバイアスをツッコむ | `/yusaburi` |

## 記述言語

すべて日本語。技術用語・ID・frontmatterキーは原文のまま。
