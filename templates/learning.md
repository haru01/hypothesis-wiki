---
id: <PREFIX>-LEARN-NNN      # ファイル名と一致させる（接頭辞つき。例 SELF-LEARN-001）
title: 短いタイトル
type: interview | demo | survey | mvp-test | desk-research | self-reflection
date: YYYY-MM-DD
stage: CPF | FPF | PSF | SPF | PMF
learns-from: <PREFIX>-TEST-NNN  # 省略可。実施した実験計画(TEST)。回顧型（desk-research/self-reflection 等）は持たない
hypotheses: [<PREFIX>-H-NNN]   # 接頭辞つき（例 [SELF-H-001]）。この学びが確信度を動かした仮説
outcome: 起票 | 支持 | 反証 | 判断保留 | 是正   # 検証の判定（board サマリへ射影。語彙の正本は ontology.md）
sources: [YYYY-MM-DD-....md]   # 根拠となった生データ（sources/ 基準の相対パス配列）。観測を伴う活動種別は必須
data: real | simulated   # 省略可。この学びが「何のデータで作られたか」（架空判定の正本。real=実観測 / simulated=生成データ）
---

# 短いタイトル

対象仮説: [[H-NNN]]
実験計画: [[<PREFIX>-TEST-NNN]]   <!-- 計画型のみ。回顧型はこの行を消す -->
生データ: [YYYY-MM-DD-....md](../../sources/YYYY-MM-DD-....md)   <!-- frontmatter sources と同じものを本文にも（二重表現）。回顧型で揺さぶり材料があればここに置く -->

<!-- LEARN ＝ 学習カード（検証後に新規作成する「実施して学びを得た」出来事）。
     テストカード（実験計画）は別レコード TEST にあり、こちらでは書き換えない。
     確信度・ステータスの更新は下の表で提案し、承認後に仮説(H)側の確信度履歴に1行追記する。
     sources（出典）は確信度の根拠鎖の末端: H の確信度履歴 → [[LEARN-NNN]] → sources/<生データ>。
     出典なしで確信度を上げると lint が provenance-chain で鳴る。
     生データ冒頭が架空/シミュレーション宣言なら、確信度は fictional-cap（上限8）を超えない。
     架空判定の正本は frontmatter の `data`。宣言を省くと出典冒頭の宣言・本文マーカー語による
     推論に戻り、架空データを「論じた」だけの学びが架空由来に誤分類されうる（明示するのが安全）。 -->

## 学習カード（検証後に記入）

### 学びの要点

この検証で分かった最も重要なこと1-2文（見出し的に鋭く）。board の結果行に射影される。事実の羅列でなく「何が言えたか」を書く。

### 事実（observed）

観測した事実だけを書く。解釈を混ぜない。発言は可能な限り原文で引用。

### 解釈（inference）

事実から何が言えるか。事実と明確に分けて書く。

### 驚き・想定外

予想と違ったこと、当初仮説になかった発見。

### 確信度の更新

| 仮説 | 更新前 | 更新後 | ステータス | 理由 |
|---|---|---|---|---|
| [[H-NNN]] | — | — | — | — |

### 次のアクション

- 次に検証すべきこと／作るべき仮説／立てるべきテストカード。
