# path: ./tools/test_prediction_system_ps_q9f_lowered_display_packet_visibility_review_contract_guard.py
# desc: Focused guard for PS-Q9F lowered display-packet visibility review contract.

from __future__ import annotations

import ast
from pathlib import Path

from _btcts_bootstrap import ensure_btcts_on_syspath
ensure_btcts_on_syspath()

from btcts.apps.operator_ui.components.prediction_warroom_actual_display_packet_lowering_adapter import build_prediction_warroom_actual_display_packet_lowering_result
from btcts.apps.operator_ui.components.prediction_warroom_lowered_display_packet_visibility_review_contract import (
    LOWERED_DISPLAY_PACKET_VISIBILITY_REVIEW_CONTRACT_VERSION,
    VISIBILITY_REVIEW_SEQUENCE,
    VISIBLE_WIDGET_GROUP_ORDER,
    build_prediction_warroom_lowered_display_packet_visibility_review_contract,
)
from btcts.apps.operator_ui.components.prediction_warroom_sample_packets import build_prediction_warroom_sample_display_packet

REPO_ROOT = Path(__file__).resolve().parents[1]
MODULE = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/components/prediction_warroom_lowered_display_packet_visibility_review_contract.py"
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
    "streamlit_render_enabled: bool = True",
    "warroom_card_rendering_enabled: bool = True",
    "warroom_page_mutation_enabled: bool = True",
    "ui_mount_patch_included: bool = True",
    "loader_execution_allowed_from_ui: bool = True",
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
    "consume_ps_q9e_lowering_result_packet_as_data_only",
    "verify_display_packet_generated_validated_and_valid",
    "build_display_only_widget_group_index_in_memory",
    "declare_warroom_visibility_review_readiness",
    "return_review_contract_packet_only",
    "do_not_render_streamlit_or_mutate_warroom_page",
    "ps_q9g_guarded_ui_mount_requires_separate_patch",
    "fail_closed_keep_runtime_and_execution_disconnected",
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


def _lowering_result() -> dict:
    return build_prediction_warroom_actual_display_packet_lowering_result(prediction_result_payload=_payload()).to_dict()


def _assert_no_side_effect_flags(packet: dict) -> None:
    false_keys = (
        "streamlit_render_enabled",
        "warroom_card_rendering_enabled",
        "warroom_page_mutation_enabled",
        "ui_mount_patch_included",
        "loader_execution_allowed_from_ui",
        "would_load_hot_latest_artifacts",
        "would_read_runtime_file",
        "would_decode_payload",
        "would_collect_public_source",
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
    for item in packet["widget_candidates"]:
        for key in false_keys:
            if key in item:
                assert item[key] is False, f"{item['widget_group_id']}:{key}"


def test_ps_q9f_static_boundaries_and_markers() -> None:
    text = MODULE.read_text(encoding="utf-8")
    imports = _imports_from(MODULE)
    for prefix in FORBIDDEN_IMPORT_PREFIXES:
        assert not any(item == prefix or item.startswith(prefix + ".") for item in imports), prefix
    for token in FORBIDDEN_TOKENS:
        assert token not in text, token
    assert "prediction_warroom_lowered_display_packet_visibility_review_contract.ps_q9f.v1" in text
    assert "PredictionWarRoomLoweredDisplayPacketVisibilityReviewContractPacket" in text
    assert "build_prediction_warroom_lowered_display_packet_visibility_review_contract" in text
    assert "ps_q9g_guarded_ui_mount_requires_separate_patch" in text
    assert list(VISIBILITY_REVIEW_SEQUENCE) == EXPECTED_SEQUENCE


def test_ps_q9f_blocks_without_lowering_result() -> None:
    packet = build_prediction_warroom_lowered_display_packet_visibility_review_contract().to_dict()
    assert packet["contract_version"] == LOWERED_DISPLAY_PACKET_VISIBILITY_REVIEW_CONTRACT_VERSION
    assert packet["contract_state"] == "blocked_visibility_review_contract"
    assert packet["ready_for_ps_q9g_guarded_ui_mount"] is False
    assert packet["widget_group_index_built"] is False
    assert "lowering_result_not_supplied" in packet["blocked_reasons"]
    assert "display_packet_mapping_missing" in packet["blocked_reasons"]
    _assert_no_side_effect_flags(packet)


def test_ps_q9f_blocks_when_q9e_lowering_is_blocked() -> None:
    lowering = build_prediction_warroom_actual_display_packet_lowering_result().to_dict()
    packet = build_prediction_warroom_lowered_display_packet_visibility_review_contract(lowering_result=lowering).to_dict()
    assert packet["contract_state"] == "blocked_visibility_review_contract"
    assert packet["display_packet_generated"] is False
    assert packet["display_packet_valid"] is False
    assert "prediction_result_payload_not_supplied" in packet["blocked_reasons"]
    assert "display_packet_not_generated_by_ps_q9e" in packet["blocked_reasons"]
    _assert_no_side_effect_flags(packet)


def test_ps_q9f_valid_lowering_result_builds_visibility_review_and_widget_index() -> None:
    packet = build_prediction_warroom_lowered_display_packet_visibility_review_contract(lowering_result=_lowering_result()).to_dict()
    assert packet["contract_state"] == "visibility_review_ready_for_ps_q9g_guarded_ui_mount_with_warnings"
    assert packet["ready_for_ps_q9g_guarded_ui_mount"] is True
    assert packet["display_packet_present"] is True
    assert packet["display_packet_generated"] is True
    assert packet["display_packet_validated"] is True
    assert packet["display_packet_valid"] is True
    assert packet["widget_group_index_built"] is True
    assert packet["widget_group_count"] == 6
    assert packet["visible_widget_group_count"] == 6
    assert tuple(packet["widget_group_order"]) == VISIBLE_WIDGET_GROUP_ORDER
    assert packet["widget_candidates"][0]["widget_group_id"] == "primary_signal_widget"
    assert packet["widget_group_index"]["index_version"] == "prediction_warroom_widget_groups.ps_q4b.v1"
    assert "validation_panel_not_supplied_ps_q9d_uses_payload_shape_only" in packet["warning_reasons"]
    _assert_no_side_effect_flags(packet)


def test_ps_q9f_sample_lowering_result_is_reviewable() -> None:
    lowering = build_prediction_warroom_actual_display_packet_lowering_result(
        prediction_result_payload=build_prediction_warroom_sample_display_packet()
    ).to_dict()
    packet = build_prediction_warroom_lowered_display_packet_visibility_review_contract(lowering_result=lowering).to_dict()
    assert packet["ready_for_ps_q9g_guarded_ui_mount"] is True
    assert packet["widget_group_count"] == 6
    assert "source_quality_widget" in packet["widget_group_order"]
    assert any(item["widget_group_id"] == "warning_refresh_widget" for item in packet["widget_candidates"])
    _assert_no_side_effect_flags(packet)


def test_ps_q9f_handoff_summary_keeps_ui_patch_separate() -> None:
    packet = build_prediction_warroom_lowered_display_packet_visibility_review_contract(lowering_result=_lowering_result()).to_dict()
    summary = packet["handoff_summary"]
    assert summary["contract_boundary"] == "ps_q9f_lowered_display_packet_visibility_review_contract_only"
    assert summary["responsibility"] == "review lowered display packet visibility and widget-group readiness before PS-Q9G guarded UI mount"
    assert summary["widget_group_index_built"] is True
    assert summary["streamlit_render_enabled"] is False
    assert summary["warroom_card_rendering_enabled"] is False
    assert summary["warroom_page_mutation_enabled"] is False
    assert summary["ui_mount_patch_included"] is False
    assert summary["loader_execution_allowed_from_ui"] is False
    assert summary["runtime_file_read_enabled"] is False
    assert summary["payload_decode_enabled_by_this_contract"] is False
    assert summary["runtime_artifact_write_enabled"] is False
    assert summary["autotrade_trigger_enabled"] is False
    assert summary["broker_private_api_enabled"] is False
    _assert_no_side_effect_flags(packet)


def main() -> int:
    test_ps_q9f_static_boundaries_and_markers()
    test_ps_q9f_blocks_without_lowering_result()
    test_ps_q9f_blocks_when_q9e_lowering_is_blocked()
    test_ps_q9f_valid_lowering_result_builds_visibility_review_and_widget_index()
    test_ps_q9f_sample_lowering_result_is_reviewable()
    test_ps_q9f_handoff_summary_keeps_ui_patch_separate()
    print("[OK] Prediction System PS-Q9F lowered display-packet visibility review contract guard passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
