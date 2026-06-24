# path: ./tools/test_phase4a_prediction_system_ps_q18ag_close_guard.py
# desc: Close guard for PS-Q18AG payload-to-widget props mapping preflight.

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

BTCTS_SRC = Path(__file__).resolve().parents[1] / "btcts_next" / "src"
if str(BTCTS_SRC) not in sys.path:
    sys.path.insert(0, str(BTCTS_SRC))

from btcts.apps.operator_ui.prediction_warroom.mapping.latest_prediction_summary_widget_q18ag_payload_to_props_mapping_preflight import FALSE_BOUNDARIES, LATEST_PREDICTION_SUMMARY_WIDGET_Q18AG_PAYLOAD_TO_PROPS_MAPPING_PREFLIGHT_ACK, TRUE_BOUNDARIES  # noqa: E402
from btcts.apps.operator_ui.prediction_warroom.presenters.latest_prediction_summary_widget_q18ag_payload_to_props_mapping_rows import build_latest_prediction_summary_widget_q18ag_payload_to_props_mapping_result_packet  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parents[1]
EXPECTED_DIRTY = {
    "btcts_next/src/btcts/apps/operator_ui/prediction_warroom/mapping/__init__.py",
    "btcts_next/src/btcts/apps/operator_ui/prediction_warroom/mapping/latest_prediction_summary_widget_q18ag_payload_to_props_mapping_preflight.py",
    "btcts_next/src/btcts/apps/operator_ui/prediction_warroom/presenters/latest_prediction_summary_widget_q18ag_payload_to_props_mapping_rows.py",
    "docs/strategy/PREDICTION_SYSTEM_PS_Q18AG_LATEST_PREDICTION_SUMMARY_WIDGET_PAYLOAD_TO_PROPS_MAPPING_PREFLIGHT_2026-06-24.md",
    "tools/test_phase4a_prediction_system_ps_q18ag_close_guard.py",
    "tools/test_phase4a_prediction_system_ps_q18ag_latest_prediction_summary_widget_payload_to_props_mapping.py",
    "tools/test_phase4a_prediction_system_ps_q18ag_payload_to_props_mapping_guard.py",
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
    packet = build_latest_prediction_summary_widget_q18ag_payload_to_props_mapping_result_packet(
        execute_mapping_preflight=True,
        explicit_ack=LATEST_PREDICTION_SUMMARY_WIDGET_Q18AG_PAYLOAD_TO_PROPS_MAPPING_PREFLIGHT_ACK,
    )
    if packet.get("ok") is not True:
        failures.append(f"Q18AG packet must be ok: {packet}")
    if packet.get("props_contract_complete") is not True:
        failures.append("props contract must be complete")
    if packet.get("payload_to_props_mapping_row_count") != 12:
        failures.append("mapping row count must be 12")
    for key in TRUE_BOUNDARIES:
        if packet.get(key) is not True:
            failures.append(f"{key} must be true")
    for key in FALSE_BOUNDARIES:
        if packet.get(key) is not False:
            failures.append(f"{key} must stay false")
    for key in ("component_props_bound_to_component", "render_latest_prediction_summary_widget_invoked", "real_prediction_widget_rendering_allowed", "refresh_invocation_allowed", "runtime_artifact_write_allowed", "autotrade_trigger_allowed", "broker_private_api_allowed"):
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
        "guard": "ps_q18ag_close_guard",
        "phase": "phase3_latest_prediction_summary_widget_payload_to_props_mapping_preflight_before_render_refresh_and_writes",
        "contract": {
            "ps_q18ag_closed": not failures,
            "props_contract_complete": packet.get("props_contract_complete"),
            "record_count": packet.get("record_count"),
            "mapped_generated_at": packet.get("mapped_generated_at"),
            "component_props_bound_to_component": False,
            "render_latest_prediction_summary_widget_invoked": False,
            "real_prediction_widget_rendering_allowed": False,
            "path_shape_preview": packet.get("path_shape_preview"),
            "next_slice": "render-disabled packet builder validation",
        },
        "dirty_paths": sorted(dirty),
        "unexpected_dirty": sorted(unexpected),
        "missing_dirty": sorted(missing),
        "failures": failures,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if not failures else 1


def test_ps_q18ag_close_guard() -> None:
    assert main_guard() == 0


if __name__ == "__main__":
    raise SystemExit(main_guard())
