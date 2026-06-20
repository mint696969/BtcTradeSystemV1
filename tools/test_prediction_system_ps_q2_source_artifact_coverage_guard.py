# path: ./tools/test_prediction_system_ps_q2_source_artifact_coverage_guard.py
# desc: Focused guard for PS-Q2 Prediction System source/artifact input coverage contracts. Non-collecting, non-executing.

from __future__ import annotations

import ast
import json
from pathlib import Path

from _btcts_bootstrap import ensure_btcts_on_syspath
ensure_btcts_on_syspath()

from btcts.prediction import (
    ContextEvidenceProfile,
    DirectionOwnership,
    EvidenceTier,
    ReferenceSourceRegistryEntry,
    SourceArtifactCoverageReport,
    SourceArtifactContract,
    SourceEffect,
    build_default_context_evidence_profiles,
    build_default_reference_source_registry,
    build_source_artifact_coverage_report,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
MODULE = REPO_ROOT / "btcts_next/src/btcts/prediction/source_artifact_coverage.py"
INIT = REPO_ROOT / "btcts_next/src/btcts/prediction/__init__.py"
SYSTEM_CONTRACT = REPO_ROOT / "btcts_next/src/btcts/prediction/system_contract.py"
SPEC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_INFERENCE_FORMAL_SPEC_BTC_BITFLYER_2026-06-20.md"

REQUIRED_SOURCE_IDS = {
    "bitflyer_spot_ticker",
    "bitflyer_fx_ticker",
    "bitflyer_trades",
    "bitflyer_board_summary",
    "ohlcv_1m",
    "ohlcv_5m",
    "ohlcv_10m",
    "ohlcv_15m",
    "ohlcv_30m",
    "ohlcv_1h",
    "ohlcv_4h",
    "ohlcv_1d",
    "global_spot_reference",
    "global_derivatives_context",
    "funding_context",
    "basis_context",
    "liquidation_context",
    "macro_context",
    "session_calendar_context",
    "exchange_status_incident_context",
    "news_event_context",
    "provider_source_reliability_state",
    "internal_replay_outcome_calibration",
}
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


def test_ps_q2_source_artifact_coverage_static_boundaries() -> None:
    for path in (MODULE, INIT, SYSTEM_CONTRACT):
        assert path.exists(), path
    text = MODULE.read_text(encoding="utf-8")
    assert "# path: ./btcts_next/src/btcts/prediction/source_artifact_coverage.py" in text
    assert "PS-Q2 source/artifact input coverage" in text
    assert "ContextEvidenceProfile" in text
    assert "SourceArtifactCoverageReport" in text
    assert "runtime_collection_allowed: bool = False" in text
    assert "collector_runtime_import_allowed: bool = False" in text
    assert "broker_or_autotrade_allowed: bool = False" in text
    imports = _imports_from(MODULE)
    for prefix in FORBIDDEN_IMPORT_PREFIXES:
        assert not any(item == prefix or item.startswith(prefix + ".") for item in imports), prefix
    for token in FORBIDDEN_TOKENS:
        assert token not in text, token


def test_ps_q2_default_registry_covers_required_sources_and_is_contract_only() -> None:
    registry = build_default_reference_source_registry()
    report = build_source_artifact_coverage_report(registry_entries=registry)
    data = report.to_dict()
    covered = {entry.source_id for entry in registry}
    assert REQUIRED_SOURCE_IDS.issubset(covered)
    assert data["coverage_state"] == "complete_contract"
    assert data["missing_required_source_ids"] == []
    assert data["coverage_ratio"] == 1.0
    assert data["read_only"] is True
    assert data["non_executing"] is True
    assert data["would_collect_public_source"] is False
    assert data["would_write_runtime_artifact"] is False
    assert data["would_send_to_broker"] is False
    assert data["broker_execution_requested"] is False
    assert data["mode_apply_requested"] is False
    assert data["command_ledger_append_requested"] is False
    assert all(entry.artifact_contract.runtime_collection_allowed is False for entry in registry)
    assert all(entry.artifact_contract.collector_runtime_import_allowed is False for entry in registry)
    assert all(entry.artifact_contract.external_api_call_allowed is False for entry in registry)
    assert all(entry.artifact_contract.broker_or_autotrade_allowed is False for entry in registry)
    assert any(entry.source_id == "ohlcv_10m" for entry in registry)
    assert any(entry.source_id == "exchange_status_incident_context" for entry in registry)
    assert any(entry.evidence_tier is EvidenceTier.TIER_1_LOCAL_EXECUTABLE_MARKET for entry in registry)
    assert any(entry.evidence_tier is EvidenceTier.TIER_5_MACRO_SESSION_EVENT for entry in registry)


def test_ps_q2_context_profiles_are_card_and_horizon_specific() -> None:
    profiles = build_default_context_evidence_profiles()
    by_id = {profile.evidence_profile_id: profile for profile in profiles}
    assert {"trend_short_horizon_v1", "reversal_now_short_v1", "macro_long_horizon_v1", "liquidity_nowcast_v1"}.issubset(by_id)
    assert EvidenceTier.TIER_1_LOCAL_EXECUTABLE_MARKET in by_id["trend_short_horizon_v1"].primary_evidence_tiers
    assert EvidenceTier.TIER_4_DERIVATIVES_LEVERAGE in by_id["reversal_now_short_v1"].secondary_evidence_tiers
    assert EvidenceTier.TIER_5_MACRO_SESSION_EVENT in by_id["macro_long_horizon_v1"].primary_evidence_tiers
    assert by_id["liquidity_nowcast_v1"].applies_to_horizon_groups == ("nowcast",)
    assert all(profile.signal_strength_ceiling <= 99 for profile in profiles)
    assert all(profile.signal_strength_floor >= 0 for profile in profiles)
    assert any("short_horizon" in profile.applies_to_horizon_groups for profile in profiles)
    assert any("long_horizon" in profile.applies_to_horizon_groups for profile in profiles)


def test_ps_q2_exports_and_serialization_roundtrip() -> None:
    assert SourceArtifactContract is not None
    assert ReferenceSourceRegistryEntry is not None
    assert ContextEvidenceProfile is not None
    assert SourceArtifactCoverageReport is not None
    assert DirectionOwnership.SUPPORTING.value == "supporting"
    assert SourceEffect.CONTEXT_ONLY.value == "context_only"
    report = build_source_artifact_coverage_report()
    payload = report.to_dict()
    decoded = json.loads(json.dumps(payload, ensure_ascii=False, sort_keys=True))
    assert decoded["registry_version"] == "prediction_source_registry.ps_q2.v1"
    assert decoded["evidence_profile_version"] == "prediction_evidence_profiles.ps_q2.v1"
    assert decoded["registry_entries"][0]["read_only"] is True
    assert decoded["context_evidence_profiles"][0]["non_executing"] is True
    assert "evidence_profile_ids" in SYSTEM_CONTRACT.read_text(encoding="utf-8")
    assert "source_artifact_coverage_summary" in SYSTEM_CONTRACT.read_text(encoding="utf-8")
    assert "Context-specific evidence profiles" in SPEC.read_text(encoding="utf-8")


def main() -> int:
    test_ps_q2_source_artifact_coverage_static_boundaries()
    test_ps_q2_default_registry_covers_required_sources_and_is_contract_only()
    test_ps_q2_context_profiles_are_card_and_horizon_specific()
    test_ps_q2_exports_and_serialization_roundtrip()
    print("[OK] Prediction System PS-Q2 source/artifact coverage guard passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
