# path: ./btcts_next/src/btcts/collector/scheduler.py
# desc: RateController に従って endpoint runner を実行する最小スケジューラ。
#       status.json には必ず items(list) を書き出す。

from __future__ import annotations

import time
from datetime import datetime, timezone
from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Optional, Tuple
from collections import defaultdict, deque

from btcts.core import audit
from .rate import RateController, RatePolicy
from .status import CollectorStatus, write_rate_state, write_status


Runner = Callable[[], None]
class EndpointSkipped(Exception):
    """Endpoint が仕様的に実行不能/未対応であることを示す（成功扱いにしない）。"""
    def __init__(self, reason: str = "skipped", hint: str = "") -> None:
        super().__init__(reason)
        self.reason = reason
        self.hint = hint


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

        self._last_any_ok_ts: float = 0.0  # 全endpointで最後に成功した時刻（0.0=未成功）
        self._stop: bool = False
        # ---- Phase1: rate_control(util/WARN) --------------------------------
        # 送信回数の rolling window（exchange 単位）
        self._req_ts_10s: Dict[str, deque[float]] = defaultdict(deque)
        self._req_ts_30s: Dict[str, deque[float]] = defaultdict(deque)

        # util 計算と mode 監査の周期制御
        self._last_util_calc_ts: float = 0.0
        self._last_mode_by_ex: Dict[str, str] = {}          # collector.rate.mode 用
        self._last_hold_audit_ts: Dict[str, float] = {}     # collector.rate.hold のスパム抑制用

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

    def _build_rate_control_summary(self) -> Dict[str, Any]:
        """status.json に載せる rate_control 要約を作る。"""
        try:
            snap = self.rc.snapshot() or {}
            items = (snap.get("items") or {}) if isinstance(snap, dict) else {}
        except Exception:
            items = {}

        if not isinstance(items, dict) or not items:
            return {
                "summary_state": "NORMAL",
                "engaged": False,
                "last_reason": "",
                "last_changed_at": "",
                "items": [],
            }

        # CRIT > WARN > NORMAL の順で代表状態を決める
        summary_state = "NORMAL"
        engaged = False
        last_reason = ""
        last_changed_at = ""
        out_items: List[Dict[str, Any]] = []

        best_rank = -1
        rank_map = {"NORMAL": 0, "WARN": 1, "CRIT": 2}

        for ex, st in items.items():
            if not isinstance(st, dict):
                continue

            mode = str(st.get("mode") or "NORMAL").upper()
            reason = str(st.get("reason") or "")
            ts = float(st.get("ts") or 0.0)

            out_items.append(
                {
                    "exchange": str(st.get("exchange") or ex),
                    "mode": mode,
                    "reason": reason,
                    "eff_max_rps": float(st.get("eff_max_rps") or 0.0),
                    "wait_ms": int(st.get("wait_ms") or 0),
                    "last_429_ts": float(st.get("last_429_ts") or 0.0),
                    "last_retry_after_sec": float(st.get("last_retry_after_sec") or 0.0),
                }
            )

            rank = rank_map.get(mode, 0)
            if rank > 0:
                engaged = True

            if rank > best_rank:
                best_rank = rank
                summary_state = mode
                last_reason = reason
                last_changed_at = (
                    datetime.fromtimestamp(ts, tz=timezone.utc)
                    .replace(microsecond=0)
                    .isoformat()
                    .replace("+00:00", "Z")
                    if ts > 0.0
                    else ""
                )

        out_items.sort(key=lambda d: d["exchange"])
        return {
            "summary_state": summary_state,
            "engaged": engaged,
            "last_reason": last_reason,
            "last_changed_at": last_changed_at,
            "items": out_items,
        }
    
    # ---- rate_control helpers ---------------------------------------------

    def _rate_control_cfg(self) -> Dict[str, Any]:
        # main.py が注入する（未注入でも安全側デフォルト）
        return getattr(self, "_btcts_rate_control_cfg", {}) or {}

    def _trim_deque(self, q: deque[float], now: float, window_sec: float) -> None:
        cut = now - float(window_sec)
        while q and q[0] < cut:
            q.popleft()

    def _note_request_sent(self, exchange: str, now: float) -> None:
        cfg = self._rate_control_cfg()
        w10 = float(cfg.get("util_window_warn_sec", 10.0))
        w30 = float(cfg.get("util_window_clear_sec", 30.0))

        q10 = self._req_ts_10s[exchange]
        q30 = self._req_ts_30s[exchange]
        q10.append(now)
        q30.append(now)
        self._trim_deque(q10, now, w10)
        self._trim_deque(q30, now, w30)

    def _calc_util_10s(self, exchange: str, eff_max_rps: float, now: float) -> float:
        cfg = self._rate_control_cfg()
        w10 = float(cfg.get("util_window_warn_sec", 10.0))

        q10 = self._req_ts_10s[exchange]
        self._trim_deque(q10, now, w10)
        denom = max(float(eff_max_rps) * w10, 1e-9)
        return min(1.0, max(0.0, float(len(q10)) / denom))

    # ---- loop ---------------------------------------------------------------

    def run_forever(
        self,
        *,
        tick_sec: float = 0.05,
        rate_state_every_sec: float = 1.0,
        status_every_sec: float = 2.0,
        startup_grace_sec: float = 30.0,
        no_data_check_every_sec: float = 1.0,
    ) -> None:

        now0 = time.time()
        write_status(
            CollectorStatus(
                ts=now0,
                mode="RUNNING",
                message="scheduler started",
                items=self._build_status_items(now0),
                last_heartbeat=(
                    datetime.fromtimestamp(now0, tz=timezone.utc)
                    .replace(microsecond=0)
                    .isoformat()
                    .replace("+00:00", "Z")
                ),
                rate_control=self._build_rate_control_summary(),
            )
        )

        last_rate = 0.0
        last_status = 0.0

        while not self._stop:
            now = time.time()

            # 起動後に一度も成功しない（=データが1件も取れていない）状態を検知して停止する
            # “動いてる風”が最も危険なので、早期にERRORへ寄せる。
            # チェック頻度は no_data_check_every_sec に従う。
            if not hasattr(self, "_last_no_data_check_ts"):
                self._last_no_data_check_ts = 0.0  # type: ignore[attr-defined]

            if (now - float(self._last_no_data_check_ts)) >= no_data_check_every_sec:  # type: ignore[attr-defined]
                self._last_no_data_check_ts = now  # type: ignore[attr-defined]

                if self._last_any_ok_ts <= 0.0 and (now - self._started_at) >= startup_grace_sec:
                    audit.emit(
                        "collector.no_data",
                        feature="collector",
                        level="CRIT",
                        payload={
                            "startup_grace_sec": float(startup_grace_sec),
                            "elapsed_sec": float(now - self._started_at),
                            "endpoints": int(len(self.table)),
                        },
                    )

                    # status を ERROR に更新して「起動失敗」を明示
                    try:
                        write_status(
                            CollectorStatus(
                                ts=now,
                                mode="ERROR",
                                message="no successful collection within startup grace",
                                items=self._build_status_items(now),
                                last_heartbeat=(
                                    datetime.fromtimestamp(now, tz=timezone.utc)
                                    .replace(microsecond=0)
                                    .isoformat()
                                    .replace("+00:00", "Z")
                                ),
                                rate_control=self._build_rate_control_summary(),
                            ),
                            emit_audit=False,
                        )
                    except Exception:
                        pass

                    # ここは「STOP」ではなく例外で上へ伝播（main 側が error 終了する）
                    raise RuntimeError("no_data: no endpoint produced data within startup grace")

            # rate_state
            if (now - last_rate) >= rate_state_every_sec:
                try:
                    # Phase1: 監査イベント collector.rate_state.write を残す（固定仕様）
                    write_rate_state(self.rc.snapshot(), emit_audit=True)
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
                            last_heartbeat=(
                                datetime.fromtimestamp(now, tz=timezone.utc)
                                .replace(microsecond=0)
                                .isoformat()
                                .replace("+00:00", "Z")
                            ),
                            rate_control=self._build_rate_control_summary(),
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
            # self.keys に残骸が混ざっても落ちないように table 側でフィルタしてからソート
            # priority: 小さいほど高優先（0が最優先）
            keys = sorted(
                (k for k in self.keys if k in self.table),
                key=lambda k: self.table[k].priority,
                reverse=False,
            )
            
            did_work = False

            # Phase1: util 計算・mode監査は 1秒に1回程度に抑える（過剰なsnapshotを避ける）
            if (now - float(self._last_util_calc_ts)) >= 1.0:
                self._last_util_calc_ts = now

                # rc.snapshot() から exchange ごとの eff_max_rps を取得
                try:
                    snap = self.rc.snapshot() or {}
                    items = (snap.get("items") or {}) if isinstance(snap, dict) else {}
                except Exception:
                    items = {}

                mode_updated = False

                # util_10s を算出して set_mode_by_util へ渡す（WARN予防の入口）
                for ex, st0 in items.items():
                    if not isinstance(st0, dict):
                        continue

                    eff = float(st0.get("eff_max_rps") or 0.0)
                    if eff <= 0.0:
                        continue

                    util10 = self._calc_util_10s(ex, eff, now)
                    try:
                        self.rc.set_mode_by_util(ex, util10)
                        mode_updated = True
                    except Exception:
                        pass

                # util により mode が変わった可能性があるため、更新後 snapshot で監査（1拍遅れ防止）
                if mode_updated:
                    try:
                        snap2 = self.rc.snapshot() or {}
                        items2 = (snap2.get("items") or {}) if isinstance(snap2, dict) else {}
                    except Exception:
                        items2 = {}

                    for ex, st2 in items2.items():
                        if not isinstance(st2, dict):
                            continue
                        mode2 = str(st2.get("mode") or "")
                        prev = self._last_mode_by_ex.get(ex)
                        if mode2 and prev != mode2:
                            self._last_mode_by_ex[ex] = mode2
                            audit.emit(
                                "collector.rate.mode",
                                feature="collector",
                                level="INFO",
                                payload={"exchange": ex, "mode": mode2, "prev": prev},
                            )

            for key in keys:
                ep = self.table.get(key)
                if not ep:
                    continue

                last = self._last_run.get(key, 0.0)
                if (now - last) < max(ep.target_interval, 0.0):
                    continue

                ok, wait_ms = self.rc.acquire(ep.exchange)
                if not ok:
                    # Phase1: hold（待機）の事実を監査（スパム抑制あり）
                    last_hold = float(self._last_hold_audit_ts.get(ep.exchange, 0.0) or 0.0)
                    if (now - last_hold) >= 1.0 and float(wait_ms) > 0.0:
                        self._last_hold_audit_ts[ep.exchange] = now
                        audit.emit(
                            "collector.rate.hold",
                            feature="collector",
                            level="INFO",
                            payload={"exchange": ep.exchange, "wait_ms": float(wait_ms)},
                        )

                    time.sleep(min(wait_ms / 1000.0, 0.25))
                    continue

                # 送信した事実をカウント（分子：実際に送ったリクエスト数）
                self._note_request_sent(ep.exchange, now)

                st = self._state.setdefault(key, EndpointState(cause="never_ok"))
                st.last_try_ts = now

                try:
                    ep.runner()

                    ok_ts = time.time()
                    self._last_run[key] = ok_ts
                    self._last_any_ok_ts = ok_ts

                    # 成功：失敗状態をクリア
                    st.last_ok_ts = ok_ts
                    st.retries = 0
                    st.cause = None
                    st.notes = None

                    did_work = True

                except EndpointSkipped as e:
                    # skip は「成功扱いしない」ので last_ok/last_any_ok は更新しない
                    st.cause = e.reason or "skipped"
                    st.notes = e.hint or None
                    # スキップ自体の audit は runner 側で emit 済みの前提
                    # did_work を立てないことで tick_sec で睡眠し、無限高速ループを避ける

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

        # NOTE:
        # - no_data 等の異常終了は例外で上位へ伝播するため、ここでは STOPPED を書かない。
        # - stop() による正常停止のみ STOPPED を書く。
        _ts_end = time.time()
        write_status(
            CollectorStatus(
                ts=_ts_end,
                mode="STOPPED",
                message="scheduler stopped",
                items=self._build_status_items(_ts_end),
                last_heartbeat=(
                    datetime.fromtimestamp(_ts_end, tz=timezone.utc)
                    .replace(microsecond=0)
                    .isoformat()
                    .replace("+00:00", "Z")
                ),
                rate_control=self._build_rate_control_summary(),
            ),
            emit_audit=False,
        )
