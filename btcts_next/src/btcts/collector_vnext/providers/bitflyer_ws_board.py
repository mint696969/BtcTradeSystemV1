# path: ./btcts_next/src/btcts/collector_vnext/providers/bitflyer_ws_board.py
# desc: bitFlyer WebSocket board snapshot + diff stream.

from __future__ import annotations

import json
import ssl
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Dict, Generator, Optional

import websocket


WS_URL = "wss://ws.lightstream.bitflyer.com/json-rpc"


@dataclass
class BoardMessage:
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


def _subscribe(channel: str) -> str:
    return json.dumps(
        {
            "method": "subscribe",
            "params": {
                "channel": channel,
            },
        }
    )


def connect_and_stream_board(
    symbol: str,
    *,
    ssl_verify: bool = True,
    ca_file: str | None = None,
) -> Generator[BoardMessage, None, None]:
    snapshot_channel = f"lightning_board_snapshot_{symbol}"
    diff_channel = f"lightning_board_{symbol}"

    sslopt = None

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

    ws = websocket.create_connection(
        WS_URL,
        timeout=10,
        sslopt=sslopt,
    )

    ws.send(_subscribe(snapshot_channel))
    ws.send(_subscribe(diff_channel))

    try:
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

            channel = params.get("channel")

            if channel not in (snapshot_channel, diff_channel):
                continue

            payload = params.get("message")

            if not isinstance(payload, dict):
                continue

            provider = "bitflyer_ws_board" if channel == diff_channel else "bitflyer_ws_board_snapshot"

            yield BoardMessage(
                provider=provider,
                exchange="bitflyer",
                transport="websocket",
                channel=channel,
                payload=payload,
                received_ts=received_ts,
                subscription_id=None,
                message_id=None,
                source_sequence=None,
                raw_message_meta={
                    "raw_channel": channel,
                    "subscription_channel": channel,
                    "recv_timeout_sec": 10,
                    "ssl_verify": ssl_verify,
                    "socket_url": WS_URL,
                    "ca_file": ca_file,
                },
            )

    finally:
        try:
            ws.close()
        except Exception:
            pass