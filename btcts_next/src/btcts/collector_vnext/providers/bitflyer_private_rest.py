# path: ./btcts_next/src/btcts/collector_vnext/providers/bitflyer_private_rest.py
# desc: bitFlyer private REST read-only client for SR-FX verification.

from __future__ import annotations

import hashlib
import hmac
import json
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Dict, Optional

import requests

from btcts.collector_vnext.secrets import BitflyerPrivateCredential


BASE_URL = "https://api.bitflyer.com"


@dataclass(frozen=True)
class PrivateRestResult:
    ok: bool
    provider: str
    exchange: str
    transport: str
    endpoint: str
    request_class: str
    status_code: int
    payload: Optional[Dict[str, Any]]
    error: str
    retry_after_sec: float
    received_ts: Optional[str]
    response_meta: Dict[str, Any]

    def redacted(self) -> Dict[str, Any]:
        return {
            "ok": self.ok,
            "provider": self.provider,
            "exchange": self.exchange,
            "transport": self.transport,
            "endpoint": self.endpoint,
            "request_class": self.request_class,
            "status_code": self.status_code,
            "payload_type": type(self.payload).__name__ if self.payload is not None else None,
            "payload_keys": sorted(self.payload.keys()) if isinstance(self.payload, dict) else [],
            "error": self.error,
            "retry_after_sec": self.retry_after_sec,
            "received_ts": self.received_ts,
            "response_meta": self.response_meta,
        }


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _retry_after_sec(resp: requests.Response) -> float:
    raw = resp.headers.get("Retry-After", "").strip()
    if not raw:
        return 0.0
    try:
        return max(float(raw), 0.0)
    except Exception:
        return 0.0


def _response_meta(resp: requests.Response) -> Dict[str, Any]:
    return {
        "status_code": int(resp.status_code),
        "headers": {
            "content_type": resp.headers.get("Content-Type", ""),
            "request_id": resp.headers.get("X-Request-Id", ""),
            "rate_limit_remaining": resp.headers.get("X-RateLimit-Remaining", ""),
            "rate_limit_reset": resp.headers.get("X-RateLimit-Reset", ""),
            "retry_after": resp.headers.get("Retry-After", ""),
        },
    }


def _sign(
    credential: BitflyerPrivateCredential,
    *,
    timestamp: str,
    method: str,
    endpoint_with_query: str,
    body: str,
) -> str:
    text = timestamp + method.upper() + endpoint_with_query + body
    return hmac.new(
        credential.api_secret.encode("utf-8"),
        text.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()


def _private_get(
    credential: BitflyerPrivateCredential,
    endpoint: str,
    *,
    params: Optional[Dict[str, Any]] = None,
    request_class: str,
    rate_runtime: Any = None,
    timeout_sec: float = 10.0,
) -> PrivateRestResult:
    exchange = "bitflyer"

    if rate_runtime is not None:
        ok, wait_ms = rate_runtime.acquire(exchange)
        if not ok and wait_ms > 0:
            time.sleep(wait_ms / 1000.0)

    method = "GET"
    query = ""
    if params:
        # requests prepares query encoding; this helper intentionally keeps params simple for bitFlyer private GETs.
        from urllib.parse import urlencode

        query = "?" + urlencode(params)
    endpoint_with_query = endpoint + query
    timestamp = str(time.time())
    body = ""
    sign = _sign(
        credential,
        timestamp=timestamp,
        method=method,
        endpoint_with_query=endpoint_with_query,
        body=body,
    )

    headers = {
        "ACCESS-KEY": credential.api_key,
        "ACCESS-TIMESTAMP": timestamp,
        "ACCESS-SIGN": sign,
        "Content-Type": "application/json",
    }

    url = f"{BASE_URL}{endpoint}"

    try:
        resp = requests.get(url, params=params or {}, headers=headers, timeout=timeout_sec)
        received_ts = _utc_now_iso()
    except Exception as exc:
        return PrivateRestResult(
            ok=False,
            provider="bitflyer_private_rest",
            exchange=exchange,
            transport="rest",
            endpoint=endpoint,
            request_class=request_class,
            status_code=0,
            payload=None,
            error=str(exc),
            retry_after_sec=0.0,
            received_ts=None,
            response_meta={},
        )

    if rate_runtime is not None:
        rate_runtime.note_request_sent(exchange, request_class)

    response_meta = _response_meta(resp)

    if resp.status_code == 429 and rate_runtime is not None:
        rate_runtime.on_429(exchange, _retry_after_sec(resp))

    if not (200 <= resp.status_code < 300):
        return PrivateRestResult(
            ok=False,
            provider="bitflyer_private_rest",
            exchange=exchange,
            transport="rest",
            endpoint=endpoint,
            request_class=request_class,
            status_code=int(resp.status_code),
            payload=None,
            error=f"http {resp.status_code}",
            retry_after_sec=_retry_after_sec(resp),
            received_ts=received_ts,
            response_meta=response_meta,
        )

    try:
        js = resp.json()
    except Exception as exc:
        return PrivateRestResult(
            ok=False,
            provider="bitflyer_private_rest",
            exchange=exchange,
            transport="rest",
            endpoint=endpoint,
            request_class=request_class,
            status_code=int(resp.status_code),
            payload=None,
            error=f"json decode error: {exc}",
            retry_after_sec=0.0,
            received_ts=received_ts,
            response_meta=response_meta,
        )

    if isinstance(js, dict):
        payload: Dict[str, Any] = js
    elif isinstance(js, list):
        payload = {"items": js}
    else:
        payload = {"value": js}

    if rate_runtime is not None:
        rate_runtime.on_success(exchange)

    return PrivateRestResult(
        ok=True,
        provider="bitflyer_private_rest",
        exchange=exchange,
        transport="rest",
        endpoint=endpoint,
        request_class=request_class,
        status_code=int(resp.status_code),
        payload=payload,
        error="",
        retry_after_sec=0.0,
        received_ts=received_ts,
        response_meta=response_meta,
    )


def fetch_collateral(
    credential: BitflyerPrivateCredential,
    *,
    rate_runtime: Any = None,
    timeout_sec: float = 10.0,
) -> PrivateRestResult:
    return _private_get(
        credential,
        "/v1/me/getcollateral",
        request_class="private_rest_account_state",
        rate_runtime=rate_runtime,
        timeout_sec=timeout_sec,
    )


def fetch_positions(
    credential: BitflyerPrivateCredential,
    *,
    product_code: str,
    rate_runtime: Any = None,
    timeout_sec: float = 10.0,
) -> PrivateRestResult:
    return _private_get(
        credential,
        "/v1/me/getpositions",
        params={"product_code": product_code},
        request_class="private_rest_account_state",
        rate_runtime=rate_runtime,
        timeout_sec=timeout_sec,
    )


def fetch_child_orders(
    credential: BitflyerPrivateCredential,
    *,
    product_code: str,
    count: int = 20,
    rate_runtime: Any = None,
    timeout_sec: float = 10.0,
) -> PrivateRestResult:
    return _private_get(
        credential,
        "/v1/me/getchildorders",
        params={"product_code": product_code, "count": int(count)},
        request_class="private_rest_order_state",
        rate_runtime=rate_runtime,
        timeout_sec=timeout_sec,
    )


def fetch_own_executions(
    credential: BitflyerPrivateCredential,
    *,
    product_code: str,
    count: int = 20,
    rate_runtime: Any = None,
    timeout_sec: float = 10.0,
) -> PrivateRestResult:
    return _private_get(
        credential,
        "/v1/me/getexecutions",
        params={"product_code": product_code, "count": int(count)},
        request_class="private_rest_own_fills",
        rate_runtime=rate_runtime,
        timeout_sec=timeout_sec,
    )
