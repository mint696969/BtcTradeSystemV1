# path: ./tools/check_phase4a_prediction_system_ps_q16f_scheduler_enablement_preflight.py
# desc: PS-Q16F read-only scheduler enablement preflight / human decision checkpoint. It inspects clean-tree state, WarRoom latest prediction source readiness, and producer status visibility after PS-Q16E; it never registers a scheduler, creates a loop, refreshes artifacts, mutates parameters, appends ledgers, triggers AutoTrade, or calls broker/private APIs.

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
import subprocess
from pathlib import Path
from typing import Any, Mapping

from _btcts_bootstrap import ensure_btcts_on_syspath

ensure_btcts_on_syspath()

from btcts.apps.operator_ui.components.prediction_warroom_non_ui_scheduled_producer_contract import (  # noqa: E402
    FRESHNESS_MAX_AGE_SEC,
    MAXIMUM_CADENCE_SEC,
    MINIMUM_CADENCE_SEC,
    PRODUCER_STATUS_ARTIFACT_RELATIVE_PATH,
    RECOMMENDED_CADENCE_SEC,
)
from btcts.apps.operator_ui.components.prediction_warroom_non_ui_scheduled_producer_status_panel import (  # noqa: E402
    build_prediction_warroom_non_ui_scheduled_producer_status_panel_packet,
)
from check_phase4a_prediction_system_ps_q12c_warroom_live_inference_smoke import (  # noqa: E402
    build_warroom_live_inference_smoke_payload,
)

CHECKER = "ps_q16f_scheduler_enablement_preflight"
HOT_ROOT = r"D:\btc_ts_hot"
REPO_ROOT = Path(__file__).resolve().parents[1]


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


def _int(value: Any) -> int:
    try:
        return int(value or 0)
    except (TypeError, ValueError):
        return 0


def _parse_utc(value: Any) -> datetime | None:
    text = str(value or "").strip()
    if not text:
        return None
    try:
        return datetime.fromisoformat(text.replace("Z", "+00:00")).astimezone(timezone.utc)
    except ValueError:
        return None


def _age_sec(value: Any, *, now: datetime) -> int | None:
    parsed = _parse_utc(value)
    if parsed is None:
        return None
    return max(0, int((now - parsed).total_seconds()))


def _safe_false_flags() -> dict[str, bool]:
    return {
        "scheduler_registered_false": True,
        "scheduled_loop_enabled_false": True,
        "warroom_ui_trigger_enabled_false": True,
        "runtime_artifact_write_automation_enabled_false": True,
        "producer_enabled_by_this_preflight_false": True,
        "approval_or_authorization_allowed_false": True,
        "ledger_append_allowed_false": True,
        "autotrade_trigger_allowed_false": True,
        "broker_private_api_allowed_false": True,
        "parameter_apply_allowed_false": True,
        "parameter_staging_write_allowed_false": True,
        "freshness_bypass_added_false": True,
        "force_ready_added_false": True,
    }


def build_report(
    *,
    hot_root: str = HOT_ROOT,
    require_clean_tree: bool = True,
    human_approval_record_present: bool = False,
    allow_guard_test_root: bool = False,
) -> dict[str, Any]:
    """Build a read-only scheduler enablement preflight report.

    This report intentionally never enables scheduling. A passing report only opens a human
    decision checkpoint for a future disabled-by-default scheduler implementation slice.
    """
    now = datetime.now(timezone.utc)
    git_status = _git_status_short()
    blockers: list[str] = []
    warnings: list[str] = []
    if require_clean_tree and git_status:
        blockers.append("working_tree_not_clean")

    source_smoke = build_warroom_live_inference_smoke_payload(hot_latest_root_hint=str(hot_root))
    status_panel = build_prediction_warroom_non_ui_scheduled_producer_status_panel_packet(
        hot_latest_root_hint=str(hot_root),
        allow_actual_read=True,
        allow_guard_test_root=allow_guard_test_root,
    ).to_dict()
    status_payload = _as_mapping(status_panel.get("payload"))
    source_summary = _as_mapping(source_smoke.get("source_summary"))
    source_run_id = str(source_summary.get("prediction_run_id") or "")
    source_generated_at = str(source_summary.get("generated_at") or "")
    status_run_id = str(status_payload.get("last_prediction_run_id") or "")
    status_generated_at = str(status_payload.get("last_success_generated_at") or "")
    status_last_success_at = str(status_payload.get("last_success_at") or "")
    status_last_failure_at = str(status_payload.get("last_failure_at") or "")
    latest_age = _age_sec(source_generated_at, now=now)
    status_success_age = _age_sec(status_last_success_at, now=now)

    source_ready = bool(
        source_smoke.get("ok") is True
        and source_smoke.get("adapter_state") == "latest_prediction_source_ready"
        and source_smoke.get("actual_file_read_succeeded") is True
        and source_smoke.get("payload_decode_succeeded") is True
        and source_smoke.get("review_packet_ready") is True
        and _int(source_smoke.get("blocker_count")) == 0
    )
    if not source_ready:
        blockers.append("latest_prediction_source_not_ready_for_scheduler_preflight")

    status_loaded = bool(
        status_panel.get("panel_state") == "producer_status_panel_loaded"
        and status_panel.get("payload_decode_succeeded") is True
        and status_panel.get("producer_runner_invoked") is False
        and status_panel.get("scheduler_enabled_by_this_panel") is False
        and status_panel.get("would_write_status_artifact") is False
        and status_panel.get("would_write_latest_prediction_artifact") is False
    )
    if not status_loaded:
        blockers.append("producer_status_panel_not_loaded_read_only")

    status_success = bool(
        status_payload
        and status_payload.get("runtime_artifact_write_enabled") is True
        and status_payload.get("producer_enabled") is False
        and status_payload.get("scheduler_enabled") is False
        and _int(status_payload.get("last_blocker_count")) == 0
        and not _list(status_payload.get("blockers"))
        and bool(status_payload.get("last_success_at"))
        and bool(status_payload.get("last_success_generated_at"))
        and bool(status_payload.get("last_prediction_run_id"))
    )
    if not status_success:
        blockers.append("producer_status_last_success_not_ready_for_scheduler_preflight")

    if latest_age is None:
        blockers.append("latest_prediction_generated_at_missing_or_unparseable")
    elif latest_age > FRESHNESS_MAX_AGE_SEC:
        blockers.append("latest_prediction_artifact_stale_for_scheduler_preflight")
    if status_success_age is None:
        blockers.append("producer_status_last_success_at_missing_or_unparseable")
    elif status_success_age > FRESHNESS_MAX_AGE_SEC:
        blockers.append("producer_status_last_success_stale_for_scheduler_preflight")
    if source_run_id and status_run_id and source_run_id != status_run_id:
        blockers.append("latest_prediction_run_id_mismatch_between_source_and_status")
    if source_generated_at and status_generated_at and source_generated_at != status_generated_at:
        blockers.append("latest_prediction_generated_at_mismatch_between_source_and_status")
    if _int(source_smoke.get("warning_count")) > 0:
        warnings.append("latest_prediction_source_has_warnings:" + str(_int(source_smoke.get("warning_count"))))
    if _int(status_panel.get("warning_count")) > 0:
        warnings.append("producer_status_panel_has_warnings:" + str(_int(status_panel.get("warning_count"))))
    for item in _list(status_payload.get("warnings")):
        warnings.append("producer_status_warning:" + str(item))

    preflight_passed = not tuple(dict.fromkeys(blockers))
    checkpoint_open = bool(preflight_passed and not human_approval_record_present)
    human_approved_for_next_slice = bool(preflight_passed and human_approval_record_present)
    return {
        "ok": preflight_passed,
        "checker": CHECKER,
        "stage": "scheduler_enablement_preflight_human_decision_checkpoint",
        "observed_at_utc": now.isoformat().replace("+00:00", "Z"),
        "hot_root": str(hot_root),
        "git_status_short": git_status,
        "preflight_passed": preflight_passed,
        "human_decision_checkpoint_open": checkpoint_open,
        "human_approval_record_present": human_approval_record_present,
        "human_approved_for_next_slice": human_approved_for_next_slice,
        "ready_for_scheduler_enablement": False,
        "ready_for_scheduler_implementation_slice": human_approved_for_next_slice,
        "scheduler_enablement_command_generated": False,
        "scheduler_registration_performed": False,
        "scheduled_loop_enabled": False,
        "recommended_cadence_sec": RECOMMENDED_CADENCE_SEC,
        "minimum_cadence_sec": MINIMUM_CADENCE_SEC,
        "maximum_cadence_sec": MAXIMUM_CADENCE_SEC,
        "freshness_max_age_sec": FRESHNESS_MAX_AGE_SEC,
        "latest_prediction": {
            "source_smoke_ok": source_smoke.get("ok"),
            "adapter_state": source_smoke.get("adapter_state"),
            "prediction_run_id": source_run_id,
            "generated_at": source_generated_at,
            "age_sec": latest_age,
            "blocker_count": source_smoke.get("blocker_count"),
            "warning_count": source_smoke.get("warning_count"),
            "signal_strength_percent": source_summary.get("signal_strength_percent"),
            "signal_strength_band": source_summary.get("signal_strength_band"),
        },
        "producer_status": {
            "status_artifact_relative_path": PRODUCER_STATUS_ARTIFACT_RELATIVE_PATH,
            "panel_state": status_panel.get("panel_state"),
            "payload_decode_succeeded": status_panel.get("payload_decode_succeeded"),
            "observed_age_sec": status_panel.get("observed_age_sec"),
            "producer_state": status_payload.get("producer_state"),
            "producer_enabled": status_payload.get("producer_enabled"),
            "scheduler_enabled": status_payload.get("scheduler_enabled"),
            "runtime_artifact_write_enabled": status_payload.get("runtime_artifact_write_enabled"),
            "last_success_at": status_last_success_at,
            "last_failure_at": status_last_failure_at,
            "last_success_generated_at": status_generated_at,
            "last_prediction_run_id": status_run_id,
            "last_target_file_size_bytes": status_payload.get("last_target_file_size_bytes"),
            "last_warning_count": status_payload.get("last_warning_count"),
            "last_blocker_count": status_payload.get("last_blocker_count"),
            "consecutive_failure_count": status_payload.get("consecutive_failure_count"),
            "disable_rollback_state": status_payload.get("disable_rollback_state"),
        },
        "blocked_reasons": list(dict.fromkeys(blockers)),
        "warning_reasons": list(dict.fromkeys(warnings)),
        "safety": _safe_false_flags(),
        "operator_note": "PS-Q16F is a read-only preflight and human decision checkpoint. It does not create a scheduler or enable automation.",
        "next_action": "human_decision_required_before_scheduler_implementation_slice" if checkpoint_open else ("scheduler_implementation_slice_can_be_designed_but_not_enabled_here" if human_approved_for_next_slice else "fix_preflight_blockers_before_scheduler_discussion"),
    }


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="PS-Q16F scheduler enablement preflight / human decision checkpoint")
    parser.add_argument("--hot-root", default=HOT_ROOT)
    parser.add_argument("--allow-dirty", action="store_true", help="Allow preflight while git status is dirty; intended for guard/test roots only.")
    parser.add_argument("--human-approval-record-present", action="store_true", help="Report that an explicit human approval record exists for the next design slice. This still does not enable a scheduler.")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    payload = build_report(
        hot_root=str(args.hot_root),
        require_clean_tree=not args.allow_dirty,
        human_approval_record_present=bool(args.human_approval_record_present),
    )
    print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if payload.get("ok") is True else 1


def test_ps_q16f_preflight_blocks_dirty_tree() -> None:
    original = _git_status_short
    try:
        globals()["_git_status_short"] = lambda: [" M dirty.py"]
        payload = build_report(require_clean_tree=True)
    finally:
        globals()["_git_status_short"] = original
    assert payload["ok"] is False
    assert "working_tree_not_clean" in payload["blocked_reasons"]
    assert payload["ready_for_scheduler_enablement"] is False
    assert payload["scheduler_registration_performed"] is False


if __name__ == "__main__":
    raise SystemExit(main())
