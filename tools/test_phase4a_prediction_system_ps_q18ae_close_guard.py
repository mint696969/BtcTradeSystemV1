# path: ./tools/test_phase4a_prediction_system_ps_q18ae_close_guard.py
# desc: Close guard for PS-Q18AE latest_prediction_summary_widget candidate resolver refresh.

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

BTCTS_SRC = Path(__file__).resolve().parents[1] / "btcts_next" / "src"
if str(BTCTS_SRC) not in sys.path:
    sys.path.insert(0, str(BTCTS_SRC))

from btcts.apps.operator_ui.prediction_warroom.sources.latest_prediction_summary_widget_q18ae_candidate_resolver_refresh import FALSE_BOUNDARIES, LATEST_PREDICTION_SUMMARY_WIDGET_Q18AE_CANDIDATE_RESOLVER_REFRESH_ACK, TRUE_BOUNDARIES  # noqa: E402
from btcts.apps.operator_ui.prediction_warroom.presenters.latest_prediction_summary_widget_q18ae_candidate_resolver_refresh_rows import build_latest_prediction_summary_widget_q18ae_candidate_resolver_refresh_result_packet  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parents[1]
EXPECTED_DIRTY = {
    "btcts_next/src/btcts/apps/operator_ui/prediction_warroom/sources/latest_prediction_summary_widget_q18ae_candidate_resolver_refresh.py",
    "btcts_next/src/btcts/apps/operator_ui/prediction_warroom/presenters/latest_prediction_summary_widget_q18ae_candidate_resolver_refresh_rows.py",
    "docs/strategy/PREDICTION_SYSTEM_PS_Q18AE_LATEST_PREDICTION_SUMMARY_WIDGET_CANDIDATE_RESOLVER_REFRESH_2026-06-24.md",
    "tools/test_phase4a_prediction_system_ps_q18ae_candidate_resolver_refresh_guard.py",
    "tools/test_phase4a_prediction_system_ps_q18ae_close_guard.py",
    "tools/test_phase4a_prediction_system_ps_q18ae_latest_prediction_summary_widget_candidate_resolver_refresh.py",
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
    packet = build_latest_prediction_summary_widget_q18ae_candidate_resolver_refresh_result_packet(
        execute_refreshed_candidate_exists_check=True,
        explicit_ack=LATEST_PREDICTION_SUMMARY_WIDGET_Q18AE_CANDIDATE_RESOLVER_REFRESH_ACK,
    )
    if packet.get("ok") is not True:
        failures.append(f"Q18AE packet must be ok: {packet}")
    if packet.get("refreshed_candidate_exists_result_state") != "present":
        failures.append("refreshed candidate result state must be present")
    if packet.get("candidate_resolver_refresh_row_count") != 12:
        failures.append("candidate resolver refresh row count must be 12")
    for key in TRUE_BOUNDARIES:
        if packet.get(key) is not True:
            failures.append(f"{key} must be true")
    for key in FALSE_BOUNDARIES:
        if packet.get(key) is not False:
            failures.append(f"{key} must stay false")
    for key in ("source_artifact_schema_checked", "actual_source_read_invoked", "payload_parse_allowed", "real_prediction_widget_rendering_allowed", "refresh_invocation_allowed", "runtime_artifact_write_allowed", "autotrade_trigger_allowed", "broker_private_api_allowed"):
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
        "guard": "ps_q18ae_close_guard",
        "phase": "phase3_latest_prediction_summary_widget_candidate_resolver_refresh_before_schema_read_refresh_and_writes",
        "contract": {
            "ps_q18ae_closed": not failures,
            "previous_candidate_exists_result_state": packet.get("previous_candidate_exists_result_state"),
            "refreshed_candidate_exists_result_state": packet.get("refreshed_candidate_exists_result_state"),
            "refreshed_candidate_path_shape_preview": packet.get("refreshed_candidate_path_shape_preview"),
            "source_artifact_schema_checked": False,
            "actual_source_read_invoked": False,
            "real_prediction_widget_rendering_allowed": False,
            "next_slice": "schema validation against refreshed present latest prediction artifact",
        },
        "dirty_paths": sorted(dirty),
        "unexpected_dirty": sorted(unexpected),
        "missing_dirty": sorted(missing),
        "failures": failures,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if not failures else 1


def test_ps_q18ae_close_guard() -> None:
    assert main_guard() == 0


if __name__ == "__main__":
    raise SystemExit(main_guard())
