# path: ./tools/test_prediction_system_ps_q6d_dry_run_status_panel_guard.py
# desc: Guard for PS-Q6D Prediction WarRoom latest-payload dry-run status panel. Display-only; no runtime reads, payload decode, rendering, Collector, AutoTrade, or broker behavior.

from __future__ import annotations

import ast
from pathlib import Path

from _btcts_bootstrap import ensure_btcts_on_syspath
ensure_btcts_on_syspath()

from btcts.apps.operator_ui.components.prediction_warroom_latest_payload_dry_run_status_panel import (
    build_prediction_warroom_latest_payload_dry_run_status_panel,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
MODULE = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/components/prediction_warroom_latest_payload_dry_run_status_panel.py"
FORBIDDEN_IMPORT_PREFIXES = (
    "btcts.prediction",
    "btcts.collector_vnext",
    "btcts.autotrade.execution",
    "btcts.autotrade.live_shadow",
    "btcts.processing.l4_consumer_models.shared",
    "streamlit",
    "requests",
    "httpx",
    "ccxt",
    "pybitflyer",
    "websocket",
    "json",
    "pathlib",
)
FORBIDDEN_TOKENS = (
    "open(",
    "Path(",
    "read_text",
    "read_bytes",
    "json.load",
    "json.loads",
    ".exists(",
    ".stat(",
    "build_prediction_system_result",
    "assess_source_quality",
    "place_order(",
    "send_order(",
    "create_order(",
    "append_decision_jsonl",
    "append_command_ledger_record",
    "requests.get",
    "requests.post",
    "httpx.get",
    "httpx.post",
    "st.button",
    "st.form",
    "persist=True",
    "actual_file_read_allowed_by_this_contract: bool = True",
    "actual_payload_decode_allowed_by_this_contract: bool = True",
    "actual_loader_execution_allowed: bool = True",
    "would_load_hot_latest_artifacts: bool = True",
    "would_read_runtime_file: bool = True",
    "would_write_runtime_artifact: bool = True",
    "would_send_to_broker: bool = True",
    "broker_execution_requested: bool = True",
    "mode_apply_requested: bool = True",
    "command_ledger_append_requested: bool = True",
)


def _imports_from(path: Path) -> set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    imports: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imports.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imports.add(node.module)
    return imports


def test_ps_q6d_static_boundaries_and_markers() -> None:
    text = MODULE.read_text(encoding="utf-8")
    imports = _imports_from(MODULE)
    for prefix in FORBIDDEN_IMPORT_PREFIXES:
        assert not any(item == prefix or item.startswith(prefix + ".") for item in imports), prefix
    for token in FORBIDDEN_TOKENS:
        assert token not in text, token
    assert "prediction_warroom_latest_payload_dry_run_status_panel.ps_q6d.v1" in text
    assert "PredictionWarRoomLatestPayloadDryRunStatusPanelPacket" in text
    assert "build_prediction_warroom_latest_payload_dry_run_status_panel" in text
    assert "prediction_latest_payload_dry_run_status_widget" in text
    assert "observe_only" in text


def test_ps_q6d_default_panel_is_blocked_display_only_and_safe() -> None:
    panel = build_prediction_warroom_latest_payload_dry_run_status_panel().to_dict()
    assert panel["panel_version"] == "prediction_warroom_latest_payload_dry_run_status_panel.ps_q6d.v1"
    assert panel["panel_state"] == "blocked_or_waiting_actual_loader_disabled"
    assert panel["widget_group_id"] == "prediction_latest_payload_dry_run_status_widget"
    assert panel["summary_metrics"]["candidate_artifact_count"] == 0
    assert panel["summary_metrics"]["actual_loader_execution_allowed"] is False
    assert panel["actual_loader_execution_allowed"] is False
    assert panel["actual_file_read_allowed_by_this_contract"] is False
    assert panel["actual_payload_decode_allowed_by_this_contract"] is False
    assert panel["would_load_hot_latest_artifacts"] is False
    assert panel["would_read_runtime_file"] is False
    assert panel["would_write_runtime_artifact"] is False
    assert panel["would_send_to_broker"] is False
    assert panel["ui_contract"]["trigger_buttons_allowed"] is False
    assert panel["ui_contract"]["file_picker_allowed"] is False
    assert panel["boundaries"]["would_read_runtime_file"] is False
    assert len(panel["artifact_status_cards"]) == 4
    assert len(panel["blocked_reason_cards"]) >= 1


def test_ps_q6d_candidate_metadata_panel_shows_candidate_but_loader_disabled() -> None:
    panel = build_prediction_warroom_latest_payload_dry_run_status_panel(
        artifact_metadata_inputs=(
            {
                "artifact_role": "prediction_system_result_snapshot",
                "supplied": True,
                "path_hint": "D:\\btc_ts_hot\\prediction\\latest_prediction_system_result.json",
                "file_size_bytes": 1200,
                "freshness_status": "fresh",
                "observed_age_sec": 12,
                "schema_validation_status": "valid",
                "schema_validation_valid": True,
            },
        )
    ).to_dict()
    assert panel["panel_state"] == "candidate_visible_actual_loader_disabled"
    assert panel["status_badge"]["badge_kind"] == "candidate_disabled"
    assert panel["summary_metrics"]["candidate_artifact_count"] == 1
    assert panel["summary_metrics"]["simulated_preflight_ready_for_payload_handoff"] is True
    candidate_cards = [item for item in panel["artifact_status_cards"] if item["candidate_for_future_guarded_loader"] is True]
    assert len(candidate_cards) == 1
    assert candidate_cards[0]["severity"] == "candidate"
    assert candidate_cards[0]["operator_action_kind"] == "observe_only"
    assert panel["actual_loader_execution_allowed"] is False
    assert panel["actual_file_read_allowed_by_this_contract"] is False
    assert panel["would_read_runtime_file"] is False
    assert "actual_file_read_not_allowed_by_ps_q6b_contract" in {item["reason_code"] for item in panel["blocked_reason_cards"]}


def test_ps_q6d_bad_metadata_panel_surfaces_blockers_as_cards() -> None:
    panel = build_prediction_warroom_latest_payload_dry_run_status_panel(
        artifact_metadata_inputs=(
            {
                "artifact_role": "prediction_system_result_snapshot",
                "supplied": True,
                "path_hint": "E:\\btc_ts\\prediction\\latest_prediction_system_result.txt",
                "file_size_bytes": 3_000_000,
                "freshness_status": "stale",
                "schema_validation_status": "invalid",
                "schema_validation_valid": False,
            },
        )
    ).to_dict()
    cards = {item["artifact_role"]: item for item in panel["artifact_status_cards"]}
    required = cards["prediction_system_result_snapshot"]
    assert required["severity"] == "blocked"
    assert required["path_scope_status"] == "outside_hot_latest_root"
    assert required["extension_status"] == "not_json"
    assert required["file_size_status"] == "too_large"
    assert required["freshness_status"] == "stale"
    assert required["schema_validation_status"] == "invalid"
    assert required["blocker_count"] >= 5
    reason_codes = {item["reason_code"] for item in panel["blocked_reason_cards"]}
    assert "path_scope_not_under_hot_latest_root" in reason_codes
    assert "schema_validation_blocked" in reason_codes
    assert panel["actual_loader_execution_allowed"] is False


def test_ps_q6d_accepts_supplied_simulation_packet_without_enabling_runtime() -> None:
    simulation = {
        "simulation_version": "prediction_warroom_latest_payload_loader_dry_run_simulator.ps_q6c.v1",
        "simulation_id": "synthetic",
        "simulation_state": "simulated_loader_blocked_or_waiting_for_metadata",
        "candidate_artifact_count": 0,
        "evaluation_blocker_count": 1,
        "evaluation_warning_count": 0,
        "simulated_preflight_ready_for_payload_handoff": False,
        "artifact_evaluations": (),
        "blocked_reasons": ("synthetic_block",),
        "warning_reasons": (),
    }
    panel = build_prediction_warroom_latest_payload_dry_run_status_panel(simulation_packet=simulation).to_dict()
    assert panel["source_simulation_version"] == "prediction_warroom_latest_payload_loader_dry_run_simulator.ps_q6c.v1"
    assert panel["source_simulation_state"] == "simulated_loader_blocked_or_waiting_for_metadata"
    assert panel["summary_metrics"]["evaluation_blocker_count"] == 1
    assert panel["blocked_reason_cards"][0]["reason_code"] == "synthetic_block"
    assert panel["actual_loader_execution_allowed"] is False
    assert panel["would_read_runtime_file"] is False


def main() -> int:
    test_ps_q6d_static_boundaries_and_markers()
    test_ps_q6d_default_panel_is_blocked_display_only_and_safe()
    test_ps_q6d_candidate_metadata_panel_shows_candidate_but_loader_disabled()
    test_ps_q6d_bad_metadata_panel_surfaces_blockers_as_cards()
    test_ps_q6d_accepts_supplied_simulation_packet_without_enabling_runtime()
    print("[OK] Prediction System PS-Q6D dry-run status panel guard passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
