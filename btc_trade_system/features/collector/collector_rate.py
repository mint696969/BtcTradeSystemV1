# path: btc_trade_system/features/collector/collector_rate.py
# desc: 取引所ごとの優先度キュー + SLA 駆動のレート制御（方式C）に、取引所レベルのトークンバケット(max_rps, burst)を追加。

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Dict, Optional, Tuple, Any

# 設計方針（方式C 拡張）
# - exchange ごとの「全体レート制御」＝トークンバケット（max_rps / burst）
# - endpoint ごとの SLA = target_interval を保証（最小インターバル）
# - 429/Retry-After を受けたら exchange 単位でペナルティ降格（指数バックオフ + クールダウン）
# - I/F:
#     set_policy(exchange, endpoint, priority, target_interval) ・・・従来どおり
#     set_exchange_policy(exchange, max_rps, burst) ・・・新規（YAML の rate.* を反映）
#     request_permit(exchange, endpoint) -> (allowed: bool, wait_ms: int)
#     on_rate_limited(exchange, retry_after_sec?)
#     on_success(exchange)

@dataclass
class EndpointPolicy:
    priority: int            # 小さいほど高優先度（例: orderbook=0, trades=1, ticker=2）
    target_interval: float   # 目安の最小間隔（秒）

@dataclass
class ExchangePolicy:
    max_rps: float = 0.0     # 0 または未設定ならバケット無効（endpoint SLA のみ）
    burst: int = 1           # バースト許容量（>=1）

@dataclass
class ExState:
    # レート制御（429系）
    cooldown_until: float = 0.0
    penalty: int = 0  # 429 ペナルティ段数（指数バックオフ）
    last_rate_limited_ts: float = 0.0  # 直近で 429/Retry-After を受けた時刻（monotonic 秒）

    # endpoint ごとの直近発行時刻
    last_at: Dict[str, float] = field(default_factory=dict)  # endpoint -> last issued

    # exchange レベルのトークンバケット
    tokens: float = 0.0
    last_refill: float = 0.0  # 最終リフィル時刻（monotonic 秒）

class RateController:
    """交換所ごとの優先度キュー + SLA + トークンバケット。"""

    def __init__(self, now_fn=time.monotonic):
        self.now = now_fn
        self.policies: Dict[str, Dict[str, EndpointPolicy]] = {}
        self.ex_policy: Dict[str, ExchangePolicy] = {}
        self.state: Dict[str, ExState] = {}

    # == 設定投入 ==

    def set_policy(self, exchange: str, endpoint: str, *, priority: int, target_interval: float) -> None:
        self.policies.setdefault(exchange, {})[endpoint] = EndpointPolicy(priority, target_interval)
        self.state.setdefault(exchange, ExState())

    def set_exchange_policy(self, exchange: str, *, max_rps: float, burst: int = 1) -> None:
        """取引所レベル（全エンドポイント合算）のレート制御を設定。"""
        if max_rps < 0:
            max_rps = 0.0
        if burst < 1:
            burst = 1
        self.ex_policy[exchange] = ExchangePolicy(max_rps=max_rps, burst=burst)
        st = self.state.setdefault(exchange, ExState())
        # 初期トークンは満タン（安定起動）
        st.tokens = float(burst)
        st.last_refill = self.now()

    # == 内部計算 ==

    def _cooldown_wait(self, ex: str) -> float:
        s = self.state.setdefault(ex, ExState())
        return max(0.0, s.cooldown_until - self.now())

    def _refill_tokens(self, ex: str) -> None:
        """トークンを max_rps に従いリフィル。"""
        pol = self.ex_policy.get(ex)
        if not pol or pol.max_rps <= 0.0:
            return  # バケット無効
        s = self.state.setdefault(ex, ExState())
        now = self.now()
        if s.last_refill == 0.0:
            s.last_refill = now
            return
        dt = max(0.0, now - s.last_refill)
        if dt <= 0:
            return
        # max_rps token/sec
        s.tokens = min(float(pol.burst), s.tokens + pol.max_rps * dt)
        s.last_refill = now

    def _bucket_wait(self, ex: str) -> float:
        """トークン不足時に必要な待機秒を返す。"""
        pol = self.ex_policy.get(ex)
        if not pol or pol.max_rps <= 0.0:
            return 0.0
        s = self.state.setdefault(ex, ExState())
        self._refill_tokens(ex)
        if s.tokens >= 1.0:
            return 0.0
        # 1 トークン貯まるまでの時間 = (1 - tokens) / max_rps
        need = 1.0 - s.tokens
        return need / pol.max_rps if pol.max_rps > 0 else 0.0

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

    # == パブリック I/F ==

    def request_permit(self, exchange: str, endpoint: str) -> Tuple[bool, int]:
        """実行許可の可否と待機ミリ秒を返す。"""
        now = self.now()

        # 429系クールダウン
        cd = self._cooldown_wait(exchange)
        if cd > 0:
            return False, int(cd * 1000)

        # endpoint SLA（最小インターバル）
        next_ep = self._next_allowed_at(exchange, endpoint)
        if now < next_ep:
            return False, int((next_ep - now) * 1000)

        # exchange バケット
        bw = self._bucket_wait(exchange)
        if bw > 0:
            return False, int(bw * 1000)

        # 許可：時刻更新 + トークン消費
        s = self.state.setdefault(exchange, ExState())
        s.last_at[endpoint] = now
        pol = self.ex_policy.get(exchange)
        if pol and pol.max_rps > 0.0:
            self._refill_tokens(exchange)
            # 十分にあるはずだが、念のため 0 未満にならないように
            s.tokens = max(0.0, s.tokens - 1.0)
        return True, 0

    def on_rate_limited(self, exchange: str, *, retry_after_sec: Optional[float] = None) -> None:
        """429/Retry-After 等のシグナルを受けたときに呼ぶ。"""
        s = self.state.setdefault(exchange, ExState())
        s.penalty = min(s.penalty + 1, 6)
        s.last_rate_limited_ts = self.now()
        if retry_after_sec and retry_after_sec > 0:
            s.cooldown_until = max(s.cooldown_until, self.now() + retry_after_sec)
        else:
            # 明示が無いときは指数バックオフ相当を反映
            s.cooldown_until = max(s.cooldown_until, self.now() + (1.6 ** s.penalty))

    def on_success(self, exchange: str) -> None:
        """成功が続いたら段階的に回復。"""
        s = self.state.setdefault(exchange, ExState())
        if s.penalty > 0 and (self.now() >= s.cooldown_until):
            s.penalty -= 1

    def get_exchange_state(self, exchange: str) -> Dict[str, Any]:
        """
        外部（collector_status / health 等）から参照するための、
        exchange 単位のレート制御状態スナップショットを返す。

        フィールド例:
            tokens           : 現在のトークン数（0〜burst）
            burst            : バースト許容量
            penalty          : ペナルティ段数（429 回数に応じて増加）
            cooldown_until   : クールダウン終了予定時刻（monotonic 秒）
            is_cooldown      : 現在クールダウン中かどうか
            last_rate_limited_ts : 直近で 429/Retry-After を受けた時刻（monotonic 秒）
            soft_limit       : 「レート制御中」とみなせるかどうかの簡易フラグ
                               （クールダウン中 / ペナルティあり / トークン不足のいずれか）
        """
        now = self.now()
        pol = self.ex_policy.get(exchange)
        s = self.state.setdefault(exchange, ExState())

        # トークンは最新の状態に更新してから参照する
        if pol and pol.max_rps > 0.0:
            self._refill_tokens(exchange)
        tokens = s.tokens
        burst = pol.burst if pol else 0

        is_cooldown = s.cooldown_until > now
        has_penalty = s.penalty > 0
        # max_rps が有効な場合のみ「トークン不足」を soft-limit 判定材料にする
        token_limited = bool(pol and pol.max_rps > 0.0 and tokens < 1.0)

        soft_limit = is_cooldown or has_penalty or token_limited

        return {
            "tokens": tokens,
            "burst": burst,
            "penalty": s.penalty,
            "cooldown_until": s.cooldown_until,
            "is_cooldown": is_cooldown,
            "last_rate_limited_ts": s.last_rate_limited_ts,
            "soft_limit": soft_limit,
        }

# 簡易セルフテスト（手動）
if __name__ == "__main__":
    rc = RateController()
    # exchange レベルのレート（5 rps, burst=2）
    rc.set_exchange_policy("bitflyer", max_rps=5, burst=2)
    # endpoint SLA
    rc.set_policy("bitflyer", "orderbook", priority=0, target_interval=0.2)
    rc.set_policy("bitflyer", "trades", priority=1, target_interval=0.5)

    import time as _t
    for i in range(6):
        ok, wait = rc.request_permit("bitflyer", "orderbook")
        print("OB", i, ok, wait)
        if not ok:
            _t.sleep(wait / 1000)

