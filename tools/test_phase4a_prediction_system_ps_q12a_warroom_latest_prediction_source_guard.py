# path: ./tools/test_phase4a_prediction_system_ps_q12a_warroom_latest_prediction_source_guard.py
# desc: Close guard for PS-Q12A WarRoom latest prediction source adapter. Allows read-only latest prediction JSON ingestion only behind explicit allow_actual_read; forbids UI/runtime/execution surfaces.

from __future__ import annotations

import ast
import json
import subprocess
import tempfile
from pathlib import Path

from _btcts_bootstrap import ensure_btcts_on_syspath

ensure_btcts_on_syspath()

from btcts.apps.operator_ui.components.prediction_warroom_actual_review_packet_session_state_handoff_harness import (  # noqa: E402
    DEFAULT_ACTUAL_REVIEW_PACKET_SESSION_KEY,
)
from btcts.apps.operator_ui.components.prediction_warroom_actual_read_review_composition_harness import (  # noqa: E402
    ACTUAL_READ_REVIEW_COMPOSITION_HARNESS_VERSION,
)
from btcts.apps.operator_ui.components.prediction_warroom_latest_prediction_source_adapter import (  # noqa: E402
    LATEST_PREDICTION_SOURCE_ADAPTER_VERSION,
    LATEST_PREDICTION_SOURCE_ADAPTER_SEQUENCE,
    build_prediction_warroom_latest_prediction_source_adapter,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
ADAPTER = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/components/prediction_warroom_latest_prediction_source_adapter.py"
TEST = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/tests/test_prediction_warroom_latest_prediction_source_adapter.py"
EXPECTED_DIRTY = {
    "btcts_next/src/btcts/apps/operator_ui/components/prediction_warroom_latest_prediction_source_adapter.py",
    "btcts_next/src/btcts/apps/operator_ui/tests/test_prediction_warroom_latest_prediction_source_adapter.py",
    "tools/test_phase4a_prediction_system_ps_q12a_warroom_latest_prediction_source_guard.py",
}
FORBIDDEN_TRUE_TOKENS = (
    "ui_controls_added=True",
    "ui_controls_added = True",
    "ui_triggered_loader_execution=True",
    "ui_triggered_loader_execution = True",
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


def _payload() -> dict:
    return {
        "prediction_run_id": "real_ps_q12a_guard_run",
        "generated_at": "2026-06-22T10:00:00Z",
        "market_uid": "bitflyer.spot.BTC_JPY",
        "headline_ja": "PS-Q12A close guard latest prediction source",
        "primary_signal_summary": {
            "estimated_signal_strength_percent": 72,
            "estimated_reference_hit_rate_percent": 68,
            "signal_strength_band": "high",
            "signal_strength_band_label_ja": "高",
            "signal_strength_cap_reasons": [],
            "prediction_unavailable_reasons": [],
        },
        "horizon_cards": [
            {
                "horizon_group": "short",
                "display_label_ja": "短期",
                "estimated_signal_strength_percent": 72,
                "signal_strength_band": "high",
                "scenario_lite": {
                    "scenario_balance_state": "continuation",
                    "turning_point_risk": "medium",
                },
            }
        ],
        "family_cards": [
            {
                "family": "scenario_core_closeout_candidate",
                "horizon_sec": 300,
                "primary_label": "monitor_watch_path",
                "estimated_signal_strength_percent": 72,
                "source_quality_gate_state": "trusted",
                "source_contribution_ledger": [],
            }
        ],
        "source_quality_panel": {
            "tier0_source_quality_gate": {"gate_state": "trusted"},
            "source_artifact_input_coverage_state": "available",
        },
        "warning_panel": {
            "blockers": [],
            "warnings": [],
        },
        "read_only": True,
        "non_executing": True,
        "would_send_to_broker": False,
        "would_append_ledger": False,
        "would_write_runtime_artifact": False,
    }


def _write_latest(root: Path) -> None:
    prediction_dir = root / "prediction"
    prediction_dir.mkdir(parents=True, exist_ok=True)
    (prediction_dir / "latest_prediction_system_result.json").write_text(
        json.dumps(_payload(), ensure_ascii=False),
        encoding="utf-8",
    )


def _check_boundary(packet, label: str, failures: list[str]) -> None:
    checks = {
        f"{label}_read_only": packet.read_only is True,
        f"{label}_non_executing": packet.non_executing is True,
        f"{label}_source_adapter_only": packet.source_adapter_only is True,
        f"{label}_in_memory_result_only": packet.in_memory_result_only is True,
        f"{label}_display_only": packet.display_only is True,
        f"{label}_render_intent_only": packet.render_intent_only is True,
        f"{label}_streamlit_import_required_false": packet.streamlit_import_required is False,
        f"{label}_ui_controls_added_false": packet.ui_controls_added is False,
        f"{label}_ui_triggered_loader_execution_false": packet.ui_triggered_loader_execution is False,
        f"{label}_warroom_page_mutation_allowed_false": packet.warroom_page_mutation_allowed is False,
        f"{label}_warroom_panel_mutation_allowed_false": packet.warroom_panel_mutation_allowed is False,
        f"{label}_runtime_artifact_write_allowed_false": packet.runtime_artifact_write_allowed is False,
        f"{label}_approval_allowed_false": packet.approval_or_authorization_allowed is False,
        f"{label}_ledger_append_allowed_false": packet.ledger_append_allowed is False,
        f"{label}_autotrade_trigger_allowed_false": packet.autotrade_trigger_allowed is False,
        f"{label}_broker_private_api_allowed_false": packet.broker_private_api_allowed is False,
        f"{label}_would_write_runtime_artifact_false": packet.would_write_runtime_artifact is False,
        f"{label}_would_write_collector_state_false": packet.would_write_collector_state is False,
        f"{label}_would_send_to_broker_false": packet.would_send_to_broker is False,
        f"{label}_broker_execution_requested_false": packet.broker_execution_requested is False,
        f"{label}_mode_apply_requested_false": packet.mode_apply_requested is False,
        f"{label}_command_ledger_append_requested_false": packet.command_ledger_append_requested is False,
        f"{label}_approval_append_requested_false": packet.approval_append_requested is False,
        f"{label}_authorization_grant_requested_false": packet.authorization_grant_requested is False,
        f"{label}_autotrade_trigger_enabled_false": packet.autotrade_trigger_enabled is False,
    }
    failures.extend(f"check failed: {name}" for name, ok in checks.items() if not ok)


def main() -> int:
    failures: list[str] = []
    for path in (ADAPTER, TEST):
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

    adapter_text = _read(ADAPTER)
    required_markers = (
        "LATEST_PREDICTION_SOURCE_ADAPTER_VERSION",
        "prediction_warroom_latest_prediction_source_adapter.ps_q12a.v1",
        "require_explicit_allow_actual_read_before_q9b_loader_call",
        "call_q9b_read_only_loader_only_when_enabled",
        "build_prediction_warroom_latest_prediction_source_adapter",
        "load_prediction_warroom_latest_payload_read_only",
        "build_prediction_warroom_actual_read_review_composition_harness",
        "build_prediction_warroom_actual_review_packet_session_state_handoff_harness",
        "latest_prediction_source_ready",
        "latest_prediction_source_blocked",
        "ready_for_warroom_review_panel",
        "ready_for_warroom_top_display",
        "runtime_artifact_write_allowed",
        "ledger_append_allowed",
        "autotrade_trigger_allowed",
        "broker_private_api_allowed",
        "would_send_to_broker",
        "would_write_runtime_artifact",
    )
    for marker in required_markers:
        if marker not in adapter_text:
            failures.append(f"missing adapter marker: {marker}")

    if "import streamlit" in adapter_text:
        failures.append("adapter must not import streamlit")

    blocked = build_prediction_warroom_latest_prediction_source_adapter()
    if blocked.adapter_version != LATEST_PREDICTION_SOURCE_ADAPTER_VERSION:
        failures.append("blocked adapter version mismatch")
    if blocked.adapter_state != "latest_prediction_source_blocked":
        failures.append("allow_actual_read false must block")
    if blocked.q9b_loader_called_by_this_adapter is not False:
        failures.append("q9b must not be called when allow_actual_read false")
    if "allow_actual_read_false" not in blocked.blocked_reasons:
        failures.append("blocked packet missing allow_actual_read_false reason")
    _check_boundary(blocked, "blocked", failures)

    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        _write_latest(root)
        session_state: dict = {}
        ready = build_prediction_warroom_latest_prediction_source_adapter(
            hot_latest_root_hint=str(root),
            allow_actual_read=True,
            session_state=session_state,
            store_in_session_state=True,
        )

    if ready.adapter_state != "latest_prediction_source_ready":
        failures.append(f"ready adapter state mismatch: {ready.adapter_state}")
    if ready.q9b_loader_called_by_this_adapter is not True:
        failures.append("q9b must be called when allow_actual_read true")
    if ready.q9o_composition_harness_called is not True:
        failures.append("q9o composition harness must be called")
    if ready.q10k_session_state_handoff_called is not True:
        failures.append("q10k session handoff must be called when store requested")
    if ready.actual_file_read_attempted is not True or ready.actual_file_read_succeeded is not True:
        failures.append("actual read should succeed in temp hot root smoke")
    if ready.payload_decode_attempted is not True or ready.payload_decode_succeeded is not True:
        failures.append("payload decode should succeed in temp hot root smoke")
    if ready.loaded_payload_count != 1:
        failures.append("loaded payload count should be 1")
    if ready.review_packet_ready is not True:
        failures.append("review packet should be ready")
    if ready.ready_for_warroom_review_panel is not True:
        failures.append("ready_for_warroom_review_panel should be true")
    if ready.ready_for_warroom_top_display is not False:
        failures.append("ready_for_warroom_top_display must remain false in PS-Q12A")
    if ready.session_state_updated is not True:
        failures.append("session_state should be updated when store requested")
    if DEFAULT_ACTUAL_REVIEW_PACKET_SESSION_KEY not in session_state:
        failures.append("default actual review packet session key not set")
    if ready.source_summary.get("prediction_run_id") != "real_ps_q12a_guard_run":
        failures.append("source summary prediction_run_id mismatch")
    if ready.source_summary.get("signal_strength_percent") != 72:
        failures.append("source summary signal strength mismatch")
    if ready.blocker_count != 0:
        failures.append(f"ready blocker count should be 0: {ready.blocked_reasons}")
    _check_boundary(ready, "ready", failures)

    if ACTUAL_READ_REVIEW_COMPOSITION_HARNESS_VERSION not in str(ready.composition_harness):
        failures.append("composition harness version missing from ready packet")
    if LATEST_PREDICTION_SOURCE_ADAPTER_SEQUENCE[0] != "require_explicit_allow_actual_read_before_q9b_loader_call":
        failures.append("adapter sequence first boundary mismatch")

    dirty = _dirty_paths()
    unexpected_dirty = dirty - EXPECTED_DIRTY
    if unexpected_dirty:
        failures.append(f"unexpected dirty paths: {sorted(unexpected_dirty)}")

    payload = {
        "ok": not failures,
        "guard": "ps_q12a_warroom_latest_prediction_source",
        "phase": "phase3_prediction_system_warroom_read_only_inference_display",
        "contract": {
            "explicit_allow_actual_read_required": not failures,
            "read_only_latest_prediction_source_only": not failures,
            "review_packet_handoff_ready": not failures,
            "warroom_top_display_not_enabled_yet": not failures,
            "no_streamlit_import": "import streamlit" not in adapter_text,
            "no_runtime_write_or_execution_surface": not failures,
            "expected_dirty_only": not unexpected_dirty,
        },
        "dirty_paths": sorted(dirty),
        "unexpected_dirty": sorted(unexpected_dirty),
        "failures": failures,
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if not failures else 1


def test_ps_q12a_warroom_latest_prediction_source_guard() -> None:
    assert main() == 0


if __name__ == "__main__":
    raise SystemExit(main())
