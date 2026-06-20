# path: ./docs/_INDEX.md
# desc: Canonical documentation entrypoint for BTC Trade System docs.
# BTC Trade System (BTC-TS)
## Documentation Index

この `docs/_INDEX.md` は **BTC-TS ドキュメントの正準入口**です。
Project Chimera の設計・仕様はここから参照します。

---

# 1. Core Design (Project Chimera)

まず最初に読むドキュメント

- BTC-TS Manifest  
  docs/BTC_TS_MANIFEST.md

- System Architecture  
  docs/architecture/SYSTEM_ARCHITECTURE.md

- Layer Responsibility Runtime Spec  
  docs/architecture/LAYER_RESPONSIBILITY_RUNTIME_SPEC_2026-04-04.md

- L2/L3 Separation Lightweight Verification Spec  
  docs/architecture/L2_L3_SEPARATION_LIGHTWEIGHT_VERIFICATION_SPEC_2026-04-04.md

- L2/L3 Separation Lightweight Verification Checklist  
  docs/architecture/L2_L3_SEPARATION_LIGHTWEIGHT_VERIFICATION_CHECKLIST_2026-04-04.md

- L4 Shared-First Design Spec  
  docs/architecture/L4_SHARED_FIRST_DESIGN_SPEC_2026-04-04.md

- L4 Shared-First Migration Checklist  
  docs/architecture/L4_SHARED_FIRST_MIGRATION_CHECKLIST_2026-04-04.md

- UI Hub / Widget Architecture Spec  
  docs/architecture/UI_HUB_WIDGET_ARCHITECTURE_SPEC_2026-04-04.md

- L4 Market Summary Field Spec  
  docs/architecture/L4_MARKET_SUMMARY_FIELD_SPEC_2026-04-04.md

- L4 Market Summary Builder Skeleton Spec  
  docs/architecture/L4_MARKET_SUMMARY_BUILDER_SKELETON_SPEC_2026-04-04.md

- L4 Operator UI Adapter Spec  
  docs/architecture/L4_OPERATOR_UI_ADAPTER_SPEC_2026-04-05.md

- AI Architecture  
  docs/architecture/AI_ARCHITECTURE.md

- Data Architecture  
  docs/architecture/DATA_ARCHITECTURE.md
- AutoTrade Pre-Armed Dry Run Authorization Chain Boundary Spec  
  docs/architecture/AUTOTRADE_PRE_ARMED_DRY_RUN_AUTHORIZATION_CHAIN_BOUNDARY_SPEC_2026-06-18.md
- AutoTrade Pre-Armed Dry Run Authorization Grant Design Spec  
  docs/architecture/AUTOTRADE_PRE_ARMED_DRY_RUN_AUTHORIZATION_GRANT_DESIGN_SPEC_2026-06-18.md



---

# 2. Strategy System

戦略進化システム

- Strategy Genome System  
  docs/strategy/STRATEGY_SYSTEM.md

- Prediction System Inference Formal Spec
  docs/strategy/PREDICTION_SYSTEM_INFERENCE_FORMAL_SPEC_BTC_BITFLYER_2026-06-20.md

---

# 3. UI System

Human-AI インターフェース

- UI Architecture  
  docs/ui/UI_ARCHITECTURE.md

- SR-FX Operator UI D-hot / Execution-Market Integrity Spec  
  docs/ui/SR_FX_OPERATOR_UI_DHOT_EXECUTION_MARKET_SPEC_2026-06-16.md

---

# 4. Development Plan

開発ロードマップ

- Development Roadmap  
  docs/roadmap/DEVELOPMENT_ROADMAP.md

---

# 5. Subsystem Specifications

実装サブシステム仕様

Collector System

docs/systems/collector/

含まれる仕様

- Collector
- API Rate Control
- Health Monitoring
- Supervisor (Watchdog)
- Audit System
- Exchange Configuration

---

# 6. Tools & Utilities

テストツール・運用ツール

docs/tools/

---

# 7. Examples / Samples

サンプルデータ

docs/placeholders/

---

# 8. GPT Working Area

GPTの作業・記憶領域

gpt_room/

※現在のスレ跨ぎ用の引き継ぎ正本

---

# Rule

- 正式仕様 → docs/
- GPT引き継ぎ → gpt_room
- 古い仕様 → _stash/Docs_OLD

docs = Project Chimera Official Documentation

---

# 9. Current GPT Handoff Room

Current cross-thread handoff files:

- gpt_room/STATUS.md
- gpt_room/FOCUS.json
- gpt_room/state.json
- gpt_room/runbook/PROJECT_STATE.md
- gpt_room/DECISIONS.md

Current baseline:

- Branch: phase2
- HEAD: 0e615c31
- Test checkpoint: 247 passed

Use these files when continuing work across threads.
