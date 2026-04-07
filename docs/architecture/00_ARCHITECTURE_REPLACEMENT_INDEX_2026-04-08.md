# path: ./docs/architecture/00_ARCHITECTURE_REPLACEMENT_INDEX_2026-04-08.md
# desc: BTC-TS Architecture Replacement Index

更新日: 2026-04-08
位置づけ: `docs/architecture/` 再配置用の統合インデックス
対象: `btcts_next/src/btcts/` 現行 mainline

---

## 1. この文書の目的
この文書は、`docs/architecture/` 配下の仕様書群を、現行 repository の実体に合わせて再編・刷新するための入口である。

旧 `docs/architecture/` には有効な原則が多く残っている一方で、次の stale が混在している。

- `processing/l4_consumer_models/` が未展開である前提
- `tmp/tmp/...` など古い参照パス
- 「次フェーズで作る」前提のまま残った package skeleton 記述
- 2026-04-04〜2026-04-05 時点のドラフト状態を現在もそのまま説明している箇所

本刷新セットでは、古い設計メモを単純に残すのではなく、**現行コード構造・current handoff・current roadmap に同期した正本候補**を提示する。

---

## 2. 結論
`docs/architecture/` は、次の6文書へ再編するのを推奨する。

1. `00_ARCHITECTURE_REPLACEMENT_INDEX_2026-04-08.md`
2. `01_L1_L2_CAPTURE_CANONICAL_RUNTIME_SPEC_2026-04-08.md`
3. `02_L3_MARKET_SEMANTICS_AND_EVENT_CONTRACT_SPEC_2026-04-08.md`
4. `03_L4_SHARED_CONSUMER_MODELS_SPEC_2026-04-08.md`
5. `04_UI_HUB_OPERATOR_UI_SPEC_2026-04-08.md`
6. `05_SUPPORTING_POLICIES_AND_VERIFICATION_SPEC_2026-04-08.md`

必要であれば、削除対象整理用として次を補助文書として置く。

7. `06_DELETE_TARGETS_OLD_ARCHITECTURE_DOCS_2026-04-08.md`

---

## 3. 再編後の役割分担

### 3.1 `01_L1_L2_CAPTURE_CANONICAL_RUNTIME_SPEC_2026-04-08.md`
L1 と L2 をまとめて扱う。

理由:
- 現行 live runtime の主系は `collector_vnext/` であり、L1 と L2 の運転導線が密接
- stale になっていた「collector runtime / canonical ownership / runtime verification」を1本で読めるようにする方が再開性が高い

### 3.2 `02_L3_MARKET_SEMANTICS_AND_EVENT_CONTRACT_SPEC_2026-04-08.md`
L3 を単独で扱う。

理由:
- L3 は市場意味の唯一の owner であり、設計上もっとも重い境界
- current roadmap の先頭が event usage contract formalization であり、L3 の仕様更新が最重要

### 3.3 `03_L4_SHARED_CONSUMER_MODELS_SPEC_2026-04-08.md`
L4 shared / consumer adapter を1本に統合する。

理由:
- 旧文書群では「L4 shared design」「market_summary field」「market_summary builder」「operator_ui adapter」「package skeleton plan」が分散していた
- 現在は `processing/l4_consumer_models/shared/market_summary.py` と `processing/l4_consumer_models/operator_ui/market_summary_adapter.py` が実体として存在するため、統合して現況反映する方が自然

### 3.4 `04_UI_HUB_OPERATOR_UI_SPEC_2026-04-08.md`
UI hub / widget / presenter / bridge をまとめる。

理由:
- UI 側の責務は L4 と密接だが、配置・描画・更新・文言・widget orchestration は UI 専用論点として切り出す方が整理しやすい

### 3.5 `05_SUPPORTING_POLICIES_AND_VERIFICATION_SPEC_2026-04-08.md`
補助ポリシーと verification をまとめる。

含める対象:
- L2/L3 lightweight verification の要約
- L3/L4 compatibility / additive-first / versioning policy
- data/AI の高位方針
- 運用データ path policy の architecture 観点要約

理由:
- verification / compatibility / data / AI は重要だが、L1〜L4 個別仕様に分散させると読みにくい

---

## 4. 現行 repository に対する前提整理
本刷新セットは、少なくとも次の現行事実を前提に書いている。

- `btcts_next/src/btcts/collector_vnext/` は live runtime 主系として存在する
- `btcts_next/src/btcts/ingestion/l2_canonical/` は L2 canonical ownership として存在する
- `btcts_next/src/btcts/processing/l3_market_semantics/` は L3 meaning ownership として存在する
- `btcts_next/src/btcts/processing/l4_consumer_models/shared/market_summary.py` は存在する
- `btcts_next/src/btcts/processing/l4_consumer_models/operator_ui/market_summary_adapter.py` は存在する
- `btcts_next/src/btcts/apps/operator_ui/components/market_state_bridge.py` は shared / adapter を読む bridge として存在する
- `btcts_next/src/btcts/market_engine/market_state/schema.py` は continuity / trust / interpretation を outward に出している
- event usage contract はまだ formal spec / runtime outward contract に未接続
- live orderbook semantics full wiring はまだ未固定

---

## 5. current roadmap との整合
この刷新セットは、`gpt_room` current memory と整合している。

### current phase
- Phase 0 complete
- Phase 1 entry

### current top priority
1. event usage contract formalization
2. Health v1 semantic observer
3. live orderbook semantics runtime wiring contract

### architecture 原則
- L3 = market meaning owner
- L4 = shared shape owner
- prediction / decision = shared contract
- execution = executor only
- Health = observer-only
- additive-first / adapter absorption / replay-first

---

## 6. 旧文書から新文書への代表マッピング

### 旧: runtime / separation / checklist
- `LAYER_RESPONSIBILITY_RUNTIME_SPEC_2026-04-04.md`
- `L2_L3_SEPARATION_LIGHTWEIGHT_VERIFICATION_SPEC_2026-04-04.md`
- `L2_L3_SEPARATION_LIGHTWEIGHT_VERIFICATION_CHECKLIST_2026-04-04.md`

→ 新:
- `01_L1_L2_CAPTURE_CANONICAL_RUNTIME_SPEC_2026-04-08.md`
- `05_SUPPORTING_POLICIES_AND_VERIFICATION_SPEC_2026-04-08.md`

### 旧: L4 shared / field / builder / adapter / structure / plan / migration
- `L4_SHARED_FIRST_DESIGN_SPEC_2026-04-04.md`
- `L4_MARKET_SUMMARY_FIELD_SPEC_2026-04-04.md`
- `L4_MARKET_SUMMARY_BUILDER_SKELETON_SPEC_2026-04-04.md`
- `L4_OPERATOR_UI_ADAPTER_SPEC_2026-04-05.md`
- `L4_UI_ADAPTER_WIDGET_STRUCTURE_SPEC_2026-04-05.md`
- `L4_PACKAGE_SKELETON_IMPLEMENTATION_PLAN_2026-04-05.md`
- `L4_SHARED_FIRST_MIGRATION_CHECKLIST_2026-04-04.md`

→ 新:
- `03_L4_SHARED_CONSUMER_MODELS_SPEC_2026-04-08.md`
- `04_UI_HUB_OPERATOR_UI_SPEC_2026-04-08.md`

### 旧: compatibility / policy / AI / data / overview
- `L3_L4_EVOLUTION_AND_COMPATIBILITY_POLICY_2026-04-05.md`
- `AI_ARCHITECTURE.md`
- `DATA_ARCHITECTURE.md`
- `SYSTEM_ARCHITECTURE.md`

→ 新:
- `00_ARCHITECTURE_REPLACEMENT_INDEX_2026-04-08.md`
- `05_SUPPORTING_POLICIES_AND_VERIFICATION_SPEC_2026-04-08.md`

---

## 7. 正本化のしかた
このセットを `docs/architecture/` へ配置する際は、次のいずれかを推奨する。

### 推奨A
旧 architecture 文書群を入れ替え、旧ファイルは削除する。

### 推奨B
旧文書を archive 的ディレクトリへ移し、`docs/architecture/` の mainline には新セットだけを残す。

どちらでもよいが、**mainline の `docs/architecture/` に stale 文書を残さない**ことを推奨する。

---

## 8. 一言
古い architecture 文書群は「思想は活きているが、現況説明としては stale」が混在している。
現行 mainline 用の正本としては、本刷新セットへ統合し直すのが安全である。
