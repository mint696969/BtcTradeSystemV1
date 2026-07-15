# path: ./btcts_next/src/btcts/prediction/market_regime/tools/shadow_pair_once.py
# desc: Manual read-only MR-F8.6 tool that validates explicit origin-evidence JSON and emits paired active/shadow forecasts without writing D-hot.

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Mapping, Sequence

from btcts.prediction.market_regime.contracts import MarketRegimeCode
from btcts.prediction.market_regime.future_baseline_model import FutureBaselineEvidence
from btcts.prediction.market_regime.future_shadow_candidate_pairing import build_future_shadow_candidate_pair
from btcts.prediction.market_regime.future_shadow_pair_trace_plan import build_future_shadow_pair_trace_plan

MARKET_REGIME_SHADOW_PAIR_ONCE_TOOL_VERSION = (
    "prediction.market_regime.tools.shadow_pair_once.mr_f8_6.v1"
)


def _mapping(value: Any, error: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise ValueError(error)
    return value


def _sequence(value: Any, error: str) -> Sequence[Any]:
    if isinstance(value, (str, bytes)) or not isinstance(value, Sequence):
        raise ValueError(error)
    return value


def _load_json(path: str | Path) -> Any:
    return json.loads(Path(path).read_text(encoding="utf-8-sig"))


def _evidence_from_bundle(bundle: Mapping[str, Any]) -> FutureBaselineEvidence:
    if bundle.get("artifact_kind") != "future_origin_evidence_bundle":
        raise ValueError("shadow_pair_once_origin_bundle_kind_invalid")
    snapshot = _mapping(bundle.get("feature_snapshot"), "shadow_pair_once_feature_snapshot_missing")
    probabilities = _mapping(
        bundle.get("candidate_probability_by_state"),
        "shadow_pair_once_probability_distribution_missing",
    )
    regime_scores: dict[MarketRegimeCode, float] = {}
    for raw_state, raw_value in probabilities.items():
        state = raw_state if isinstance(raw_state, MarketRegimeCode) else MarketRegimeCode(str(raw_state))
        if state is not MarketRegimeCode.UNKNOWN:
            regime_scores[state] = float(raw_value)
    if not regime_scores:
        raise ValueError("shadow_pair_once_probability_distribution_empty")

    available = snapshot.get("available_feature_families")
    if available is None:
        available = tuple(
            family
            for family in ("price_structure", "volatility", "liquidity", "source_quality", "microprice")
            if snapshot.get(family) not in (None, {}, [])
        )
    families = tuple(str(item) for item in _sequence(available, "shadow_pair_once_feature_families_invalid"))
    if not families:
        raise ValueError("shadow_pair_once_feature_families_missing")

    origin = str(bundle.get("prediction_origin") or "").strip()
    snapshot_ref = str(bundle.get("feature_snapshot_ref") or "").strip()
    horizon = int(bundle.get("target_horizon_sec") or 0)
    current_state_raw = str(snapshot.get("origin_current_state") or bundle.get("origin_current_state") or "UNKNOWN")
    source_epoch = snapshot.get("source_timestamp_epoch_sec")
    origin_epoch = snapshot.get("origin_timestamp_epoch_sec")
    if not origin or not snapshot_ref or horizon <= 0:
        raise ValueError("shadow_pair_once_origin_identity_missing")
    if source_epoch is None or origin_epoch is None:
        raise ValueError("shadow_pair_once_epoch_identity_missing")

    return FutureBaselineEvidence(
        origin_timestamp=origin,
        origin_current_state=MarketRegimeCode(current_state_raw),
        target_horizon_sec=horizon,
        feature_snapshot_ref=snapshot_ref,
        regime_scores=regime_scores,
        available_feature_families=families,
        source_timestamp_epoch_sec=float(source_epoch),
        origin_timestamp_epoch_sec=float(origin_epoch),
    )


def build_shadow_pair_once_report(*, input_payload: Any) -> Mapping[str, Any]:
    if isinstance(input_payload, Mapping) and input_payload.get("artifact_kind") == "future_origin_evidence_batch":
        rows = _sequence(input_payload.get("rows"), "shadow_pair_once_batch_rows_invalid")
    elif isinstance(input_payload, Mapping) and input_payload.get("artifact_kind") == "future_origin_evidence_bundle":
        rows = (input_payload,)
    else:
        raise ValueError("shadow_pair_once_input_kind_invalid")
    if not rows:
        raise ValueError("shadow_pair_once_input_rows_empty")

    pairs = []
    seen_bundle_ids: set[str] = set()
    for raw in rows:
        bundle = _mapping(raw, "shadow_pair_once_bundle_invalid")
        bundle_id = str(bundle.get("bundle_id") or "").strip()
        if not bundle_id:
            raise ValueError("shadow_pair_once_bundle_id_missing")
        if bundle_id in seen_bundle_ids:
            raise ValueError("shadow_pair_once_duplicate_bundle_id")
        seen_bundle_ids.add(bundle_id)
        pair = build_future_shadow_candidate_pair(evidence=_evidence_from_bundle(bundle))
        trace_plan = build_future_shadow_pair_trace_plan(pair=pair)
        pairs.append({"source_bundle_id": bundle_id, **dict(pair), "trace_plan": trace_plan})

    return {
        "schema_version": "market_regime_shadow_pair_once_report.mr_f8_6.v1",
        "tool_version": MARKET_REGIME_SHADOW_PAIR_ONCE_TOOL_VERSION,
        "ok": True,
        "pair_count": len(pairs),
        "pairs": pairs,
        "comparison_ready_for_outcome_join_count": sum(
            1 for pair in pairs if pair.get("comparison_ready_for_outcome_join") is True
        ),
        "trace_plan_ready_count": sum(
            1 for pair in pairs if pair.get("trace_plan", {}).get("persistence_plan", {}).get("would_write") is False
        ),
        "safety": {
            "read_only": True,
            "writes_hot_data": False,
            "trace_writer_invoked": False,
            "writes_repository": False,
            "scheduler_enabled": False,
            "producer_loop_enabled": False,
            "broker_private_api_allowed": False,
            "autotrade_trigger_allowed": False,
            "order_submission_allowed": False,
            "parameter_auto_promotion_allowed": False,
            "live_parameter_apply_allowed": False,
        },
    }


def _json_default(value: Any) -> Any:
    if isinstance(value, Mapping):
        return dict(value)
    raise TypeError(f"shadow_pair_once_json_type_unsupported:{type(value).__name__}")


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Generate MR-F8 paired active/shadow forecasts from explicit origin-evidence JSON without writes."
    )
    parser.add_argument("--input-json", required=True)
    parser.add_argument(
        "--preflight",
        action="store_true",
        help="Required acknowledgement that this command is read-only and does not persist evidence.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)
    if not args.preflight:
        parser.error("--preflight is required; this MR-F8.6 tool never writes D-hot")
    report = build_shadow_pair_once_report(input_payload=_load_json(args.input_json))
    print(json.dumps(report, ensure_ascii=False, sort_keys=True, default=_json_default))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
