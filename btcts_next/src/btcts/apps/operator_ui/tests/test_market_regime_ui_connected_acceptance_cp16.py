# path: ./btcts_next/src/btcts/apps/operator_ui/tests/test_market_regime_ui_connected_acceptance_cp16.py
# desc: CP16 acceptance checks for MarketRegime UI connected done. Static guard across WarRoom, Collector controls, linked runtime summary, feed resolver, and non-execution safety.

from __future__ import annotations

import sys
from pathlib import Path

_SRC_ROOT = Path(__file__).resolve().parents[4]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

REPO_ROOT = Path(__file__).resolve().parents[6]
WARROOM = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/prediction_warroom/v2/rt_ui/prediction_cards_view.py"
COLLECTOR = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/views/collector_page.py"
TOP_PANELS = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/components/collector_top_panels.py"
LIVE_BRIDGE = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/components/live_bridge.py"
RUNTIME = REPO_ROOT / "btcts_next/src/btcts/prediction/market_regime/operator_ui_runtime.py"
PRODUCER_LOOP = REPO_ROOT / "btcts_next/src/btcts/prediction/market_regime/producer_loop.py"
LAUNCH = REPO_ROOT / "tools/run_operator_ui_sr_fx_dhot.ps1"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8-sig" if path.suffix == ".ps1" else "utf-8")


def test_cp16_warroom_reads_market_regime_latest_cards_from_hot_root() -> None:
    warroom = _read(WARROOM)
    launch = _read(LAUNCH)
    required = [
        "RT_MARKET_REGIME_CARDS_ARTIFACT_RELATIVE_PATH = \"prediction/market_regime/latest_cards.json\"",
        "def _market_regime_cards_artifact_root()",
        "BTCTS_HOT_ROOT",
        "candidate.name.lower() == \"data\"",
        "artifact latest_cards",
    ]
    assert [token for token in required if token not in warroom] == []
    assert '$env:BTCTS_HOT_ROOT = "D:\\btc_ts_hot"' in launch
    assert "data/prediction/market_regime/latest_cards.json" not in warroom


def test_cp16_warroom_render_path_does_not_invoke_classifier_or_raw_preview() -> None:
    warroom = _read(WARROOM)
    forbidden = [
        "classify_market_regime_feature_bundle",
        "build_market_regime_feature_bundle(",
        "RT_MARKET_REGIME_CARD_PREVIEW_HOT_ROOT",
        "broker_private_api_allowed: bool = True",
        "autotrade_trigger_allowed: bool = True",
    ]
    assert [token for token in forbidden if token in warroom] == []
    required = [
        '"raw_market_source_read_performed": False',
        '"preview_inference_invoked": False',
        '"classifier_invoked": False',
    ]
    assert [token for token in required if token not in warroom] == []


def test_cp16_collector_unified_buttons_manage_chart_and_market_regime_loop() -> None:
    collector = _read(COLLECTOR)
    required = [
        "start_chart_engine_detached",
        "request_chart_engine_safe_stop",
        "request_chart_engine_restart",
        "start_market_regime_producer_loop_detached",
        "request_market_regime_producer_loop_safe_stop",
        "request_market_regime_producer_loop_restart",
        "market_regime=",
        "Chart Engine / MarketRegime",
    ]
    assert [token for token in required if token not in collector] == []
    assert "Collector 起動/停止/再起動ボタンへの自動連動は未接続" not in collector


def test_cp16_collector_top_summary_is_display_only_and_has_details() -> None:
    panels = _read(TOP_PANELS)
    required = [
        "Linked Runtime Summary",
        "build_linked_runtime_summary_items",
        "_render_runtime_status_card",
        "runtime_id",
        "severity",
        "detail_rows",
        "st.popover(\"詳細\"",
        "height:7.35rem",
    ]
    assert [token for token in required if token not in panels] == []
    forbidden = [
        "start_stack_detached",
        "start_chart_engine_detached",
        "start_market_regime_producer_loop_detached",
        "request_market_regime_producer_loop_safe_stop",
        "write_unified_supervisor_request",
    ]
    assert [token for token in forbidden if token in panels] == []


def test_cp16_collector_feed_state_is_single_source_display_snapshot() -> None:
    live_bridge = _read(LIVE_BRIDGE)
    assert live_bridge.count("def _resolve_feed_state") == 1
    assert live_bridge.count("_resolve_feed_state(status, origin_status, audit_rows)") == 2
    assert "load_origin_status" in live_bridge
    assert "unified_origin_status.json" in live_bridge
    assert "return _resolve_feed_state(status, origin_status, audit_rows)" not in live_bridge
    forbidden = [
        "start_stack_detached",
        "start_chart_engine_detached",
        "start_market_regime_producer_loop_detached",
        "request_market_regime_producer_loop_safe_stop",
        "write_unified_supervisor_request",
        "subprocess.Popen",
    ]
    assert [token for token in forbidden if token in live_bridge] == []


def test_cp16_market_regime_loop_is_preflight_gated_and_non_executing() -> None:
    loop = _read(PRODUCER_LOOP)
    runtime = _read(RUNTIME)
    required_loop = [
        "preflight_market_regime_latest_artifacts_once",
        "write_market_regime_latest_artifacts_once",
        "control.json",
        "safe_stop",
        "max_iterations",
        "controlled_loop_only",
    ]
    assert [token for token in required_loop if token not in loop] == []
    required_runtime = [
        "--once-loop",
        "producer_loop.lock.json",
        "market_regime_producer_loop_runtime_snapshot",
    ]
    assert [token for token in required_runtime if token not in runtime] == []


def test_cp16_acceptance_keeps_broker_autotrade_order_paths_disabled() -> None:
    paths = [WARROOM, COLLECTOR, TOP_PANELS, LIVE_BRIDGE, RUNTIME, PRODUCER_LOOP]
    forbidden = [
        "broker_private_api_allowed: bool = True",
        "autotrade_trigger_allowed: bool = True",
        "would_send_to_broker: bool = True",
        "order_intent_submitted: bool = True",
        "trade_ledger_append_allowed: bool = True",
        "parameter_auto_promotion_allowed: bool = True",
    ]
    hits: list[str] = []
    for path in paths:
        text = _read(path)
        for token in forbidden:
            if token in text:
                hits.append(f"{path.relative_to(REPO_ROOT)}:{token}")
    assert hits == []
