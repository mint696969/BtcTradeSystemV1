# path: ./tools/test_prediction_system_ps_q2d_tier0_source_quality_gate_guard.py
# desc: Focused guard for PS-Q2D/PS-Q3-entry Tier 0 source quality/freshness gate effects.

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


def test_ps_q2d_static_boundaries_and_markers() -> None:
    text = SYSTEM.read_text(encoding="utf-8")
    imports = _imports_from(SYSTEM)
    for prefix in FORBIDDEN_IMPORT_PREFIXES:
        assert not any(item == prefix or item.startswith(prefix + ".") for item in imports), prefix
    for token in FORBIDDEN_TOKENS:
        assert token not in text, token
    assert "_tier0_source_quality_gate_summary" in text
    assert "tier0_source_quality_gate_not_passed" in text
    assert "tier0_source_quality_gate" in text
    assert "tier0_source_quality_blocked" in text
    assert "tier0_source_quality_missing_or_degraded" in text


def test_ps_q2d_missing_quality_status_caps_context_even_with_runtime_inputs() -> None:
    now = datetime(2026, 6, 20, 0, 0, 0, tzinfo=timezone.utc)
    result = build_prediction_system_result(
        rows=_rows(now),
        venue_snapshots=_snapshots(now),
        requested_horizon_groups=(HorizonGroup.SHORT_HORIZON,),
        now=now,
    )
    data = result.to_dict()
    tier0 = data["gpt_review_digest"]["tier0_source_quality_gate"]
    assert tier0["gate_state"] == "warning_context_only"
    assert tier0["signal_strength_cap_reason"] == "tier0_source_quality_missing_or_degraded"
    assert tier0["missing_quality_status_source_ids"]
    assert "tier0_source_quality_status_missing" in data["scenario_core"]["warnings"]
    assert data["scenario_core"]["scenario_trace"]["tier0_source_quality_gate"]["gate_state"] == "warning_context_only"
    assert data["gpt_review_digest"]["tier0_source_quality_gate_state"] == "warning_context_only"
    assert data["gpt_review_digest"]["tier0_source_quality_signal_strength_cap_reason"] == "tier0_source_quality_missing_or_degraded"


def test_ps_q2d_stale_or_untrusted_quality_blocks_tier0_gate() -> None:
    now = datetime(2026, 6, 20, 0, 0, 0, tzinfo=timezone.utc)
    stale = now - timedelta(minutes=10)
    q = {
        "bf_spot": assess_source_quality(source_id="bf_spot", source_family="bitflyer_spot", latest_event_ts=stale.isoformat().replace("+00:00", "Z"), now=now, max_age_sec=30.0, trust_state=SourceTrustState.TRUSTED),
        "bf_fx": assess_source_quality(source_id="bf_fx", source_family="bitflyer_fx", latest_event_ts=now.isoformat().replace("+00:00", "Z"), now=now, trust_state=SourceTrustState.UNTRUSTED),
    }
    result = build_prediction_system_result(
        rows=_rows(now),
        venue_snapshots=_snapshots(now),
        source_quality_by_id=q,
        requested_horizon_groups=(HorizonGroup.SHORT_HORIZON,),
        now=now,
    )
    data = result.to_dict()
    tier0 = data["gpt_review_digest"]["tier0_source_quality_gate"]
    assert tier0["gate_state"] == "blocked"
    assert tier0["signal_strength_cap_reason"] == "tier0_source_quality_blocked"
    assert "bf_spot" in tier0["blocked_source_ids"]
    assert "bf_fx" in tier0["blocked_source_ids"]
    assert "source_stale" in tier0["blockers"]
    assert "source_not_trusted" in tier0["blockers"]
    assert "tier0_source_quality_blocked_sources_present" in data["scenario_core"]["warnings"]
    assert data["scenario_core"]["scenario_trace"]["tier0_source_quality_gate"]["gate_state"] == "blocked"
    assert data["read_only"] is True
    assert data["non_executing"] is True
    assert data["would_send_to_broker"] is False
    assert data["broker_execution_requested"] is False
    assert data["mode_apply_requested"] is False
    assert data["command_ledger_append_requested"] is False


def main() -> int:
    test_ps_q2d_static_boundaries_and_markers()
    test_ps_q2d_missing_quality_status_caps_context_even_with_runtime_inputs()
    test_ps_q2d_stale_or_untrusted_quality_blocks_tier0_gate()
    print("[OK] Prediction System PS-Q2D Tier 0 source quality gate guard passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
