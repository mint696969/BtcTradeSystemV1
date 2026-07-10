# path: ./btcts_next/src/btcts/prediction/market_regime/source_scorecard_artifacts.py
# desc: Current-primary MarketRegime source-scorecard artifact preflight and atomic writer. Reads only derived trace/outcome artifacts and never mutates runtime parameters.

from __future__ import annotations

from datetime import datetime, timezone
import json
from pathlib import Path
from typing import Any, Iterable, Mapping

from .source_scorecard_pipeline import (
    MARKET_REGIME_SOURCE_SCORECARD_PIPELINE_VERSION,
    build_market_regime_source_scorecard_pipeline,
)

MARKET_REGIME_SOURCE_SCORECARD_ARTIFACT_WRITER_VERSION = (
    "prediction.market_regime.source_scorecard_artifacts.2026_07_10.v1"
)
SOURCE_SCORECARD_CURRENT_PRIMARY_RELPATH = (
    "prediction/market_regime/source_scorecard/latest_current_primary.json"
)
CURRENT_PRIMARY_COHORT_STARTED_AT = "2026-07-10T15:27:22Z"


def source_scorecard_current_primary_relpath() -> str:
    return SOURCE_SCORECARD_CURRENT_PRIMARY_RELPATH


def _parse_utc(value: object) -> datetime | None:
    text = str(value or "").strip()
    if not text:
        return None
    try:
        parsed = datetime.fromisoformat(text.replace("Z", "+00:00"))
    except ValueError:
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def _is_current(row: Mapping[str, Any], cutoff: datetime) -> bool:
    generated_at = _parse_utc(row.get("generated_at"))
    return generated_at is not None and generated_at >= cutoff


def _iter_jsonl(paths: Iterable[Path]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for path in sorted(paths):
        if not path.is_file():
            continue
        with path.open("r", encoding="utf-8") as handle:
            for line_no, raw in enumerate(handle, start=1):
                if not raw.strip():
                    continue
                try:
                    payload = json.loads(raw)
                except json.JSONDecodeError as exc:
                    raise ValueError(f"invalid JSONL: {path}:{line_no}: {exc}") from exc
                if isinstance(payload, Mapping):
                    rows.append(dict(payload))
    return rows


def _has_source_attribution(row: Mapping[str, Any]) -> bool:
    value = row.get("source_attribution_by_horizon")
    return isinstance(value, Mapping) and bool(value)


def _is_trusted_outcome(row: Mapping[str, Any]) -> bool:
    source = str(row.get("observation_source") or "").strip().lower()
    if source == "candle_summary":
        return True
    summary = row.get("observation_summary")
    if isinstance(summary, Mapping):
        nested = str(summary.get("observation_source") or "").strip().lower()
        return nested == "candle_summary"
    return False


def _writer_safety() -> dict[str, Any]:
    return {
        "reads_derived_trace_rows_only": True,
        "reads_derived_outcome_rows_only": True,
        "writes_source_scorecard_read_model_only": True,
        "raw_market_data_read": False,
        "raw_market_data_duplicated": False,
        "scheduler_enabled": False,
        "producer_enabled": False,
        "broker_private_api_allowed": False,
        "autotrade_trigger_allowed": False,
        "order_intent_submitted": False,
        "parameter_auto_promotion_allowed": False,
        "live_parameter_apply_allowed": False,
        "human_gate_required": True,
        "would_send_to_broker": False,
    }


def _write_json_atomic(path: Path, payload: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + ".tmp")
    tmp.write_text(
        json.dumps(payload, ensure_ascii=False, sort_keys=True, indent=2) + "\n",
        encoding="utf-8",
    )
    tmp.replace(path)


def build_market_regime_current_primary_source_scorecard_artifact_write_plan(
    root: str | Path,
    *,
    current_cutoff: str = CURRENT_PRIMARY_COHORT_STARTED_AT,
    min_trusted_samples: int = 20,
) -> dict[str, Any]:
    base = Path(root)
    cutoff = _parse_utc(current_cutoff)
    if cutoff is None:
        raise ValueError("current_cutoff must be a valid timestamp")

    trace_rows_all = _iter_jsonl(
        base.glob("prediction/market_regime/ledgers/date=*/hour=*/part-*.jsonl")
    )
    outcome_rows_all = _iter_jsonl(
        base.glob("prediction/market_regime/outcomes/date=*/part-*.jsonl")
    )
    trace_rows = [
        row for row in trace_rows_all
        if _has_source_attribution(row) and _is_current(row, cutoff)
    ]
    outcome_rows = [
        row for row in outcome_rows_all
        if _is_current(row, cutoff) and _is_trusted_outcome(row)
    ]

    pipeline = build_market_regime_source_scorecard_pipeline(
        trace_rows=trace_rows,
        outcome_rows=outcome_rows,
        min_trusted_samples=min_trusted_samples,
    )
    read_model = {
        "schema_version": "market_regime_source_scorecard_current_primary.2026_07_10.v1",
        "artifact_family": "prediction/market_regime",
        "artifact_kind": "source_scorecard_current_primary_read_model",
        "prediction_family_id": "market_regime",
        "source_scorecard_artifact_writer_version": MARKET_REGIME_SOURCE_SCORECARD_ARTIFACT_WRITER_VERSION,
        "source_scorecard_pipeline_version": MARKET_REGIME_SOURCE_SCORECARD_PIPELINE_VERSION,
        "current_primary_cohort_started_at": current_cutoff,
        "minimum_trusted_sample_count": int(min_trusted_samples),
        "trace_row_count": len(trace_rows),
        "outcome_row_count": len(outcome_rows),
        "pipeline": pipeline,
        "source_progress": list(pipeline.get("source_progress") or []),
        "source_scorecards": list((pipeline.get("scorecard") or {}).get("source_scorecards") or []),
        "comparison_ready": bool(pipeline.get("pipeline_ready")),
        "comparison_blockers": list(pipeline.get("pipeline_blockers") or []),
        "ready_source_count": int(pipeline.get("ready_source_count") or 0),
        "source_count": int(pipeline.get("source_count") or 0),
        "auto_apply_allowed": False,
        "auto_promotion_allowed": False,
        "safety": _writer_safety(),
    }
    relpath = source_scorecard_current_primary_relpath()
    return {
        "ok": True,
        "source_scorecard_artifact_writer_version": MARKET_REGIME_SOURCE_SCORECARD_ARTIFACT_WRITER_VERSION,
        "preflight_only": True,
        "would_write": False,
        "current_cutoff": current_cutoff,
        "min_trusted_samples": int(min_trusted_samples),
        "trace_row_count": len(trace_rows),
        "outcome_row_count": len(outcome_rows),
        "comparison_ready": read_model["comparison_ready"],
        "comparison_blockers": read_model["comparison_blockers"],
        "ready_source_count": read_model["ready_source_count"],
        "source_count": read_model["source_count"],
        "source_scorecard_current_primary_json": relpath,
        "read_model": read_model,
        "safety": _writer_safety(),
    }


def preflight_market_regime_current_primary_source_scorecard(
    root: str | Path,
    *,
    current_cutoff: str = CURRENT_PRIMARY_COHORT_STARTED_AT,
    min_trusted_samples: int = 20,
) -> dict[str, Any]:
    plan = build_market_regime_current_primary_source_scorecard_artifact_write_plan(
        root,
        current_cutoff=current_cutoff,
        min_trusted_samples=min_trusted_samples,
    )
    return {key: value for key, value in plan.items() if key != "read_model"}


def write_market_regime_current_primary_source_scorecard(
    root: str | Path,
    *,
    current_cutoff: str = CURRENT_PRIMARY_COHORT_STARTED_AT,
    min_trusted_samples: int = 20,
) -> dict[str, Any]:
    base = Path(root)
    plan = build_market_regime_current_primary_source_scorecard_artifact_write_plan(
        base,
        current_cutoff=current_cutoff,
        min_trusted_samples=min_trusted_samples,
    )
    relpath = str(plan["source_scorecard_current_primary_json"])
    _write_json_atomic(base / relpath, plan["read_model"])
    return {
        key: value
        for key, value in plan.items()
        if key != "read_model"
    } | {
        "preflight_only": False,
        "would_write": True,
    }
