# path: ./btcts_next/src/btcts/processing/l4_consumer_models/shared/prediction_direction_builder.py
# desc: Thin skeleton builder for read-only PredictionDirectionOutput.

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from btcts.processing.l4_consumer_models.contracts import (
    HorizonDirectionReading,
    PredictionDirectionOutput,
)


@dataclass(frozen=True)
class PredictionDirectionBuildInput:
    scenario_ref: str
    source_kind: str = "scenario_reading"
    market_uid: str = "unknown"
    event_ts: str = "unknown"
    primary_direction_bias: str = "neutral"
    diagnostics: dict[str, Any] | None = None


def build_prediction_direction_input_from_scenario(
    *,
    scenario_ref: str,
    source_kind: str = "scenario_reading",
    market_uid: str = "unknown",
    event_ts: str = "unknown",
    scenario_regime_bias: str = "neutral",
    diagnostics: dict[str, Any] | None = None,
) -> PredictionDirectionBuildInput:
    return PredictionDirectionBuildInput(
        scenario_ref=scenario_ref,
        source_kind=source_kind,
        market_uid=market_uid,
        event_ts=event_ts,
        primary_direction_bias=scenario_regime_bias,
        diagnostics={
            "derivation_type": "scenario_to_direction_input",
            "derivation_stage": "thin_local_helper",
            "read_only_contract": True,
            "not_runtime_wiring": True,
            "not_replay_wiring": True,
            "not_ui_wiring": True,
            **dict(diagnostics or {}),
        },
    )


def build_prediction_direction_output(
    inp: PredictionDirectionBuildInput,
) -> PredictionDirectionOutput:
    return PredictionDirectionOutput(
        prediction_type="direction",
        prediction_version="phase4a.direction.v1",
        source_kind=inp.source_kind,
        market_uid=inp.market_uid,
        event_ts=inp.event_ts,
        scenario_ref=inp.scenario_ref,
        primary_direction_bias=inp.primary_direction_bias,
        horizon_direction_readings=(
            HorizonDirectionReading(
                horizon_key="read_only_skeleton",
                direction_bias=inp.primary_direction_bias,
                confidence=0.0,
                continuation_balance=0.0,
                reversal_balance=0.0,
                turning_point_risk=0.0,
                invalidation_hint=None,
            ),
        ),
        continuation_reversal_balance=0.0,
        turning_point_risk=0.0,
        confidence=0.0,
        caution_level="normal",
        invalidation_carry=None,
        evidence_trace_refs=(),
        diagnostics={
            "builder_type": "prediction_direction_output",
            "builder_stage": "thin_skeleton",
            "read_only_contract": True,
            "not_position_owner": True,
            "not_execution_instruction": True,
            "not_broker_automation": True,
            **dict(inp.diagnostics or {}),
        },
    )

def prediction_direction_output_to_snapshot(
    output: PredictionDirectionOutput,
) -> dict[str, Any]:
    return {
        "prediction_type": output.prediction_type,
        "prediction_version": output.prediction_version,
        "source_kind": output.source_kind,
        "market_uid": output.market_uid,
        "event_ts": output.event_ts,
        "scenario_ref": output.scenario_ref,
        "primary_direction_bias": output.primary_direction_bias,
        "horizon_direction_readings": [
            {
                "horizon_key": reading.horizon_key,
                "direction_bias": reading.direction_bias,
                "confidence": reading.confidence,
                "continuation_balance": reading.continuation_balance,
                "reversal_balance": reading.reversal_balance,
                "turning_point_risk": reading.turning_point_risk,
                "invalidation_hint": reading.invalidation_hint,
            }
            for reading in output.horizon_direction_readings
        ],
        "continuation_reversal_balance": output.continuation_reversal_balance,
        "turning_point_risk": output.turning_point_risk,
        "confidence": output.confidence,
        "caution_level": output.caution_level,
        "invalidation_carry": output.invalidation_carry,
        "evidence_trace_refs": list(output.evidence_trace_refs),
        "diagnostics": dict(output.diagnostics),
        "snapshot_stage": "direction_read_only_local_snapshot",
        "read_only_contract": True,
        "not_runtime_wiring": True,
        "not_replay_wiring": True,
        "not_ui_wiring": True,
    }