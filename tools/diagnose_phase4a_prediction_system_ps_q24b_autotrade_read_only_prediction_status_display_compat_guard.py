# path: ./tools/diagnose_phase4a_prediction_system_ps_q24b_autotrade_read_only_prediction_status_display_compat_guard.py
# desc: No-write diagnostic for AutoTrade read-only prediction status display compatibility after PS-Q24A.

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

from btcts.apps.operator_ui.components.autotrade_prediction_preview_status_display import (  # noqa: E402
    AUTOTRADE_PREDICTION_PREVIEW_STATUS_DISPLAY_CONTRACT,
    build_autotrade_prediction_preview_status_display_packet,
    prediction_preview_status_compact_line,
    prediction_preview_status_snapshot_lines,
)
from btcts.autotrade.prediction_preview_status import AutoTradePredictionPreviewStatus  # noqa: E402
from tools.diagnose_phase4a_prediction_system_ps_q24a_autotrade_read_only_prediction_consumption_planning import (  # noqa: E402
    run_autotrade_read_only_prediction_consumption_planning,
)

DIAGNOSTIC_VERSION = "prediction_warroom.ps_q24b_autotrade_read_only_prediction_status_display_compat_guard.v1"
DISPLAY_MODULE = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/components/autotrade_prediction_preview_status_display.py"
AUTOTRADE_PAGE = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/views/autotrade_page.py"


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _git(args: list[str]) -> str:
    proc = subprocess.run(["git", *args], cwd=REPO_ROOT, text=True, capture_output=True, check=False)
    return proc.stdout.strip()


def _all_false(payload: Mapping[str, Any], names: tuple[str, ...]) -> bool:
    return all(payload.get(name) is False for name in names)


def _sample_status() -> AutoTradePredictionPreviewStatus:
    return AutoTradePredictionPreviewStatus(
        status_id="ps_q24b_display_sample_status",
        generated_at="2026-06-29T00:00:00Z",
        status_state="ok",
        preview_id="ps_q24b_preview",
        readiness_id="ps_q24b_readiness",
        readiness_state="ready",
        intended_mode="READ_ONLY_PREVIEW",
        preview_action="WATCH",
        preview_bias="neutral",
        preview_confidence="medium",
        validation_state="ok",
        average_score=0.0,
        label_hit_rate=0.0,
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


def run_autotrade_prediction_status_display_compat_guard() -> dict[str, Any]:
    branch = _git(["rev-parse", "--abbrev-ref", "HEAD"])
    head = _git(["rev-parse", "--short", "HEAD"])
    status_short = _git(["status", "--short", "--untracked-files=all"])
    q24a = run_autotrade_read_only_prediction_consumption_planning()
    status = _sample_status()
    packet = build_autotrade_prediction_preview_status_display_packet(status)
    compact_line = prediction_preview_status_compact_line(status)
    snapshot_lines = tuple(prediction_preview_status_snapshot_lines(status))
    display_text = DISPLAY_MODULE.read_text(encoding="utf-8")
    page_text = AUTOTRADE_PAGE.read_text(encoding="utf-8") if AUTOTRADE_PAGE.exists() else ""

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

    blockers: list[str] = []
    if q24a.get("ready") is not True:
        blockers.append("q24a_read_only_consumption_planning_ready_required")
    for item in list(q24a.get("blockers") or []):
        blockers.append(f"q24a:{item}")
    if AUTOTRADE_PREDICTION_PREVIEW_STATUS_DISPLAY_CONTRACT.get("section_type") != "autotrade_prediction_preview_status_display_packet":
        blockers.append("display_contract_section_type_required")
    if AUTOTRADE_PREDICTION_PREVIEW_STATUS_DISPLAY_CONTRACT.get("read_only_contract") is not True:
        blockers.append("display_contract_read_only_required")
    if packet.get("display_state") != "ok" or packet.get("status_available") is not True:
        blockers.append("display_packet_ok_required")
    if packet.get("preview_action") != "WATCH" or packet.get("preview_bias") != "neutral":
        blockers.append("display_packet_preview_fields_required")
    for marker in ("no_command_buttons=true", "not_runtime_wiring=true", "not_ui_rendering=true"):
        if marker not in snapshot_lines:
            blockers.append(f"display_snapshot_marker_required:{marker}")
    if not compact_line.endswith("display_only"):
        blockers.append("display_compact_line_must_be_display_only")
    if packet.get("read_only_contract") is not True or packet.get("non_executing") is not True:
        blockers.append("display_packet_read_only_non_executing_required")
    if packet.get("no_command_buttons") is not True or packet.get("not_runtime_wiring") is not True or packet.get("not_ui_rendering") is not True:
        blockers.append("display_packet_no_runtime_ui_command_markers_required")
    if not _all_false(packet, execution_flags):
        blockers.append("display_packet_execution_flags_false_required")

    forbidden_display_tokens = (
        "st." + "button",
        "st." + "checkbox",
        "append_" + "decision_jsonl",
        "run_shadow_" + "decision_from_snapshot",
        "submit_mode_" + "change_command_request",
        "validate_and_" + "append_command",
        "place_" + "order(",
        "send_" + "order(",
        "create_" + "order(",
        "write_" + "text(",
        "." + "write(",
        "op" + "en(",
    )
    for token in forbidden_display_tokens:
        if token in display_text:
            blockers.append(f"display_module_forbidden_token:{token}")

    page_wired_to_display = "autotrade_prediction_preview_status_display" in page_text or "build_autotrade_prediction_preview_status_display_packet" in page_text
    if page_wired_to_display:
        blockers.append("autotrade_page_runtime_wiring_unexpected")

    ready = not blockers
    return {
        "ok": True,
        "diagnostic_version": DIAGNOSTIC_VERSION,
        "generated_at": _utc_now(),
        "repo": {"branch": branch, "head": head, "status_short": status_short},
        "ready": ready,
        "state": "ps_q24b_autotrade_prediction_status_display_compat_ready" if ready else "ps_q24b_autotrade_prediction_status_display_compat_blocked",
        "blockers": blockers,
        "q24a_read_only_consumption": {
            "ready": q24a.get("ready"),
            "diagnostic_version": q24a.get("diagnostic_version"),
            "autotrade_read_only_chain": q24a.get("autotrade_read_only_chain"),
            "q23t_manifest_first": q24a.get("q23t_manifest_first"),
        },
        "display_compat": {
            "contract_section_type": AUTOTRADE_PREDICTION_PREVIEW_STATUS_DISPLAY_CONTRACT.get("section_type"),
            "contract_read_only": AUTOTRADE_PREDICTION_PREVIEW_STATUS_DISPLAY_CONTRACT.get("read_only_contract"),
            "display_state": packet.get("display_state"),
            "status_available": packet.get("status_available"),
            "compact_line": compact_line,
            "snapshot_lines": snapshot_lines,
            "preview_action": packet.get("preview_action"),
            "preview_bias": packet.get("preview_bias"),
            "read_only_contract": packet.get("read_only_contract"),
            "non_executing": packet.get("non_executing"),
            "no_command_buttons": packet.get("no_command_buttons"),
            "not_runtime_wiring": packet.get("not_runtime_wiring"),
            "not_ui_rendering": packet.get("not_ui_rendering"),
            "autotrade_page_runtime_wired": page_wired_to_display,
        },
        "safety": {
            "read_only_diagnostic": True,
            "ui_runtime_wiring_changed": False,
            "ui_command_buttons_enabled": False,
            "streamlit_rendering_added": False,
            "runtime_artifact_write_enabled": False,
            "scheduler_action_changed": False,
            "shadow_decision_append_allowed": False,
            "mode_apply_allowed": False,
            "command_or_approval_ledger_allowed": False,
            "parameter_apply_allowed": False,
            "broker_private_api_allowed": False,
            "autotrade_trigger_allowed": False,
            "would_send_to_broker": False,
        },
    }


def main() -> int:
    result = run_autotrade_prediction_status_display_compat_guard()
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True, default=str))
    return 0 if result.get("ok") is True else 1


if __name__ == "__main__":
    raise SystemExit(main())
