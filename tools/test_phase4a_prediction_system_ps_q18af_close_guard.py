# path: ./tools/test_phase4a_prediction_system_ps_q18af_close_guard.py
# desc: Close guard for PS-Q18AF bounded JSON schema probe.

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

BTCTS_SRC = Path(__file__).resolve().parents[1] / "btcts_next" / "src"
if str(BTCTS_SRC) not in sys.path:
    sys.path.insert(0, str(BTCTS_SRC))

from btcts.apps.operator_ui.prediction_warroom.sources.latest_prediction_summary_widget_q18af_schema_probe import FALSE_BOUNDARIES, LATEST_PREDICTION_SUMMARY_WIDGET_Q18AF_SCHEMA_PROBE_ACK, TRUE_BOUNDARIES  # noqa: E402
from btcts.apps.operator_ui.prediction_warroom.presenters.latest_prediction_summary_widget_q18af_schema_probe_rows import build_latest_prediction_summary_widget_q18af_schema_probe_result_packet  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parents[1]
EXPECTED_DIRTY = {
    "btcts_next/src/btcts/apps/operator_ui/prediction_warroom/sources/latest_prediction_summary_widget_q18af_schema_probe.py",
    "btcts_next/src/btcts/apps/operator_ui/prediction_warroom/presenters/latest_prediction_summary_widget_q18af_schema_probe_rows.py",
    "docs/strategy/PREDICTION_SYSTEM_PS_Q18AF_LATEST_PREDICTION_SUMMARY_WIDGET_SCHEMA_PROBE_2026-06-24.md",
    "tools/test_phase4a_prediction_system_ps_q18af_close_guard.py",
    "tools/test_phase4a_prediction_system_ps_q18af_latest_prediction_summary_widget_schema_probe.py",
    "tools/test_phase4a_prediction_system_ps_q18af_schema_probe_guard.py",
}


def _dirty_paths() -> set[str]:
    proc = subprocess.run(["git", "status", "--short"], cwd=REPO_ROOT, text=True, capture_output=True, check=True)
    return {line[3:].replace(chr(92), "/") for line in proc.stdout.splitlines() if line.strip() and "/__pycache__/" not in line and not line.endswith(".pyc")}


def main_guard() -> int:
    failures: list[str] = []
    packet = build_latest_prediction_summary_widget_q18af_schema_probe_result_packet(
        execute_schema_probe=True,
        explicit_ack=LATEST_PREDICTION_SUMMARY_WIDGET_Q18AF_SCHEMA_PROBE_ACK,
    )
    if packet.get("ok") is not True:
        failures.append(f"Q18AF packet must be ok: {packet}")
    if packet.get("source_artifact_schema_valid") is not True:
        failures.append("schema must be valid")
    if packet.get("schema_probe_row_count") != 12:
        failures.append("schema probe row count must be 12")
    for key in TRUE_BOUNDARIES:
        if packet.get(key) is not True:
            failures.append(f"{key} must be true")
    for key in FALSE_BOUNDARIES:
        if packet.get(key) is not False:
            failures.append(f"{key} must stay false")
    for key in ("actual_source_read_invoked", "payload_to_widget_mapping_invoked", "real_prediction_widget_rendering_allowed", "refresh_invocation_allowed", "runtime_artifact_write_allowed", "autotrade_trigger_allowed", "broker_private_api_allowed"):
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
        "guard": "ps_q18af_close_guard",
        "phase": "phase3_latest_prediction_summary_widget_schema_probe_before_mapping_render_refresh_and_writes",
        "contract": {
            "ps_q18af_closed": not failures,
            "source_artifact_schema_valid": packet.get("source_artifact_schema_valid"),
            "record_count": packet.get("record_count"),
            "observed_file_size_bytes": packet.get("observed_file_size_bytes"),
            "actual_source_read_invoked": False,
            "payload_to_widget_mapping_invoked": False,
            "real_prediction_widget_rendering_allowed": False,
            "path_shape_preview": packet.get("path_shape_preview"),
            "next_slice": "actual source read handoff or payload-to-widget props mapping preflight",
        },
        "dirty_paths": sorted(dirty),
        "unexpected_dirty": sorted(unexpected),
        "missing_dirty": sorted(missing),
        "failures": failures,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if not failures else 1


def test_ps_q18af_close_guard() -> None:
    assert main_guard() == 0


if __name__ == "__main__":
    raise SystemExit(main_guard())
