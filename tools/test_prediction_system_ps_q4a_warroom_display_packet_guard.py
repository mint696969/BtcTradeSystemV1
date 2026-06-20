# path: ./tools/test_prediction_system_ps_q4a_warroom_display_packet_guard.py
# desc: Focused guard for PS-Q4A WarRoom display packet contract. Display-only, no UI/runtime/AutoTrade side effects.

from __future__ import annotations

import ast
from datetime import datetime, timedelta, timezone
from pathlib import Path

from _btcts_bootstrap import ensure_btcts_on_syspath
ensure_btcts_on_syspath()

from btcts.prediction import HorizonGroup, SourceTrustState, assess_source_quality, build_prediction_system_result, build_prediction_warroom_display_packet

REPO_ROOT = Path(__file__).resolve().parents[1]
MODULE = REPO_ROOT / "btcts_next/src/btcts/prediction/warroom_display_packet.py"
INIT = REPO_ROOT / "btcts_next/src/btcts/prediction/__init__.py"
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
    return [
        {"event_ts": (base + timedelta(minutes=idx)).isoformat().replace("+00:00", "Z"), "price": 10_000_000 + idx * 1000, "size": 0.2}
        for idx in range(30)
    ]


def _snapshots(now: datetime) -> list[dict[str, object]]:
    ts = now.isoformat().replace("+00:00", "Z")
    return [
        {"source_id": "bitflyer_spot_ticker", "venue": "bitFlyer", "symbol": "BTC_JPY", "price": 10_000_000, "event_ts": ts, "market_role": "bitflyer_spot"},
        {"source_id": "bitflyer_fx_ticker", "venue": "bitFlyer", "symbol": "FX_BTC_JPY", "price": 10_010_000, "event_ts": ts, "market_role": "bitflyer_fx"},
        {"source_id": "global_spot_reference", "venue": "Binance", "symbol": "BTC_JPY_REF", "price": 10_012_000, "event_ts": ts, "market_role": "reference"},
    ]


def _quality(now: datetime, *, stale_spot: bool = False) -> dict[str, object]:
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
    out = {
        source_id: assess_source_quality(source_id=source_id, source_family=family_by_id[source_id], latest_event_ts=now.isoformat().replace("+00:00", "Z"), now=now, max_age_sec=300.0, trust_state=SourceTrustState.TRUSTED)
        for source_id in ids
    }
    if stale_spot:
        stale = now - timedelta(minutes=10)
        out["bitflyer_spot_ticker"] = assess_source_quality(source_id="bitflyer_spot_ticker", source_family="bitflyer_spot", latest_event_ts=stale.isoformat().replace("+00:00", "Z"), now=now, max_age_sec=30.0, trust_state=SourceTrustState.TRUSTED)
    return out


def _result(stale_spot: bool = False):
    now = datetime(2026, 6, 20, 0, 0, 0, tzinfo=timezone.utc)
    return build_prediction_system_result(rows=_rows(now), venue_snapshots=_snapshots(now), source_quality_by_id=_quality(now, stale_spot=stale_spot), requested_horizon_groups=(HorizonGroup.SHORT_HORIZON,), now=now)


def test_ps_q4a_static_boundaries_exports_and_markers() -> None:
    text = MODULE.read_text(encoding="utf-8")
    init_text = INIT.read_text(encoding="utf-8")
    imports = _imports_from(MODULE)
    for prefix in FORBIDDEN_IMPORT_PREFIXES:
        assert not any(item == prefix or item.startswith(prefix + ".") for item in imports), prefix
    for token in FORBIDDEN_TOKENS:
        assert token not in text, token
    assert "prediction_warroom_display_packet.ps_q4a.v1" in text
    assert "PredictionWarRoomDisplayPacket" in text
    assert "build_prediction_warroom_display_packet" in text
    assert "not_loaded_as_runtime_display_source" in text
    assert "PredictionWarRoomDisplayPacket" in init_text
    assert "build_prediction_warroom_display_packet" in init_text


def test_ps_q4a_packet_contains_warroom_display_sections_and_q3c_signal_summary() -> None:
    packet = build_prediction_warroom_display_packet(_result()).to_dict()
    assert packet["packet_version"] == "prediction_warroom_display_packet.ps_q4a.v1"
    assert packet["read_only"] is True
    assert packet["non_executing"] is True
    assert packet["ui_contract"]["intended_consumer"] == "WarRoom"
    assert packet["ui_contract"]["display_only"] is True
    assert packet["ui_contract"]["trigger_buttons_allowed"] is False
    assert packet["boundaries"]["not_loaded_as_runtime_display_source"] is True
    assert packet["primary_signal_summary"]["summary_version"] == "prediction_signal_strength_bands.ps_q3c.v1"
    assert packet["horizon_cards"]
    assert packet["family_cards"]
    assert packet["source_quality_panel"]["tier0_source_quality_gate"]["gate_state"] == "passed"
    assert packet["evidence_panel"]["source_contribution_ledger_count"] > 0
    assert any(card["source_contribution_ledger"] for card in packet["family_cards"])
    assert any(card["context_profile_source_caps"] for card in packet["family_cards"])


def test_ps_q4a_packet_preserves_blocked_signal_and_never_enables_execution() -> None:
    packet = build_prediction_warroom_display_packet(_result(stale_spot=True)).to_dict()
    assert int(packet["primary_signal_summary"]["estimated_signal_strength_percent"]) <= 24
    assert packet["source_quality_panel"]["tier0_source_quality_gate"]["gate_state"] == "blocked"
    assert "tier0_source_quality_blocked" in packet["warning_panel"]["signal_strength_cap_reasons"]
    assert packet["would_send_to_broker"] is False
    assert packet["broker_execution_requested"] is False
    assert packet["mode_apply_requested"] is False
    assert packet["command_ledger_append_requested"] is False
    assert packet["approval_append_requested"] is False
    assert packet["boundaries"]["would_write_runtime_artifact"] is False
    assert packet["boundaries"]["autotrade_trigger_enabled"] is False


def main() -> int:
    test_ps_q4a_static_boundaries_exports_and_markers()
    test_ps_q4a_packet_contains_warroom_display_sections_and_q3c_signal_summary()
    test_ps_q4a_packet_preserves_blocked_signal_and_never_enables_execution()
    print("[OK] Prediction System PS-Q4A WarRoom display packet guard passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
