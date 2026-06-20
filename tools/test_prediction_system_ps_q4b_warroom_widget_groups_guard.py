# path: ./tools/test_prediction_system_ps_q4b_warroom_widget_groups_guard.py
# desc: Focused guard for PS-Q4B WarRoom widget-group display packet contracts. No rendering/runtime side effects.

from __future__ import annotations

import ast
from datetime import datetime, timedelta, timezone
from pathlib import Path

from _btcts_bootstrap import ensure_btcts_on_syspath
ensure_btcts_on_syspath()

from btcts.apps.operator_ui.components.prediction_warroom_widget_groups import build_prediction_warroom_widget_group_packet_index, build_prediction_warroom_widget_group_packets
from btcts.prediction import HorizonGroup, SourceTrustState, assess_source_quality, build_prediction_system_result, build_prediction_warroom_display_packet

REPO_ROOT = Path(__file__).resolve().parents[1]
MODULE = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/components/prediction_warroom_widget_groups.py"
FORBIDDEN_IMPORT_PREFIXES = (
    "btcts.collector_vnext",
    "btcts.autotrade.execution",
    "btcts.autotrade.live_shadow",
    "streamlit",
    "requests",
    "httpx",
    "ccxt",
    "pybitflyer",
    "websocket",
)
FORBIDDEN_TOKENS = (
    "place_order(",
    "send_order(",
    "create_order(",
    "append_decision_jsonl",
    "append_command_ledger_record",
    "requests.get",
    "requests.post",
    "httpx.get",
    "httpx.post",
    "st.button",
    "st.form",
    "persist=True",
    "would_send_to_broker=True",
    "broker_execution_requested=True",
    "mode_apply_requested=True",
    "command_ledger_append_requested=True",
)
EXPECTED_GROUPS = (
    "primary_signal_widget",
    "horizon_scenario_widgets",
    "family_detail_widgets",
    "source_quality_widget",
    "evidence_ledger_widget",
    "warning_refresh_widget",
)


def _imports_from(path: Path) -> set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    imports: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imports.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imports.add(node.module)
    return imports


def _rows(now: datetime) -> list[dict[str, object]]:
    base = now - timedelta(minutes=29)
    return [{"event_ts": (base + timedelta(minutes=idx)).isoformat().replace("+00:00", "Z"), "price": 10_000_000 + idx * 1000, "size": 0.2} for idx in range(30)]


def _snapshots(now: datetime) -> list[dict[str, object]]:
    ts = now.isoformat().replace("+00:00", "Z")
    return [
        {"source_id": "bitflyer_spot_ticker", "venue": "bitFlyer", "symbol": "BTC_JPY", "price": 10_000_000, "event_ts": ts, "market_role": "bitflyer_spot"},
        {"source_id": "bitflyer_fx_ticker", "venue": "bitFlyer", "symbol": "FX_BTC_JPY", "price": 10_010_000, "event_ts": ts, "market_role": "bitflyer_fx"},
        {"source_id": "global_spot_reference", "venue": "Binance", "symbol": "BTC_JPY_REF", "price": 10_012_000, "event_ts": ts, "market_role": "reference"},
    ]


def _quality(now: datetime) -> dict[str, object]:
    ids = ("provider_source_reliability_state", "bitflyer_spot_ticker", "bitflyer_fx_ticker", "global_spot_reference", "ohlcv_5m", "ohlcv_10m", "ohlcv_15m", "ohlcv_30m")
    family_by_id = {
        "provider_source_reliability_state": "bf_spot_source_quality",
        "bitflyer_spot_ticker": "bitflyer_spot",
        "bitflyer_fx_ticker": "bitflyer_fx",
        "global_spot_reference": "binance_spot_reference",
        "ohlcv_5m": "bf_spot_ohlcv",
        "ohlcv_10m": "bf_spot_ohlcv",
        "ohlcv_15m": "bf_spot_ohlcv",
        "ohlcv_30m": "bf_spot_ohlcv",
    }
    return {
        source_id: assess_source_quality(source_id=source_id, source_family=family_by_id[source_id], latest_event_ts=now.isoformat().replace("+00:00", "Z"), now=now, max_age_sec=300.0, trust_state=SourceTrustState.TRUSTED)
        for source_id in ids
    }


def _display_packet():
    now = datetime(2026, 6, 20, 0, 0, 0, tzinfo=timezone.utc)
    result = build_prediction_system_result(rows=_rows(now), venue_snapshots=_snapshots(now), source_quality_by_id=_quality(now), requested_horizon_groups=(HorizonGroup.SHORT_HORIZON,), now=now)
    return build_prediction_warroom_display_packet(result)


def test_ps_q4b_static_boundaries_and_markers() -> None:
    text = MODULE.read_text(encoding="utf-8")
    imports = _imports_from(MODULE)
    for prefix in FORBIDDEN_IMPORT_PREFIXES:
        assert not any(item == prefix or item.startswith(prefix + ".") for item in imports), prefix
    for token in FORBIDDEN_TOKENS:
        assert token not in text, token
    assert "prediction_warroom_widget_groups.ps_q4b.v1" in text
    assert "PredictionWarRoomWidgetGroupPacket" in text
    assert "build_prediction_warroom_widget_group_packets" in text
    assert "build_prediction_warroom_widget_group_packet_index" in text
    assert "independent_refresh_allowed" in text
    assert "not_loaded_as_runtime_display_source" in text


def test_ps_q4b_widget_group_index_has_expected_groups_and_refresh_metadata() -> None:
    index = build_prediction_warroom_widget_group_packet_index(_display_packet())
    assert index["index_version"] == "prediction_warroom_widget_groups.ps_q4b.v1"
    assert tuple(index["widget_group_order"]) == EXPECTED_GROUPS
    assert index["widget_group_count"] == len(EXPECTED_GROUPS)
    assert len(index["auto_refresh_groups"]) == len(EXPECTED_GROUPS)
    for item in index["auto_refresh_groups"]:
        assert item["refresh_group_id"].startswith("prediction_warroom:")
        assert int(item["refresh_interval_sec"]) > 0
        assert item["independent_refresh_allowed"] is True
        assert item["data_dependencies"]
    assert index["display_only"] is True
    assert index["render_intent_only"] is True
    assert index["not_loaded_as_runtime_display_source"] is True


def test_ps_q4b_widget_group_payloads_are_separated_for_future_widgets() -> None:
    groups = [item.to_dict() for item in build_prediction_warroom_widget_group_packets(_display_packet())]
    by_id = {item["widget_group_id"]: item for item in groups}
    assert by_id["primary_signal_widget"]["payload"]["primary_signal_summary"]["summary_version"] == "prediction_signal_strength_bands.ps_q3c.v1"
    assert by_id["horizon_scenario_widgets"]["payload"]["horizon_cards_by_group"]
    assert by_id["family_detail_widgets"]["payload"]["family_cards_by_family"]
    assert by_id["source_quality_widget"]["payload"]["source_quality_panel"]["tier0_source_quality_gate"]["gate_state"] == "passed"
    assert by_id["evidence_ledger_widget"]["payload"]["source_contribution_ledger_count"] > 0
    assert "warning_panel" in by_id["warning_refresh_widget"]["payload"]
    for item in groups:
        assert item["read_only"] is True
        assert item["non_executing"] is True
        assert item["display_only"] is True
        assert item["would_send_to_broker"] is False
        assert item["broker_execution_requested"] is False
        assert item["mode_apply_requested"] is False
        assert item["command_ledger_append_requested"] is False
        assert item["approval_append_requested"] is False


def main() -> int:
    test_ps_q4b_static_boundaries_and_markers()
    test_ps_q4b_widget_group_index_has_expected_groups_and_refresh_metadata()
    test_ps_q4b_widget_group_payloads_are_separated_for_future_widgets()
    print("[OK] Prediction System PS-Q4B WarRoom widget groups guard passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
