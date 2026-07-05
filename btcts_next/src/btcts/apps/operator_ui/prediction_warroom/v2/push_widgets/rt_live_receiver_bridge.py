# path: ./btcts_next/src/btcts/apps/operator_ui/prediction_warroom/v2/push_widgets/rt_live_receiver_bridge.py
# desc: RT0-RT6 WarRoom push-widget live observation runtime. Starts receiver-only WebSocket runtime, drains received messages, updates widget state/session_state/page packets, and keeps no-action guards.

from __future__ import annotations

import json
import os
import threading
import time
from collections import deque
from typing import Any, Callable, Mapping, MutableMapping

from .wp1_architecture_contracts import build_wp1_no_send_flags
from .wp3_per_widget_state_store import build_initial_widget_state_store
from .wp4_receive_only_push_router import route_receive_only_push_batch
from .wp6_independent_widget_update_pipeline import build_render_packets_from_store
from .wp7_widget_health_freshness import attach_widget_health, build_widget_health_packets
from .wp9_warroom_page_mount import WARROOM_WP9_PAGE_MOUNT_SESSION_STATE_KEY
from .wp11_top_layout_push_widget_polish import WARROOM_WP11_TOP_LAYOUT_SESSION_STATE_KEY, build_wp11_top_layout_groups
from .wp12_bottom_chart_layout import WARROOM_WP12_BOTTOM_CHART_SESSION_STATE_KEY, build_bottom_chart_overlays, build_bottom_chart_rows
from .wp13_prediction_card_connection import WARROOM_WP13_PREDICTION_CARD_SESSION_STATE_KEY, build_prediction_card_contexts

RT_LIVE_RECEIVER_BRIDGE_VERSION = "warroom.manual_trade_support.push_widgets.rt0_rt6.live_observation_runtime.v1"
WARROOM_RT_LIVE_RECEIVER_SOURCE_STATE_KEY = "warroom_push_widget_rt_live_receiver_messages"
WARROOM_RT_LIVE_WIDGET_STORE_STATE_KEY = "warroom_push_widget_rt_live_widget_store"
WARROOM_RT_LIVE_RECEIVER_BRIDGE_SESSION_STATE_KEY = "warroom_push_widget_rt_live_receiver_bridge_packet"
WARROOM_RT_LIVE_RUNTIME_STATUS_STATE_KEY = "warroom_push_widget_rt_live_runtime_status"
WARROOM_RT_LIVE_DRAINED_MESSAGES_STATE_KEY = "warroom_push_widget_rt_live_drained_messages"
WARROOM_RT_LIVE_ENDPOINT_STATE_KEY = "warroom_push_widget_rt_live_receiver_endpoint_url"
_Q33_LIGHTWEIGHT_PREVIEW_KEY = "warroom_v2_ws_receiver_only_client_lightweight_state_q33f_preview"
_Q33_HIDDEN_RECORD_KEY = "warroom_v2_ws_receiver_only_client_lightweight_state_target_write_hidden_record_q33j"
_RUNTIME: dict[str, "ReceiverOnlyRuntime"] = {}
_RUNTIME_LOCK = threading.Lock()
ConnectFn = Callable[[str, Mapping[str, Any]], Any]


def _flags() -> dict[str, Any]:
    flags = build_wp1_no_send_flags()
    flags.update({"websocket_send_enabled": False, "broker_send_enabled": False, "order_intent_submitted": False, "ledger_append_allowed": False, "auto_trading_enabled": False, "prediction_invoked": False, "classifier_invoked": False})
    return flags


def _parse_wire_message(raw: object) -> list[Mapping[str, Any]]:
    if isinstance(raw, bytes):
        raw = raw.decode("utf-8", errors="replace")
    if isinstance(raw, str):
        try:
            raw = json.loads(raw)
        except json.JSONDecodeError:
            return [{"topic_key": "receiver.lifecycle", "value": {"text": raw[:200]}, "received_at_ms": int(time.time() * 1000)}]
    if isinstance(raw, list):
        return [x for x in raw if isinstance(x, Mapping)]
    if isinstance(raw, Mapping):
        if isinstance(raw.get("messages"), list):
            return [x for x in raw["messages"] if isinstance(x, Mapping)]
        return [raw]
    return []


def _source_items(source: object) -> list[Mapping[str, Any]]:
    if isinstance(source, (list, tuple, deque)):
        return [x for x in source if isinstance(x, Mapping)]
    if isinstance(source, Mapping):
        for key in ("messages", "received_messages", "drained_messages", "target_messages"):
            value = source.get(key)
            if isinstance(value, (list, tuple, deque)):
                return [x for x in value if isinstance(x, Mapping)]
        nested = source.get("target_lightweight_state_value_preview")
        if isinstance(nested, Mapping):
            return _source_items(nested)
    return []


def normalize_live_receiver_messages(source: object) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for index, msg in enumerate(_source_items(source)):
        topic = str(msg.get("topic_key") or msg.get("topic") or "")
        if not topic:
            continue
        value = msg.get("value", {})
        if not isinstance(value, Mapping):
            value = {"value": value}
        seq = msg.get("sequence", index + 1)
        out.append({"topic_key": topic, "value": dict(value), "received_at_ms": int(msg.get("received_at_ms") or msg.get("updated_at_ms") or msg.get("ts_ms") or int(time.time() * 1000)), "sequence": int(seq) if str(seq).strip() else index + 1, "receive_only": True})
    return out


def _default_connect(endpoint: str, runtime_config: Mapping[str, Any]) -> Any:
    try:
        from websockets.sync.client import connect as ws_connect  # type: ignore
        return ws_connect(endpoint, open_timeout=float(runtime_config.get("open_timeout_sec", 5)))
    except Exception as first_exc:  # noqa: BLE001
        try:
            import websocket  # type: ignore
            return websocket.create_connection(endpoint, timeout=float(runtime_config.get("open_timeout_sec", 5)))
        except Exception as second_exc:  # noqa: BLE001
            raise RuntimeError(f"receiver websocket client unavailable or failed: {type(first_exc).__name__}; {type(second_exc).__name__}") from second_exc


class ReceiverOnlyRuntime:
    def __init__(self, *, endpoint_url: str, runtime_key: str, connect_fn: ConnectFn | None = None, runtime_config: Mapping[str, Any] | None = None, buffer_limit: int = 256) -> None:
        self.endpoint_url = endpoint_url
        self.runtime_key = runtime_key
        self.connect_fn = connect_fn or _default_connect
        self.runtime_config = dict(runtime_config or {})
        self.buffer: deque[dict[str, Any]] = deque(maxlen=buffer_limit)
        self.lock = threading.Lock()
        self.stop_event = threading.Event()
        self.thread: threading.Thread | None = None
        self.status: dict[str, Any] = {"runtime_key": runtime_key, "endpoint_url_present": bool(endpoint_url), "receiver_runtime_started": False, "socket_opened": False, "receive_loop_started": False, "received_message_count": 0, **_flags()}

    def start(self) -> None:
        if self.thread and self.thread.is_alive():
            return
        self.thread = threading.Thread(target=self._run, name=f"warroom-push-widget-receiver-{self.runtime_key}", daemon=True)
        self.status.update({"receiver_runtime_started": True, "receiver_thread_alive": True})
        self.thread.start()

    def _append(self, messages: list[Mapping[str, Any]]) -> None:
        normalized = normalize_live_receiver_messages(messages)
        with self.lock:
            for message in normalized:
                self.buffer.append(message)
            self.status["received_message_count"] = int(self.status.get("received_message_count", 0)) + len(normalized)
            self.status["latest_message_at_ms"] = int(time.time() * 1000)

    def _recv_once(self, conn: Any) -> object:
        if hasattr(conn, "recv"):
            return conn.recv()
        if isinstance(conn, Mapping):
            messages = conn.get("messages") or conn.get("received_messages") or []
            self.stop_event.set()
            return {"messages": messages}
        if isinstance(conn, (list, tuple)):
            self.stop_event.set()
            return {"messages": list(conn)}
        self.stop_event.set()
        return {}

    def _run(self) -> None:
        conn = None
        try:
            conn = self.connect_fn(self.endpoint_url, dict(self.runtime_config))
            self.status.update({"socket_opened": True, "websocket_opened": True, "client_started": True, "runtime_connected": True, "push_connected": True, "receive_loop_started": True, **_flags()})
            while not self.stop_event.is_set():
                raw = self._recv_once(conn)
                parsed = _parse_wire_message(raw)
                if parsed:
                    self._append(parsed)
                if isinstance(conn, Mapping) or isinstance(conn, (list, tuple)):
                    break
        except Exception as exc:  # noqa: BLE001
            self.status.update({"receiver_error": {"error_type": type(exc).__name__, "error_message": str(exc)}, "socket_opened": False, "websocket_opened": False, "receive_loop_started": False})
        finally:
            self.status["receiver_thread_alive"] = False
            try:
                if conn is not None and hasattr(conn, "close"):
                    conn.close()
            except Exception:  # noqa: BLE001
                pass

    def drain(self) -> list[dict[str, Any]]:
        with self.lock:
            items = list(self.buffer)
            self.buffer.clear()
        self.status["last_drain_count"] = len(items)
        self.status["last_drain_at_ms"] = int(time.time() * 1000)
        return items

    def snapshot(self) -> dict[str, Any]:
        with self.lock:
            pending = len(self.buffer)
        return {**self.status, "pending_message_count": pending, **_flags()}


def _endpoint(session_state: Mapping[str, Any], endpoint_url: str | None) -> str:
    return str(endpoint_url or session_state.get(WARROOM_RT_LIVE_ENDPOINT_STATE_KEY) or os.environ.get("WARROOM_PUSH_WIDGET_WS_URL") or "")


def ensure_warroom_push_widget_live_observation_runtime(session_state: MutableMapping[str, Any], *, endpoint_url: str | None = None, connect_fn: ConnectFn | None = None, runtime_config: Mapping[str, Any] | None = None, runtime_key: str = "default") -> dict[str, Any]:
    endpoint = _endpoint(session_state, endpoint_url)
    if not endpoint:
        status = {"ok": True, "packet_kind": "warroom_push_widget_rt_live_runtime_status_packet", "receiver_runtime_configured": False, "receiver_runtime_started": False, "endpoint_url_present": False, "drained_message_count": 0, **_flags()}
        session_state[WARROOM_RT_LIVE_RUNTIME_STATUS_STATE_KEY] = status
        return status
    with _RUNTIME_LOCK:
        runtime = _RUNTIME.get(runtime_key)
        if runtime is None or runtime.endpoint_url != endpoint or connect_fn is not None:
            runtime = ReceiverOnlyRuntime(endpoint_url=endpoint, runtime_key=runtime_key, connect_fn=connect_fn, runtime_config=runtime_config)
            _RUNTIME[runtime_key] = runtime
        runtime.start()
    drained = runtime.drain()
    if drained:
        session_state[WARROOM_RT_LIVE_DRAINED_MESSAGES_STATE_KEY] = drained
    status = {"ok": True, "packet_kind": "warroom_push_widget_rt_live_runtime_status_packet", "receiver_runtime_configured": True, "receiver_runtime_started": True, "endpoint_url_present": True, "endpoint_url_redacted": "<provided>", "drained_message_count": len(drained), "drained_messages": drained, **runtime.snapshot(), **_flags()}
    session_state[WARROOM_RT_LIVE_RUNTIME_STATUS_STATE_KEY] = status
    return status


def _session_source(session_state: Mapping[str, Any]) -> object:
    for key in (WARROOM_RT_LIVE_DRAINED_MESSAGES_STATE_KEY, WARROOM_RT_LIVE_RECEIVER_SOURCE_STATE_KEY, _Q33_LIGHTWEIGHT_PREVIEW_KEY, _Q33_HIDDEN_RECORD_KEY):
        value = session_state.get(key)
        if value:
            return value
    return {}


def _page_packet(render_packets: Mapping[str, Mapping[str, Any]], *, now_ms: int, messages_applied: int) -> dict[str, Any]:
    health = build_widget_health_packets(render_packets, now_ms=now_ms)
    enriched = attach_widget_health(render_packets, health)
    live_ids = sorted(k for k, v in enriched.items() if v.get("freshness_label") == "live")
    packet = {"ok": True, "packet_kind": "warroom_push_widget_rt_live_page_mount_packet", "version": RT_LIVE_RECEIVER_BRIDGE_VERSION, "rt0_live_receiver_runtime_started": True, "live_receiver_bridge_used": True, "messages_applied": messages_applied, "widget_count": len(enriched), "render_packet_count": len(enriched), "live_widget_count": len(live_ids), "widget_ids": sorted(enriched), "live_widget_ids": live_ids, "render_packets": enriched, "health_packets": health}
    packet.update(_flags())
    return packet


def apply_warroom_push_widget_rt_live_receiver_bridge_to_session_state(session_state: MutableMapping[str, Any], *, receiver_source: object | None = None, now_ms: int = 0) -> dict[str, Any]:
    messages = normalize_live_receiver_messages(_session_source(session_state) if receiver_source is None else receiver_source)
    has_store = isinstance(session_state.get(WARROOM_RT_LIVE_WIDGET_STORE_STATE_KEY), Mapping)
    if not messages and not has_store:
        return {"ok": True, "packet_kind": "warroom_push_widget_rt_live_receiver_bridge_idle_packet", "live_receiver_bridge_idle": True, "messages_applied": 0, "session_state_mutated": False, **_flags()}
    store = session_state.get(WARROOM_RT_LIVE_WIDGET_STORE_STATE_KEY) if has_store else build_initial_widget_state_store()
    routed = route_receive_only_push_batch(store, messages)
    render_packets = build_render_packets_from_store(routed)
    effective_now = int(now_ms or max([m["received_at_ms"] for m in messages] + [int(time.time() * 1000)]))
    page = _page_packet(render_packets, now_ms=effective_now, messages_applied=len(messages))
    groups = build_wp11_top_layout_groups(page)
    top = {"ok": True, "packet_kind": "warroom_push_widget_rt_live_top_layout_packet", "version": RT_LIVE_RECEIVER_BRIDGE_VERSION, "top_information_groups_ready": True, "group_count": len(groups), "base_widget_count": page["widget_count"], "live_widget_count": page["live_widget_count"], "groups": [g.to_dict() for g in groups], **_flags()}
    rows, overlays = build_bottom_chart_rows(page), build_bottom_chart_overlays(top)
    bottom = {"ok": True, "packet_kind": "warroom_push_widget_rt_live_bottom_chart_packet", "version": RT_LIVE_RECEIVER_BRIDGE_VERSION, "bottom_chart_data_adapter_ready": True, "bottom_chart_overlay_ready": True, "bottom_chart_stale_handling_ready": True, "chart_row_count": len(rows), "overlay_count": len(overlays), "stale_row_count": len([r for r in rows if r.freshness_label != "live"]), "refresh_cadence_ms": 1000, "chart_rows": [r.to_dict() for r in rows], "overlays": [o.to_dict() for o in overlays], **_flags()}
    cards = build_prediction_card_contexts(bottom)
    prediction = {"ok": True, "packet_kind": "warroom_push_widget_rt_live_prediction_card_packet", "version": RT_LIVE_RECEIVER_BRIDGE_VERSION, "prediction_card_connection_ready": True, "prediction_card_update_ready": True, "prediction_card_no_action_boundary_ready": True, "prediction_card_count": len(cards), "bottom_chart_row_count": bottom["chart_row_count"], "bottom_chart_overlay_count": bottom["overlay_count"], "cards": [c.to_dict() for c in cards], **_flags()}
    composite = {"ok": True, "packet_kind": "warroom_push_widget_rt_live_receiver_bridge_packet", "version": RT_LIVE_RECEIVER_BRIDGE_VERSION, "rt0_live_receiver_runtime_started": True, "rt1_live_receiver_source_to_router_bridge_ready": True, "rt2_received_websocket_message_to_state_store_apply_ready": True, "rt3_session_state_lightweight_state_reflection_ready": True, "rt4_warroom_auto_refresh_observation_ready": True, "rt5_live_freshness_stale_error_observation_ready": True, "rt6_no_send_broker_order_boundary_ready": True, "messages_applied": len(messages), "updated_widget_ids": page["live_widget_ids"], "session_state_mutated": True, **_flags()}
    session_state[WARROOM_RT_LIVE_WIDGET_STORE_STATE_KEY] = routed
    session_state[WARROOM_RT_LIVE_RECEIVER_BRIDGE_SESSION_STATE_KEY] = composite
    session_state[WARROOM_WP9_PAGE_MOUNT_SESSION_STATE_KEY] = page
    session_state[WARROOM_WP11_TOP_LAYOUT_SESSION_STATE_KEY] = top
    session_state[WARROOM_WP12_BOTTOM_CHART_SESSION_STATE_KEY] = bottom
    session_state[WARROOM_WP13_PREDICTION_CARD_SESSION_STATE_KEY] = prediction
    session_state[WARROOM_RT_LIVE_DRAINED_MESSAGES_STATE_KEY] = []
    return composite
