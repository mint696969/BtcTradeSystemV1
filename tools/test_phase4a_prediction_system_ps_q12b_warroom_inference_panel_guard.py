# path: ./tools/test_phase4a_prediction_system_ps_q12b_warroom_inference_panel_guard.py
# desc: Close guard for PS-Q12B WarRoom read-only inference panel connection.

from __future__ import annotations

import ast
import json
import subprocess
from pathlib import Path

from _btcts_bootstrap import ensure_btcts_on_syspath

ensure_btcts_on_syspath()

import btcts.apps.operator_ui.components.prediction_warroom_latest_prediction_source_review_panel as panel_mod  # noqa: E402
from btcts.apps.operator_ui.components.prediction_warroom_latest_prediction_source_review_panel import (  # noqa: E402
    PREDICTION_WARROOM_LATEST_PREDICTION_SOURCE_REVIEW_PANEL_VERSION,
    build_prediction_warroom_latest_prediction_source_review_panel_packet,
    latest_prediction_source_boundary_rows,
    latest_prediction_source_status_rows,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
PANEL = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/components/prediction_warroom_latest_prediction_source_review_panel.py"
TEST = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/tests/test_prediction_warroom_latest_prediction_source_review_panel.py"
WARROOM = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/views/warroom_page.py"
EXPECTED_DIRTY = {
    "btcts_next/src/btcts/apps/operator_ui/components/prediction_warroom_latest_prediction_source_review_panel.py",
    "btcts_next/src/btcts/apps/operator_ui/tests/test_prediction_warroom_latest_prediction_source_review_panel.py",
    "btcts_next/src/btcts/apps/operator_ui/views/warroom_page.py",
    "tools/test_phase4a_prediction_system_ps_q12b_warroom_inference_panel_guard.py",
}
FORBIDDEN_TRUE_TOKENS = (
    "warroom_page_mutation_allowed=True",
    "warroom_page_mutation_allowed = True",
    "warroom_panel_mutation_allowed=True",
    "warroom_panel_mutation_allowed = True",
    "runtime_artifact_write_allowed=True",
    "runtime_artifact_write_allowed = True",
    "approval_or_authorization_allowed=True",
    "approval_or_authorization_allowed = True",
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
    proc = subprocess.run(
        ["git", "status", "--short"],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=True,
    )
    out: set[str] = set()
    for line in proc.stdout.splitlines():
        if line.strip():
            out.add(line[3:].replace(chr(92), "/"))
    return out


def _stub_adapter_packet(*, allow_actual_read: bool, session_state: dict | None, store_in_session_state: bool, **_: object):
    class _Packet:
        def to_dict(self) -> dict:
            if store_in_session_state and session_state is not None:
                session_state["warroom_prediction_lowered_display_packet_visibility_review_packet"] = {"seeded": True}
            return {
                "adapter_state": "latest_prediction_source_ready" if allow_actual_read else "latest_prediction_source_blocked",
                "source_summary": {
                    "prediction_run_id": "stub-ps-q12b",
                    "generated_at": "2026-06-22T12:00:00Z",
                    "market_uid": "bitflyer.spot.BTC_JPY",
                    "signal_strength_percent": 70,
                    "signal_strength_band": "medium",
                },
                "review_packet_ready": bool(allow_actual_read),
                "ready_for_warroom_review_panel": bool(allow_actual_read),
                "session_state_updated": bool(store_in_session_state and session_state is not None and allow_actual_read),
                "q9b_loader_called_by_this_adapter": bool(allow_actual_read),
                "actual_file_read_attempted": bool(allow_actual_read),
                "payload_decode_attempted": bool(allow_actual_read),
                "loaded_payload_count": 1 if allow_actual_read else 0,
                "blocked_reasons": [] if allow_actual_read else ["allow_actual_read_false"],
                "warning_reasons": [],
                "would_send_to_broker": False,
                "would_write_runtime_artifact": False,
                "broker_execution_requested": False,
                "mode_apply_requested": False,
                "command_ledger_append_requested": False,
                "approval_append_requested": False,
                "authorization_grant_requested": False,
                "autotrade_trigger_enabled": False,
            }
    return _Packet()


def _check_panel_boundary(packet: dict, failures: list[str]) -> None:
    checks = {
        "read_only": packet.get("read_only") is True,
        "non_executing": packet.get("non_executing") is True,
        "display_only": packet.get("display_only") is True,
        "render_intent_only": packet.get("render_intent_only") is True,
        "warroom_page_mutation_allowed_false": packet.get("warroom_page_mutation_allowed") is False,
        "warroom_panel_mutation_allowed_false": packet.get("warroom_panel_mutation_allowed") is False,
        "runtime_artifact_write_allowed_false": packet.get("runtime_artifact_write_allowed") is False,
        "approval_or_authorization_allowed_false": packet.get("approval_or_authorization_allowed") is False,
        "ledger_append_allowed_false": packet.get("ledger_append_allowed") is False,
        "autotrade_trigger_allowed_false": packet.get("autotrade_trigger_allowed") is False,
        "broker_private_api_allowed_false": packet.get("broker_private_api_allowed") is False,
        "would_write_runtime_artifact_false": packet.get("would_write_runtime_artifact") is False,
        "would_write_collector_state_false": packet.get("would_write_collector_state") is False,
        "would_send_to_broker_false": packet.get("would_send_to_broker") is False,
        "broker_execution_requested_false": packet.get("broker_execution_requested") is False,
        "mode_apply_requested_false": packet.get("mode_apply_requested") is False,
        "command_ledger_append_requested_false": packet.get("command_ledger_append_requested") is False,
        "approval_append_requested_false": packet.get("approval_append_requested") is False,
        "authorization_grant_requested_false": packet.get("authorization_grant_requested") is False,
        "autotrade_trigger_enabled_false": packet.get("autotrade_trigger_enabled") is False,
    }
    failures.extend(f"panel boundary failed: {name}" for name, ok in checks.items() if not ok)


def main() -> int:
    failures: list[str] = []
    for path in (PANEL, TEST, WARROOM):
        if not path.exists():
            failures.append(f"missing file: {path.relative_to(REPO_ROOT)}")
            continue
        text = _read(path)
        try:
            ast.parse(text, filename=str(path))
        except SyntaxError as exc:
            failures.append(f"syntax failed: {path.relative_to(REPO_ROOT)}: {exc}")
        for token in FORBIDDEN_TRUE_TOKENS:
            if token in text:
                failures.append(f"forbidden true token in {path.relative_to(REPO_ROOT)}: {token}")

    panel_text = _read(PANEL)
    warroom_text = _read(WARROOM)
    required_panel_markers = (
        "PREDICTION_WARROOM_LATEST_PREDICTION_SOURCE_REVIEW_PANEL_VERSION",
        "prediction_warroom_latest_prediction_source_review_panel.ps_q12b.v1",
        "latest_prediction_source_status_rows",
        "latest_prediction_source_boundary_rows",
        "build_prediction_warroom_latest_prediction_source_review_panel_packet",
        "render_prediction_warroom_latest_prediction_source_review_panel",
        "allow_actual_read=True",
        "store_in_session_state=True",
        "top_default_expanded_review_panel_connected",
        "q9g_session_state_seed_ready",
        "no runtime write",
        "no approval",
        "no ledger",
        "no AutoTrade",
        "no broker/private API",
    )
    for marker in required_panel_markers:
        if marker not in panel_text:
            failures.append(f"missing panel marker: {marker}")
    required_warroom_markers = (
        "render_prediction_warroom_latest_prediction_source_review_panel",
        "Prediction WarRoom real payload review",
        "expanded=True",
        "PS-Q12B may read/decode D-hot latest prediction JSON through PS-Q12A",
        "but no runtime write, no approval, no ledger, no AutoTrade, no broker.",
        "Render PS-Q12B latest prediction source status, then PS-Q9G review packet visibility.",
    )
    for marker in required_warroom_markers:
        if marker not in warroom_text:
            failures.append(f"missing warroom marker: {marker}")
    function_marker = "def _render_prediction_warroom_lowered_display_packet_visibility_review_section() -> None:"
    function_start = warroom_text.find(function_marker)
    if function_start < 0:
        failures.append("warroom review section function not found")
        function_body = ""
    else:
        next_def = warroom_text.find(chr(10) + "def ", function_start + len(function_marker))
        function_body = warroom_text[function_start: next_def if next_def >= 0 else len(warroom_text)]
    source_call = function_body.find("render_prediction_warroom_latest_prediction_source_review_panel()")
    seed_call = function_body.find("apply_prediction_warroom_actual_review_packet_live_session_seed_page_mount")
    q9g_call = function_body.find("render_prediction_warroom_lowered_display_packet_visibility_review_panel()")
    if not (source_call >= 0 and seed_call > source_call and q9g_call > seed_call):
        failures.append("warroom call order must be PS-Q12B source panel -> live session seed -> Q9G panel")

    sample = {
        "adapter_state": "latest_prediction_source_ready",
        "source_summary": {
            "prediction_run_id": "run-ps-q12b",
            "generated_at": "2026-06-22T11:00:00Z",
            "market_uid": "bitflyer.spot.BTC_JPY",
            "signal_strength_percent": 66,
            "signal_strength_band": "medium",
        },
        "review_packet_ready": True,
        "session_state_updated": True,
        "q9b_loader_called_by_this_adapter": True,
        "actual_file_read_attempted": True,
        "payload_decode_attempted": True,
    }
    status_rows = latest_prediction_source_status_rows(sample)
    boundary_rows = latest_prediction_source_boundary_rows(sample)
    if [row.get("name") for row in status_rows] != [
        "adapter_state",
        "prediction_run_id",
        "generated_at",
        "market_uid",
        "signal_strength",
        "review_packet_ready",
        "session_state_updated",
    ]:
        failures.append("status row order mismatch")
    if not all(row.get("read_only") is True and row.get("execution") == "false" for row in status_rows):
        failures.append("status rows must be read-only/non-executing")
    boundary = {row.get("boundary"): row.get("enabled") for row in boundary_rows}
    for key in ("warroom_page_mutation", "runtime_artifact_write", "approval_or_authorization", "decision_or_command_ledger_append", "autotrade_trigger", "broker_private_api"):
        if boundary.get(key) is not False:
            failures.append(f"boundary must remain false: {key}")

    original = panel_mod.build_prediction_warroom_latest_prediction_source_adapter
    try:
        panel_mod.build_prediction_warroom_latest_prediction_source_adapter = _stub_adapter_packet
        session_state: dict = {}
        ready_panel = build_prediction_warroom_latest_prediction_source_review_panel_packet(
            session_state=session_state,
            allow_actual_read=True,
            store_in_session_state=True,
        )
        blocked_panel = build_prediction_warroom_latest_prediction_source_review_panel_packet(
            session_state={},
            allow_actual_read=False,
            store_in_session_state=False,
        )
    finally:
        panel_mod.build_prediction_warroom_latest_prediction_source_adapter = original

    if ready_panel.get("panel_version") != PREDICTION_WARROOM_LATEST_PREDICTION_SOURCE_REVIEW_PANEL_VERSION:
        failures.append("ready panel version mismatch")
    if ready_panel.get("panel_state") != "latest_prediction_source_review_panel_ready":
        failures.append(f"ready panel state mismatch: {ready_panel.get('panel_state')}")
    if ready_panel.get("q9g_session_state_seed_ready") is not True:
        failures.append("ready panel must seed Q9G session state")
    if "warroom_prediction_lowered_display_packet_visibility_review_packet" not in session_state:
        failures.append("stubbed session_state handoff key missing")
    _check_panel_boundary(ready_panel, failures)
    if blocked_panel.get("panel_state") != "latest_prediction_source_review_panel_blocked":
        failures.append("blocked panel must remain blocked")
    if blocked_panel.get("q9g_session_state_seed_ready") is not False:
        failures.append("blocked panel must not be Q9G seed ready")
    _check_panel_boundary(blocked_panel, failures)

    dirty = _dirty_paths()
    unexpected_dirty = dirty - EXPECTED_DIRTY
    if unexpected_dirty:
        failures.append(f"unexpected dirty paths: {sorted(unexpected_dirty)}")

    payload = {
        "ok": not failures,
        "guard": "ps_q12b_warroom_inference_panel",
        "phase": "phase3_prediction_system_warroom_read_only_inference_display",
        "contract": {
            "top_default_expanded_review_panel_connected": not failures,
            "ps_q12a_adapter_invoked_by_panel": not failures,
            "q9g_session_state_seed_supported": not failures,
            "warroom_call_order_source_then_q9g": not failures,
            "no_runtime_write_or_execution_surface": not failures,
            "expected_dirty_only": not unexpected_dirty,
        },
        "dirty_paths": sorted(dirty),
        "unexpected_dirty": sorted(unexpected_dirty),
        "failures": failures,
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if not failures else 1


def test_ps_q12b_warroom_inference_panel_guard() -> None:
    assert main() == 0


if __name__ == "__main__":
    raise SystemExit(main())
