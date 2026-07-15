# path: ./btcts_next/src/btcts/prediction/market_regime/tests/test_market_regime_future_shadow_runtime_writer_handoff.py
# desc: MR-F8.9 tests for the pure runtime-preflight to guarded-writer schema adapter.

from __future__ import annotations

from copy import deepcopy

import pytest

from btcts.prediction.market_regime.future_shadow_runtime_preflight_bridge import (
    MARKET_REGIME_FUTURE_SHADOW_RUNTIME_PREFLIGHT_BRIDGE_VERSION,
)
from btcts.prediction.market_regime.future_shadow_runtime_writer_handoff import (
    WRITER_REPORT_SCHEMA,
    build_runtime_writer_handoff_report,
)
from btcts.prediction.market_regime.tools.shadow_runtime_preflight_once import (
    MR_F8_RUNTIME_PREFLIGHT_ONCE_TOOL_VERSION,
)


def _pair(index: int) -> dict:
    return {
        "artifact_kind": "future_shadow_candidate_pair",
        "pair_id": f"pair:{index}",
        "source_bundle_id": f"bundle:{index}",
        "candidate_count": 2,
        "slot_identity": {
            "origin_timestamp": "2026-07-15T09:12:33Z",
            "feature_snapshot_ref": "snapshot:runtime",
            "target_horizon_sec": (300, 900, 1800, 3600, 21600, 43200, 86400)[index],
        },
        "candidate_identities": [
            {"parameter_set_id": "active"},
            {"parameter_set_id": "shadow"},
        ],
        "forecasts": [
            {"trace_id": f"trace:{index}:active", "parameter_set_id": "active"},
            {"trace_id": f"trace:{index}:shadow", "parameter_set_id": "shadow"},
        ],
        "trace_plan": {
            "trace_count": 2,
            "trace_ids": [f"trace:{index}:active", f"trace:{index}:shadow"],
            "parameter_set_ids": ["active", "shadow"],
            "persistence_plan": {"would_write": False},
        },
    }


def report() -> dict:
    pairs = [_pair(index) for index in range(7)]
    return {
        "schema_version": MR_F8_RUNTIME_PREFLIGHT_ONCE_TOOL_VERSION,
        "artifact_kind": "mr_f8_runtime_preflight_once_result",
        "source_snapshot_ok": True,
        "pair_count": 7,
        "preflight_only": True,
        "writer_invoked": False,
        "writes_dhot": False,
        "scheduler_enabled": False,
        "producer_loop_enabled": False,
        "broker_private_api_allowed": False,
        "autotrade_trigger_allowed": False,
        "order_submission_allowed": False,
        "auto_promotion_allowed": False,
        "live_parameter_apply_allowed": False,
        "preflight_report": {
            "schema_version": MARKET_REGIME_FUTURE_SHADOW_RUNTIME_PREFLIGHT_BRIDGE_VERSION,
            "artifact_kind": "future_shadow_runtime_preflight_report",
            "prediction_origin": "2026-07-15T09:12:33Z",
            "feature_snapshot_ref": "snapshot:runtime",
            "pair_count": 7,
            "pairs": pairs,
            "runtime_source_ready": True,
            "preflight_only": True,
            "writer_invoked": False,
            "writes_dhot": False,
            "scheduler_enabled": False,
            "auto_promotion_allowed": False,
            "live_parameter_apply_allowed": False,
            "canonical_replacement_allowed": False,
        },
    }


def test_builds_writer_compatible_runtime_handoff_for_all_seven_pairs() -> None:
    result = build_runtime_writer_handoff_report(runtime_preflight_result=report())
    assert result["schema_version"] == WRITER_REPORT_SCHEMA
    assert result["ok"] is True
    assert result["runtime_derived"] is True
    assert result["fixture_derived"] is False
    assert result["pair_count"] == 7
    assert len(result["pairs"]) == 7
    assert len(result["pair_ids"]) == 7
    assert len(result["source_bundle_ids"]) == 7
    assert result["writer_invoked"] is False
    assert result["writes_dhot"] is False


def test_rejects_outer_write_or_scheduler_surface() -> None:
    for field in ("writer_invoked", "writes_dhot", "scheduler_enabled"):
        value = deepcopy(report())
        value[field] = True
        with pytest.raises(ValueError, match="outer_safety_invalid"):
            build_runtime_writer_handoff_report(runtime_preflight_result=value)


def test_rejects_nonseven_or_duplicate_runtime_pairs() -> None:
    value = report()
    value["preflight_report"]["pairs"] = value["preflight_report"]["pairs"][:6]
    value["pair_count"] = 6
    value["preflight_report"]["pair_count"] = 6
    with pytest.raises(ValueError, match="pair_count_invalid"):
        build_runtime_writer_handoff_report(runtime_preflight_result=value)

    value = report()
    value["preflight_report"]["pairs"][1]["pair_id"] = value["preflight_report"]["pairs"][0]["pair_id"]
    with pytest.raises(ValueError, match="pair_duplicate"):
        build_runtime_writer_handoff_report(runtime_preflight_result=value)


def test_rejects_write_enabled_trace_plan() -> None:
    value = report()
    value["preflight_report"]["pairs"][0]["trace_plan"]["persistence_plan"]["would_write"] = True
    with pytest.raises(ValueError, match="write_enabled"):
        build_runtime_writer_handoff_report(runtime_preflight_result=value)
