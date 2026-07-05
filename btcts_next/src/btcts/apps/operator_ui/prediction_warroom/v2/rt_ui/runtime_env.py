# path: ./btcts_next/src/btcts/apps/operator_ui/prediction_warroom/v2/rt_ui/runtime_env.py
# desc: WarRoom v2 RT runtime environment adapter. Reads launch env and returns redaction-safe runtime config.

from __future__ import annotations

import os
from typing import Any


def bool_env(name: str, default: str = "true") -> bool:
    return str(os.environ.get(name, default)).strip().lower() not in {"0", "false", "no", "off"}


def endpoint_from_env() -> str:
    return str(os.environ.get("WARROOM_PUSH_WIDGET_WS_URL") or "")


def runtime_config_from_env() -> dict[str, Any]:
    return {
        "source": os.environ.get("WARROOM_PUSH_WIDGET_SOURCE", "dhot_unified_market_state_provider"),
        "symbol": os.environ.get("BTCTS_SYMBOL", "FX_BTC_JPY"),
        "ssl_verify": str(bool_env("BTCTS_WS_SSL_VERIFY", "true")).lower(),
        "ca_file": os.environ.get("BTCTS_WS_CA_FILE", ""),
        "recv_timeout_sec": float(os.environ.get("WARROOM_PUSH_WIDGET_RECV_TIMEOUT_SEC", "60")),
        "state_root": os.environ.get("BTCTS_STATE_ROOT", "D:/btc_ts_hot/state"),
        "poll_interval_sec": float(os.environ.get("WARROOM_PUSH_WIDGET_DHOT_POLL_INTERVAL_SEC", "0.25")),
    }
