# path: ./tools/test_prediction_system_ps_q4c_l4_latest_adapter_contract_guard.py
# desc: Focused guard for PS-Q4C L4/latest adapter contract boundary. No hot file load, runtime write, rendering, Collector, AutoTrade, or broker behavior.

from __future__ import annotations

import ast
from datetime import datetime, timedelta, timezone
from pathlib import Path

from _btcts_bootstrap import ensure_btcts_on_syspath
ensure_btcts_on_syspath()

from btcts.apps.operator_ui.components.prediction_warroom_l4_latest_adapter import (
    build_prediction_warroom_l4_latest_adapter_contract,
    build_prediction_warroom_l4_latest_expected_artifacts,
)
from btcts.prediction import HorizonGroup, SourceTrustState, assess_source_quality, build_prediction_system_result, build_prediction_warroom_display_packet

REPO_ROOT = Path(__file__).resolve().parents[1]
MODULE = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/components/prediction_warroom_l4_latest_adapter.py"
FORBIDDEN_IMPORT_PREFIXES = (
    "btcts.collector_vnext",
    "btcts.autotrade.execution",
    "btcts.autotrade.live_shadow",
    "btcts.processing.l4_consumer_models.shared.prediction_system_input",
    "streamlit",
    "requests",
    "httpx",
    "ccxt",
    "pybitflyer",
    "websocket",
)
FORBIDDEN_TOKENS = (
    "open(",
    "Path.read_text",
    "json.load",
    "json.loads",
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
    "would_load_hot_latest_artifacts=True",
    "would_read_runtime_file=True",
    "would_write_runtime_artifact=True",
    "would_send_to_broker=True",
    "broker_execution_requested=True",
    "mode_apply_requested=True",
    "command_ledger_append_requested=True",
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
    return {source_id: assess_source_quality(source_id=source_id, source_family=family_by_id[source_id], latest_event_ts=now.isoformat().replace("+00:00", "Z"), now=now, max_age_sec=300.0, trust_state=SourceTrustState.TRUSTED) for source_id in ids}


def _display_packet():
    now = datetime(2026, 6, 20, 0, 0, 0, tzinfo=timezone.utc)
    result = build_prediction_system_result(rows=_rows(now), venue_snapshots=_snapshots(now), source_quality_by_id=_quality(now), requested_horizon_groups=(HorizonGroup.SHORT_HORIZON,), now=now)
    return build_prediction_warroom_display_packet(result)


def test_ps_q4c_static_boundaries_and_markers() -> None:
    text = MODULE.read_text(encoding="utf-8")
    imports = _imports_from(MODULE)
    for prefix in FORBIDDEN_IMPORT_PREFIXES:
        assert not any(item == prefix or item.startswith(prefix + ".") for item in imports), prefix
    for token in FORBIDDEN_TOKENS:
        assert token not in text, token
    assert "prediction_warroom_l4_latest_adapter.ps_q4c.v1" in text
    assert "PredictionWarRoomL4LatestAdapterPacket" in text
    assert "build_prediction_warroom_l4_latest_adapter_contract" in text
    assert "build_prediction_warroom_l4_latest_expected_artifacts" in text
    assert "D:\\\\btc_ts_hot" in text
    assert "would_load_hot_latest_artifacts" in text
    assert "would_read_runtime_file" in text


def test_ps_q4c_expected_artifacts_are_hot_root_hints_only_not_loaded() -> None:
    refs = [item.to_dict() for item in build_prediction_warroom_l4_latest_expected_artifacts()]
    roles = {item["artifact_role"] for item in refs}
    assert "prediction_system_result_snapshot" in roles
    assert "prediction_warroom_display_packet" in roles
    assert "prediction_warroom_widget_group_index" in roles
    assert "prediction_source_quality_snapshot" in roles
    assert all(str(item["expected_path_hint"]).startswith("D:\\btc_ts_hot") for item in refs)
    assert all(item["read_by_this_adapter"] is False for item in refs)
    assert all(item["loaded_in_this_slice"] is False for item in refs)


def test_ps_q4c_contract_builds_widget_index_from_supplied_display_packet_without_loading_runtime() -> None:
    packet = build_prediction_warroom_l4_latest_adapter_contract(display_packet=_display_packet()).to_dict()
    assert packet["adapter_version"] == "prediction_warroom_l4_latest_adapter.ps_q4c.v1"
    assert packet["adapter_state"] == "display_packet_supplied_widget_index_ready"
    assert packet["hot_latest_root_hint"] == "D:\\btc_ts_hot"
    assert packet["display_packet_available"] is True
    assert packet["widget_group_index_available"] is True
    assert packet["widget_group_count"] == 6
    assert packet["widget_group_order"] == [
        "primary_signal_widget",
        "horizon_scenario_widgets",
        "family_detail_widgets",
        "source_quality_widget",
        "evidence_ledger_widget",
        "warning_refresh_widget",
    ]
    assert packet["handoff_summary"]["auto_refresh_ready_for_contract"] is True
    assert packet["read_only"] is True
    assert packet["non_executing"] is True
    assert packet["dry_run"] is True
    assert packet["contract_only"] is True
    assert packet["would_load_hot_latest_artifacts"] is False
    assert packet["would_read_runtime_file"] is False
    assert packet["would_write_runtime_artifact"] is False
    assert packet["would_send_to_broker"] is False
    assert packet["broker_execution_requested"] is False
    assert packet["mode_apply_requested"] is False
    assert packet["command_ledger_append_requested"] is False


def test_ps_q4c_contract_without_payload_waits_for_latest_adapter_loader() -> None:
    packet = build_prediction_warroom_l4_latest_adapter_contract().to_dict()
    assert packet["adapter_state"] == "contract_only_waiting_for_latest_payload"
    assert packet["display_packet_available"] is False
    assert packet["widget_group_index_available"] is False
    assert packet["widget_group_count"] == 0
    assert packet["handoff_summary"]["future_loader_required"] is True
    assert packet["handoff_summary"]["loaded_in_this_slice"] is False
    assert packet["boundaries"]["would_load_hot_latest_artifacts"] is False
    assert packet["boundaries"]["would_read_runtime_file"] is False


def main() -> int:
    test_ps_q4c_static_boundaries_and_markers()
    test_ps_q4c_expected_artifacts_are_hot_root_hints_only_not_loaded()
    test_ps_q4c_contract_builds_widget_index_from_supplied_display_packet_without_loading_runtime()
    test_ps_q4c_contract_without_payload_waits_for_latest_adapter_loader()
    print("[OK] Prediction System PS-Q4C L4/latest adapter contract guard passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
