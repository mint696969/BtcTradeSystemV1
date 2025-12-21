# path: ./btcts_next/src/btcts/collector/rate.py
# desc: 取引所ごとのレート制御（soft/hard/429緊急制御）を提供する。Scheduler から呼ばれ、Health には状態を提供する。

from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Dict, Optional, Tuple


@dataclass
class RatePolicy:
    """取引所ごとの制御方針。

    official_max_rps: 取引所公式の上限（rps）
    soft_ratio:      ここを超えたら WARN（= 計画的な減速を開始）
    hard_ratio:      ここを超えたら CRIT（= 強制的に最低限の収集へ落とす）
    burst_base_sec:  バースト許容量のベース秒（旧V1の概念を踏襲）

    注意: ratio は 0.0〜1.0（1.0 が 100%）。
    """

    official_max_rps: float
    soft_ratio: float = 0.8
    hard_ratio: float = 0.9
    burst_base_sec: float = 1.0


@dataclass
class RateState:
    """各取引所の動的状態（観測・表示用）。"""

    ts: float
    exchange: str
    mode: str  # NORMAL / WARN / CRIT
    eff_max_rps: float
    wait_ms: int
    last_429_ts: float = 0.0
    last_retry_after_sec: float = 0.0


class RateController:
    """取引所別の最大RPSを守りつつ、状況に応じて自動で抑制する。

    - NORMAL: eff_max_rps = official_max_rps * 1.0
    - WARN:   eff_max_rps = official_max_rps * soft_ratio
    - CRIT:   eff_max_rps = official_max_rps * hard_ratio

    429 / Retry-After を受けた場合は CRIT に落とし、一定時間は強制待機を入れる。
    """

    def __init__(self) -> None:
        self._policy: Dict[str, RatePolicy] = {}
        self._state: Dict[str, RateState] = {}
        self._next_allowed: Dict[str, float] = {}

    # ---- config -----------------------------------------------------------------

    def set_policy(self, exchange: str, policy: RatePolicy) -> None:
        ex = (exchange or "").strip()
        if not ex:
            raise ValueError("exchange is empty")
        if policy.official_max_rps <= 0:
            raise ValueError("official_max_rps must be > 0")
        self._policy[ex] = policy
        # init state
        if ex not in self._state:
            self._state[ex] = RateState(
                ts=time.time(),
                exchange=ex,
                mode="NORMAL",
                eff_max_rps=policy.official_max_rps,
                wait_ms=0,
            )
            self._next_allowed[ex] = 0.0

    def get_policy(self, exchange: str) -> Optional[RatePolicy]:
        return self._policy.get(exchange)

    def get_state(self, exchange: str) -> Optional[RateState]:
        return self._state.get(exchange)

    def snapshot(self) -> Dict[str, Dict]:
        """health/UI へ渡すための軽量スナップショット。"""
        out: Dict[str, Dict] = {}
        for ex, st in self._state.items():
            out[ex] = {
                "ts": st.ts,
                "exchange": st.exchange,
                "mode": st.mode,
                "eff_max_rps": st.eff_max_rps,
                "wait_ms": st.wait_ms,
                "last_429_ts": st.last_429_ts,
                "last_retry_after_sec": st.last_retry_after_sec,
            }
        return out

    # ---- scheduling --------------------------------------------------------------

    def acquire(self, exchange: str) -> Tuple[bool, int]:
        """1リクエスト分の実行許可を取得する。

        戻り値: (ok, wait_ms)
        - ok=True なら即実行してよい
        - ok=False なら wait_ms 待ってから再試行
        """
        ex = (exchange or "").strip()
        pol = self._policy.get(ex)
        if not pol:
            raise KeyError(f"policy not set: {ex}")

        now = time.time()
        next_ok = self._next_allowed.get(ex, 0.0)
        if now < next_ok:
            wait_ms = int((next_ok - now) * 1000)
            self._update_state(ex, wait_ms=wait_ms)
            return False, max(wait_ms, 1)

        # NORMAL モード前提の間隔（mode に応じて eff_max_rps は変わる）
        st = self._state[ex]
        interval = 1.0 / max(st.eff_max_rps, 0.0001)
        self._next_allowed[ex] = now + interval
        self._update_state(ex, wait_ms=0)
        return True, 0

    def on_429(self, exchange: str, retry_after_sec: float = 0.0) -> None:
        """429 を受けた場合の緊急制御。"""
        ex = (exchange or "").strip()
        pol = self._policy.get(ex)
        if not pol:
            return
        now = time.time()
        st = self._state.get(ex)
        if not st:
            return
        # CRIT に落とす
        st.mode = "CRIT"
        st.eff_max_rps = max(pol.official_max_rps * pol.hard_ratio, 0.1)
        st.last_429_ts = now
        st.last_retry_after_sec = max(retry_after_sec, 0.0)
        st.ts = now

        # Retry-After があればそれを優先して待機、無ければ短い待機を入れる
        hold = st.last_retry_after_sec if st.last_retry_after_sec > 0 else 2.0
        self._next_allowed[ex] = max(self._next_allowed.get(ex, 0.0), now + hold)

    def set_mode_by_util(self, exchange: str, util_ratio: float) -> str:
        """外部観測（利用率）から mode を更新する。

        util_ratio: 0.0〜1.0（1.0=100%）
        戻り値: mode
        """
        ex = (exchange or "").strip()
        pol = self._policy.get(ex)
        st = self._state.get(ex)
        if not pol or not st:
            return "UNKNOWN"

        now = time.time()
        # 429 直後は CRIT を維持（一定秒は解除しない）
        if st.last_429_ts and (now - st.last_429_ts) < 10.0:
            st.ts = now
            return st.mode

        if util_ratio >= pol.hard_ratio:
            st.mode = "CRIT"
            st.eff_max_rps = max(pol.official_max_rps * pol.hard_ratio, 0.1)
        elif util_ratio >= pol.soft_ratio:
            st.mode = "WARN"
            st.eff_max_rps = max(pol.official_max_rps * pol.soft_ratio, 0.1)
        else:
            st.mode = "NORMAL"
            st.eff_max_rps = pol.official_max_rps

        st.ts = now
        return st.mode

    # ---- internal ---------------------------------------------------------------

    def _update_state(self, ex: str, *, wait_ms: int) -> None:
        st = self._state.get(ex)
        if not st:
            return
        st.ts = time.time()
        st.wait_ms = int(wait_ms)
