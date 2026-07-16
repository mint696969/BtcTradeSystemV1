# path: ./btcts_next/src/btcts/prediction/market_regime/tools/shadow_runtime_preflight_once.py
# desc: MR-F8.8 read-only one-shot runtime assembly from an explicit hot root to paired shadow preflight JSON.

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from collections.abc import Mapping as MappingABC
from enum import Enum
from pathlib import Path
from types import MappingProxyType
from typing import Any, Mapping

from btcts.prediction.market_regime.current_state_persistence import read_persisted_current_state
from btcts.prediction.market_regime.features import build_market_regime_feature_bundle
from btcts.prediction.market_regime.features.current_l4_candle_window import future_origin_l4_candle_rows
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
from btcts.prediction.market_regime.runtime_horizon_artifact import (
    build_market_regime_runtime_horizon_artifact,
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


def _canonical_utc_seconds(value: str, field: str) -> str:
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ValueError(f"mr_f8_runtime_once_timestamp_invalid:{field}") from exc
    if parsed.tzinfo is None:
        raise ValueError(f"mr_f8_runtime_once_timestamp_timezone_missing:{field}")
    return (
        parsed.astimezone(timezone.utc)
        .replace(microsecond=0)
        .isoformat()
        .replace("+00:00", "Z")
    )


def _signal_value(feature_bundle: Any, name: str) -> Any:
    matches = tuple(signal for signal in feature_bundle.signals if signal.name == name and signal.available)
    if len(matches) != 1:
        raise ValueError(f"mr_f8_runtime_once_signal_invalid:{name}:count={len(matches)}")
    return matches[0].value


def _current_prediction(prediction_packet: Any) -> Any:
    matches = tuple(item for item in prediction_packet.predictions if int(item.horizon_sec) == 0)
    if len(matches) != 1:
        raise ValueError("mr_f8_runtime_once_current_prediction_invalid")
    return matches[0]


def _current_regime(prediction_packet: Any) -> Any:
    return _current_prediction(prediction_packet).regime_code


def _future_only_signal_score_report(signal_score_report: Mapping[str, Any]) -> Mapping[str, Any]:
    rows = signal_score_report.get("horizons")
    if not isinstance(rows, (tuple, list)):
        raise ValueError("mr_f8_runtime_once_signal_rows_missing")
    future_rows = []
    for row in rows:
        if not isinstance(row, Mapping):
            raise ValueError("mr_f8_runtime_once_signal_row_invalid")
        horizon = int(row.get("horizon_sec") or 0)
        if horizon == 0:
            continue
        future_rows.append(dict(row))
    if len(future_rows) != 7:
        raise ValueError(f"mr_f8_runtime_once_future_horizon_count_invalid:{len(future_rows)}")
    report = dict(signal_score_report)
    report["horizons"] = future_rows
    report["horizon_count"] = len(future_rows)
    return report


def build_shadow_runtime_preflight_once(
    *,
    hot_root: str | Path,
    generated_at: str,
    shadow_candidate_id: str,
) -> Mapping[str, Any]:
    root = Path(hot_root)
    if not generated_at.strip():
        raise ValueError("mr_f8_runtime_once_generated_at_missing")
    canonical_generated_at = _canonical_utc_seconds(generated_at, "generated_at")
    if not shadow_candidate_id.strip():
        raise ValueError("mr_f8_runtime_once_shadow_candidate_missing")

    registry = build_default_market_regime_parameter_set_registry()
    active_parameter_set = registry.active_parameter_set()
    source_snapshot = build_market_regime_source_snapshot(root)
    feature_bundle = build_market_regime_feature_bundle(
        source_snapshot,
        generated_at=canonical_generated_at,
        parameter_set=active_parameter_set,
    )
    previous_current_state = read_persisted_current_state(root)
    prediction_packet = classify_market_regime_feature_bundle(
        feature_bundle,
        generated_at=canonical_generated_at,
        previous_current_state=previous_current_state,
    )
    runtime_bundle = build_market_regime_origin_feature_runtime_bundle(
        feature_bundle=feature_bundle,
        previous_current_state=previous_current_state,
        canonical_current_l4_candle_rows=future_origin_l4_candle_rows(source_snapshot),
        shadow_candidate_id=shadow_candidate_id,
    )
    signal_score_report = score_market_regime_signals(
        feature_bundle,
        origin_feature_context=runtime_bundle,
    )
    future_signal_score_report = _future_only_signal_score_report(signal_score_report)
    source_timestamp = str(
        runtime_bundle.get("selected_candle_source_timestamp")
        or _signal_value(feature_bundle, "current_l4_candle_window_generated_at")
        or ""
    )
    origin_epoch = _parse_epoch(canonical_generated_at, "generated_at")
    source_epoch = _parse_epoch(source_timestamp, "source_timestamp")
    shadow_packet = build_market_regime_future_shadow_packet(
        feature_bundle=feature_bundle,
        signal_score_report=future_signal_score_report,
        origin_current_state=_current_regime(prediction_packet),
        origin_timestamp_epoch_sec=origin_epoch,
        source_timestamp_epoch_sec=source_epoch,
    )
    preflight = build_future_shadow_runtime_preflight_report(
        packet=shadow_packet,
        signal_score_report=future_signal_score_report,
        runtime_bundle=runtime_bundle,
    )
    runtime_horizon_artifact = build_market_regime_runtime_horizon_artifact(
        current_prediction=_current_prediction(prediction_packet),
        future_packet=shadow_packet,
        future_source_timestamp=source_timestamp,
        future_source_currentness_verified=bool(
            runtime_bundle.get("selected_window_is_latest_source", False)
        ),
    )
    return {
        "schema_version": MR_F8_RUNTIME_PREFLIGHT_ONCE_TOOL_VERSION,
        "artifact_kind": "mr_f8_runtime_preflight_once_result",
        "hot_root": str(root),
        "generated_at": canonical_generated_at,
        "shadow_candidate_id": shadow_candidate_id,
        "source_snapshot_ok": source_snapshot.ok,
        "feature_signal_count": feature_bundle.available_signal_count(),
        "current_regime": _current_regime(prediction_packet).value,
        "pair_count": preflight["pair_count"],
        "shadow_packet": _json_native(shadow_packet),
        "preflight_report": _json_native(preflight),
        "runtime_horizon_artifact": _json_native(runtime_horizon_artifact),
        "runtime_horizon_artifact_built": True,
        "runtime_horizon_artifact_persisted": False,
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


def _json_native(value: Any) -> Any:
    if isinstance(value, Enum):
        return value.value
    if isinstance(value, (MappingProxyType, MappingABC)):
        return {str(key): _json_native(item) for key, item in value.items()}
    if isinstance(value, (tuple, list)):
        return [_json_native(item) for item in value]
    if hasattr(value, "to_dict"):
        return _json_native(value.to_dict())
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
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
    print(json.dumps(_json_native(result), ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
