# path: ./btcts_next/src/btcts/collector_vnext/providers/bitflyer_ws.py
# desc: Minimal bitFlyer WebSocket client for executions stream with configurable SSL verification.

from __future__ import annotations

import json
import ssl
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Dict, Generator, Optional

import websocket


WS_URL = "wss://ws.lightstream.bitflyer.com/json-rpc"


@dataclass
class WSMessage:
    provider: str
    exchange: str
    transport: str
    channel: str
    payload: Dict[str, Any]
    received_ts: Optional[str]
    subscription_id: Optional[str]
    message_id: Optional[str]
    source_sequence: int | str | None
    raw_message_meta: Dict[str, Any]


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _subscribe_message(channel: str) -> str:
    msg = {
        "method": "subscribe",
        "params": {
            "channel": channel,
        },
    }
    return json.dumps(msg)


def connect_and_stream_executions(
    symbol: str,
    *,
    ssl_verify: bool = True,
    recv_timeout_sec: float = 60.0,
    ca_file: str | None = None,
) -> Generator[WSMessage, None, None]:
    channel = f"lightning_executions_{symbol}"

    sslopt: Dict[str, Any] | None = None
    if not ssl_verify:
        sslopt = {
            "cert_reqs": ssl.CERT_NONE,
            "check_hostname": False,
        }
    elif ca_file:
        sslopt = {
            "cert_reqs": ssl.CERT_REQUIRED,
            "ca_certs": str(ca_file),
        }

    try:
        ws = websocket.create_connection(
            WS_URL,
            timeout=recv_timeout_sec,
            sslopt=sslopt,
        )
    except Exception as exc:
        raise RuntimeError(f"bitflyer websocket connect failed: {exc}") from exc

    try:
        ws.send(_subscribe_message(channel))

        while True:
            raw = ws.recv()
            received_ts = _utc_now_iso()

            if raw is None:
                break

            try:
                msg = json.loads(raw)
            except Exception:
                yield WSMessage(
                    provider="bitflyer_ws_executions_meta",
                    exchange="bitflyer",
                    transport="websocket",
                    channel=channel,
                    payload={
                        "_meta_event": "json_decode_failed",
                        "_raw_preview": str(raw)[:500],
                    },
                    received_ts=received_ts,
                    subscription_id=None,
                    message_id=None,
                    source_sequence=None,
                    raw_message_meta={
                        "raw_channel": None,
                        "subscription_channel": channel,
                        "recv_timeout_sec": recv_timeout_sec,
                        "ssl_verify": ssl_verify,
                        "socket_url": WS_URL,
                        "ca_file": ca_file,
                    },
                )
                continue

            params = msg.get("params")
            if not params:
                yield WSMessage(
                    provider="bitflyer_ws_executions_meta",
                    exchange="bitflyer",
                    transport="websocket",
                    channel=channel,
                    payload={
                        "_meta_event": "params_missing",
                        "_message_keys": sorted(list(msg.keys())) if isinstance(msg, dict) else None,
                        "_raw_message": msg,
                    },
                    received_ts=received_ts,
                    subscription_id=None,
                    message_id=None,
                    source_sequence=None,
                    raw_message_meta={
                        "raw_channel": None,
                        "subscription_channel": channel,
                        "recv_timeout_sec": recv_timeout_sec,
                        "ssl_verify": ssl_verify,
                        "socket_url": WS_URL,
                        "ca_file": ca_file,
                    },
                )
                continue

            raw_channel = params.get("channel")
            if raw_channel != channel:
                yield WSMessage(
                    provider="bitflyer_ws_executions_meta",
                    exchange="bitflyer",
                    transport="websocket",
                    channel=str(raw_channel or channel),
                    payload={
                        "_meta_event": "unexpected_channel",
                        "_expected_channel": channel,
                        "_actual_channel": raw_channel,
                        "_raw_message": msg,
                    },
                    received_ts=received_ts,
                    subscription_id=None,
                    message_id=None,
                    source_sequence=None,
                    raw_message_meta={
                        "raw_channel": raw_channel,
                        "subscription_channel": channel,
                        "recv_timeout_sec": recv_timeout_sec,
                        "ssl_verify": ssl_verify,
                        "socket_url": WS_URL,
                        "ca_file": ca_file,
                    },
                )
                continue

            data = params.get("message")
            if isinstance(data, list):
                for item in data:
                    if not isinstance(item, dict):
                        yield WSMessage(
                            provider="bitflyer_ws_executions_meta",
                            exchange="bitflyer",
                            transport="websocket",
                            channel=channel,
                            payload={
                                "_meta_event": "non_dict_trade_item",
                                "_item_type": type(item).__name__,
                                "_raw_item": item,
                            },
                            received_ts=received_ts,
                            subscription_id=None,
                            message_id=None,
                            source_sequence=None,
                            raw_message_meta={
                                "raw_channel": raw_channel,
                                "subscription_channel": channel,
                                "recv_timeout_sec": recv_timeout_sec,
                                "ssl_verify": ssl_verify,
                                "socket_url": WS_URL,
                        "ca_file": ca_file,
                            },
                        )
                        continue

                    yield WSMessage(
                        provider="bitflyer_ws_executions",
                        exchange="bitflyer",
                        transport="websocket",
                        channel=channel,
                        payload=item,
                        received_ts=received_ts,
                        subscription_id=None,
                        message_id=None,
                        source_sequence=None,
                        raw_message_meta={
                            "raw_channel": raw_channel,
                            "subscription_channel": channel,
                            "recv_timeout_sec": recv_timeout_sec,
                            "ssl_verify": ssl_verify,
                            "socket_url": WS_URL,
                        "ca_file": ca_file,
                        },
                    )
                continue

            if isinstance(data, dict):
                yield WSMessage(
                    provider="bitflyer_ws_executions",
                    exchange="bitflyer",
                    transport="websocket",
                    channel=channel,
                    payload=data,
                    received_ts=received_ts,
                    subscription_id=None,
                    message_id=None,
                    source_sequence=None,
                    raw_message_meta={
                        "raw_channel": raw_channel,
                        "subscription_channel": channel,
                        "recv_timeout_sec": recv_timeout_sec,
                        "ssl_verify": ssl_verify,
                        "socket_url": WS_URL,
                        "ca_file": ca_file,
                    },
                )
                continue

            yield WSMessage(
                provider="bitflyer_ws_executions_meta",
                exchange="bitflyer",
                transport="websocket",
                channel=channel,
                payload={
                    "_meta_event": "unsupported_message_shape",
                    "_message_type": type(data).__name__,
                    "_raw_message": msg,
                },
                received_ts=received_ts,
                subscription_id=None,
                message_id=None,
                source_sequence=None,
                raw_message_meta={
                    "raw_channel": raw_channel,
                    "subscription_channel": channel,
                    "recv_timeout_sec": recv_timeout_sec,
                    "ssl_verify": ssl_verify,
                    "socket_url": WS_URL,
                },
            )
    finally:
        try:
            ws.close()
        except Exception:
            pass