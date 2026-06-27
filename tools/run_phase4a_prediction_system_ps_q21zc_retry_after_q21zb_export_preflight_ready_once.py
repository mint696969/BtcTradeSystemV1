# path: ./tools/run_phase4a_prediction_system_ps_q21zc_retry_after_q21zb_export_preflight_ready_once.py
# desc: PS-Q21ZC exact-token one-shot retry wrapper after Q21ZB export-preflight ready. Default no write; no producer/scheduler/broker.

from __future__ import annotations

import argparse
from collections.abc import Callable
import json
from pathlib import Path
import subprocess
import sys
from typing import Any, Mapping

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC = REPO_ROOT / "btcts_next" / "src"
for candidate in (REPO_ROOT, SRC):
    if str(candidate) not in sys.path:
        sys.path.insert(0, str(candidate))

from btcts.apps.operator_ui.components.prediction_warroom_prediction_system_result_builder_runner import (  # noqa: E402
    build_prediction_warroom_prediction_system_result_builder_runner,
)
from btcts.apps.operator_ui.components.prediction_warroom_latest_payload_export_preflight_bridge import (  # noqa: E402
    build_prediction_warroom_latest_payload_export_preflight_bridge,
)
from tools.run_phase4a_prediction_system_ps_q21i_one_shot_bounded_manual_latest_prediction_write import (  # noqa: E402
    DEFAULT_HOT_ROOT,
    REQUIRED_CONFIRMATION,
    run_one_shot_write,
)
from tools.verify_phase4a_prediction_system_ps_q21u_scheduler_producer_registration_preflight import (  # noqa: E402
    REQUIRED_NEXT_PRODUCER_CONFIRMATION,
)

RETRY_VERSION = "prediction_warroom.retry_after_q21zb_export_preflight_ready.ps_q21zc.v1"
Q21IRunner = Callable[..., dict[str, Any]]


def _as_mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _false_boundary() -> dict[str, Any]:
    return {
        "producer_loop_enabled": False,
        "producer_runner_invoked": False,
        "scheduler_enabled": False,
        "scheduler_enablement_allowed_now": False,
        "trigger_added": False,
        "trigger_addition_allowed_now": False,
        "recurring_enablement_allowed_now": False,
        "warroom_ui_trigger_allowed": False,
        "approval_or_ledger_allowed": False,
        "parameter_apply_allowed": False,
        "parameter_staging_write_allowed": False,
        "autotrade_trigger_allowed": False,
        "broker_private_api_allowed": False,
        "would_send_to_broker": False,
        "would_write_collector_state": False,
    }


def build_q21zb_retry_diagnostic() -> dict[str, Any]:
    builder = build_prediction_warroom_prediction_system_result_builder_runner(
        hot_latest_root_hint=str(DEFAULT_HOT_ROOT),
        operator_acknowledged=True,
        allow_actual_read=True,
        allow_prediction_build=True,
        allow_guard_test_root=False,
        requested_latest_payload_export=False,
        requested_runtime_write=False,
        requested_warroom_ui_trigger=False,
        requested_approval_or_ledger_or_autotrade_or_broker=False,
    ).to_dict()
    bridge = build_prediction_warroom_latest_payload_export_preflight_bridge(
        hot_latest_root_hint=str(DEFAULT_HOT_ROOT),
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
    payload = builder.get("prediction_result_payload") if isinstance(builder.get("prediction_result_payload"), dict) else {}
    return {
        "ok": True,
        "payload_usable": payload.get("usable") is True,
        "payload_blockers": list(payload.get("blockers") or []),
        "builder_ready_for_future_latest_payload_export_preflight": builder.get("ready_for_future_latest_payload_export_preflight") is True,
        "bridge_ready_for_future_non_ui_export_runner": bridge.get("ready_for_future_non_ui_export_runner") is True,
        "bridge_blocked_reasons": list(bridge.get("blocked_reasons") or []),
        "bridge_state": str(bridge.get("bridge_state") or ""),
        "latest_prediction_artifact_written": False,
        "status_artifact_written": False,
        "would_send_to_broker": False,
    }


def _repo_clean() -> bool:
    proc = subprocess.run(["git", "status", "--short"], cwd=REPO_ROOT, text=True, capture_output=True, check=False)
    return proc.stdout.strip() == ""


def run_retry_after_q21zb_once(
    *,
    operator_acknowledged: bool = False,
    execute_retry_once: bool = False,
    allow_retry_after_q21zb_export_preflight_ready: bool = False,
    confirmation: str = "",
    diagnostic_packet: Mapping[str, Any] | None = None,
    q21i_runner: Q21IRunner | None = None,
    repo_clean: bool | None = None,
) -> dict[str, Any]:
    diag = dict(diagnostic_packet) if diagnostic_packet is not None else build_q21zb_retry_diagnostic()
    blockers: list[str] = []
    if not operator_acknowledged:
        blockers.append("operator_acknowledgement_required")
    if not execute_retry_once:
        blockers.append("execute_retry_once_flag_required")
    if not allow_retry_after_q21zb_export_preflight_ready:
        blockers.append("allow_retry_after_q21zb_export_preflight_ready_flag_required")
    if confirmation != REQUIRED_CONFIRMATION:
        blockers.append("exact_q21i_confirmation_token_required")
    repo_is_clean = _repo_clean() if repo_clean is None else bool(repo_clean)
    if not repo_is_clean:
        blockers.append("repo_clean_required_before_retry")
    if diag.get("payload_usable") is not True:
        blockers.append("q21zb_payload_usable_required")
    if diag.get("payload_blockers") not in ([], None):
        blockers.append("q21zb_payload_blockers_must_be_empty")
    if diag.get("bridge_ready_for_future_non_ui_export_runner") is not True:
        blockers.append("q21zb_bridge_ready_for_future_non_ui_export_runner_required")
    if diag.get("bridge_blocked_reasons") not in ([], None):
        blockers.append("q21zb_bridge_blockers_must_be_empty")
    if blockers:
        return {
            "ok": True,
            "retry_version": RETRY_VERSION,
            "retry_state": "retry_after_q21zb_blocked_no_write",
            "success": False,
            "blocked_reasons": blockers,
            "q21zb_diagnostic": diag,
            "q21i_runner_invoked": False,
            "latest_prediction_artifact_written": False,
            "status_artifact_written": False,
            "manual_refresh_confirmation_required": REQUIRED_CONFIRMATION,
            "required_next_producer_confirmation": REQUIRED_NEXT_PRODUCER_CONFIRMATION,
            **_false_boundary(),
        }
    runner = q21i_runner or run_one_shot_write
    q21i = runner(
        hot_root=DEFAULT_HOT_ROOT,
        operator_acknowledged=True,
        execute_one_shot_write=True,
        confirmation=REQUIRED_CONFIRMATION,
        require_clean_tree=True,
    )
    latest_written = q21i.get("latest_prediction_artifact_written") is True
    status_written = q21i.get("status_artifact_written") is True
    success = q21i.get("success") is True and latest_written and status_written
    return {
        "ok": True,
        "retry_version": RETRY_VERSION,
        "retry_state": "retry_after_q21zb_executed_existing_q21i_once" if success else "retry_after_q21zb_existing_q21i_failed_or_incomplete",
        "success": success,
        "blocked_reasons": [],
        "q21zb_diagnostic": diag,
        "q21i_runner_invoked": True,
        "q21i_result": q21i,
        "prediction_run_id": str(q21i.get("prediction_run_id") or ""),
        "generated_at": str(q21i.get("generated_at") or ""),
        "latest_prediction_artifact_written": latest_written,
        "status_artifact_written": status_written,
        "manual_refresh_confirmation_required": REQUIRED_CONFIRMATION,
        "required_next_producer_confirmation": REQUIRED_NEXT_PRODUCER_CONFIRMATION,
        **_false_boundary(),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="PS-Q21ZC one-shot retry after Q21ZB export-preflight ready")
    parser.add_argument("--operator-acknowledged", action="store_true")
    parser.add_argument("--execute-retry-once", action="store_true")
    parser.add_argument("--allow-retry-after-q21zb-export-preflight-ready", action="store_true")
    parser.add_argument("--confirmation", default="")
    args = parser.parse_args(argv)
    result = run_retry_after_q21zb_once(
        operator_acknowledged=args.operator_acknowledged,
        execute_retry_once=args.execute_retry_once,
        allow_retry_after_q21zb_export_preflight_ready=args.allow_retry_after_q21zb_export_preflight_ready,
        confirmation=args.confirmation,
    )
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True, default=str))
    return 0 if result.get("ok") is True and (result.get("success") is True or not args.execute_retry_once) else 1


if __name__ == "__main__":
    raise SystemExit(main())
