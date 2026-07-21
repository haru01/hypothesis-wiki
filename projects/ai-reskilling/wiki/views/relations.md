<!-- 生成物: gen_views.py relations による機械生成。手編集禁止。`python3 tools/gen_views.py relations` で再生成する。生成基準日: 2026-07-21（ステージ CPF） -->
<!-- ⚠️ 架空/シミュレーションデータを含む活動: [[AIRE-ACT-004]]。これら由来の確信度・判断は実データ未検証。 -->

# 関係グラフ（ai-reskilling）

レコード間の型付きリンク（オントロジーの関係）を frontmatter から射影する。ノード=レコード、矢印=関係（ラベル=関係名）。関係の定義は [ontology.md](../../../../ontology.md) を参照。

## 型付き関係グラフ

```mermaid
flowchart LR
    subgraph H["仮説 H"]
      AIRE_H_001["H-001 専門外を丸投げ承認<br/>⚪未検証"]
      AIRE_H_002["H-002★ 累積ドリフト<br/>⚪未検証"]
      AIRE_H_003["H-003 目利き不足<br/>⚪未検証"]
    end
    subgraph ACT["活動 ACT"]
      AIRE_ACT_001["ACT-001 AI時代のリスキリング（2名＋専門エージ…"]
      AIRE_ACT_002["ACT-002 エージェント実務者への発見型インタビュー…"]
      AIRE_ACT_003["ACT-003 認知的降伏シナリオの反証インタビュー（2…"]
      AIRE_ACT_004["ACT-004 CPF仮説群への揺さぶり監査（ちゃぶ台返…"]
    end
    AIRE_H_001 -->|因果先| AIRE_H_002
    AIRE_H_001 -->|因果先| AIRE_H_003
    AIRE_ACT_001 -->|検証対象| AIRE_H_001
    AIRE_ACT_001 -->|検証対象| AIRE_H_002
    AIRE_ACT_001 -->|検証対象| AIRE_H_003
    AIRE_ACT_002 -->|検証対象| AIRE_H_001
    AIRE_ACT_002 -->|検証対象| AIRE_H_002
    AIRE_ACT_002 -->|検証対象| AIRE_H_003
    AIRE_ACT_003 -->|検証対象| AIRE_H_001
    AIRE_ACT_003 -->|検証対象| AIRE_H_002
    AIRE_ACT_003 -->|検証対象| AIRE_H_003
    AIRE_ACT_004 -->|検証対象| AIRE_H_001
    AIRE_ACT_004 -->|検証対象| AIRE_H_002
    AIRE_ACT_004 -->|検証対象| AIRE_H_003
```

## 関係インデックス

### 因果先（`leads-to`: H→H）

| 始点 | 関係 | 終点 |
|---|---|---|
| [[AIRE-H-001]] | 因果先 → | [[AIRE-H-002]] |
| [[AIRE-H-001]] | 因果先 → | [[AIRE-H-003]] |

### 検証対象（`hypotheses`: ACT→H）

| 始点 | 関係 | 終点 |
|---|---|---|
| [[AIRE-ACT-001]] | 検証対象 → | [[AIRE-H-001]] |
| [[AIRE-ACT-001]] | 検証対象 → | [[AIRE-H-002]] |
| [[AIRE-ACT-001]] | 検証対象 → | [[AIRE-H-003]] |
| [[AIRE-ACT-002]] | 検証対象 → | [[AIRE-H-001]] |
| [[AIRE-ACT-002]] | 検証対象 → | [[AIRE-H-002]] |
| [[AIRE-ACT-002]] | 検証対象 → | [[AIRE-H-003]] |
| [[AIRE-ACT-003]] | 検証対象 → | [[AIRE-H-001]] |
| [[AIRE-ACT-003]] | 検証対象 → | [[AIRE-H-002]] |
| [[AIRE-ACT-003]] | 検証対象 → | [[AIRE-H-003]] |
| [[AIRE-ACT-004]] | 検証対象 → | [[AIRE-H-001]] |
| [[AIRE-ACT-004]] | 検証対象 → | [[AIRE-H-002]] |
| [[AIRE-ACT-004]] | 検証対象 → | [[AIRE-H-003]] |

## バックリンク索引（誰から・どの関係で参照されているか）

- [[AIRE-H-001]] ← 検証活動: [[AIRE-ACT-001]] [[AIRE-ACT-002]] [[AIRE-ACT-003]] [[AIRE-ACT-004]]
- [[AIRE-H-002]] ← 因果元: [[AIRE-H-001]] ／ 検証活動: [[AIRE-ACT-001]] [[AIRE-ACT-002]] [[AIRE-ACT-003]] [[AIRE-ACT-004]]
- [[AIRE-H-003]] ← 因果元: [[AIRE-H-001]] ／ 検証活動: [[AIRE-ACT-001]] [[AIRE-ACT-002]] [[AIRE-ACT-003]] [[AIRE-ACT-004]]
