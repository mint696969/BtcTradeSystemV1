# path: ./tools/test_phase4a_prediction_system_ps_q12_thread_closeout_guard.py
# desc: Guard for PS-Q12 thread closeout documentation.

from __future__ import annotations

import json
import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
DOC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q12_THREAD_CLOSEOUT_2026-06-22.md"
EXPECTED_DIRTY = {
    "docs/strategy/PREDICTION_SYSTEM_PS_Q12_THREAD_CLOSEOUT_2026-06-22.md",
    "tools/test_phase4a_prediction_system_ps_q12_thread_closeout_guard.py",
}
BS = chr(92)
ARTIFACT_MARKER = "artifact_path=D:" + BS + "btc_ts_hot" + BS + "prediction" + BS + "latest_prediction_system_result.json"
CHECK_ALLOW_MISSING_CMD = "python ." + BS + "tools" + BS + "check_phase4a_prediction_system_ps_q12h_warroom_uicheck_snapshot.py --allow-missing"
REQUIRED_MARKERS = (
    "Head at closeout candidate: 7bd437ac",
    "74a21f6c PS-Q12A WarRoom latest prediction source adapter",
    "a4b84292 PS-Q12B WarRoom inference panel connection",
    "14ed153f PS-Q12C WarRoom live inference smoke CLI",
    "PS-Q12D operator refresh observation",
    "PS-Q12E WarRoom UI observation",
    "5d66089a PS-Q12F UI observed closeout docs/guard",
    "db4b7628 PS-Q12G warning/readability polish",
    "7bd437ac PS-Q12H UI Check snapshot/check automation",
    "WarRoom top/default-expanded Prediction WarRoom real payload review is connected.",
    "PS-Q12H checker validates tmp/uicheck/uicheck_*_warroom.json",
    ARTIFACT_MARKER,
    "prediction_run_id=prediction_system.ps_g_lite.v1:BTC_JPY:bitFlyer:2026-06-21T21:49:47Z",
    "panel_state=latest_prediction_source_review_panel_ready",
    "adapter_state=latest_prediction_source_ready",
    "q9g_contract_state=visibility_review_ready_for_ps_q9g_guarded_ui_mount_with_warnings",
    "blocker_count=0",
    "warning_count=5",
    CHECK_ALLOW_MISSING_CMD,
    "AutoTrade execution was not resumed.",
    "Broker integration was not added.",
    "Mode apply was not added.",
    "Order placement was not added.",
    "Approval/grant execution was not added.",
    "Decision ledger append was not added.",
    "Command ledger append was not added.",
    "WarRoom UI trigger bridge was not added.",
    "WarRoom UI export controls were not added.",
    "WarRoom UI runtime artifact write was not added.",
    "Freshness bypass was not added.",
    "Broker/private API was not added.",
    "read_only=true",
    "non_executing=true",
    "display_only=true",
    "would_send_to_broker=false",
    "would_write_runtime_artifact=false",
    "approval_or_authorization_allowed=false",
    "ledger_append_allowed=false",
    "autotrade_trigger_allowed=false",
    "broker_private_api_allowed=false",
    "requires a separate explicit human scope and approval",
)
FORBIDDEN_ENABLEMENT_MARKERS = (
    "AutoTrade execution was resumed",
    "Broker integration was added",
    "Mode apply was added",
    "Order placement was added",
    "Approval/grant execution was added",
    "Decision ledger append was added",
    "Command ledger append was added",
    "WarRoom UI trigger bridge was added",
    "WarRoom UI export controls were added",
    "WarRoom UI runtime artifact write was added",
    "Freshness bypass was added",
    "Broker/private API was added",
)


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8-sig")


def _dirty_paths() -> set[str]:
    proc = subprocess.run(["git", "status", "--short"], cwd=REPO_ROOT, text=True, capture_output=True, check=True)
    out: set[str] = set()
    for line in proc.stdout.splitlines():
        if line.strip():
            out.add(line[3:].replace(chr(92), "/"))
    return out


def main() -> int:
    failures: list[str] = []
    if not DOC.exists():
        failures.append(f"missing doc: {DOC.relative_to(REPO_ROOT)}")
        text = ""
    else:
        text = _read(DOC)
    for marker in REQUIRED_MARKERS:
        if marker not in text:
            failures.append(f"missing closeout marker: {marker}")
    for marker in FORBIDDEN_ENABLEMENT_MARKERS:
        if marker in text:
            failures.append(f"forbidden enablement marker present: {marker}")
    dirty = _dirty_paths()
    unexpected_dirty = dirty - EXPECTED_DIRTY
    if unexpected_dirty:
        failures.append(f"unexpected dirty paths: {sorted(unexpected_dirty)}")
    payload = {
        "ok": not failures,
        "guard": "ps_q12_thread_closeout",
        "phase": "phase3_prediction_system_warroom_read_only_inference_display",
        "contract": {
            "thread_closeout_doc_present": not failures,
            "ps_q12_a_to_h_lineage_recorded": not failures,
            "read_only_non_executing_boundary_recorded": not failures,
            "no_execution_surface_enabled": not failures,
            "expected_dirty_only": not unexpected_dirty,
        },
        "dirty_paths": sorted(dirty),
        "unexpected_dirty": sorted(unexpected_dirty),
        "failures": failures,
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if not failures else 1


def test_ps_q12_thread_closeout_guard() -> None:
    assert main() == 0


if __name__ == "__main__":
    raise SystemExit(main())
