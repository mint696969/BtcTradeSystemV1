# path: ./tools/test_phase4a_prediction_system_ps_q18ba_close_guard.py
# desc: Close guard for PS-Q18BA WarRoom legacy prediction dev helper/import prune.

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = REPO_ROOT / "btcts_next" / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

import btcts.apps.operator_ui.views.warroom_page as warroom_page  # noqa: E402

EXPECTED_DIRTY = {
    "btcts_next/src/btcts/apps/operator_ui/views/warroom_page.py",
    "docs/strategy/PREDICTION_SYSTEM_PS_Q18BA_WARROOM_LEGACY_PREDICTION_DEV_HELPER_IMPORT_PRUNE_2026-06-24.md",
    "tools/test_phase4a_prediction_system_ps_q18ba_close_guard.py",
    "tools/test_phase4a_prediction_system_ps_q18ba_warroom_legacy_prediction_dev_helper_import_prune.py",
    "tools/test_phase4a_prediction_system_ps_q18ba_warroom_legacy_prediction_dev_helper_import_prune_guard.py",
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
    packet = warroom_page._warroom_operator_first_render_path_cleanup_packet()
    if packet.get("normal_ui_path_operator_first") is not True:
        failures.append("normal UI path must stay operator-first")
    if packet.get("latest_prediction_quick_status_kept") is not True:
        failures.append("quick status must stay kept")
    if packet.get("future_extension_contracts_preserved") is not True:
        failures.append("future extension contracts must be preserved")
    if packet.get("prediction_warroom_dev_preflight_sections_rendered_in_normal_path") is not False:
        failures.append("dev/preflight sections must remain outside normal render path")
    for key in FALSE_BOUNDARIES:
        if packet.get(key) is not False:
            failures.append(f"{key} must stay false")
    if hasattr(warroom_page, "_render_prediction_warroom_real_source_handoff_preflight_section"):
        failures.append("unexpected legacy real-source handoff helper still exported")
    if not hasattr(warroom_page, "_render_prediction_warroom_latest_prediction_observation_cleanup_summary_section"):
        failures.append("quick status render helper must remain")
    dirty = _dirty_paths()
    unexpected = dirty - EXPECTED_DIRTY
    missing = EXPECTED_DIRTY - dirty
    if unexpected:
        failures.append(f"unexpected dirty paths: {sorted(unexpected)}")
    if missing:
        failures.append(f"missing expected dirty paths: {sorted(missing)}")
    result = {
        "ok": not failures,
        "guard": "ps_q18ba_close_guard",
        "phase": "phase3_warroom_legacy_prediction_dev_helper_import_prune_closed",
        "contract": {
            "ps_q18ba_closed": not failures,
            "warroom_page_legacy_prediction_dev_helpers_pruned": not failures,
            "component_modules_deleted": False,
            "future_extension_contracts_preserved": packet.get("future_extension_contracts_preserved"),
            "normal_ui_path_operator_first": packet.get("normal_ui_path_operator_first"),
            "real_prediction_widget_render_invoked": False,
            "autotrade_trigger_allowed": False,
            "broker_private_api_allowed": False,
            "next_slice": "PS-Q18BB reference audit for legacy component modules and archive/delete decision",
        },
        "dirty_paths": sorted(dirty),
        "unexpected_dirty": sorted(unexpected),
        "missing_dirty": sorted(missing),
        "failures": failures,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if not failures else 1


def test_ps_q18ba_close_guard() -> None:
    assert main_guard() == 0


if __name__ == "__main__":
    raise SystemExit(main_guard())
