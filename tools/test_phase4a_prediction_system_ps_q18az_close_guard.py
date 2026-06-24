# path: ./tools/test_phase4a_prediction_system_ps_q18az_close_guard.py
# desc: Close guard for PS-Q18AZ WarRoom operator-first render path cleanup.

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = REPO_ROOT / "btcts_next" / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from btcts.apps.operator_ui.views.warroom_page import (  # noqa: E402
    _warroom_operator_first_render_path_cleanup_packet,
)

EXPECTED_DIRTY = {
    "btcts_next/src/btcts/apps/operator_ui/views/warroom_page.py",
    "docs/strategy/PREDICTION_SYSTEM_PS_Q18AZ_WARROOM_OPERATOR_FIRST_RENDER_PATH_CLEANUP_2026-06-24.md",
    "tools/test_phase4a_prediction_system_ps_q18az_close_guard.py",
    "tools/test_phase4a_prediction_system_ps_q18az_warroom_operator_first_render_path_cleanup.py",
    "tools/test_phase4a_prediction_system_ps_q18az_warroom_operator_first_render_path_cleanup_guard.py",
}

FALSE_BOUNDARIES = (
    "real_prediction_widget_rendering_allowed",
    "real_prediction_widget_render_invoked",
    "streamlit_real_widget_render_invoked",
    "component_runtime_binding_allowed",
    "component_props_bound_to_runtime",
    "runtime_artifact_write_allowed",
    "status_artifact_write_allowed",
    "parameter_apply_allowed",
    "parameter_staging_write_allowed",
    "ledger_append_allowed",
    "autotrade_trigger_allowed",
    "broker_private_api_allowed",
    "would_send_to_broker",
)


def _dirty_paths() -> set[str]:
    proc = subprocess.run(["git", "status", "--short"], cwd=REPO_ROOT, text=True, capture_output=True, check=True)
    return {line[3:].replace(chr(92), "/") for line in proc.stdout.splitlines() if line.strip() and "/__pycache__/" not in line and not line.endswith(".pyc")}


def main_guard() -> int:
    failures: list[str] = []
    packet = _warroom_operator_first_render_path_cleanup_packet()
    if packet.get("cleanup_state") != "normal_warroom_ui_operator_first_dev_preflight_sections_removed":
        failures.append("cleanup state mismatch")
    if packet.get("normal_ui_path_operator_first") is not True:
        failures.append("normal UI path must be operator-first")
    if packet.get("latest_prediction_quick_status_kept") is not True:
        failures.append("quick status must remain")
    if packet.get("prediction_warroom_dev_preflight_sections_rendered_in_normal_path") is not False:
        failures.append("dev/preflight sections must be out of normal path")
    if packet.get("legacy_dev_helpers_deleted_this_slice") is not False:
        failures.append("helper deletion is deferred to PS-Q18BA")
    if packet.get("future_extension_contracts_preserved") is not True:
        failures.append("future extension contracts must be preserved")
    if packet.get("removed_section_count") != 12:
        failures.append("removed section count must be 12")
    for key in FALSE_BOUNDARIES:
        if packet.get(key) is not False:
            failures.append(f"{key} must stay false")
    dirty = _dirty_paths()
    unexpected = dirty - EXPECTED_DIRTY
    missing = EXPECTED_DIRTY - dirty
    if unexpected:
        failures.append(f"unexpected dirty paths: {sorted(unexpected)}")
    if missing:
        failures.append(f"missing expected dirty paths: {sorted(missing)}")
    result = {
        "ok": not failures,
        "guard": "ps_q18az_close_guard",
        "phase": "phase3_warroom_operator_first_render_path_cleanup_closed",
        "contract": {
            "ps_q18az_closed": not failures,
            "cleanup_state": packet.get("cleanup_state"),
            "removed_section_count": packet.get("removed_section_count"),
            "latest_prediction_quick_status_kept": packet.get("latest_prediction_quick_status_kept"),
            "legacy_dev_helpers_deleted_this_slice": packet.get("legacy_dev_helpers_deleted_this_slice"),
            "future_extension_contracts_preserved": packet.get("future_extension_contracts_preserved"),
            "real_prediction_widget_render_invoked": False,
            "autotrade_trigger_allowed": False,
            "broker_private_api_allowed": False,
            "next_slice": packet.get("next_safe_slice"),
        },
        "dirty_paths": sorted(dirty),
        "unexpected_dirty": sorted(unexpected),
        "missing_dirty": sorted(missing),
        "failures": failures,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if not failures else 1


def test_ps_q18az_close_guard() -> None:
    assert main_guard() == 0


if __name__ == "__main__":
    raise SystemExit(main_guard())
