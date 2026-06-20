# path: ./tools/test_prediction_system_ps_q6a_latest_payload_preflight_status_guard.py
# desc: Guard for PS-Q6A latest payload preflight status contract. Contract-only; no runtime reads, rendering, Collector, AutoTrade, or broker behavior.

from __future__ import annotations

import ast
from pathlib import Path

from _btcts_bootstrap import ensure_btcts_on_syspath
ensure_btcts_on_syspath()

from btcts.apps.operator_ui.components.prediction_warroom_latest_payload_preflight_status import (
    build_prediction_warroom_latest_payload_preflight_status_contract,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
MODULE = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/components/prediction_warroom_latest_payload_preflight_status.py"
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
    "Path.read_text",
    "json.load",
    "json.loads",
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
    "future_loader_allowed_by_this_contract: bool = True",
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


def test_ps_q6a_static_boundaries_and_markers() -> None:
    text = MODULE.read_text(encoding="utf-8")
    imports = _imports_from(MODULE)
    for prefix in FORBIDDEN_IMPORT_PREFIXES:
        assert not any(item == prefix or item.startswith(prefix + ".") for item in imports), prefix
    for token in FORBIDDEN_TOKENS:
        assert token not in text, token
    assert "prediction_warroom_latest_payload_preflight_status.ps_q6a.v1" in text
    assert "PredictionWarRoomLatestPayloadPreflightArtifactStatus" in text
    assert "PredictionWarRoomLatestPayloadPreflightStatusPacket" in text
    assert "build_prediction_warroom_latest_payload_preflight_status_contract" in text
    assert "future_loader_must_validate_schema_before_display" in text
    assert "future_loader_must_check_freshness_before_display" in text


def test_ps_q6a_default_contract_waits_for_future_loader_without_reads() -> None:
    packet = build_prediction_warroom_latest_payload_preflight_status_contract().to_dict()
    assert packet["preflight_status_version"] == "prediction_warroom_latest_payload_preflight_status.ps_q6a.v1"
    assert packet["preflight_state"] == "blocked_waiting_for_latest_loader"
    assert packet["hot_latest_root_hint"] == "D:\\btc_ts_hot"
    assert packet["l4_latest_adapter_contract_version"] == "prediction_warroom_l4_latest_adapter.ps_q4c.v1"
    assert packet["schema_validator_contract_version"] == "prediction_warroom_payload_schema_validator.ps_q5c.v1"
    assert [item["artifact_role"] for item in packet["artifact_statuses"]] == EXPECTED_ROLES
    assert packet["required_artifact_blocker_count"] == 1
    assert packet["preflight_ready_for_payload_handoff"] is False
    assert "required_latest_artifact_not_supplied" in packet["blocked_reasons"]
    assert packet["future_loader_required"] is True
    assert packet["future_loader_allowed_by_this_contract"] is False
    assert packet["would_load_hot_latest_artifacts"] is False
    assert packet["would_read_runtime_file"] is False
    assert packet["would_write_runtime_artifact"] is False
    assert packet["would_send_to_broker"] is False


def test_ps_q6a_artifact_statuses_keep_expected_paths_and_safe_flags() -> None:
    packet = build_prediction_warroom_latest_payload_preflight_status_contract().to_dict()
    statuses = packet["artifact_statuses"]
    assert all(item["expected_path_hint"].startswith("D:\\btc_ts_hot\\prediction\\") for item in statuses)
    required = [item for item in statuses if item["required"]]
    optional = [item for item in statuses if not item["required"]]
    assert len(required) == 1
    assert len(optional) == 3
    assert required[0]["artifact_role"] == "prediction_system_result_snapshot"
    assert "required_artifact_not_supplied_by_preflight_input" in required[0]["blocker_reasons"]
    assert all("optional_artifact_not_supplied_by_preflight_input" in item["warning_reasons"] for item in optional)
    for item in statuses:
        assert item["read_by_this_slice"] is False
        assert item["loaded_in_this_slice"] is False
        assert item["would_load_hot_latest_artifacts"] is False
        assert item["would_read_runtime_file"] is False
        assert item["would_write_runtime_artifact"] is False
        assert item["would_send_to_broker"] is False
        assert item["broker_execution_requested"] is False
        assert item["mode_apply_requested"] is False
        assert item["command_ledger_append_requested"] is False


def test_ps_q6a_supplied_fresh_valid_required_artifact_allows_handoff_with_optional_warnings() -> None:
    packet = build_prediction_warroom_latest_payload_preflight_status_contract(
        artifact_status_inputs=(
            {
                "artifact_role": "prediction_system_result_snapshot",
                "supplied": True,
                "freshness_status": "fresh",
                "observed_age_sec": 12,
                "freshness_max_age_sec": 60,
                "schema_validation_status": "valid",
                "schema_validation_valid": True,
                "schema_validation_report_version": "prediction_warroom_payload_schema_validator.ps_q5c.v1",
                "payload_contract_version": "l4.latest.prediction_system_result.v1",
            },
        )
    ).to_dict()
    assert packet["preflight_state"] == "ready_for_payload_handoff"
    assert packet["preflight_ready_for_payload_handoff"] is True
    assert packet["required_artifact_blocker_count"] == 0
    assert packet["freshness_blocker_count"] == 0
    assert packet["schema_blocker_count"] == 0
    assert packet["optional_artifact_warning_count"] == 3
    required = [item for item in packet["artifact_statuses"] if item["artifact_role"] == "prediction_system_result_snapshot"][0]
    assert required["supplied_by_preflight_input"] is True
    assert required["freshness_status"] == "fresh"
    assert required["schema_validation_status"] == "valid"
    assert required["schema_validation_valid"] is True
    assert required["future_loader_required"] is False


def test_ps_q6a_stale_or_invalid_schema_blocks_handoff() -> None:
    packet = build_prediction_warroom_latest_payload_preflight_status_contract(
        artifact_status_inputs=(
            {
                "artifact_role": "prediction_system_result_snapshot",
                "supplied": True,
                "freshness_status": "stale",
                "schema_validation_status": "invalid",
                "schema_validation_valid": False,
            },
        )
    ).to_dict()
    assert packet["preflight_state"] == "blocked_waiting_for_latest_loader"
    assert packet["preflight_ready_for_payload_handoff"] is False
    assert packet["freshness_blocker_count"] == 1
    assert packet["schema_blocker_count"] == 1
    assert "freshness_not_acceptable" in packet["blocked_reasons"]
    assert "schema_validation_not_acceptable" in packet["blocked_reasons"]


def main() -> int:
    test_ps_q6a_static_boundaries_and_markers()
    test_ps_q6a_default_contract_waits_for_future_loader_without_reads()
    test_ps_q6a_artifact_statuses_keep_expected_paths_and_safe_flags()
    test_ps_q6a_supplied_fresh_valid_required_artifact_allows_handoff_with_optional_warnings()
    test_ps_q6a_stale_or_invalid_schema_blocks_handoff()
    print("[OK] Prediction System PS-Q6A latest payload preflight status guard passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
