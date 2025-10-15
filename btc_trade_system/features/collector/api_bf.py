# path: ./btc_trade_system/features/collector/adapters/bitflyer_public.py
# desc: bitFlyer の公開API（/v1/executions, /v1/board）を標準ライブラリで叩く最小アダプタ。依存ゼロ・UA/Timeout対応。

from __future__ import annotations
import json
from dataclasses import dataclass
from typing import Any, Dict, List, Optional
from urllib.parse import urlencode
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError

BITFLYER_BASE = "https://api.bitflyer.com"


@dataclass(frozen=True)
class Execution:
    id: int
    side: str         # "BUY"/"SELL"
    price: float
    size: float
    exec_date: str    # ISO8601
    buy_child_order_acceptance_id: Optional[str]
    sell_child_order_acceptance_id: Optional[str]


class BitflyerPublic:
    """
    公開API最小クライアント（標準ライブラリのみ）。
    - timeout 秒でリクエストを切る
    - User-Agent を固定で送る（規制回避のため識別しやすく）
    - JSONの基本検証のみ実施（必要最低限）
    """

    def __init__(self, base_url: str = BITFLYER_BASE, *, timeout: float = 5.0, user_agent: str = "BtcTS-V1/collector"):
        self.base_url = base_url.rstrip("/")
        self.timeout = float(timeout)
        self.user_agent = user_agent

    # ---- HTTP -----------------------------------------------------------------
    def _get_json(self, path: str, params: Dict[str, Any]) -> Any:
        q = ("?" + urlencode(params)) if params else ""
        url = f"{self.base_url}{path}{q}"
        req = Request(url, headers={"User-Agent": self.user_agent})
        try:
            with urlopen(req, timeout=self.timeout) as resp:
                data = resp.read()
            return json.loads(data.decode("utf-8"))
        except HTTPError as e:
            # 呼び出し側で扱いやすいよう情報を保つ
            raise RuntimeError(f"HTTP {e.code} for {path}: {e.reason}") from e
        except URLError as e:
            raise RuntimeError(f"URL error for {path}: {e.reason}") from e
        except Exception as e:
            raise RuntimeError(f"Unexpected error for {path}: {e}") from e

    # ---- Endpoints ------------------------------------------------------------
    def executions(self, *, product_code: str = "BTC_JPY", count: int = 200, before: Optional[int] = None, after: Optional[int] = None) -> List[Execution]:
        """
        https://api.bitflyer.com/v1/executions
        - 最大200件（bitFlyer側の上限に合わせる）
        - before/after は取引IDでのページング
        """
        params: Dict[str, Any] = {"product_code": product_code, "count": int(count)}
        if before is not None:
            params["before"] = int(before)
        if after is not None:
            params["after"] = int(after)

        js = self._get_json("/v1/executions", params)
        if not isinstance(js, list):
            raise RuntimeError("invalid response type (expected list)")

        out: List[Execution] = []
        for x in js:
            try:
                out.append(Execution(
                    id=int(x["id"]),
                    side=str(x.get("side") or ""),
                    price=float(x["price"]),
                    size=float(x["size"]),
                    exec_date=str(x["exec_date"]),
                    buy_child_order_acceptance_id=x.get("buy_child_order_acceptance_id"),
                    sell_child_order_acceptance_id=x.get("sell_child_order_acceptance_id"),
                ))
            except Exception:
                # 壊れた要素はスキップ（最小運用）
                continue
        return out

    def board(self, *, product_code: str = "BTC_JPY", top: int = 5) -> dict:
        """
        https://api.bitflyer.com/v1/board
        板情報を取得して軽量サマリを返す。
        戻り値: {
          "product_code": "BTC_JPY",
          "mid_price": <float|None>,
          "best_bid": {"price": float, "size": float} | None,
          "best_ask": {"price": float, "size": float} | None,
          "bids": [{"price": float, "size": float}, ... up to top],
          "asks": [{"price": float, "size": float}, ... up to top],
          "raw_count": {"bids": int, "asks": int},
        }
        """
        params = {"product_code": product_code}
        data = self._get_json("/v1/board", params)  # 例外は上位で捕捉

        def _norm(side_list):
            out = []
            for x in side_list or []:
                try:
                    p = float(x.get("price"))
                    s = float(x.get("size"))
                except Exception:
                    continue
                out.append({"price": p, "size": s})
            return out

        bids = _norm(data.get("bids"))[:max(0, int(top))]
        asks = _norm(data.get("asks"))[:max(0, int(top))]
        best_bid = bids[0] if bids else None
        best_ask = asks[0] if asks else None

        mid_price = data.get("mid_price")
        if mid_price is None and best_bid and best_ask:
            mid_price = (best_bid["price"] + best_ask["price"]) / 2.0

        return {
            "product_code": product_code,
            "mid_price": float(mid_price) if mid_price is not None else None,
            "best_bid": best_bid,
            "best_ask": best_ask,
            "bids": bids,
            "asks": asks,
            "raw_count": {
                "bids": len(data.get("bids") or []),
                "asks": len(data.get("asks") or []),
            },
        }
