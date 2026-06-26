# path: ./tools/diagnose_phase4a_prediction_system_ps_q21h_bounded_manual_refresh_export_preflight_dry_run.py
# desc: PS-Q21H read-only bounded manual refresh export preflight dry-run. It builds PredictionSystemResult in memory and runs export preflight only; no artifact write/export/status write/scheduler/producer/AutoTrade/broker.

from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from typing import Any, Mapping

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC = REPO_ROOT / "btcts_next" / "src"
for candidate in (REPO_ROOT, SRC):
    if str(candidate) not in sys.path:
        sys.path.insert(0, str(candidate))

from btcts.apps.operator_ui.components.prediction_warroom_latest_payload_export_preflight_bridge import (  # noqa: E402
    LATEST_PAYLOAD_EXPORT_PREFLIGHT_BRIDGE_VERSION,
    build_prediction_warroom_latest_payload_export_preflight_bridge,
)

DIAGNOSTIC_VERSION = "prediction_warroom.bounded_manual_refresh_export_preflight_dry_run.ps_q21h.v1"
DEFAULT_HOT_ROOT = Path(r"D:\btc_ts_hot")


def _as_mapping(value: Any) -> Mapping[str, Any]:
    if hasattr(value, "to_dict"):
        converted = value.to_dict()
        return converted if isinstance(converted, Mapping) else {}
    return value if isinstance(value, Mapping) else {}


def _str_list(value: Any) -> list[str]:
    if isinstance(value, list | tuple):
        return [str(item) for item in value if item]
    return []


def build_bounded_manual_refresh_export_preflight_dry_run(*, preflight_bridge_packet: Mapping[str, Any] | Any) -> dict[str, Any]:
    bridge = _as_mapping(preflight_bridge_packet)
    builder = _as_mapping(bridge.get("builder_runner_packet"))
    export_preflight = _as_mapping(bridge.get("export_preflight_packet"))
    payload = _as_mapping(builder.get("prediction_result_payload"))
    run_identity = _as_mapping(payload.get("run_identity"))
    bridge_blockers = _str_list(bridge.get("blocked_reasons"))
    builder_blockers = _str_list(builder.get("blocked_reasons"))
    export_blockers = _str_list(export_preflight.get("blocked_reasons"))
    bridge_warnings = _str_list(bridge.get("warning_reasons"))
    builder_warnings = _str_list(builder.get("warning_reasons"))
    export_warnings = _str_list(export_preflight.get("warning_reasons"))
    combined_blockers = list(dict.fromkeys(bridge_blockers + builder_blockers + export_blockers))
    combined_warnings = list(dict.fromkeys(bridge_warnings + builder_warnings + export_warnings))
    ready_for_export_runner = bool(bridge.get("ready_for_future_non_ui_export_runner")) and not combined_blockers
    payload_present = bool(payload)
    output_count = len(payload.get("outputs", [])) if isinstance(payload.get("outputs", []), list) else int(bridge.get("output_count") or 0)
    if ready_for_export_runner and payload_present:
        diagnosis_state = "bounded_manual_refresh_export_preflight_ready_no_write"
        next_action = "Manual latest prediction artifact write can be considered only with explicit operator approval and guards."
    elif payload_present:
        diagnosis_state = "bounded_manual_refresh_export_preflight_blocked_after_payload_build"
        next_action = "Fix export preflight blockers before any manual write."
    else:
        diagnosis_state = "bounded_manual_refresh_export_preflight_blocked_before_payload_build"
        next_action = "Fix prediction build/source blockers before any manual write."
    return {
        "ok": True,
        "diagnostic_version": DIAGNOSTIC_VERSION,
        "preflight_bridge_version": LATEST_PAYLOAD_EXPORT_PREFLIGHT_BRIDGE_VERSION,
        "diagnosis_state": diagnosis_state,
        "hot_root": str(bridge.get("hot_latest_root_hint") or ""),
        "bridge_state": str(bridge.get("bridge_state") or ""),
        "builder_runner_state": str(builder.get("runner_state") or ""),
        "export_preflight_state": str(export_preflight.get("contract_state") or ""),
        "prediction_result_payload_present": payload_present,
        "prediction_run_id": str(run_identity.get("prediction_run_id") or bridge.get("prediction_run_id") or ""),
        "generated_at": str(run_identity.get("generated_at") or bridge.get("generated_at") or ""),
        "market_uid": str(run_identity.get("market_uid") or bridge.get("market_uid") or ""),
        "output_count": output_count,
        "prediction_result_blocker_count": int(builder.get("prediction_result_blocker_count") or 0),
        "prediction_result_warning_count": int(bridge.get("prediction_result_warning_count") or 0),
        "ready_for_future_latest_payload_export_preflight": bool(bridge.get("ready_for_future_latest_payload_export_preflight")),
        "ready_for_future_non_ui_export_runner": ready_for_export_runner,
        "ready_for_bounded_manual_refresh_write_step": ready_for_export_runner,
        "combined_blocker_count": len(combined_blockers),
        "combined_warning_count": len(combined_warnings),
        "bridge_blockers": bridge_blockers,
        "builder_blockers": builder_blockers,
        "export_preflight_blockers": export_blockers,
        "combined_blockers": combined_blockers,
        "combined_warnings": combined_warnings,
        "target_artifact_path_hint": str(export_preflight.get("target_artifact_path_hint") or ""),
        "observed_expected_artifact_exists": export_preflight.get("observed_expected_artifact_exists"),
        "next_recommended_action": next_action,
        "actual_read_performed": True,
        "prediction_build_in_memory_attempted": True,
        "prediction_build_in_memory_performed": bool(builder.get("prediction_system_result_built_by_this_runner")) or payload_present,
        "export_preflight_contract_attempted": True,
        "export_preflight_contract_performed": bool(export_preflight),
        "latest_payload_export_requested": False,
        "runtime_artifact_write_requested": False,
        "target_file_written": False,
        "status_artifact_written": False,
        "read_only_diagnostic_only": True,
        "stdout_json_only": True,
        "latest_prediction_artifact_export_allowed": False,
        "runtime_artifact_write_allowed": False,
        "status_artifact_write_allowed": False,
        "prediction_artifact_write_allowed": False,
        "scheduler_enablement_allowed": False,
        "producer_enablement_allowed": False,
        "warroom_ui_trigger_allowed": False,
        "approval_or_ledger_allowed": False,
        "autotrade_trigger_allowed": False,
        "broker_private_api_allowed": False,
        "would_send_to_broker": False,
    }


def run_diagnostic(*, hot_root: Path | None = None) -> dict[str, Any]:
    root_hint = hot_root or os.environ.get("BTCTS_HOT_ROOT") or os.environ.get("BTC_TS_HOT_ROOT") or DEFAULT_HOT_ROOT
    bridge = build_prediction_warroom_latest_payload_export_preflight_bridge(
        hot_latest_root_hint=str(root_hint),
        operator_acknowledged=True,
        allow_actual_read=True,
        allow_prediction_build=True,
        allow_export_preflight=True,
        allow_guard_test_root=False,
        requested_latest_payload_export=False,
        requested_runtime_write=False,
        requested_warroom_ui_trigger=False,
        requested_approval_or_ledger_or_autotrade_or_broker=False,
    ).to_dict()
    return build_bounded_manual_refresh_export_preflight_dry_run(preflight_bridge_packet=bridge)


def main() -> int:
    result = run_diagnostic()
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if result.get("ok") is True else 1


if __name__ == "__main__":
    raise SystemExit(main())
