# path: ./btcts_next/src/btcts/prediction/market_regime/runtime_horizon_read_model.py
# desc: MR-F9 P1 pure fail-closed projection from one validated runtime-horizon run into the family-neutral read model. No I/O, UI mount, inference, persistence, broker, AutoTrade, or order behavior.

from __future__ import annotations

import hashlib
import json
from typing import Any, Mapping

from btcts.prediction.family_read_model import build_prediction_family_read_model

MARKET_REGIME_RUNTIME_HORIZON_READ_MODEL_VERSION = (
    "prediction.market_regime.runtime_horizon_read_model.mr_f9_p1.v1"
)
_EXPECTED_HORIZONS = (0, 300, 900, 1800, 3600, 21600, 43200, 86400)
_EXPECTED_MANIFEST_KIND = "market_regime_runtime_horizon_run_manifest"
_EXPECTED_PAYLOAD_KIND = "market_regime_runtime_horizon"


def _text(value: object) -> str:
    return str(value or "")


def _canonical_sha256(payload: Mapping[str, Any]) -> str:
    canonical = json.dumps(
        payload,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def _require(condition: bool, failure: str) -> None:
    if not condition:
        raise ValueError(failure)


def _confidence_percent(horizon: Mapping[str, Any]) -> int:
    value = horizon.get("display_confidence_percent")
    if value is None:
        return 0
    try:
        return max(0, min(99, int(round(float(value)))))
    except (TypeError, ValueError) as exc:
        raise ValueError("runtime_horizon_display_confidence_invalid") from exc


def _texts(value: object) -> list[str]:
    if isinstance(value, (list, tuple)):
        return [str(item) for item in value if str(item)]
    if value in (None, ""):
        return []
    return [str(value)]


def _blockers(horizon: Mapping[str, Any]) -> list[str]:
    result: list[str] = []
    metadata = horizon.get("metadata") if isinstance(horizon.get("metadata"), Mapping) else {}
    result.extend(_texts(metadata.get("blockers")))
    result.extend(_texts(horizon.get("abstain_reason")))
    result.extend(_texts(horizon.get("invalidation_conditions")))
    return list(dict.fromkeys(item for item in result if item))


def _evidence_quality(horizon: Mapping[str, Any]) -> str:
    status = _text(horizon.get("status")).upper()
    if bool(horizon.get("abstained")) or status == "ABSTAIN":
        return "ABSTAIN"
    if status == "OBSERVED_ESTIMATE":
        return "OBSERVED"
    return status or "UNKNOWN"


def _horizon_group(horizon_sec: int) -> str:
    if horizon_sec == 0:
        return "current"
    if horizon_sec <= 1800:
        return "short"
    if horizon_sec <= 21600:
        return "medium"
    return "long"


def _row_from_payload(
    *,
    payload: Mapping[str, Any],
    artifact_relpath: str,
    payload_sha256: str,
) -> dict[str, Any]:
    horizon = payload.get("horizon") if isinstance(payload.get("horizon"), Mapping) else {}
    horizon_sec = int(horizon.get("horizon_sec"))
    confidence = _confidence_percent(horizon)
    calibrated = bool(horizon.get("calibrated_probability_claim"))
    confidence_kind = (
        "calibrated_probability"
        if calibrated
        else "unavailable_not_promoted"
        if horizon.get("display_confidence_percent") is None
        else "diagnostic_not_calibrated_probability"
    )
    label = _text(horizon.get("label")) or "UNKNOWN"
    trace_id = _text(horizon.get("trace_id"))
    return {
        "horizon_key": _text(horizon.get("horizon_key")) or str(horizon_sec),
        "horizon_sec": horizon_sec,
        "horizon_group": _horizon_group(horizon_sec),
        "primary_label": label,
        "primary_label_display": label,
        "confidence_percent": confidence,
        "confidence_kind": confidence_kind,
        "freshness_state": _text(horizon.get("source_freshness_state")) or "UNKNOWN",
        "evidence_quality": _evidence_quality(horizon),
        "drivers": _texts(horizon.get("warnings")),
        "blockers": _blockers(horizon),
        "warnings": _texts(horizon.get("warnings")),
        "invalidation_hints": _texts(horizon.get("invalidation_conditions")),
        "source_refs": [
            {
                "source_kind": _text(horizon.get("source_kind")),
                "source_timestamp": _text(horizon.get("source_timestamp")),
                "source_age_sec": horizon.get("source_age_sec"),
            }
        ],
        "trace_refs": [
            {
                "trace_id": trace_id,
                "artifact_relpath": artifact_relpath,
                "payload_sha256": payload_sha256,
                "prediction_origin": _text(horizon.get("prediction_origin")),
            }
        ],
        "family_payload": {
            "regime_code": label,
            "status": _text(horizon.get("status")),
            "inference_mode": _text(horizon.get("inference_mode")),
            "model_id": _text(horizon.get("model_id")),
            "logic_version": _text(horizon.get("logic_version")),
            "parameter_set_id": _text(horizon.get("parameter_set_id")),
            "target_definition_version": _text(horizon.get("target_definition_version")),
            "source_kind": _text(horizon.get("source_kind")),
            "source_timestamp": _text(horizon.get("source_timestamp")),
            "source_age_sec": horizon.get("source_age_sec"),
            "calibrated_probability_claim": calibrated,
            "confidence_semantics": _text(horizon.get("confidence_semantics")),
            "fallback_used": bool(horizon.get("fallback_used")),
            "fallback_reason": _text(horizon.get("fallback_reason")),
            "abstained": bool(horizon.get("abstained")),
            "abstain_reason": _text(horizon.get("abstain_reason")),
        },
    }


def project_market_regime_runtime_horizons_to_read_model(
    *,
    manifest: Mapping[str, Any],
    payloads_by_relpath: Mapping[str, Mapping[str, Any]],
) -> dict[str, Any]:
    """Project one complete validated run without reading files or mutating inputs."""
    _require(manifest.get("artifact_kind") == _EXPECTED_MANIFEST_KIND, "runtime_horizon_manifest_kind_mismatch")
    _require(manifest.get("prediction_family_id") == "market_regime", "runtime_horizon_manifest_family_mismatch")
    _require(manifest.get("read_only") is True, "runtime_horizon_manifest_read_only_required")
    _require(manifest.get("non_executing") is True, "runtime_horizon_manifest_non_executing_required")
    _require(manifest.get("ui_inference_allowed") is False, "runtime_horizon_manifest_ui_inference_forbidden")
    _require(
        manifest.get("ui_confidence_recalculation_allowed") is False,
        "runtime_horizon_manifest_ui_confidence_recalculation_forbidden",
    )
    _require(manifest.get("latest_pointer_relpath") is None, "runtime_horizon_manifest_latest_pointer_forbidden")

    run_id = _text(manifest.get("run_id"))
    origin = _text(manifest.get("prediction_origin"))
    _require(bool(run_id), "runtime_horizon_manifest_run_id_missing")
    _require(bool(origin), "runtime_horizon_manifest_prediction_origin_missing")

    artifacts = manifest.get("horizon_artifacts")
    _require(isinstance(artifacts, list), "runtime_horizon_manifest_artifacts_missing")
    _require(int(manifest.get("horizon_count") or -1) == 8, "runtime_horizon_manifest_horizon_count_mismatch")
    _require(len(artifacts) == 8, "runtime_horizon_manifest_artifact_count_mismatch")

    rows: list[dict[str, Any]] = []
    actual_horizons: list[int] = []
    for artifact in artifacts:
        _require(isinstance(artifact, Mapping), "runtime_horizon_manifest_artifact_not_mapping")
        relpath = _text(artifact.get("artifact_relpath"))
        expected_digest = _text(artifact.get("payload_sha256"))
        _require(bool(relpath), "runtime_horizon_manifest_artifact_relpath_missing")
        _require(bool(expected_digest), "runtime_horizon_manifest_payload_sha256_missing")
        payload = payloads_by_relpath.get(relpath)
        _require(isinstance(payload, Mapping), f"runtime_horizon_payload_missing:{relpath}")
        _require(_canonical_sha256(payload) == expected_digest, f"runtime_horizon_payload_digest_mismatch:{relpath}")
        _require(payload.get("artifact_kind") == _EXPECTED_PAYLOAD_KIND, f"runtime_horizon_payload_kind_mismatch:{relpath}")
        _require(payload.get("prediction_family_id") == "market_regime", f"runtime_horizon_payload_family_mismatch:{relpath}")
        _require(payload.get("run_id") == run_id, f"runtime_horizon_payload_run_id_mismatch:{relpath}")
        _require(payload.get("prediction_origin") == origin, f"runtime_horizon_payload_origin_mismatch:{relpath}")
        _require(payload.get("read_only") is True, f"runtime_horizon_payload_read_only_required:{relpath}")
        _require(payload.get("non_executing") is True, f"runtime_horizon_payload_non_executing_required:{relpath}")
        _require(payload.get("ui_inference_allowed") is False, f"runtime_horizon_payload_ui_inference_forbidden:{relpath}")
        _require(
            payload.get("ui_confidence_recalculation_allowed") is False,
            f"runtime_horizon_payload_ui_confidence_recalculation_forbidden:{relpath}",
        )
        horizon = payload.get("horizon") if isinstance(payload.get("horizon"), Mapping) else {}
        sec = int(horizon.get("horizon_sec"))
        _require(int(payload.get("horizon_sec")) == sec, f"runtime_horizon_payload_sec_mismatch:{relpath}")
        _require(int(artifact.get("horizon_sec")) == sec, f"runtime_horizon_manifest_sec_mismatch:{relpath}")
        _require(horizon.get("prediction_origin") == origin, f"runtime_horizon_row_origin_mismatch:{relpath}")
        _require(bool(_text(horizon.get("trace_id"))), f"runtime_horizon_trace_id_missing:{relpath}")
        actual_horizons.append(sec)
        rows.append(
            _row_from_payload(
                payload=payload,
                artifact_relpath=relpath,
                payload_sha256=expected_digest,
            )
        )

    _require(tuple(sorted(actual_horizons)) == _EXPECTED_HORIZONS, "runtime_horizon_coverage_mismatch")
    _require(len(set(actual_horizons)) == 8, "runtime_horizon_duplicate_horizon")
    rows.sort(key=lambda item: int(item["horizon_sec"]))

    model = build_prediction_family_read_model(
        prediction_family_id="market_regime",
        generated_at=origin,
        run_id=run_id,
        prediction_id=f"{run_id}:{origin}",
        model_id="market_regime.runtime_horizon_collection",
        logic_version=MARKET_REGIME_RUNTIME_HORIZON_READ_MODEL_VERSION,
        parameter_set_id="market_regime.runtime_horizon.per_row_parameter_sets",
        horizon_rows=rows,
    )
    model["projection"] = {
        "projection_version": MARKET_REGIME_RUNTIME_HORIZON_READ_MODEL_VERSION,
        "source_artifact_kind": _EXPECTED_MANIFEST_KIND,
        "source_schema_version": _text(manifest.get("schema_version")),
        "payload_digest_match_count": 8,
        "horizon_identity_preserved": True,
        "prediction_invoked": False,
        "classifier_invoked": False,
        "confidence_recalculated": False,
        "source_merge_performed": False,
        "artifact_read_performed": False,
        "writes_dhot": False,
        "mount_enabled": False,
    }
    return model
