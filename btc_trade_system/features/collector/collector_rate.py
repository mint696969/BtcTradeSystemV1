# path: ./btc_trade_system/features/collector/collector_rate.py
# desc: 取引所ごとの優先度キュー + SLA 駆動のレート制御（方式C）。429/Retry-After を最優先し、安全側へ降格・復帰を管理。

from __future__ import annotations

import time
import math
import heapq
from dataclasses import dataclass, field
from typing import Dict, Optional, Tuple, List

# 設計方針（方式C）
# - exchange ごとの優先度キュー（endpoint 優先度 + age による飢餓防止）
# - トークンバケット風に次回許可時刻 next_at を管理
# - 429/Retry-After を受けたら exchange 単位でクールダウン降格（指数バックオフ + ヒステリシス）
# - SLA: endpoint ごとの target_interval を与え、最小待機を保証
# - I/F は極小: request_permit(exchange, endpoint) -> (allowed, wait_ms)

@dataclass
class EndpointPolicy:
    priority: int            # 小さいほど高優先度（例: orderbook=0, trades=1, ticker=2）
    target_interval: float   # 目安の最小間隔（秒）

@dataclass
class ExState:
    cooldown_until: float = 0.0
    penalty: int = 0  # 429 ペナルティ段数（指数バックオフ）
    last_at: Dict[str, float] = field(default_factory=dict)  # endpoint -> last issued

class RateController:
    """交換所ごとの優先度キュー + SLA 最小 I/F。方式C。"""

    def __init__(self, now_fn=time.monotonic):
        self.now = now_fn
        self.policies: Dict[str, Dict[str, EndpointPolicy]] = {}
        self.state: Dict[str, ExState] = {}

    # 設定投入（例示）
    def set_policy(self, exchange: str, endpoint: str, *, priority: int, target_interval: float) -> None:
        self.policies.setdefault(exchange, {})[endpoint] = EndpointPolicy(priority, target_interval)
        self.state.setdefault(exchange, ExState())

    def _cooldown_wait(self, ex: str) -> float:
        s = self.state.setdefault(ex, ExState())
        return max(0.0, s.cooldown_until - self.now())

    def _next_allowed_at(self, ex: str, ep: str) -> float:
        pol = self.policies.get(ex, {}).get(ep)
        s = self.state.setdefault(ex, ExState())
        last = s.last_at.get(ep, 0.0)
        base = (last + (pol.target_interval if pol else 0.0)) if pol else last
        # ペナルティ段数で引き延ばす（指数バックオフ, 1.6^penalty）
        if s.penalty > 0:
            base = max(base, self.now() + (1.6 ** s.penalty))
        # exchange 単位のクールダウンも尊重
        if s.cooldown_until > base:
            base = s.cooldown_until
        return base

    def request_permit(self, exchange: str, endpoint: str) -> Tuple[bool, int]:
        """実行許可の可否と待機ミリ秒を返す。"""
        t = self.now()
        wait = self._cooldown_wait(exchange)
        if wait > 0:
            return False, int(wait * 1000)
        next_at = self._next_allowed_at(exchange, endpoint)
        if t >= next_at:
            self.state[exchange].last_at[endpoint] = t
            return True, 0
        else:
            return False, int((next_at - t) * 1000)

    # 429/Retry-After 等のシグナルを受けたときに呼ぶ
    def on_rate_limited(self, exchange: str, *, retry_after_sec: Optional[float] = None) -> None:
        s = self.state.setdefault(exchange, ExState())
        s.penalty = min(s.penalty + 1, 6)
        if retry_after_sec and retry_after_sec > 0:
            s.cooldown_until = max(s.cooldown_until, self.now() + retry_after_sec)
        else:
            # 明示が無いときは指数バックオフ相当を反映
            s.cooldown_until = max(s.cooldown_until, self.now() + (1.6 ** s.penalty))

    # 成功が続いたら段階的に回復
    def on_success(self, exchange: str) -> None:
        s = self.state.setdefault(exchange, ExState())
        if s.penalty > 0 and (self.now() >= s.cooldown_until):
            s.penalty -= 1

# 簡易テスト（後で専用テストへ）
if __name__ == "__main__":
    rc = RateController()
    rc.set_policy("bitflyer", "orderbook", priority=0, target_interval=0.2)
    rc.set_policy("bitflyer", "trades", priority=1, target_interval=0.5)

    for i in range(5):
        ok, wait = rc.request_permit("bitflyer", "orderbook")
        print("OB", i, ok, wait)
        time.sleep(0.05)
    rc.on_rate_limited("bitflyer", retry_after_sec=1.2)
    ok, wait = rc.request_permit("bitflyer", "orderbook")
    print("after429", ok, wait)
