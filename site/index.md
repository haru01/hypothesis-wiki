---
title: 仮説検証Wiki
description: 仮説検証活動（CPF→FPF→PSF→SPF→PMF）を通じて育てる LLM-wiki。仮説・実験計画・学び・意思決定を追記専用の出来事として積み、現在の確信度をその射影として導く。
---

# 仮説検証Wiki

仮説検証活動を通じて育てる LLM-wiki の公開ビュー。

「仮説を立てた → 実験計画を立てた → 実施して学びを得た → 意思決定した」を**追記専用の出来事**として
時系列に積み、いま何をどれだけ確かだと思っているか（確信度・ステータス）を**その射影**として導く。
レコードは作成後は原則書き換えず、更新より新規作成を選ぶ。

## プロジェクト

仮説検証は案件単位で分かれている。

### self — この Wiki 自身の仮説検証

Wiki というプロダクト自体を題材にした仮説検証。デスクリサーチで課題仮説の種を取り、
反証可能な仮説5件に起こして最初の検証計画を立てたところ（CPF・一次インタビューは未実施）。

- [[projects/self/wiki/index|仮説インデックス]] — 全仮説の現在の確信度・ステータス
- [[projects/self/wiki/views/board|ボード]] — 仮説・実験・学び・意思決定を1枚で
- [[projects/self/wiki/views/relations|関係グラフ]] — レコード間の型付きリンク
- [[projects/self/wiki/log|活動ログ]]

### oldself — 旧 self（凍結アーカイブ）

上の self の前身。CPF→FPF 移行 → LP 提示で反証 → 揺さぶり監査 → FPF→CPF 巻き戻し、まで一巡した記録。
サンプルとしては読み解きづらくなったため検証を止め、退避した（レコードIDの接頭辞は `OLDSELF-`）。

- [[projects/oldself/wiki/index|仮説インデックス]]
- [[projects/oldself/wiki/views/board|ボード]]
- [[projects/oldself/wiki/views/relations|関係グラフ]]
- [[projects/oldself/wiki/log|活動ログ]]

### ai-reskilling — AI時代のリスキリング

- [[projects/ai-reskilling/wiki/index|仮説インデックス]]
- [[projects/ai-reskilling/wiki/views/board|ボード]]
- [[projects/ai-reskilling/wiki/views/relations|関係グラフ]]
- [[projects/ai-reskilling/wiki/log|活動ログ]]

## 読み方

**確信度（1〜10）** は証拠の強さの目安で、**ステータス**（未検証／検証中／検証済み／反証）とは
別に管理する。「検証中なのに確信度 3-4」は異常ではなく、検証したが証拠が集まっていない
正当な状態（判断保留）を表す。

確信度を上げる根拠には序列がある（弱→強）: 〈発言〉＜〈自認〉＜〈実コスト〉＜〈行動〉＜〈支払い〉。
発言だけで確信度を上げない（interest ≠ intent）。架空・シミュレーションデータ由来の確信度は上限 8 で、
9-10 は実観測に限る。各仮説の確信度履歴テーブルが正本で、そこから学びレコードを辿れる。

型・関係・状態機械の定義は [[ontology|オントロジー]]、規約は [[CLAUDE|スキーマ]]、
各ステージの問いかけバンクと移行基準は [[cpf|CPF]]・[[fpf|FPF]]・[[psf|PSF]]・[[spf|SPF]]・[[pmf|PMF]] の
プレイブックにある。

> [!note] 生データは非公開
> 学びレコードが根拠として指す生データ（インタビュー録など）は `projects/<slug>/sources/` にあり、
> このサイトには含めていない。そのため確信度の根拠鎖 `確信度履歴 → 学び → 生データ` の
> **末端はここでは辿れない**。学びレコードの `sources` に、どの生データに基づくかは記録されている。

このサイトは [hypothesis-wiki](https://github.com/haru01/hypothesis-wiki) から生成している。
