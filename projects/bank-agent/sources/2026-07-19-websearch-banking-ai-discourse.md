# WebSearch言説収集 — 銀行×AIエージェント（インタビュー代替の二次情報）

> **データ種別: 二次情報（WebSearchで収集した公開言説）。架空ではないが一次インタビューでもない。**
> 証拠の階梯では〈二次〉に相当し、この根拠での確信度上限は4（二次情報・状況証拠）とする。
> 実顧客の〈自認〉〈実コスト〉ではないため、確信度5以上には使わない。
> 収集日: 2026-07-19 ／ 方法: WebSearch 5クエリ。

---

## 対象 BANK-H-001（事務は手続き書＋複数システム＋人手ダブルチェックで処理）

- 金融庁「金融検査マニュアル（預金等受入金融機関）」: 市場部門と事務管理部門における取引データの突合・定期照合を要求。システムは中央集中型汎用機・分散系・EUC を含むと明記。出典: fsa.go.jp/manual/manualj/yokin.html, fsa.go.jp/manual/manualj/yokin.pdf
- フィンテックス「金融業務マニュアルが難しい理由」: 金融機関の手続きは商品・手続きの種類が極めて多く、本人確認・反社チェック・記録保存などのコンプラ要件が手続きごとに紐づく。マニュアルは部署ごと数百ページ、全社で2万〜10万ページ（A4換算）にのぼる。出典: fintecs.co.jp/academy/financial_industry_manual/
- 日本銀行金融機構局「オペレーショナルリスク管理の現状と高度化への課題」: 事務リスク管理における照合・突合・二重確認の実務。出典: boj.or.jp/finsys/c_aft/basic_seminar/data/rel120815a10.pdf
- Automation Anywhere「銀行による自動化の利用状況」: 銀行事務の手作業・複数システム横断が RPA 導入の主対象であることを前提に記述。出典: automationanywhere.com/jp/rpa/banking-automation

## 対象 BANK-H-002（規制対応・接続の壁でAIがPoC止まり）

- TechTarget「1800万円の損失から銀行が学んだAI本番運用の絶対条件」: 銀行のPoCが失敗に至った3原因＝①可観測性の欠如 ②評価の欠如 ③ガバナンスの欠如。出典: techtarget.itmedia.co.jp/tt/news/2606/22/news08.html
- 富士通「銀行DXの鍵は生成AI〜導入の課題と成功戦略」: PoC段階では限定環境で良い結果でも、全社展開でデータ連携・セキュリティ要件・既存業務フロー統合の課題が浮上し頓挫するケースが多い。出典: global.fujitsu/ja-jp/local/blog/article/2024-10-15-01
- サーバーワークス「生成AI導入におけるPoCとは／"検証止まり"にしないポイント」: PoC止まりの一般構造。出典: serverworks.co.jp/blog/ai/what_is_poc_for_implementing_generative_ai.html
- Labz「生成AIがPoC止まりで終わる理由｜ツール導入を中核プロセスへの組み込みに変える」: 「ツール導入」に留まり「中核プロセスへの組み込み」に至らない構造を指摘（本仮説＝業務ループへの組み込みと同型）。出典: labz-inc.com
- 全国銀行協会 金融庁AIフォーラム説明資料（2025-06-18）: 銀行界のAI活用の論点整理。出典: fsa.go.jp/singi/ai_forum/siryou/20250618/02.pdf

## 対象 BANK-H-003（誤り時の説明責任・是正フロー未設計で人手確認を外せない）

- 金融庁「AIディスカッションペーパー（第1.1版）2026-03」: 金融分野AIの健全な利活用の論点。説明可能性・責任所在。出典: fsa.go.jp/news/r7/sonota/20260303/aidp_version1.1.pdf
- PwC「金融庁AIディスカッションペーパー1.1版の概要と内部監査への示唆」: 経営陣がAIの設計・テスト・導入・監視・統制の監督責任を負い、結果を継続検証することが求められる。トラブル時の責任所在明確化・人間の最終責任者の明示・意思決定の記録と監査可能性の確保。出典: pwc.com/jp/ja/knowledge/column/ai-governance/ai-discussion-paper.html
- Acompany「金融機関がAI導入で直面する5つの課題」: 規制対応から現場定着までの課題。出典: service.acompany.tech/blog/ai-adoption/ai5_2.php
- 生成AIのブラックボックス性（「なぜその出力をしたか」を人間が完全に説明できない）が複数記事で共通指摘。

## 対象 BANK-H-004（個別ツール乱立で横展開できずコスト分散）

- エンジニアtype「メガバンクはいかにAI-Ready な組織へ変わるのか」: 三菱UFJ銀行が次期AI共通基盤に Databricks を採用。背景に、分析基盤が各所に点在する「サイロ化」。案件ごとにインフラ準備・権限調整・データ収集・環境構築をゼロから行い、分析開始まで膨大な時間。出典: type.jp/et/feature/31184/
- TWOSTONE&Sons「金融DXでサイロ化の課題を解消できる？」: 金融機関は縦割り組織が根強く、部門間連携不足・情報共有不備がDXを妨げる。出典: twostone-s.com/columns/dx/finance/374/
- 日本銀行「金融システムレポート別冊 金融機関における生成AIの利用状況とリスク管理」（2025-09）: 利用状況とリスク管理の横断的整理。出典: boj.or.jp/research/brp/fsr/fsrb250930.htm

## 補足（接続の壁の裏付け／BANK-H-002 に追加）

- FinBridge / The Finance / NEC: 勘定系の多くは1980年代の第3次オンライン期に作られ老朽化・ブラックボックス化。新技術との統合・改修が困難。出典: finbridge.jp/overview/overview-bank/overview-bankcore/, thefinance.jp/strategy/system_modernization
- NTTテクノクロス: 銀行APIは「プログラム開発が困難」「既存業務システムの改造が必要」「開発にコスト・期間・高度ノウハウ」。出典: ntt-tx.co.jp/products/bankinggate/apix/lp_202010.html
- EY「銀行が生成AIの力を活用するには」: 専門知識不足・コスト高騰・レガシーテクノロジーが短期的障壁。出典: ey.com/ja_jp/insights/banking-capital-markets/five-priorities-for-harnessing-the-power-of-gen-ai-in-banking
