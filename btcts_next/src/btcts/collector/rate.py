# path: ./btcts_next/src/btcts/collector/rate.py
# desc: 取引所ごとのレート制御（soft/hard/429緊急制御）を提供する。Scheduler から呼ばれ、Health には状態を提供する。

from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Dict, Optional, Tuple
from typing import Any


@dataclass
class RatePolicy:
    """取引所ごとの制御方針。

    official_max_rps: 取引所公式の上限（rps）
    soft_ratio:      ここを超えたら WARN（= 計画的な減速を開始）
    hard_ratio:      ここを超えたら CRIT（= 強制的に最低限の収集へ落とす）
    ※ Phase1では soft_ratio / hard_ratio は閾値・capとしては使用しない（互換保持のみ）。
       閾値は rate_control.yaml の warn_util / crit_util、cap は warn_cap / crit_cap が正。
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

@dataclass
class CommonRateControl:
    """rate_control.yaml の共通ポリシー（Phase1）。"""

    util_window_warn_sec: float = 10.0
    util_window_clear_sec: float = 30.0

    warn_util: float = 0.90
    warn_clear_util: float = 0.85
    crit_util: float = 0.98

    warn_cap: float = 0.80
    crit_cap: float = 0.50

    floor_rps: float = 0.10

    crit_backoff_initial_sec: float = 2.0
    crit_backoff_max_sec: float = 30.0
    crit_hold_min_sec: float = 10.0
    no_429_for_sec: float = 60.0


class RateController:
    """取引所別の最大RPSを守りつつ、状況に応じて自動で抑制する（Phase1）。

    - 取引所固有: RatePolicy.official_max_rps（公式上限）
    - 共通ポリシー: rate_control.yaml（閾値/cap/floor/backoff）

    mode と eff_max_rps:
    - NORMAL: eff_max_rps = official_max_rps
    - WARN:   eff_max_rps = max(official_max_rps * warn_cap, floor_rps)
    - CRIT:   eff_max_rps = max(official_max_rps * crit_cap, floor_rps)

    429 / Retry-After を受けた場合は CRIT に落とし、
    Retry-After 優先で hold、無ければ backoff（指数増加）を適用する。
    """

    def __init__(self) -> None:
        self._policy: Dict[str, RatePolicy] = {}
        self._state: Dict[str, RateState] = {}
        self._next_allowed: Dict[str, float] = {}

        # Phase1: rate_control.yaml の共通ポリシー（Scheduler/main が注入）
        self._common: CommonRateControl = CommonRateControl()
        self._crit_backoff_sec: Dict[str, float] = {}  # exchange単位の backoff 状態

    # ---- config -----------------------------------------------------------------

    def set_common_policy(self, cfg: Dict[str, Any]) -> None:
        """rate_control.yaml の共通ポリシーを注入する（Phase1）。"""
        if not isinstance(cfg, dict):
            return

        c = self._common
        # window
        c.util_window_warn_sec = float(cfg.get("util_window_warn_sec", c.util_window_warn_sec))
        c.util_window_clear_sec = float(cfg.get("util_window_clear_sec", c.util_window_clear_sec))

        # thresholds (util)
        c.warn_util = float(cfg.get("warn_util", c.warn_util))
        c.warn_clear_util = float(cfg.get("warn_clear_util", c.warn_clear_util))
        c.crit_util = float(cfg.get("crit_util", c.crit_util))

        # caps
        c.warn_cap = float(cfg.get("warn_cap", c.warn_cap))
        c.crit_cap = float(cfg.get("crit_cap", c.crit_cap))

        # floor
        c.floor_rps = float(cfg.get("floor_rps", c.floor_rps))

        # backoff/hold
        c.crit_backoff_initial_sec = float(cfg.get("crit_backoff_initial_sec", c.crit_backoff_initial_sec))
        c.crit_backoff_max_sec = float(cfg.get("crit_backoff_max_sec", c.crit_backoff_max_sec))
        c.crit_hold_min_sec = float(cfg.get("crit_hold_min_sec", c.crit_hold_min_sec))
        c.no_429_for_sec = float(cfg.get("no_429_for_sec", c.no_429_for_sec))

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
        now = time.time()
        items: Dict[str, Dict] = {}
        for ex, st in self._state.items():
            items[ex] = {
                "ts": st.ts,
                "exchange": st.exchange,
                "mode": st.mode,
                "eff_max_rps": st.eff_max_rps,
                "wait_ms": st.wait_ms,
                "last_429_ts": st.last_429_ts,
                "last_retry_after_sec": st.last_retry_after_sec,
            }
        return {"ts": now, "items": items}

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
        # Phase1: floor_rps を確実に守る（完全停止回避）
        eff = max(float(st.eff_max_rps), float(self._common.floor_rps), 0.0001)
        interval = 1.0 / eff
        self._next_allowed[ex] = now + interval
        self._update_state(ex, wait_ms=0)
        return True, 0

    def on_429(self, exchange: str, retry_after_sec: float = 0.0) -> None:
        """429 を受けた場合の緊急制御（Phase1: 共通ポリシー準拠）。"""
        ex = (exchange or "").strip()
        pol = self._policy.get(ex)
        st = self._state.get(ex)
        if not pol or not st:
            return

        c = self._common
        now = time.time()

        # CRIT に落とす（capは共通ポリシー、floorを適用）
        st.mode = "CRIT"
        st.eff_max_rps = max(pol.official_max_rps * float(c.crit_cap), float(c.floor_rps))
        st.last_429_ts = now
        st.last_retry_after_sec = max(float(retry_after_sec), 0.0)
        st.ts = now

        # backoff（Retry-After優先、無ければ指数的に増やす）
        if st.last_retry_after_sec > 0.0:
            hold = st.last_retry_after_sec
            self._crit_backoff_sec[ex] = float(c.crit_backoff_initial_sec)
        else:
            cur = float(self._crit_backoff_sec.get(ex, c.crit_backoff_initial_sec) or c.crit_backoff_initial_sec)
            hold = cur
            nxt = min(cur * 2.0, float(c.crit_backoff_max_sec))
            self._crit_backoff_sec[ex] = nxt

        # 最低holdを保証
        hold = max(float(hold), float(c.crit_hold_min_sec))

        self._next_allowed[ex] = max(self._next_allowed.get(ex, 0.0), now + hold)

    def set_mode_by_util(self, exchange: str, util_ratio: float) -> str:
        """外部観測（利用率）から mode を更新する（Phase1: 共通ポリシー準拠）。"""
        ex = (exchange or "").strip()
        pol = self._policy.get(ex)
        st = self._state.get(ex)
        if not pol or not st:
            return "UNKNOWN"

        c = self._common
        now = time.time()

        # 429 直後は一定期間 CRIT 維持（no_429_for_sec を満たすまで復帰しない）
        if st.last_429_ts and (now - st.last_429_ts) < float(c.no_429_for_sec):
            st.ts = now
            return st.mode

        u = max(0.0, min(1.0, float(util_ratio)))

        # CRIT判定（閾値は crit_util）
        if u >= float(c.crit_util):
            st.mode = "CRIT"
            st.eff_max_rps = max(pol.official_max_rps * float(c.crit_cap), float(c.floor_rps))
            st.ts = now
            return st.mode

        # WARN判定（ヒステリシス：WARN中は warn_clear_util まで落ちないと戻らない）
        if st.mode == "WARN":
            if u <= float(c.warn_clear_util):
                st.mode = "NORMAL"
                st.eff_max_rps = pol.official_max_rps
            else:
                st.mode = "WARN"
                st.eff_max_rps = max(pol.official_max_rps * float(c.warn_cap), float(c.floor_rps))
            st.ts = now
            return st.mode

        if u >= float(c.warn_util):
            st.mode = "WARN"
            st.eff_max_rps = max(pol.official_max_rps * float(c.warn_cap), float(c.floor_rps))
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
