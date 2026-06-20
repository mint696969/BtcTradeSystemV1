# path: ./tools/test_prediction_system_ps_q3b_profile_family_source_caps_guard.py
# desc: Focused guard for PS-Q3B profile/family-specific minimum-source caps and source contribution ledger entries.

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
PROFILE_TARGET_FAMILIES = {
    "trend_bias",
    "market_regime",
    "human_technical_structure",
    "cross_venue_confirmation",
    "reversal_zone",
    "volatility_risk",
    "breakout_false_break",
    "algorithmic_participant_footprint",
}
NON_TARGET_FAMILIES = {"liquidity_execution_quality", "opportunity_participation", "macro_risk_context"}


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


def _quality(now: datetime) -> dict[str, object]:
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
    return {
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


def _ledger_has_q3b(values: dict[str, object]) -> bool:
    return any(isinstance(item, dict) and item.get("ledger_version") == "prediction_source_contribution_ledger.ps_q3b.v1" for item in values.get("source_contribution_ledger", []))


def test_ps_q3b_static_boundaries_and_markers() -> None:
    text = SYSTEM.read_text(encoding="utf-8")
    imports = _imports_from(SYSTEM)
    for prefix in FORBIDDEN_IMPORT_PREFIXES:
        assert not any(item == prefix or item.startswith(prefix + ".") for item in imports), prefix
    for token in FORBIDDEN_TOKENS:
        assert token not in text, token
    assert "_apply_context_profile_source_caps_to_outputs" in text
    assert "prediction_source_contribution_ledger.ps_q3b.v1" in text
    assert "context_profile_family_minimum_sources_missing" in text
    assert "context_profile_source_caps" in text


def test_ps_q3b_profile_missing_sources_cap_only_matching_families_when_tier0_passes() -> None:
    now = datetime(2026, 6, 20, 0, 0, 0, tzinfo=timezone.utc)
    result = build_prediction_system_result(
        rows=_rows(now),
        venue_snapshots=_snapshots(now),
        source_quality_by_id=_quality(now),
        requested_horizon_groups=(HorizonGroup.SHORT_HORIZON,),
        now=now,
    )
    data = result.to_dict()
    assert data["gpt_review_digest"]["tier0_source_quality_gate_state"] == "passed"
    target_outputs = [item for item in data["outputs"] if item["family"] in PROFILE_TARGET_FAMILIES and item["score"] is not None]
    non_target_outputs = [item for item in data["outputs"] if item["family"] in NON_TARGET_FAMILIES and item["score"] is not None]
    assert target_outputs
    assert non_target_outputs
    assert any(item["values"].get("context_profile_source_caps") for item in target_outputs)
    assert all(int(item["values"]["estimated_signal_strength_percent"]) <= 59 for item in target_outputs)
    assert all(_ledger_has_q3b(item["values"]) for item in target_outputs)
    assert all("context_profile_family_minimum_sources_missing" in item["warnings"] for item in target_outputs)
    assert all(not item["values"].get("context_profile_source_caps") for item in non_target_outputs)
    assert all(not _ledger_has_q3b(item["values"]) for item in non_target_outputs)


def test_ps_q3b_keeps_tier0_hard_block_as_stronger_global_cap() -> None:
    now = datetime(2026, 6, 20, 0, 0, 0, tzinfo=timezone.utc)
    stale = now - timedelta(minutes=10)
    q = _quality(now)
    q["bitflyer_spot_ticker"] = assess_source_quality(source_id="bitflyer_spot_ticker", source_family="bitflyer_spot", latest_event_ts=stale.isoformat().replace("+00:00", "Z"), now=now, max_age_sec=30.0, trust_state=SourceTrustState.TRUSTED)
    result = build_prediction_system_result(
        rows=_rows(now),
        venue_snapshots=_snapshots(now),
        source_quality_by_id=q,
        requested_horizon_groups=(HorizonGroup.SHORT_HORIZON,),
        now=now,
    )
    data = result.to_dict()
    assert data["gpt_review_digest"]["tier0_source_quality_gate_state"] == "blocked"
    scored = [item for item in data["outputs"] if item["score"] is not None]
    assert scored
    assert all(float(item["score"]) <= 0.24 for item in scored)
    assert all(int(item["values"]["estimated_signal_strength_percent"]) <= 24 for item in scored)
    target_outputs = [item for item in scored if item["family"] in PROFILE_TARGET_FAMILIES]
    assert target_outputs
    assert any(_ledger_has_q3b(item["values"]) for item in target_outputs)
    assert data["read_only"] is True
    assert data["non_executing"] is True
    assert data["would_send_to_broker"] is False
    assert data["broker_execution_requested"] is False
    assert data["mode_apply_requested"] is False
    assert data["command_ledger_append_requested"] is False


def main() -> int:
    test_ps_q3b_static_boundaries_and_markers()
    test_ps_q3b_profile_missing_sources_cap_only_matching_families_when_tier0_passes()
    test_ps_q3b_keeps_tier0_hard_block_as_stronger_global_cap()
    print("[OK] Prediction System PS-Q3B profile/family source caps guard passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
