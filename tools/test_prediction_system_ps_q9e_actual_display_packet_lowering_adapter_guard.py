# path: ./tools/test_prediction_system_ps_q9e_actual_display_packet_lowering_adapter_guard.py
# desc: Focused guard for PS-Q9E in-memory actual display-packet lowering adapter.

from __future__ import annotations

import ast
from pathlib import Path

from _btcts_bootstrap import ensure_btcts_on_syspath
ensure_btcts_on_syspath()

from btcts.apps.operator_ui.components.prediction_warroom_actual_display_packet_lowering_adapter import (
    ACTUAL_DISPLAY_PACKET_LOWERING_ADAPTER_VERSION,
    LOWERING_ADAPTER_SEQUENCE,
    build_prediction_warroom_actual_display_packet_lowering_result,
)
from btcts.apps.operator_ui.components.prediction_warroom_payload_schema_validator import DISPLAY_PACKET_VERSION
from btcts.apps.operator_ui.components.prediction_warroom_sample_packets import build_prediction_warroom_sample_display_packet

REPO_ROOT = Path(__file__).resolve().parents[1]
MODULE = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/components/prediction_warroom_actual_display_packet_lowering_adapter.py"
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
    "warroom_card_rendering_enabled: bool = True",
    "warroom_page_mutation_enabled: bool = True",
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
    "consume_prediction_system_result_snapshot_mapping_as_in_memory_data_only",
    "run_ps_q9d_lowering_contract_readiness",
    "build_q4a_compatible_display_packet_mapping_in_memory",
    "validate_display_packet_mapping_with_q5c",
    "return_lowering_result_packet_only",
    "do_not_mount_or_render_warroom_cards",
    "ps_q9f_ui_mount_requires_separate_guard",
    "fail_closed_keep_runtime_disconnected",
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
        "headline_ja": "短期は上方向優勢。",
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
        "warroom_card_rendering_enabled",
        "warroom_page_mutation_enabled",
        "would_load_hot_latest_artifacts",
        "would_read_runtime_file",
        "would_decode_payload",
        "would_write_runtime_artifact",
        "would_write_collector_state",
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


def test_ps_q9e_static_boundaries_and_markers() -> None:
    text = MODULE.read_text(encoding="utf-8")
    imports = _imports_from(MODULE)
    for prefix in FORBIDDEN_IMPORT_PREFIXES:
        assert not any(item == prefix or item.startswith(prefix + ".") for item in imports), prefix
    for token in FORBIDDEN_TOKENS:
        assert token not in text, token
    assert "prediction_warroom_actual_display_packet_lowering_adapter.ps_q9e.v1" in text
    assert "build_prediction_warroom_actual_display_packet_lowering_result" in text
    assert "validate_prediction_warroom_display_packet_schema" in text
    assert "ps_q9f_ui_mount_requires_separate_guard" in text
    assert list(LOWERING_ADAPTER_SEQUENCE) == EXPECTED_SEQUENCE


def test_ps_q9e_blocks_before_generation_when_q9d_not_ready() -> None:
    packet = build_prediction_warroom_actual_display_packet_lowering_result().to_dict()
    assert packet["adapter_version"] == ACTUAL_DISPLAY_PACKET_LOWERING_ADAPTER_VERSION
    assert packet["adapter_state"] == "blocked_by_ps_q9d_lowering_contract"
    assert packet["display_packet_generated"] is False
    assert packet["display_packet_validated"] is False
    assert "prediction_result_payload_not_supplied" in packet["blocked_reasons"]
    _assert_no_side_effect_flags(packet)


def test_ps_q9e_lowers_valid_payload_and_q5c_validates_display_packet() -> None:
    packet = build_prediction_warroom_actual_display_packet_lowering_result(prediction_result_payload=_payload()).to_dict()
    assert packet["adapter_state"] == "display_packet_lowered_and_validated_in_memory"
    assert packet["display_packet_generated"] is True
    assert packet["display_packet_validated"] is True
    assert packet["display_packet_valid"] is True
    assert packet["blocker_count"] == 0
    display_packet = packet["display_packet"]
    assert display_packet["packet_version"] == DISPLAY_PACKET_VERSION
    assert display_packet["prediction_run_id"] == "run-1"
    assert display_packet["primary_signal_summary"]["estimated_signal_strength_percent"] == 42
    assert display_packet["horizon_cards"][0]["horizon_group"] == "short_horizon"
    assert display_packet["family_cards"][0]["family"] == "trend_bias"
    assert display_packet["ui_contract"]["trigger_buttons_allowed"] is False
    assert display_packet["boundaries"]["autotrade_trigger_enabled"] is False
    assert packet["validation_report"]["valid"] is True
    assert packet["validation_report"]["schema_target"] == "display_packet"
    _assert_no_side_effect_flags(packet)


def test_ps_q9e_sample_display_packet_can_roundtrip_as_source_payload() -> None:
    source = build_prediction_warroom_sample_display_packet()
    packet = build_prediction_warroom_actual_display_packet_lowering_result(prediction_result_payload=source).to_dict()
    assert packet["adapter_state"] == "display_packet_lowered_and_validated_in_memory"
    assert packet["display_packet_valid"] is True
    assert packet["display_packet"]["prediction_run_id"] == source["prediction_run_id"]
    assert packet["display_packet"]["primary_signal_summary"]["estimated_signal_strength_percent"] == 59
    assert packet["display_packet"]["horizon_cards"]
    assert packet["display_packet"]["family_cards"]
    _assert_no_side_effect_flags(packet)


def test_ps_q9e_nested_q9d_aliases_are_used_by_actual_lowering() -> None:
    payload = {
        "metadata": {"prediction_run_id": "run-nested", "generated_at": "2026-06-21T00:00:00Z"},
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
    packet = build_prediction_warroom_actual_display_packet_lowering_result(prediction_result_payload=payload).to_dict()
    assert packet["adapter_state"] == "display_packet_lowered_and_validated_in_memory"
    assert packet["display_packet_valid"] is True
    assert packet["display_packet"]["prediction_run_id"] == "run-nested"
    assert packet["display_packet"]["market_uid"] == "BTC_JPY:bitFlyer"
    assert packet["display_packet"]["primary_signal_summary"]["estimated_signal_strength_percent"] == 12
    _assert_no_side_effect_flags(packet)


def test_ps_q9e_lowers_actual_prediction_system_result_shape_in_memory() -> None:
    packet = build_prediction_warroom_actual_display_packet_lowering_result(
        prediction_result_payload=_actual_prediction_system_result_payload(),
        validation_panel={
            "panel_version": "prediction_warroom_loaded_payload_schema_validation_result_panel.ps_q9c.v1",
            "blocker_count": 0,
            "warning_reasons": ["schema_validation_deferred_to_ps_q9c"],
        },
    ).to_dict()
    assert packet["adapter_state"] == "display_packet_lowered_and_validated_in_memory"
    assert packet["display_packet_generated"] is True
    assert packet["display_packet_validated"] is True
    assert packet["display_packet_valid"] is True
    display_packet = packet["display_packet"]
    assert display_packet["prediction_run_id"].startswith("prediction_system.ps_g_lite.v1:")
    assert display_packet["market_uid"] == "BTC_JPY:bitFlyer"
    assert display_packet["horizon_cards"]
    assert display_packet["family_cards"]
    assert display_packet["warning_panel"]["warnings"]
    assert display_packet["boundaries"]["autotrade_trigger_enabled"] is False
    assert display_packet["boundaries"]["would_send_to_broker"] is False
    _assert_no_side_effect_flags(packet)


def test_ps_q9e_bad_payload_blocks_before_generation_via_q9d() -> None:
    payload = _payload()
    payload["primary_signal_summary"] = {"estimated_signal_strength_percent": 100}
    packet = build_prediction_warroom_actual_display_packet_lowering_result(prediction_result_payload=payload).to_dict()
    assert packet["adapter_state"] == "blocked_by_ps_q9d_lowering_contract"
    assert packet["display_packet_generated"] is False
    assert "primary_signal_summary_missing_valid_estimated_signal_strength_percent" in packet["blocked_reasons"]
    _assert_no_side_effect_flags(packet)


def test_ps_q9e_validation_panel_blockers_block_before_generation() -> None:
    panel = {
        "panel_version": "prediction_warroom_loaded_payload_schema_validation_result_panel.ps_q9c.v1",
        "blocker_count": 1,
        "warning_reasons": [],
    }
    packet = build_prediction_warroom_actual_display_packet_lowering_result(
        prediction_result_payload=_payload(),
        validation_panel=panel,
    ).to_dict()
    assert packet["adapter_state"] == "blocked_by_ps_q9d_lowering_contract"
    assert packet["display_packet_generated"] is False
    assert "validation_panel_has_schema_blockers" in packet["blocked_reasons"]
    _assert_no_side_effect_flags(packet)


def test_ps_q9e_handoff_summary_keeps_ui_mount_separate() -> None:
    packet = build_prediction_warroom_actual_display_packet_lowering_result(prediction_result_payload=_payload()).to_dict()
    summary = packet["handoff_summary"]
    assert summary["adapter_boundary"] == "ps_q9e_actual_display_packet_lowering_adapter_in_memory_only"
    assert summary["responsibility"] == "build and validate Q4A-compatible display packet mapping from in-memory PredictionSystemResult-like payload"
    assert summary["display_packet_generated"] is True
    assert summary["display_packet_validated"] is True
    assert summary["warroom_card_rendering_enabled"] is False
    assert summary["warroom_page_mutation_enabled"] is False
    assert summary["runtime_file_read_enabled"] is False
    assert summary["payload_decode_enabled_by_this_adapter"] is False
    assert summary["runtime_artifact_write_enabled"] is False
    assert summary["autotrade_trigger_enabled"] is False
    assert summary["broker_private_api_enabled"] is False
    _assert_no_side_effect_flags(packet)


def main() -> int:
    test_ps_q9e_static_boundaries_and_markers()
    test_ps_q9e_blocks_before_generation_when_q9d_not_ready()
    test_ps_q9e_lowers_valid_payload_and_q5c_validates_display_packet()
    test_ps_q9e_sample_display_packet_can_roundtrip_as_source_payload()
    test_ps_q9e_nested_q9d_aliases_are_used_by_actual_lowering()
    test_ps_q9e_lowers_actual_prediction_system_result_shape_in_memory()
    test_ps_q9e_bad_payload_blocks_before_generation_via_q9d()
    test_ps_q9e_validation_panel_blockers_block_before_generation()
    test_ps_q9e_handoff_summary_keeps_ui_mount_separate()
    print("[OK] Prediction System PS-Q9E actual display-packet lowering adapter guard passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
