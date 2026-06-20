# path: ./tools/test_prediction_system_ps_q2c_context_evidence_profiles_guard.py
# desc: Focused guard for PS-Q2C context-specific evidence profile use in Prediction System horizon/scenario interpretation.

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
        {"source_id": "bf_spot", "venue": "bitFlyer", "symbol": "BTC_JPY", "price": 10_000_000, "event_ts": ts, "market_role": "bitflyer_spot"},
        {"source_id": "bf_fx", "venue": "bitFlyer", "symbol": "FX_BTC_JPY", "price": 10_010_000, "event_ts": ts, "market_role": "bitflyer_fx"},
        {"source_id": "binance_spot", "venue": "Binance", "symbol": "BTC_JPY_REF", "price": 10_012_000, "event_ts": ts, "market_role": "reference"},
    ]


def test_ps_q2c_static_boundaries_and_markers() -> None:
    text = SYSTEM.read_text(encoding="utf-8")
    imports = _imports_from(SYSTEM)
    for prefix in FORBIDDEN_IMPORT_PREFIXES:
        assert not any(item == prefix or item.startswith(prefix + ".") for item in imports), prefix
    for token in FORBIDDEN_TOKENS:
        assert token not in text, token
    assert "_context_evidence_profile_packets" in text
    assert "context_evidence_profile_minimum_sources_missing" in text
    assert "selected_context_evidence_profile_ids" in text
    assert "context_evidence_profiles" in text
    assert "context_profile_signal_strength_cap_reasons" in text


def test_ps_q2c_missing_profile_sources_affect_horizon_and_scenario() -> None:
    now = datetime(2026, 6, 20, 0, 0, 0, tzinfo=timezone.utc)
    result = build_prediction_system_result(requested_horizon_groups=(HorizonGroup.SHORT_HORIZON,), now=now)
    data = result.to_dict()
    outlook = data["scenario_core"]["outlooks"][0]
    digest = outlook["gpt_review_digest"]
    profiles = digest["context_evidence_profiles"]
    profile_ids = {item["evidence_profile_id"] for item in profiles}
    assert "trend_short_horizon_v1" in profile_ids
    assert "reversal_now_short_v1" in profile_ids
    assert any(item["missing_minimum_required_sources"] for item in profiles)
    assert "context_evidence_profile_minimum_sources_missing" in outlook["warnings"]
    assert outlook["caution_level"] in {"blocked", "high"}
    assert digest["context_profile_signal_strength_cap_reasons"] == ["context_evidence_profile_minimum_sources_missing"]
    assert data["scenario_core"]["scenario_trace"]["context_evidence_profiles"]
    assert "context_evidence_profile_minimum_sources_missing" in data["scenario_core"]["warnings"]
    assert data["gpt_review_digest"]["context_evidence_profile_version"] == "prediction_evidence_profiles.ps_q2.v1"
    assert data["gpt_review_digest"]["selected_context_evidence_profile_ids"]


def test_ps_q2c_supplied_sources_reduce_profile_missing_sources_but_keep_unavailable_context_visible() -> None:
    now = datetime(2026, 6, 20, 0, 0, 0, tzinfo=timezone.utc)
    q = {
        "bf_spot": assess_source_quality(source_id="bf_spot", source_family="bitflyer_spot", latest_event_ts=now.isoformat().replace("+00:00", "Z"), now=now, trust_state=SourceTrustState.TRUSTED),
        "bf_fx": assess_source_quality(source_id="bf_fx", source_family="bitflyer_fx", latest_event_ts=now.isoformat().replace("+00:00", "Z"), now=now, trust_state=SourceTrustState.TRUSTED),
    }
    result = build_prediction_system_result(
        rows=_rows(now),
        venue_snapshots=_snapshots(now),
        source_quality_by_id=q,
        requested_horizon_groups=(HorizonGroup.SHORT_HORIZON,),
        now=now,
    )
    data = result.to_dict()
    profiles = data["scenario_core"]["outlooks"][0]["gpt_review_digest"]["context_evidence_profiles"]
    trend = next(item for item in profiles if item["evidence_profile_id"] == "trend_short_horizon_v1")
    reversal = next(item for item in profiles if item["evidence_profile_id"] == "reversal_now_short_v1")
    assert "ohlcv_5m" in trend["observed_minimum_required_sources"]
    assert "ohlcv_10m" in trend["observed_minimum_required_sources"]
    assert "bitflyer_trades" in trend["missing_minimum_required_sources"]
    assert "bitflyer_board_summary" in reversal["missing_minimum_required_sources"]
    assert data["scenario_core"]["scenario_trace"]["context_evidence_profiles"]
    outlook = data["scenario_core"]["outlooks"][0]
    assert "context_evidence_profile_minimum_sources_missing" in outlook["warnings"]
    assert outlook["caution_level"] == "high"
    assert data["read_only"] is True
    assert data["non_executing"] is True
    assert data["would_send_to_broker"] is False
    assert data["broker_execution_requested"] is False
    assert data["mode_apply_requested"] is False
    assert data["command_ledger_append_requested"] is False


def main() -> int:
    test_ps_q2c_static_boundaries_and_markers()
    test_ps_q2c_missing_profile_sources_affect_horizon_and_scenario()
    test_ps_q2c_supplied_sources_reduce_profile_missing_sources_but_keep_unavailable_context_visible()
    print("[OK] Prediction System PS-Q2C context evidence profiles guard passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
