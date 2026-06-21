# path: ./tools/check_phase4a_prediction_system_ps_q12c_warroom_live_inference_smoke.py
# desc: PS-Q12C operator smoke for WarRoom live inference read-only display path. Reads D-hot latest prediction through PS-Q12A adapter only, reports readiness for PS-Q12B/Q9G WarRoom display, and never writes runtime artifacts or touches AutoTrade/broker/ledger.

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Mapping

from _btcts_bootstrap import ensure_btcts_on_syspath

ensure_btcts_on_syspath()

from btcts.apps.operator_ui.components.prediction_warroom_latest_prediction_source_adapter import (  # noqa: E402
    LATEST_PREDICTION_SOURCE_ADAPTER_VERSION,
    build_prediction_warroom_latest_prediction_source_adapter,
)
from btcts.apps.operator_ui.components.prediction_warroom_l4_latest_adapter import (  # noqa: E402
    DEFAULT_HOT_LATEST_ROOT_HINT,
)

SMOKE_VERSION = "prediction_system_ps_q12c_warroom_live_inference_smoke.v1"


def _as_mapping(value: Any) -> Mapping[str, Any]:
    if hasattr(value, "to_dict"):
        converted = value.to_dict()
        return converted if isinstance(converted, Mapping) else {}
    return value if isinstance(value, Mapping) else {}


def _list(value: Any) -> list[Any]:
    return list(value) if isinstance(value, (list, tuple)) else []


def _artifact_status(adapter_packet: Mapping[str, Any]) -> list[dict[str, Any]]:
    loader = _as_mapping(adapter_packet.get("loader_result"))
    rows: list[dict[str, Any]] = []
    for raw in _list(loader.get("artifact_results")):
        item = _as_mapping(raw)
        rows.append(
            {
                "artifact_role": item.get("artifact_role"),
                "loader_state": item.get("loader_state"),
                "path_exists": item.get("path_exists"),
                "observed_file_size_bytes": item.get("observed_file_size_bytes"),
                "observed_age_sec": item.get("observed_age_sec"),
                "observed_last_modified_at": item.get("observed_last_modified_at"),
                "actual_file_read_attempted": item.get("actual_file_read_attempted"),
                "actual_file_read_succeeded": item.get("actual_file_read_succeeded"),
                "payload_decode_attempted": item.get("payload_decode_attempted"),
                "payload_decode_succeeded": item.get("payload_decode_succeeded"),
                "blocker_reasons": _list(item.get("blocker_reasons")),
                "warning_reasons": _list(item.get("warning_reasons")),
            }
        )
    return rows


def _boundary_summary(adapter_packet: Mapping[str, Any]) -> dict[str, bool]:
    return {
        "read_only": adapter_packet.get("read_only") is True,
        "non_executing": adapter_packet.get("non_executing") is True,
        "source_adapter_only": adapter_packet.get("source_adapter_only") is True,
        "in_memory_result_only": adapter_packet.get("in_memory_result_only") is True,
        "runtime_artifact_write_allowed_false": adapter_packet.get("runtime_artifact_write_allowed") is False,
        "ledger_append_allowed_false": adapter_packet.get("ledger_append_allowed") is False,
        "autotrade_trigger_allowed_false": adapter_packet.get("autotrade_trigger_allowed") is False,
        "broker_private_api_allowed_false": adapter_packet.get("broker_private_api_allowed") is False,
        "would_write_runtime_artifact_false": adapter_packet.get("would_write_runtime_artifact") is False,
        "would_write_collector_state_false": adapter_packet.get("would_write_collector_state") is False,
        "would_send_to_broker_false": adapter_packet.get("would_send_to_broker") is False,
        "broker_execution_requested_false": adapter_packet.get("broker_execution_requested") is False,
        "mode_apply_requested_false": adapter_packet.get("mode_apply_requested") is False,
        "command_ledger_append_requested_false": adapter_packet.get("command_ledger_append_requested") is False,
        "approval_append_requested_false": adapter_packet.get("approval_append_requested") is False,
        "authorization_grant_requested_false": adapter_packet.get("authorization_grant_requested") is False,
        "autotrade_trigger_enabled_false": adapter_packet.get("autotrade_trigger_enabled") is False,
    }


def build_warroom_live_inference_smoke_payload(*, hot_latest_root_hint: str = DEFAULT_HOT_LATEST_ROOT_HINT) -> dict[str, Any]:
    """Build a read-only operator smoke payload for the same adapter path used by WarRoom."""
    session_state: dict[str, Any] = {}
    adapter = build_prediction_warroom_latest_prediction_source_adapter(
        hot_latest_root_hint=hot_latest_root_hint,
        allow_actual_read=True,
        session_state=session_state,
        store_in_session_state=True,
    ).to_dict()
    summary = _as_mapping(adapter.get("source_summary"))
    boundary = _boundary_summary(adapter)
    ready = bool(
        adapter.get("ready_for_warroom_review_panel")
        and adapter.get("review_packet_ready")
        and adapter.get("session_state_updated")
        and adapter.get("actual_file_read_succeeded")
        and adapter.get("payload_decode_succeeded")
        and int(adapter.get("blocker_count") or 0) == 0
        and all(boundary.values())
    )
    return {
        "ok": ready,
        "smoke_version": SMOKE_VERSION,
        "adapter_version": LATEST_PREDICTION_SOURCE_ADAPTER_VERSION,
        "hot_latest_root_hint": str(hot_latest_root_hint),
        "expected_prediction_path": str(Path(str(hot_latest_root_hint)) / "prediction" / "latest_prediction_system_result.json"),
        "adapter_state": adapter.get("adapter_state"),
        "ready_for_warroom_review_panel": adapter.get("ready_for_warroom_review_panel"),
        "review_packet_ready": adapter.get("review_packet_ready"),
        "session_state_updated": adapter.get("session_state_updated"),
        "actual_file_read_attempted": adapter.get("actual_file_read_attempted"),
        "actual_file_read_succeeded": adapter.get("actual_file_read_succeeded"),
        "payload_decode_attempted": adapter.get("payload_decode_attempted"),
        "payload_decode_succeeded": adapter.get("payload_decode_succeeded"),
        "loaded_payload_count": adapter.get("loaded_payload_count"),
        "blocker_count": adapter.get("blocker_count"),
        "warning_count": adapter.get("warning_count"),
        "blocked_reasons": _list(adapter.get("blocked_reasons")),
        "warning_reasons": _list(adapter.get("warning_reasons")),
        "source_summary": dict(summary),
        "artifact_status": _artifact_status(adapter),
        "session_state_keys": sorted(str(key) for key in session_state.keys()),
        "boundary": boundary,
        "operator_note": "read-only WarRoom inference smoke only; no runtime write, no approval, no ledger, no AutoTrade, no broker/private API",
    }


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="PS-Q12C WarRoom live inference read-only smoke")
    parser.add_argument("--hot-root", default=DEFAULT_HOT_LATEST_ROOT_HINT, help="Hot data root containing prediction/latest_prediction_system_result.json")
    parser.add_argument("--allow-blocked", action="store_true", help="Exit 0 even when smoke reports blocked; useful for inspection")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    payload = build_warroom_live_inference_smoke_payload(hot_latest_root_hint=str(args.hot_root))
    print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
    if payload["ok"] or args.allow_blocked:
        return 0
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
