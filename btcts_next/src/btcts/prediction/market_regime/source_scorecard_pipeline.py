# path: ./btcts_next/src/btcts/prediction/market_regime/source_scorecard_pipeline.py
# desc: Pure/read-only MR-VS4 orchestration from trace rows and trusted outcomes to source scorecard readiness with explicit sample deficits.

from __future__ import annotations

from typing import Any, Iterable, Mapping

from .source_attribution_adapter import expand_market_regime_trace_source_attribution_rows
from .source_scorecard_read_model import build_market_regime_source_scorecard_read_model

MARKET_REGIME_SOURCE_SCORECARD_PIPELINE_VERSION = "prediction.market_regime.source_scorecard_pipeline.2026_07_10.v1"


def build_market_regime_source_scorecard_pipeline(
    *,
    trace_rows: Iterable[Mapping[str, Any]],
    outcome_rows: Iterable[Mapping[str, Any]],
    min_trusted_samples: int = 20,
) -> dict[str, Any]:
    """Build a fail-closed scorecard pipeline summary without runtime I/O or mutation."""

    adapter = expand_market_regime_trace_source_attribution_rows(trace_rows)
    scorecard = build_market_regime_source_scorecard_read_model(
        outcome_rows=outcome_rows,
        attribution_rows=adapter["rows"],
        min_trusted_samples=min_trusted_samples,
    )

    scorecard_by_source = {
        str(row.get("source_id") or ""): row
        for row in scorecard["source_scorecards"]
        if str(row.get("source_id") or "")
    }
    observed_source_ids = sorted({
        str(source_id)
        for attribution_row in adapter["rows"]
        for source_id in (
            attribution_row.get("source_signals", {}).keys()
            if isinstance(attribution_row.get("source_signals"), Mapping)
            else []
        )
        if str(source_id)
    })
    source_ids = sorted(set(observed_source_ids) | set(scorecard_by_source))

    source_progress: list[dict[str, Any]] = []
    for source_id in source_ids:
        row = scorecard_by_source.get(source_id, {})
        trusted = int(row.get("trusted_sample_count") or 0)
        minimum = int(row.get("minimum_trusted_sample_count") or min_trusted_samples)
        source_progress.append({
            "source_id": source_id,
            "trusted_sample_count": trusted,
            "minimum_trusted_sample_count": minimum,
            "remaining_trusted_samples": max(minimum - trusted, 0),
            "ready": trusted >= minimum,
        })

    blockers = list(scorecard["comparison_blockers"])
    if not adapter["ok"]:
        blockers.append("source_attribution_adapter_rejected_rows")
    blockers = list(dict.fromkeys(blockers))

    pipeline_ready = bool(adapter["ok"] and scorecard["comparison_ready"])
    return {
        "schema_version": "market_regime_source_scorecard_pipeline.2026_07_10.v1",
        "source_scorecard_pipeline_version": MARKET_REGIME_SOURCE_SCORECARD_PIPELINE_VERSION,
        "pipeline_ready": pipeline_ready,
        "pipeline_blockers": blockers,
        "minimum_trusted_sample_count": int(min_trusted_samples),
        "adapter": {
            "ok": bool(adapter["ok"]),
            "row_count": int(adapter["row_count"]),
            "rejected_row_count": int(adapter["rejected_row_count"]),
            "rejected_rows": list(adapter["rejected_rows"]),
            "version": str(adapter["source_attribution_adapter_version"]),
        },
        "scorecard": scorecard,
        "source_progress": source_progress,
        "ready_source_count": sum(1 for row in source_progress if row["ready"]),
        "source_count": len(source_progress),
        "safety": {
            "read_only": True,
            "writes_dhot": False,
            "producer_enabled": False,
            "broker_private_api_allowed": False,
            "autotrade_trigger_allowed": False,
            "order_intent_submitted": False,
            "parameter_auto_promotion_allowed": False,
            "live_parameter_apply_allowed": False,
            "human_gate_required": True,
        },
    }
