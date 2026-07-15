# path: ./btcts_next/src/btcts/prediction/market_regime/tools/shadow_runtime_preflight_once.py
# desc: MR-F8.8 read-only one-shot runtime assembly from an explicit hot root to paired shadow preflight JSON.

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping

from btcts.prediction.market_regime.current_state_persistence import read_persisted_current_state
from btcts.prediction.market_regime.features import build_market_regime_feature_bundle
from btcts.prediction.market_regime.features.current_l4_candle_window import current_l4_candle_rows
from btcts.prediction.market_regime.future_origin_feature_runtime_bundle import (
    build_market_regime_origin_feature_runtime_bundle,
)
from btcts.prediction.market_regime.future_shadow_adapter import build_market_regime_future_shadow_packet
from btcts.prediction.market_regime.future_shadow_runtime_preflight_bridge import (
    build_future_shadow_runtime_preflight_report,
)
from btcts.prediction.market_regime.inference import classify_market_regime_feature_bundle
from btcts.prediction.market_regime.parameter_set_registry import (
    build_default_market_regime_parameter_set_registry,
)
from btcts.prediction.market_regime.signal_scoring import score_market_regime_signals
from btcts.prediction.market_regime.sources import build_market_regime_source_snapshot

MR_F8_RUNTIME_PREFLIGHT_ONCE_TOOL_VERSION = (
    "prediction.market_regime.tools.shadow_runtime_preflight_once.mr_f8_8.v1"
)


def _parse_epoch(value: str, field: str) -> float:
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ValueError(f"mr_f8_runtime_once_timestamp_invalid:{field}") from exc
    if parsed.tzinfo is None:
        raise ValueError(f"mr_f8_runtime_once_timestamp_timezone_missing:{field}")
    return parsed.astimezone(timezone.utc).timestamp()


def _signal_value(feature_bundle: Any, name: str) -> Any:
    matches = tuple(signal for signal in feature_bundle.signals if signal.name == name and signal.available)
    if len(matches) != 1:
        raise ValueError(f"mr_f8_runtime_once_signal_invalid:{name}:count={len(matches)}")
    return matches[0].value


def _current_regime(prediction_packet: Any) -> Any:
    matches = tuple(item for item in prediction_packet.predictions if int(item.horizon_sec) == 0)
    if len(matches) != 1:
        raise ValueError("mr_f8_runtime_once_current_prediction_invalid")
    return matches[0].regime_code


def build_shadow_runtime_preflight_once(
    *,
    hot_root: str | Path,
    generated_at: str,
    shadow_candidate_id: str,
) -> Mapping[str, Any]:
    root = Path(hot_root)
    if not generated_at.strip():
        raise ValueError("mr_f8_runtime_once_generated_at_missing")
    if not shadow_candidate_id.strip():
        raise ValueError("mr_f8_runtime_once_shadow_candidate_missing")

    registry = build_default_market_regime_parameter_set_registry()
    active_parameter_set = registry.active_parameter_set()
    source_snapshot = build_market_regime_source_snapshot(root)
    feature_bundle = build_market_regime_feature_bundle(
        source_snapshot,
        generated_at=generated_at,
        parameter_set=active_parameter_set,
    )
    previous_current_state = read_persisted_current_state(root)
    prediction_packet = classify_market_regime_feature_bundle(
        feature_bundle,
        generated_at=generated_at,
        previous_current_state=previous_current_state,
    )
    signal_score_report = score_market_regime_signals(feature_bundle)
    source_timestamp = str(_signal_value(feature_bundle, "current_l4_candle_window_generated_at") or "")
    origin_epoch = _parse_epoch(generated_at, "generated_at")
    source_epoch = _parse_epoch(source_timestamp, "source_timestamp")
    shadow_packet = build_market_regime_future_shadow_packet(
        feature_bundle=feature_bundle,
        signal_score_report=signal_score_report,
        origin_current_state=_current_regime(prediction_packet),
        origin_timestamp_epoch_sec=origin_epoch,
        source_timestamp_epoch_sec=source_epoch,
    )
    runtime_bundle = build_market_regime_origin_feature_runtime_bundle(
        feature_bundle=feature_bundle,
        previous_current_state=previous_current_state,
        canonical_current_l4_candle_rows=current_l4_candle_rows(source_snapshot),
        shadow_candidate_id=shadow_candidate_id,
    )
    preflight = build_future_shadow_runtime_preflight_report(
        packet=shadow_packet,
        signal_score_report=signal_score_report,
        runtime_bundle=runtime_bundle,
    )
    return {
        "schema_version": MR_F8_RUNTIME_PREFLIGHT_ONCE_TOOL_VERSION,
        "artifact_kind": "mr_f8_runtime_preflight_once_result",
        "hot_root": str(root),
        "generated_at": generated_at,
        "shadow_candidate_id": shadow_candidate_id,
        "source_snapshot_ok": source_snapshot.ok,
        "feature_signal_count": feature_bundle.available_signal_count(),
        "current_regime": _current_regime(prediction_packet).value,
        "pair_count": preflight["pair_count"],
        "preflight_report": preflight,
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
    }


def _json_default(value: Any) -> Any:
    if isinstance(value, Mapping):
        return dict(value)
    if isinstance(value, tuple):
        return list(value)
    if hasattr(value, "to_dict"):
        return value.to_dict()
    raise TypeError(f"mr_f8_runtime_once_json_type_unsupported:{type(value).__name__}")


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Build MR-F8 runtime paired-shadow preflight JSON from an explicit hot root without writes."
    )
    parser.add_argument("--hot-root", required=True)
    parser.add_argument("--generated-at", required=True)
    parser.add_argument("--shadow-candidate-id", required=True)
    parser.add_argument("--preflight", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)
    if not args.preflight:
        parser.error("--preflight is required; writer and scheduler are unavailable")
    result = build_shadow_runtime_preflight_once(
        hot_root=args.hot_root,
        generated_at=args.generated_at,
        shadow_candidate_id=args.shadow_candidate_id,
    )
    print(json.dumps(result, ensure_ascii=False, sort_keys=True, default=_json_default))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
