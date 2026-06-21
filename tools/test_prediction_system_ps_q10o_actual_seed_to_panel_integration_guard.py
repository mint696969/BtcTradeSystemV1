# path: ./tools/test_prediction_system_ps_q10o_actual_seed_to_panel_integration_guard.py
# desc: Test-only integration guard for PS-Q10O: supplied actual Q9F review packet -> PS-Q10N seed hook -> session_state -> PS-Q9H fallback=False -> existing Q9G panel widgets=6. No production UI mutation and no loader/file/decode/write/approval/ledger/AutoTrade/broker behavior.

from __future__ import annotations

import importlib
from pathlib import Path
import sys
import types
from typing import Any

from _btcts_bootstrap import ensure_btcts_on_syspath
ensure_btcts_on_syspath()

from btcts.apps.operator_ui.components.prediction_warroom_actual_display_packet_lowering_adapter import build_prediction_warroom_actual_display_packet_lowering_result
from btcts.apps.operator_ui.components.prediction_warroom_actual_review_packet_local_observation_seed_hook import (
    ACTUAL_REVIEW_PACKET_LOCAL_OBSERVATION_ALLOWED_MODE,
    ACTUAL_REVIEW_PACKET_LOCAL_OBSERVATION_SEED_HOOK_VERSION,
    build_prediction_warroom_actual_review_packet_local_observation_seed_hook,
)
from btcts.apps.operator_ui.components.prediction_warroom_actual_review_packet_session_state_handoff_harness import DEFAULT_ACTUAL_REVIEW_PACKET_SESSION_KEY
from btcts.apps.operator_ui.components.prediction_warroom_lowered_display_packet_visibility_review_contract import build_prediction_warroom_lowered_display_packet_visibility_review_contract
from btcts.apps.operator_ui.components.prediction_warroom_lowered_display_packet_visibility_review_source_handoff import resolve_prediction_warroom_lowered_display_packet_visibility_review_source
from btcts.apps.operator_ui.components.prediction_warroom_sample_packets import build_prediction_warroom_sample_display_packet

REPO_ROOT = Path(__file__).resolve().parents[1]
WARROOM_PAGE = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/views/warroom_page.py"
PANEL = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/components/prediction_warroom_lowered_display_packet_visibility_review_panel.py"
SEED_HOOK = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/components/prediction_warroom_actual_review_packet_local_observation_seed_hook.py"
FORBIDDEN_PAGE_TOKENS = (
    "prediction_warroom_actual_review_packet_local_observation_seed_hook",
    "build_prediction_warroom_actual_review_packet_local_observation_seed_hook",
    "build_prediction_warroom_actual_read_operator_runner_scaffold",
    "build_prediction_warroom_latest_payload_actual_export_runner",
    "allow_actual_read=True",
    "execute_actual_read=True",
    "warroom_prediction_actual_review_packet_local_observation_enabled",
)
FORBIDDEN_PANEL_TOKENS = (
    "prediction_warroom_actual_review_packet_local_observation_seed_hook",
    "build_prediction_warroom_actual_review_packet_local_observation_seed_hook",
    "build_prediction_warroom_actual_read_operator_runner_scaffold",
    "build_prediction_warroom_latest_payload_actual_export_runner",
    "load_prediction_warroom_latest_payload_read_only",
    "allow_actual_read=True",
    "execute_actual_read=True",
    "open(",
    "read_text",
    "read_bytes",
    "json.load",
    "json.loads",
    "write_text",
    "write_bytes",
    "json.dump",
    "json.dumps",
    "st.button",
    "st.form",
    "st.checkbox",
    "st.toggle",
    "place_order(",
    "send_order(",
    "create_order(",
    "append_decision_jsonl",
    "append_command_ledger_record",
)
FORBIDDEN_SEED_HOOK_TOKENS = (
    "import streamlit",
    "open(",
    "read_text",
    "read_bytes",
    "json.load",
    "json.loads",
    "write_text",
    "write_bytes",
    "json.dump",
    "json.dumps",
    "subprocess",
    "st.button",
    "st.form",
    "st.checkbox",
    "st.toggle",
    "build_prediction_warroom_actual_read_operator_runner_scaffold(",
    "build_prediction_warroom_latest_payload_actual_export_runner(",
    "load_prediction_warroom_latest_payload_read_only(",
    "allow_actual_read=True",
    "execute_actual_read=True",
    "place_order(",
    "send_order(",
    "create_order(",
    "append_decision_jsonl",
    "append_command_ledger_record",
)


class FakeStreamlit(types.ModuleType):
    def __init__(self) -> None:
        super().__init__("streamlit")
        self.session_state: dict[str, Any] = {}
        self.captions: list[str] = []
        self.dataframes: list[Any] = []
        self.infos: list[str] = []
        self.warnings: list[str] = []

    def caption(self, text: Any) -> None:
        self.captions.append(str(text))

    def dataframe(self, data: Any, *args: Any, **kwargs: Any) -> None:
        self.dataframes.append(data)

    def info(self, text: Any) -> None:
        self.infos.append(str(text))

    def warning(self, text: Any) -> None:
        self.warnings.append(str(text))


def _real_like_display_packet() -> dict[str, Any]:
    payload = build_prediction_warroom_sample_display_packet()
    payload["prediction_run_id"] = "actual_seed_to_panel_integration_run_20260621T000000Z"
    payload["packet_id"] = "prediction_warroom_display_packet.ps_q4a.v1:actual_seed_to_panel_integration_run_20260621T000000Z"
    payload["headline_ja"] = "Actual seed-to-panel integration: 短期は上方向優勢、参考度59%。"
    payload["primary_signal_summary"] = dict(payload["primary_signal_summary"])
    payload["primary_signal_summary"].pop("synthetic_only", None)
    payload["primary_signal_summary"].pop("fixture_only", None)
    payload["boundaries"] = dict(payload["boundaries"])
    payload["boundaries"].pop("synthetic_only", None)
    payload["boundaries"].pop("fixture_only", None)
    payload.pop("synthetic_only", None)
    payload.pop("fixture_only", None)
    return payload


def _actual_review_packet() -> dict[str, Any]:
    lowering = build_prediction_warroom_actual_display_packet_lowering_result(
        prediction_result_payload=_real_like_display_packet(),
    ).to_dict()
    review = build_prediction_warroom_lowered_display_packet_visibility_review_contract(
        lowering_result=lowering,
    ).to_dict()
    assert review["ready_for_ps_q9g_guarded_ui_mount"] is True
    assert review["widget_group_count"] == 6
    return review


def _install_fake_streamlit(fake: FakeStreamlit) -> None:
    sys.modules["streamlit"] = fake
    module_name = "btcts.apps.operator_ui.components.prediction_warroom_lowered_display_packet_visibility_review_panel"
    sys.modules.pop(module_name, None)
    importlib.invalidate_caches()


def _panel_module(fake: FakeStreamlit):
    _install_fake_streamlit(fake)
    return importlib.import_module("btcts.apps.operator_ui.components.prediction_warroom_lowered_display_packet_visibility_review_panel")


def _flatten_rows(dataframes: list[Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for frame in dataframes:
        if isinstance(frame, list):
            rows.extend(item for item in frame if isinstance(item, dict))
    return rows


def _captions(fake: FakeStreamlit) -> str:
    return chr(10).join(fake.captions)


def test_ps_q10o_static_not_mounted_and_no_runtime_boundaries() -> None:
    page_text = WARROOM_PAGE.read_text(encoding="utf-8")
    panel_text = PANEL.read_text(encoding="utf-8")
    seed_text = SEED_HOOK.read_text(encoding="utf-8")
    for token in FORBIDDEN_PAGE_TOKENS:
        assert token not in page_text, token
    for token in FORBIDDEN_PANEL_TOKENS:
        assert token not in panel_text, token
    for token in FORBIDDEN_SEED_HOOK_TOKENS:
        assert token not in seed_text, token
    assert "Prediction WarRoom real payload review" in page_text
    assert "render_prediction_warroom_lowered_display_packet_visibility_review_panel()" in page_text
    assert ACTUAL_REVIEW_PACKET_LOCAL_OBSERVATION_SEED_HOOK_VERSION == "prediction_warroom_actual_review_packet_local_observation_seed_hook.ps_q10n.v1"


def test_ps_q10o_seed_hook_supplies_q9h_session_packet_before_panel_render() -> None:
    fake = FakeStreamlit()
    seed_packet = build_prediction_warroom_actual_review_packet_local_observation_seed_hook(
        review_packet=_actual_review_packet(),
        session_state=fake.session_state,
        enable_actual_review_packet_seed=True,
        local_observation_mode=ACTUAL_REVIEW_PACKET_LOCAL_OBSERVATION_ALLOWED_MODE,
    ).to_dict()
    resolved = resolve_prediction_warroom_lowered_display_packet_visibility_review_source(
        session_state=fake.session_state,
    ).to_dict()
    assert seed_packet["hook_state"] == "actual_review_packet_local_observation_seed_hook_actual_packet_installed"
    assert seed_packet["actual_seed_enabled"] is True
    assert seed_packet["actual_review_packet_present"] is True
    assert seed_packet["actual_review_packet_ready"] is True
    assert seed_packet["session_state_updated"] is True
    assert seed_packet["source_handoff_ready"] is True
    assert seed_packet["synthetic_review_packet_detected"] is False
    assert seed_packet["fixture_review_packet_detected"] is False
    assert DEFAULT_ACTUAL_REVIEW_PACKET_SESSION_KEY in fake.session_state
    assert resolved["handoff_state"] == "review_source_handoff_ready"
    assert resolved["source_kind"] == "session_state_in_memory_mapping"
    assert resolved["matched_key"] == DEFAULT_ACTUAL_REVIEW_PACKET_SESSION_KEY
    assert resolved["fallback_used"] is False
    assert resolved["review_packet_ready"] is True


def test_ps_q10o_existing_q9g_panel_consumes_q10n_seeded_packet_without_fallback() -> None:
    fake = FakeStreamlit()
    seed_packet = build_prediction_warroom_actual_review_packet_local_observation_seed_hook(
        review_packet=_actual_review_packet(),
        session_state=fake.session_state,
        enable_actual_review_packet_seed=True,
        local_observation_mode=ACTUAL_REVIEW_PACKET_LOCAL_OBSERVATION_ALLOWED_MODE,
    ).to_dict()
    assert seed_packet["hook_state"] == "actual_review_packet_local_observation_seed_hook_actual_packet_installed"
    panel = _panel_module(fake)
    panel.render_prediction_warroom_lowered_display_packet_visibility_review_panel()
    captions = _captions(fake)
    rows = _flatten_rows(fake.dataframes)
    assert "source_handoff=review_source_handoff_ready" in captions
    assert "source_kind=session_state_in_memory_mapping" in captions
    assert "matched_key=" + DEFAULT_ACTUAL_REVIEW_PACKET_SESSION_KEY in captions
    assert "fallback=False" in captions
    assert "ready_for_ui_mount=True" in captions
    assert "widgets=6" in captions
    assert not fake.infos
    assert not fake.warnings
    assert any(row.get("name") == "widget_group_count" and row.get("value") == 6 for row in rows)
    assert any(row.get("name") == "visible_widget_group_count" and row.get("value") == 6 for row in rows)
    assert any(row.get("widget_group_id") == "primary_signal_widget" for row in rows)
    assert any(row.get("widget_group_id") == "warning_refresh_widget" for row in rows)
    assert any(row.get("card_id") == "prediction_headline" and row.get("prediction_run_id") == "actual_seed_to_panel_integration_run_20260621T000000Z" for row in rows)
    assert any(row.get("gate_id") == "real_payload_required_for_top_default" and row.get("state") == "ready" for row in rows)


def test_ps_q10o_fallback_remains_visible_when_no_seed_packet_exists() -> None:
    fake = FakeStreamlit()
    panel = _panel_module(fake)
    panel.render_prediction_warroom_lowered_display_packet_visibility_review_panel()
    captions = _captions(fake)
    assert "source_handoff=review_source_handoff_fallback_blocked" in captions
    assert "source_kind=blocked_fallback_contract" in captions
    assert "fallback=True" in captions
    assert fake.infos == ["No lowered display-packet widget candidates are available for review yet."]


def test_ps_q10o_existing_q9g_panel_keeps_execution_boundaries_false_after_q10n_seed() -> None:
    fake = FakeStreamlit()
    seed_packet = build_prediction_warroom_actual_review_packet_local_observation_seed_hook(
        review_packet=_actual_review_packet(),
        session_state=fake.session_state,
        enable_actual_review_packet_seed=True,
        local_observation_mode=ACTUAL_REVIEW_PACKET_LOCAL_OBSERVATION_ALLOWED_MODE,
    ).to_dict()
    for key in (
        "streamlit_import_required",
        "ui_controls_added",
        "ui_triggered_loader_execution",
        "would_load_source_artifacts",
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
    ):
        assert seed_packet[key] is False, key
    panel = _panel_module(fake)
    panel.render_prediction_warroom_lowered_display_packet_visibility_review_panel()
    rows = _flatten_rows(fake.dataframes)
    boundary = {str(row.get("boundary")): row.get("enabled") for row in rows if "boundary" in row}
    assert boundary["streamlit_review_panel"] is True
    for key in (
        "warroom_card_rendering",
        "warroom_page_mutation_after_this_mount",
        "ui_triggered_loader_execution",
        "runtime_file_read",
        "payload_decode",
        "runtime_artifact_write",
        "approval_or_authorization_grant",
        "decision_or_command_ledger_append",
        "autotrade_trigger",
        "broker_private_api",
    ):
        assert boundary[key] is False, key
    assert any(row.get("execution") == "false" for row in rows)
    assert all(row.get("broker") != "true" for row in rows)
    assert all(row.get("autotrade") != "true" for row in rows)


def main() -> int:
    test_ps_q10o_static_not_mounted_and_no_runtime_boundaries()
    test_ps_q10o_seed_hook_supplies_q9h_session_packet_before_panel_render()
    test_ps_q10o_existing_q9g_panel_consumes_q10n_seeded_packet_without_fallback()
    test_ps_q10o_fallback_remains_visible_when_no_seed_packet_exists()
    test_ps_q10o_existing_q9g_panel_keeps_execution_boundaries_false_after_q10n_seed()
    print("[OK] Prediction System PS-Q10O actual seed-to-panel integration guard passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
