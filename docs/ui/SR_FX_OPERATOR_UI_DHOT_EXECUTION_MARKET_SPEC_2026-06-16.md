# path: ./docs/ui/SR_FX_OPERATOR_UI_DHOT_EXECUTION_MARKET_SPEC_2026-06-16.md
# desc: SR-FX Operator UI D-hot / execution-market refresh and display integrity closeout spec.

# SR-FX Operator UI D-hot / Execution-Market Integrity Spec

Updated: 2026-06-16
Status: current implementation closeout spec
Scope: Operator UI `Collector`, `Health`, `WarRoom`; D-hot runtime; SR-FX execution-market display integrity

---

## 1. Purpose

This document records the UI closeout state reached after the SR-FX Data/UI Integrity Gate recovery work.

The goal of this work was not to add trading logic. The goal was to make the Operator UI usable and trustworthy before returning to the main AutoTrade roadmap.

The closeout criteria were:

- no browser/page reload whitening during normal tab use;
- faster tab transitions and less stress during WarRoom / Collector / Health use;
- Collector / Health / WarRoom must read D-hot runtime roots when launched through the SR-FX D-hot launcher;
- WarRoom current decision material must be FX execution-market only;
- implicit `BTC_JPY` / spot current material must not appear in the three-tab decision surface;
- implicit `E:\btc_ts` cold-data reads must not drive current WarRoom material;
- Health may show aggregate bitFlyer/system pressure, but must not be mistaken for WarRoom current FX-only decision material;
- no broker execution is enabled by this work.

---

## 2. Runtime identity and root contract

When the SR-FX D-hot launcher is used, the UI runtime is expected to carry these roots and market identity:

```text
BTC_TS_DATA_DIR=D:\btc_ts_hot\data
BTC_TS_LOGS_DIR=D:\btc_ts_hot\logs
BTCTS_DATA_ROOT=D:\btc_ts_hot\data
BTCTS_LOGS_ROOT=D:\btc_ts_hot\logs
BTCTS_STATE_ROOT=D:\btc_ts_hot\state
BTCTS_SYMBOL=FX_BTC_JPY
BTCTS_INSTRUMENT_ID=bitflyer.fx.FX_BTC_JPY
BTCTS_EXECUTION_PRODUCT_CODE=FX_BTC_JPY
BTCTS_EXECUTION_MARKET_UID=bitflyer.fx.FX_BTC_JPY
BTCTS_WS_SSL_VERIFY=true
BTCTS_WS_CA_FILE=<certifi cacert.pem path>
```

Current UI display rules:

```text
Collector tab = D-hot collector runtime view.
Health tab = aggregate bitFlyer/system pressure and runtime health view.
WarRoom tab = FX_BTC_JPY / bitflyer.fx.FX_BTC_JPY execution-market current material only.
```

Health may aggregate exchange/system pressure across relevant request classes. WarRoom current material must not silently use spot `BTC_JPY` as the current execution decision source.

---

## 3. Refresh and anti-whitening contract

The UI closeout uses soft fragment refresh instead of page-level reloads for the main live pages.

Required behavior:

- page reload refresh remains disabled for normal live operation;
- fragment refresh remains enabled when `ui_auto_refresh` is on;
- `Collector`, `Health`, and `WarRoom` must avoid full-page whiteout during normal updates;
- expensive diagnostics are folded/lazy and must not run on every normal render;
- repeated JSONL and market-state reads are bounded or cached where appropriate.

Important implementation points:

- `live_shell` owns fragment / page refresh policy.
- `collector_page.render()` wraps the Collector body with `render_fragment_block(..., page_key="collector")`.
- Health fragment blocks pass `page_key="health"` so freshness and continuity logic can tell when a section is in the live fragment context.
- WarRoom diagnostics sections are gated behind checkboxes so they do not run during normal page use.
- Health builds the expensive snapshot once per page render and only reloads per-section snapshots inside fragment context.

---

## 4. Collector tab contract

Collector is the D-hot live operations view.

Collector UI must:

- read collector state from the D-hot logs/state-derived roots;
- show D-hot UI roots and market-state roots explicitly in diagnostics;
- support soft refresh without page whitening;
- show execution-market market summary captions, not default spot `BTC_JPY` captions;
- inherit verified WS TLS settings when starting stack children from the UI;
- keep Start / Stop / Restart controls read-only with respect to broker execution; they control collector processes, not broker orders.

Collector-related closeout changes include:

- Collector page soft fragment refresh;
- persistent Auto Save checkbox/state behavior in app-level UI settings;
- Collector caption helpers changed from default market summary helpers to execution-market helpers;
- execution-feed and system-stats caption helpers changed to execution-market helpers;
- stack control now sets verified WS TLS env defaults with certifi fallback instead of disabling verification.

WS Board heartbeat audit:

- `unified_ws_board_lane` emits throttled `collector_vnext.unified.ws_board.message.received` audit heartbeats;
- the heartbeat is fail-soft and must never break the live board stream;
- heartbeat audit is throttled by `BTCTS_UNIFIED_WS_BOARD_AUDIT_HEARTBEAT_SEC`, defaulting to 60 seconds.

---

## 5. Health tab contract

Health is an aggregate runtime and exchange-pressure observer. It is not the owner of market meaning.

Health UI must:

- read from D-hot roots under the SR-FX launcher;
- keep fragment refresh on and page reload off during normal operation;
- show WS/API/Layer3 continuity in a stable way;
- show WS Board and WS Executions lanes using current truth overlays for the rightmost/recent cells;
- distinguish historical audit coverage from current lane truth;
- keep hot/cold retention safety display-only and based on precomputed summaries; it must not scan/copy/delete D/E data trees from the UI render path.

Continuity rail current conventions:

```text
API REST = REST / board snapshot / trades polling
WS Board = orderbook stream
WS Executions = trades/executions stream
```

Rightmost cells may overlay current lane truth so that a live WS lane is visible even when older audit coverage has gaps.

---

## 6. WarRoom contract

WarRoom is the FX execution-market current decision-support view.

WarRoom current material must be:

```text
FX_BTC_JPY / bitflyer.fx.FX_BTC_JPY
read_only=true
would_send_to_broker=false
```

WarRoom must not silently use:

- default `BTC_JPY` market summary/prediction helpers;
- hardcoded `E:\btc_ts` logs/replay/research roots;
- old `live_canonical`-only source checks;
- `replay_board+tradeflow` labels for execution-market live/current sources.

Closeout changes:

- WarRoom current summary/status/prediction/tactic captions now use execution-market helpers;
- Risk Monitor, AI Signal, AI Reasoning, AI Market Summary, AI Conversation diagnostics, Strategy State, Decision Log, Watch List, Market Regime, and WarRoom active-event captions are aligned to execution-market helpers;
- WarRoom alert/audit/research bridges use `btcts.core.paths` roots instead of hardcoded `E:\btc_ts`;
- if D-hot research/replay artifacts are absent, panels should show missing/unknown rather than silently reading cold E data;
- source labels recognize `execution_market_live_canonical` and `execution_market_state` as first-class current sources;
- legacy labels are kept only for old test/caller compatibility.

AI Operator status:

- fallback-local is a valid safe operating mode when external AI is not configured;
- `BTCTS_AI_EXTERNAL_ENABLED=1` and `BTCTS_AI_EXTERNAL_URL` are required before external HTTP AI can be used;
- AI Operator output is advisory/review support only and is not a broker execution instruction.

---

## 7. File/path boundary rules

UI code must prefer `btcts.core.paths` for runtime roots.

Allowed current runtime reads:

- D-hot data/logs/state roots through environment-aware core path helpers;
- execution-market market-state helpers through `market_state_bridge` execution-market functions;
- precomputed display artifacts when explicitly labeled as research/replay support.

Disallowed for current WarRoom material:

- implicit spot `BTC_JPY` fallback;
- hardcoded `E:\btc_ts` current audit/replay/research reads;
- UI-side reconstruction of market meaning;
- broker-send behavior or real order execution.

---

## 8. Verification commands

Useful closeout checks:

```powershell
Set-Location C:\BtcTradeSystem
$ErrorActionPreference = "Stop"

# Compile main touched UI and support files as needed.
.\.venv\Scripts\python.exe -m py_compile `
  .\btcts_next\src\btcts\apps\operator_ui\views\collector_page.py `
  .\btcts_next\src\btcts\apps\operator_ui\views\health_page.py `
  .\btcts_next\src\btcts\apps\operator_ui\views\warroom_page.py `
  .\btcts_next\src\btcts\apps\operator_ui\components\market_state_bridge.py

# Three-tab decision-surface grep.
git grep -n "load_market_summary_widget_model()" -- `
  .\btcts_next\src\btcts\apps\operator_ui\views\collector_page.py `
  .\btcts_next\src\btcts\apps\operator_ui\views\health_page.py `
  .\btcts_next\src\btcts\apps\operator_ui\views\warroom_page.py `
  .\btcts_next\src\btcts\apps\operator_ui\components

git grep -n "BTC_JPY\|E:\\btc_ts\|== \"live_canonical\"\|replay_board+tradeflow" -- `
  .\btcts_next\src\btcts\apps\operator_ui\views\collector_page.py `
  .\btcts_next\src\btcts\apps\operator_ui\views\health_page.py `
  .\btcts_next\src\btcts\apps\operator_ui\views\warroom_page.py `
  .\btcts_next\src\btcts\apps\operator_ui\components
```

Expected result for the three-tab current decision-surface grep is no runtime current-material hits.

Manual UI smoke:

```text
Collector: D-hot roots visible; no whiteout; caption not stale spot/BTC_JPY.
Health: fragment refresh on; page reload off; WS Board/Executions continuity updates; D-hot roots visible.
WarRoom: source=execution_market_*; no stale 2026-04 BTC_JPY caption; AI Operator fallback-local is safe if external AI is disabled.
```

---

## 9. Remaining non-blocking follow-up

These are not blockers for closing this UI thread:

1. Install pytest later if desired.
2. Keep the WS Board heartbeat audit test finite before adding it to a pytest gate.
3. Consider extracting repeated `_source_label_for_data_source` helpers into a small shared UI helper.
4. Decide CRLF/LF policy before long-term cleanup commits.
5. Configure external AI only when a real external endpoint is ready.

---

## 10. Closeout statement

As of this closeout, the Operator UI has moved from a stressful full-page reload / mixed-source display surface to a softer fragment-refresh and execution-market-aligned display surface.

The UI work is considered closed enough to return to the main AutoTrade roadmap after commit and final human approval.
