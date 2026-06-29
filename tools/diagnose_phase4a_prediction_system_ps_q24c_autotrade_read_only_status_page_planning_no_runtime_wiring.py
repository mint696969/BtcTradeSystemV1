# path: ./tools/diagnose_phase4a_prediction_system_ps_q24c_autotrade_read_only_status_page_planning_no_runtime_wiring.py
# desc: No-write diagnostic for future AutoTrade read-only prediction status page placement planning. Does not modify or wire autotrade_page.py.

from __future__ import annotations

from datetime import datetime, timezone
import json
from pathlib import Path
import subprocess
import sys
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = REPO_ROOT / "btcts_next" / "src"
for candidate in (REPO_ROOT, SRC_ROOT):
    if str(candidate) not in sys.path:
        sys.path.insert(0, str(candidate))

from tools.diagnose_phase4a_prediction_system_ps_q24b_autotrade_read_only_prediction_status_display_compat_guard import (  # noqa: E402
    run_autotrade_prediction_status_display_compat_guard,
)

DIAGNOSTIC_VERSION = "prediction_warroom.ps_q24c_autotrade_read_only_status_page_planning_no_runtime_wiring.v1"
AUTOTRADE_PAGE = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/views/autotrade_page.py"
DISPLAY_MODULE_REF = "autotrade_prediction_preview_status_display"
DISPLAY_BUILDER_REF = "build_autotrade_prediction_preview_status_display_packet"


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _git(args: list[str]) -> str:
    proc = subprocess.run(["git", *args], cwd=REPO_ROOT, text=True, capture_output=True, check=False)
    return proc.stdout.strip()


def _count(text: str, token: str) -> int:
    return text.count(token)


def run_autotrade_read_only_status_page_planning_no_runtime_wiring() -> dict[str, Any]:
    branch = _git(["rev-parse", "--abbrev-ref", "HEAD"])
    head = _git(["rev-parse", "--short", "HEAD"])
    status_short = _git(["status", "--short", "--untracked-files=all"])
    q24b = run_autotrade_prediction_status_display_compat_guard()
    page_text = AUTOTRADE_PAGE.read_text(encoding="utf-8") if AUTOTRADE_PAGE.exists() else ""

    button_token = "st." + "button"
    checkbox_token = "st." + "checkbox"
    append_command_token = "validate_and_" + "append_command"
    mode_request_token = "submit_mode_" + "change_command_request"
    broker_send_token = "send_" + "order("
    broker_place_token = "place_" + "order("
    broker_create_token = "create_" + "order("

    prediction_display_wired = DISPLAY_MODULE_REF in page_text or DISPLAY_BUILDER_REF in page_text
    existing_button_count = _count(page_text, button_token)
    existing_checkbox_count = _count(page_text, checkbox_token)
    existing_command_request_surface = append_command_token in page_text or mode_request_token in page_text

    blockers: list[str] = []
    if q24b.get("ready") is not True:
        blockers.append("q24b_display_compat_ready_required")
    for item in list(q24b.get("blockers") or []):
        blockers.append(f"q24b:{item}")
    if not AUTOTRADE_PAGE.exists():
        blockers.append("autotrade_page_exists_required")
    if prediction_display_wired:
        blockers.append("prediction_status_display_already_wired_to_autotrade_page")
    if broker_send_token in page_text or broker_place_token in page_text or broker_create_token in page_text:
        blockers.append("autotrade_page_broker_order_token_unexpected")

    ready = not blockers
    return {
        "ok": True,
        "diagnostic_version": DIAGNOSTIC_VERSION,
        "generated_at": _utc_now(),
        "repo": {"branch": branch, "head": head, "status_short": status_short},
        "ready": ready,
        "state": "ps_q24c_autotrade_status_page_planning_no_runtime_wiring_ready" if ready else "ps_q24c_autotrade_status_page_planning_no_runtime_wiring_blocked",
        "blockers": blockers,
        "q24b_display_compat": {
            "ready": q24b.get("ready"),
            "diagnostic_version": q24b.get("diagnostic_version"),
            "display_compat": q24b.get("display_compat"),
            "safety": q24b.get("safety"),
        },
        "autotrade_page_plan": {
            "page_exists": AUTOTRADE_PAGE.exists(),
            "page_relative_path": "btcts_next/src/btcts/apps/operator_ui/views/autotrade_page.py",
            "planned_future_section": "AutoTrade page / Runtime Health vicinity / read-only prediction status subsection",
            "prediction_status_display_wired": prediction_display_wired,
            "prediction_status_display_module_ref_present": DISPLAY_MODULE_REF in page_text,
            "prediction_status_display_builder_ref_present": DISPLAY_BUILDER_REF in page_text,
            "existing_command_surface_acknowledged": existing_command_request_surface,
            "existing_button_count": existing_button_count,
            "existing_checkbox_count": existing_checkbox_count,
            "page_modification_changed": False,
            "ui_runtime_wiring_changed": False,
            "streamlit_rendering_added": False,
            "command_buttons_added": False,
        },
        "safety": {
            "read_only_diagnostic": True,
            "planning_only": True,
            "autotrade_page_modified": False,
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
    result = run_autotrade_read_only_status_page_planning_no_runtime_wiring()
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True, default=str))
    return 0 if result.get("ok") is True else 1


if __name__ == "__main__":
    raise SystemExit(main())
