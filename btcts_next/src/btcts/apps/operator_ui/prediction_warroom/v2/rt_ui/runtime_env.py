# path: ./btcts_next/src/btcts/apps/operator_ui/prediction_warroom/v2/rt_ui/runtime_env.py
# desc: WarRoom v2 RT runtime environment adapter. Defaults to D-hot collector state for safe realtime observation.

from __future__ import annotations

import os
from typing import Any

D_HOT_ENDPOINT = "dhot://unified_market_state"
D_HOT_SOURCE = "dhot_unified_market_state_provider"


def bool_env(name: str, default: str = "true") -> bool:
    return str(os.environ.get(name, default)).strip().lower() not in {"0", "false", "no", "off"}


def default_realtime_observation_enabled() -> bool:
    return bool_env("WARROOM_PUSH_WIDGET_REALTIME_OBSERVATION_DEFAULT", "true")


def endpoint_from_env() -> str:
    configured = str(os.environ.get("WARROOM_PUSH_WIDGET_WS_URL") or "")
    source = str(os.environ.get("WARROOM_PUSH_WIDGET_SOURCE") or "")
    if default_realtime_observation_enabled() and (not configured or configured.startswith("bitflyer://") or source == "bitflyer_collector_provider"):
        return D_HOT_ENDPOINT
    return configured or D_HOT_ENDPOINT


def source_from_env() -> str:
    configured = str(os.environ.get("WARROOM_PUSH_WIDGET_SOURCE") or "")
    endpoint = endpoint_from_env()
    if endpoint.startswith("dhot://") or not configured or configured == "bitflyer_collector_provider":
        return D_HOT_SOURCE
    return configured


def runtime_config_from_env() -> dict[str, Any]:
    return {
        "source": source_from_env(),
        "symbol": os.environ.get("BTCTS_SYMBOL", "FX_BTC_JPY"),
        "ssl_verify": str(bool_env("BTCTS_WS_SSL_VERIFY", "true")).lower(),
        "ca_file": os.environ.get("BTCTS_WS_CA_FILE", ""),
        "recv_timeout_sec": float(os.environ.get("WARROOM_PUSH_WIDGET_RECV_TIMEOUT_SEC", "60")),
        "state_root": os.environ.get("BTCTS_STATE_ROOT", "D:/btc_ts_hot/state"),
        "poll_interval_sec": float(os.environ.get("WARROOM_PUSH_WIDGET_DHOT_POLL_INTERVAL_SEC", "0.25")),
    }
