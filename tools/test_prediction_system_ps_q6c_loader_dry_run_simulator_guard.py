# path: ./tools/test_prediction_system_ps_q6c_loader_dry_run_simulator_guard.py
# desc: Guard for PS-Q6C latest payload loader dry-run simulator. Metadata-only; no runtime reads, payload decode, rendering, Collector, AutoTrade, or broker behavior.

from __future__ import annotations

import ast
from pathlib import Path

from _btcts_bootstrap import ensure_btcts_on_syspath
ensure_btcts_on_syspath()

from btcts.apps.operator_ui.components.prediction_warroom_latest_payload_loader_dry_run_simulator import (
    build_prediction_warroom_latest_payload_loader_dry_run_simulation,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
MODULE = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/components/prediction_warroom_latest_payload_loader_dry_run_simulator.py"
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
    "would_load_hot_latest_artifacts: bool = True",
    "would_read_runtime_file: bool = True",
    "would_write_runtime_artifact: bool = True",
    "would_send_to_broker: bool = True",
    "broker_execution_requested: bool = True",
    "mode_apply_requested: bool = True",
    "command_ledger_append_requested: bool = True",
)
EXPECTED_ROLES = [
    "prediction_system_result_snapshot",
    "prediction_warroom_display_packet",
    "prediction_warroom_widget_group_index",
    "prediction_source_quality_snapshot",
]


def _imports_from(path: Path) -> set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    imports: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imports.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imports.add(node.module)
    return imports


def test_ps_q6c_static_boundaries_and_markers() -> None:
    text = MODULE.read_text(encoding="utf-8")
    imports = _imports_from(MODULE)
    for prefix in FORBIDDEN_IMPORT_PREFIXES:
        assert not any(item == prefix or item.startswith(prefix + ".") for item in imports), prefix
    for token in FORBIDDEN_TOKENS:
        assert token not in text, token
    assert "prediction_warroom_latest_payload_loader_dry_run_simulator.ps_q6c.v1" in text
    assert "PredictionWarRoomLatestPayloadLoaderDryRunArtifactEvaluation" in text
    assert "PredictionWarRoomLatestPayloadLoaderDryRunSimulationPacket" in text
    assert "build_prediction_warroom_latest_payload_loader_dry_run_simulation" in text
    assert "metadata_only_latest_payload_loader_dry_run" in text


def test_ps_q6c_default_simulation_blocks_without_metadata_and_without_reads() -> None:
    packet = build_prediction_warroom_latest_payload_loader_dry_run_simulation().to_dict()
    assert packet["simulation_version"] == "prediction_warroom_latest_payload_loader_dry_run_simulator.ps_q6c.v1"
    assert packet["simulation_state"] == "simulated_loader_blocked_or_waiting_for_metadata"
    assert packet["loader_permission_contract_version"] == "prediction_warroom_latest_payload_loader_permission_contract.ps_q6b.v1"
    assert packet["preflight_status_contract_version"] == "prediction_warroom_latest_payload_preflight_status.ps_q6a.v1"
    assert [item["artifact_role"] for item in packet["artifact_evaluations"]] == EXPECTED_ROLES
    assert packet["simulated_preflight_ready_for_payload_handoff"] is False
    assert packet["candidate_artifact_count"] == 0
    assert packet["actual_loader_execution_allowed"] is False
    assert packet["actual_file_read_allowed_by_this_contract"] is False
    assert packet["actual_payload_decode_allowed_by_this_contract"] is False
    assert packet["would_load_hot_latest_artifacts"] is False
    assert packet["would_read_runtime_file"] is False
    assert packet["would_write_runtime_artifact"] is False
    assert packet["would_send_to_broker"] is False
    assert "required_artifact_metadata_not_supplied" in packet["blocked_reasons"]
    assert "actual_file_read_not_allowed_by_ps_q6b_contract" in packet["blocked_reasons"]


def test_ps_q6c_fresh_valid_required_metadata_becomes_candidate_but_actual_loader_disabled() -> None:
    packet = build_prediction_warroom_latest_payload_loader_dry_run_simulation(
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
    assert packet["simulation_state"] == "simulated_metadata_handoff_ready_actual_loader_disabled"
    assert packet["simulated_preflight_ready_for_payload_handoff"] is True
    assert packet["candidate_artifact_count"] == 1
    assert packet["actual_loader_execution_allowed"] is False
    required = [item for item in packet["artifact_evaluations"] if item["artifact_role"] == "prediction_system_result_snapshot"][0]
    assert required["candidate_for_future_guarded_loader"] is True
    assert required["path_scope_status"] == "passed"
    assert required["extension_status"] == "passed"
    assert required["file_size_status"] == "passed"
    assert required["freshness_status"] == "fresh"
    assert required["schema_validation_status"] == "valid"
    assert required["actual_file_read_allowed_by_this_contract"] is False
    assert "actual_file_read_not_allowed_by_ps_q6b_contract" in packet["blocked_reasons"]


def test_ps_q6c_bad_path_extension_or_size_blocks_before_read() -> None:
    packet = build_prediction_warroom_latest_payload_loader_dry_run_simulation(
        artifact_metadata_inputs=(
            {
                "artifact_role": "prediction_system_result_snapshot",
                "supplied": True,
                "path_hint": "E:\\btc_ts\\prediction\\latest_prediction_system_result.txt",
                "file_size_bytes": 12_000_000,
                "freshness_status": "fresh",
                "schema_validation_status": "valid",
                "schema_validation_valid": True,
            },
        )
    ).to_dict()
    required = [item for item in packet["artifact_evaluations"] if item["artifact_role"] == "prediction_system_result_snapshot"][0]
    assert required["candidate_for_future_guarded_loader"] is False
    assert required["path_scope_status"] == "outside_hot_latest_root"
    assert required["extension_status"] == "not_json"
    assert required["file_size_status"] == "too_large"
    assert "path_scope_not_under_hot_latest_root" in required["blocker_reasons"]
    assert "extension_not_allowed" in required["blocker_reasons"]
    assert "file_size_exceeds_max_before_parse" in required["blocker_reasons"]
    assert packet["actual_file_read_allowed_by_this_contract"] is False


def test_ps_q6c_stale_or_schema_invalid_blocks_metadata_handoff() -> None:
    packet = build_prediction_warroom_latest_payload_loader_dry_run_simulation(
        artifact_metadata_inputs=(
            {
                "artifact_role": "prediction_system_result_snapshot",
                "supplied": True,
                "path_hint": "D:\\btc_ts_hot\\prediction\\latest_prediction_system_result.json",
                "file_size_bytes": 1200,
                "freshness_status": "stale",
                "schema_validation_status": "invalid",
                "schema_validation_valid": False,
            },
        )
    ).to_dict()
    required = [item for item in packet["artifact_evaluations"] if item["artifact_role"] == "prediction_system_result_snapshot"][0]
    assert required["candidate_for_future_guarded_loader"] is False
    assert "freshness_status_stale" in required["blocker_reasons"]
    assert "schema_validation_blocked" in required["blocker_reasons"]
    assert packet["simulated_preflight_ready_for_payload_handoff"] is False
    assert packet["actual_loader_execution_allowed"] is False


def main() -> int:
    test_ps_q6c_static_boundaries_and_markers()
    test_ps_q6c_default_simulation_blocks_without_metadata_and_without_reads()
    test_ps_q6c_fresh_valid_required_metadata_becomes_candidate_but_actual_loader_disabled()
    test_ps_q6c_bad_path_extension_or_size_blocks_before_read()
    test_ps_q6c_stale_or_schema_invalid_blocks_metadata_handoff()
    print("[OK] Prediction System PS-Q6C loader dry-run simulator guard passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
