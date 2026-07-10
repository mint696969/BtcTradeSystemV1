# path: ./btcts_next/src/btcts/prediction/bundle_assembly.py
# desc: Non-executing inference bundle assembly from PredictionOutput objects only. No AutoTrade publication or runtime writes.

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Mapping, Tuple

from .contracts import InferenceBundle, PredictionOutput

LOGIC_VERSION = "prediction_inference_bundle.s129.v1"

OUTPUT_LOCAL_BLOCKERS = frozenset(
    {
        "insufficient_exact_horizon_candles",
    }
)


def _generated_at(now: datetime | None) -> str:
    dt = now.astimezone(timezone.utc) if now else datetime.now(timezone.utc)
    return dt.replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _bundle_id(generated_at: str, outputs: Tuple[PredictionOutput, ...]) -> str:
    family_part = "-".join(output.family.value for output in outputs) or "empty"
    horizon_part = "-".join(str(item) for item in sorted({int(output.horizon.horizon_sec) for output in outputs})) or "none"
    return f"{LOGIC_VERSION}:{generated_at}:{family_part}:{horizon_part}"


def _family_coverage(outputs: Tuple[PredictionOutput, ...]) -> dict[str, Any]:
    families = tuple(dict.fromkeys(output.family.value for output in outputs))
    blocked = tuple(output.family.value for output in outputs if output.blockers)
    return {
        "family_count": len(families),
        "families_present": list(families),
        "blocked_families": list(dict.fromkeys(blocked)),
        "all_outputs_unblocked": not blocked and bool(outputs),
    }


def _horizon_coverage(outputs: Tuple[PredictionOutput, ...]) -> dict[str, Any]:
    horizons = tuple(dict.fromkeys(int(output.horizon.horizon_sec) for output in outputs))
    return {
        "horizon_count": len(horizons),
        "horizons_present_sec": list(horizons),
        "single_horizon_bundle": len(horizons) == 1,
    }


def _score_summary(outputs: Tuple[PredictionOutput, ...]) -> dict[str, Any]:
    scores = [float(output.score) for output in outputs if output.score is not None and not output.blockers]
    if not scores:
        return {"scored_output_count": 0, "average_score": None, "min_score": None, "max_score": None}
    return {
        "scored_output_count": len(scores),
        "average_score": round(sum(scores) / len(scores), 6),
        "min_score": min(scores),
        "max_score": max(scores),
    }


def _cross_family_agreement(outputs: Tuple[PredictionOutput, ...]) -> dict[str, Any]:
    labels = {output.family.value: output.primary_label for output in outputs}
    blockers = [output.family.value for output in outputs if output.blockers]
    warnings = [warning for output in outputs for warning in output.warnings]
    bearish_or_risk = any(label in labels.values() for label in ("elevated_risk", "divergent_warning", "volatile_or_divergent"))
    directional = labels.get("trend_bias") in ("long_bias", "short_bias")
    if blockers:
        state = "blocked_or_incomplete"
    elif bearish_or_risk and directional:
        state = "directional_with_risk_warning"
    elif directional:
        state = "directional_agreement"
    elif outputs:
        state = "partial_or_neutral_agreement"
    else:
        state = "empty"
    return {
        "agreement_state": state,
        "labels_by_family": labels,
        "blocked_family_count": len(blockers),
        "warning_count": len(warnings),
    }


def _risk_context(outputs: Tuple[PredictionOutput, ...]) -> dict[str, Any]:
    warning_count = sum(len(output.warnings) for output in outputs)
    blocker_count = sum(len(output.blockers) for output in outputs)
    risk_labels = [output.primary_label for output in outputs if output.primary_label in ("elevated_risk", "divergent_warning", "volatile_or_divergent", "compression_watch")]
    if blocker_count:
        risk_state = "blocked"
    elif "elevated_risk" in risk_labels or "divergent_warning" in risk_labels or "volatile_or_divergent" in risk_labels:
        risk_state = "risk_warning"
    elif "compression_watch" in risk_labels:
        risk_state = "watch"
    elif outputs:
        risk_state = "normal"
    else:
        risk_state = "unknown"
    return {
        "risk_state": risk_state,
        "warning_count": warning_count,
        "blocker_count": blocker_count,
        "risk_labels": risk_labels,
    }


def _partition_output_blockers(
    outputs: Tuple[PredictionOutput, ...],
) -> tuple[Tuple[str, ...], Tuple[dict[str, Any], ...]]:
    bundle_blockers: list[str] = []
    local_blockers: list[dict[str, Any]] = []
    for output in outputs:
        for blocker in output.blockers:
            blocker_text = str(blocker)
            if blocker_text in OUTPUT_LOCAL_BLOCKERS:
                local_blockers.append(
                    {
                        "family": output.family.value,
                        "horizon_sec": int(output.horizon.horizon_sec),
                        "blocker": blocker_text,
                        "scope": "output_local",
                    }
                )
            else:
                bundle_blockers.append(blocker_text)
    return tuple(dict.fromkeys(bundle_blockers)), tuple(local_blockers)


def _operator_explanation(outputs: Tuple[PredictionOutput, ...]) -> Tuple[str, ...]:
    if not outputs:
        return ("no prediction outputs supplied",)
    lines: list[str] = []
    for output in outputs:
        label = output.primary_label
        score = "unknown" if output.score is None else f"{output.score:.3f}"
        suffix = " blocked" if output.blockers else ""
        lines.append(f"{output.family.value}: {label} score={score}{suffix}")
    return tuple(lines)


def build_inference_bundle_from_outputs(
    outputs: Tuple[PredictionOutput, ...],
    *,
    now: datetime | None = None,
    source_quality_summary: Mapping[str, Any] | None = None,
    extra_risk_context: Mapping[str, Any] | None = None,
) -> InferenceBundle:
    normalized = tuple(outputs)
    generated_at = _generated_at(now)
    blockers: list[str] = []
    warnings: list[str] = []
    if not normalized:
        blockers.append("prediction_outputs_missing")
    output_bundle_blockers, output_local_blockers = _partition_output_blockers(normalized)
    blockers.extend(output_bundle_blockers)
    for output in normalized:
        warnings.extend(output.warnings)
    risk_context = _risk_context(normalized)
    if extra_risk_context:
        risk_context = {**risk_context, **dict(extra_risk_context)}
    quality_summary = dict(source_quality_summary or {})
    quality_summary["family_coverage"] = _family_coverage(normalized)
    quality_summary["horizon_coverage"] = _horizon_coverage(normalized)
    quality_summary["score_summary"] = _score_summary(normalized)
    quality_summary["output_local_blockers"] = [dict(item) for item in output_local_blockers]
    quality_summary["output_local_blocker_count"] = len(output_local_blockers)
    quality_summary["bundle_fatal_output_blockers"] = list(output_bundle_blockers)
    return InferenceBundle(
        bundle_id=_bundle_id(generated_at, normalized),
        generated_at=generated_at,
        logic_version=LOGIC_VERSION,
        outputs=normalized,
        source_quality_summary=quality_summary,
        cross_family_agreement=_cross_family_agreement(normalized),
        risk_context=risk_context,
        operator_explanation=_operator_explanation(normalized),
        blockers=tuple(dict.fromkeys(blockers)),
        warnings=tuple(dict.fromkeys(warnings)),
    )
