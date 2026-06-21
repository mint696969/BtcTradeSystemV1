# path: ./tools/test_prediction_system_ps_q10r_actual_review_packet_live_page_mount_guard.py
# desc: Focused guard for PS-Q10R minimal WarRoom page mount. Verifies Q10P page-mount adapter is called before existing Q9G panel and preserves fallback/no-runtime boundaries.

from __future__ import annotations

import ast
import importlib
from pathlib import Path
import sys
import types
from typing import Any

from _btcts_bootstrap import ensure_btcts_on_syspath
ensure_btcts_on_syspath()

from btcts.apps.operator_ui.components.prediction_warroom_actual_display_packet_lowering_adapter import build_prediction_warroom_actual_display_packet_lowering_result
from btcts.apps.operator_ui.components.prediction_warroom_actual_review_packet_live_session_seed_gate import ACTUAL_REVIEW_PACKET_LIVE_SESSION_SEED_GATE_MODE
from btcts.apps.operator_ui.components.prediction_warroom_actual_review_packet_live_session_seed_page_mount import (
    ACTUAL_REVIEW_PACKET_LIVE_SESSION_ALLOW_SEED_KEY,
    ACTUAL_REVIEW_PACKET_LIVE_SESSION_GATE_MODE_KEY,
    ACTUAL_REVIEW_PACKET_LIVE_SESSION_LOCAL_ONLY_KEY,
    ACTUAL_REVIEW_PACKET_LIVE_SESSION_OPERATOR_ACK_KEY,
    ACTUAL_REVIEW_PACKET_LIVE_SESSION_SEED_PAGE_MOUNT_VERSION,
    ACTUAL_REVIEW_PACKET_LIVE_SESSION_SUPPLIED_REVIEW_PACKET_KEY,
    apply_prediction_warroom_actual_review_packet_live_session_seed_page_mount,
)
from btcts.apps.operator_ui.components.prediction_warroom_actual_review_packet_session_state_handoff_harness import DEFAULT_ACTUAL_REVIEW_PACKET_SESSION_KEY
from btcts.apps.operator_ui.components.prediction_warroom_lowered_display_packet_visibility_review_contract import build_prediction_warroom_lowered_display_packet_visibility_review_contract
from btcts.apps.operator_ui.components.prediction_warroom_sample_packets import build_prediction_warroom_sample_display_packet

REPO_ROOT = Path(__file__).resolve().parents[1]
PAGE = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/views/warroom_page.py"
MOUNT = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/components/prediction_warroom_actual_review_packet_live_session_seed_page_mount.py"
PANEL = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/components/prediction_warroom_lowered_display_packet_visibility_review_panel.py"
FORBIDDEN_MOUNT_TOKENS = (
    "import streamlit", "open(", "Path(", "read_text", "read_bytes", "json.load", "json.loads", "write_text", "write_bytes", "json.dump", "json.dumps",
    "subprocess", "st.button", "st.form", "st.checkbox", "st.toggle", "build_prediction_warroom_actual_read_operator_runner_scaffold(",
    "build_prediction_warroom_latest_payload_actual_export_runner(", "load_prediction_warroom_latest_payload_read_only(", "allow_actual_read=True", "execute_actual_read=True",
    "place_order(", "send_order(", "create_order(", "append_decision_jsonl", "append_command_ledger_record",
)
FORBIDDEN_PAGE_RUNTIME_TOKENS = (
    "build_prediction_warroom_actual_read_operator_runner_scaffold",
    "build_prediction_warroom_latest_payload_actual_export_runner",
    "load_prediction_warroom_latest_payload_read_only",
    "allow_actual_read=True",
    "execute_actual_read=True",
    "st.button(\"Actual",
    "st.form(\"Actual",
    "st.toggle(\"Actual",
    "append_decision_jsonl",
    "append_command_ledger_record",
    "place_order(", "send_order(", "create_order(",
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
    payload["prediction_run_id"] = "actual_live_page_mount_run_20260621T000000Z"
    payload["packet_id"] = "prediction_warroom_display_packet.ps_q4a.v1:actual_live_page_mount_run_20260621T000000Z"
    payload["primary_signal_summary"] = dict(payload["primary_signal_summary"])
    payload["primary_signal_summary"].pop("synthetic_only", None)
    payload["primary_signal_summary"].pop("fixture_only", None)
    payload["boundaries"] = dict(payload["boundaries"])
    payload["boundaries"].pop("synthetic_only", None)
    payload["boundaries"].pop("fixture_only", None)
    payload.pop("synthetic_only", None)
    payload.pop("fixture_only", None)
    return payload


def _review_packet() -> dict[str, Any]:
    lowering = build_prediction_warroom_actual_display_packet_lowering_result(prediction_result_payload=_real_like_display_packet()).to_dict()
    review = build_prediction_warroom_lowered_display_packet_visibility_review_contract(lowering_result=lowering).to_dict()
    assert review["ready_for_ps_q9g_guarded_ui_mount"] is True
    assert review["widget_group_count"] == 6
    return review


def _flatten_rows(dataframes: list[Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for frame in dataframes:
        if isinstance(frame, list):
            rows.extend(item for item in frame if isinstance(item, dict))
    return rows


def _captions(fake: FakeStreamlit) -> str:
    return chr(10).join(fake.captions)


def _panel_module(fake: FakeStreamlit):
    sys.modules["streamlit"] = fake
    module_name = "btcts.apps.operator_ui.components.prediction_warroom_lowered_display_packet_visibility_review_panel"
    sys.modules.pop(module_name, None)
    importlib.invalidate_caches()
    return importlib.import_module(module_name)


def _call_names_in_function(source: str, function_name: str) -> list[str]:
    tree = ast.parse(source)
    calls: list[str] = []
    target = next(node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef) and node.name == function_name)
    for node in ast.walk(target):
        if isinstance(node, ast.Call):
            func = node.func
            if isinstance(func, ast.Name):
                calls.append(func.id)
            elif isinstance(func, ast.Attribute):
                calls.append(func.attr)
    return calls


def _assert_no_side_effect_flags(packet: dict[str, Any]) -> None:
    for key in (
        "streamlit_import_required", "ui_controls_added", "ui_triggered_loader_execution", "would_load_source_artifacts",
        "would_read_runtime_file", "would_decode_payload", "would_write_runtime_artifact", "would_write_collector_state",
        "would_send_to_broker", "broker_execution_requested", "command_ledger_append_requested", "approval_append_requested",
        "authorization_grant_requested", "autotrade_trigger_enabled",
    ):
        assert packet[key] is False, key


def test_ps_q10r_static_page_patch_is_limited_and_before_existing_panel() -> None:
    page_text = PAGE.read_text(encoding="utf-8")
    mount_text = MOUNT.read_text(encoding="utf-8")
    for token in FORBIDDEN_MOUNT_TOKENS:
        assert token not in mount_text, token
    for token in FORBIDDEN_PAGE_RUNTIME_TOKENS:
        assert token not in page_text, token
    assert "apply_prediction_warroom_actual_review_packet_live_session_seed_page_mount" in page_text
    assert "render_prediction_warroom_lowered_display_packet_visibility_review_panel()" in page_text
    assert page_text.index("apply_prediction_warroom_actual_review_packet_live_session_seed_page_mount(") < page_text.index("render_prediction_warroom_lowered_display_packet_visibility_review_panel()")
    calls = _call_names_in_function(page_text, "_render_prediction_warroom_lowered_display_packet_visibility_review_section")
    assert calls.index("apply_prediction_warroom_actual_review_packet_live_session_seed_page_mount") < calls.index("render_prediction_warroom_lowered_display_packet_visibility_review_panel")
    assert ACTUAL_REVIEW_PACKET_LIVE_SESSION_SEED_PAGE_MOUNT_VERSION == "prediction_warroom_actual_review_packet_live_session_seed_page_mount.ps_q10r.v1"
    assert "Prediction WarRoom real payload review is top/default-expanded and read-only" in page_text


def test_ps_q10r_page_mount_without_packet_preserves_q9g_fallback() -> None:
    fake = FakeStreamlit()
    mount_packet = apply_prediction_warroom_actual_review_packet_live_session_seed_page_mount(session_state=fake.session_state)
    assert mount_packet["page_mount_version"] == ACTUAL_REVIEW_PACKET_LIVE_SESSION_SEED_PAGE_MOUNT_VERSION
    assert mount_packet["gate_packet"]["seed_attempted"] is False
    assert mount_packet["gate_packet"]["session_state_updated"] is False
    assert DEFAULT_ACTUAL_REVIEW_PACKET_SESSION_KEY not in fake.session_state
    _assert_no_side_effect_flags(dict(mount_packet))
    panel = _panel_module(fake)
    panel.render_prediction_warroom_lowered_display_packet_visibility_review_panel()
    captions = _captions(fake)
    assert "source_handoff=review_source_handoff_fallback_blocked" in captions
    assert "fallback=True" in captions
    assert fake.infos == ["No lowered display-packet widget candidates are available for review yet."]


def test_ps_q10r_page_mount_with_supplied_packet_seeds_before_q9g_panel() -> None:
    fake = FakeStreamlit()
    fake.session_state[ACTUAL_REVIEW_PACKET_LIVE_SESSION_SUPPLIED_REVIEW_PACKET_KEY] = _review_packet()
    fake.session_state[ACTUAL_REVIEW_PACKET_LIVE_SESSION_OPERATOR_ACK_KEY] = True
    fake.session_state[ACTUAL_REVIEW_PACKET_LIVE_SESSION_LOCAL_ONLY_KEY] = True
    fake.session_state[ACTUAL_REVIEW_PACKET_LIVE_SESSION_ALLOW_SEED_KEY] = True
    fake.session_state[ACTUAL_REVIEW_PACKET_LIVE_SESSION_GATE_MODE_KEY] = ACTUAL_REVIEW_PACKET_LIVE_SESSION_SEED_GATE_MODE
    mount_packet = apply_prediction_warroom_actual_review_packet_live_session_seed_page_mount(session_state=fake.session_state)
    assert mount_packet["gate_packet"]["gate_state"] == "actual_review_packet_live_session_seed_gate_seeded_for_existing_q9g_panel"
    assert mount_packet["gate_packet"]["source_handoff_ready"] is True
    assert mount_packet["gate_packet"]["fallback_used"] is False
    assert DEFAULT_ACTUAL_REVIEW_PACKET_SESSION_KEY in fake.session_state
    _assert_no_side_effect_flags(dict(mount_packet))
    panel = _panel_module(fake)
    panel.render_prediction_warroom_lowered_display_packet_visibility_review_panel()
    captions = _captions(fake)
    rows = _flatten_rows(fake.dataframes)
    assert "source_handoff=review_source_handoff_ready" in captions
    assert "source_kind=session_state_in_memory_mapping" in captions
    assert "fallback=False" in captions
    assert "ready_for_ui_mount=True" in captions
    assert "widgets=6" in captions
    assert not fake.infos
    assert not fake.warnings
    assert any(row.get("card_id") == "prediction_headline" and row.get("prediction_run_id") == "actual_live_page_mount_run_20260621T000000Z" for row in rows)
    assert any(row.get("name") == "widget_group_count" and row.get("value") == 6 for row in rows)


def test_ps_q10r_boundary_rows_remain_false_after_seeded_page_mount() -> None:
    fake = FakeStreamlit()
    fake.session_state[ACTUAL_REVIEW_PACKET_LIVE_SESSION_SUPPLIED_REVIEW_PACKET_KEY] = _review_packet()
    fake.session_state[ACTUAL_REVIEW_PACKET_LIVE_SESSION_OPERATOR_ACK_KEY] = True
    fake.session_state[ACTUAL_REVIEW_PACKET_LIVE_SESSION_LOCAL_ONLY_KEY] = True
    fake.session_state[ACTUAL_REVIEW_PACKET_LIVE_SESSION_ALLOW_SEED_KEY] = True
    fake.session_state[ACTUAL_REVIEW_PACKET_LIVE_SESSION_GATE_MODE_KEY] = ACTUAL_REVIEW_PACKET_LIVE_SESSION_SEED_GATE_MODE
    apply_prediction_warroom_actual_review_packet_live_session_seed_page_mount(session_state=fake.session_state)
    panel = _panel_module(fake)
    panel.render_prediction_warroom_lowered_display_packet_visibility_review_panel()
    boundary = {str(row.get("boundary")): row.get("enabled") for row in _flatten_rows(fake.dataframes) if "boundary" in row}
    assert boundary["streamlit_review_panel"] is True
    for key in (
        "warroom_card_rendering", "warroom_page_mutation_after_this_mount", "ui_triggered_loader_execution",
        "runtime_file_read", "payload_decode", "runtime_artifact_write", "approval_or_authorization_grant",
        "decision_or_command_ledger_append", "autotrade_trigger", "broker_private_api",
    ):
        assert boundary[key] is False, key


def main() -> int:
    test_ps_q10r_static_page_patch_is_limited_and_before_existing_panel()
    test_ps_q10r_page_mount_without_packet_preserves_q9g_fallback()
    test_ps_q10r_page_mount_with_supplied_packet_seeds_before_q9g_panel()
    test_ps_q10r_boundary_rows_remain_false_after_seeded_page_mount()
    print("[OK] Prediction System PS-Q10R actual review-packet live page mount guard passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
