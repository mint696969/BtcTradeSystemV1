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
) -> Generator[WSMessage, None, None]:
    channel = f"lightning_executions_{symbol}"

    sslopt: Dict[str, Any] | None = None
    if not ssl_verify:
        sslopt = {
            "cert_reqs": ssl.CERT_NONE,
            "check_hostname": False,
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
                continue

            params = msg.get("params")
            if not params:
                continue

            if params.get("channel") != channel:
                continue

            data = params.get("message")
            if not isinstance(data, list):
                continue

            for item in data:
                if not isinstance(item, dict):
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
                        "raw_channel": params.get("channel"),
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