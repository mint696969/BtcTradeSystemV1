# path: ./tools/test_prediction_system_ps_q10l_actual_session_state_panel_handoff_guard.py
# desc: Focused guard for PS-Q10L actual session-state handoff into existing Q9G panel using fake Streamlit. Test-only; no WarRoom page mutation, no UI loader, no file read/decode, no runtime write, no approval, no ledger, no AutoTrade, no broker.

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
from btcts.apps.operator_ui.components.prediction_warroom_actual_review_packet_session_state_handoff_harness import (
    ACTUAL_REVIEW_PACKET_SESSION_STATE_HANDOFF_HARNESS_VERSION,
    DEFAULT_ACTUAL_REVIEW_PACKET_SESSION_KEY,
    build_prediction_warroom_actual_review_packet_session_state_handoff_harness,
)
from btcts.apps.operator_ui.components.prediction_warroom_lowered_display_packet_visibility_review_contract import build_prediction_warroom_lowered_display_packet_visibility_review_contract
from btcts.apps.operator_ui.components.prediction_warroom_lowered_display_packet_visibility_review_source_handoff import resolve_prediction_warroom_lowered_display_packet_visibility_review_source
from btcts.apps.operator_ui.components.prediction_warroom_sample_packets import build_prediction_warroom_sample_display_packet

REPO_ROOT = Path(__file__).resolve().parents[1]
PANEL = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/components/prediction_warroom_lowered_display_packet_visibility_review_panel.py"
WARROOM_PAGE = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/views/warroom_page.py"
THIS_GUARD = REPO_ROOT / "tools/test_prediction_system_ps_q10l_actual_session_state_panel_handoff_guard.py"
FORBIDDEN_PANEL_TOKENS = (
    "load_prediction",
    "latest_payload",
    "allow_actual_read=True",
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
    "broker_private_api_allowed: bool = True",
    "ui_triggered_loader_execution: bool = True",
)
FORBIDDEN_PAGE_TOKENS = (
    "prediction_warroom_actual_review_packet_session_state_handoff_harness",
    "build_prediction_warroom_actual_read_operator_runner_scaffold",
    "build_prediction_warroom_latest_payload_actual_export_runner",
    "allow_actual_read=True",
    "warroom_prediction_actual_review_packet",
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


def _real_like_display_packet() -> dict:
    payload = build_prediction_warroom_sample_display_packet()
    payload["prediction_run_id"] = "actual_panel_handoff_run_20260621T000000Z"
    payload["packet_id"] = "prediction_warroom_display_packet.ps_q4a.v1:actual_panel_handoff_run_20260621T000000Z"
    payload["headline_ja"] = "Actual panel handoff: 短期は上方向優勢、参考度59%。"
    payload["primary_signal_summary"] = dict(payload["primary_signal_summary"])
    payload["primary_signal_summary"].pop("synthetic_only", None)
    payload["primary_signal_summary"].pop("fixture_only", None)
    payload["boundaries"] = dict(payload["boundaries"])
    payload["boundaries"].pop("synthetic_only", None)
    payload["boundaries"].pop("fixture_only", None)
    payload.pop("synthetic_only", None)
    payload.pop("fixture_only", None)
    return payload


def _actual_review_packet() -> dict:
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


def test_ps_q10l_static_panel_and_page_boundaries() -> None:
    panel_text = PANEL.read_text(encoding="utf-8")
    page_text = WARROOM_PAGE.read_text(encoding="utf-8")
    guard_text = THIS_GUARD.read_text(encoding="utf-8")
    for token in FORBIDDEN_PANEL_TOKENS:
        assert token not in panel_text, token
    for token in FORBIDDEN_PAGE_TOKENS:
        assert token not in page_text, token
    assert "render_prediction_warroom_lowered_display_packet_visibility_review_panel()" in page_text
    assert "Prediction WarRoom real payload review" in page_text
    assert "prediction_warroom_actual_review_packet_session_state_handoff_harness" not in page_text
    assert "FakeStreamlit" in guard_text


def test_ps_q10l_q10k_handoff_can_supply_session_state_packet_for_q9h() -> None:
    state: dict[str, Any] = {}
    handoff = build_prediction_warroom_actual_review_packet_session_state_handoff_harness(
        review_packet=_actual_review_packet(),
        session_state=state,
        store_in_session_state=True,
    ).to_dict()
    resolved = resolve_prediction_warroom_lowered_display_packet_visibility_review_source(session_state=state).to_dict()
    assert handoff["harness_version"] == ACTUAL_REVIEW_PACKET_SESSION_STATE_HANDOFF_HARNESS_VERSION
    assert handoff["harness_state"] == "actual_review_packet_session_state_handoff_ready"
    assert handoff["session_state_updated"] is True
    assert handoff["source_handoff_ready"] is True
    assert handoff["synthetic_review_packet_detected"] is False
    assert handoff["fixture_review_packet_detected"] is False
    assert handoff["blocker_count"] == 0
    assert DEFAULT_ACTUAL_REVIEW_PACKET_SESSION_KEY in state
    assert resolved["handoff_state"] == "review_source_handoff_ready"
    assert resolved["source_kind"] == "session_state_in_memory_mapping"
    assert resolved["fallback_used"] is False
    assert resolved["review_packet_ready"] is True


def test_ps_q10l_existing_q9g_panel_renders_actual_session_packet_without_fallback() -> None:
    fake = FakeStreamlit()
    handoff = build_prediction_warroom_actual_review_packet_session_state_handoff_harness(
        review_packet=_actual_review_packet(),
        session_state=fake.session_state,
        store_in_session_state=True,
    ).to_dict()
    assert handoff["harness_state"] == "actual_review_packet_session_state_handoff_ready"
    panel = _panel_module(fake)
    panel.render_prediction_warroom_lowered_display_packet_visibility_review_panel()

    captions = chr(10).join(fake.captions)
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
    assert any(row.get("card_id") == "prediction_headline" and row.get("prediction_run_id") == "actual_panel_handoff_run_20260621T000000Z" for row in rows)
    assert any(row.get("gate_id") == "real_payload_required_for_top_default" and row.get("state") == "ready" for row in rows)


def test_ps_q10l_existing_q9g_panel_keeps_execution_boundaries_false() -> None:
    fake = FakeStreamlit()
    build_prediction_warroom_actual_review_packet_session_state_handoff_harness(
        review_packet=_actual_review_packet(),
        session_state=fake.session_state,
        store_in_session_state=True,
    )
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
    test_ps_q10l_static_panel_and_page_boundaries()
    test_ps_q10l_q10k_handoff_can_supply_session_state_packet_for_q9h()
    test_ps_q10l_existing_q9g_panel_renders_actual_session_packet_without_fallback()
    test_ps_q10l_existing_q9g_panel_keeps_execution_boundaries_false()
    print("[OK] Prediction System PS-Q10L actual session-state panel handoff guard passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
