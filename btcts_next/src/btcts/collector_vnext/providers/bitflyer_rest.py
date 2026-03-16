# path: ./btcts_next/src/btcts/collector_vnext/providers/bitflyer_rest.py
# desc: bitFlyer REST provider for Collector vNext that returns raw source payloads.

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Dict, Optional

import requests


BASE_URL = "https://api.bitflyer.com"


@dataclass(frozen=True)
class RestFetchResult:
    ok: bool
    provider: str
    exchange: str
    transport: str
    endpoint: str
    status_code: int
    payload: Optional[Dict[str, Any]]
    error: str
    retry_after_sec: float
    request_meta: Dict[str, Any]
    response_meta: Dict[str, Any]
    received_ts: Optional[str]


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


def _get_json(
    endpoint: str,
    *,
    params: Optional[Dict[str, Any]] = None,
    timeout_sec: float = 10.0,
) -> RestFetchResult:
    url = f"{BASE_URL}{endpoint}"
    request_meta = {
        "method": "GET",
        "endpoint": endpoint,
        "params": params or {},
        "timeout_sec": timeout_sec,
    }

    try:
        resp = requests.get(url, params=params, timeout=timeout_sec)
        received_ts = _utc_now_iso()
    except Exception as exc:
        return RestFetchResult(
            ok=False,
            provider="bitflyer_rest",
            exchange="bitflyer",
            transport="rest",
            endpoint=endpoint,
            status_code=0,
            payload=None,
            error=str(exc),
            retry_after_sec=0.0,
            request_meta=request_meta,
            response_meta={},
            received_ts=None,
        )

    response_meta = _response_meta(resp)

    if not (200 <= resp.status_code < 300):
        return RestFetchResult(
            ok=False,
            provider="bitflyer_rest",
            exchange="bitflyer",
            transport="rest",
            endpoint=endpoint,
            status_code=int(resp.status_code),
            payload=None,
            error=f"http {resp.status_code}",
            retry_after_sec=_retry_after_sec(resp),
            request_meta=request_meta,
            response_meta=response_meta,
            received_ts=received_ts,
        )

    try:
        js = resp.json()
    except Exception as exc:
        return RestFetchResult(
            ok=False,
            provider="bitflyer_rest",
            exchange="bitflyer",
            transport="rest",
            endpoint=endpoint,
            status_code=int(resp.status_code),
            payload=None,
            error=f"json decode error: {exc}",
            retry_after_sec=0.0,
            request_meta=request_meta,
            response_meta=response_meta,
            received_ts=received_ts,
        )

    if isinstance(js, dict):
        payload: Dict[str, Any] = js
    elif isinstance(js, list):
        payload = {"items": js}
    else:
        return RestFetchResult(
            ok=False,
            provider="bitflyer_rest",
            exchange="bitflyer",
            transport="rest",
            endpoint=endpoint,
            status_code=int(resp.status_code),
            payload=None,
            error="unexpected json type",
            retry_after_sec=0.0,
            request_meta=request_meta,
            response_meta=response_meta,
            received_ts=received_ts,
        )

    return RestFetchResult(
        ok=True,
        provider="bitflyer_rest",
        exchange="bitflyer",
        transport="rest",
        endpoint=endpoint,
        status_code=int(resp.status_code),
        payload=payload,
        error="",
        retry_after_sec=0.0,
        request_meta=request_meta,
        response_meta=response_meta,
        received_ts=received_ts,
    )


def fetch_board(*, product_code: str = "BTC_JPY", timeout_sec: float = 10.0) -> RestFetchResult:
    return _get_json(
        "/v1/board",
        params={"product_code": product_code},
        timeout_sec=timeout_sec,
    )


def fetch_executions(
    *,
    product_code: str = "BTC_JPY",
    count: int = 50,
    timeout_sec: float = 10.0,
) -> RestFetchResult:
    return _get_json(
        "/v1/executions",
        params={
            "product_code": product_code,
            "count": int(count),
        },
        timeout_sec=timeout_sec,
    )