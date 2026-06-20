# path: ./tools/test_prediction_system_ps_q3c_signal_strength_bands_guard.py
# desc: Focused guard for PS-Q3C WarRoom-ready signal strength band summaries.

from __future__ import annotations

import ast
from datetime import datetime, timedelta, timezone
from pathlib import Path

from _btcts_bootstrap import ensure_btcts_on_syspath
ensure_btcts_on_syspath()

from btcts.prediction import HorizonGroup, SourceTrustState, assess_source_quality, build_prediction_system_result

REPO_ROOT = Path(__file__).resolve().parents[1]
SYSTEM = REPO_ROOT / "btcts_next/src/btcts/prediction/system.py"
FORBIDDEN_IMPORT_PREFIXES = (
    "btcts.collector_vnext",
    "btcts.autotrade.execution",
    "btcts.autotrade.live_shadow",
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
    ids = (
        "provider_source_reliability_state",
        "bitflyer_spot_ticker",
        "bitflyer_fx_ticker",
        "global_spot_reference",
        "ohlcv_5m",
        "ohlcv_10m",
        "ohlcv_15m",
        "ohlcv_30m",
    )
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
        source_id: assess_source_quality(
            source_id=source_id,
            source_family=family_by_id[source_id],
            latest_event_ts=now.isoformat().replace("+00:00", "Z"),
            now=now,
            max_age_sec=300.0,
            trust_state=SourceTrustState.TRUSTED,
        )
        for source_id in ids
    }
    if stale_spot:
        stale = now - timedelta(minutes=10)
        out["bitflyer_spot_ticker"] = assess_source_quality(
            source_id="bitflyer_spot_ticker",
            source_family="bitflyer_spot",
            latest_event_ts=stale.isoformat().replace("+00:00", "Z"),
            now=now,
            max_age_sec=30.0,
            trust_state=SourceTrustState.TRUSTED,
        )
    return out


def test_ps_q3c_static_boundaries_and_markers() -> None:
    text = SYSTEM.read_text(encoding="utf-8")
    imports = _imports_from(SYSTEM)
    for prefix in FORBIDDEN_IMPORT_PREFIXES:
        assert not any(item == prefix or item.startswith(prefix + ".") for item in imports), prefix
    for token in FORBIDDEN_TOKENS:
        assert token not in text, token
    assert "prediction_signal_strength_bands.ps_q3c.v1" in text
    assert "_signal_strength_summary_from_outputs" in text
    assert "_scenario_signal_strength_summary_from_outlooks" in text
    assert "signal_strength_band_label_ja" in text
    assert "estimated_reference_hit_rate_percent" in text


def test_ps_q3c_horizon_and_top_level_signal_summary_exists_and_never_uses_100() -> None:
    now = datetime(2026, 6, 20, 0, 0, 0, tzinfo=timezone.utc)
    result = build_prediction_system_result(
        rows=_rows(now),
        venue_snapshots=_snapshots(now),
        source_quality_by_id=_quality(now),
        requested_horizon_groups=(HorizonGroup.SHORT_HORIZON,),
        now=now,
    )
    data = result.to_dict()
    top = data["gpt_review_digest"]["signal_strength_summary"]
    assert top["summary_version"] == "prediction_signal_strength_bands.ps_q3c.v1"
    assert 0 <= int(top["estimated_signal_strength_percent"]) <= 99
    assert int(top["estimated_signal_strength_percent"]) != 100
    assert top["signal_strength_band"] in {
        "unavailable",
        "very_low_reference",
        "low_reference",
        "useful_reference",
        "strong_reference",
        "very_strong_reference",
        "maximum_reference_not_certainty",
    }
    outlook = data["scenario_core"]["outlooks"][0]
    horizon_summary = outlook["gpt_review_digest"]["signal_strength_summary"]
    assert horizon_summary["summary_version"] == "prediction_signal_strength_bands.ps_q3c.v1"
    assert horizon_summary["family_breakdown"]
    assert int(horizon_summary["estimated_signal_strength_percent"]) <= 99
    assert horizon_summary["signal_strength_band_label_ja"]
    assert "context_profile_family_minimum_sources_missing" in horizon_summary["signal_strength_cap_reasons"]


def test_ps_q3c_tier0_blocked_caps_top_and_horizon_signal_to_very_low() -> None:
    now = datetime(2026, 6, 20, 0, 0, 0, tzinfo=timezone.utc)
    result = build_prediction_system_result(
        rows=_rows(now),
        venue_snapshots=_snapshots(now),
        source_quality_by_id=_quality(now, stale_spot=True),
        requested_horizon_groups=(HorizonGroup.SHORT_HORIZON,),
        now=now,
    )
    data = result.to_dict()
    top = data["gpt_review_digest"]["signal_strength_summary"]
    assert int(top["estimated_signal_strength_percent"]) <= 24
    assert top["signal_strength_band"] in {"very_low_reference", "unavailable"}
    assert "tier0_source_quality_blocked" in top["signal_strength_cap_reasons"]
    horizon_summary = data["scenario_core"]["outlooks"][0]["gpt_review_digest"]["signal_strength_summary"]
    assert int(horizon_summary["estimated_signal_strength_percent"]) <= 24
    assert horizon_summary["capped_family_count"] > 0
    assert data["read_only"] is True
    assert data["non_executing"] is True
    assert data["would_send_to_broker"] is False
    assert data["broker_execution_requested"] is False
    assert data["mode_apply_requested"] is False
    assert data["command_ledger_append_requested"] is False


def main() -> int:
    test_ps_q3c_static_boundaries_and_markers()
    test_ps_q3c_horizon_and_top_level_signal_summary_exists_and_never_uses_100()
    test_ps_q3c_tier0_blocked_caps_top_and_horizon_signal_to_very_low()
    print("[OK] Prediction System PS-Q3C signal strength bands guard passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
