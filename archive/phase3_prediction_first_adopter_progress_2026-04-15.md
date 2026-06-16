# path: ./archive/phase3_prediction_first_adopter_progress_2026-04-15.md
# desc: Archived note, specification, report, or reference document.

# Phase 3 prediction first adopter progress

更新日: 2026-04-16
位置づけ: `./tmp/` 成果物 / PredictionSummary adopter progress note

---

## 結論
`PredictionSummary` の current adopter line は、repo truth として

### AI lightweight family
- `ai_reasoning_panel`
- `ai_market_summary_panel`
- `ai_signal_panel`
- `ai_operator_panel`

### pure display WarRoom family
- `strategy_state_panel`
- `agent_panels`

の **6 adopter reached** と読んでよい。

ただし current rollout は still narrow であり、
- decision log / execution feed などの action / persistence / audit owner 側
- prediction observer full panel

には広げていない。

---

## reached と読んでよいもの
### 1. shared prediction first slice
- `PredictionSummary`
- `PredictionSummaryBuildInput`
- `build_prediction_summary(...)`
- primary anchor = `market_summary`
- optional caution input = `health_digest`

### 2. operator_ui thin path
- thin adapter
- state owner
- bridge
- `prediction_snapshot_lines(...)`

### 3. adopter reached
#### AI lightweight family
- `ai_reasoning_panel`
- `ai_market_summary_panel`
- `ai_signal_panel`
- `ai_operator_panel`

#### pure display WarRoom family
- `strategy_state_panel`
- `agent_panels`

いずれも thin snapshot 補助表示に留めている。

---

## current safe reading
### reached
- shared read model: reached
- thin snapshot presenter path: reached
- AI lightweight family: reached
- pure display WarRoom extension: reached

### intentionally held
- `decision_log_panel`
- `execution_feed_panel`
- prediction observer full panel
- decision contract
- tactic contract
- execution bundle
- broader non-display rollout

---

## tests / checks
### 追加・更新確認
- `btcts_next/src/btcts/apps/operator_ui/tests/test_ai_reasoning_prediction_snapshot.py`
- `btcts_next/src/btcts/apps/operator_ui/tests/test_ai_market_summary_prediction_snapshot.py`
- `btcts_next/src/btcts/apps/operator_ui/tests/test_ai_signal_prediction_snapshot.py`
- `btcts_next/src/btcts/apps/operator_ui/tests/test_ai_operator_prediction_snapshot.py`
- `btcts_next/src/btcts/apps/operator_ui/tests/test_strategy_state_prediction_snapshot.py`
- `btcts_next/src/btcts/apps/operator_ui/tests/test_agent_panels_prediction_snapshot.py`
- `btcts_next/src/btcts/apps/operator_ui/tests/test_market_state_bridge.py`
- `btcts_next/src/btcts/apps/operator_ui/tests/test_market_signal_state_adopters.py`
- `tmp/phase25_thread_operator_ui_regression_2026-04-14.ps1`

### user-run checks
- `python -m py_compile` on touched python files
- `test_ai_operator_prediction_snapshot.py`
- `test_strategy_state_prediction_snapshot.py`
- `test_agent_panels_prediction_snapshot.py`
- `test_market_state_bridge.py`
- `test_market_signal_state_adopters.py`
- `powershell -ExecutionPolicy Bypass -File tmp/phase25_thread_operator_ui_regression_2026-04-14.ps1`

focused regression bundle は all green で通過。

---

## current open
- decision / execution owner 側へ prediction snapshot を広げる value が本当にあるか
- prediction observer full panel を別 owner として起こす必要があるか
- pure display を超えて action / persistence 側へ広げる必要があるか

---

## 次の自然な候補
1. current reached を `STATUS / handoff / worklog` に同期する
2. Prediction rollout をいったん止めて minimality を維持する
3. next actual adopter need が出た場合だけ 1 本追加する

---

## 一言
current truth は、
**PredictionSummary first slice reached, current adopter line = AI lightweight family 4本 + pure display WarRoom family 2本, broader rollout intentionally held**
である。
