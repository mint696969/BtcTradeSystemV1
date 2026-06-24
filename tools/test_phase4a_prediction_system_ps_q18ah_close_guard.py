# path: ./tools/test_phase4a_prediction_system_ps_q18ah_close_guard.py
# desc: Close guard for PS-Q18AH render-disabled packet builder validation.

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

BTCTS_SRC = Path(__file__).resolve().parents[1] / "btcts_next" / "src"
if str(BTCTS_SRC) not in sys.path:
    sys.path.insert(0, str(BTCTS_SRC))

from btcts.apps.operator_ui.prediction_warroom.mapping.latest_prediction_summary_widget_q18ah_render_disabled_packet_builder_validation import FALSE_BOUNDARIES, LATEST_PREDICTION_SUMMARY_WIDGET_Q18AH_RENDER_DISABLED_PACKET_BUILDER_VALIDATION_ACK, TRUE_BOUNDARIES  # noqa: E402
from btcts.apps.operator_ui.prediction_warroom.presenters.latest_prediction_summary_widget_q18ah_render_disabled_packet_rows import build_latest_prediction_summary_widget_q18ah_render_disabled_packet_result_packet  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parents[1]
EXPECTED_DIRTY = {
    "btcts_next/src/btcts/apps/operator_ui/prediction_warroom/mapping/latest_prediction_summary_widget_q18ah_render_disabled_packet_builder_validation.py",
    "btcts_next/src/btcts/apps/operator_ui/prediction_warroom/presenters/latest_prediction_summary_widget_q18ah_render_disabled_packet_rows.py",
    "docs/strategy/PREDICTION_SYSTEM_PS_Q18AH_LATEST_PREDICTION_SUMMARY_WIDGET_RENDER_DISABLED_PACKET_VALIDATION_2026-06-24.md",
    "tools/test_phase4a_prediction_system_ps_q18ah_close_guard.py",
    "tools/test_phase4a_prediction_system_ps_q18ah_latest_prediction_summary_widget_render_disabled_packet.py",
    "tools/test_phase4a_prediction_system_ps_q18ah_render_disabled_packet_guard.py",
}


def _is_noise_path(rel: str) -> bool:
    return "/__pycache__/" in rel or rel.endswith(".pyc")


def _dirty_paths() -> set[str]:
    proc = subprocess.run(["git", "status", "--short"], cwd=REPO_ROOT, text=True, capture_output=True, check=True)
    paths: set[str] = set()
    for line in proc.stdout.splitlines():
        if not line.strip():
            continue
        rel = line[3:].replace(chr(92), "/")
        absolute = REPO_ROOT / rel
        if rel.endswith("/") and absolute.exists():
            for child in absolute.rglob("*"):
                if child.is_file():
                    child_rel = child.relative_to(REPO_ROOT).as_posix()
                    if not _is_noise_path(child_rel):
                        paths.add(child_rel)
        elif not _is_noise_path(rel):
            paths.add(rel)
    return paths


def main_guard() -> int:
    failures: list[str] = []
    packet = build_latest_prediction_summary_widget_q18ah_render_disabled_packet_result_packet(
        execute_packet_builder_validation=True,
        explicit_ack=LATEST_PREDICTION_SUMMARY_WIDGET_Q18AH_RENDER_DISABLED_PACKET_BUILDER_VALIDATION_ACK,
    )
    if packet.get("ok") is not True:
        failures.append(f"Q18AH packet must be ok: {packet}")
    if packet.get("component_packet_valid") is not True:
        failures.append("component packet must be valid")
    if packet.get("render_disabled_packet_row_count") != 12:
        failures.append("render-disabled row count must be 12")
    for key in TRUE_BOUNDARIES:
        if packet.get(key) is not True:
            failures.append(f"{key} must be true")
    for key in FALSE_BOUNDARIES:
        if packet.get(key) is not False:
            failures.append(f"{key} must stay false")
    for key in ("streamlit_render_invoked", "real_prediction_widget_render_invoked", "real_prediction_widget_rendering_allowed", "refresh_invocation_allowed", "runtime_artifact_write_allowed", "autotrade_trigger_allowed", "broker_private_api_allowed"):
        if packet.get(key) is not False:
            failures.append(f"{key} must remain false in close guard")
    dirty = _dirty_paths()
    unexpected = dirty - EXPECTED_DIRTY
    missing = EXPECTED_DIRTY - dirty
    if unexpected:
        failures.append(f"unexpected dirty paths: {sorted(unexpected)}")
    if missing:
        failures.append(f"missing expected dirty paths: {sorted(missing)}")
    result = {
        "ok": not failures,
        "guard": "ps_q18ah_close_guard",
        "phase": "phase3_latest_prediction_summary_widget_render_disabled_packet_validation_before_warroom_mount_refresh_and_writes",
        "contract": {
            "ps_q18ah_closed": not failures,
            "component_packet_valid": packet.get("component_packet_valid"),
            "component_packet_state": packet.get("component_packet_state"),
            "mapped_record_count": packet.get("mapped_record_count"),
            "component_source_generated_at": packet.get("component_source_generated_at"),
            "streamlit_render_invoked": False,
            "real_prediction_widget_render_invoked": False,
            "refresh_invocation_allowed": False,
            "next_slice": "WarRoom render-disabled packet status/value panel mount",
        },
        "dirty_paths": sorted(dirty),
        "unexpected_dirty": sorted(unexpected),
        "missing_dirty": sorted(missing),
        "failures": failures,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if not failures else 1


def test_ps_q18ah_close_guard() -> None:
    assert main_guard() == 0


if __name__ == "__main__":
    raise SystemExit(main_guard())
