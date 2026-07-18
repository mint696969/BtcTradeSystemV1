# path: ./btcts_next/src/btcts/apps/operator_ui/tests/test_market_regime_runtime_horizon_read_model_mr_f9_p1.py
# desc: MR-F9 P1 guards runtime-horizon digest, identity, coverage, common read-model projection, selector fallback, and card bridge integration.

from __future__ import annotations

import hashlib
import json
import sys
from copy import deepcopy
from pathlib import Path

import pytest

_SRC_ROOT = Path(__file__).resolve().parents[4]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

from btcts.apps.operator_ui.prediction_warroom.v2.rt_ui.market_regime_read_model_source import (  # noqa: E402
    select_market_regime_read_model_source,
)
from btcts.apps.operator_ui.prediction_warroom.v2.rt_ui.market_regime_selected_read_model_bridge import (  # noqa: E402
    build_market_regime_selected_read_model_bridge,
)
from btcts.prediction.family_read_model import validate_prediction_family_read_model  # noqa: E402
from btcts.prediction.market_regime.runtime_horizon_read_model import (  # noqa: E402
    project_market_regime_runtime_horizons_to_read_model,
)

HORIZONS = (0, 300, 900, 1800, 3600, 21600, 43200, 86400)
RUN_ID = "run-20260717T185500Z-a81ebcb6466e"
ORIGIN = "2026-07-17T18:55:00Z"


def _digest(payload: dict) -> str:
    canonical = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def _fixture() -> tuple[dict, dict[str, dict]]:
    payloads: dict[str, dict] = {}
    artifacts = []
    for sec in HORIZONS:
        relpath = f"prediction/market_regime/runtime_horizons/date=2026-07-17/runs/{RUN_ID}/horizon={sec}.json"
        current = sec == 0
        payload = {
            "schema_version": "prediction.market_regime.runtime_horizon_persistence_plan.mr_f9_19b.v1",
            "artifact_kind": "market_regime_runtime_horizon",
            "prediction_family_id": "market_regime",
            "prediction_origin": ORIGIN,
            "run_id": RUN_ID,
            "horizon_sec": sec,
            "read_only": True,
            "non_executing": True,
            "ui_inference_allowed": False,
            "ui_confidence_recalculation_allowed": False,
            "horizon": {
                "horizon_key": "current" if current else f"{sec}s",
                "horizon_sec": sec,
                "prediction_origin": ORIGIN,
                "trace_id": f"trace:{sec}",
                "label": "RANGE" if current else "UNKNOWN",
                "status": "OBSERVED_ESTIMATE" if current else "ABSTAIN",
                "abstained": not current,
                "abstain_reason": "" if current else "fixture_abstain",
                "inference_mode": "current_state_estimation" if current else "horizon_specific_future_model",
                "model_id": f"model-{sec}",
                "logic_version": f"logic-{sec}",
                "parameter_set_id": f"params-{sec}",
                "target_definition_version": f"target-{sec}",
                "display_confidence_percent": None,
                "calibrated_probability_claim": False,
                "confidence_semantics": "not_promoted_for_runtime_display",
                "source_kind": "fixture_source",
                "source_timestamp": "2026-07-17T18:53:00Z",
                "source_age_sec": 120,
                "source_freshness_state": "LIVE",
                "fallback_used": False,
                "fallback_reason": "",
                "warnings": [f"warning-{sec}"],
                "invalidation_conditions": [] if current else [f"invalidate-{sec}"],
                "metadata": {"blockers": [] if current else [f"blocker-{sec}"]},
                "read_only": True,
            },
        }
        payloads[relpath] = payload
        artifacts.append(
            {
                "artifact_relpath": relpath,
                "horizon_sec": sec,
                "payload_sha256": _digest(payload),
                "trace_id": f"trace:{sec}",
            }
        )
    manifest = {
        "schema_version": "prediction.market_regime.runtime_horizon_persistence_plan.mr_f9_19b.v1",
        "artifact_kind": "market_regime_runtime_horizon_run_manifest",
        "prediction_family_id": "market_regime",
        "prediction_origin": ORIGIN,
        "run_id": RUN_ID,
        "horizon_count": 8,
        "horizon_artifacts": artifacts,
        "latest_pointer_relpath": None,
        "read_only": True,
        "non_executing": True,
        "ui_inference_allowed": False,
        "ui_confidence_recalculation_allowed": False,
    }
    return manifest, payloads


def test_projects_complete_run_into_valid_common_read_model() -> None:
    manifest, payloads = _fixture()
    model = project_market_regime_runtime_horizons_to_read_model(
        manifest=manifest,
        payloads_by_relpath=payloads,
    )

    validation = validate_prediction_family_read_model(model)
    assert validation["ok"] is True
    assert model["generated_at"] == ORIGIN
    assert model["run_id"] == RUN_ID
    assert model["prediction_id"] == f"{RUN_ID}:{ORIGIN}"
    assert [row["horizon_sec"] for row in model["horizon_rows"]] == list(HORIZONS)
    assert model["horizon_rows"][0]["primary_label"] == "RANGE"
    assert model["horizon_rows"][1]["primary_label"] == "UNKNOWN"
    assert model["horizon_rows"][1]["evidence_quality"] == "ABSTAIN"
    assert all(row["confidence_percent"] == 0 for row in model["horizon_rows"])
    assert model["projection"]["payload_digest_match_count"] == 8
    assert model["projection"]["prediction_invoked"] is False
    assert model["projection"]["classifier_invoked"] is False
    assert model["projection"]["confidence_recalculated"] is False
    assert model["projection"]["writes_dhot"] is False


def test_digest_mismatch_fails_closed() -> None:
    manifest, payloads = _fixture()
    relpath = manifest["horizon_artifacts"][2]["artifact_relpath"]
    payloads[relpath]["horizon"]["label"] = "DOWN_TREND"

    with pytest.raises(ValueError, match="runtime_horizon_payload_digest_mismatch"):
        project_market_regime_runtime_horizons_to_read_model(
            manifest=manifest,
            payloads_by_relpath=payloads,
        )


def test_identity_or_safety_mismatch_fails_closed() -> None:
    manifest, payloads = _fixture()
    relpath = manifest["horizon_artifacts"][0]["artifact_relpath"]
    bad_identity = deepcopy(payloads)
    bad_identity[relpath]["run_id"] = "other-run"
    manifest["horizon_artifacts"][0]["payload_sha256"] = _digest(bad_identity[relpath])

    with pytest.raises(ValueError, match="runtime_horizon_payload_run_id_mismatch"):
        project_market_regime_runtime_horizons_to_read_model(
            manifest=manifest,
            payloads_by_relpath=bad_identity,
        )

    safe_manifest, safe_payloads = _fixture()
    safe_manifest["ui_inference_allowed"] = True
    with pytest.raises(ValueError, match="runtime_horizon_manifest_ui_inference_forbidden"):
        project_market_regime_runtime_horizons_to_read_model(
            manifest=safe_manifest,
            payloads_by_relpath=safe_payloads,
        )


def test_incomplete_or_duplicate_horizon_set_fails_closed() -> None:
    manifest, payloads = _fixture()
    manifest["horizon_artifacts"][7]["horizon_sec"] = 43200

    with pytest.raises(ValueError, match="runtime_horizon_manifest_sec_mismatch"):
        project_market_regime_runtime_horizons_to_read_model(
            manifest=manifest,
            payloads_by_relpath=payloads,
        )


def test_existing_selector_and_card_bridge_accept_projected_artifact() -> None:
    manifest, payloads = _fixture()
    model = project_market_regime_runtime_horizons_to_read_model(
        manifest=manifest,
        payloads_by_relpath=payloads,
    )

    selected = select_market_regime_read_model_source(artifact_read_model=model)
    bridge = build_market_regime_selected_read_model_bridge(selected)

    assert selected["selected_source"] == "artifact"
    assert selected["fallback_used"] is True
    assert selected["fallback_reason"] == "push_missing"
    assert selected["run_id"] == RUN_ID
    assert selected["prediction_generated_at"] == ORIGIN
    assert selected["confidence_merge_performed"] is False
    assert selected["confidence_recalculation_performed"] is False
    assert bridge["ok"] is True
    assert bridge["selected_source"] == "artifact"
    assert bridge["prediction_generated_at"] == ORIGIN
    assert bridge["run_id"] == RUN_ID
    assert bridge["card_count"] == 8
    assert bridge["cards"][0]["run_id"] == RUN_ID
    assert bridge["cards"][0]["prediction_id"] == f"{RUN_ID}:{ORIGIN}"
    assert bridge["prediction_invoked"] is False
    assert bridge["classifier_invoked"] is False
    assert bridge["confidence_recalculated"] is False
    assert bridge["would_send_to_broker"] is False
