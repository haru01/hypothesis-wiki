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
- **モックアップ**は単一HTML内に画面を `<section data-screen>` で持ち、JS で show/hide 切替する（画面数・複雑さ次第で分割してよい＝スキル判断）。各画面に遷移ボタンを置く。
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

### モックアップ骨格（2〜3画面・JSで画面切替）

```html
<!-- 生成物。/prototype で再生成。紐づく活動: {{PREFIX-ACT-NNN}} / 仮説: {{PREFIX-H-NNN}} / 生成日: {{YYYY-MM-DD}} -->
<!doctype html>
<html lang="ja">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{{アプリ名}} モックアップ</title>
<style>
  :root { --fg:#1a1a1a; --bg:#f0f2f5; --card:#fff; --accent:#2563eb; --muted:#6b7280; --line:#e5e7eb; }
  * { box-sizing:border-box; margin:0; padding:0; }
  body { font-family:system-ui,-apple-system,"Hiragino Kaku Gothic ProN","Noto Sans JP",sans-serif; color:var(--fg); background:var(--bg); }
  .device { max-width:420px; margin:24px auto; background:var(--card); min-height:80vh; border-radius:24px; box-shadow:0 8px 40px rgba(0,0,0,.12); overflow:hidden; display:flex; flex-direction:column; }
  .appbar { background:var(--accent); color:#fff; padding:16px 18px; font-weight:600; }
  .screen { display:none; flex:1; padding:20px; }
  .screen.active { display:block; }
  .card { background:var(--bg); border:1px solid var(--line); border-radius:12px; padding:16px; margin-bottom:12px; }
  button { font:inherit; cursor:pointer; }
  .btn { display:block; width:100%; background:var(--accent); color:#fff; border:0; padding:14px; border-radius:10px; font-size:15px; margin-top:12px; }
  .tabbar { display:flex; border-top:1px solid var(--line); }
  .tabbar button { flex:1; background:none; border:0; padding:12px; color:var(--muted); font-size:13px; }
  .tabbar button.active { color:var(--accent); font-weight:600; }
  @media (prefers-color-scheme: dark) {
    :root { --fg:#e5e7eb; --bg:#0f1115; --card:#1b1f27; --line:#2a2f3a; --muted:#9ca3af; }
    body { background:#000; }
  }
</style>
</head>
<body>
  <div class="device">
    <div class="appbar" id="appbar">{{画面1タイトル}}</div>

    <section class="screen active" data-screen="1">
      <div class="card">{{画面1の主コンテンツ（対象仮説の入り口）}}</div>
      <button class="btn" onclick="go(2)">{{画面2へ進むアクション}}</button>
    </section>

    <section class="screen" data-screen="2">
      <div class="card">{{画面2の主コンテンツ}}</div>
      <button class="btn" onclick="go(3)">{{画面3へ進むアクション}}</button>
    </section>

    <section class="screen" data-screen="3">
      <div class="card">{{画面3の主コンテンツ（提供価値の核）}}</div>
      <button class="btn" onclick="go(1)">最初に戻る</button>
    </section>

    <nav class="tabbar">
      <button class="active" onclick="go(1)">{{タブ1}}</button>
      <button onclick="go(2)">{{タブ2}}</button>
      <button onclick="go(3)">{{タブ3}}</button>
    </nav>
  </div>

  <script>
    var titles = {1:"{{画面1タイトル}}", 2:"{{画面2タイトル}}", 3:"{{画面3タイトル}}"};
    function go(n){
      document.querySelectorAll('.screen').forEach(function(s){ s.classList.toggle('active', s.dataset.screen == String(n)); });
      document.querySelectorAll('.tabbar button').forEach(function(b,i){ b.classList.toggle('active', i+1 === n); });
      document.getElementById('appbar').textContent = titles[n];
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
