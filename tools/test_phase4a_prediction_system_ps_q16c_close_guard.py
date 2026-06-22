# path: ./tools/test_phase4a_prediction_system_ps_q16c_close_guard.py
# desc: Close guard for PS-Q16C WarRoom read-only producer status loader/panel.

from __future__ import annotations

import json
import subprocess
from pathlib import Path
from tempfile import TemporaryDirectory

from _btcts_bootstrap import ensure_btcts_on_syspath

ensure_btcts_on_syspath()

from btcts.apps.operator_ui.components.prediction_warroom_non_ui_scheduled_producer_runner import (  # noqa: E402
    build_prediction_warroom_non_ui_scheduled_producer_runner,
)
from btcts.apps.operator_ui.components.prediction_warroom_non_ui_scheduled_producer_status_panel import (  # noqa: E402
    PREDICTION_WARROOM_NON_UI_SCHEDULED_PRODUCER_STATUS_PANEL_VERSION,
    build_prediction_warroom_non_ui_scheduled_producer_status_panel_packet,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
EXPECTED_DIRTY = {
    "btcts_next/src/btcts/apps/operator_ui/components/prediction_warroom_non_ui_scheduled_producer_status_panel.py",
    "btcts_next/src/btcts/apps/operator_ui/tests/test_prediction_warroom_non_ui_scheduled_producer_status_panel.py",
    "docs/strategy/PREDICTION_SYSTEM_PS_Q16C_WARROOM_PRODUCER_STATUS_PANEL_2026-06-22.md",
    "tools/test_phase4a_prediction_system_ps_q16c_warroom_producer_status_panel_guard.py",
    "tools/test_phase4a_prediction_system_ps_q16c_close_guard.py",
    "btcts_next/src/btcts/apps/operator_ui/views/warroom_page.py",
}
REQUIRED_FILES = tuple(EXPECTED_DIRTY)
UNIT_TEST = "btcts_next/src/btcts/apps/operator_ui/tests/test_prediction_warroom_non_ui_scheduled_producer_status_panel.py"
FOCUSED_GUARD = "tools/test_phase4a_prediction_system_ps_q16c_warroom_producer_status_panel_guard.py"


def _dirty_paths() -> set[str]:
    proc = subprocess.run(["git", "status", "--short"], cwd=REPO_ROOT, text=True, capture_output=True, check=True)
    out: set[str] = set()
    for line in proc.stdout.splitlines():
        if line.strip():
            out.add(line[3:].replace(chr(92), "/"))
    return out


def main() -> int:
    failures: list[str] = []
    for rel in REQUIRED_FILES:
        if not (REPO_ROOT / rel).exists():
            failures.append(f"missing required file: {rel}")
    page_text = (REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/views/warroom_page.py").read_text(encoding="utf-8-sig")
    if "render_prediction_warroom_non_ui_scheduled_producer_status_panel" not in page_text:
        failures.append("WarRoom page must import/render PS-Q16C producer status panel")
    default_packet = build_prediction_warroom_non_ui_scheduled_producer_status_panel_packet().to_dict()
    if default_packet.get("panel_version") != PREDICTION_WARROOM_NON_UI_SCHEDULED_PRODUCER_STATUS_PANEL_VERSION:
        failures.append("panel version mismatch")
    if default_packet.get("actual_file_read_attempted") is not False:
        failures.append("default panel packet must not read without allow_actual_read")
    for key in (
        "producer_runner_invoked",
        "scheduler_enabled_by_this_panel",
        "warroom_ui_trigger_enabled",
        "runtime_artifact_write_allowed",
        "latest_prediction_artifact_write_allowed",
        "status_artifact_write_allowed",
        "would_write_runtime_artifact",
        "would_write_status_artifact",
        "would_write_latest_prediction_artifact",
        "parameter_apply_allowed",
        "parameter_staging_write_allowed",
        "autotrade_trigger_allowed",
        "broker_private_api_allowed",
    ):
        if default_packet.get(key) is not False:
            failures.append(f"unsafe/default flag must remain false: {key}={default_packet.get(key)!r}")
    with TemporaryDirectory() as temp_dir:
        writer = build_prediction_warroom_non_ui_scheduled_producer_runner(
            hot_latest_root_hint=temp_dir,
            operator_acknowledged=True,
            allow_status_artifact_write=True,
            execute_status_artifact_write=True,
            allow_guard_test_root=True,
        ).to_dict()
        packet = build_prediction_warroom_non_ui_scheduled_producer_status_panel_packet(
            hot_latest_root_hint=temp_dir,
            allow_actual_read=True,
            allow_guard_test_root=True,
        ).to_dict()
        if writer.get("status_artifact_written") is not True:
            failures.append("test setup status writer did not write")
        if packet.get("panel_state") != "producer_status_panel_loaded":
            failures.append("panel must read/decode explicit guard-root status artifact")
        if not packet.get("status_rows"):
            failures.append("loaded panel must expose status_rows")
        if not packet.get("safety_rows"):
            failures.append("loaded panel must expose safety_rows")
        if packet.get("producer_runner_invoked") is not False:
            failures.append("panel must not invoke producer runner")
        if packet.get("would_write_status_artifact") is not False:
            failures.append("panel must not write status artifact")
    dirty = _dirty_paths()
    unexpected_dirty = dirty - EXPECTED_DIRTY
    if unexpected_dirty:
        failures.append(f"unexpected dirty paths: {sorted(unexpected_dirty)}")
    payload = {
        "ok": not failures,
        "guard": "ps_q16c_close_guard",
        "phase": "phase3_prediction_system_warroom_realtime_observation_status_panel_closed",
        "focused_guards_to_run_before_commit": [UNIT_TEST, FOCUSED_GUARD],
        "contract": {
            "ps_q16c_closed": not failures,
            "next_slice": "PS-Q16D bounded manual refresh runner under explicit operator flags, no scheduler, no WarRoom UI trigger",
            "warroom_status_panel_mounted": "render_prediction_warroom_non_ui_scheduled_producer_status_panel" in page_text,
            "read_only_status_observation": True,
            "producer_runner_invoked": False,
            "scheduler_enabled_by_panel": False,
            "latest_prediction_write_by_panel": False,
            "autotrade_trigger_candidate_deferred": True,
        },
        "dirty_paths": sorted(dirty),
        "unexpected_dirty": sorted(unexpected_dirty),
        "failures": failures,
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if not failures else 1


def test_ps_q16c_close_guard() -> None:
    assert main() == 0


if __name__ == "__main__":
    raise SystemExit(main())
