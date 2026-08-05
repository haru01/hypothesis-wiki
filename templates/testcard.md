---
id: <PREFIX>-TEST-NNN        # ファイル名と一致させる（接頭辞つき。例 SELF-TEST-001）
title: 短いタイトル
type: interview | demo | survey | mvp-test | desk-research | self-reflection
date: YYYY-MM-DD
stage: CPF | FPF | PSF | SPF | PMF
hypotheses: [<PREFIX>-H-NNN]   # 接頭辞つきで書く（例 [SELF-H-001]）。この実験が検証する仮説
riskiest-assumption: 最もリスクの高い前提を一文で（この実験で崩れたら全体が崩れる一点）
data: real | simulated   # 必須。この実験が「何のデータで作られるか」（架空判定の正本。real=実観測 / simulated=生成データ）
# 成功基準の機械可読な背骨（省略可・下の「成功基準」節の散文と二重表現）。検証前に確定し、
# 実施後は riskiest-assumption と同格で凍結される。学び(LEARN)の measurements と metric 名で
# 突き合わせ、実測と真逆の判定を lint が弾く＝ゴールポストの事後移動を数値で止める。
# op の語彙は ontology.md「成功基準の演算子」。of は母数（「5名中3名」の5）。
success-criteria:
  - {hypothesis: <PREFIX>-H-NNN, metric: 指標名, op: ">=", threshold: 3, of: 5}
---

# 短いタイトル

対象仮説: [[H-NNN]]
スクリプト・プロトタイプへのリンクもここ（`## テストカード` の手前）に置く。

<!-- TEST ＝ テストカード（実験計画）。検証前に記入する。
     学び(LEARN)を紐づけるまでは自由に直してよい（実施前に計画を練り直す機会はよくある）。
     紐づけた後に凍結されるのは「成功基準」節と frontmatter riskiest-assumption だけで、
     目的・方法・指標の補正・リンク追加・誤字修正は後からでもよい（不変ルール6）。
     検証後の学び（学習カード）は別レコード LEARN として新規作成する。 -->

## テストカード（検証前に記入）

<!-- 各項目の下に段落・小箇条書き・表を自由に置いてよい。 -->

### 目的

この活動で何を明らかにしたいか（どの仮説のどこを検証するか）。

### 方法

具体的な検証方法（誰に・何を・どうやって）。スクリプトがあれば参照リンクを置く。

### 指標

何を測るか（観測する事実・数値・発言）。

### 成功基準

どうなれば仮説を支持／反証と判断するか。数えられる基準は frontmatter `success-criteria` にも同じものを
書く（散文はニュアンス、frontmatter は検算用の背骨。二重表現）。**実施後は凍結される**（後知恵バイアス防止。
凍結されるのはこの節と frontmatter `riskiest-assumption`・`success-criteria` だけ）。
**見出し名「成功基準」は機械が凍結範囲を特定する
目印なので変えない**（変えると不変チェックがテストカード全体比較にフォールバックし、目的・方法・指標の
補正までブロックされる）。
