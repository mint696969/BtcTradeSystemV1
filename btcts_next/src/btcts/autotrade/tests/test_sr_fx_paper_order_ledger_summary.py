# path: ./btcts_next/src/btcts/autotrade/tests/test_sr_fx_paper_order_ledger_summary.py
# desc: Read-only SR-FX paper order ledger summary tests. No broker calls.

from __future__ import annotations

from btcts.autotrade.execution.paper_intent import build_fx_paper_order_intent_from_service_input
from btcts.autotrade.execution.paper_ledger import (
    default_paper_order_ledger_path,
    read_paper_order_ledger_rows,
    record_paper_order,
    summarize_paper_order_ledger,
)
from btcts.autotrade.replay.paper_engine import PaperExecutionEngine


def _service_input(**overrides):
    data = {
        "contract_type": "execution_market_service_input",
        "service_input_role": "execution_market",
        "exchange": "bitflyer",
        "symbol_raw": "FX_BTC_JPY",
        "market_uid": "bitflyer.fx.FX_BTC_JPY",
        "source_kind": "market_state_preferred",
        "source_series_id": "unit:fx:rest:series:1",
        "event_ts": "2026-06-14T00:00:00Z",
        "freshness": "LIVE",
        "is_stale": False,
        "trust_state": "trusted",
        "continuity_state": "rest_baseline_snapshot",
        "interpretation_bucket": "allow_structural_use",
        "semantic_runtime_wiring_status": "wired",
        "orderbook_wiring_status": "missing",
        "consumer_allowed": ["workroom", "operator_ui", "autotrade", "l4_consumer"],
        "capabilities": ["market_summary_anchor", "freshness_usable", "trusted_market_state"],
        "blocked_by": [],
        "warnings": ["execution_market_rest_baseline_not_continuous_ws_series"],
        "read_only": True,
        "would_send_to_broker": False,
    }
    data.update(overrides)
    return data


def _intent_build(decision_id: str, service_input=None):
    return build_fx_paper_order_intent_from_service_input(
        service_input or _service_input(),
        decision_id=decision_id,
        snapshot_id=f"snapshot_{decision_id}",
        forecast_id=None,
        parameter_set_id="params_fx_balanced_v0_1",
        logic_version="autotrade_logic_v0_1",
        side="buy",
        size=0.001,
        price=100.0,
        reason_codes=("unit_summary",),
        risk_gate_allowed=True,
        mode="PAPER_OR_REPLAY",
    )


def test_summarize_empty_paper_order_ledger_is_read_only(monkeypatch, tmp_path) -> None:
    monkeypatch.setenv("BTC_TS_AUTOTRADE_RUNTIME_ROOT", str(tmp_path / "btc_ts_hot"))

    summary = summarize_paper_order_ledger()

    assert summary.exists is False
    assert summary.total_rows == 0
    assert summary.active_paper_order_count == 0
    assert summary.terminal_paper_order_count == 0
    assert summary.read_only is True
    assert summary.would_send_to_broker is False


def test_summarize_paper_order_ledger_counts_active_terminal_and_rejected(monkeypatch, tmp_path) -> None:
    monkeypatch.setenv("BTC_TS_AUTOTRADE_RUNTIME_ROOT", str(tmp_path / "btc_ts_hot"))
    path = default_paper_order_ledger_path(ensure=True)
    engine = PaperExecutionEngine()

    accepted_build = _intent_build("decision_summary_active_001")
    assert accepted_build.intent is not None
    accepted_order = engine.submit_fx_execution_intent(accepted_build.intent, ts="2026-06-14T00:00:00Z")
    record_paper_order(intent_build=accepted_build, order=accepted_order, recorded_at="2026-06-14T00:00:01Z")

    filled_order = engine.fill(accepted_build.intent.decision_id, ts="2026-06-14T00:00:02Z", fill_price=101.0)
    assert filled_order is not None
    record_paper_order(intent_build=accepted_build, order=filled_order, recorded_at="2026-06-14T00:00:03Z")

    blocked_build = _intent_build("decision_summary_blocked_001", _service_input(freshness="STALE", is_stale=True))
    record_paper_order(intent_build=blocked_build, order=None, recorded_at="2026-06-14T00:00:04Z")

    summary = summarize_paper_order_ledger(path)
    data = summary.to_dict()

    assert summary.exists is True
    assert summary.total_rows == 3
    assert summary.accepted_count == 2
    assert summary.rejected_count == 1
    assert summary.active_paper_order_count == 1
    assert summary.terminal_paper_order_count == 1
    assert summary.status_counts == {"accepted": 1, "filled": 1}
    assert summary.blocked_by_counts["service_input_stale"] == 1
    assert summary.blocked_by_counts["paper_order_missing"] == 1
    assert summary.latest_decision_id is None
    assert summary.latest_status is None
    assert summary.latest_accepted is False
    assert "service_input_stale" in summary.latest_blocked_by
    assert data["read_only"] is True
    assert data["would_send_to_broker"] is False


def test_paper_order_ledger_summary_failsoft_skips_malformed_rows(monkeypatch, tmp_path) -> None:
    monkeypatch.setenv("BTC_TS_AUTOTRADE_RUNTIME_ROOT", str(tmp_path / "btc_ts_hot"))
    path = default_paper_order_ledger_path(ensure=True)
    path.write_text("not-json\n", encoding="utf-8")
    intent_build = _intent_build("decision_summary_after_bad_001")
    assert intent_build.intent is not None
    order = PaperExecutionEngine().submit_fx_execution_intent(intent_build.intent, ts="2026-06-14T00:00:00Z")
    record_paper_order(intent_build=intent_build, order=order, recorded_at="2026-06-14T00:00:01Z")

    read = read_paper_order_ledger_rows(path)
    summary = summarize_paper_order_ledger(path)

    assert read.skipped_count == 1
    assert len(read.error_samples) == 1
    assert summary.skipped_rows == 1
    assert summary.total_rows == 1
    assert summary.latest_status == "accepted"
    assert summary.error_samples == read.error_samples
    assert summary.read_only is True
    assert summary.would_send_to_broker is False
