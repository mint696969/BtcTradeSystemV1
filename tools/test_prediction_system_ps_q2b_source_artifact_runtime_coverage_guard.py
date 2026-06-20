# path: ./tools/test_prediction_system_ps_q2b_source_artifact_runtime_coverage_guard.py
# desc: Focused guard for PS-Q2B runtime input coverage use in Prediction System. Non-collecting, non-executing.

from __future__ import annotations

import ast
from datetime import datetime, timedelta, timezone
from pathlib import Path

from _btcts_bootstrap import ensure_btcts_on_syspath
ensure_btcts_on_syspath()

from btcts.prediction import HorizonGroup, SourceTrustState, assess_source_quality, build_prediction_system_result, build_source_artifact_coverage_report

REPO_ROOT = Path(__file__).resolve().parents[1]
SYSTEM = REPO_ROOT / "btcts_next/src/btcts/prediction/system.py"
COVERAGE = REPO_ROOT / "btcts_next/src/btcts/prediction/source_artifact_coverage.py"
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
    "runtime_collection_allowed=True",
    "collector_runtime_import_allowed=True",
    "broker_or_autotrade_allowed=True",
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


def test_ps_q2b_static_boundaries_and_markers() -> None:
    text = SYSTEM.read_text(encoding="utf-8") + "\n" + COVERAGE.read_text(encoding="utf-8")
    for path in (SYSTEM, COVERAGE):
        imports = _imports_from(path)
        for prefix in FORBIDDEN_IMPORT_PREFIXES:
            assert not any(item == prefix or item.startswith(prefix + ".") for item in imports), prefix
    for token in FORBIDDEN_TOKENS:
        assert token not in text, token
    assert "observed_required_source_ids" in text
    assert "input_coverage_state" in text
    assert "signal_strength_cap_reason" in text
    assert "source_artifact_input_coverage_incomplete" in text
    assert "build_source_artifact_coverage_report" in text


def test_ps_q2b_coverage_report_distinguishes_contract_and_runtime_input_coverage() -> None:
    report = build_source_artifact_coverage_report(observed_source_ids=("bitflyer_spot_ticker", "ohlcv_5m"))
    data = report.to_dict()
    assert data["coverage_state"] == "complete_contract"
    assert data["input_coverage_state"] == "incomplete_inputs"
    assert data["coverage_ratio"] == 1.0
    assert 0 < data["input_coverage_ratio"] < 1.0
    assert "bitflyer_spot_ticker" in data["observed_required_source_ids"]
    assert "ohlcv_10m" in data["missing_observed_required_source_ids"]
    assert data["signal_strength_cap_reason"] == "required_runtime_source_inputs_missing"
    assert data["read_only"] is True
    assert data["non_executing"] is True
    assert data["would_collect_public_source"] is False
    assert data["would_send_to_broker"] is False


def test_ps_q2b_prediction_system_surfaces_runtime_coverage_and_caps_when_missing() -> None:
    now = datetime(2026, 6, 20, 0, 0, 0, tzinfo=timezone.utc)
    result = build_prediction_system_result(requested_horizon_groups=(HorizonGroup.SHORT_HORIZON,), now=now)
    data = result.to_dict()
    coverage = data["system_input"]["source_artifact_coverage_summary"]
    assert coverage["coverage_state"] == "complete_contract"
    assert coverage["input_coverage_state"] == "incomplete_inputs"
    assert coverage["input_coverage_ratio"] == 0.0
    assert coverage["missing_observed_required_source_ids"]
    assert coverage["signal_strength_cap_reason"] == "required_runtime_source_inputs_missing"
    assert data["gpt_review_digest"]["source_artifact_input_coverage_state"] == "incomplete_inputs"
    assert data["gpt_review_digest"]["source_artifact_signal_strength_cap_reason"] == "required_runtime_source_inputs_missing"
    assert "source_artifact_input_coverage_incomplete" in data["scenario_core"]["warnings"]
    assert data["scenario_core"]["scenario_trace"]["source_artifact_coverage"]["input_coverage_state"] == "incomplete_inputs"
    assert data["gpt_review_digest"]["scenario_review_summary"]["source_artifact_coverage"]["input_coverage_state"] == "incomplete_inputs"
    assert data["read_only"] is True
    assert data["non_executing"] is True
    assert data["would_send_to_broker"] is False
    assert data["broker_execution_requested"] is False
    assert data["mode_apply_requested"] is False
    assert data["command_ledger_append_requested"] is False


def test_ps_q2b_prediction_system_detects_some_supplied_runtime_sources() -> None:
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
    coverage = data["system_input"]["source_artifact_coverage_summary"]
    observed = set(coverage["observed_required_source_ids"])
    assert "provider_source_reliability_state" in observed
    assert "bitflyer_spot_ticker" in observed
    assert "bitflyer_fx_ticker" in observed
    assert "global_spot_reference" in observed
    assert "ohlcv_5m" in observed
    assert "ohlcv_10m" in observed
    assert coverage["input_coverage_ratio"] > 0.0
    assert coverage["input_coverage_state"] == "incomplete_inputs"
    assert data["system_input"]["source_registry_version"] == "prediction_source_registry.ps_q2.v1"
    assert data["system_input"]["evidence_profile_ids"]
    assert data["gpt_review_digest"]["source_artifact_observed_required_source_count"] == len(coverage["observed_required_source_ids"])


def main() -> int:
    test_ps_q2b_static_boundaries_and_markers()
    test_ps_q2b_coverage_report_distinguishes_contract_and_runtime_input_coverage()
    test_ps_q2b_prediction_system_surfaces_runtime_coverage_and_caps_when_missing()
    test_ps_q2b_prediction_system_detects_some_supplied_runtime_sources()
    print("[OK] Prediction System PS-Q2B source/artifact runtime coverage guard passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
