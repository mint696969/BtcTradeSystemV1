# path: ./btcts_next/src/btcts/collector_vnext/exploration_scheduler.py
# desc: Exploration Runtime 用の multi-window budget scheduler。NORMAL/WARN/CRIT/RECOVERY を管理する。

from __future__ import annotations

import time
from collections import deque
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Deque, Dict, List

from .exploration_config import (
    ExplorationExchangeConfig,
    ExplorationRequestClassConfig,
    ExplorationRuntimeConfig,
)


def _iso_utc_from_unix(ts: float | None) -> str | None:
    if ts is None or ts <= 0:
        return None
    return (
        datetime.fromtimestamp(ts, tz=timezone.utc)
        .isoformat(timespec="milliseconds")
        .replace("+00:00", "Z")
    )


def _clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


def _trim_window(q: Deque[float], now: float, window_sec: float) -> None:
    cut = now - max(window_sec, 0.0)
    while q and q[0] < cut:
        q.popleft()


@dataclass
class ExplorationRequestStats:
    sent_ts: Deque[float] = field(default_factory=deque)
    success_ts: Deque[float] = field(default_factory=deque)
    fail_ts: Deque[float] = field(default_factory=deque)
    status_429_ts: Deque[float] = field(default_factory=deque)


@dataclass
class ExplorationExchangeState:
    mode: str = "NORMAL"
    active_target_ratio: float = 0.95
    last_mode_change_ts: float | None = None
    last_429_ts: float | None = None
    crit_entered_ts: float | None = None
    recovery_started_ts: float | None = None
    last_recovery_step_ts: float | None = None
    hold_until_ts: float | None = None
    request_ts_60s: Deque[float] = field(default_factory=deque)
    request_ts_300s: Deque[float] = field(default_factory=deque)
    recent_429_ts: Deque[float] = field(default_factory=deque)
    last_dispatched_class: str | None = None
    per_class: Dict[str, ExplorationRequestStats] = field(default_factory=dict)


class ExplorationScheduler:
    def __init__(self, runtime_cfg: ExplorationRuntimeConfig):
        self.runtime_cfg = runtime_cfg
        self.exchange_states: Dict[str, ExplorationExchangeState] = {}

    def _stats_snapshot(self, stats: ExplorationRequestStats) -> dict:
        return {
            "sent_ts": list(stats.sent_ts),
            "success_ts": list(stats.success_ts),
            "fail_ts": list(stats.fail_ts),
            "status_429_ts": list(stats.status_429_ts),
        }

    def export_state(self) -> dict:
        items: Dict[str, dict] = {}

        for exchange, state in self.exchange_states.items():
            per_class: Dict[str, dict] = {}
            for request_class, stats in state.per_class.items():
                per_class[request_class] = self._stats_snapshot(stats)

            items[exchange] = {
                "mode": state.mode,
                "active_target_ratio": state.active_target_ratio,
                "last_mode_change_ts": state.last_mode_change_ts,
                "last_429_ts": state.last_429_ts,
                "crit_entered_ts": state.crit_entered_ts,
                "recovery_started_ts": state.recovery_started_ts,
                "last_recovery_step_ts": state.last_recovery_step_ts,
                "hold_until_ts": state.hold_until_ts,
                "last_dispatched_class": state.last_dispatched_class,
                "request_ts_60s": list(state.request_ts_60s),
                "request_ts_300s": list(state.request_ts_300s),
                "recent_429_ts": list(state.recent_429_ts),
                "per_class": per_class,
            }

        return {"items": items}

    def restore_state(self, payload: dict | None) -> None:
        items = payload.get("items") if isinstance(payload, dict) else {}
        if not isinstance(items, dict):
            return

        for exchange, item in items.items():
            if not isinstance(item, dict):
                continue

            state = self._state_for(str(exchange))
            state.mode = str(item.get("mode") or state.mode)
            state.active_target_ratio = float(item.get("active_target_ratio") or state.active_target_ratio)
            state.last_mode_change_ts = item.get("last_mode_change_ts")
            state.last_429_ts = item.get("last_429_ts")
            state.crit_entered_ts = item.get("crit_entered_ts")
            state.recovery_started_ts = item.get("recovery_started_ts")
            state.last_recovery_step_ts = item.get("last_recovery_step_ts")
            state.hold_until_ts = item.get("hold_until_ts")
            state.last_dispatched_class = item.get("last_dispatched_class")

            state.request_ts_60s = deque(float(x) for x in (item.get("request_ts_60s") or []))
            state.request_ts_300s = deque(float(x) for x in (item.get("request_ts_300s") or []))
            state.recent_429_ts = deque(float(x) for x in (item.get("recent_429_ts") or []))

            per_class = item.get("per_class")
            if not isinstance(per_class, dict):
                continue

            for request_class, class_item in per_class.items():
                if not isinstance(class_item, dict):
                    continue

                stats = self._request_stats_for(str(exchange), str(request_class))
                stats.sent_ts = deque(float(x) for x in (class_item.get("sent_ts") or []))
                stats.success_ts = deque(float(x) for x in (class_item.get("success_ts") or []))
                stats.fail_ts = deque(float(x) for x in (class_item.get("fail_ts") or []))
                stats.status_429_ts = deque(float(x) for x in (class_item.get("status_429_ts") or []))

    def restore_last_dispatched_class(
        self,
        exchange: str,
        request_class: str | None,
    ) -> None:
        if not request_class:
            return

        state = self._state_for(exchange)
        state.last_dispatched_class = str(request_class)

    def _state_for(self, exchange: str) -> ExplorationExchangeState:
        state = self.exchange_states.get(exchange)
        if state is None:
            exchange_cfg = self.runtime_cfg.get_exchange(exchange)
            target = 0.95
            if exchange_cfg is not None:
                target = exchange_cfg.control.target_utilization

            state = ExplorationExchangeState(
                mode="NORMAL",
                active_target_ratio=target,
                last_mode_change_ts=time.time(),
            )
            self.exchange_states[exchange] = state
        return state

    def _exchange_cfg(self, exchange: str) -> ExplorationExchangeConfig | None:
        return self.runtime_cfg.get_exchange(exchange)

    def _request_stats_for(
        self,
        exchange: str,
        request_class: str,
    ) -> ExplorationRequestStats:
        state = self._state_for(exchange)
        stats = state.per_class.get(request_class)
        if stats is None:
            stats = ExplorationRequestStats()
            state.per_class[request_class] = stats
        return stats

    def _trim_exchange_state(self, exchange: str, now: float) -> None:
        state = self._state_for(exchange)

        _trim_window(state.request_ts_60s, now, 60.0)
        _trim_window(state.request_ts_300s, now, 300.0)

        exchange_cfg = self._exchange_cfg(exchange)
        crit_window_sec = 30.0
        if exchange_cfg is not None:
            crit_window_sec = float(exchange_cfg.control.crit_trigger_window_sec)
        _trim_window(state.recent_429_ts, now, crit_window_sec)

        for request_class, stats in list(state.per_class.items()):
            _trim_window(stats.sent_ts, now, 300.0)
            _trim_window(stats.success_ts, now, 300.0)
            _trim_window(stats.fail_ts, now, 300.0)
            _trim_window(stats.status_429_ts, now, 300.0)

    def _request_count(self, q: Deque[float], now: float, window_sec: float) -> int:
        _trim_window(q, now, window_sec)
        return len(q)

    def _requests_60s(self, exchange: str, now: float) -> int:
        state = self._state_for(exchange)
        return self._request_count(state.request_ts_60s, now, 60.0)

    def _requests_300s(self, exchange: str, now: float) -> int:
        state = self._state_for(exchange)
        return self._request_count(state.request_ts_300s, now, 300.0)

    def _class_requests(
        self,
        exchange: str,
        request_class: str,
        now: float,
        window_sec: float,
    ) -> int:
        stats = self._request_stats_for(exchange, request_class)
        return self._request_count(stats.sent_ts, now, window_sec)

    def note_request_sent(
        self,
        exchange: str,
        request_class: str,
        now: float | None = None,
    ) -> None:
        ts = time.time() if now is None else float(now)
        state = self._state_for(exchange)
        self._trim_exchange_state(exchange, ts)

        state.request_ts_60s.append(ts)
        state.request_ts_300s.append(ts)
        state.last_dispatched_class = request_class

        stats = self._request_stats_for(exchange, request_class)
        stats.sent_ts.append(ts)

    def note_request_result(
        self,
        exchange: str,
        request_class: str,
        *,
        ok: bool,
        status_code: int | None = None,
        retry_after_sec: float | None = None,
        now: float | None = None,
    ) -> None:
        ts = time.time() if now is None else float(now)
        state = self._state_for(exchange)
        stats = self._request_stats_for(exchange, request_class)

        self._trim_exchange_state(exchange, ts)

        if ok:
            stats.success_ts.append(ts)
        else:
            stats.fail_ts.append(ts)

        if status_code == 429:
            stats.status_429_ts.append(ts)
            state.recent_429_ts.append(ts)
            state.last_429_ts = ts
            if retry_after_sec is not None and retry_after_sec > 0:
                hold_until = ts + float(retry_after_sec)
                state.hold_until_ts = max(state.hold_until_ts or 0.0, hold_until)

        self._refresh_mode(exchange, ts)

    def _utilization_pair(
        self,
        exchange: str,
        now: float,
    ) -> tuple[float, float]:
        exchange_cfg = self._exchange_cfg(exchange)
        if exchange_cfg is None:
            return 0.0, 0.0

        req_60s = self._requests_60s(exchange, now)
        req_300s = self._requests_300s(exchange, now)

        util_60s = req_60s / max(float(exchange_cfg.limits.window_60s_ip), 1.0)
        util_300s = req_300s / max(float(exchange_cfg.limits.window_300s), 1.0)
        return util_60s, util_300s

    def _current_utilization(self, exchange: str, now: float) -> float:
        util_60s, util_300s = self._utilization_pair(exchange, now)
        return max(util_60s, util_300s)

    def _recovery_target_ratio(
        self,
        exchange: str,
        now: float,
    ) -> float:
        exchange_cfg = self._exchange_cfg(exchange)
        state = self._state_for(exchange)
        if exchange_cfg is None:
            return state.active_target_ratio

        control = exchange_cfg.control
        floor_ratio = float(control.crit_floor_ratio)
        target_ratio = float(control.target_utilization)
        step_count = max(int(control.recovery_step_count), 1)
        step_interval_sec = max(int(control.recovery_step_interval_sec), 1)

        recovery_started_ts = state.recovery_started_ts or now
        elapsed_sec = max(0.0, now - recovery_started_ts)
        steps_completed = min(
            step_count,
            int(elapsed_sec // step_interval_sec),
        )

        if steps_completed <= 0:
            return floor_ratio

        recovery_steps = [
            max(floor_ratio, min(target_ratio, float(x)))
            for x in getattr(control, "recovery_steps", []) or []
        ]
        recovery_curve = str(getattr(control, "recovery_curve", "linear") or "linear").strip() or "linear"

        if recovery_curve == "custom_steps" and recovery_steps:
            if len(recovery_steps) >= step_count:
                return recovery_steps[min(steps_completed - 1, len(recovery_steps) - 1)]
            padded = list(recovery_steps)
            while len(padded) < step_count:
                padded.append(target_ratio)
            return padded[min(steps_completed - 1, len(padded) - 1)]

        delta = max(0.0, target_ratio - floor_ratio)
        step_size = delta / float(step_count)
        return min(target_ratio, floor_ratio + (step_size * steps_completed))

    def _set_mode(self, exchange: str, mode: str, now: float) -> None:
        state = self._state_for(exchange)
        if state.mode != mode:
            state.mode = mode
            state.last_mode_change_ts = now

    def _refresh_mode(self, exchange: str, now: float | None = None) -> str:
        ts = time.time() if now is None else float(now)
        exchange_cfg = self._exchange_cfg(exchange)
        state = self._state_for(exchange)

        if exchange_cfg is None:
            self._set_mode(exchange, "NORMAL", ts)
            return state.mode

        self._trim_exchange_state(exchange, ts)

        control = exchange_cfg.control
        util = self._current_utilization(exchange, ts)
        recent_429_count = len(state.recent_429_ts)

        if state.mode in {"NORMAL", "WARN"} and recent_429_count >= control.crit_trigger_429_count:
            self._set_mode(exchange, "CRIT", ts)
            state.active_target_ratio = control.crit_floor_ratio
            state.crit_entered_ts = ts
            state.recovery_started_ts = None
            state.last_recovery_step_ts = None
            if state.hold_until_ts is None:
                state.hold_until_ts = ts + float(control.crit_cooldown_sec)
            else:
                state.hold_until_ts = max(
                    state.hold_until_ts,
                    ts + float(control.crit_cooldown_sec),
                )
            return state.mode

        if state.mode == "CRIT":
            hold_until_ts = state.hold_until_ts or 0.0
            can_leave_crit = ts >= hold_until_ts
            last_429_ok = (
                state.last_429_ts is None
                or (ts - state.last_429_ts) >= float(control.recovery_start_after_sec)
            )

            if can_leave_crit and last_429_ok:
                self._set_mode(exchange, "RECOVERY", ts)
                state.recovery_started_ts = ts
                state.last_recovery_step_ts = ts
                state.active_target_ratio = float(control.crit_floor_ratio)
                state.recent_429_ts.clear()
                return state.mode

            state.active_target_ratio = float(control.crit_floor_ratio)
            return state.mode

        if state.mode == "RECOVERY":
            state.active_target_ratio = self._recovery_target_ratio(exchange, ts)

            if state.active_target_ratio >= float(control.target_utilization):
                if util <= float(control.warn_utilization):
                    self._set_mode(exchange, "NORMAL", ts)
                    state.active_target_ratio = float(control.target_utilization)
                    return state.mode

            if util > float(control.warn_utilization):
                self._set_mode(exchange, "WARN", ts)
                return state.mode

            return state.mode

        if util > float(control.warn_utilization):
            self._set_mode(exchange, "WARN", ts)
            state.active_target_ratio = float(control.target_utilization)
            return state.mode

        self._set_mode(exchange, "NORMAL", ts)
        state.active_target_ratio = float(control.target_utilization)
        return state.mode

    def current_mode(self, exchange: str, now: float | None = None) -> str:
        return self._refresh_mode(exchange, now)

    def current_budget(self, exchange: str, now: float | None = None) -> dict:
        ts = time.time() if now is None else float(now)
        exchange_cfg = self._exchange_cfg(exchange)
        state = self._state_for(exchange)

        self._refresh_mode(exchange, ts)

        if exchange_cfg is None:
            return {
                "target_ratio": state.active_target_ratio,
                "remaining_60s": 0,
                "remaining_300s": 0,
                "allowed_now": False,
            }

        target_ratio = _clamp(
            state.active_target_ratio,
            0.0,
            exchange_cfg.control.hard_cap_utilization,
        )

        budget_60s = int(exchange_cfg.limits.window_60s_ip * target_ratio)
        budget_300s = int(exchange_cfg.limits.window_300s * target_ratio)

        used_60s = self._requests_60s(exchange, ts)
        used_300s = self._requests_300s(exchange, ts)

        remaining_60s = max(0, budget_60s - used_60s)
        remaining_300s = max(0, budget_300s - used_300s)

        allowed_now = remaining_60s > 0 and remaining_300s > 0
        if state.mode == "CRIT" and state.hold_until_ts and ts < state.hold_until_ts:
            allowed_now = remaining_60s > 0 and remaining_300s > 0

        return {
            "target_ratio": target_ratio,
            "budget_60s": budget_60s,
            "budget_300s": budget_300s,
            "used_60s": used_60s,
            "used_300s": used_300s,
            "remaining_60s": remaining_60s,
            "remaining_300s": remaining_300s,
            "allowed_now": allowed_now,
        }

    def _enabled_priority_classes(self, exchange: str) -> List[str]:
        exchange_cfg = self._exchange_cfg(exchange)
        if exchange_cfg is None:
            return []

        enabled: List[str] = []
        for request_class in exchange_cfg.request_priority:
            class_cfg = exchange_cfg.request_classes.get(request_class)
            if class_cfg is None or class_cfg.enabled:
                enabled.append(request_class)
        return enabled

    def _bootstrap_rotating_dispatch(
        self,
        exchange: str,
        candidates: List[str],
        now: float,
    ) -> str | None:
        state = self._state_for(exchange)
        total_sent_60s = self._requests_60s(exchange, now)
        total_sent_300s = self._requests_300s(exchange, now)

        if total_sent_60s > 0 or total_sent_300s > 0:
            return None

        if not candidates:
            return None

        last_class = state.last_dispatched_class
        if not last_class or last_class not in candidates:
            return candidates[0]

        idx = candidates.index(last_class)
        next_idx = (idx + 1) % len(candidates)
        return candidates[next_idx]

    def _target_share(
        self,
        exchange: str,
        request_class: str,
    ) -> float:
        exchange_cfg = self._exchange_cfg(exchange)
        if exchange_cfg is None:
            return 0.0

        enabled_classes = self._enabled_priority_classes(exchange)
        if not enabled_classes:
            return 0.0

        total_weight = 0.0
        for name in enabled_classes:
            cfg = exchange_cfg.request_classes.get(name)
            if cfg is None:
                cfg = ExplorationRequestClassConfig()
            total_weight += max(0.0, cfg.weight)

        if total_weight <= 0.0:
            return 1.0 / max(len(enabled_classes), 1)

        class_cfg = exchange_cfg.request_classes.get(request_class)
        if class_cfg is None:
            class_cfg = ExplorationRequestClassConfig()

        return max(0.0, class_cfg.weight) / total_weight

    def _share_score(
        self,
        exchange: str,
        request_class: str,
        now: float,
        class_cfg: ExplorationRequestClassConfig,
    ) -> float:
        exchange_cfg = self._exchange_cfg(exchange)
        if exchange_cfg is None:
            return 0.0

        total_60s = max(1, self._requests_60s(exchange, now))
        class_60s = self._class_requests(exchange, request_class, now, 60.0)
        actual_share = class_60s / total_60s

        target_share = self._target_share(exchange, request_class)
        target_gap = target_share - actual_share
        min_share_gap = max(0.0, class_cfg.min_share - actual_share)

        return (min_share_gap * 1000.0) + (target_gap * 100.0)

    def _last_sent_ts(
        self,
        exchange: str,
        request_class: str,
        now: float,
    ) -> float | None:
        stats = self._request_stats_for(exchange, request_class)
        _trim_window(stats.sent_ts, now, 300.0)
        if not stats.sent_ts:
            return None
        return float(stats.sent_ts[-1])

    def next_dispatch(
        self,
        exchange: str,
        now: float | None = None,
    ) -> str | None:
        ts = time.time() if now is None else float(now)
        exchange_cfg = self._exchange_cfg(exchange)
        if exchange_cfg is None or not exchange_cfg.enabled:
            return None

        budget = self.current_budget(exchange, ts)
        if not budget.get("allowed_now"):
            return None

        candidates = self._enabled_priority_classes(exchange)
        if not candidates:
            return None

        bootstrap_choice = self._bootstrap_rotating_dispatch(exchange, candidates, ts)
        if bootstrap_choice is not None:
            return bootstrap_choice

        state = self._state_for(exchange)
        best_class: str | None = None
        best_score: float | None = None
        best_last_sent_ts: float | None = None

        for request_class in candidates:
            class_cfg = exchange_cfg.request_classes.get(request_class)
            if class_cfg is None:
                class_cfg = ExplorationRequestClassConfig()

            score = self._share_score(exchange, request_class, ts, class_cfg)
            last_sent_ts = self._last_sent_ts(exchange, request_class, ts)

            if best_score is None or score > best_score:
                best_score = score
                best_class = request_class
                best_last_sent_ts = last_sent_ts
                continue

            if score == best_score:
                if best_class == state.last_dispatched_class and request_class != state.last_dispatched_class:
                    best_class = request_class
                    best_last_sent_ts = last_sent_ts
                    continue

                if last_sent_ts is None and best_last_sent_ts is not None:
                    best_class = request_class
                    best_last_sent_ts = last_sent_ts
                    continue

                if (
                    last_sent_ts is not None
                    and best_last_sent_ts is not None
                    and last_sent_ts < best_last_sent_ts
                ):
                    best_class = request_class
                    best_last_sent_ts = last_sent_ts
                    continue

        return best_class

    def snapshot(self, now: float | None = None) -> dict:
        ts = time.time() if now is None else float(now)
        items: Dict[str, dict] = {}

        for exchange, exchange_cfg in self.runtime_cfg.exchanges.items():
            state = self._state_for(exchange)
            mode = self._refresh_mode(exchange, ts)
            budget = self.current_budget(exchange, ts)
            util_60s, util_300s = self._utilization_pair(exchange, ts)

            request_classes: Dict[str, dict] = {}
            for request_class in exchange_cfg.request_priority:
                stats = self._request_stats_for(exchange, request_class)
                class_cfg = exchange_cfg.request_classes.get(request_class)
                if class_cfg is None:
                    class_cfg = ExplorationRequestClassConfig()

                request_classes[request_class] = {
                    "domain": class_cfg.domain,
                    "requests_60s": self._request_count(stats.sent_ts, ts, 60.0),
                    "requests_300s": self._request_count(stats.sent_ts, ts, 300.0),
                    "success_60s": self._request_count(stats.success_ts, ts, 60.0),
                    "fail_60s": self._request_count(stats.fail_ts, ts, 60.0),
                    "status_429_300s": self._request_count(stats.status_429_ts, ts, 300.0),
                }

            items[exchange] = {
                "exchange": exchange,
                "enabled": exchange_cfg.enabled,
                "mode": mode,
                "engaged": mode in {"WARN", "CRIT", "RECOVERY"},
                "domain_names": ["market_data", *[name for name in exchange_cfg.domains.keys() if name != "market_data"]],
                "target_utilization": exchange_cfg.control.target_utilization,
                "active_target_ratio": state.active_target_ratio,
                "warn_utilization": exchange_cfg.control.warn_utilization,
                "hard_cap_utilization": exchange_cfg.control.hard_cap_utilization,
                "crit_floor_ratio": exchange_cfg.control.crit_floor_ratio,
                "requests_60s": self._requests_60s(exchange, ts),
                "requests_300s": self._requests_300s(exchange, ts),
                "utilization_60s": util_60s,
                "utilization_300s": util_300s,
                "utilization": max(util_60s, util_300s),
                "last_429_ts": _iso_utc_from_unix(state.last_429_ts),
                "crit_entered_ts": _iso_utc_from_unix(state.crit_entered_ts),
                "recovery_started_ts": _iso_utc_from_unix(state.recovery_started_ts),
                "hold_until_ts": _iso_utc_from_unix(state.hold_until_ts),
                "last_mode_change_ts": _iso_utc_from_unix(state.last_mode_change_ts),
                "budget": budget,
                "domains": {
                    "market_data": {
                        "mode": mode,
                        "engaged": mode in {"WARN", "CRIT", "RECOVERY"},
                        "target_utilization": exchange_cfg.control.target_utilization,
                        "active_target_ratio": state.active_target_ratio,
                        "warn_utilization": exchange_cfg.control.warn_utilization,
                        "hard_cap_utilization": exchange_cfg.control.hard_cap_utilization,
                        "crit_floor_ratio": exchange_cfg.control.crit_floor_ratio,
                        "requests_60s": self._requests_60s(exchange, ts),
                        "requests_300s": self._requests_300s(exchange, ts),
                        "utilization_60s": util_60s,
                        "utilization_300s": util_300s,
                        "utilization": max(util_60s, util_300s),
                        "last_429_ts": _iso_utc_from_unix(state.last_429_ts),
                        "crit_entered_ts": _iso_utc_from_unix(state.crit_entered_ts),
                        "recovery_started_ts": _iso_utc_from_unix(state.recovery_started_ts),
                        "hold_until_ts": _iso_utc_from_unix(state.hold_until_ts),
                        "last_mode_change_ts": _iso_utc_from_unix(state.last_mode_change_ts),
                        "budget": budget,
                    },
                    **{
                        name: {}
                        for name in exchange_cfg.domains.keys()
                        if name != "market_data"
                    },
                },
                "shared_ip": dict(exchange_cfg.shared_ip),
                "request_classes": request_classes,
                "ts": _iso_utc_from_unix(ts),
            }

        return {
            "ts": _iso_utc_from_unix(ts),
            "items": items,
        }