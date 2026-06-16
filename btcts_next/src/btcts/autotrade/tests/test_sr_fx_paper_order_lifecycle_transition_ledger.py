# path: ./btcts_next/src/btcts/autotrade/tests/test_sr_fx_paper_order_lifecycle_transition_ledger.py
# desc: SR-FX paper order lifecycle transition ledger tests. Simulation only; no broker calls.

from __future__ import annotations

from btcts.autotrade.execution.paper_intent import build_fx_paper_order_intent_from_service_input
from btcts.autotrade.execution.paper_ledger import (
    default_paper_order_ledger_path,
    record_paper_order,
    record_paper_order_transition,
    summarize_paper_order_lifecycle,
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
        "consumer_allowed": ["workroom", "operator_ui", "autotrade", "l4_consumer"],
        "blocked_by": [],
        "warnings": [],
        "read_only": True,
        "would_send_to_broker": False,
    }
    data.update(overrides)
    return data


def _intent_build(decision_id: str, *, size: float = 0.03):
    return build_fx_paper_order_intent_from_service_input(
        _service_input(),
        decision_id=decision_id,
        snapshot_id=f"snapshot_{decision_id}",
        forecast_id=None,
        parameter_set_id="params_fx_balanced_v0_1",
        logic_version="autotrade_logic_v0_1",
        side="buy",
        size=size,
        price=100.0,
        reason_codes=("unit_lifecycle_transition",),
        risk_gate_allowed=True,
        mode="PAPER_OR_REPLAY",
    )


def test_records_lifecycle_transitions_and_current_state_summary(monkeypatch, tmp_path) -> None:
    monkeypatch.setenv("BTC_TS_AUTOTRADE_RUNTIME_ROOT", str(tmp_path / "btc_ts_hot"))
    intent_build = _intent_build("decision_transition_001")
    assert intent_build.intent is not None
    engine = PaperExecutionEngine()

    accepted = engine.submit_fx_execution_intent(intent_build.intent, ts="2026-06-14T00:00:00Z")
    record_paper_order(intent_build=intent_build, order=accepted, recorded_at="2026-06-14T00:00:00Z")
    record_paper_order_transition(order=accepted, recorded_at="2026-06-14T00:00:00Z", transition_event="new_to_accepted")

    partial = engine.partial_fill(intent_build.intent.decision_id, ts="2026-06-14T00:00:01Z", fill_size=0.01, fill_price=101.0)
    assert partial is not None
    record_paper_order_transition(
        previous_order=accepted,
        order=partial,
        recorded_at="2026-06-14T00:00:01Z",
        fill_size=0.01,
        fill_price=101.0,
    )

    filled = engine.fill(intent_build.intent.decision_id, ts="2026-06-14T00:00:02Z", fill_price=103.0)
    assert filled is not None
    record_paper_order_transition(
        previous_order=partial,
        order=filled,
        recorded_at="2026-06-14T00:00:02Z",
        fill_size=0.02,
        fill_price=103.0,
    )

    summary = summarize_paper_order_lifecycle()
    data = summary.to_dict()

    assert summary.exists is True
    assert summary.total_rows == 4
    assert summary.order_count == 1
    assert summary.active_paper_order_count == 0
    assert summary.terminal_paper_order_count == 1
    assert summary.rejected_order_count == 0
    assert summary.status_counts == {"filled": 1}
    assert summary.transition_event_counts["new_to_accepted"] == 1
    assert summary.transition_event_counts["accepted_to_partially_filled"] == 1
    assert summary.transition_event_counts["partially_filled_to_filled"] == 1
    assert summary.latest_status == "filled"
    assert summary.latest_transition_event == "partially_filled_to_filled"
    assert summary.latest_market_uid == "bitflyer.fx.FX_BTC_JPY"
    assert data["read_only"] is True
    assert data["would_send_to_broker"] is False


def test_lifecycle_summary_tracks_cancel_as_terminal_current_state(monkeypatch, tmp_path) -> None:
    monkeypatch.setenv("BTC_TS_AUTOTRADE_RUNTIME_ROOT", str(tmp_path / "btc_ts_hot"))
    intent_build = _intent_build("decision_transition_cancel_001")
    assert intent_build.intent is not None
    engine = PaperExecutionEngine()

    accepted = engine.submit_fx_execution_intent(intent_build.intent, ts="2026-06-14T00:00:00Z")
    record_paper_order_transition(order=accepted, recorded_at="2026-06-14T00:00:00Z", transition_event="new_to_accepted")
    canceled = engine.cancel(intent_build.intent.decision_id, ts="2026-06-14T00:00:03Z", reason="unit_cancel")
    assert canceled is not None
    record_paper_order_transition(previous_order=accepted, order=canceled, recorded_at="2026-06-14T00:00:03Z", reason="unit_cancel")

    summary = summarize_paper_order_lifecycle()

    assert summary.order_count == 1
    assert summary.active_paper_order_count == 0
    assert summary.terminal_paper_order_count == 1
    assert summary.status_counts == {"canceled": 1}
    assert summary.transition_event_counts["accepted_to_canceled"] == 1
    assert summary.latest_status == "canceled"
    assert summary.read_only is True
    assert summary.would_send_to_broker is False


def test_lifecycle_summary_failsoft_skips_malformed_transition_rows(monkeypatch, tmp_path) -> None:
    monkeypatch.setenv("BTC_TS_AUTOTRADE_RUNTIME_ROOT", str(tmp_path / "btc_ts_hot"))
    path = default_paper_order_ledger_path(ensure=True)
    path.write_text("not-json\n", encoding="utf-8")
    intent_build = _intent_build("decision_transition_after_bad_001")
    assert intent_build.intent is not None
    order = PaperExecutionEngine().submit_fx_execution_intent(intent_build.intent, ts="2026-06-14T00:00:00Z")
    record_paper_order_transition(order=order, recorded_at="2026-06-14T00:00:00Z", transition_event="new_to_accepted")

    summary = summarize_paper_order_lifecycle(path)

    assert summary.skipped_rows == 1
    assert len(summary.error_samples) == 1
    assert summary.total_rows == 1
    assert summary.order_count == 1
    assert summary.latest_status == "accepted"
    assert summary.read_only is True
    assert summary.would_send_to_broker is False
