# path: ./btcts_next/src/btcts/apps/operator_ui/prediction_warroom/v2/rt_ui/status_view.py
# desc: Compact WarRoom v2 RT runtime status renderer.

from __future__ import annotations

from typing import Any, Mapping


def render_rt_runtime_status(runtime_status: Mapping[str, Any], bridge_packet: Mapping[str, Any], st_api: Any) -> dict[str, Any]:
    c1, c2, c3, c4 = st_api.columns(4)
    receiver_started = bool(runtime_status.get("receiver_runtime_started"))
    receive_loop = bool(runtime_status.get("receive_loop_started"))
    messages_applied = int(bridge_packet.get("messages_applied") or 0)
    c1.metric("Runtime", "connected" if receiver_started else "waiting")
    c2.metric("Push", "receiving" if receive_loop or messages_applied else "waiting")
    c3.metric("Drained", int(runtime_status.get("drained_message_count") or 0))
    c4.metric("Applied", messages_applied)
    endpoint_label = "<provided>" if runtime_status.get("endpoint_url_present") else "not configured"
    st_api.caption(
        " / ".join(
            [
                f"endpoint={endpoint_label}",
                f"receiver_runtime_started={receiver_started}",
                f"socket_opened={bool(runtime_status.get('socket_opened'))}",
                f"receive_loop_started={receive_loop}",
                "websocket_send_enabled=false",
                "broker_send_enabled=false",
            ]
        )
    )
    error = runtime_status.get("receiver_error")
    if isinstance(error, Mapping) and error:
        st_api.warning(f"receiver_error={error.get('error_type')}: {error.get('error_message')}")
    return {"ok": True, "receiver_started": receiver_started, "receive_loop_started": receive_loop, "messages_applied": messages_applied, "read_only": True}
