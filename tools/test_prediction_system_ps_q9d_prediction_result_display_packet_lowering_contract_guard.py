# path: ./tools/test_prediction_system_ps_q9d_prediction_result_display_packet_lowering_contract_guard.py
# desc: Focused guard for PS-Q9D PredictionSystemResult-to-display-packet lowering contract/readiness.

from __future__ import annotations

import ast
from pathlib import Path

from _btcts_bootstrap import ensure_btcts_on_syspath
ensure_btcts_on_syspath()

from btcts.apps.operator_ui.components.prediction_warroom_prediction_result_display_packet_lowering_contract import (
    DISPLAY_PACKET_REQUIRED_SECTIONS,
    FIELD_MAPPING_RULES,
    LOWERING_SEQUENCE,
    PREDICTION_RESULT_DISPLAY_PACKET_LOWERING_CONTRACT_VERSION,
    build_prediction_warroom_prediction_result_display_packet_lowering_contract,
)
from btcts.apps.operator_ui.components.prediction_warroom_payload_schema_validator import DISPLAY_PACKET_VERSION

REPO_ROOT = Path(__file__).resolve().parents[1]
MODULE = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/components/prediction_warroom_prediction_result_display_packet_lowering_contract.py"
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
    "write_text",
    "write_bytes",
    "json.dump",
    "json.dumps",
    ".exists(",
    ".stat(",
    "build_prediction_system_result",
    "build_prediction_warroom_display_packet(",
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
    "actual_display_packet_generation_enabled: bool = True",
    "display_packet_validation_run_by_this_contract: bool = True",
    "would_load_hot_latest_artifacts: bool = True",
    "would_read_runtime_file: bool = True",
    "would_decode_payload: bool = True",
    "would_write_runtime_artifact: bool = True",
    "would_send_to_broker: bool = True",
    "broker_execution_requested: bool = True",
    "mode_apply_requested: bool = True",
    "command_ledger_append_requested: bool = True",
    "approval_append_requested: bool = True",
    "authorization_grant_requested: bool = True",
    "autotrade_trigger_enabled: bool = True",
)
EXPECTED_SEQUENCE = [
    "consume_ps_q9c_validation_panel_result_as_data_only",
    "consume_prediction_system_result_snapshot_mapping_as_data_only",
    "declare_source_to_display_field_rules",
    "check_required_display_packet_sections_without_generating_packet",
    "check_primary_signal_summary_candidate",
    "check_horizon_and_family_card_candidate_sources",
    "check_source_quality_and_warning_panel_candidates",
    "return_lowering_readiness_contract_only",
    "ps_q9e_actual_lowering_requires_separate_guard",
    "fail_closed_keep_warroom_and_runtime_disconnected",
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


def _payload() -> dict:
    return {
        "prediction_run_id": "run-1",
        "generated_at": "2026-06-21T00:00:00Z",
        "market_uid": "BTC_JPY:bitFlyer",
        "primary_signal_summary": {
            "estimated_signal_strength_percent": 42,
            "estimated_reference_hit_rate_percent": 55,
            "signal_strength_band": "medium",
        },
        "horizon_cards": [
            {"horizon_group": "short_horizon", "estimated_signal_strength_percent": 42, "signal_strength_band": "medium"},
        ],
        "family_cards": [
            {"family": "trend_bias", "horizon_sec": 300, "estimated_signal_strength_percent": 42},
        ],
        "source_quality_panel": {"tier0_source_quality_gate": {"gate_state": "passed"}},
        "warning_panel": {"blockers": [], "warnings": []},
    }


def _actual_prediction_system_result_payload() -> dict:
    return {
        "run_identity": {
            "prediction_run_id": "prediction_system.ps_g_lite.v1:BTC_JPY:bitFlyer:2026-06-21T11:42:43Z",
            "generated_at": "2026-06-21T11:42:43Z",
            "market_uid": "BTC_JPY:bitFlyer",
        },
        "system_input": {
            "market_uid": "BTC_JPY:bitFlyer",
            "source_artifact_coverage_summary": {"coverage_state": "partial", "required_runtime_source_inputs_missing": True},
            "diagnostics": {"logic_version": "prediction_system.ps_g_lite.v1"},
        },
        "scenario_core": {
            "scenario_id": "scenario-1",
            "generated_at": "2026-06-21T11:42:43Z",
            "current_hypothesis_health": "low",
            "outlooks": [
                {"horizon_group": "nowcast", "display_label_ja": "現在", "score": 0.12, "warnings": ["sample_warning"]},
                {"horizon_group": "short_horizon", "display_label_ja": "短期", "score": 0.22},
            ],
            "gpt_review_digest": {"score": 0.12, "confidence": "low"},
            "warnings": ["scenario_warning"],
        },
        "outputs": [
            {"family": "trend_bias", "horizon": {"horizon_sec": 300}, "primary_label": "unknown", "score": 0.12, "warnings": []},
            {"family": "liquidity_execution_quality", "horizon": {"horizon_sec": 60}, "primary_label": "poor", "score": 0.08, "warnings": ["liquidity_poor_liquidity"]},
        ],
        "gpt_review_digest": {"score": 0.12, "confidence": "low"},
        "blockers": [],
        "warnings": ["orderbook_snapshot_missing_exchange_ts_context_only", "prediction_result_warnings_present:16"],
        "read_only": True,
        "non_executing": True,
        "would_send_to_broker": False,
        "broker_execution_requested": False,
    }


def _assert_no_side_effect_flags(packet: dict) -> None:
    false_keys = (
        "actual_display_packet_generation_enabled",
        "display_packet_validation_run_by_this_contract",
        "would_load_hot_latest_artifacts",
        "would_read_runtime_file",
        "would_decode_payload",
        "would_write_runtime_artifact",
        "would_send_to_broker",
        "broker_execution_requested",
        "mode_apply_requested",
        "command_ledger_append_requested",
        "approval_append_requested",
        "authorization_grant_requested",
        "autotrade_trigger_enabled",
    )
    for key in false_keys:
        assert packet[key] is False, key
    for item in packet["field_checks"]:
        for key in false_keys:
            if key in item:
                assert item[key] is False, f"{item['display_field']}:{key}"


def test_ps_q9d_static_boundaries_and_markers() -> None:
    text = MODULE.read_text(encoding="utf-8")
    imports = _imports_from(MODULE)
    for prefix in FORBIDDEN_IMPORT_PREFIXES:
        assert not any(item == prefix or item.startswith(prefix + ".") for item in imports), prefix
    for token in FORBIDDEN_TOKENS:
        assert token not in text, token
    assert "prediction_warroom_prediction_result_display_packet_lowering_contract.ps_q9d.v1" in text
    assert "PredictionWarRoomPredictionResultLoweringFieldCheck" in text
    assert "PredictionWarRoomPredictionResultDisplayPacketLoweringContractPacket" in text
    assert "build_prediction_warroom_prediction_result_display_packet_lowering_contract" in text
    assert "ps_q9e_actual_lowering_requires_separate_guard" in text


def test_ps_q9d_declares_required_display_sections_and_mapping_rules() -> None:
    assert list(LOWERING_SEQUENCE) == EXPECTED_SEQUENCE
    assert DISPLAY_PACKET_REQUIRED_SECTIONS == (
        "packet_version",
        "packet_id",
        "generated_at",
        "market_uid",
        "prediction_run_id",
        "primary_signal_summary",
        "horizon_cards",
        "family_cards",
        "source_quality_panel",
        "warning_panel",
        "ui_contract",
        "boundaries",
    )
    fields = [rule["display_field"] for rule in FIELD_MAPPING_RULES]
    assert fields == [
        "prediction_run_id",
        "generated_at",
        "market_uid",
        "primary_signal_summary",
        "horizon_cards",
        "family_cards",
        "source_quality_panel",
        "warning_panel",
    ]


def test_ps_q9d_blocks_without_payload_and_does_not_generate_display_packet() -> None:
    packet = build_prediction_warroom_prediction_result_display_packet_lowering_contract().to_dict()
    assert packet["contract_version"] == PREDICTION_RESULT_DISPLAY_PACKET_LOWERING_CONTRACT_VERSION
    assert packet["contract_state"] == "blocked_display_packet_lowering_contract"
    assert packet["target_display_packet_version"] == DISPLAY_PACKET_VERSION
    assert packet["ready_for_ps_q9e_actual_display_packet_lowering"] is False
    assert "prediction_result_payload_not_supplied" in packet["blocked_reasons"]
    assert packet["candidate_display_packet_contract"]["actual_display_packet_generation_enabled"] is False
    assert packet["candidate_display_packet_contract"]["warroom_card_rendering_enabled"] is False
    _assert_no_side_effect_flags(packet)


def test_ps_q9d_valid_payload_is_ready_for_ps_q9e_but_still_contract_only() -> None:
    packet = build_prediction_warroom_prediction_result_display_packet_lowering_contract(prediction_result_payload=_payload()).to_dict()
    assert packet["contract_state"] == "ready_for_ps_q9e_actual_display_packet_lowering_contract_handoff"
    assert packet["operator_visible_readiness_state"] == "ready_for_ps_q9e_actual_display_packet_lowering"
    assert packet["ready_for_ps_q9e_actual_display_packet_lowering"] is True
    assert packet["required_field_count"] == 8
    assert packet["ready_field_count"] == 8
    assert packet["blocker_count"] == 0
    assert "validation_panel_not_supplied_ps_q9d_uses_payload_shape_only" in packet["warning_reasons"]
    checks = {item["display_field"]: item for item in packet["field_checks"]}
    assert checks["primary_signal_summary"]["matched_source_path"] == "primary_signal_summary"
    assert checks["horizon_cards"]["source_value_type"] == "list"
    assert checks["family_cards"]["source_value_type"] == "list"
    _assert_no_side_effect_flags(packet)


def test_ps_q9d_nested_source_aliases_can_satisfy_contract() -> None:
    payload = {
        "run_id": "run-nested",
        "created_at": "2026-06-21T00:00:00Z",
        "market": {"market_uid": "BTC_JPY:bitFlyer"},
        "summary": {
            "primary_signal_summary": {
                "estimated_signal_strength_percent": 12,
                "estimated_reference_hit_rate_percent": 10,
                "signal_strength_band": "weak",
            }
        },
        "horizons": [{"horizon_group": "short_horizon", "estimated_signal_strength_percent": 12}],
        "predictions": [{"family": "trend_bias", "horizon_sec": 300, "estimated_signal_strength_percent": 12}],
        "quality": {"tier0_source_quality_gate": {"gate_state": "passed"}},
        "warnings": {"blockers": [], "warnings": []},
    }
    packet = build_prediction_warroom_prediction_result_display_packet_lowering_contract(prediction_result_payload=payload).to_dict()
    assert packet["ready_for_ps_q9e_actual_display_packet_lowering"] is True
    checks = {item["display_field"]: item for item in packet["field_checks"]}
    assert checks["prediction_run_id"]["matched_source_path"] == "run_id"
    assert checks["market_uid"]["matched_source_path"] == "market.market_uid"
    assert checks["primary_signal_summary"]["matched_source_path"] == "summary.primary_signal_summary"
    _assert_no_side_effect_flags(packet)


def test_ps_q9d_bad_signal_or_card_shape_blocks_before_lowering() -> None:
    payload = _payload()
    payload["primary_signal_summary"] = {"estimated_signal_strength_percent": 100}
    payload["horizon_cards"] = {"bad": "not-list"}
    packet = build_prediction_warroom_prediction_result_display_packet_lowering_contract(prediction_result_payload=payload).to_dict()
    assert packet["ready_for_ps_q9e_actual_display_packet_lowering"] is False
    assert "primary_signal_summary_missing_valid_estimated_signal_strength_percent" in packet["blocked_reasons"]
    assert "horizon_cards_must_be_list_before_display_packet_lowering" in packet["blocked_reasons"]
    _assert_no_side_effect_flags(packet)


def test_ps_q9d_actual_prediction_system_result_shape_is_ready_for_q9e() -> None:
    payload = _actual_prediction_system_result_payload()
    panel = {
        "panel_version": "prediction_warroom_loaded_payload_schema_validation_result_panel.ps_q9c.v1",
        "blocker_count": 0,
        "warning_reasons": ["schema_validation_deferred_to_ps_q9c"],
    }
    packet = build_prediction_warroom_prediction_result_display_packet_lowering_contract(
        prediction_result_payload=payload,
        validation_panel=panel,
    ).to_dict()
    assert packet["ready_for_ps_q9e_actual_display_packet_lowering"] is True
    assert packet["blocker_count"] == 0
    checks = {item["display_field"]: item for item in packet["field_checks"]}
    assert checks["prediction_run_id"]["matched_source_path"] == "run_identity.prediction_run_id"
    assert checks["generated_at"]["matched_source_path"] == "run_identity.generated_at"
    assert checks["market_uid"]["matched_source_path"] == "run_identity.market_uid"
    assert checks["primary_signal_summary"]["matched_source_path"] in {"gpt_review_digest", "scenario_core.gpt_review_digest", "scenario_core"}
    assert checks["horizon_cards"]["matched_source_path"] == "scenario_core.outlooks"
    assert checks["family_cards"]["matched_source_path"] == "outputs"
    assert checks["source_quality_panel"]["matched_source_path"].startswith("system_input.")
    assert checks["warning_panel"]["matched_source_path"] == "warnings"
    _assert_no_side_effect_flags(packet)


def test_ps_q9d_validation_panel_blockers_block_lowering() -> None:
    panel = {
        "panel_version": "prediction_warroom_loaded_payload_schema_validation_result_panel.ps_q9c.v1",
        "blocker_count": 1,
        "warning_reasons": [],
    }
    packet = build_prediction_warroom_prediction_result_display_packet_lowering_contract(
        prediction_result_payload=_payload(),
        validation_panel=panel,
    ).to_dict()
    assert packet["ready_for_ps_q9e_actual_display_packet_lowering"] is False
    assert "validation_panel_has_schema_blockers" in packet["blocked_reasons"]
    _assert_no_side_effect_flags(packet)


def test_ps_q9d_handoff_summary_keeps_next_boundary() -> None:
    packet = build_prediction_warroom_prediction_result_display_packet_lowering_contract(prediction_result_payload=_payload()).to_dict()
    summary = packet["handoff_summary"]
    assert summary["contract_boundary"] == "ps_q9d_prediction_result_display_packet_lowering_contract_only"
    assert summary["responsibility"] == "declare and check PredictionSystemResult-like payload fields before PS-Q9E actual display-packet lowering"
    assert summary["actual_display_packet_generation_enabled"] is False
    assert summary["display_packet_validation_run_by_this_contract"] is False
    assert summary["warroom_card_rendering_enabled"] is False
    assert summary["warroom_page_mutation_enabled"] is False
    assert summary["runtime_file_read_enabled"] is False
    assert summary["payload_decode_enabled_by_this_contract"] is False
    assert summary["runtime_artifact_write_enabled"] is False
    assert summary["autotrade_trigger_enabled"] is False
    assert summary["broker_private_api_enabled"] is False
    _assert_no_side_effect_flags(packet)


def main() -> int:
    test_ps_q9d_static_boundaries_and_markers()
    test_ps_q9d_declares_required_display_sections_and_mapping_rules()
    test_ps_q9d_blocks_without_payload_and_does_not_generate_display_packet()
    test_ps_q9d_valid_payload_is_ready_for_ps_q9e_but_still_contract_only()
    test_ps_q9d_nested_source_aliases_can_satisfy_contract()
    test_ps_q9d_bad_signal_or_card_shape_blocks_before_lowering()
    test_ps_q9d_actual_prediction_system_result_shape_is_ready_for_q9e()
    test_ps_q9d_validation_panel_blockers_block_lowering()
    test_ps_q9d_handoff_summary_keeps_next_boundary()
    print("[OK] Prediction System PS-Q9D prediction result display-packet lowering contract guard passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
