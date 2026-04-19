# path: ./archive/phase3_warroom_graph_hybrid_refresh_progress_2026-04-15.md
# desc: Archived note, specification, report, or reference document.

# Phase 3 WarRoom hybrid refresh progress

更新日: 2026-04-15
位置づけ: `./tmp/` 成果物 / WarRoom live foundation progress note

---

## 結論
WarRoom は current repo truth として、

- graph family 3本
  - `market_monitor`
  - `liquidity_pressure`
  - `trade_flow_monitor`
- pure display summary family 6本
  - `warroom_header`
  - `market_regime`
  - `ai_signal`
  - `strategy_state`
  - `risk_monitor`
  - `agent_panels`

の合計 **9 widget を fragment refresh reached** と読んでよい。

ただし current mode は full fragment page ではない。
正しい読みは
**majority fragment + page reload fallback の hybrid refresh**
である。

---

## reached と読んでよいもの
### 1. refresh planning
- `live_shell.resolve_page_refresh_plan(...)` で `warroom` は fragment target に含まれる
- ただし non-fragment widget を守るため、page reload fallback も維持している
- page reload 間隔は graph 3秒 path に全体が引っ張られないよう、non-fragment widget 基準へ分離した
- current fallback bottleneck は `warroom_alert_engine` / `warroom_timeline` で、これらは `poll_slow` に落としてある

### 2. fragment reached widgets
#### graph family
- `market_monitor`
- `liquidity_pressure`
- `trade_flow_monitor`

#### pure display summary family
- `warroom_header`
- `market_regime`
- `ai_signal`
- `strategy_state`
- `risk_monitor`
- `agent_panels`

### 3. diagnostics
- WarRoom refresh diagnostics は hybrid refresh profile を表示する
- current reading を UI 上で確認しやすくした
- current diagnostic reading:
  - fragment widget count = 9
  - fragment interval = 3s
  - page reload fallback = 15s 寄り

---

## current safe reading
### fragment reached
- graph family: reached
- pure display majority: reached
- hybrid diagnostics: reached

### hold / page reload fallback side
- `warroom_alert_engine`
- `warroom_timeline`
- `ai_operator_panel`
- `decision_log_panel`
- `watch_list_panel`
- `ai_reasoning_panel`
- `ai_market_summary_panel`
- `ai_conversation_panel`

### reason for hold
- button / replay jump / session mutation を持つもの
- memory / decision persistence を持つもの
- AI diagnostics family で slow reload の方が安全なもの

---

## tests / checks
### 追加・更新確認
- `btcts_next/src/btcts/apps/operator_ui/tests/test_live_shell_refresh_plan.py`
- `btcts_next/src/btcts/apps/operator_ui/tests/test_warroom_page_graph_refresh_path.py`
- `btcts_next/src/btcts/apps/operator_ui/tests/test_warroom_page_summary_refresh_path.py`
- `btcts_next/src/btcts/apps/operator_ui/tests/test_warroom_page_refresh_diagnostics.py`

### user-run checks
- `python -m py_compile` on touched files
- `test_live_shell_refresh_plan.py`
- `test_warroom_page_graph_refresh_path.py`
- `test_warroom_page_summary_refresh_path.py`
- `test_warroom_page_refresh_diagnostics.py`

all green で通過。

---

## current open
- `warroom_alert_engine` / `warroom_timeline` を button-safe に fragment 化する need があるか
- `ai_operator_panel` を fragment 化する actual value があるか
- AI diagnostics family を slow reload のまま維持するか
- fallback page reload をさらに下げる価値があるか

---

## 次の自然な候補
1. current reached を `STATUS / handoff / worklog` に同期する
2. `warroom_alert_engine` / `warroom_timeline` を hold のまま current truth に固定する
3. WarRoom next adopter need が weak ならここで一旦止める
4. need が明確なら button-safe / state-safe な 1 widget だけ追加で切る

---

## 一言
今回の repo truth は、
**WarRoom 全面 live 化** ではない。

正しい読みは
**WarRoom majority fragment reached, current mode = hybrid refresh, interactive widgets intentionally held**
である。
