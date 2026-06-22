# path: ./tools/test_phase4a_prediction_system_ps_q14a_source_readiness_explanation_guard.py
# desc: Guard for PS-Q14A WarRoom latest prediction source readiness explanation rows.

from __future__ import annotations

import json
import subprocess
from pathlib import Path

from _btcts_bootstrap import ensure_btcts_on_syspath

ensure_btcts_on_syspath()

from btcts.apps.operator_ui.components.prediction_warroom_latest_prediction_source_review_panel import (  # noqa: E402
    PREDICTION_WARROOM_LATEST_PREDICTION_SOURCE_READINESS_EXPLANATION_VERSION,
    build_prediction_warroom_latest_prediction_source_review_panel_packet,
    latest_prediction_source_readiness_explanation_rows,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
PANEL = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/components/prediction_warroom_latest_prediction_source_review_panel.py"
TEST = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/tests/test_prediction_warroom_latest_prediction_source_review_panel.py"
GUARD = REPO_ROOT / "tools/test_phase4a_prediction_system_ps_q14a_source_readiness_explanation_guard.py"
EXPECTED_DIRTY = {
    "btcts_next/src/btcts/apps/operator_ui/components/prediction_warroom_latest_prediction_source_review_panel.py",
    "btcts_next/src/btcts/apps/operator_ui/tests/test_prediction_warroom_latest_prediction_source_review_panel.py",
    "tools/test_phase4a_prediction_system_ps_q14a_source_readiness_explanation_guard.py",
}
REQUIRED_PANEL_MARKERS = (
    "PREDICTION_WARROOM_LATEST_PREDICTION_SOURCE_READINESS_EXPLANATION_VERSION",
    "prediction_warroom_latest_prediction_source_readiness_explanation.ps_q14a.v1",
    "latest_prediction_source_readiness_explanation_rows",
    "_source_readiness_category",
    "human_explanation_ja",
    "next_check_ja",
    "can_fix_in_warroom",
    "bypass_allowed",
    "PS-Q14A source-readiness explanations are human-readable",
    "does not change readiness or bypass blockers",
)
REQUIRED_TEST_MARKERS = (
    "PREDICTION_WARROOM_LATEST_PREDICTION_SOURCE_READINESS_EXPLANATION_VERSION",
    "latest_prediction_source_readiness_explanation_rows",
    "freshness_guard",
    "can_fix_in_warroom",
    "bypass_allowed",
    "readiness_explanation_row_count",
)
FORBIDDEN_TRUE_TOKENS = (
    "can_fix_in_warroom=True",
    "can_fix_in_warroom = True",
    "bypass_allowed=True",
    "bypass_allowed = True",
    "runtime_artifact_write_allowed=True",
    "ledger_append_allowed=True",
    "autotrade_trigger_allowed=True",
    "broker_private_api_allowed=True",
    "would_send_to_broker=True",
    "would_write_runtime_artifact=True",
    "mode_apply_requested=True",
    "approval_append_requested=True",
    "authorization_grant_requested=True",
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


def _blocked_sample() -> dict:
    return {
        "adapter_state": "latest_prediction_source_blocked",
        "source_summary": {},
        "review_packet_ready": False,
        "ready_for_warroom_review_panel": False,
        "session_state_updated": False,
        "q9b_loader_called_by_this_adapter": True,
        "actual_file_read_attempted": True,
        "actual_file_read_succeeded": False,
        "payload_decode_attempted": True,
        "payload_decode_succeeded": False,
        "loaded_payload_count": 0,
        "blocker_count": 3,
        "warning_count": 1,
        "blocked_reasons": [
            "freshness_status_stale_before_actual_read",
            "prediction_result_payload_mapping_missing",
            "q10k_session_state_handoff_not_updated",
        ],
        "warning_reasons": ["real_payload_review_packet_not_verified_by_ui_observation_yet"],
    }


def main() -> int:
    failures: list[str] = []
    for path in (PANEL, TEST, GUARD):
        if not path.exists():
            failures.append(f"missing file: {path.relative_to(REPO_ROOT)}")
    panel_text = _read(PANEL) if PANEL.exists() else ""
    test_text = _read(TEST) if TEST.exists() else ""
    for marker in REQUIRED_PANEL_MARKERS:
        if marker not in panel_text:
            failures.append(f"missing panel marker: {marker}")
    for marker in REQUIRED_TEST_MARKERS:
        if marker not in test_text:
            failures.append(f"missing test marker: {marker}")
    for token in FORBIDDEN_TRUE_TOKENS:
        if token in panel_text or token in test_text:
            failures.append(f"forbidden true token present: {token}")

    if PREDICTION_WARROOM_LATEST_PREDICTION_SOURCE_READINESS_EXPLANATION_VERSION != "prediction_warroom_latest_prediction_source_readiness_explanation.ps_q14a.v1":
        failures.append("readiness explanation version mismatch")
    rows = latest_prediction_source_readiness_explanation_rows(_blocked_sample())
    categories = [row.get("category") for row in rows]
    for expected in ("freshness_guard", "payload_read_decode_validation", "review_handoff", "operator_review_warning"):
        if expected not in categories:
            failures.append(f"missing category: {expected}")
    if not all(row.get("can_fix_in_warroom") is False for row in rows):
        failures.append("can_fix_in_warroom must remain false")
    if not all(row.get("bypass_allowed") is False for row in rows):
        failures.append("bypass_allowed must remain false")
    if not all(row.get("read_only") is True and row.get("execution") == "false" for row in rows):
        failures.append("readiness explanation rows must be read-only/non-executing")

    blocked_panel = build_prediction_warroom_latest_prediction_source_review_panel_packet(
        session_state={},
        allow_actual_read=False,
        store_in_session_state=False,
    )
    if blocked_panel.get("readiness_explanation_version") != PREDICTION_WARROOM_LATEST_PREDICTION_SOURCE_READINESS_EXPLANATION_VERSION:
        failures.append("panel missing readiness_explanation_version")
    if not blocked_panel.get("readiness_explanation_rows"):
        failures.append("panel missing readiness_explanation_rows")
    if blocked_panel.get("uicheck_snapshot", {}).get("readiness_explanation_row_count") != len(blocked_panel.get("readiness_explanation_rows", [])):
        failures.append("uicheck snapshot readiness_explanation_row_count mismatch")
    for key in (
        "warroom_page_mutation_allowed",
        "warroom_panel_mutation_allowed",
        "runtime_artifact_write_allowed",
        "ledger_append_allowed",
        "autotrade_trigger_allowed",
        "broker_private_api_allowed",
        "would_write_runtime_artifact",
        "would_write_collector_state",
        "would_send_to_broker",
        "broker_execution_requested",
        "mode_apply_requested",
        "command_ledger_append_requested",
        "approval_append_requested",
        "authorization_grant_requested",
        "autotrade_trigger_enabled",
    ):
        if blocked_panel.get(key) is not False:
            failures.append(f"panel {key} must remain false")

    dirty = _dirty_paths()
    unexpected_dirty = dirty - EXPECTED_DIRTY
    if unexpected_dirty:
        failures.append(f"unexpected dirty paths: {sorted(unexpected_dirty)}")
    payload = {
        "ok": not failures,
        "guard": "ps_q14a_source_readiness_explanation",
        "phase": "phase3_prediction_system_warroom_source_readiness_explanation",
        "contract": {
            "readiness_explanation_rows_present": not failures,
            "human_explanation_and_next_check_present": not failures,
            "bypass_not_allowed": not failures,
            "no_loader_or_readiness_behavior_change": not failures,
            "no_execution_surface": not failures,
            "expected_dirty_only": not unexpected_dirty,
        },
        "dirty_paths": sorted(dirty),
        "unexpected_dirty": sorted(unexpected_dirty),
        "failures": failures,
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if not failures else 1


def test_ps_q14a_source_readiness_explanation_guard() -> None:
    assert main() == 0


if __name__ == "__main__":
    raise SystemExit(main())
