# path: ./btc_trade_system/common/rate.py
# desc: 軽量トークンバケットとスコープ管理（global→group→endpoint の汎用構成に拡張可能な最小実装）。

from __future__ import annotations
import time, threading
from dataclasses import dataclass
from typing import Dict, Optional

__all__ = ["TokenBucket", "RateRegistry", "RateLimitExceeded", "now_ms"]


def now_ms() -> int:
    return int(time.time() * 1000)


class RateLimitExceeded(Exception):
    pass


@dataclass
class TokenBucket:
    capacity: float          # 最大トークン数
    refill_per_sec: float    # 1 秒あたり補充量
    tokens: float = 0.0
    last_ms: int = 0
    lock: threading.RLock = threading.RLock()

    def __post_init__(self) -> None:
        self.tokens = self.capacity
        self.last_ms = now_ms()

    def _refill(self, now: Optional[int] = None) -> None:
        if now is None:
            now = now_ms()
        elapsed = max(0, now - self.last_ms) / 1000.0
        if elapsed > 0:
            self.tokens = min(self.capacity, self.tokens + self.refill_per_sec * elapsed)
            self.last_ms = now

    def try_acquire(self, cost: float = 1.0) -> bool:
        with self.lock:
            self._refill()
            if self.tokens >= cost:
                self.tokens -= cost
                return True
            return False

    def acquire(self, cost: float = 1.0, timeout_ms: int = 0) -> None:
        deadline = now_ms() + max(0, timeout_ms)
        while True:
            with self.lock:
                self._refill()
                if self.tokens >= cost:
                    self.tokens -= cost
                    return
                # 追加で必要な時間（ms）を概算
                need = (cost - self.tokens) / max(1e-9, self.refill_per_sec)
                sleep_ms = int(max(1, need * 1000))
            if timeout_ms <= 0 and sleep_ms > 0:
                time.sleep(min(0.5, sleep_ms / 1000.0))
                continue
            # timeout あり
            if now_ms() + sleep_ms > deadline:
                raise RateLimitExceeded("rate limit timeout")
            time.sleep(min(0.5, sleep_ms / 1000.0))


class RateRegistry:
    """名前付きスコープのレート制御。将来は階層（global→group→endpoint）に拡張。
    現状は endpoint 単位の最小実装。
    """

    def __init__(self) -> None:
        self._buckets: Dict[str, TokenBucket] = {}
        self._lock = threading.RLock()

    def ensure(self, name: str, capacity: float, refill_per_sec: float) -> TokenBucket:
        with self._lock:
            bk = self._buckets.get(name)
            if bk is None:
                bk = TokenBucket(capacity=capacity, refill_per_sec=refill_per_sec)
                self._buckets[name] = bk
            return bk

    def acquire(self, name: str, *, cost: float = 1.0, timeout_ms: int = 0,
                capacity: float = 10.0, refill_per_sec: float = 5.0) -> None:
        bk = self.ensure(name, capacity=capacity, refill_per_sec=refill_per_sec)
        bk.acquire(cost=cost, timeout_ms=timeout_ms)

    def try_acquire(self, name: str, *, cost: float = 1.0,
                    capacity: float = 10.0, refill_per_sec: float = 5.0) -> bool:
        bk = self.ensure(name, capacity=capacity, refill_per_sec=refill_per_sec)
        return bk.try_acquire(cost=cost)
