# path: ./btcts_next/src/btcts/apps/tests/test_sr_fx_data_lineage_parity_audit_once.py
# desc: SR-FX Data/UI Integrity Gate G3 lineage parity audit tests. Read-only; no broker calls.

from __future__ import annotations

import json
from pathlib import Path

from btcts.apps import sr_fx_data_lineage_parity_audit_once as app


def _ctx() -> dict:
    return {
        "exchange": "bitflyer",
        "symbol_raw": "FX_BTC_JPY",
        "product_code": "FX_BTC_JPY",
        "market_uid": "bitflyer.fx.FX_BTC_JPY",
        "market_type": "fx",
        "market_role": "execution",
        "read_only": True,
        "would_send_to_broker": False,
    }


def _overview(**overrides) -> dict:
    data = {
        "exchange": "bitflyer",
        "symbol_raw": "FX_BTC_JPY",
        "market_uid": "bitflyer.fx.FX_BTC_JPY",
        "collector_ts": "2026-06-14T00:00:00Z",
        "trust_state": "trusted",
        "continuity_state": "rest_baseline_snapshot",
        "interpretation_bucket": "allow_structural_use",
        "best_bid": 100.0,
        "best_ask": 101.0,
        "spread": 1.0,
        "imbalance": 0.25,
        "trade_delta": -0.5,
        "source_series_id": "unit:fx:rest_board_baseline",
        "near_zone_liquidity_summary": {"bid_size_total": 2.0, "ask_size_total": 1.2},
    }
    data.update(overrides)
    return data


def _summary(**overrides) -> dict:
    data = {
        "summary_type": "market_summary",
        "exchange": "bitflyer",
        "symbol_raw": "FX_BTC_JPY",
        "market_uid": "bitflyer.fx.FX_BTC_JPY",
        "source_kind": "market_state_preferred",
        "source_series_id": "unit:fx:rest_board_baseline",
        "freshness": "LIVE",
        "is_stale": False,
        "trust_state": "trusted",
        "continuity_state": "rest_baseline_snapshot",
        "interpretation_bucket": "allow_structural_use",
        "semantic_runtime_wiring_status": "partial",
        "orderbook_wiring_status": "missing",
        "orderbook_active_event_count": 0,
        "orderbook_summary_slots_count": 0,
        "service_input_role": "execution_market",
        "execution_product_code": "FX_BTC_JPY",
        "execution_market_uid": "bitflyer.fx.FX_BTC_JPY",
        "read_only": True,
        "would_send_to_broker": False,
    }
    data.update(overrides)
    return data


def _service(**overrides) -> dict:
    data = {
        "contract_type": "execution_market_service_input",
        "service_input_role": "execution_market",
        "exchange": "bitflyer",
        "symbol_raw": "FX_BTC_JPY",
        "market_uid": "bitflyer.fx.FX_BTC_JPY",
        "source_kind": "market_state_preferred",
        "source_series_id": "unit:fx:rest_board_baseline",
        "freshness": "LIVE",
        "is_stale": False,
        "trust_state": "trusted",
        "continuity_state": "rest_baseline_snapshot",
        "interpretation_bucket": "allow_structural_use",
        "semantic_runtime_wiring_status": "partial",
        "orderbook_wiring_status": "missing",
        "consumer_allowed": ["workroom", "operator_ui", "autotrade", "l4_consumer"],
        "capabilities": ["market_summary_anchor", "freshness_usable", "trusted_market_state", "structural_use_allowed", "semantic_context_available"],
        "blocked_by": [],
        "warnings": ["execution_market_rest_baseline_not_continuous_ws_series", "orderbook_context_missing"],
        "read_only": True,
        "would_send_to_broker": False,
    }
    data.update(overrides)
    return data


def test_audit_marks_rest_baseline_usable_but_not_parity_complete() -> None:
    payload = app.build_sr_fx_data_lineage_parity_audit_payload(
        context=_ctx(),
        overview=_overview(),
        summary_payload=_summary(),
        service_input_payload=_service(),
    )

    assert payload["stage"] == "sr_fx_data_lineage_parity_audit_once"
    assert payload["ok"] is False
    assert payload["parity_complete"] is False
    assert payload["summary"]["execution_market_identity_ok"] is True
    assert payload["summary"]["rest_baseline_usable"] is True
    assert payload["summary"]["primary_lineage"] == "rest_baseline"
    assert payload["summary"]["continuous_ws_l3_lineage_present"] is False
    assert payload["summary"]["orderbook_context_available"] is False
    assert "sr_fx_continuous_ws_l3_lineage_missing" in payload["blocked_by"]
    assert "sr_fx_orderbook_context_missing" in payload["blocked_by"]
    assert payload["read_only"] is True
    assert payload["would_send_to_broker"] is False

    rows = {row["stage_id"]: row for row in payload["stages"]}
    assert rows["l1_public_rest_board"]["status"] == "partial"
    assert rows["l3_market_state_overview"]["status"] == "partial"
    assert rows["l4_execution_market_service_input"]["status"] == "partial"
    assert rows["l3_orderbook_semantics"]["status"] == "missing_or_blocked"


def test_audit_blocks_identity_mismatch() -> None:
    payload = app.build_sr_fx_data_lineage_parity_audit_payload(
        context=_ctx(),
        overview=_overview(symbol_raw="BTC_JPY", market_uid="bitflyer.spot.BTC_JPY"),
        summary_payload=_summary(symbol_raw="BTC_JPY", market_uid="bitflyer.spot.BTC_JPY"),
        service_input_payload=_service(),
    )

    assert payload["ok"] is False
    assert payload["summary"]["execution_market_identity_ok"] is False
    assert "sr_fx_execution_market_identity_not_consistent" in payload["blocked_by"]


def test_audit_can_mark_continuous_ws_and_orderbook_context_as_review_eligible() -> None:
    payload = app.build_sr_fx_data_lineage_parity_audit_payload(
        context=_ctx(),
        overview=_overview(continuity_state="continuous"),
        summary_payload=_summary(continuity_state="continuous", orderbook_wiring_status="partial", orderbook_active_event_count=1, orderbook_summary_slots_count=1),
        service_input_payload=_service(
            continuity_state="continuous",
            orderbook_wiring_status="partial",
            capabilities=["market_summary_anchor", "freshness_usable", "trusted_market_state", "structural_use_allowed", "semantic_context_available", "orderbook_context_available"],
            warnings=[],
        ),
    )

    assert payload["ok"] is True
    assert payload["parity_complete"] is True
    assert payload["summary"]["continuous_ws_l3_lineage_present"] is True
    assert payload["summary"]["primary_lineage"] == "continuous_ws"
    assert payload["summary"]["orderbook_context_available"] is True
    assert payload["decision"] == "eligible_for_final_human_review_before_autotrade_resume"
    rows = {row["stage_id"]: row for row in payload["stages"]}
    assert rows["l1_public_rest_board"]["status"] == "not_current_primary"
    assert rows["l1_public_rest_board"]["warnings"] == ["rest_board_not_current_primary_lineage"]


def test_audit_does_not_accept_stale_continuous_ws_as_lineage_present() -> None:
    payload = app.build_sr_fx_data_lineage_parity_audit_payload(
        context=_ctx(),
        overview=_overview(continuity_state="continuous"),
        summary_payload=_summary(
            continuity_state="continuous",
            orderbook_wiring_status="partial",
            orderbook_active_event_count=1,
            orderbook_summary_slots_count=1,
        ),
        service_input_payload=_service(
            continuity_state="continuous",
            orderbook_wiring_status="partial",
            is_stale=True,
            blocked_by=["market_summary_stale"],
            warnings=[],
        ),
    )

    assert payload["ok"] is False
    assert payload["summary"]["continuous_ws_l3_lineage_present"] is False
    assert payload["summary"]["service_stale"] is True
    assert payload["summary"]["primary_lineage"] == "continuous_ws_stale"
    assert "sr_fx_l4_service_input_blocked" in payload["blocked_by"]
    rows = {row["stage_id"]: row for row in payload["stages"]}
    assert rows["l1_public_rest_board"]["status"] == "not_current_primary"
    assert rows["l1_public_rest_board"]["warnings"] == ["rest_board_not_current_primary_lineage"]
    assert rows["l1_public_ws_board"]["blockers"] == ["continuous_ws_board_stale"]
    assert rows["l1_public_ws_executions"]["blockers"] == ["continuous_ws_executions_stale"]


def test_main_writes_read_only_audit_json(monkeypatch, tmp_path) -> None:
    class DummyConfig:
        def roots(self):
            return {"state": tmp_path / "state"}

    monkeypatch.setattr(app, "load_config", lambda: DummyConfig())
    monkeypatch.setattr(
        app,
        "build_sr_fx_data_lineage_parity_audit_payload",
        lambda: app.build_sr_fx_data_lineage_parity_audit_payload(
            context=_ctx(),
            overview=_overview(),
            summary_payload=_summary(),
            service_input_payload=_service(),
        ),
    )

    rc = app.main()
    out = tmp_path / "state" / "operator_ui" / "sr_fx_data_lineage_parity_audit.json"
    data = json.loads(out.read_text(encoding="utf-8"))

    assert rc == 0
    assert data["ok"] is False
    assert data["read_only"] is True
    assert data["would_send_to_broker"] is False
