# path: ./tools/test_prediction_system_ps_q10t_actual_review_packet_live_page_observation_capture_contract_guard.py
# desc: Guard for PS-Q10T live/local observation capture contract. Uses local fake Streamlit observation of the mounted Q10R path; no production UI mutation.

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
from btcts.apps.operator_ui.components.prediction_warroom_actual_review_packet_live_page_observation_capture_contract import (
    ACTUAL_REVIEW_PACKET_LIVE_PAGE_OBSERVATION_CAPTURE_CONTRACT_VERSION,
    build_prediction_warroom_actual_review_packet_live_page_observation_capture_contract,
)
from btcts.apps.operator_ui.components.prediction_warroom_actual_review_packet_live_page_observation_runbook_contract import (
    PASSIVE_LIVE_PAGE_OBSERVATION_MARKERS,
    SEEDED_LIVE_PAGE_OBSERVATION_MARKERS,
)
from btcts.apps.operator_ui.components.prediction_warroom_actual_review_packet_live_session_seed_gate import ACTUAL_REVIEW_PACKET_LIVE_SESSION_SEED_GATE_MODE
from btcts.apps.operator_ui.components.prediction_warroom_actual_review_packet_live_session_seed_page_mount import (
    ACTUAL_REVIEW_PACKET_LIVE_SESSION_ALLOW_SEED_KEY,
    ACTUAL_REVIEW_PACKET_LIVE_SESSION_GATE_MODE_KEY,
    ACTUAL_REVIEW_PACKET_LIVE_SESSION_LOCAL_ONLY_KEY,
    ACTUAL_REVIEW_PACKET_LIVE_SESSION_OPERATOR_ACK_KEY,
    ACTUAL_REVIEW_PACKET_LIVE_SESSION_SUPPLIED_REVIEW_PACKET_KEY,
    apply_prediction_warroom_actual_review_packet_live_session_seed_page_mount,
)
from btcts.apps.operator_ui.components.prediction_warroom_lowered_display_packet_visibility_review_contract import build_prediction_warroom_lowered_display_packet_visibility_review_contract
from btcts.apps.operator_ui.components.prediction_warroom_sample_packets import build_prediction_warroom_sample_display_packet

REPO_ROOT = Path(__file__).resolve().parents[1]
MODULE = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/components/prediction_warroom_actual_review_packet_live_page_observation_capture_contract.py"
WARROOM_PAGE = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/views/warroom_page.py"
PANEL = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/components/prediction_warroom_lowered_display_packet_visibility_review_panel.py"
FORBIDDEN_IMPORT_PREFIXES = ("streamlit", "pathlib", "json", "subprocess", "requests", "httpx", "ccxt", "pybitflyer", "websocket", "btcts.collector_vnext", "btcts.autotrade")
FORBIDDEN_MODULE_TOKENS = (
    "import streamlit", "open(", "Path(", "read_text", "read_bytes", "json.load", "json.loads", "write_text", "write_bytes", "json.dump", "json.dumps",
    "subprocess", "st.button", "st.form", "st.checkbox", "st.toggle", "build_prediction_warroom_actual_read_operator_runner_scaffold(",
    "build_prediction_warroom_latest_payload_actual_export_runner(", "load_prediction_warroom_latest_payload_read_only(", "allow_actual_read=True", "execute_actual_read=True",
    "place_order(", "send_order(", "create_order(", "append_decision_jsonl", "append_command_ledger_record",
    "streamlit_import_required: bool = True", "ui_controls_added: bool = True", "ui_triggered_loader_execution: bool = True",
    "would_read_runtime_file: bool = True", "would_decode_payload: bool = True", "would_write_runtime_artifact: bool = True",
    "would_send_to_broker: bool = True", "broker_execution_requested: bool = True", "command_ledger_append_requested: bool = True",
    "approval_append_requested: bool = True", "authorization_grant_requested: bool = True", "autotrade_trigger_enabled: bool = True",
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


def _imports_from(path: Path) -> set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    imports: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imports.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imports.add(node.module)
    return imports


def _real_like_display_packet() -> dict[str, Any]:
    payload = build_prediction_warroom_sample_display_packet()
    payload["prediction_run_id"] = "actual_live_page_observation_capture_run_20260621T000000Z"
    payload["packet_id"] = "prediction_warroom_display_packet.ps_q4a.v1:actual_live_page_observation_capture_run_20260621T000000Z"
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


def _panel_module(fake: FakeStreamlit):
    sys.modules["streamlit"] = fake
    module_name = "btcts.apps.operator_ui.components.prediction_warroom_lowered_display_packet_visibility_review_panel"
    sys.modules.pop(module_name, None)
    importlib.invalidate_caches()
    return importlib.import_module(module_name)


def _flatten_rows(dataframes: list[Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for frame in dataframes:
        if isinstance(frame, list):
            rows.extend(item for item in frame if isinstance(item, dict))
    return rows


def _captions(fake: FakeStreamlit) -> str:
    return chr(10).join(fake.captions)


def _boundary_markers(fake: FakeStreamlit) -> list[str]:
    rows = _flatten_rows(fake.dataframes)
    markers: list[str] = []
    for row in rows:
        if "boundary" in row and row.get("enabled") is False:
            markers.append(f"{row.get('boundary')}:false")
    return markers


def _passive_observed_markers() -> tuple[str, ...]:
    fake = FakeStreamlit()
    apply_prediction_warroom_actual_review_packet_live_session_seed_page_mount(session_state=fake.session_state)
    panel = _panel_module(fake)
    panel.render_prediction_warroom_lowered_display_packet_visibility_review_panel()
    captions = _captions(fake)
    markers = ["Prediction WarRoom real payload review", "top/default-expanded"]
    for token in (
        "source_handoff=review_source_handoff_fallback_blocked",
        "source_kind=blocked_fallback_contract",
        "fallback=True",
    ):
        if token in captions:
            markers.append(token)
    if "No lowered display-packet widget candidates are available for review yet." in fake.infos:
        markers.append("No lowered display-packet widget candidates are available for review yet.")
    markers.extend(_boundary_markers(fake))
    return tuple(dict.fromkeys(markers))


def _seeded_observed_markers() -> tuple[str, ...]:
    fake = FakeStreamlit()
    fake.session_state[ACTUAL_REVIEW_PACKET_LIVE_SESSION_SUPPLIED_REVIEW_PACKET_KEY] = _review_packet()
    fake.session_state[ACTUAL_REVIEW_PACKET_LIVE_SESSION_OPERATOR_ACK_KEY] = True
    fake.session_state[ACTUAL_REVIEW_PACKET_LIVE_SESSION_LOCAL_ONLY_KEY] = True
    fake.session_state[ACTUAL_REVIEW_PACKET_LIVE_SESSION_ALLOW_SEED_KEY] = True
    fake.session_state[ACTUAL_REVIEW_PACKET_LIVE_SESSION_GATE_MODE_KEY] = ACTUAL_REVIEW_PACKET_LIVE_SESSION_SEED_GATE_MODE
    apply_prediction_warroom_actual_review_packet_live_session_seed_page_mount(session_state=fake.session_state)
    panel = _panel_module(fake)
    panel.render_prediction_warroom_lowered_display_packet_visibility_review_panel()
    captions = _captions(fake)
    markers = ["Prediction WarRoom real payload review"]
    for token in (
        "source_handoff=review_source_handoff_ready",
        "source_kind=session_state_in_memory_mapping",
        "fallback=False",
        "ready_for_ui_mount=True",
        "widgets=6",
    ):
        if token in captions:
            markers.append(token)
    if "No lowered display-packet widget candidates are available for review yet." not in fake.infos:
        markers.append("No lowered display-packet widget candidates are available for review yet:absent")
    markers.extend(_boundary_markers(fake))
    return tuple(dict.fromkeys(markers))


def _assert_no_side_effect_flags(packet: dict[str, Any]) -> None:
    for key in (
        "streamlit_import_required", "ui_controls_added", "ui_triggered_loader_execution", "would_load_source_artifacts",
        "would_read_runtime_file", "would_decode_payload", "would_write_runtime_artifact", "would_write_collector_state",
        "would_send_to_broker", "broker_execution_requested", "command_ledger_append_requested", "approval_append_requested",
        "authorization_grant_requested", "autotrade_trigger_enabled",
    ):
        assert packet[key] is False, key


def test_ps_q10t_static_contract_only_and_no_ui_runtime_tokens() -> None:
    text = MODULE.read_text(encoding="utf-8")
    imports = _imports_from(MODULE)
    for prefix in FORBIDDEN_IMPORT_PREFIXES:
        assert not any(item == prefix or item.startswith(prefix + ".") for item in imports), prefix
    for token in FORBIDDEN_MODULE_TOKENS:
        assert token not in text, token
    page_text = WARROOM_PAGE.read_text(encoding="utf-8")
    panel_text = PANEL.read_text(encoding="utf-8")
    assert "build_prediction_warroom_actual_review_packet_live_page_observation_capture_contract" not in page_text
    assert "build_prediction_warroom_actual_review_packet_live_page_observation_capture_contract" not in panel_text
    assert "apply_prediction_warroom_actual_review_packet_live_session_seed_page_mount(session_state=st.session_state)" in page_text
    for token in FORBIDDEN_PAGE_RUNTIME_TOKENS:
        assert token not in page_text, token
    assert ACTUAL_REVIEW_PACKET_LIVE_PAGE_OBSERVATION_CAPTURE_CONTRACT_VERSION == "prediction_warroom_actual_review_packet_live_page_observation_capture_contract.ps_q10t.v1"


def test_ps_q10t_default_blocks_without_markers_and_prerequisites() -> None:
    packet = build_prediction_warroom_actual_review_packet_live_page_observation_capture_contract().to_dict()
    assert packet["contract_state"] == "actual_review_packet_live_page_observation_capture_blocked"
    assert packet["ready_for_live_page_observation_acceptance"] is False
    assert "operator_acknowledgement_required" in packet["blocked_reasons"]
    assert "ps_q10s_runbook_ready_required" in packet["blocked_reasons"]
    assert "passive_observation_markers_required" in packet["blocked_reasons"]
    assert "seeded_observation_markers_required" in packet["blocked_reasons"]
    _assert_no_side_effect_flags(packet)


def test_ps_q10t_accepts_local_observation_capture_markers() -> None:
    passive = _passive_observed_markers()
    seeded = _seeded_observed_markers()
    assert set(PASSIVE_LIVE_PAGE_OBSERVATION_MARKERS).issubset(set(passive))
    assert set(SEEDED_LIVE_PAGE_OBSERVATION_MARKERS).issubset(set(seeded))
    packet = build_prediction_warroom_actual_review_packet_live_page_observation_capture_contract(
        passive_observed_markers=passive,
        seeded_observed_markers=seeded,
        operator_acknowledged=True,
        q10s_runbook_ready=True,
        q10r_guard_passed=True,
    ).to_dict()
    assert packet["contract_state"] == "actual_review_packet_live_page_observation_capture_accepted"
    assert packet["ready_for_live_page_observation_acceptance"] is True
    assert packet["passive_observation_matches_runbook"] is True
    assert packet["seeded_observation_matches_runbook"] is True
    assert packet["passive_missing_markers"] == []
    assert packet["seeded_missing_markers"] == []
    assert packet["seeded_absent_marker_violations"] == []
    assert "live_local_observation_capture_accepted_contract_only" in packet["warning_reasons"]
    _assert_no_side_effect_flags(packet)


def test_ps_q10t_blocks_missing_or_contradictory_markers() -> None:
    packet = build_prediction_warroom_actual_review_packet_live_page_observation_capture_contract(
        passive_observed_markers=("Prediction WarRoom real payload review",),
        seeded_observed_markers=(
            "Prediction WarRoom real payload review",
            "No lowered display-packet widget candidates are available for review yet:absent",
            "No lowered display-packet widget candidates are available for review yet.",
        ),
        operator_acknowledged=True,
        q10s_runbook_ready=True,
        q10r_guard_passed=True,
    ).to_dict()
    assert packet["contract_state"] == "actual_review_packet_live_page_observation_capture_blocked"
    assert "passive_observation_markers_missing" in packet["blocked_reasons"]
    assert "seeded_observation_markers_missing" in packet["blocked_reasons"]
    assert "seeded_absent_marker_observed_as_present" in packet["blocked_reasons"]


def test_ps_q10t_rejects_unsafe_runtime_or_ui_requests() -> None:
    packet = build_prediction_warroom_actual_review_packet_live_page_observation_capture_contract(
        passive_observed_markers=PASSIVE_LIVE_PAGE_OBSERVATION_MARKERS,
        seeded_observed_markers=SEEDED_LIVE_PAGE_OBSERVATION_MARKERS,
        operator_acknowledged=True,
        q10s_runbook_ready=True,
        q10r_guard_passed=True,
        requested_warroom_page_patch_this_slice=True,
        requested_warroom_panel_patch_this_slice=True,
        requested_ui_actual_read_controls=True,
        requested_ui_loader_execution=True,
        requested_ui_file_read_or_decode=True,
        requested_runtime_artifact_write_from_ui=True,
        requested_approval_ledger_autotrade_or_broker=True,
    ).to_dict()
    assert packet["contract_state"] == "actual_review_packet_live_page_observation_capture_blocked"
    for reason in (
        "warroom_page_patch_not_allowed_in_q10t",
        "warroom_panel_patch_not_allowed_in_q10t",
        "warroom_ui_actual_read_controls_not_allowed",
        "warroom_ui_loader_execution_not_allowed",
        "warroom_ui_file_read_or_payload_decode_not_allowed",
        "runtime_artifact_write_from_warroom_ui_not_allowed",
        "approval_ledger_autotrade_broker_not_allowed",
    ):
        assert reason in packet["blocked_reasons"], reason
    _assert_no_side_effect_flags(packet)


def main() -> int:
    test_ps_q10t_static_contract_only_and_no_ui_runtime_tokens()
    test_ps_q10t_default_blocks_without_markers_and_prerequisites()
    test_ps_q10t_accepts_local_observation_capture_markers()
    test_ps_q10t_blocks_missing_or_contradictory_markers()
    test_ps_q10t_rejects_unsafe_runtime_or_ui_requests()
    print("[OK] Prediction System PS-Q10T actual review-packet live page observation capture contract guard passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
