# path: ./tools/test_phase4a_prediction_system_ps_q12g_warning_readability_guard.py
# desc: Guard for PS-Q12G read-only warning/readability polish in WarRoom latest prediction source panel.

from __future__ import annotations

import ast
import json
import subprocess
from pathlib import Path

from _btcts_bootstrap import ensure_btcts_on_syspath

ensure_btcts_on_syspath()

from btcts.apps.operator_ui.components.prediction_warroom_latest_prediction_source_review_panel import (  # noqa: E402
    PREDICTION_WARROOM_LATEST_PREDICTION_SOURCE_READABILITY_POLISH_VERSION,
    build_prediction_warroom_latest_prediction_source_review_panel_packet,
    latest_prediction_source_issue_rows,
    latest_prediction_source_readability_rows,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
PANEL = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/components/prediction_warroom_latest_prediction_source_review_panel.py"
TEST = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/tests/test_prediction_warroom_latest_prediction_source_review_panel.py"
GUARD = REPO_ROOT / "tools/test_phase4a_prediction_system_ps_q12g_warning_readability_guard.py"
EXPECTED_DIRTY = {
    "btcts_next/src/btcts/apps/operator_ui/components/prediction_warroom_latest_prediction_source_review_panel.py",
    "btcts_next/src/btcts/apps/operator_ui/tests/test_prediction_warroom_latest_prediction_source_review_panel.py",
    "tools/test_phase4a_prediction_system_ps_q12g_warning_readability_guard.py",
}
FORBIDDEN_TRUE_TOKENS = (
    "warroom_page_mutation_allowed=True",
    "warroom_page_mutation_allowed = True",
    "warroom_panel_mutation_allowed=True",
    "warroom_panel_mutation_allowed = True",
    "runtime_artifact_write_allowed=True",
    "runtime_artifact_write_allowed = True",
    "ledger_append_allowed=True",
    "ledger_append_allowed = True",
    "autotrade_trigger_allowed=True",
    "autotrade_trigger_allowed = True",
    "broker_private_api_allowed=True",
    "broker_private_api_allowed = True",
    "would_send_to_broker=True",
    "would_send_to_broker = True",
    "would_write_runtime_artifact=True",
    "would_write_runtime_artifact = True",
    "broker_execution_requested=True",
    "broker_execution_requested = True",
    "mode_apply_requested=True",
    "mode_apply_requested = True",
    "command_ledger_append_requested=True",
    "command_ledger_append_requested = True",
    "approval_append_requested=True",
    "approval_append_requested = True",
    "authorization_grant_requested=True",
    "authorization_grant_requested = True",
    "autotrade_trigger_enabled=True",
    "autotrade_trigger_enabled = True",
)


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _dirty_paths() -> set[str]:
    proc = subprocess.run(["git", "status", "--short"], cwd=REPO_ROOT, text=True, capture_output=True, check=True)
    out: set[str] = set()
    for line in proc.stdout.splitlines():
        if line.strip():
            out.add(line[3:].replace(chr(92), "/"))
    return out


def _sample_adapter(*, blocked: bool = False) -> dict:
    return {
        "adapter_state": "latest_prediction_source_blocked" if blocked else "latest_prediction_source_ready",
        "source_summary": {
            "prediction_run_id": "run-ps-q12g",
            "generated_at": "2026-06-22T14:00:00Z",
            "market_uid": "BTC_JPY:bitFlyer",
            "signal_strength_percent": 40,
            "signal_strength_band": "low_reference",
        },
        "review_packet_ready": not blocked,
        "ready_for_warroom_review_panel": not blocked,
        "session_state_updated": not blocked,
        "q9b_loader_called_by_this_adapter": True,
        "actual_file_read_attempted": True,
        "actual_file_read_succeeded": not blocked,
        "payload_decode_attempted": True,
        "payload_decode_succeeded": not blocked,
        "loaded_payload_count": 0 if blocked else 1,
        "blocker_count": 1 if blocked else 0,
        "warning_count": 2,
        "blocked_reasons": ["freshness_status_stale_before_actual_read"] if blocked else [],
        "warning_reasons": ["schema_validation_deferred_to_ps_q9c", "operator_review_warning"],
    }


def main() -> int:
    failures: list[str] = []
    for path in (PANEL, TEST, GUARD):
        if not path.exists():
            failures.append(f"missing file: {path.relative_to(REPO_ROOT)}")
            continue
        text = _read(path)
        try:
            ast.parse(text, filename=str(path))
        except SyntaxError as exc:
            failures.append(f"syntax failed: {path.relative_to(REPO_ROOT)}: {exc}")
    for path in (PANEL, TEST):
        text = _read(path)
        for token in FORBIDDEN_TRUE_TOKENS:
            if token in text:
                failures.append(f"forbidden true token in {path.relative_to(REPO_ROOT)}: {token}")

    panel_text = _read(PANEL)
    required_panel_markers = (
        "PREDICTION_WARROOM_LATEST_PREDICTION_SOURCE_READABILITY_POLISH_VERSION",
        "prediction_warroom_latest_prediction_source_readability_polish.ps_q12g.v1",
        "latest_prediction_source_readability_rows",
        "latest_prediction_source_issue_rows",
        "warning_readability_polish",
        "PS-Q12G readability summary is display-only",
        "warning/blocker detail rows are review-only",
        "no execution, no approval, no ledger, no AutoTrade, no broker/private API",
    )
    for marker in required_panel_markers:
        if marker not in panel_text:
            failures.append(f"missing panel marker: {marker}")

    if PREDICTION_WARROOM_LATEST_PREDICTION_SOURCE_READABILITY_POLISH_VERSION != "prediction_warroom_latest_prediction_source_readability_polish.ps_q12g.v1":
        failures.append("readability polish version mismatch")

    ready_rows = latest_prediction_source_readability_rows(_sample_adapter(blocked=False))
    ready_map = {row.get("item"): row for row in ready_rows}
    if [row.get("item") for row in ready_rows] != ["source_panel", "payload_load_decode", "q9g_review_handoff", "warnings", "blockers", "signal"]:
        failures.append("readability row order mismatch")
    if ready_map.get("source_panel", {}).get("severity") != "ok":
        failures.append("ready source_panel severity must be ok")
    if ready_map.get("warnings", {}).get("severity") != "warning":
        failures.append("warnings severity must be warning when warning_count > 0")
    if ready_map.get("blockers", {}).get("severity") != "ok":
        failures.append("blockers severity must be ok when blocker_count=0")
    if ready_map.get("signal", {}).get("severity") != "review_only":
        failures.append("signal row must be review_only")
    if not all(row.get("read_only") is True and row.get("execution") == "false" for row in ready_rows):
        failures.append("readability rows must remain read-only/non-executing")

    blocked_rows = latest_prediction_source_readability_rows(_sample_adapter(blocked=True))
    blocked_map = {row.get("item"): row for row in blocked_rows}
    for key in ("source_panel", "payload_load_decode", "q9g_review_handoff", "blockers"):
        if blocked_map.get(key, {}).get("severity") != "blocker":
            failures.append(f"blocked {key} severity must be blocker")
    issue_rows = latest_prediction_source_issue_rows(_sample_adapter(blocked=True))
    if issue_rows[0].get("severity") != "blocker" or issue_rows[0].get("reason") != "freshness_status_stale_before_actual_read":
        failures.append("blocked issue row must surface blocker first")
    if not all(row.get("read_only") is True and row.get("execution") == "false" for row in issue_rows):
        failures.append("issue rows must remain read-only/non-executing")

    blocked_panel = build_prediction_warroom_latest_prediction_source_review_panel_packet(
        session_state={},
        allow_actual_read=False,
        store_in_session_state=False,
    )
    if blocked_panel.get("readability_polish_version") != PREDICTION_WARROOM_LATEST_PREDICTION_SOURCE_READABILITY_POLISH_VERSION:
        failures.append("panel missing readability polish version")
    if blocked_panel.get("warning_readability_polish") is not True:
        failures.append("panel missing warning_readability_polish true marker")
    if not isinstance(blocked_panel.get("readability_rows"), list) or not blocked_panel.get("readability_rows"):
        failures.append("panel readability_rows missing")
    if not isinstance(blocked_panel.get("issue_rows"), list) or not blocked_panel.get("issue_rows"):
        failures.append("panel issue_rows missing")
    for key in (
        "read_only",
        "non_executing",
        "display_only",
        "render_intent_only",
    ):
        if blocked_panel.get(key) is not True:
            failures.append(f"panel {key} must be true")
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
        "guard": "ps_q12g_warning_readability",
        "phase": "phase3_prediction_system_warroom_read_only_inference_display",
        "contract": {
            "display_only_warning_readability": not failures,
            "readability_rows_present": not failures,
            "issue_rows_present": not failures,
            "no_loader_behavior_change_required": not failures,
            "no_execution_surface": not failures,
            "expected_dirty_only": not unexpected_dirty,
        },
        "dirty_paths": sorted(dirty),
        "unexpected_dirty": sorted(unexpected_dirty),
        "failures": failures,
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if not failures else 1


def test_ps_q12g_warning_readability_guard() -> None:
    assert main() == 0


if __name__ == "__main__":
    raise SystemExit(main())
