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
- **自己完結**: インラインCSS/JS、外部依存ゼロ（CDN・外部フォント・fetch・画像URL無し）。**イメージ図はインラインSVGで描く**（アイコン・ヒーローイラスト等）。絵文字も可。写真はプレースホルダ（`<div>`＋ラベル）。`file://` でダブルクリック起動できること。
- **レスポンシブ・日本語UI**。
- **LP**は世間標準のSaaS系構成（ナビ→ヒーロー＋SVGイラスト→トラスト→課題→特徴→使い方→声→料金→最終CTA→フッター）を土台にする。案件に不要な節（声・料金など）は省いてよい。
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

世間標準のSaaS系LP構成（固定ナビ → ヒーロー＋イラスト → トラスト → 課題 → 特徴 → 使い方 → 声 → 料金 → 最終CTA → フッター）。イメージは**インラインSVG**で表現し外部依存を持たない（下のSVGは例。プロダクトに合わせて描き替える）。**声・料金は実在の証言や確定価格を装わない**——必ず「デモ用ダミー」「仮の表示」と明示する。案件に不要な節（料金・声など）は省いてよい（スキル判断）。

```html
<!-- 生成物。/prototype で再生成。紐づく活動: {{PREFIX-ACT-NNN}} / 仮説: {{PREFIX-H-NNN}} / 生成日: {{YYYY-MM-DD}} -->
<!doctype html>
<html lang="ja">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{{サービス名}} — {{価値提案}}</title>
<style>
  :root {
    --fg:#111827; --bg:#ffffff; --soft:#f5f7fa; --muted:#6b7280; --line:#e5e7eb;
    --accent:#2563eb; --accent2:#7c3aed; --tag:#e0e7ff; --tag-fg:#3730a3;
    --hi:#16a34a; --mid:#d97706; --lo:#dc2626;
  }
  * { box-sizing:border-box; margin:0; padding:0; }
  html { scroll-behavior:smooth; }
  body { font-family:system-ui,-apple-system,"Hiragino Kaku Gothic ProN","Noto Sans JP",sans-serif; color:var(--fg); background:var(--bg); line-height:1.75; -webkit-font-smoothing:antialiased; }
  .wrap { max-width:1080px; margin:0 auto; padding:0 24px; }
  a { color:inherit; text-decoration:none; }
  .nav { position:sticky; top:0; z-index:20; background:rgba(255,255,255,.82); backdrop-filter:saturate(180%) blur(10px); border-bottom:1px solid var(--line); }
  .nav .row { display:flex; align-items:center; justify-content:space-between; height:64px; }
  .brand { display:flex; align-items:center; gap:10px; font-weight:800; font-size:18px; }
  .nav .links { display:flex; gap:26px; color:var(--muted); font-size:14px; }
  .nav .links a:hover { color:var(--fg); }
  .btn { display:inline-flex; align-items:center; gap:8px; background:var(--accent); color:#fff; border:0; padding:11px 20px; font-size:15px; font-weight:600; border-radius:10px; cursor:pointer; }
  .btn.lg { padding:15px 30px; font-size:16px; }
  .btn.ghost { background:transparent; color:var(--accent); border:1px solid var(--line); }
  @media (max-width:720px){ .nav .links{ display:none; } }
  .hero { padding:72px 0 64px; background:radial-gradient(1200px 400px at 80% -10%, #eef2ff 0%, transparent 60%); }
  .hero .grid { display:grid; grid-template-columns:1.05fr .95fr; gap:48px; align-items:center; }
  .eyebrow { display:inline-block; font-size:13px; font-weight:700; color:var(--accent); background:var(--tag); padding:5px 12px; border-radius:999px; margin-bottom:18px; }
  .hero h1 { font-size:clamp(30px,4.6vw,52px); line-height:1.22; letter-spacing:-.01em; }
  .hero p.sub { color:var(--muted); margin-top:20px; font-size:clamp(16px,2vw,19px); max-width:34ch; }
  .hero .actions { margin-top:32px; display:flex; gap:14px; align-items:center; flex-wrap:wrap; }
  .hero .note { margin-top:16px; font-size:13px; color:var(--muted); }
  .hero .art { width:100%; height:auto; }
  @media (max-width:820px){ .hero .grid{ grid-template-columns:1fr; gap:32px; } .hero p.sub{ max-width:none; } .hero .art{ max-width:460px; } }
  .trust { border-top:1px solid var(--line); border-bottom:1px solid var(--line); background:var(--soft); }
  .trust .row { display:flex; gap:32px; justify-content:space-between; flex-wrap:wrap; padding:22px 0; color:var(--muted); font-size:14px; }
  .trust b { color:var(--fg); }
  section.block { padding:80px 0; }
  .center { text-align:center; }
  h2.sec { font-size:clamp(24px,3.2vw,34px); letter-spacing:-.01em; }
  .lead { color:var(--muted); margin-top:14px; font-size:17px; }
  .kicker { color:var(--accent); font-weight:700; font-size:13px; letter-spacing:.08em; text-transform:uppercase; }
  .pains { display:grid; grid-template-columns:repeat(2,1fr); gap:16px; margin-top:36px; }
  .pain { background:var(--soft); border:1px solid var(--line); padding:20px 22px; border-radius:14px; display:flex; gap:14px; align-items:flex-start; }
  .pain .ico { flex:0 0 auto; }
  .tag { display:inline-block; font-size:11px; background:var(--tag); color:var(--tag-fg); padding:2px 9px; border-radius:999px; margin-left:8px; vertical-align:middle; font-weight:700; }
  @media (max-width:720px){ .pains{ grid-template-columns:1fr; } }
  .features { display:grid; grid-template-columns:repeat(3,1fr); gap:22px; margin-top:44px; }
  .feature { border:1px solid var(--line); border-radius:16px; padding:28px 24px; background:var(--bg); }
  .feature .fico { width:52px; height:52px; border-radius:13px; display:grid; place-items:center; background:linear-gradient(135deg,#eef2ff,#f5f3ff); margin-bottom:18px; }
  .feature h3 { font-size:19px; margin-bottom:10px; }
  .feature p { color:var(--muted); font-size:15px; }
  @media (max-width:820px){ .features{ grid-template-columns:1fr; } }
  .steps { display:grid; grid-template-columns:repeat(3,1fr); gap:22px; margin-top:44px; }
  .step { padding:28px 24px; border:1px solid var(--line); border-radius:16px; background:var(--soft); }
  .step .num { width:38px; height:38px; border-radius:50%; background:var(--accent); color:#fff; font-weight:800; display:grid; place-items:center; margin-bottom:16px; }
  .step h3 { font-size:17px; margin-bottom:8px; }
  .step p { color:var(--muted); font-size:14px; }
  @media (max-width:820px){ .steps{ grid-template-columns:1fr; } }
  .quotes { display:grid; grid-template-columns:repeat(2,1fr); gap:22px; margin-top:40px; }
  .quote { border:1px solid var(--line); border-radius:16px; padding:26px; background:var(--bg); }
  .quote p { font-size:16px; }
  .who { display:flex; align-items:center; gap:12px; margin-top:18px; }
  .avatar { width:42px; height:42px; border-radius:50%; background:linear-gradient(135deg,#c7d2fe,#ddd6fe); }
  .who .n { font-weight:700; font-size:14px; } .who .r { color:var(--muted); font-size:13px; }
  @media (max-width:720px){ .quotes{ grid-template-columns:1fr; } }
  .plans { display:grid; grid-template-columns:repeat(3,1fr); gap:22px; margin-top:44px; }
  .plan { border:1px solid var(--line); border-radius:18px; padding:30px 26px; background:var(--bg); }
  .plan.pop { border-color:var(--accent); box-shadow:0 12px 40px rgba(37,99,235,.14); position:relative; }
  .plan.pop::before { content:"人気"; position:absolute; top:-12px; left:26px; background:var(--accent); color:#fff; font-size:12px; font-weight:700; padding:3px 12px; border-radius:999px; }
  .plan h3 { font-size:18px; }
  .price { font-size:34px; font-weight:800; margin:10px 0 4px; }
  .price small { font-size:14px; font-weight:500; color:var(--muted); }
  .plan ul { list-style:none; margin:18px 0 22px; }
  .plan li { padding:7px 0 7px 26px; position:relative; font-size:14px; color:var(--muted); }
  .plan li::before { content:"✓"; position:absolute; left:0; color:var(--hi); font-weight:800; }
  @media (max-width:820px){ .plans{ grid-template-columns:1fr; } }
  .cta-band { margin:0 24px 80px; border-radius:24px; background:linear-gradient(135deg,var(--accent),var(--accent2)); color:#fff; text-align:center; padding:64px 24px; }
  .cta-band h2 { font-size:clamp(24px,3.4vw,34px); }
  .cta-band p { opacity:.9; margin-top:12px; }
  .cta-band .btn { background:#fff; color:var(--accent); margin-top:26px; }
  footer { border-top:1px solid var(--line); color:var(--muted); font-size:13px; }
  footer .row { display:flex; justify-content:space-between; flex-wrap:wrap; gap:12px; padding:28px 0; }
  .demo-note { text-align:center; font-size:12px; color:var(--muted); padding-bottom:28px; }
  dialog { border:0; border-radius:16px; padding:32px; max-width:380px; text-align:center; box-shadow:0 20px 60px rgba(0,0,0,.3); }
  dialog::backdrop { background:rgba(15,17,21,.5); }
  @media (prefers-color-scheme: dark) {
    :root { --fg:#e5e7eb; --bg:#0f1115; --soft:#161a22; --muted:#9ca3af; --line:#262b36; --tag:#312e81; --tag-fg:#c7d2fe; }
    .nav { background:rgba(15,17,21,.8); }
    .hero { background:radial-gradient(1200px 400px at 80% -10%, #1a2140 0%, transparent 60%); }
    .feature .fico { background:linear-gradient(135deg,#1e2440,#241a40); }
  }
</style>
</head>
<body>

  <div class="nav">
    <div class="wrap row">
      <div class="brand">
        <svg width="26" height="26" viewBox="0 0 32 32" aria-hidden="true"><rect x="2" y="2" width="28" height="28" rx="8" fill="#2563eb"/><path d="M9 17.5l4.5 4.5L23 11" stroke="#fff" stroke-width="3" stroke-linecap="round" stroke-linejoin="round" fill="none"/></svg>
        {{サービス名}}
      </div>
      <nav class="links">
        <a href="#pains">課題</a><a href="#features">解決</a><a href="#how">使い方</a><a href="#pricing">料金</a>
      </nav>
      <button class="btn" onclick="thx.showModal()">{{CTA文言}}</button>
    </div>
  </div>

  <header class="hero">
    <div class="wrap grid">
      <div>
        <span class="eyebrow">{{対象顧客}}</span>
        <h1>{{価値提案の見出し（1〜2行）}}</h1>
        <p class="sub">{{サブコピー：誰の・どんな課題を・どう解決するか}}</p>
        <div class="actions">
          <button class="btn lg" onclick="thx.showModal()">{{CTA文言}}</button>
          <a class="btn lg ghost" href="#how">使い方を見る</a>
        </div>
        <p class="note">{{補足（例: クレジットカード不要）}}</p>
      </div>
      <div>
        <!-- ヒーローSVGは例。プロダクトのUIや価値が伝わる図に描き替える（外部画像は使わない） -->
        <svg class="art" viewBox="0 0 480 360" role="img" aria-label="{{プロダクトのイメージ}}">
          <defs><linearGradient id="g1" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#eef2ff"/><stop offset="1" stop-color="#faf5ff"/></linearGradient></defs>
          <rect x="20" y="24" width="440" height="312" rx="20" fill="url(#g1)"/>
          <rect x="52" y="56" width="376" height="248" rx="14" fill="#ffffff" stroke="#e5e7eb"/>
          <circle cx="72" cy="78" r="4" fill="#dc2626"/><circle cx="86" cy="78" r="4" fill="#d97706"/><circle cx="100" cy="78" r="4" fill="#16a34a"/>
          <text x="72" y="112" font-family="system-ui" font-size="13" font-weight="700" fill="#111827">{{画面タイトル}}</text>
          <rect x="72" y="128" width="230" height="12" rx="6" fill="#eef1f5"/><rect x="330" y="124" width="78" height="20" rx="10" fill="#16a34a"/><text x="369" y="139" font-family="system-ui" font-size="11" fill="#fff" text-anchor="middle">{{指標A}}</text>
          <rect x="72" y="164" width="196" height="12" rx="6" fill="#eef1f5"/><rect x="330" y="160" width="78" height="20" rx="10" fill="#d97706"/><text x="369" y="175" font-family="system-ui" font-size="11" fill="#fff" text-anchor="middle">{{指標B}}</text>
          <rect x="72" y="200" width="150" height="12" rx="6" fill="#eef1f5"/><rect x="330" y="196" width="78" height="20" rx="10" fill="#dc2626"/><text x="369" y="211" font-family="system-ui" font-size="11" fill="#fff" text-anchor="middle">{{指標C}}</text>
          <rect x="72" y="242" width="336" height="44" rx="10" fill="#f5f7fa" stroke="#e5e7eb"/>
          <text x="92" y="269" font-family="system-ui" font-size="12" fill="#374151">{{補足キャプション}}</text>
        </svg>
      </div>
    </div>
  </header>

  <div class="trust">
    <div class="wrap row">
      <span>✓ <b>{{要点1}}</b></span><span>✓ <b>{{要点2}}</b></span><span>✓ <b>{{要点3}}</b></span>
    </div>
  </div>

  <section class="block" id="pains">
    <div class="wrap center">
      <span class="kicker">Problem</span>
      <h2 class="sec">{{課題セクションの見出し}}</h2>
      <p class="lead">{{リード（検証済みの課題を含む等）}}</p>
    </div>
    <div class="wrap">
      <div class="pains">
        <!-- 検証済み(高確信)の課題仮説には <span class="tag">検証済み</span> を付ける。それ以外は付けない。 -->
        <div class="pain"><svg class="ico" width="26" height="26" viewBox="0 0 24 24" fill="none" stroke="#dc2626" stroke-width="2" stroke-linecap="round"><path d="M12 9v4M12 17h.01"/><path d="M10.3 3.9L2.4 18a2 2 0 0 0 1.7 3h15.8a2 2 0 0 0 1.7-3L13.7 3.9a2 2 0 0 0-3.4 0z"/></svg><div>{{ペイン1（課題仮説から）}}<span class="tag">検証済み</span></div></div>
        <div class="pain"><svg class="ico" width="26" height="26" viewBox="0 0 24 24" fill="none" stroke="#dc2626" stroke-width="2" stroke-linecap="round"><path d="M12 9v4M12 17h.01"/><path d="M10.3 3.9L2.4 18a2 2 0 0 0 1.7 3h15.8a2 2 0 0 0 1.7-3L13.7 3.9a2 2 0 0 0-3.4 0z"/></svg><div>{{ペイン2}}<span class="tag">検証済み</span></div></div>
        <div class="pain"><svg class="ico" width="26" height="26" viewBox="0 0 24 24" fill="none" stroke="#6b7280" stroke-width="2" stroke-linecap="round"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/></svg><div>{{ペイン3}}</div></div>
        <div class="pain"><svg class="ico" width="26" height="26" viewBox="0 0 24 24" fill="none" stroke="#6b7280" stroke-width="2" stroke-linecap="round"><circle cx="11" cy="11" r="7"/><path d="M21 21l-4.3-4.3"/></svg><div>{{ペイン4}}</div></div>
      </div>
    </div>
  </section>

  <section class="block" id="features" style="background:var(--soft);">
    <div class="wrap center">
      <span class="kicker">Solution</span>
      <h2 class="sec">{{解決セクションの見出し}}</h2>
      <p class="lead">{{リード（ソリューション仮説の核）}}</p>
    </div>
    <div class="wrap">
      <div class="features">
        <div class="feature"><div class="fico"><svg width="26" height="26" viewBox="0 0 24 24" fill="none" stroke="#2563eb" stroke-width="2" stroke-linecap="round"><path d="M10 13a5 5 0 0 0 7 0l3-3a5 5 0 0 0-7-7l-1 1"/><path d="M14 11a5 5 0 0 0-7 0l-3 3a5 5 0 0 0 7 7l1-1"/></svg></div><h3>{{特徴1見出し}}</h3><p>{{特徴1の説明（ソリューション仮説から）}}</p></div>
        <div class="feature"><div class="fico"><svg width="26" height="26" viewBox="0 0 24 24" fill="none" stroke="#7c3aed" stroke-width="2" stroke-linecap="round"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/><path d="M12 8v4M12 15h.01"/></svg></div><h3>{{特徴2見出し}}</h3><p>{{特徴2の説明}}</p></div>
        <div class="feature"><div class="fico"><svg width="26" height="26" viewBox="0 0 24 24" fill="none" stroke="#2563eb" stroke-width="2" stroke-linecap="round"><circle cx="12" cy="12" r="9"/><path d="M15.5 8.5l-2 5-5 2 2-5z" fill="#2563eb" stroke="none"/></svg></div><h3>{{特徴3見出し}}</h3><p>{{特徴3の説明}}</p></div>
      </div>
    </div>
  </section>

  <section class="block" id="how">
    <div class="wrap center"><span class="kicker">How it works</span><h2 class="sec">{{使い方の見出し（例: 3ステップで回る）}}</h2></div>
    <div class="wrap">
      <div class="steps">
        <div class="step"><div class="num">1</div><h3>{{ステップ1}}</h3><p>{{ステップ1の説明}}</p></div>
        <div class="step"><div class="num">2</div><h3>{{ステップ2}}</h3><p>{{ステップ2の説明}}</p></div>
        <div class="step"><div class="num">3</div><h3>{{ステップ3}}</h3><p>{{ステップ3の説明}}</p></div>
      </div>
    </div>
  </section>

  <!-- 声（Voices）: 実在の証言を装わない。必ず「デモ用ダミー」と明示。不要なら節ごと削除してよい。 -->
  <section class="block" style="background:var(--soft);">
    <div class="wrap center"><span class="kicker">Voices</span><h2 class="sec">現場の声（イメージ）</h2><p class="lead">＊デモ用のダミーです（実在の利用者の声ではありません）。</p></div>
    <div class="wrap">
      <div class="quotes">
        <div class="quote"><p>「{{想定される好意的な声1}}」</p><div class="who"><div class="avatar"></div><div><div class="n">{{肩書き}}（ダミー）</div><div class="r">{{属性}}</div></div></div></div>
        <div class="quote"><p>「{{想定される好意的な声2}}」</p><div class="who"><div class="avatar"></div><div><div class="n">{{肩書き}}（ダミー）</div><div class="r">{{属性}}</div></div></div></div>
      </div>
    </div>
  </section>

  <!-- 料金（Pricing）: 確定価格を装わない。必ず「仮の表示」と明示。不要なら節ごと削除してよい。 -->
  <section class="block" id="pricing">
    <div class="wrap center"><span class="kicker">Pricing</span><h2 class="sec">シンプルな料金（デモ）</h2><p class="lead">＊金額はプロトタイプ検証用の仮の表示です。</p></div>
    <div class="wrap">
      <div class="plans">
        <div class="plan"><h3>{{プラン1名}}</h3><div class="price">{{価格1}}<small>{{単位}}</small></div><ul><li>{{特典}}</li><li>{{特典}}</li></ul><button class="btn ghost" style="width:100%;" onclick="thx.showModal()">{{CTA}}</button></div>
        <div class="plan pop"><h3>{{プラン2名}}</h3><div class="price">{{価格2}}<small>{{単位}}</small></div><ul><li>{{特典}}</li><li>{{特典}}</li><li>{{特典}}</li></ul><button class="btn" style="width:100%;" onclick="thx.showModal()">{{CTA文言}}</button></div>
        <div class="plan"><h3>{{プラン3名}}</h3><div class="price">{{価格3}}</div><ul><li>{{特典}}</li><li>{{特典}}</li></ul><button class="btn ghost" style="width:100%;" onclick="thx.showModal()">{{CTA}}</button></div>
      </div>
    </div>
  </section>

  <div class="cta-band">
    <h2>{{最終CTAの見出し}}</h2>
    <p>{{最終CTAの一言}}</p>
    <button class="btn lg" onclick="thx.showModal()">{{CTA文言}}</button>
  </div>

  <footer>
    <div class="wrap row">
      <div class="brand"><svg width="20" height="20" viewBox="0 0 32 32" aria-hidden="true"><rect x="2" y="2" width="28" height="28" rx="8" fill="#2563eb"/><path d="M9 17.5l4.5 4.5L23 11" stroke="#fff" stroke-width="3" stroke-linecap="round" stroke-linejoin="round" fill="none"/></svg> {{サービス名}}</div>
      <span>© {{年}} {{サービス名}}（検証用プロトタイプ）</span>
    </div>
    <div class="demo-note">これは検証用プロトタイプであり、実サービス・実在の企業/利用者・確定した価格を表すものではありません。</div>
  </footer>

  <dialog id="thx">
    <div style="font-size:40px;">🎉</div>
    <p style="margin-top:8px;font-weight:700;">ありがとうございます！</p>
    <p style="color:var(--muted);font-size:14px;margin-top:6px;">これは検証用モックです。実際の登録・課金は行われません。</p>
    <button class="btn" style="margin-top:20px;" onclick="thx.close()">閉じる</button>
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
- 生成HTMLは外部依存ゼロで `file://` から開けること。過剰装飾しない。イメージ図はインラインSVGで描く（外部画像・CDNを使わない）。
- **証言・ロゴ・料金を"本物"に見せない**。声（testimonial）や導入企業ロゴ、確定価格は実在を装わず、必ず「デモ用ダミー」「仮の表示」と明示する。フッターに検証用プロトタイプである旨を残す。実在の人物・企業・レビューを捏造しない。
- プロトタイプHTMLは `/view` の自動集計対象外（レコードから乖離しうる生成物）。
