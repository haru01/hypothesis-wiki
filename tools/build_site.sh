#!/usr/bin/env bash
# 公開サイト（GitHub Pages）を Quartz v5 でビルドする。
#
# Quartz はリポジトリに取り込まず、site/QUARTZ_REF でピン止めしたコミットを
# ビルド時に .site/quartz へ取ってくる。Node はこのスクリプトと CI の中にしか存在しない。
#
#   bash tools/build_site.sh            … ビルドして .site/quartz/public に出す
#   bash tools/build_site.sh --serve    … ローカルプレビュー（http://localhost:8080）
#   bash tools/build_site.sh --check    … ビルド後に壊れリンクを数え、0 でなければ非ゼロ終了
#   bash tools/build_site.sh --fresh    … Quartz を取り直してから実行する
#
# 出力（.site/）は生成物。手で直さず、レコード側を直して再生成する。
set -euo pipefail

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
WORK="$REPO/.site"
STAGED="$WORK/staged"
QUARTZ="$WORK/quartz"
QUARTZ_URL="https://github.com/jackyzha0/quartz.git"
BASE_URL="haru01.github.io/hypothesis-wiki"

SERVE=0 CHECK=0 FRESH=0
for arg in "$@"; do
  case "$arg" in
    --serve) SERVE=1 ;;
    --check) CHECK=1 ;;
    --fresh) FRESH=1 ;;
    *) echo "不明な引数: $arg" >&2; exit 2 ;;
  esac
done

# site/QUARTZ_REF はコメント行つき。最初の非コメント・非空行を SHA として読む。
SHA="$(grep -vE '^\s*(#|$)' "$REPO/site/QUARTZ_REF" | head -1 | tr -d '[:space:]')"
if [ -z "$SHA" ]; then
  echo "site/QUARTZ_REF から SHA を読めなかった" >&2
  exit 1
fi

# Quartz を取る前に、いま動いている Node のバージョンを捕まえておく。
# Quartz のリポジトリには開発用の `.node-version`（現在 v22.16.0）が入っており、
# nodenv/asdf を使っていると「その版が入っていない」と言って止まる。
# Quartz の要件は 22 以上なので、実行中の版で上書きしてしまってよい。
NODE_VER="$(node -v | sed 's/^v//')"
NODE_MAJOR="${NODE_VER%%.*}"
if [ "$NODE_MAJOR" -lt 22 ]; then
  echo "Quartz は Node 22 以上を要求する（いま v${NODE_VER}）" >&2
  exit 1
fi

# ---- 1. 公開ツリーを組み立てる ------------------------------------------------
echo "==> 公開ツリーを組み立てる"
python3 "$REPO/tools/gen_site.py" --out "$STAGED"

# ---- 2. Quartz を用意する（ピン止めした SHA。既にあれば再利用）--------------------
if [ "$FRESH" = 1 ]; then
  rm -rf "$QUARTZ"
fi
# セットアップ完了マーカー。SHA が一致するだけでは足りない——途中で失敗して
# node_modules や quartz.config.yaml が無いツリーを「再利用」してしまうため、
# 全工程を終えたときだけ印を書く。
SETUP_MARK="$QUARTZ/.hw-setup-done"
if [ "$(cat "$SETUP_MARK" 2>/dev/null || true)" = "$SHA" ]; then
  echo "==> Quartz は既に ${SHA}（再利用）"
else
  echo "==> Quartz $SHA を取得する"
  rm -rf "$QUARTZ"
  mkdir -p "$QUARTZ"
  git -C "$QUARTZ" init -q
  git -C "$QUARTZ" remote add origin "$QUARTZ_URL"
  # SHA 直指定の shallow fetch。拒否されたらブランチを浅く引いて checkout に落とす。
  if ! git -C "$QUARTZ" fetch -q --depth 1 origin "$SHA" 2>/dev/null; then
    echo "    （SHA 直指定の fetch が拒否された。v5 を浅く引いて checkout する）"
    git -C "$QUARTZ" fetch -q --depth 200 origin v5
  fi
  git -C "$QUARTZ" checkout -q "$SHA"

  echo "$NODE_VER" > "$QUARTZ/.node-version"   # 下の「毎回書く」と同じ理由

  echo "==> 依存をインストールする（Node v${NODE_VER}）"
  (cd "$QUARTZ" && npm ci)

  # content は空で作る（中身は staged を毎回入れ直すので create に運ばせない）。
  # obsidian テンプレートは wikilink・callout・mermaid を有効にし、
  # リンク解決を shortest に固定する。
  echo "==> Quartz を初期化する（obsidian テンプレート）"
  (cd "$QUARTZ" && npx quartz create --template obsidian --strategy new --baseUrl "$BASE_URL")

  echo "$SHA" > "$SETUP_MARK"
fi

# Quartz 同梱の .node-version（開発用に v22 系を指す）を実行中の版に差し替える。
# git checkout や create で戻ることがあるので、再利用時も含めて毎回書く。
echo "$NODE_VER" > "$QUARTZ/.node-version"

# ---- 3. コンテンツと設定を入れる ------------------------------------------------
echo "==> コンテンツと設定を入れる"
rm -rf "$QUARTZ/content"
cp -R "$STAGED" "$QUARTZ/content"
# `quartz create` は quartz.config.yaml を無条件に上書きするので、必ずこの順で。
cp "$REPO/site/quartz.config.yaml" "$QUARTZ/quartz.config.yaml"
(cd "$QUARTZ" && npx quartz plugin install --from-config)

# ---- 4. ビルド ---------------------------------------------------------------
if [ "$SERVE" = 1 ]; then
  echo "==> プレビュー: http://localhost:8080"
  (cd "$QUARTZ" && exec npx quartz build --serve)
fi

echo "==> ビルド"
(cd "$QUARTZ" && npx quartz build)

# Quartz は content 内の .html を**拡張子を落として**出す（index.html → index）が、
# 本文からのリンクはディレクトリ（.../self-test-004/）を指すので index.html が無いと 404 になり、
# 拡張子なしのままでは MIME も効かない（ブラウザがダウンロードしてしまう）。
# /building が生成する自己完結プロトタイプがこれに当たるので、実体を置き直す。
# 出力側のパスは Quartz が小文字化するのでそれに合わせる。
echo "==> HTML アセットを置き直す"
python3 - "$STAGED" "$QUARTZ/public" <<'PY'
import shutil, sys
from pathlib import Path
staged, public = Path(sys.argv[1]), Path(sys.argv[2])
n = 0
for src in sorted(staged.rglob("*.html")):
    rel = src.relative_to(staged)
    dest = public.joinpath(*[part.lower() for part in rel.parts])
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dest)
    n += 1
print(f"    {n} 件")
PY

echo "==> 出力: $QUARTZ/public"

# ---- 5. 壊れリンクのゲート -----------------------------------------------------
if [ "$CHECK" = 1 ]; then
  echo "==> 壊れリンクを数える"
  # disableBrokenWikilinks: true が、解決できなかった内部リンクに broken クラスを付ける。
  # 数えるのは「壊れたリンク数」であって「壊れたファイル数」ではない（-h -o を使う理由）。
  # 一致 0 件のとき grep は終了コード 1 を返す。それが成功の状態なので、
  # pipefail + set -e に殺されないよう明示的に飲む。
  count="$({ grep -rho 'class="[^"]*broken' "$QUARTZ/public" 2>/dev/null || true; } | wc -l | tr -d '[:space:]')"
  if [ "$count" != "0" ]; then
    echo "壊れた内部リンクが $count 件ある:" >&2
    grep -rn 'class="[^"]*broken' "$QUARTZ/public" | head -50 >&2
    exit 1
  fi
  echo "壊れた内部リンク: 0 件"
fi
