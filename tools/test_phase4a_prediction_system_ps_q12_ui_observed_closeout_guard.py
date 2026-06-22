# path: ./tools/test_phase4a_prediction_system_ps_q12_ui_observed_closeout_guard.py
# desc: Guard for PS-Q12 WarRoom inference UI observed closeout documentation.

from __future__ import annotations

import json
import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
DOC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q12_WARROOM_INFERENCE_UI_OBSERVED_2026-06-22.md"
EXPECTED_DIRTY = {
    "docs/strategy/PREDICTION_SYSTEM_PS_Q12_WARROOM_INFERENCE_UI_OBSERVED_2026-06-22.md",
    "tools/test_phase4a_prediction_system_ps_q12_ui_observed_closeout_guard.py",
}

REQUIRED_MARKERS = (
    "Head at UI observation: 14ed153f",
    "74a21f6c PS-Q12A WarRoom latest prediction source adapter",
    "a4b84292 PS-Q12B WarRoom inference panel connection",
    "14ed153f PS-Q12C WarRoom live inference smoke CLI",
    "PS-Q12D operator refresh observation",
    "PS-Q12E WarRoom UI observation",
    r"artifact_path=D:\btc_ts_hot\prediction\latest_prediction_system_result.json",
    "artifact_size_bytes=2981055",
    "prediction_run_id=prediction_system.ps_g_lite.v1:BTC_JPY:bitFlyer:2026-06-21T21:49:47Z",
    "generated_at=2026-06-21T21:49:47Z",
    "market_uid=BTC_JPY:bitFlyer",
    "panel_state=latest_prediction_source_review_panel_ready",
    "adapter_state=latest_prediction_source_ready",
    "loaded_payloads=1",
    "review_ready=True",
    "session_handoff=True",
    "signal_strength=40 / low_reference",
    "contract_state=visibility_review_ready_for_ps_q9g_guarded_ui_mount_with_warnings",
    "ready_for_ps_q9g_guarded_ui_mount=True",
    "display_packet_present=True",
    "display_packet_valid=True",
    "widget_group_count=6",
    "visible_widget_group_count=6",
    "blocker_count=0",
    "warning_count=5",
    "read_only=true",
    "execution=false",
    "autotrade=false",
    "broker=false",
    "warroom_page_mutation=false",
    "runtime_artifact_write=false",
    "approval_or_authorization=false",
    "decision_or_command_ledger_append=false",
    "would_send_to_broker=false",
    "would_write_runtime_artifact=false",
    "AutoTrade execution was not resumed.",
    "Broker integration was not added.",
    "Mode apply was not added.",
    "Order placement was not added.",
    "Approval/grant execution was not added.",
    "Decision ledger append was not added.",
    "Command ledger append was not added.",
    "WarRoom UI trigger bridge was not added.",
    "Freshness bypass was not added.",
    "read-only UI polish / warning readability / observation automation",
    "Do not add trigger bridge, approval/ledger append, broker/mode/order, AutoTrade, or WarRoom runtime-write behavior",
)

FORBIDDEN_ENABLEMENT_MARKERS = (
    "AutoTrade execution was resumed",
    "broker integration was added",
    "Mode apply was added",
    "Order placement was added",
    "approval/grant execution was added",
    "Decision ledger append was added",
    "Command ledger append was added",
    "WarRoom UI trigger bridge was added",
    "Freshness bypass was added",
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
        "guard": "ps_q12_ui_observed_closeout_docs",
        "phase": "phase3_prediction_system_warroom_read_only_inference_display",
        "contract": {
            "docs_only": not failures,
            "ui_observed_ready_recorded": not failures,
            "q9g_review_rows_recorded": not failures,
            "read_only_boundaries_recorded": not failures,
            "execution_surfaces_not_enabled": not failures,
            "expected_dirty_only": not unexpected_dirty,
        },
        "dirty_paths": sorted(dirty),
        "unexpected_dirty": sorted(unexpected_dirty),
        "failures": failures,
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if not failures else 1


def test_ps_q12_ui_observed_closeout_guard() -> None:
    assert main() == 0


if __name__ == "__main__":
    raise SystemExit(main())
