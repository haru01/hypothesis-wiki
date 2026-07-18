# `/prototype` スキル Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 検証対象の仮説から、インタビュー・デモで見せるHTML+JS自己完結プロトタイプ（LP／2〜3画面モックアップ）を生成し `demo`/`interview` の ACT に紐づける `/prototype` スキルを追加する。

**Architecture:** 既存の Wiki スキル群と同じく `.claude/skills/<name>/SKILL.md` 単一ファイルとして実装する（このリポジトリの各スキルは SKILL.md 1枚のみで、バンドル資産は持たない慣習）。品質担保のためのレイアウト骨格（LP用・モックアップ用）は SKILL.md 内に埋め込みHTMLとして持つ。スキルは検証*前*の準備活動であり、確信度・ステータスは変更しない（検証後の更新は `/ingest` の責務）。

**Tech Stack:** Markdown（SKILL.md）＋ 生成対象は素の HTML/CSS/JavaScript（外部依存ゼロ・`file://` 起動）。自動テストの仕組みは無く、検証は構造チェック（grep）と project `self` での結合ドライランで行う。

## Global Constraints

以下は spec 由来のプロジェクト全体制約。全タスクの要件に暗黙で含まれる。

- 生成HTMLは**外部依存ゼロ**（CDN・外部フォント・fetch・画像URL無し）で `file://` からダブルクリック起動できること。
- ID・ファイル名は**プロジェクト接頭辞つき**（例 `SELF-ACT-005`）。frontmatter `id` はファイル名と完全一致。
- 相互参照は**本文に wikilink**（`[[SELF-H-012]]`）。schema層（`playbooks/`・`templates/` 等）への参照は**相対mdリンク**。
- **確信度・ステータスはこのスキルでは変更しない**（検証後の学習カード記入・確信度更新は `/ingest`）。
- テストカードの**成功基準は検証開始後に書き換えない**。
- `sources/` は読み取り専用。`wiki/prototypes/` は生成物。`log.md` は追記のみ（過去行の編集禁止）。
- すべて日本語。技術用語・ID・frontmatterキーは原文のまま。

---

## File Structure

| ファイル | 責務 |
|---|---|
| `.claude/skills/prototype/SKILL.md`（新規） | スキル本体。frontmatter（name/description＝トリガー語）＋ワークフロー＋埋め込みレイアウト骨格＋守ること |
| `CLAUDE.md`（修正・139行付近） | ワークフロー表に `/prototype` の行を1つ追加 |
| `projects/self/wiki/...`（Task 3のドライランで生成／更新） | 結合検証で作る実サンプル（ACT-005・prototype・log・仮説wikilink） |

---

### Task 1: `.claude/skills/prototype/SKILL.md` を作成

**Files:**
- Create: `.claude/skills/prototype/SKILL.md`

**Interfaces:**
- Consumes: なし（新規スキル）。実行時に読むのは `projects/current.md`・`projects/<slug>/wiki/`・`templates/activity.md`。
- Produces: スキル `/prototype`。トリガー語「モックアップ」「プロトタイプ」「LP」「ランディングページ」「画面を作って」「prototype」「mockup」「mock」「lp」。生成物 `projects/<slug>/wiki/prototypes/<PREFIX>-ACT-NNN/index.html`。

- [ ] **Step 1: SKILL.md を下記の内容で作成する**

以下を**そのまま** `.claude/skills/prototype/SKILL.md` に書く（埋め込みHTML骨格を含む完全版）。

> ⚠️ **以下は初期版**。実装後にモックアップ＝Webアプリ化・LP＝SaaS系フル構成＋SVGへ更新し、**骨格HTMLは `templates/prototype-lp.html`・`templates/prototype-mockup.html` に外出し**、SKILL.md は薄い参照に変更した。**現在の正典は `.claude/skills/prototype/SKILL.md` と `templates/prototype-*.html`**。再実行・再現時は現行版を用いること（詳細は末尾「実装後の骨格更新」）。

````markdown
---
name: prototype
description: 検証対象の仮説からインタビュー・デモで見せるクリッカブルなHTML+JS自己完結プロトタイプ（ランディングページ／2〜3画面モックアップ）を生成し、demo/interview の活動レコード（ACT）に紐づける。ユーザーが「モックアップ」「プロトタイプ」「LP」「ランディングページ」「画面を作って」「prototype」「mockup」「mock」「lp」と言ったときに使う。
---

# /prototype — 検証用HTMLプロトタイプ生成

検証対象の仮説（H）から、インタビュー・デモで見せる **HTML＋JavaScript 自己完結プロトタイプ**（ランディングページ、または2〜3画面モックアップ）を「サクッと」生成し、`demo`/`interview` の活動レコード（ACT）に紐づける。生成物は検証活動の小道具であり、実データ計測は行わない（定性フィードバック中心）。

> **パス・ID規約**: 以下の `wiki/` は現在のプロジェクト `projects/<slug>/` 配下を指す（現在のプロジェクトは `projects/current.md` の `current-project`）。ID とファイル名は**プロジェクト接頭辞つき**（例 `SELF-ACT-005`）。frontmatter `id` はファイル名と完全一致。相互参照は本文に wikilink（`[[SELF-H-012]]`）、schema層（`templates/` など）への参照は相対mdリンク。

> **責務の境界**: このスキルは検証*前*の準備活動である。**確信度・ステータスは変更しない**。見せて反応を得たあとの学習カード記入・確信度更新は `/ingest` に委ねる。ACT はテストカード（前半）だけの状態で作られ、これは「テストカードは検証前に記入」規約と一致する。

## ワークフロー

### 1. 現在プロジェクト解決
`projects/current.md` の `current-project: <slug>` を読む。以降 `wiki/` は `projects/<slug>/wiki/`。接頭辞（例 `SELF`）もここで確定する。

### 2. 検証対象の仮説（H）を選ぶ
- 引数で仮説ID（例 `SELF-H-012`）が指定されていればそれを対象にする。
- 無指定なら「次に検証すべき仮説」（重要度高 × 確信度低 × ステータス未検証/検証中）を `wiki/hypotheses/` から数件抽出して提示し、選ばせる。現在ステージ（`wiki/stage.md`）の重点仮説タイプ（`CLAUDE.md` のステージ→重点仮説タイプ表）を優先する。

### 3. 種別を選ぶ
- **LP（ランディングページ）** … 価値提案を1ページで訴求。買ってもらえる仮説・ソリューション仮説の反応を見るのに向く。
- **モックアップ（2〜3画面）** … 操作の流れを見せる。ソリューション仮説の使い勝手・理解を見るのに向く。
- 引数（`lp` / `mockup`）または対話で決める。

### 4. 最小インテイク（自動ドラフト → 確認）
対象仮説と関連レコード（課題仮説・ソリューション仮説・買ってもらえる仮説）から内容を**自動ドラフト**し、ユーザーは確認・上書きするだけ。聞くのは2〜3点まで。
- LP: ヒーロー見出し（価値提案の一文）／対象顧客／主要ペイン／CTA文言
- モックアップ: 見せたい画面（2〜3）とその主目的

価値提案・ペインは仮説文・確信度履歴・関連する課題仮説から引く。ドラフトの根拠にした仮説を明示する。

### 5. ACTを解決（両対応）
- 対象仮説に紐づく **計画済みの demo/interview ACT**（テストカードは記入済みで**学習カードが未記入**のもの）があれば、それを使い、新規作成しない。
- 無ければ `templates/activity.md` に従って**最小テストカード**を新規作成する:
  - ID: 種別×プロジェクトで既存最大+1・接頭辞つき（例 既存最大が `SELF-ACT-004` なら `SELF-ACT-005`）。欠番は再利用しない。
  - `type`: `demo`（自分で操作して見せる）または `interview`（相手に見せて反応を聞く）。
  - `stage`: 現在ステージ。`hypotheses`: 対象仮説（接頭辞つき配列）。
  - テストカードの 目的／方法／指標／**成功基準** を書く。成功基準は検証開始後に書き換えない。
  - 学習カードの節（事実／解釈／驚き／確信度の更新／次のアクション）は**空の見出しのまま残す**（検証後に `/ingest` が埋める）。

### 6. 生成
`wiki/prototypes/<PREFIX>-ACT-NNN/index.html` を生成する。
- **自己完結**: インラインCSS/JS、外部依存ゼロ（CDN・外部フォント・fetch・画像URL無し）。アイコンは絵文字またはインラインSVG、写真はプレースホルダ（`<div>`＋ラベル）。`file://` でダブルクリック起動できること。
- **レスポンシブ・日本語UI**。
- **モックアップ**は**Webアプリ**を想定する（上部バー＋左サイドバーナビ＋メインコンテンツのシェル。スマホアプリ枠にしない）。単一HTML内に画面を `<section data-screen>` で持ち、JS で show/hide 切替する（画面数・複雑さ次第で分割してよい＝スキル判断）。サイドバーと各画面に遷移導線を置く。
- **CTA/フォーム**はクリックするとクライアント側で確認状態（サンクス表示など）を出すだけ。送信先（バックエンド・外部フォーム）は持たない。
- HTML先頭に生成物メタコメントを入れる:
  `<!-- 生成物。/prototype で再生成。紐づく活動: <PREFIX>-ACT-NNN / 仮説: <PREFIX>-H-NNN / 生成日: YYYY-MM-DD -->`
- 下の**レイアウト骨格**を土台に、仮説内容で中身を差し替える。骨格は品質の下限を担保するもので、そのままコピーするのではなく仮説に合わせて作り込む。

### 7. 記録
- ACTレコードのテストカードに、プロトタイプへの相対リンクを1行追記する: `プロトタイプ: [index.html](../prototypes/<PREFIX>-ACT-NNN/index.html)`。
- 対象仮説レコードの本文（系譜の節、または末尾）に `[[<PREFIX>-ACT-NNN]]` を追記する（本文wikilink。frontmatter配列だけにしない）。
- `wiki/log.md` に1行追記する（追記のみ・過去行編集禁止）:
  `## [YYYY-MM-DD] <demo|interview> | <PREFIX>-ACT-NNN <要約> → プロトタイプ生成（<lp|mockup>）。<PREFIX>-H-NNN 確信度変更なし`
- **確信度・ステータスは変更しない**。仮説の確信度履歴テーブルにも行を足さない（検証前のため）。

### 8. 反復
生成後、見た目・文言の微修正を対話で受け、同じ `index.html` を上書き再生成する。テストカードの成功基準は変更しない。

## レイアウト骨格（土台。中身は仮説で差し替える）

`{{...}}` は仮説から埋める箇所。骨格は品質の下限を担保するための出発点であり、仮説の内容に応じて自由に作り込んでよい。

### LP骨格

```html
<!-- 生成物。/prototype で再生成。紐づく活動: {{PREFIX-ACT-NNN}} / 仮説: {{PREFIX-H-NNN}} / 生成日: {{YYYY-MM-DD}} -->
<!doctype html>
<html lang="ja">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{{サービス名 または 価値提案}}</title>
<style>
  :root { --fg:#1a1a1a; --bg:#fff; --accent:#2563eb; --muted:#6b7280; --card:#f5f7fa; }
  * { box-sizing:border-box; margin:0; padding:0; }
  body { font-family:system-ui,-apple-system,"Hiragino Kaku Gothic ProN","Noto Sans JP",sans-serif; color:var(--fg); background:var(--bg); line-height:1.7; }
  .wrap { max-width:840px; margin:0 auto; padding:0 20px; }
  header.hero { text-align:center; padding:72px 20px 56px; background:linear-gradient(160deg,#eef2ff,#fff); }
  .hero h1 { font-size:clamp(24px,5vw,40px); line-height:1.35; }
  .hero p.sub { color:var(--muted); margin-top:16px; font-size:clamp(15px,2.5vw,18px); }
  .cta { display:inline-block; margin-top:28px; background:var(--accent); color:#fff; border:0; padding:14px 28px; font-size:16px; border-radius:8px; cursor:pointer; }
  section { padding:48px 0; }
  section h2 { font-size:22px; margin-bottom:20px; }
  .pains { display:grid; gap:14px; }
  .pain { background:var(--card); padding:16px 18px; border-radius:8px; }
  .solution { background:var(--card); border-radius:12px; padding:28px; }
  footer { text-align:center; padding:40px 20px; color:var(--muted); font-size:13px; }
  dialog { border:0; border-radius:12px; padding:28px; max-width:360px; text-align:center; box-shadow:0 10px 40px rgba(0,0,0,.2); }
  dialog::backdrop { background:rgba(0,0,0,.4); }
  @media (prefers-color-scheme: dark) {
    :root { --fg:#e5e7eb; --bg:#0f1115; --card:#1b1f27; --muted:#9ca3af; }
    header.hero { background:linear-gradient(160deg,#1a2035,#0f1115); }
  }
</style>
</head>
<body>
  <header class="hero">
    <div class="wrap">
      <h1>{{ヒーロー見出し＝価値提案の一文}}</h1>
      <p class="sub">{{対象顧客}}向け。{{解決する主要ペインの要約}}</p>
      <button class="cta" onclick="document.getElementById('thx').showModal()">{{CTA文言（例: 無料で試す）}}</button>
    </div>
  </header>

  <section class="wrap">
    <h2>こんな場面で困っていませんか？</h2>
    <div class="pains">
      <div class="pain">😩 {{ペイン1（課題仮説から）}}</div>
      <div class="pain">😩 {{ペイン2}}</div>
      <div class="pain">😩 {{ペイン3}}</div>
    </div>
  </section>

  <section class="wrap">
    <h2>{{サービス名}}が解決します</h2>
    <div class="solution">
      <p>{{ソリューション仮説の提供価値を2〜3文で}}</p>
    </div>
  </section>

  <section class="wrap" style="text-align:center;">
    <button class="cta" onclick="document.getElementById('thx').showModal()">{{CTA文言}}</button>
  </section>

  <footer>{{サービス名}} — 検証用プロトタイプ（実サービスではありません）</footer>

  <dialog id="thx">
    <p style="font-size:32px;">🎉</p>
    <p>ありがとうございます！<br>（これは検証用モックです。実際の登録は行われません）</p>
    <button class="cta" style="margin-top:16px;" onclick="this.closest('dialog').close()">閉じる</button>
  </dialog>
</body>
</html>
```

### モックアップ骨格（Webアプリ・2〜3画面をJSで切替）

Webアプリのシェル（上部バー＋左サイドバーナビ＋メインコンテンツ）。画面は `<section data-screen>` で持ち、サイドバーで切り替える。狭い画面では縦積みになる。

```html
<!-- 生成物。/prototype で再生成。紐づく活動: {{PREFIX-ACT-NNN}} / 仮説: {{PREFIX-H-NNN}} / 生成日: {{YYYY-MM-DD}} -->
<!doctype html>
<html lang="ja">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{{アプリ名}} モックアップ</title>
<style>
  :root { --fg:#1a1a1a; --bg:#f0f2f5; --card:#fff; --accent:#2563eb; --muted:#6b7280; --line:#e5e7eb; --side:#111827; --side-fg:#e5e7eb; }
  * { box-sizing:border-box; margin:0; padding:0; }
  body { font-family:system-ui,-apple-system,"Hiragino Kaku Gothic ProN","Noto Sans JP",sans-serif; color:var(--fg); background:var(--bg); }
  .app { max-width:1080px; margin:24px auto; background:var(--card); border:1px solid var(--line); border-radius:12px; box-shadow:0 8px 40px rgba(0,0,0,.10); overflow:hidden; display:grid; grid-template-columns:220px 1fr; grid-template-rows:auto 1fr; grid-template-areas:"brand topbar" "nav main"; min-height:70vh; }
  .brand { grid-area:brand; background:var(--side); color:var(--side-fg); padding:18px 20px; font-weight:700; }
  .topbar { grid-area:topbar; border-bottom:1px solid var(--line); padding:14px 24px; display:flex; align-items:center; justify-content:space-between; }
  .topbar .who { width:32px; height:32px; border-radius:50%; background:var(--line); }
  nav.side { grid-area:nav; background:var(--side); color:var(--side-fg); padding:12px; }
  nav.side button { display:block; width:100%; text-align:left; background:none; border:0; color:var(--side-fg); opacity:.75; padding:12px 14px; border-radius:8px; font:inherit; cursor:pointer; }
  nav.side button.active { opacity:1; background:rgba(255,255,255,.12); font-weight:600; }
  main.content { grid-area:main; padding:24px; }
  .screen { display:none; }
  .screen.active { display:block; }
  h2 { font-size:20px; margin-bottom:16px; }
  .card { background:var(--bg); border:1px solid var(--line); border-radius:12px; padding:16px; margin-bottom:12px; }
  .row { display:flex; justify-content:space-between; align-items:center; gap:12px; }
  button { font:inherit; cursor:pointer; }
  .btn { background:var(--accent); color:#fff; border:0; padding:12px 20px; border-radius:8px; font-size:15px; cursor:pointer; margin-top:12px; }
  @media (max-width:720px) {
    .app { grid-template-columns:1fr; grid-template-areas:"brand" "topbar" "nav" "main"; margin:0; border-radius:0; min-height:100vh; }
    nav.side { display:flex; gap:8px; overflow-x:auto; }
    nav.side button { width:auto; white-space:nowrap; }
  }
  @media (prefers-color-scheme: dark) {
    :root { --fg:#e5e7eb; --bg:#0f1115; --card:#161a22; --line:#2a2f3a; --muted:#9ca3af; --side:#0b0e14; }
    body { background:#000; }
  }
</style>
</head>
<body>
  <div class="app">
    <div class="brand">{{アプリ名}}</div>
    <div class="topbar"><strong id="crumb">{{画面1タイトル}}</strong><div class="who" title="ユーザー"></div></div>
    <nav class="side">
      <button class="active" onclick="go(1)">{{ナビ1}}</button>
      <button onclick="go(2)">{{ナビ2}}</button>
      <button onclick="go(3)">{{ナビ3}}</button>
    </nav>
    <main class="content">
      <section class="screen active" data-screen="1">
        <h2>{{画面1タイトル}}</h2>
        <div class="card">{{画面1の主コンテンツ（対象仮説の入り口）}}</div>
        <button class="btn" onclick="go(2)">{{画面2へ進むアクション}}</button>
      </section>

      <section class="screen" data-screen="2">
        <h2>{{画面2タイトル}}</h2>
        <div class="card">{{画面2の主コンテンツ}}</div>
        <button class="btn" onclick="go(3)">{{画面3へ進むアクション}}</button>
      </section>

      <section class="screen" data-screen="3">
        <h2>{{画面3タイトル}}</h2>
        <div class="card">{{画面3の主コンテンツ（提供価値の核）}}</div>
        <button class="btn" onclick="go(1)">最初に戻る</button>
      </section>
    </main>
  </div>

  <script>
    var titles = {1:"{{画面1タイトル}}", 2:"{{画面2タイトル}}", 3:"{{画面3タイトル}}"};
    function go(n){
      document.querySelectorAll('.screen').forEach(function(s){ s.classList.toggle('active', s.dataset.screen === String(n)); });
      document.querySelectorAll('nav.side button').forEach(function(b,i){ b.classList.toggle('active', i+1 === n); });
      document.getElementById('crumb').textContent = titles[n];
    }
  </script>
</body>
</html>
```

## 守ること

- `sources/` は読むだけ。`wiki/prototypes/` は生成物。`log.md` は追記のみ。
- **確信度・ステータスはこのスキルでは変更しない**（検証後の更新は `/ingest`）。
- テストカードの成功基準は検証開始後に書き換えない。
- ID採番・接頭辞・wikilink規約に従う。frontmatter `id` はファイル名と完全一致。
- 生成HTMLは外部依存ゼロで `file://` から開けること。過剰装飾しない。
- プロトタイプHTMLは `/view` の自動集計対象外（レコードから乖離しうる生成物）。
````

- [ ] **Step 2: 構造チェックを実行する**

Run:
```bash
cd /Users/eiji/src/hypothesis-wiki
test -f .claude/skills/prototype/SKILL.md && echo "FILE OK"
grep -q '^name: prototype$' .claude/skills/prototype/SKILL.md && echo "NAME OK"
grep -qE 'モックアップ|プロトタイプ|mockup' .claude/skills/prototype/SKILL.md && echo "TRIGGER OK"
grep -q 'data-screen' .claude/skills/prototype/SKILL.md && echo "MOCKUP SKELETON OK"
grep -q '確信度・ステータス.*変更しない' .claude/skills/prototype/SKILL.md && echo "GUARD OK"
```
Expected: 5行すべて `... OK` が出力される。

- [ ] **Step 3: 埋め込み骨格が外部依存ゼロであることを確認する**

Run:
```bash
cd /Users/eiji/src/hypothesis-wiki
grep -nE 'https?://|src=|cdn|<link[^>]+href' .claude/skills/prototype/SKILL.md || echo "NO EXTERNAL REFS"
```
Expected: `NO EXTERNAL REFS`（骨格内に `http(s)://`・`src=`・CDN・外部 `<link href>` が無い）。もし何か出たら骨格を修正して外部依存を除く。

- [ ] **Step 4: コミット**

```bash
cd /Users/eiji/src/hypothesis-wiki
git add .claude/skills/prototype/SKILL.md
git commit -m "feat: /prototype スキルを追加（検証用HTMLプロトタイプ生成）

Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>"
```

---

### Task 2: CLAUDE.md のワークフロー表に `/prototype` を登録

**Files:**
- Modify: `CLAUDE.md`（139〜140行付近）

**Interfaces:**
- Consumes: Task 1 で作成した `/prototype` スキル名。
- Produces: なし（ドキュメント更新のみ）。

- [ ] **Step 1: ワークフロー表に行を追加する**

`CLAUDE.md` の `/plan` 行の直後（`/ingest` 行の直前）に `/prototype` 行を挿入する。編集対象は次の2行:

置換前:
```
| 次に検証すべき仮説の抽出とテストカード立案 | `/plan` |
| インタビュー録・デモ記録の取り込みと学習カード作成・確信度更新 | `/ingest` |
```

置換後:
```
| 次に検証すべき仮説の抽出とテストカード立案 | `/plan` |
| 検証用のHTMLプロトタイプ（LP／モックアップ）を仮説から生成しdemo/interviewのACTに紐づける | `/prototype` |
| インタビュー録・デモ記録の取り込みと学習カード作成・確信度更新 | `/ingest` |
```

- [ ] **Step 2: 登録を確認する**

Run:
```bash
cd /Users/eiji/src/hypothesis-wiki
grep -c '`/prototype`' CLAUDE.md
```
Expected: `1`（ワークフロー表に1行追加された）。

- [ ] **Step 3: コミット**

```bash
cd /Users/eiji/src/hypothesis-wiki
git add CLAUDE.md
git commit -m "docs: ワークフロー表に /prototype を追加

Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>"
```

---

### Task 3: project `self` で結合ドライラン（実サンプル生成）

スキルの記述どおりに手で一巡実行し、生成物・レコード更新が規約に沿うか検証する。既存の「スキル一巡テスト」の慣習に倣う。対象は現ステージ PSF の重点タイプ＝ソリューション仮説。ここでは **`SELF-H-012`（証拠に紐づく確信度の共有で報告の合意形成を早める）× モックアップ** を使う。`SELF-H-012` の既存 ACT（`SELF-ACT-004`）は学習カード記入済みのため、両対応ルールにより**新規 ACT（`SELF-ACT-005`）を作成**するパスを通す。

**Files:**
- Create: `projects/self/wiki/prototypes/SELF-ACT-005/index.html`
- Create: `projects/self/wiki/activities/SELF-ACT-005.md`
- Modify: `projects/self/wiki/hypotheses/SELF-H-012.md`（本文に `[[SELF-ACT-005]]` 追記）
- Modify: `projects/self/wiki/log.md`（1行追記）

**Interfaces:**
- Consumes: Task 1 の `/prototype` スキル記述、`templates/activity.md`。
- Produces: 実サンプル一式（以降このスキルの使用例になる）。

- [ ] **Step 1: 前提確認（現在プロジェクト・接頭辞・次のACT番号・対象仮説）**

Run:
```bash
cd /Users/eiji/src/hypothesis-wiki
grep 'current-project' projects/current.md
ls projects/self/wiki/activities/ | grep -oE 'SELF-ACT-[0-9]+' | sort -u | tail -1
grep -E '^(title|type|status|confidence|stage):' projects/self/wiki/hypotheses/SELF-H-012.md
```
Expected: `current-project: self` / 既存最大 `SELF-ACT-004` → 次は `SELF-ACT-005` / SELF-H-012 が `ソリューション仮説`・`検証中`（または `未検証`）で PSF。

- [ ] **Step 2: ACTレコード `SELF-ACT-005.md` を作成する（テストカードのみ・学習カードは空の見出し）**

`projects/self/wiki/activities/SELF-ACT-005.md` を作成（下記は初期版。**確定版は実際の同ファイル**——テストカードは後に箇条書き様式へ修正済み）:

```markdown
---
id: SELF-ACT-005
title: 共有ビュー・モックアップのデモ（SELF-H-012）
type: demo
date: 2026-07-18
stage: PSF
hypotheses: [SELF-H-012]
---

# 共有ビュー・モックアップのデモ（SELF-H-012）

対象仮説: [[SELF-H-012]]（証拠に紐づく確信度の共有で報告の合意形成を早める）

プロトタイプ: [index.html](../prototypes/SELF-ACT-005/index.html)

## テストカード（検証前に記入・後から書き換えない）

### 目的

[[SELF-H-012]] の価値の芯——「証拠リンク付きの確信度を一望させると、報告の場での見解のズレに早く気づける」——が、クリッカブルなモックアップを見せたときに伝わるかを確かめる。

### 方法

- 2〜3画面のモックアップ（一覧→確信度の根拠→合意状況）をインタビュー相手に操作してもらいながら見せる。
- The Mom Test 準拠で、想定と逆の反応（「これでは合意形成は早まらない」）を意図的に探す。

### 指標

- 各画面で相手が「これは自分の報告場面の課題に効く」と自発的に語ったか（発言の原文）。
- どの画面・要素に反応・混乱が集中したか。

### 成功基準（検証開始前に確定・後から書き換えない）

- 見せた相手の過半が、証拠リンク付き確信度の一覧を見て「報告時のズレに早く気づける」旨を**自発的に**述べる。
- かつ「この程度では合意形成は変わらない」という反証が優勢でない。

## 学習カード（検証後に記入）

### 事実（observed）

### 解釈（inference）

### 驚き・想定外

### 確信度の更新

| 仮説 | 更新前 | 更新後 | ステータス | 理由 |
|---|---|---|---|---|
| [[SELF-H-012]] | — | — | — | — |

### 次のアクション
```

- [ ] **Step 3: モックアップ `index.html` を生成する（骨格を SELF-H-012 の内容で差し替え）**

`projects/self/wiki/prototypes/SELF-ACT-005/index.html` を作成。モックアップ骨格を土台に、3画面を「① 仮説一覧（確信度バッジつき）／② 確信度の根拠（証拠リンク）／③ 合意状況」に差し替える（下記は初期のスマホ枠版。**確定版は実際の同ファイル**——後に Webアプリシェルへ差し替え済み）:

```html
<!-- 生成物。/prototype で再生成。紐づく活動: SELF-ACT-005 / 仮説: SELF-H-012 / 生成日: 2026-07-18 -->
<!doctype html>
<html lang="ja">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>確信度シェア モックアップ</title>
<style>
  :root { --fg:#1a1a1a; --bg:#f0f2f5; --card:#fff; --accent:#2563eb; --muted:#6b7280; --line:#e5e7eb; --side:#111827; --side-fg:#e5e7eb; }
  * { box-sizing:border-box; margin:0; padding:0; }
  body { font-family:system-ui,-apple-system,"Hiragino Kaku Gothic ProN","Noto Sans JP",sans-serif; color:var(--fg); background:var(--bg); }
  .app { max-width:1080px; margin:24px auto; background:var(--card); border:1px solid var(--line); border-radius:12px; box-shadow:0 8px 40px rgba(0,0,0,.10); overflow:hidden; display:grid; grid-template-columns:220px 1fr; grid-template-rows:auto 1fr; grid-template-areas:"brand topbar" "nav main"; min-height:70vh; }
  .brand { grid-area:brand; background:var(--side); color:var(--side-fg); padding:18px 20px; font-weight:700; }
  .topbar { grid-area:topbar; border-bottom:1px solid var(--line); padding:14px 24px; display:flex; align-items:center; justify-content:space-between; }
  .topbar .who { width:32px; height:32px; border-radius:50%; background:var(--line); }
  nav.side { grid-area:nav; background:var(--side); color:var(--side-fg); padding:12px; }
  nav.side button { display:block; width:100%; text-align:left; background:none; border:0; color:var(--side-fg); opacity:.75; padding:12px 14px; border-radius:8px; font:inherit; cursor:pointer; }
  nav.side button.active { opacity:1; background:rgba(255,255,255,.12); font-weight:600; }
  main.content { grid-area:main; padding:24px; }
  .screen { display:none; }
  .screen.active { display:block; }
  h2 { font-size:20px; margin-bottom:16px; }
  .card { background:var(--bg); border:1px solid var(--line); border-radius:12px; padding:16px; margin-bottom:12px; }
  .row { display:flex; justify-content:space-between; align-items:center; gap:12px; }
  .badge { font-size:12px; padding:3px 10px; border-radius:999px; color:#fff; white-space:nowrap; }
  .b-hi { background:#16a34a; } .b-mid { background:#d97706; } .b-lo { background:#dc2626; }
  .link { color:var(--accent); text-decoration:underline; font-size:13px; cursor:pointer; }
  .muted { color:var(--muted); font-size:13px; }
  button { font:inherit; cursor:pointer; }
  .btn { background:var(--accent); color:#fff; border:0; padding:12px 20px; border-radius:8px; font-size:15px; cursor:pointer; margin-top:12px; }
  @media (max-width:720px) {
    .app { grid-template-columns:1fr; grid-template-areas:"brand" "topbar" "nav" "main"; margin:0; border-radius:0; min-height:100vh; }
    nav.side { display:flex; gap:8px; overflow-x:auto; }
    nav.side button { width:auto; white-space:nowrap; }
  }
  @media (prefers-color-scheme: dark) {
    :root { --fg:#e5e7eb; --bg:#0f1115; --card:#161a22; --line:#2a2f3a; --muted:#9ca3af; --side:#0b0e14; }
    body { background:#000; }
  }
</style>
</head>
<body>
  <div class="app">
    <div class="brand">確信度シェア</div>
    <div class="topbar"><strong id="crumb">仮説の確信度一覧</strong><div class="who" title="ユーザー"></div></div>
    <nav class="side">
      <button class="active" onclick="go(1)">一覧</button>
      <button onclick="go(2)">根拠</button>
      <button onclick="go(3)">報告</button>
    </nav>
    <main class="content">
      <section class="screen active" data-screen="1">
        <h2>仮説の確信度一覧</h2>
        <p class="muted">報告前に、チームの確信度を一望する</p>
        <div class="card">
          <div class="row"><span>課題は切実だ</span><span class="badge b-hi">確信度 8</span></div>
          <div class="row" style="margin-top:8px;"><span class="link" onclick="go(2)">根拠を見る →</span></div>
        </div>
        <div class="card">
          <div class="row"><span>この解決策で合意形成が早まる</span><span class="badge b-mid">確信度 4</span></div>
          <div class="row" style="margin-top:8px;"><span class="link" onclick="go(2)">根拠を見る →</span></div>
        </div>
        <div class="card">
          <div class="row"><span>市場で買ってもらえる</span><span class="badge b-lo">確信度 2</span></div>
          <div class="row" style="margin-top:8px;"><span class="link" onclick="go(2)">根拠を見る →</span></div>
        </div>
        <button class="btn" onclick="go(3)">報告用にまとめる</button>
      </section>

      <section class="screen" data-screen="2">
        <h2>確信度の根拠</h2>
        <p class="muted">選択した仮説の根拠（証拠リンク）— 例: 確信度 4 の仮説</p>
        <div class="card">
          <div class="row"><strong>この解決策で合意形成が早まる</strong><span class="badge b-mid">確信度 4</span></div>
        </div>
        <div class="card">📄 <span>デモ観察 SELF-ACT-004</span><br><span class="muted">価値の芯は成功基準を充足。実在ステークホルダーでの合意形成は未検証。</span></div>
        <div class="card">⚠️ <span class="muted">弱点: 数値根拠がリンク先依存。実データではない。</span></div>
        <button class="btn" onclick="go(1)">一覧に戻る</button>
      </section>

      <section class="screen" data-screen="3">
        <h2>報告ビュー</h2>
        <p class="muted">確信度と根拠を添えて共有する</p>
        <div class="card">
          <div class="row"><span>課題は切実だ</span><span class="badge b-hi">8 ✓根拠あり</span></div>
          <div class="row" style="margin-top:8px;"><span>合意形成が早まる</span><span class="badge b-mid">4 ⚠要検証</span></div>
          <div class="row" style="margin-top:8px;"><span>買ってもらえる</span><span class="badge b-lo">2 未検証</span></div>
        </div>
        <p class="muted">「どこで見解が割れているか」が確信度の差で一目でわかる。</p>
        <button class="btn" onclick="go(1)">最初に戻る</button>
      </section>
    </main>
  </div>

  <script>
    var titles = {1:"仮説の確信度一覧", 2:"確信度の根拠", 3:"報告ビュー"};
    function go(n){
      document.querySelectorAll('.screen').forEach(function(s){ s.classList.toggle('active', s.dataset.screen === String(n)); });
      document.querySelectorAll('nav.side button').forEach(function(b,i){ b.classList.toggle('active', i+1 === n); });
      document.getElementById('crumb').textContent = titles[n];
    }
  </script>
</body>
</html>
```

- [ ] **Step 4: 仮説レコードに wikilink を追記する**

`projects/self/wiki/hypotheses/SELF-H-012.md` の本文（系譜の節、または末尾の適切な位置）に、検証活動へのwikilinkを1行追記する。例（既存の書式に合わせる）:

```markdown
- 検証プロトタイプ: [[SELF-ACT-005]]（共有ビューのモックアップをデモで見せる）
```

frontmatter の `confidence`・`status`、および確信度履歴テーブルは**変更しない**。

- [ ] **Step 5: log.md に追記する**

`projects/self/wiki/log.md` の末尾に1行追記する（過去行は編集しない）:

```
## [2026-07-18] demo | SELF-ACT-005 共有ビューのモックアップを生成（SELF-H-012） → プロトタイプ生成（mockup）。SELF-H-012 確信度変更なし（検証前の準備活動）
```

- [ ] **Step 6: 生成物と規約整合を検証する**

Run:
```bash
cd /Users/eiji/src/hypothesis-wiki
# 生成HTMLが外部依存ゼロか
grep -nE 'https?://|src=|cdn' projects/self/wiki/prototypes/SELF-ACT-005/index.html || echo "NO EXTERNAL REFS OK"
# 画面切替の要素があるか
grep -c 'data-screen' projects/self/wiki/prototypes/SELF-ACT-005/index.html
# ACTのidがファイル名と一致・学習カードが空か
grep -q '^id: SELF-ACT-005$' projects/self/wiki/activities/SELF-ACT-005.md && echo "ID OK"
# 仮説の確信度が変わっていないこと（履歴テーブルに2026-07-18行が無い）
grep -q '2026-07-18' projects/self/wiki/hypotheses/SELF-H-012.md && echo "WARN: 仮説に日付追記あり→確信度履歴を触っていないか確認" || echo "HYPOTHESIS UNTOUCHED (confidence table) OK"
# log追記
tail -1 projects/self/wiki/log.md | grep -q 'SELF-ACT-005' && echo "LOG OK"
```
Expected: `NO EXTERNAL REFS OK` / `data-screen` が3以上 / `ID OK` / `LOG OK`。仮説側は wikilink 追記のみなので、確信度履歴テーブルに `2026-07-18` 行が無いことを目視で確認する（Step 4 の wikilink 行に日付を書かなければ `HYPOTHESIS UNTOUCHED ... OK` が出る）。

- [ ] **Step 7: ブラウザで目視確認する**

Run:
```bash
open projects/self/wiki/prototypes/SELF-ACT-005/index.html
```
Expected: モックアップが表示され、左サイドバーのナビ／ボタンで3画面（一覧・根拠・報告）が切り替わる。外部リソース読み込みエラーが出ない。

- [ ] **Step 8: コミット**

```bash
cd /Users/eiji/src/hypothesis-wiki
git add projects/self/wiki/prototypes/SELF-ACT-005/ projects/self/wiki/activities/SELF-ACT-005.md projects/self/wiki/hypotheses/SELF-H-012.md projects/self/wiki/log.md
git commit -m "test(self): /prototype ドライラン — SELF-H-012 の共有ビューモックアップを生成

SELF-ACT-005（demo・テストカードのみ）とモックアップを追加。
確信度・ステータスは変更なし（検証後の更新は /ingest）。

Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>"
```

---

## Self-Review

**1. Spec coverage（spec の各要件 → 対応タスク）:**
- Wiki密結合（仮説を読む・価値提案/課題/CTA反映） → Task 1 Step1 ワークフロー2・4、Task 3 Step3
- デモ・インタビュー用途／計測コード不要 → Task 1（CTAは確認状態のみ・送信先なし）
- 置き場所 `wiki/prototypes/<PREFIX>-ACT-NNN/` → Task 1 ワークフロー6、Task 3 Step3
- 単一HTML基本・必要時分割 → Task 1（モックアップ骨格・スキル判断）
- ACT両対応 → Task 1 ワークフロー5、Task 3（新規作成パスを実行）
- リーンインテイク＋定番骨格 → Task 1 ワークフロー4・レイアウト骨格
- 確信度を変えず /ingest に委ねる → Global Constraints・Task 1 責務境界・Task 3 Step4/Step6
- CLAUDE.md 登録 → Task 2
- CTA挙動（送信先なし・確認状態のみ） → Task 1 ワークフロー6・LP骨格の dialog

**2. Placeholder scan:** 骨格内の `{{...}}` は「実行時に仮説から埋める箇所」という**意図的なテンプレートマーカー**であり、プランの未確定TODOではない（Task 3 で具体値に差し替える実例を全て記載済み）。それ以外に TBD/TODO/「適宜」等の穴埋め表現は無い。

**3. Type consistency:** 画面切替関数は全箇所で `go(n)`。切替判定はモックアップ骨格・Task 3 実装ともに `s.dataset.screen === String(n)` と `i+1 === n` で統一。生成物メタコメントの書式（`紐づく活動 / 仮説 / 生成日`）は骨格と Task 3 実装で一致。ACT の `type` は `demo`／`interview`、log の type と一致。

矛盾・欠落なし。

---

## 実装後の骨格更新（ユーザーフィードバック反映）

初回実装後、ユーザーレビューと `/simplify` で以下を更新した。**正典は `.claude/skills/prototype/SKILL.md` と `templates/prototype-lp.html`・`templates/prototype-mockup.html`**（本プランの埋め込みは初期版。細部は正典を参照）。

- **骨格の外出し（altitude修正）**: HTML骨格を SKILL.md 埋め込みから schema層の雛形 `templates/prototype-lp.html`・`templates/prototype-mockup.html` に移し、SKILL.md は参照だけの薄い形にした（`/plan` が `templates/activity.md` を参照するのと同じ方式）。骨格の正典が1箇所になり、SKILL.md とプランの二重保持によるドリフトを解消。
- **モックアップ骨格**: スマホアプリ枠（`.device`＋下部タブ）→ **Webアプリのシェル**（上部バー＋左サイドバーナビ＋メイン、狭画面で縦積み）。
- **LP骨格**: 単純な hero/課題/解決/CTA → **世間標準のSaaS系フルLP**（ナビ→ヒーロー＋インラインSVGイラスト→トラスト→課題→特徴→使い方→声→料金→最終CTA→フッター）。イメージはインラインSVG、声・料金は「デモ用ダミー／仮の表示」を明示。
- 実例: モックアップ `SELF-ACT-005`（Webアプリ）、LP `SELF-ACT-006`（`SELF-H-013` 買ってもらえる仮説・SPF先取りプレビュー）。
