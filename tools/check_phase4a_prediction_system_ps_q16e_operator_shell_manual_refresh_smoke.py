# path: ./tools/check_phase4a_prediction_system_ps_q16e_operator_shell_manual_refresh_smoke.py
# desc: PS-Q16E operator-shell manual refresh wrapper/smoke. It runs PS-Q16D against D-hot only from a clean operator shell with explicit flags, then verifies WarRoom source smoke and producer status visibility. No scheduler, WarRoom UI trigger, AutoTrade, broker/private API, ledger, parameter apply, or parameter staging behavior.

from __future__ import annotations

import argparse
from collections.abc import Callable
from datetime import datetime, timezone
import json
import subprocess
from pathlib import Path
from typing import Any, Mapping

from _btcts_bootstrap import ensure_btcts_on_syspath

ensure_btcts_on_syspath()

from btcts.apps.operator_ui.components.prediction_warroom_bounded_manual_refresh_runner import (  # noqa: E402
    build_prediction_warroom_bounded_manual_refresh_runner,
)
from btcts.apps.operator_ui.components.prediction_warroom_non_ui_scheduled_producer_status_panel import (  # noqa: E402
    build_prediction_warroom_non_ui_scheduled_producer_status_panel_packet,
)
from check_phase4a_prediction_system_ps_q12c_warroom_live_inference_smoke import (  # noqa: E402
    build_warroom_live_inference_smoke_payload,
)

CHECKER = "ps_q16e_operator_shell_manual_refresh_smoke"
HOT_ROOT = r"D:\btc_ts_hot"
REPO_ROOT = Path(__file__).resolve().parents[1]
ActualExportRunner = Callable[..., Any]


def _git_status_short() -> list[str]:
    proc = subprocess.run(["git", "status", "--short"], cwd=REPO_ROOT, text=True, capture_output=True, check=True)
    return [line for line in proc.stdout.splitlines() if line.strip()]


def _as_mapping(value: Any) -> Mapping[str, Any]:
    if hasattr(value, "to_dict"):
        converted = value.to_dict()
        return converted if isinstance(converted, Mapping) else {}
    return value if isinstance(value, Mapping) else {}


def _list(value: Any) -> list[Any]:
    return list(value) if isinstance(value, (list, tuple)) else []


def _safe_flags(packet: Mapping[str, Any]) -> dict[str, bool]:
    return {
        "non_ui_runner_only_true": packet.get("non_ui_runner_only") is True,
        "bounded_manual_run_only_true": packet.get("bounded_manual_run_only") is True,
        "producer_enabled_false": packet.get("producer_enabled") is False,
        "scheduler_enabled_false": packet.get("scheduler_enabled") is False,
        "scheduled_loop_enabled_false": packet.get("scheduled_loop_enabled") is False,
        "warroom_ui_trigger_enabled_false": packet.get("warroom_ui_trigger_enabled") is False,
        "ui_triggered_runner_execution_false": packet.get("ui_triggered_runner_execution") is False,
        "ready_for_scheduler_enablement_false": packet.get("ready_for_scheduler_enablement") is False,
        "ready_for_automation_enablement_false": packet.get("ready_for_automation_enablement") is False,
        "approval_or_authorization_allowed_false": packet.get("approval_or_authorization_allowed") is False,
        "ledger_append_allowed_false": packet.get("ledger_append_allowed") is False,
        "autotrade_trigger_allowed_false": packet.get("autotrade_trigger_allowed") is False,
        "broker_private_api_allowed_false": packet.get("broker_private_api_allowed") is False,
        "parameter_apply_allowed_false": packet.get("parameter_apply_allowed") is False,
        "parameter_staging_write_allowed_false": packet.get("parameter_staging_write_allowed") is False,
        "would_send_to_broker_false": packet.get("would_send_to_broker") is False,
        "would_write_collector_state_false": packet.get("would_write_collector_state") is False,
    }


def build_report(
    *,
    hot_root: str = HOT_ROOT,
    require_clean_tree: bool = True,
    actual_export_runner: ActualExportRunner | None = None,
    allow_guard_test_root: bool = False,
) -> dict[str, Any]:
    before_status = _git_status_short()
    if require_clean_tree and before_status:
        return {
            "ok": False,
            "checker": CHECKER,
            "stage": "precheck_blocked",
            "observed_at_utc": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
            "hot_root": str(hot_root),
            "git_status_short_before": before_status,
            "manual_refresh_executed": False,
            "blocked_reasons": ["working_tree_not_clean"],
            "operator_note": "PS-Q16E refuses to refresh D-hot unless the repository working tree is clean.",
        }

    refresh_packet = build_prediction_warroom_bounded_manual_refresh_runner(
        hot_latest_root_hint=str(hot_root),
        operator_acknowledged=True,
        execute_manual_refresh=True,
        allow_actual_read=True,
        allow_prediction_build=True,
        allow_export_preflight=True,
        allow_latest_payload_export=True,
        allow_runtime_artifact_write=True,
        allow_status_artifact_write=True,
        execute_status_artifact_write=True,
        allow_guard_test_root=allow_guard_test_root,
        actual_export_runner=actual_export_runner,
        request_scheduler_enable=False,
        request_warroom_ui_trigger=False,
        request_parameter_apply=False,
        request_parameter_staging_write=False,
        request_approval_or_ledger_or_autotrade_or_broker=False,
    ).to_dict()
    source_smoke = build_warroom_live_inference_smoke_payload(hot_latest_root_hint=str(hot_root))
    status_panel = build_prediction_warroom_non_ui_scheduled_producer_status_panel_packet(
        hot_latest_root_hint=str(hot_root),
        allow_actual_read=True,
        allow_guard_test_root=allow_guard_test_root,
    ).to_dict()
    after_status = _git_status_short()
    safe_flags = _safe_flags(refresh_packet)
    refresh_ok = (
        refresh_packet.get("runner_state") == "bounded_manual_refresh_exported_status_written"
        and refresh_packet.get("actual_export_runner_invoked") is True
        and refresh_packet.get("latest_prediction_artifact_written") is True
        and refresh_packet.get("status_artifact_written") is True
        and int(refresh_packet.get("blocker_count") or 0) == 0
        and all(safe_flags.values())
    )
    smoke_ok = source_smoke.get("ok") is True
    status_ok = (
        status_panel.get("panel_state") == "producer_status_panel_loaded"
        and status_panel.get("payload_decode_succeeded") is True
        and status_panel.get("producer_runner_invoked") is False
        and status_panel.get("scheduler_enabled_by_this_panel") is False
        and status_panel.get("would_write_status_artifact") is False
        and status_panel.get("would_write_latest_prediction_artifact") is False
    )
    clean_after = not after_status
    return {
        "ok": refresh_ok and smoke_ok and status_ok and clean_after,
        "checker": CHECKER,
        "stage": "operator_shell_manual_refresh_smoke",
        "observed_at_utc": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "hot_root": str(hot_root),
        "git_status_short_before": before_status,
        "git_status_short_after": after_status,
        "manual_refresh_executed": True,
        "refresh": {
            "runner_state": refresh_packet.get("runner_state"),
            "actual_export_runner_invoked": refresh_packet.get("actual_export_runner_invoked"),
            "latest_prediction_artifact_written": refresh_packet.get("latest_prediction_artifact_written"),
            "latest_prediction_artifact_path": refresh_packet.get("latest_prediction_artifact_path"),
            "latest_prediction_artifact_size_bytes": refresh_packet.get("latest_prediction_artifact_size_bytes"),
            "status_artifact_written": refresh_packet.get("status_artifact_written"),
            "status_artifact_path": refresh_packet.get("status_artifact_path"),
            "prediction_run_id": refresh_packet.get("prediction_run_id"),
            "generated_at": refresh_packet.get("generated_at"),
            "blocker_count": refresh_packet.get("blocker_count"),
            "warning_count": refresh_packet.get("warning_count"),
            "blocked_reasons": _list(refresh_packet.get("blocked_reasons")),
            "warning_reasons": _list(refresh_packet.get("warning_reasons")),
            "safe_flags": safe_flags,
        },
        "source_smoke": {
            "ok": source_smoke.get("ok"),
            "adapter_state": source_smoke.get("adapter_state"),
            "actual_file_read_succeeded": source_smoke.get("actual_file_read_succeeded"),
            "payload_decode_succeeded": source_smoke.get("payload_decode_succeeded"),
            "review_packet_ready": source_smoke.get("review_packet_ready"),
            "session_state_updated": source_smoke.get("session_state_updated"),
            "blocker_count": source_smoke.get("blocker_count"),
            "warning_count": source_smoke.get("warning_count"),
            "source_summary": dict(_as_mapping(source_smoke.get("source_summary"))),
        },
        "producer_status_panel": {
            "panel_state": status_panel.get("panel_state"),
            "path_exists": status_panel.get("path_exists"),
            "payload_decode_succeeded": status_panel.get("payload_decode_succeeded"),
            "observed_age_sec": status_panel.get("observed_age_sec"),
            "blocker_count": status_panel.get("blocker_count"),
            "warning_count": status_panel.get("warning_count"),
            "producer_runner_invoked": status_panel.get("producer_runner_invoked"),
            "scheduler_enabled_by_this_panel": status_panel.get("scheduler_enabled_by_this_panel"),
            "would_write_status_artifact": status_panel.get("would_write_status_artifact"),
            "would_write_latest_prediction_artifact": status_panel.get("would_write_latest_prediction_artifact"),
        },
        "safety": {
            "operator_shell_only": True,
            "clean_tree_precheck": require_clean_tree,
            "scheduler_registered": False,
            "scheduled_loop_enabled": False,
            "warroom_ui_trigger_enabled": False,
            "approval_or_ledger_or_autotrade_or_broker": False,
            "parameter_apply_or_staging": False,
            "freshness_bypass_added": False,
            "force_ready_added": False,
        },
        "operator_note": "PS-Q16E is an explicit operator-shell manual refresh smoke only; no scheduler registration, no WarRoom UI trigger, no AutoTrade, no broker/private API.",
    }


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="PS-Q16E operator-shell manual refresh wrapper/smoke")
    parser.add_argument("--hot-root", default=HOT_ROOT)
    parser.add_argument("--allow-dirty", action="store_true", help="Allow execution when git status is dirty. Not recommended; intended only for guard/test roots.")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    payload = build_report(hot_root=str(args.hot_root), require_clean_tree=not args.allow_dirty)
    print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if payload.get("ok") is True else 1


def test_ps_q16e_precheck_blocks_dirty_tree() -> None:
    original = _git_status_short
    try:
        globals()["_git_status_short"] = lambda: [" M some_file.py"]
        payload = build_report(hot_root=HOT_ROOT, require_clean_tree=True, actual_export_runner=lambda **_: {})
    finally:
        globals()["_git_status_short"] = original
    assert payload["ok"] is False
    assert payload["manual_refresh_executed"] is False
    assert "working_tree_not_clean" in payload["blocked_reasons"]


if __name__ == "__main__":
    raise SystemExit(main())
