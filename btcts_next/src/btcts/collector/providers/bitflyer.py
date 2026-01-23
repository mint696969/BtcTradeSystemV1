# path: ./btcts_next/src/btcts/collector/providers/bitflyer.py
# desc: bitFlyer 公開API（board/executions）を取得し、429/Retry-After を解析して上位層へ返す。

from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

import requests


BASE = "https://api.bitflyer.com"


@dataclass
class HttpResult:
    ok: bool
    status_code: int
    retry_after_sec: float = 0.0
    payload: Optional[Dict[str, Any]] = None
    err: str = ""


def _get_json(url: str, *, params: Optional[Dict[str, Any]] = None, timeout_sec: float = 10.0) -> HttpResult:
    try:
        r = requests.get(url, params=params, timeout=timeout_sec)
    except Exception as e:
        return HttpResult(ok=False, status_code=0, err=str(e))

    ra = 0.0
    if r.status_code == 429:
        # Retry-After (sec) を優先、無ければ0
        v = r.headers.get("Retry-After", "") or ""
        try:
            ra = float(v)
        except Exception:
            ra = 0.0
        return HttpResult(ok=False, status_code=429, retry_after_sec=max(ra, 0.0), err="rate limited (429)")

    if not (200 <= r.status_code < 300):
        return HttpResult(ok=False, status_code=int(r.status_code), err=f"http {r.status_code}")

    try:
        js = r.json()
    except Exception as e:
        return HttpResult(ok=False, status_code=int(r.status_code), err=f"json decode error: {e}")

    if isinstance(js, dict):
        return HttpResult(ok=True, status_code=int(r.status_code), payload=js)

    # board は dict / executions は list が来るので list は dict で包む
    if isinstance(js, list):
        return HttpResult(ok=True, status_code=int(r.status_code), payload={"items": js})

    return HttpResult(ok=False, status_code=int(r.status_code), err="unexpected json type")


def fetch_board(*, product_code: str = "BTC_JPY") -> HttpResult:
    """
    /v1/board
    戻り: payload は dict
    """
    url = f"{BASE}/v1/board"
    return _get_json(url, params={"product_code": product_code})


def fetch_executions(*, product_code: str = "BTC_JPY", count: int = 50) -> HttpResult:
    """
    /v1/executions
    戻り: payload は {"items":[...]} の dict に正規化
    ※ compact_executions が product_code を確実に入れられるよう、payload に付与する
    """
    url = f"{BASE}/v1/executions"
    res = _get_json(url, params={"product_code": product_code, "count": int(count)})

    if res.ok and isinstance(res.payload, dict):
        # executions は list を {"items": [...]} に包むため、ここで付与するのが最も安全
        res.payload.setdefault("product_code", product_code)

    return res


def compact_board(raw: Dict[str, Any], *, depth: int = 10) -> Dict[str, Any]:
    """
    GPTに見せる用途を前提に、板情報を軽量化。
    - best bid/ask
    - mid/spread
    - 上位 depth の bids/asks（price,size）
    """
    bids = raw.get("bids") or []
    asks = raw.get("asks") or []

    def _top(x: Any) -> List[Dict[str, float]]:
        out: List[Dict[str, float]] = []
        if isinstance(x, list):
            for it in x[: max(int(depth), 0)]:
                if not isinstance(it, dict):
                    continue
                p = it.get("price")
                s = it.get("size")
                try:
                    out.append({"price": float(p), "size": float(s)})
                except Exception:
                    continue
        return out

    tb = _top(bids)
    ta = _top(asks)

    best_bid = tb[0]["price"] if tb else None
    best_ask = ta[0]["price"] if ta else None
    mid = (best_bid + best_ask) / 2.0 if (best_bid is not None and best_ask is not None) else None
    spread = (best_ask - best_bid) if (best_bid is not None and best_ask is not None) else None

    return {
        "ts": time.time(),
        "exchange": "bitflyer",
        "topic": "orderbook",
        "product_code": raw.get("product_code"),
        "best_bid": best_bid,
        "best_ask": best_ask,
        "mid": mid,
        "spread": spread,
        "bids": tb,
        "asks": ta,
    }


def compact_executions(raw: Dict[str, Any], *, limit: int = 50) -> Dict[str, Any]:
    """
    約定を軽量化。必要最低限だけ（exec_date, price, size, side）
    ※ product_code は必ず上位オブジェクトに入れる（仕様書: 6A.4）
    """
    items = raw.get("items") or []
    out: List[Dict[str, Any]] = []

    # bitFlyer executions の素データには通常 product_code が入らないため、
    # 呼び出し側（fetch_executions の product_code）または wrapper 側で付与する前提。
    # ここでは raw 側に付与されていればそれを採用し、無ければ None のままにしないよう
    # items からは推測せず、raw からのみ取得する。
    product_code = raw.get("product_code")

    if isinstance(items, list):
        for it in items[: max(int(limit), 0)]:
            if not isinstance(it, dict):
                continue
            try:
                out.append(
                    {
                        "id": it.get("id"),
                        "exec_date": it.get("exec_date"),
                        "price": float(it.get("price")),
                        "size": float(it.get("size")),
                        "side": it.get("side"),
                    }
                )

            except Exception:
                continue

    return {
        "ts": time.time(),
        "exchange": "bitflyer",
        "topic": "trades",
        "product_code": product_code,
        "items": out,
    }
