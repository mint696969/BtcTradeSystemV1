# path: ./btcts_next/src/btcts/collector/scheduler.py
# desc: RateController に従って endpoint runner を実行する最小スケジューラ。
#       status.json には必ず items(list) を書き出す。

from __future__ import annotations

import time
from datetime import datetime, timezone
from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Optional, Tuple

from btcts.core import audit
from .rate import RateController, RatePolicy
from .status import CollectorStatus, write_rate_state, write_status


Runner = Callable[[], None]


@dataclass
class Endpoint:
    exchange: str
    endpoint: str
    priority: int
    target_interval: float
    runner: Runner

@dataclass
class EndpointState:
    last_ok_ts: float = 0.0      # 最後に「成功」した時刻（time.time）
    last_try_ts: float = 0.0     # 最後に「試行」した時刻（成功/失敗問わず）
    retries: int = 0             # 直近の失敗回数（成功で0に戻す）
    cause: Optional[str] = None  # 例: never_ok / error / rate_limited など
    notes: Optional[str] = None  # 短い補足（例外型など）


class Scheduler:
    """RateController で許可されたタイミングで runner を実行する最小スケジューラ。"""

    def __init__(self, rc: Optional[RateController] = None) -> None:
        self.rc = rc or RateController()
        self.table: Dict[Tuple[str, str], Endpoint] = {}
        self.keys: List[Tuple[str, str]] = []

        # 成功時刻（互換のため残す：status の last_ok はこれを元に作る）
        self._last_run: Dict[Tuple[str, str], float] = {}

        # endpoint 状態（失敗回数/原因などを status に反映する）
        self._state: Dict[Tuple[str, str], EndpointState] = {}

        # “never_ok の age_sec” を意味ある値にするための基準時刻
        self._started_at: float = time.time()

        self._stop: bool = False

    # ---- setup --------------------------------------------------------------

    def set_policy(self, exchange: str, policy: RatePolicy) -> None:
        self.rc.set_policy(exchange, policy)

    def add(self, ep: Endpoint) -> None:
        key = (ep.exchange, ep.endpoint)
        self.table[key] = ep
        if key not in self.keys:
            self.keys.append(key)

        self._last_run.setdefault(key, 0.0)
        self._state.setdefault(key, EndpointState(cause="never_ok"))

    def stop(self) -> None:
        self._stop = True

    # ---- status helpers -----------------------------------------------------

    def _build_status_items(self, now: float) -> List[dict]:
        items: List[dict] = []

        for (ex, epname), ep in self.table.items():
            key = (ex, epname)
            st = self._state.get(key) or EndpointState(cause="never_ok")

            last_ok_ts = float(self._last_run.get(key, 0.0) or 0.0)
            if last_ok_ts > 0.0:
                age = max(0.0, now - last_ok_ts)
                last_ok = (
                    datetime.fromtimestamp(last_ok_ts, tz=timezone.utc)
                    .replace(microsecond=0)
                    .isoformat()
                    .replace("+00:00", "Z")
                )
                cause = st.cause  # 成功後は通常 None にする運用
            else:
                # “never_ok” は 1e9 のようなダミー値にせず、起動後の経過秒にする
                age = max(0.0, now - float(self._started_at or now))
                last_ok = None
                cause = st.cause or "never_ok"

            items.append(
                {
                    "exchange": ex,
                    "topic": epname,
                    "last_ok": last_ok,
                    "age_sec": float(age),
                    "cause": cause,
                    "retries": int(st.retries or 0),
                    "notes": st.notes,
                }
            )

        items.sort(key=lambda d: (d["exchange"], d["topic"]))
        return items

    # ---- loop ---------------------------------------------------------------

    def run_forever(
        self,
        *,
        tick_sec: float = 0.05,
        rate_state_every_sec: float = 1.0,
        status_every_sec: float = 2.0,
    ) -> None:
        now0 = time.time()
        write_status(
            CollectorStatus(
                ts=now0,
                mode="RUNNING",
                message="scheduler started",
                items=self._build_status_items(now0),
            )
        )

        last_rate = 0.0
        last_status = 0.0

        while not self._stop:
            now = time.time()

            # rate_state
            if (now - last_rate) >= rate_state_every_sec:
                try:
                    write_rate_state(self.rc.snapshot(), emit_audit=False)
                except Exception as e:
                    audit.emit(
                        "collector.rate_state.error",
                        feature="collector",
                        level="WARN",
                        payload={"err": str(e)},
                    )
                last_rate = now

            # status
            if (now - last_status) >= status_every_sec:
                try:
                    write_status(
                        CollectorStatus(
                            ts=now,
                            mode="RUNNING",
                            message=f"scheduler running endpoints={len(self.table)}",
                            items=self._build_status_items(now),
                        ),
                        emit_audit=False,
                    )
                except Exception as e:
                    audit.emit(
                        "collector.status.error",
                        feature="collector",
                        level="WARN",
                        payload={"err": str(e)},
                    )
                last_status = now

            # endpoint run
            keys = sorted(self.keys, key=lambda k: self.table[k].priority, reverse=True)
            did_work = False

            for key in keys:
                ep = self.table.get(key)
                if not ep:
                    continue

                last = self._last_run.get(key, 0.0)
                if (now - last) < max(ep.target_interval, 0.0):
                    continue

                ok, wait_ms = self.rc.acquire(ep.exchange)
                if not ok:
                    time.sleep(min(wait_ms / 1000.0, 0.25))
                    continue

                st = self._state.setdefault(key, EndpointState(cause="never_ok"))
                st.last_try_ts = now

                try:
                    ep.runner()

                    ok_ts = time.time()
                    self._last_run[key] = ok_ts

                    # 成功：失敗状態をクリア
                    st.last_ok_ts = ok_ts
                    st.retries = 0
                    st.cause = None
                    st.notes = None

                    did_work = True

                except Exception as e:
                    st.retries = int(st.retries or 0) + 1
                    st.cause = "error"
                    st.notes = f"{type(e).__name__}: {e}"

                    audit.emit(
                        "collector.endpoint.error",
                        feature="collector",
                        level="WARN",
                        payload={
                            "exchange": ep.exchange,
                            "endpoint": ep.endpoint,
                            "err": str(e),
                            "err_type": type(e).__name__,
                            "retries": st.retries,
                        },
                    )

            if not did_work:
                time.sleep(tick_sec)

        write_status(
            CollectorStatus(
                ts=time.time(),
                mode="STOPPED",
                message="scheduler stopped",
                items=[],
            )
        )
