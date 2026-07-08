# path: ./btcts_next/src/btcts/apps/operator_ui/tests/test_collector_buttons_link_market_regime_loop_cp15c.py
# desc: Tests Collector unified buttons link Chart Engine and MarketRegime producer loop. No broker, AutoTrade, order, or trade ledger behavior.

from __future__ import annotations

import sys
from pathlib import Path

_SRC_ROOT = Path(__file__).resolve().parents[4]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

REPO_ROOT = Path(__file__).resolve().parents[6]
COLLECTOR_PAGE = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/views/collector_page.py"


def _collector_text() -> str:
    return COLLECTOR_PAGE.read_text(encoding="utf-8")


def test_cp15c_collector_start_links_market_regime_loop() -> None:
    text = _collector_text()
    start_index = text.index("def _request_unified_start")
    stop_index = text.index("def _request_unified_safe_stop")
    block = text[start_index:stop_index]
    assert "start_chart_engine_detached" in block
    assert "start_market_regime_producer_loop_detached" in block
    assert "market_regime=" in block
    assert "market_regime_start_failed" in block


def test_cp15c_collector_safe_stop_links_market_regime_loop() -> None:
    text = _collector_text()
    start_index = text.index("def _request_unified_safe_stop")
    stop_index = text.index("def _request_unified_restart")
    block = text[start_index:stop_index]
    assert "request_chart_engine_safe_stop" in block
    assert "request_market_regime_producer_loop_safe_stop" in block
    assert "market_regime=" in block


def test_cp15c_collector_restart_links_market_regime_loop() -> None:
    text = _collector_text()
    start_index = text.index("def _request_unified_restart")
    stop_index = text.index("def _supervisor_status_rows")
    block = text[start_index:stop_index]
    assert "request_chart_engine_restart" in block or "start_chart_engine_detached" in block
    assert "request_market_regime_producer_loop_restart" in block
    assert "market_regime=" in block


def test_cp15c_supervisor_linked_runtime_tracks_chart_and_market_regime() -> None:
    text = _collector_text()
    assert "market_regime_loop_snapshot = market_regime_producer_loop_runtime_snapshot()" in text
    assert "linked_runtime_active=bool(chart_engine_snapshot.get(\"active\") or market_regime_loop_snapshot.get(\"active\"))" in text
    assert 'linked_runtime_label="Chart Engine / MarketRegime"' in text
    old_note = "Collector 起動/停止/再起動ボタンへの自動連動は未接続"
    assert old_note not in text
    assert "Collector の起動/停止/再起動ボタンにも連動します" in text


def test_cp15c_no_execution_side_effect_flags_enabled() -> None:
    text = _collector_text()
    forbidden = [
        "broker_private_api_allowed: bool = True",
        "autotrade_trigger_allowed: bool = True",
        "order_intent_submitted: bool = True",
        "trade_ledger_append_allowed: bool = True",
        "parameter_auto_promotion_allowed: bool = True",
    ]
    assert [token for token in forbidden if token in text] == []
