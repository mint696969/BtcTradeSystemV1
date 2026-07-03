# path: ./btcts_next/src/btcts/apps/operator_ui/prediction_warroom/v2/transport/ws_display_connection_status.py
# desc: WarRoom v2 compact WS display connection status contract. Pure packet only; no UI, sockets, IO, order send, or polling fallback.

from __future__ import annotations

from typing import Any, Iterable, Mapping

from .ws_display_client_observation import build_warroom_v2_ws_display_client_observation_packet

WARROOM_V2_WS_DISPLAY_CONNECTION_STATUS_VERSION = "prediction_warroom.v2.transport.ws_display_connection_status.ps_q32c.v1"
_ALLOWED_STATUS_FIELDS: tuple[str, ...] = (
    "transport_state_ja",
    "data_freshness_ja",
    "last_update_age_ja",
    "received_message_count",
    "dropped_count",
    "operator_guidance_ja",
)


def _transport_status(*, socket_opened: bool, client_started: bool, received_message_count: int, dropped_count: int) -> tuple[str, str, str]:
    if not socket_opened and not client_started:
        return (
            "ws_not_started_no_socket_open",
            "WS未接続（準備中）",
            "画面更新はまだWS接続ではありません。表示契約のみ確認中です。",
        )
    if socket_opened and client_started and dropped_count > 0:
        return (
            "ws_receiving_with_drops",
            "WS受信中（一部破棄あり）",
            "一部メッセージが表示対象外または不正です。詳細は監査/Diagnosticsで確認します。",
        )
    if socket_opened and client_started and received_message_count > 0:
        return (
            "ws_receiving_display_updates",
            "WS受信中",
            "WarRoom表示更新を受信しています。注文や売買ロジックとは接続していません。",
        )
    if socket_opened:
        return (
            "ws_open_waiting_for_display_messages",
            "WS接続中（表示待ち）",
            "接続はありますが、表示更新メッセージはまだありません。",
        )
    return (
        "ws_client_defined_not_connected",
        "WS未接続",
        "WSクライアント契約はありますが、接続は開始していません。",
    )


def build_warroom_v2_ws_display_connection_status_contract() -> dict[str, Any]:
    return {
        "ok": True,
        "status_version": WARROOM_V2_WS_DISPLAY_CONNECTION_STATUS_VERSION,
        "status_kind": "warroom_v2_ws_display_connection_status_contract_no_socket_open",
        "current_small_goal": "warroom_tab_ws_push_realtime_update_and_japanese_readability",
        "warroom_status_line_allowed_later": True,
        "warroom_status_line_mounted_now": False,
        "allowed_warroom_status_fields": list(_ALLOWED_STATUS_FIELDS),
        "compact_status_only": True,
        "detailed_diagnostics_default_surface": "audit_or_diagnostics_tab",
        "websocket_display_push_required": True,
        "websocket_display_push_main_path": True,
        "ui_receiver_side": True,
        "server_to_warroom_ui": True,
        "socket_opened": False,
        "client_started": False,
        "client_sends_messages": False,
        "external_message_send_enabled": False,
        "websocket_enabled": False,
        "runtime_connected": False,
        "push_connected": False,
        "browser_timer_polling_is_legacy_compat_only": True,
        "browser_timer_refresh_replacement_target": True,
        "no_new_polling_fallback": True,
        "no_browser_timer_reload_introduced": True,
        "streamlit_render_allowed": False,
        "warroom_page_ui_switch": False,
        "order_intent_submitted": False,
        "broker_send_enabled": False,
        "would_send_to_broker": False,
        "ledger_append_allowed": False,
        "mode_apply_allowed": False,
        "parameter_apply_allowed": False,
        "prediction_generation_invoked": False,
        "prediction_inference_invoked": False,
        "classifier_invoked": False,
    }


def build_warroom_v2_ws_display_connection_status_packet(
    *,
    fragment_summary: Mapping[str, Any] | None = None,
    messages: Iterable[Mapping[str, Any]] | None = None,
    now_label: str = "not-connected",
) -> dict[str, Any]:
    observation = build_warroom_v2_ws_display_client_observation_packet(fragment_summary=fragment_summary, messages=list(messages or []))
    received = int(observation.get("received_message_count") or 0)
    dropped = int(observation.get("dropped_count") or 0)
    socket_opened = bool(observation.get("socket_opened"))
    client_started = bool(observation.get("client_started"))
    status_code, transport_state_ja, operator_guidance_ja = _transport_status(
        socket_opened=socket_opened,
        client_started=client_started,
        received_message_count=received,
        dropped_count=dropped,
    )
    status_line = {
        "transport_state_ja": transport_state_ja,
        "data_freshness_ja": "未接続のため未取得",
        "last_update_age_ja": "未接続",
        "received_message_count": received,
        "dropped_count": dropped,
        "operator_guidance_ja": operator_guidance_ja,
    }
    return {
        **build_warroom_v2_ws_display_connection_status_contract(),
        "packet_kind": "warroom_v2_ws_display_connection_status_packet",
        "status_code": status_code,
        "status_line": status_line,
        "status_line_field_count": len(status_line),
        "status_line_labels_ja": list(status_line.keys()),
        "status_line_compact": True,
        "status_line_allowed_in_warroom_later": True,
        "status_line_visible_now": False,
        "now_label": str(now_label),
        "client_observation_packet": observation,
        "received_message_count": received,
        "dropped_count": dropped,
        "socket_opened": False,
        "client_started": False,
        "client_sends_messages": False,
        "visible_ui_decoration_added": False,
        "streamlit_component_added": False,
        "button_added": False,
        "checkbox_added": False,
        "metric_added": False,
        "caption_added": False,
    }
