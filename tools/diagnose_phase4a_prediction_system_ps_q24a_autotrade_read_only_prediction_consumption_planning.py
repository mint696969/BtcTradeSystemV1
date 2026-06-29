# path: ./tools/diagnose_phase4a_prediction_system_ps_q24a_autotrade_read_only_prediction_consumption_planning.py
# desc: No-write diagnostic proving Q23T manifest-first state can be paired with existing AutoTrade read-only prediction consumption contracts.

from __future__ import annotations

from datetime import datetime, timezone
import json
from pathlib import Path
import subprocess
import sys
from typing import Any, Mapping

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = REPO_ROOT / "btcts_next" / "src"
for candidate in (REPO_ROOT, SRC_ROOT):
    if str(candidate) not in sys.path:
        sys.path.insert(0, str(candidate))

from btcts.autotrade.prediction_preview_artifact_preflight import build_prediction_preview_artifact_preflight  # noqa: E402
from btcts.autotrade.prediction_preview_status import AutoTradePredictionPreviewStatus  # noqa: E402
from btcts.autotrade.shadow_prediction_context import build_autotrade_shadow_prediction_context  # noqa: E402
from btcts.apps.operator_ui.components.autotrade_prediction_preview_status_display import (  # noqa: E402
    build_autotrade_prediction_preview_status_display_packet,
)
from tools.diagnose_phase4a_prediction_system_ps_q23t_manifest_first_steady_state_guard import (  # noqa: E402
    run_manifest_first_steady_state_guard,
)

DIAGNOSTIC_VERSION = "prediction_warroom.ps_q24a_autotrade_read_only_prediction_consumption_planning.v1"
EXPECTED_FULL_RECORD_COUNT = 110
EXPECTED_COMPACT_RECORD_COUNT = 24


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _git(args: list[str]) -> str:
    proc = subprocess.run(["git", *args], cwd=REPO_ROOT, text=True, capture_output=True, check=False)
    return proc.stdout.strip()


def _mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _all_false(payload: Mapping[str, Any], names: tuple[str, ...]) -> bool:
    return all(payload.get(name) is False for name in names)


def _sample_status(now: datetime) -> AutoTradePredictionPreviewStatus:
    stamp = now.astimezone(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    return AutoTradePredictionPreviewStatus(
        status_id="ps_q24a_sample_status",
        generated_at=stamp,
        status_state="ok",
        preview_id="ps_q24a_manifest_first_preview",
        readiness_id="ps_q24a_readiness",
        readiness_state="ready",
        intended_mode="READ_ONLY_PREVIEW",
        preview_action="WATCH",
        preview_bias="neutral",
        preview_confidence="medium",
        validation_state="ok",
        average_score=0.0,
        label_hit_rate=0.0,
        weak_families=(),
        blockers=(),
        warnings=(),
        read_only=True,
        non_executing=True,
        would_append_shadow_decision=False,
        would_apply_mode=False,
        would_execute_prearmed_grant=False,
        would_write_runtime_artifact=False,
        would_send_to_broker=False,
        broker_execution_requested=False,
        mode_apply_requested=False,
        command_ledger_append_requested=False,
        approval_append_requested=False,
    )


def run_autotrade_read_only_prediction_consumption_planning() -> dict[str, Any]:
    branch = _git(["rev-parse", "--abbrev-ref", "HEAD"])
    head = _git(["rev-parse", "--short", "HEAD"])
    status_short = _git(["status", "--short", "--untracked-files=all"])
    q23t = run_manifest_first_steady_state_guard()
    q23r = _mapping(q23t.get("q23r_closeout"))
    artifact = _mapping(q23r.get("artifact_summary"))
    q23e = _mapping(q23t.get("q23e_manifest_first_live"))
    panel = _mapping(q23t.get("display_panel_default"))

    now = datetime(2026, 6, 29, 0, 0, 0, tzinfo=timezone.utc)
    sample_status = _sample_status(now)
    sample_context = build_autotrade_shadow_prediction_context(sample_status, now=now)
    sample_preflight = build_prediction_preview_artifact_preflight(
        sample_status,
        sample_context,
        artifact_path="planning/prediction_preview_status_read_only_sample.json",
        now=now,
    )
    sample_display = build_autotrade_prediction_preview_status_display_packet(sample_status)
    status_payload = sample_status.to_dict()
    context_payload = sample_context.to_dict()
    preflight_payload = sample_preflight.to_dict()

    execution_flags = (
        "would_append_shadow_decision",
        "would_apply_mode",
        "would_execute_prearmed_grant",
        "would_write_runtime_artifact",
        "would_send_to_broker",
        "broker_execution_requested",
        "mode_apply_requested",
        "command_ledger_append_requested",
        "approval_append_requested",
    )
    preflight_flags = execution_flags + (
        "artifact_write_allowed",
        "artifact_write_requested",
        "would_write_preview_status_artifact",
    )

    blockers: list[str] = []
    if q23t.get("ready") is not True:
        blockers.append("q23t_manifest_first_guard_ready_required")
    for item in list(q23t.get("blockers") or []):
        blockers.append(f"q23t:{item}")
    if artifact.get("legacy_compact_record_count") != EXPECTED_COMPACT_RECORD_COUNT:
        blockers.append("legacy_compact_record_count_24_required")
    if artifact.get("manifest_record_count") != EXPECTED_FULL_RECORD_COUNT:
        blockers.append("manifest_record_count_110_required")
    if artifact.get("forecast_records_line_count") != EXPECTED_FULL_RECORD_COUNT:
        blockers.append("forecast_records_line_count_110_required")
    if q23e.get("source_artifact_mode") != "distributed":
        blockers.append("q23e_distributed_source_required")
    if q23e.get("selected_record_count") != EXPECTED_FULL_RECORD_COUNT:
        blockers.append("q23e_selected_record_count_110_required")
    if q23e.get("legacy_fallback_ready") is not True:
        blockers.append("q23e_legacy_fallback_ready_required")
    if panel.get("source_artifact_mode") != "distributed":
        blockers.append("display_panel_distributed_source_required")
    if int(panel.get("prediction_row_count") or 0) <= 0:
        blockers.append("display_panel_prediction_rows_required")

    if status_payload.get("status_state") != "ok" or status_payload.get("usable") is not True:
        blockers.append("sample_prediction_preview_status_ok_required")
    if context_payload.get("context_state") != "ok" or context_payload.get("usable_as_context") is not True:
        blockers.append("sample_shadow_prediction_context_ok_required")
    if preflight_payload.get("preflight_state") != "ready" or preflight_payload.get("ready_for_future_write") is not True:
        blockers.append("sample_prediction_preview_artifact_preflight_ready_required")
    if sample_display.get("display_state") != "ok" or sample_display.get("status_available") is not True:
        blockers.append("sample_prediction_preview_display_ok_required")

    if status_payload.get("read_only") is not True or status_payload.get("non_executing") is not True:
        blockers.append("sample_status_read_only_non_executing_required")
    if context_payload.get("read_only") is not True or context_payload.get("non_executing") is not True:
        blockers.append("sample_context_read_only_non_executing_required")
    if preflight_payload.get("read_only") is not True or preflight_payload.get("non_executing") is not True:
        blockers.append("sample_preflight_read_only_non_executing_required")
    if context_payload.get("optional_context_only") is not True or context_payload.get("persist_false_only") is not True:
        blockers.append("sample_context_optional_persist_false_only_required")
    if preflight_payload.get("preflight_only") is not True or preflight_payload.get("artifact_write_preflight_only") is not True:
        blockers.append("sample_preflight_only_required")
    if not _all_false(status_payload, execution_flags):
        blockers.append("sample_status_execution_flags_false_required")
    if not _all_false(context_payload, ("would_change_shadow_candidate",) + execution_flags):
        blockers.append("sample_context_execution_flags_false_required")
    if not _all_false(preflight_payload, preflight_flags):
        blockers.append("sample_preflight_execution_flags_false_required")
    if sample_display.get("would_append_shadow_decision") is not False or sample_display.get("would_send_to_broker") is not False:
        blockers.append("sample_display_execution_flags_false_required")

    ready = not blockers
    return {
        "ok": True,
        "diagnostic_version": DIAGNOSTIC_VERSION,
        "generated_at": _utc_now(),
        "repo": {
            "branch": branch,
            "head": head,
            "status_short": status_short,
        },
        "ready": ready,
        "state": "ps_q24a_autotrade_read_only_prediction_consumption_planning_ready" if ready else "ps_q24a_autotrade_read_only_prediction_consumption_planning_blocked",
        "blockers": blockers,
        "q23t_manifest_first": {
            "ready": q23t.get("ready"),
            "diagnostic_version": q23t.get("diagnostic_version"),
            "source_artifact_mode": q23e.get("source_artifact_mode"),
            "selected_record_count": q23e.get("selected_record_count"),
            "legacy_fallback_ready": q23e.get("legacy_fallback_ready"),
            "display_panel_source_artifact_mode": panel.get("source_artifact_mode"),
            "display_panel_prediction_row_count": panel.get("prediction_row_count"),
            "artifact_summary": dict(artifact),
        },
        "autotrade_read_only_chain": {
            "status_state": status_payload.get("status_state"),
            "status_usable": status_payload.get("usable"),
            "context_state": context_payload.get("context_state"),
            "context_usable": context_payload.get("usable_as_context"),
            "preflight_state": preflight_payload.get("preflight_state"),
            "preflight_ready_for_future_write": preflight_payload.get("ready_for_future_write"),
            "display_state": sample_display.get("display_state"),
            "display_status_available": sample_display.get("status_available"),
            "in_memory_only": True,
            "not_runtime_wiring": True,
            "not_ui_command": True,
        },
        "safety": {
            "read_only_diagnostic": True,
            "runtime_artifact_write_enabled": False,
            "latest_prediction_artifact_written": False,
            "status_artifact_written": False,
            "latest_manifest_written": False,
            "run_sidecars_written": False,
            "scheduler_action_changed": False,
            "scheduler_enabled_by_this_tool": False,
            "trigger_added": False,
            "shadow_decision_append_allowed": False,
            "mode_apply_allowed": False,
            "prearmed_grant_execution_allowed": False,
            "command_or_approval_ledger_allowed": False,
            "parameter_apply_allowed": False,
            "broker_private_api_allowed": False,
            "autotrade_trigger_allowed": False,
            "would_send_to_broker": False,
        },
    }


def main() -> int:
    result = run_autotrade_read_only_prediction_consumption_planning()
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True, default=str))
    return 0 if result.get("ok") is True else 1


if __name__ == "__main__":
    raise SystemExit(main())
