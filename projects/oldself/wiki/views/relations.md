<!-- 生成物: gen_views.py relations による機械生成。手編集禁止。`python3 tools/gen_views.py relations` で再生成する。生成基準日: 2026-08-02（ステージ CPF） / ontology-version: 2 -->
<!-- ⚠️ 架空/シミュレーションデータを含む活動: [[OLDSELF-LEARN-002]] [[OLDSELF-LEARN-003]] [[OLDSELF-LEARN-004]] [[OLDSELF-LEARN-006]] [[OLDSELF-TEST-002]] [[OLDSELF-TEST-003]] [[OLDSELF-TEST-004]]。これら由来の確信度・判断は実データ未検証。 -->

# 関係グラフ（oldself）

レコード間の型付きリンク（オントロジーの関係）を frontmatter から射影する。ノード=レコード、矢印=関係（ラベル=関係名）。関係の定義は [ontology.md](../../../../ontology.md) を参照。

## 型付き関係グラフ

```mermaid
flowchart LR
    subgraph H["仮説 H"]
      OLDSELF_H_001["H-001 検証を反復<br/>確信度4 🔄検証中"]
      OLDSELF_H_002["H-002 学びが散在<br/>確信度4 🔄検証中"]
      OLDSELF_H_003["H-003 報告駆動更新<br/>確信度3 🔄検証中"]
      OLDSELF_H_004["H-004★ 記録が残らない<br/>確信度4 🔄検証中"]
      OLDSELF_H_005["H-005 確証バイアス<br/>確信度4 🔄検証中"]
      OLDSELF_H_006["H-006 偽の確証<br/>確信度4 🔄検証中"]
      OLDSELF_H_007["H-007 反証不能な仮説<br/>確信度4 🔄検証中"]
      OLDSELF_H_008["H-008 説明できず停滞<br/>確信度4 🔄検証中"]
      OLDSELF_H_009["H-009 AI支援+記録+レポート<br/>確信度2 ❌反証"]
      OLDSELF_H_010["H-010 対価/乗り換え<br/>確信度2 ❌反証"]
    end
    subgraph TEST["実験計画 TEST"]
      OLDSELF_TEST_002["TEST-002 問題インタビュー5名（シミュレーション）"]
      OLDSELF_TEST_003["TEST-003 核心クラスタの反証テスト10名（シミュレ…"]
      OLDSELF_TEST_004["TEST-004 確信度WikiのLP提示インタビュー（シ…"]
      OLDSELF_TEST_006["TEST-006 実データでの問題インタビュー（核心クラス…"]
    end
    subgraph LEARN["学び LEARN"]
      OLDSELF_LEARN_001["LEARN-001 企業の仮説検証の状況・課題のデスクリサー…"]
      OLDSELF_LEARN_002["LEARN-002 問題インタビュー5名（シミュレーション）"]
      OLDSELF_LEARN_003["LEARN-003 核心クラスタの反証テスト10名（シミュレ…"]
      OLDSELF_LEARN_004["LEARN-004 確信度WikiのLP提示インタビュー（シ…"]
      OLDSELF_LEARN_005["LEARN-005 核心クラスタと移行判断への揺さぶり監査（…"]
      OLDSELF_LEARN_006["LEARN-006 出典突き合わせによる記録の是正（表層形の…"]
      OLDSELF_LEARN_007["LEARN-007 引き下げ後に残った「6」への揺さぶり監査…"]
    end
    subgraph DEC["意思決定 DEC"]
      OLDSELF_DEC_001["DEC-001 CPF→FPF ステージ移行"]
      OLDSELF_DEC_002["DEC-002 FPF→CPF 巻き戻し（架空依存の偽「…"]
    end
    OLDSELF_H_001 -->|因果先| OLDSELF_H_004
    OLDSELF_H_001 -->|因果先| OLDSELF_H_006
    OLDSELF_H_002 -->|派生元| OLDSELF_H_001
    OLDSELF_H_002 -->|因果先| OLDSELF_H_004
    OLDSELF_H_002 -->|因果先| OLDSELF_H_009
    OLDSELF_H_003 -->|派生元| OLDSELF_H_001
    OLDSELF_H_003 -->|因果先| OLDSELF_H_008
    OLDSELF_H_004 -->|因果先| OLDSELF_H_008
    OLDSELF_H_004 -->|因果先| OLDSELF_H_009
    OLDSELF_H_006 -->|因果先| OLDSELF_H_009
    OLDSELF_H_008 -->|派生元| OLDSELF_H_004
    OLDSELF_H_008 -->|因果先| OLDSELF_H_009
    OLDSELF_H_009 -->|派生元| OLDSELF_H_004
    OLDSELF_H_009 -->|因果先| OLDSELF_H_010
    OLDSELF_H_009 -->|対応課題| OLDSELF_H_004
    OLDSELF_H_009 -->|対応課題| OLDSELF_H_006
    OLDSELF_H_009 -->|対応課題| OLDSELF_H_008
    OLDSELF_H_010 -->|派生元| OLDSELF_H_009
    OLDSELF_TEST_002 -->|検証対象| OLDSELF_H_001
    OLDSELF_TEST_002 -->|検証対象| OLDSELF_H_002
    OLDSELF_TEST_002 -->|検証対象| OLDSELF_H_003
    OLDSELF_TEST_002 -->|検証対象| OLDSELF_H_004
    OLDSELF_TEST_002 -->|検証対象| OLDSELF_H_005
    OLDSELF_TEST_002 -->|検証対象| OLDSELF_H_006
    OLDSELF_TEST_002 -->|検証対象| OLDSELF_H_007
    OLDSELF_TEST_002 -->|検証対象| OLDSELF_H_008
    OLDSELF_TEST_003 -->|検証対象| OLDSELF_H_004
    OLDSELF_TEST_003 -->|検証対象| OLDSELF_H_002
    OLDSELF_TEST_003 -->|検証対象| OLDSELF_H_006
    OLDSELF_TEST_003 -->|検証対象| OLDSELF_H_008
    OLDSELF_TEST_003 -->|検証対象| OLDSELF_H_001
    OLDSELF_TEST_004 -->|検証対象| OLDSELF_H_009
    OLDSELF_TEST_004 -->|検証対象| OLDSELF_H_010
    OLDSELF_TEST_006 -->|検証対象| OLDSELF_H_001
    OLDSELF_TEST_006 -->|検証対象| OLDSELF_H_002
    OLDSELF_TEST_006 -->|検証対象| OLDSELF_H_003
    OLDSELF_TEST_006 -->|検証対象| OLDSELF_H_004
    OLDSELF_TEST_006 -->|検証対象| OLDSELF_H_006
    OLDSELF_TEST_006 -->|検証対象| OLDSELF_H_008
    OLDSELF_LEARN_001 -->|検証対象| OLDSELF_H_001
    OLDSELF_LEARN_001 -->|検証対象| OLDSELF_H_002
    OLDSELF_LEARN_001 -->|検証対象| OLDSELF_H_003
    OLDSELF_LEARN_001 -->|検証対象| OLDSELF_H_004
    OLDSELF_LEARN_001 -->|検証対象| OLDSELF_H_005
    OLDSELF_LEARN_001 -->|検証対象| OLDSELF_H_006
    OLDSELF_LEARN_001 -->|検証対象| OLDSELF_H_007
    OLDSELF_LEARN_001 -->|検証対象| OLDSELF_H_008
    OLDSELF_LEARN_002 -->|検証対象| OLDSELF_H_001
    OLDSELF_LEARN_002 -->|検証対象| OLDSELF_H_002
    OLDSELF_LEARN_002 -->|検証対象| OLDSELF_H_003
    OLDSELF_LEARN_002 -->|検証対象| OLDSELF_H_004
    OLDSELF_LEARN_002 -->|検証対象| OLDSELF_H_005
    OLDSELF_LEARN_002 -->|検証対象| OLDSELF_H_006
    OLDSELF_LEARN_002 -->|検証対象| OLDSELF_H_007
    OLDSELF_LEARN_002 -->|検証対象| OLDSELF_H_008
    OLDSELF_LEARN_002 -->|実験計画| OLDSELF_TEST_002
    OLDSELF_LEARN_003 -->|検証対象| OLDSELF_H_004
    OLDSELF_LEARN_003 -->|検証対象| OLDSELF_H_002
    OLDSELF_LEARN_003 -->|検証対象| OLDSELF_H_006
    OLDSELF_LEARN_003 -->|検証対象| OLDSELF_H_008
    OLDSELF_LEARN_003 -->|検証対象| OLDSELF_H_001
    OLDSELF_LEARN_003 -->|実験計画| OLDSELF_TEST_003
    OLDSELF_LEARN_004 -->|検証対象| OLDSELF_H_009
    OLDSELF_LEARN_004 -->|検証対象| OLDSELF_H_010
    OLDSELF_LEARN_004 -->|実験計画| OLDSELF_TEST_004
    OLDSELF_LEARN_005 -->|検証対象| OLDSELF_H_001
    OLDSELF_LEARN_005 -->|検証対象| OLDSELF_H_002
    OLDSELF_LEARN_005 -->|検証対象| OLDSELF_H_004
    OLDSELF_LEARN_005 -->|検証対象| OLDSELF_H_006
    OLDSELF_LEARN_005 -->|検証対象| OLDSELF_H_008
    OLDSELF_LEARN_006 -->|検証対象| OLDSELF_H_004
    OLDSELF_LEARN_006 -->|検証対象| OLDSELF_H_008
    OLDSELF_LEARN_006 -->|検証対象| OLDSELF_H_009
    OLDSELF_LEARN_006 -->|検証対象| OLDSELF_H_010
    OLDSELF_LEARN_007 -->|検証対象| OLDSELF_H_001
    OLDSELF_LEARN_007 -->|検証対象| OLDSELF_H_002
    OLDSELF_LEARN_007 -->|検証対象| OLDSELF_H_003
    OLDSELF_LEARN_007 -->|検証対象| OLDSELF_H_004
    OLDSELF_LEARN_007 -->|検証対象| OLDSELF_H_006
    OLDSELF_LEARN_007 -->|検証対象| OLDSELF_H_008
    OLDSELF_DEC_001 -->|根拠活動| OLDSELF_LEARN_002
    OLDSELF_DEC_001 -->|根拠活動| OLDSELF_LEARN_003
    OLDSELF_DEC_002 -->|根拠活動| OLDSELF_LEARN_005
```

## 関係インデックス

### 派生元（`derived-from`: H→H）

| 始点 | 関係 | 終点 |
|---|---|---|
| [[OLDSELF-H-002]] | 派生元 → | [[OLDSELF-H-001]] |
| [[OLDSELF-H-003]] | 派生元 → | [[OLDSELF-H-001]] |
| [[OLDSELF-H-008]] | 派生元 → | [[OLDSELF-H-004]] |
| [[OLDSELF-H-009]] | 派生元 → | [[OLDSELF-H-004]] |
| [[OLDSELF-H-010]] | 派生元 → | [[OLDSELF-H-009]] |

### 因果先（`leads-to`: H→H）

| 始点 | 関係 | 終点 |
|---|---|---|
| [[OLDSELF-H-001]] | 因果先 → | [[OLDSELF-H-004]] |
| [[OLDSELF-H-001]] | 因果先 → | [[OLDSELF-H-006]] |
| [[OLDSELF-H-002]] | 因果先 → | [[OLDSELF-H-004]] |
| [[OLDSELF-H-002]] | 因果先 → | [[OLDSELF-H-009]] |
| [[OLDSELF-H-003]] | 因果先 → | [[OLDSELF-H-008]] |
| [[OLDSELF-H-004]] | 因果先 → | [[OLDSELF-H-008]] |
| [[OLDSELF-H-004]] | 因果先 → | [[OLDSELF-H-009]] |
| [[OLDSELF-H-006]] | 因果先 → | [[OLDSELF-H-009]] |
| [[OLDSELF-H-008]] | 因果先 → | [[OLDSELF-H-009]] |
| [[OLDSELF-H-009]] | 因果先 → | [[OLDSELF-H-010]] |

### 対応課題（`addresses`: H→H）

| 始点 | 関係 | 終点 |
|---|---|---|
| [[OLDSELF-H-009]] | 対応課題 → | [[OLDSELF-H-004]] |
| [[OLDSELF-H-009]] | 対応課題 → | [[OLDSELF-H-006]] |
| [[OLDSELF-H-009]] | 対応課題 → | [[OLDSELF-H-008]] |

### 検証対象（`hypotheses`: LEARN/TEST→H）

| 始点 | 関係 | 終点 |
|---|---|---|
| [[OLDSELF-TEST-002]] | 検証対象 → | [[OLDSELF-H-001]] |
| [[OLDSELF-TEST-002]] | 検証対象 → | [[OLDSELF-H-002]] |
| [[OLDSELF-TEST-002]] | 検証対象 → | [[OLDSELF-H-003]] |
| [[OLDSELF-TEST-002]] | 検証対象 → | [[OLDSELF-H-004]] |
| [[OLDSELF-TEST-002]] | 検証対象 → | [[OLDSELF-H-005]] |
| [[OLDSELF-TEST-002]] | 検証対象 → | [[OLDSELF-H-006]] |
| [[OLDSELF-TEST-002]] | 検証対象 → | [[OLDSELF-H-007]] |
| [[OLDSELF-TEST-002]] | 検証対象 → | [[OLDSELF-H-008]] |
| [[OLDSELF-TEST-003]] | 検証対象 → | [[OLDSELF-H-004]] |
| [[OLDSELF-TEST-003]] | 検証対象 → | [[OLDSELF-H-002]] |
| [[OLDSELF-TEST-003]] | 検証対象 → | [[OLDSELF-H-006]] |
| [[OLDSELF-TEST-003]] | 検証対象 → | [[OLDSELF-H-008]] |
| [[OLDSELF-TEST-003]] | 検証対象 → | [[OLDSELF-H-001]] |
| [[OLDSELF-TEST-004]] | 検証対象 → | [[OLDSELF-H-009]] |
| [[OLDSELF-TEST-004]] | 検証対象 → | [[OLDSELF-H-010]] |
| [[OLDSELF-TEST-006]] | 検証対象 → | [[OLDSELF-H-001]] |
| [[OLDSELF-TEST-006]] | 検証対象 → | [[OLDSELF-H-002]] |
| [[OLDSELF-TEST-006]] | 検証対象 → | [[OLDSELF-H-003]] |
| [[OLDSELF-TEST-006]] | 検証対象 → | [[OLDSELF-H-004]] |
| [[OLDSELF-TEST-006]] | 検証対象 → | [[OLDSELF-H-006]] |
| [[OLDSELF-TEST-006]] | 検証対象 → | [[OLDSELF-H-008]] |
| [[OLDSELF-LEARN-001]] | 検証対象 → | [[OLDSELF-H-001]] |
| [[OLDSELF-LEARN-001]] | 検証対象 → | [[OLDSELF-H-002]] |
| [[OLDSELF-LEARN-001]] | 検証対象 → | [[OLDSELF-H-003]] |
| [[OLDSELF-LEARN-001]] | 検証対象 → | [[OLDSELF-H-004]] |
| [[OLDSELF-LEARN-001]] | 検証対象 → | [[OLDSELF-H-005]] |
| [[OLDSELF-LEARN-001]] | 検証対象 → | [[OLDSELF-H-006]] |
| [[OLDSELF-LEARN-001]] | 検証対象 → | [[OLDSELF-H-007]] |
| [[OLDSELF-LEARN-001]] | 検証対象 → | [[OLDSELF-H-008]] |
| [[OLDSELF-LEARN-002]] | 検証対象 → | [[OLDSELF-H-001]] |
| [[OLDSELF-LEARN-002]] | 検証対象 → | [[OLDSELF-H-002]] |
| [[OLDSELF-LEARN-002]] | 検証対象 → | [[OLDSELF-H-003]] |
| [[OLDSELF-LEARN-002]] | 検証対象 → | [[OLDSELF-H-004]] |
| [[OLDSELF-LEARN-002]] | 検証対象 → | [[OLDSELF-H-005]] |
| [[OLDSELF-LEARN-002]] | 検証対象 → | [[OLDSELF-H-006]] |
| [[OLDSELF-LEARN-002]] | 検証対象 → | [[OLDSELF-H-007]] |
| [[OLDSELF-LEARN-002]] | 検証対象 → | [[OLDSELF-H-008]] |
| [[OLDSELF-LEARN-003]] | 検証対象 → | [[OLDSELF-H-004]] |
| [[OLDSELF-LEARN-003]] | 検証対象 → | [[OLDSELF-H-002]] |
| [[OLDSELF-LEARN-003]] | 検証対象 → | [[OLDSELF-H-006]] |
| [[OLDSELF-LEARN-003]] | 検証対象 → | [[OLDSELF-H-008]] |
| [[OLDSELF-LEARN-003]] | 検証対象 → | [[OLDSELF-H-001]] |
| [[OLDSELF-LEARN-004]] | 検証対象 → | [[OLDSELF-H-009]] |
| [[OLDSELF-LEARN-004]] | 検証対象 → | [[OLDSELF-H-010]] |
| [[OLDSELF-LEARN-005]] | 検証対象 → | [[OLDSELF-H-001]] |
| [[OLDSELF-LEARN-005]] | 検証対象 → | [[OLDSELF-H-002]] |
| [[OLDSELF-LEARN-005]] | 検証対象 → | [[OLDSELF-H-004]] |
| [[OLDSELF-LEARN-005]] | 検証対象 → | [[OLDSELF-H-006]] |
| [[OLDSELF-LEARN-005]] | 検証対象 → | [[OLDSELF-H-008]] |
| [[OLDSELF-LEARN-006]] | 検証対象 → | [[OLDSELF-H-004]] |
| [[OLDSELF-LEARN-006]] | 検証対象 → | [[OLDSELF-H-008]] |
| [[OLDSELF-LEARN-006]] | 検証対象 → | [[OLDSELF-H-009]] |
| [[OLDSELF-LEARN-006]] | 検証対象 → | [[OLDSELF-H-010]] |
| [[OLDSELF-LEARN-007]] | 検証対象 → | [[OLDSELF-H-001]] |
| [[OLDSELF-LEARN-007]] | 検証対象 → | [[OLDSELF-H-002]] |
| [[OLDSELF-LEARN-007]] | 検証対象 → | [[OLDSELF-H-003]] |
| [[OLDSELF-LEARN-007]] | 検証対象 → | [[OLDSELF-H-004]] |
| [[OLDSELF-LEARN-007]] | 検証対象 → | [[OLDSELF-H-006]] |
| [[OLDSELF-LEARN-007]] | 検証対象 → | [[OLDSELF-H-008]] |

### 実験計画（`learns-from`: LEARN→TEST）

| 始点 | 関係 | 終点 |
|---|---|---|
| [[OLDSELF-LEARN-002]] | 実験計画 → | [[OLDSELF-TEST-002]] |
| [[OLDSELF-LEARN-003]] | 実験計画 → | [[OLDSELF-TEST-003]] |
| [[OLDSELF-LEARN-004]] | 実験計画 → | [[OLDSELF-TEST-004]] |

### 根拠活動（`based-on`: DEC→LEARN/TEST）

| 始点 | 関係 | 終点 |
|---|---|---|
| [[OLDSELF-DEC-001]] | 根拠活動 → | [[OLDSELF-LEARN-002]] |
| [[OLDSELF-DEC-001]] | 根拠活動 → | [[OLDSELF-LEARN-003]] |
| [[OLDSELF-DEC-002]] | 根拠活動 → | [[OLDSELF-LEARN-005]] |

## バックリンク索引（誰から・どの関係で参照されているか）

- [[OLDSELF-H-001]] ← 派生先: [[OLDSELF-H-002]] [[OLDSELF-H-003]] ／ 検証活動: [[OLDSELF-TEST-002]] [[OLDSELF-TEST-003]] [[OLDSELF-TEST-006]] [[OLDSELF-LEARN-001]] [[OLDSELF-LEARN-002]] [[OLDSELF-LEARN-003]] [[OLDSELF-LEARN-005]] [[OLDSELF-LEARN-007]]
- [[OLDSELF-H-002]] ← 検証活動: [[OLDSELF-TEST-002]] [[OLDSELF-TEST-003]] [[OLDSELF-TEST-006]] [[OLDSELF-LEARN-001]] [[OLDSELF-LEARN-002]] [[OLDSELF-LEARN-003]] [[OLDSELF-LEARN-005]] [[OLDSELF-LEARN-007]]
- [[OLDSELF-H-003]] ← 検証活動: [[OLDSELF-TEST-002]] [[OLDSELF-TEST-006]] [[OLDSELF-LEARN-001]] [[OLDSELF-LEARN-002]] [[OLDSELF-LEARN-007]]
- [[OLDSELF-H-004]] ← 因果元: [[OLDSELF-H-001]] [[OLDSELF-H-002]] ／ 派生先: [[OLDSELF-H-008]] [[OLDSELF-H-009]] ／ 対応する価値: [[OLDSELF-H-009]] ／ 検証活動: [[OLDSELF-TEST-002]] [[OLDSELF-TEST-003]] [[OLDSELF-TEST-006]] [[OLDSELF-LEARN-001]] [[OLDSELF-LEARN-002]] [[OLDSELF-LEARN-003]] [[OLDSELF-LEARN-005]] [[OLDSELF-LEARN-006]] [[OLDSELF-LEARN-007]]
- [[OLDSELF-H-005]] ← 検証活動: [[OLDSELF-TEST-002]] [[OLDSELF-LEARN-001]] [[OLDSELF-LEARN-002]]
- [[OLDSELF-H-006]] ← 因果元: [[OLDSELF-H-001]] ／ 対応する価値: [[OLDSELF-H-009]] ／ 検証活動: [[OLDSELF-TEST-002]] [[OLDSELF-TEST-003]] [[OLDSELF-TEST-006]] [[OLDSELF-LEARN-001]] [[OLDSELF-LEARN-002]] [[OLDSELF-LEARN-003]] [[OLDSELF-LEARN-005]] [[OLDSELF-LEARN-007]]
- [[OLDSELF-H-007]] ← 検証活動: [[OLDSELF-TEST-002]] [[OLDSELF-LEARN-001]] [[OLDSELF-LEARN-002]]
- [[OLDSELF-H-008]] ← 因果元: [[OLDSELF-H-003]] [[OLDSELF-H-004]] ／ 対応する価値: [[OLDSELF-H-009]] ／ 検証活動: [[OLDSELF-TEST-002]] [[OLDSELF-TEST-003]] [[OLDSELF-TEST-006]] [[OLDSELF-LEARN-001]] [[OLDSELF-LEARN-002]] [[OLDSELF-LEARN-003]] [[OLDSELF-LEARN-005]] [[OLDSELF-LEARN-006]] [[OLDSELF-LEARN-007]]
- [[OLDSELF-H-009]] ← 因果元: [[OLDSELF-H-002]] [[OLDSELF-H-004]] [[OLDSELF-H-006]] [[OLDSELF-H-008]] ／ 派生先: [[OLDSELF-H-010]] ／ 検証活動: [[OLDSELF-TEST-004]] [[OLDSELF-LEARN-004]] [[OLDSELF-LEARN-006]]
- [[OLDSELF-H-010]] ← 因果元: [[OLDSELF-H-009]] ／ 検証活動: [[OLDSELF-TEST-004]] [[OLDSELF-LEARN-004]] [[OLDSELF-LEARN-006]]
- [[OLDSELF-LEARN-002]] ← 導いた判断: [[OLDSELF-DEC-001]]
- [[OLDSELF-LEARN-003]] ← 導いた判断: [[OLDSELF-DEC-001]]
- [[OLDSELF-LEARN-005]] ← 導いた判断: [[OLDSELF-DEC-002]]
- [[OLDSELF-TEST-002]] ← 学び: [[OLDSELF-LEARN-002]]
- [[OLDSELF-TEST-003]] ← 学び: [[OLDSELF-LEARN-003]]
- [[OLDSELF-TEST-004]] ← 学び: [[OLDSELF-LEARN-004]]

## 課題↔ソリューション フィット（addresses）

ソリューション仮説の `addresses`（対応課題）で突き合わせる。反証された価値は ⚠️反証 を付す（実質的な対応にならない）。

| 課題 | 対応する価値（ソリューション） |
|---|---|
| [[OLDSELF-H-004]] 記録が残らず散逸・属人化し過去の学びが忘れられる | [[OLDSELF-H-009]]⚠️反証 |
| [[OLDSELF-H-005]] 確証バイアスで反証を軽視し過大評価する | **空白** |
| [[OLDSELF-H-006]] 好意的反応を購買意向と取り違え偽の確証で前進する | [[OLDSELF-H-009]]⚠️反証 |
| [[OLDSELF-H-007]] 反証不能な曖昧仮説を成功基準なしで検証する | **空白** |
| [[OLDSELF-H-008]] 検証の根拠を経営層に説明できず合意形成が停滞する | [[OLDSELF-H-009]]⚠️反証 |

- **未カバーの課題**（対応する価値がない）: [[OLDSELF-H-005]] [[OLDSELF-H-007]]
- **実質未カバー**（反証された価値でしか対応されていない）: [[OLDSELF-H-004]] [[OLDSELF-H-006]] [[OLDSELF-H-008]]
- **課題なき解決**（addresses 先が無いソリューション仮説）: なし

## グラフ診断

グラフ全体の欠落・偏りを機械算出する（個別の辺の型検証は `/lint` の担当）。

- **規模**: ノード 23 ／ 辺 83 ／ **辺÷ノード = 3.61**（密（richly connected））
- **連結成分**: 1（最大成分 23 ノード）。単一成分＝全レコードが関係で繋がっている
- **孤立仮説**（どの関係も持たない）: なし
- **ハブ**（次数上位＝コーパスを束ねているレコード）: [[OLDSELF-H-004]](13) [[OLDSELF-H-001]](12) [[OLDSELF-H-008]](12) [[OLDSELF-H-002]](11) [[OLDSELF-H-006]](10)
- **下流依存度**（`leads-to` の推移閉包＝崩れると波及が大きい背骨）: [[OLDSELF-H-001]](5) [[OLDSELF-H-002]](4) [[OLDSELF-H-003]](3) [[OLDSELF-H-004]](3) [[OLDSELF-H-006]](2)
- **未取り込みの生データ**（どの学びの `sources` からも参照されていない）: なし
