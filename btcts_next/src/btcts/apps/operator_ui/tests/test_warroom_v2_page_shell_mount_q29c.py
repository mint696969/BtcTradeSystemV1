# path: ./btcts_next/src/btcts/apps/operator_ui/tests/test_warroom_v2_page_shell_mount_q29c.py
# desc: Guards the current WarRoom v2 RT visible mount contract while preserving Q29C history.

from __future__ import annotations

import sys
from pathlib import Path

_SRC_ROOT = Path(__file__).resolve().parents[4]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

from btcts.apps.operator_ui.views.warroom_v2_page import (  # noqa: E402
    WARROOM_V2_RT_VISIBLE_MOUNT_VERSION,
    build_warroom_v2_page_mount_packet,
)

REPO_ROOT = Path(__file__).resolve().parents[6]
APP = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/app.py"
V2_VIEW = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/views/warroom_v2_page.py"
HISTORICAL_DOC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q29C_WARROOM_V2_PAGE_SHELL_MOUNT_2026-07-02.md"
CURRENT_DOC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_WARROOM_V2_RT_VISIBLE_MOUNT_2026-07-05.md"


def test_q29c_current_app_uses_localized_v2_route_and_redirects_legacy_key() -> None:
    text = APP.read_text(encoding="utf-8-sig")
    assert '("warroom_v2", get_text(lang, "page_warroom"), warroom_v2_page)' in text
    assert 'LEGACY_PAGE_KEY_REDIRECTS = {' in text
    assert '"warroom": "warroom_v2"' in text
    assert '("warroom", get_text(lang, "page_warroom"), warroom_page)' not in text


def test_q29c_empty_runtime_mount_packet_is_receive_only_and_safe() -> None:
    packet = build_warroom_v2_page_mount_packet()
    assert packet["page_mount_version"] == WARROOM_V2_RT_VISIBLE_MOUNT_VERSION
    assert packet["page_key"] == "warroom_v2"
    assert packet["thin_page_shell_only"] is False
    assert packet["rt_visible_mount_ready"] is True
    assert packet["runtime_connected"] is False
    assert packet["push_connected"] is False
    assert packet["websocket_enabled"] is False
    assert packet["page_reload_enabled"] is False
    assert packet["websocket_send_enabled"] is False
    assert packet["broker_send_enabled"] is False
    assert packet["order_intent_submitted"] is False
    assert packet["ledger_append_allowed"] is False
    assert packet["prediction_invoked"] is False
    assert packet["classifier_invoked"] is False


def test_q29c_live_receiver_state_updates_observation_flags_without_execution() -> None:
    packet = build_warroom_v2_page_mount_packet(
        runtime_status={
            "receiver_runtime_started": True,
            "socket_opened": True,
            "receive_loop_started": True,
        },
        bridge_packet={"messages_applied": 3},
        display_source="live",
    )
    assert packet["runtime_connected"] is True
    assert packet["push_connected"] is True
    assert packet["websocket_enabled"] is True
    assert packet["receive_loop_started"] is True
    assert packet["messages_applied"] == 3
    assert packet["rt_display_source"] == "live"
    assert packet["websocket_send_enabled"] is False
    assert packet["broker_send_enabled"] is False
    assert packet["order_intent_submitted"] is False
    assert packet["ledger_append_allowed"] is False
    assert packet["prediction_invoked"] is False
    assert packet["classifier_invoked"] is False


def test_q29c_current_page_has_receive_only_runtime_boundary() -> None:
    text = V2_VIEW.read_text(encoding="utf-8-sig")
    assert "ensure_warroom_push_widget_live_observation_runtime" in text
    assert "apply_warroom_push_widget_rt_live_receiver_bridge_to_session_state" in text
    assert '"websocket_send_enabled": False' in text
    assert '"broker_send_enabled": False' in text
    assert '"order_intent_submitted": False' in text
    assert '"ledger_append_allowed": False' in text
    assert '"prediction_invoked": False' in text
    assert '"classifier_invoked": False' in text
    for forbidden in (
        "send_to_broker(",
        "append_ledger(",
        "ledger.append(",
        "write_prediction_artifact(",
        "classify_market_regime_feature_bundle(",
    ):
        assert forbidden not in text


def test_q29c_historical_shell_doc_is_preserved_and_current_rt_doc_is_authoritative() -> None:
    historical = HISTORICAL_DOC.read_text(encoding="utf-8-sig")
    current = CURRENT_DOC.read_text(encoding="utf-8-sig")

    assert "PS-Q29C WarRoom v2 page shell mount" in historical
    assert "not_connecting_dhot=true" in historical
    assert "not_enabling_websocket=true" in historical

    assert "warroom_v2_rt_visible_mount_ready=true" in current
    assert "preview_shell_removed=true" in current
    assert "warroom_page_starts_receiver_runtime_when_endpoint_present=true" in current
    assert "websocket_send_enabled=false" in current
    assert "broker_send_enabled=false" in current
    assert "prediction_invoked=false" in current
    assert "classifier_invoked=false" in current
