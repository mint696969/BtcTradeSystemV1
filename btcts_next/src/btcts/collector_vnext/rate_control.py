# path: ./btcts_next/src/btcts/collector_vnext/rate_control.py
# desc: Collector vNext 用のレート制御（soft/hard/429緊急制御）を提供する。

from __future__ import annotations

import os
import time
from dataclasses import dataclass
from typing import Any, Dict, Optional, Tuple

from btcts.core import audit


@dataclass
class RatePolicy:
    """取引所ごとの制御方針。

    official_max_rps: 取引所公式の上限（rps）
    soft_ratio:      ここを超えたら WARN（互換保持用）
    hard_ratio:      ここを超えたら CRIT（互換保持用）
    burst_base_sec:  バースト許容量のベース秒（旧V1の概念を踏襲）
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
    reason: str = ""


@dataclass
class CommonRateControl:
    """rate_control.yaml の共通ポリシー。"""

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
    """取引所別の最大RPSを守りつつ、状況に応じて自動で抑制する。

    - 取引所固有: RatePolicy.official_max_rps
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

        self._common: CommonRateControl = CommonRateControl()
        self._crit_backoff_sec: Dict[str, float] = {}

    # ------------------------------------------------------------------
    # helpers
    # ------------------------------------------------------------------

    def _audit_mode(self) -> str:
        return (os.environ.get("BTC_TS_MODE", "") or "NORMAL").strip().upper()

    def _emit_rate_event(
        self,
        event: str,
        *,
        exchange: str,
        prev_mode: str = "",
        new_mode: str = "",
        reason: str = "",
        level: str = "INFO",
        extra: Optional[Dict[str, Any]] = None,
    ) -> None:
        payload: Dict[str, Any] = {
            "exchange": exchange,
            "prev_mode": prev_mode,
            "new_mode": new_mode,
            "reason": reason,
        }
        if extra:
            payload.update(extra)
        audit.emit(event, feature="collector_vnext", level=level, payload=payload)

    def _set_mode(
        self,
        ex: str,
        *,
        new_mode: str,
        eff_max_rps: float,
        reason: str,
        extra: Optional[Dict[str, Any]] = None,
    ) -> str:
        st = self._state.get(ex)
        if not st:
            return "UNKNOWN"

        prev_mode = st.mode
        prev_reason = st.reason

        st.mode = new_mode
        st.eff_max_rps = eff_max_rps
        st.reason = reason
        st.ts = time.time()

        # 重要イベントは全モードで必ず出す
        if prev_mode != new_mode:
            if new_mode == "NORMAL" and prev_mode in ("WARN", "CRIT"):
                self._emit_rate_event(
                    "rate_control.released",
                    exchange=ex,
                    prev_mode=prev_mode,
                    new_mode=new_mode,
                    reason=reason,
                    level="INFO",
                    extra=extra,
                )
            else:
                self._emit_rate_event(
                    "rate_control.engaged",
                    exchange=ex,
                    prev_mode=prev_mode,
                    new_mode=new_mode,
                    reason=reason,
                    level="INFO",
                    extra=extra,
                )
        else:
            # modeは同じでも理由が変わったら DEBUG/BOOST では見たい
            if prev_reason != reason and self._audit_mode() in ("DEBUG", "BOOST"):
                self._emit_rate_event(
                    "rate_control.reason",
                    exchange=ex,
                    prev_mode=prev_mode,
                    new_mode=new_mode,
                    reason=reason,
                    level="DEBUG",
                    extra=extra,
                )

        return st.mode

    def _current_eff(self, ex: str) -> float:
        st = self._state.get(ex)
        if not st:
            return 0.0
        return float(st.eff_max_rps)

    # ------------------------------------------------------------------
    # public config
    # ------------------------------------------------------------------

    def has_policy(self, exchange: str) -> bool:
        ex = (exchange or "").strip().lower()
        return bool(ex) and (ex in self._policy)

    def set_common_policy(self, cfg: Dict[str, Any]) -> None:
        """rate_control.yaml の共通ポリシーを注入する。"""
        if not isinstance(cfg, dict):
            return

        c = self._common
        c.util_window_warn_sec = float(cfg.get("util_window_warn_sec", c.util_window_warn_sec))
        c.util_window_clear_sec = float(cfg.get("util_window_clear_sec", c.util_window_clear_sec))

        c.warn_util = float(cfg.get("warn_util", c.warn_util))
        c.warn_clear_util = float(cfg.get("warn_clear_util", c.warn_clear_util))
        c.crit_util = float(cfg.get("crit_util", c.crit_util))

        c.warn_cap = float(cfg.get("warn_cap", c.warn_cap))
        c.crit_cap = float(cfg.get("crit_cap", c.crit_cap))

        c.floor_rps = float(cfg.get("floor_rps", c.floor_rps))

        c.crit_backoff_initial_sec = float(cfg.get("crit_backoff_initial_sec", c.crit_backoff_initial_sec))
        c.crit_backoff_max_sec = float(cfg.get("crit_backoff_max_sec", c.crit_backoff_max_sec))
        c.crit_hold_min_sec = float(cfg.get("crit_hold_min_sec", c.crit_hold_min_sec))
        c.no_429_for_sec = float(cfg.get("no_429_for_sec", c.no_429_for_sec))

    def set_policy(self, exchange: str, policy: RatePolicy) -> None:
        ex = (exchange or "").strip().lower()
        if not ex:
            raise ValueError("exchange is empty")
        if policy.official_max_rps <= 0:
            raise ValueError("official_max_rps must be > 0")

        self._policy[ex] = policy
        if ex not in self._state:
            self._state[ex] = RateState(
                ts=time.time(),
                exchange=ex,
                mode="NORMAL",
                eff_max_rps=policy.official_max_rps,
                wait_ms=0,
                reason="policy_initialized",
            )
            self._next_allowed[ex] = 0.0

    def get_policy(self, exchange: str) -> Optional[RatePolicy]:
        ex = (exchange or "").strip().lower()
        return self._policy.get(ex)

    def get_state(self, exchange: str) -> Optional[RateState]:
        ex = (exchange or "").strip().lower()
        return self._state.get(ex)

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
                "reason": st.reason,
            }
        return {"ts": now, "items": items}

    # ------------------------------------------------------------------
    # scheduling
    # ------------------------------------------------------------------

    def acquire(self, exchange: str) -> Tuple[bool, int]:
        """1リクエスト分の実行許可を取得する。

        戻り値: (ok, wait_ms)
        - ok=True なら即実行してよい
        - ok=False なら wait_ms 待ってから再試行
        """
        ex = (exchange or "").strip().lower()
        pol = self._policy.get(ex)
        if not pol:
            raise KeyError(f"policy not set: {ex}")

        now = time.time()
        next_ok = self._next_allowed.get(ex, 0.0)
        if now < next_ok:
            wait_ms = int((next_ok - now) * 1000)
            self._update_state(ex, wait_ms=wait_ms)

            # BOOST だけ acquire待ちを細かく観測
            if self._audit_mode() == "BOOST":
                self._emit_rate_event(
                    "rate_control.acquire_delayed",
                    exchange=ex,
                    prev_mode=self._state[ex].mode,
                    new_mode=self._state[ex].mode,
                    reason=self._state[ex].reason,
                    level="DEBUG",
                    extra={"wait_ms": max(wait_ms, 1)},
                )
            return False, max(wait_ms, 1)

        st = self._state[ex]
        eff = max(float(st.eff_max_rps), float(self._common.floor_rps), 0.0001)
        interval = 1.0 / eff
        self._next_allowed[ex] = now + interval
        self._update_state(ex, wait_ms=0)
        return True, 0

    def on_429(self, exchange: str, retry_after_sec: float = 0.0) -> None:
        """429 を受けた場合の緊急制御。"""
        ex = (exchange or "").strip().lower()
        pol = self._policy.get(ex)
        st = self._state.get(ex)
        if not pol or not st:
            return

        c = self._common
        now = time.time()

        eff = max(pol.official_max_rps * float(c.crit_cap), float(c.floor_rps))

        if retry_after_sec > 0.0:
            hold = float(retry_after_sec)
            self._crit_backoff_sec[ex] = float(c.crit_backoff_initial_sec)
            reason = "retry_after_header"
        else:
            cur = float(self._crit_backoff_sec.get(ex, c.crit_backoff_initial_sec) or c.crit_backoff_initial_sec)
            hold = cur
            nxt = min(cur * 2.0, float(c.crit_backoff_max_sec))
            self._crit_backoff_sec[ex] = nxt
            reason = "http_429"

            if self._audit_mode() in ("DEBUG", "BOOST"):
                self._emit_rate_event(
                    "rate_control.backoff_changed",
                    exchange=ex,
                    prev_mode=st.mode,
                    new_mode="CRIT",
                    reason="http_429_backoff",
                    level="DEBUG",
                    extra={"prev_backoff_sec": cur, "next_backoff_sec": nxt},
                )

        hold = max(float(hold), float(c.crit_hold_min_sec))
        self._next_allowed[ex] = max(self._next_allowed.get(ex, 0.0), now + hold)

        st.last_429_ts = now
        st.last_retry_after_sec = max(float(retry_after_sec), 0.0)

        extra: Dict[str, Any] = {
            "retry_after_sec": st.last_retry_after_sec,
            "hold_sec": hold,
        }
        if self._audit_mode() in ("DEBUG", "BOOST"):
            extra["eff_max_rps"] = eff
            extra["floor_rps"] = float(c.floor_rps)

        self._set_mode(
            ex,
            new_mode="CRIT",
            eff_max_rps=eff,
            reason=reason,
            extra=extra,
        )

        # hold開始の事実は DEBUG/BOOST で追加観測
        if self._audit_mode() in ("DEBUG", "BOOST"):
            self._emit_rate_event(
                "rate_control.hold_started",
                exchange=ex,
                prev_mode=st.mode,
                new_mode=st.mode,
                reason=reason,
                level="DEBUG",
                extra={"hold_sec": hold},
            )

    def set_mode_by_util(self, exchange: str, util_ratio: float) -> str:
        """外部観測（利用率）から mode を更新する。"""
        ex = (exchange or "").strip().lower()
        pol = self._policy.get(ex)
        st = self._state.get(ex)
        if not pol or not st:
            return "UNKNOWN"

        c = self._common
        now = time.time()
        u = max(0.0, min(1.0, float(util_ratio)))

        # DEBUG/BOOST では util 観測を残しておく
        if self._audit_mode() in ("DEBUG", "BOOST"):
            self._emit_rate_event(
                "rate_control.util_observed",
                exchange=ex,
                prev_mode=st.mode,
                new_mode=st.mode,
                reason="util_sampled",
                level="DEBUG",
                extra={
                    "util_ratio": u,
                    "warn_util": float(c.warn_util),
                    "warn_clear_util": float(c.warn_clear_util),
                    "crit_util": float(c.crit_util),
                },
            )

        # 429直後は一定期間 CRIT 維持
        if st.last_429_ts and (now - st.last_429_ts) < float(c.no_429_for_sec):
            st.ts = now
            st.reason = "cooldown_after_429"

            if self._audit_mode() in ("DEBUG", "BOOST"):
                self._emit_rate_event(
                    "rate_control.reason",
                    exchange=ex,
                    prev_mode=st.mode,
                    new_mode=st.mode,
                    reason="cooldown_after_429",
                    level="DEBUG",
                    extra={
                        "elapsed_since_429_sec": now - st.last_429_ts,
                        "no_429_for_sec": float(c.no_429_for_sec),
                    },
                )
            return st.mode

        # CRIT
        if u >= float(c.crit_util):
            eff = max(pol.official_max_rps * float(c.crit_cap), float(c.floor_rps))
            return self._set_mode(
                ex,
                new_mode="CRIT",
                eff_max_rps=eff,
                reason="crit_util_threshold",
                extra={
                    "util_ratio": u,
                    "threshold": float(c.crit_util),
                    "eff_max_rps": eff,
                } if self._audit_mode() in ("DEBUG", "BOOST") else None,
            )

        # WARN中のヒステリシス
        if st.mode == "WARN":
            if u <= float(c.warn_clear_util):
                return self._set_mode(
                    ex,
                    new_mode="NORMAL",
                    eff_max_rps=pol.official_max_rps,
                    reason="recovered_below_warn_clear_util",
                    extra={
                        "util_ratio": u,
                        "threshold": float(c.warn_clear_util),
                    } if self._audit_mode() in ("DEBUG", "BOOST") else None,
                )
            eff = max(pol.official_max_rps * float(c.warn_cap), float(c.floor_rps))
            return self._set_mode(
                ex,
                new_mode="WARN",
                eff_max_rps=eff,
                reason="warn_hysteresis_hold",
                extra={
                    "util_ratio": u,
                    "warn_clear_util": float(c.warn_clear_util),
                    "eff_max_rps": eff,
                } if self._audit_mode() in ("DEBUG", "BOOST") else None,
            )

        # WARN入り
        if u >= float(c.warn_util):
            eff = max(pol.official_max_rps * float(c.warn_cap), float(c.floor_rps))
            return self._set_mode(
                ex,
                new_mode="WARN",
                eff_max_rps=eff,
                reason="warn_util_threshold",
                extra={
                    "util_ratio": u,
                    "threshold": float(c.warn_util),
                    "eff_max_rps": eff,
                } if self._audit_mode() in ("DEBUG", "BOOST") else None,
            )

        # NORMAL
        return self._set_mode(
            ex,
            new_mode="NORMAL",
            eff_max_rps=pol.official_max_rps,
            reason="normal_util_range",
            extra={
                "util_ratio": u,
                "eff_max_rps": pol.official_max_rps,
            } if self._audit_mode() in ("DEBUG", "BOOST") else None,
        )

    # ------------------------------------------------------------------
    # internal
    # ------------------------------------------------------------------

    def _update_state(self, ex: str, *, wait_ms: int) -> None:
        st = self._state.get(ex)
        if not st:
            return
        prev_wait = int(st.wait_ms or 0)
        st.ts = time.time()
        st.wait_ms = int(wait_ms)

        # hold終了の事実は DEBUG/BOOST だけで拾う
        if prev_wait > 0 and st.wait_ms == 0 and self._audit_mode() in ("DEBUG", "BOOST"):
            self._emit_rate_event(
                "rate_control.hold_finished",
                exchange=ex,
                prev_mode=st.mode,
                new_mode=st.mode,
                reason=st.reason or "wait_cleared",
                level="DEBUG",
                extra={"prev_wait_ms": prev_wait},
            )