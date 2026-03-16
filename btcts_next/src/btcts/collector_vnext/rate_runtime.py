# path: ./btcts_next/src/btcts/collector_vnext/rate_runtime.py
# desc: Thin rate-control adapter for Collector vNext built on top of btcts.collector.rate.RateController.

from __future__ import annotations

import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Dict, List

from btcts.collector.rate import RateController, RatePolicy
from btcts.settings import svc as settings_svc

from .config import CollectorConfig
from .state import write_json_state


def _safe_float(value, default: float) -> float:
    try:
        return float(value)
    except Exception:
        return default


def _safe_iso_from_unix(value) -> str | None:
    try:
        ts = float(value)
    except Exception:
        return None

    if ts <= 0.0:
        return None

    return (
        datetime.fromtimestamp(ts, tz=timezone.utc)
        .isoformat(timespec="milliseconds")
        .replace("+00:00", "Z")
    )


@dataclass
class VNextRateRuntime:
    cfg: CollectorConfig
    rc: RateController
    requests_sent: Dict[str, List[float]] = field(default_factory=dict)
    rate_cfg: dict = field(default_factory=dict)

    @classmethod
    def build(cls, cfg: CollectorConfig) -> "VNextRateRuntime":
        rc = RateController()

        try:
            rate_cfg = settings_svc.load_effective("rate_control")
        except Exception:
            rate_cfg = {}

        if isinstance(rate_cfg, dict):
            try:
                rc.set_common_policy(rate_cfg)
            except Exception:
                pass

        try:
            exchanges_cfg = settings_svc.load_effective("exchanges")
        except Exception:
            exchanges_cfg = {}

        ex_map = exchanges_cfg.get("exchanges") if isinstance(exchanges_cfg, dict) else {}
        if isinstance(ex_map, dict):
            for exchange, item in ex_map.items():
                if not isinstance(item, dict):
                    continue

                if not bool(item.get("enabled", False)):
                    continue

                rate = item.get("rate") if isinstance(item.get("rate"), dict) else {}
                max_rps = _safe_float(rate.get("max_rps"), 0.0)
                if max_rps <= 0.0:
                    continue

                soft_ratio = _safe_float(rate.get("soft_ratio"), 0.9)
                hard_ratio = _safe_float(rate.get("hard_ratio"), 0.8)
                burst_base_sec = _safe_float(rate.get("burst_base_sec"), 1.0)

                if soft_ratio < hard_ratio:
                    soft_ratio, hard_ratio = hard_ratio, soft_ratio

                rc.set_policy(
                    str(exchange),
                    RatePolicy(
                        official_max_rps=max_rps,
                        soft_ratio=soft_ratio,
                        hard_ratio=hard_ratio,
                        burst_base_sec=burst_base_sec,
                    ),
                )

        runtime = cls(
            cfg=cfg,
            rc=rc,
            requests_sent={},
            rate_cfg=rate_cfg if isinstance(rate_cfg, dict) else {},
        )
        runtime.write_snapshot()
        return runtime

    def acquire(self, exchange: str) -> tuple[bool, int]:
        try:
            return self.rc.acquire(exchange)
        except KeyError:
            return True, 0

    def note_request_sent(self, exchange: str) -> None:
        now = time.time()
        q = self.requests_sent.setdefault(exchange, [])
        q.append(now)
        self._trim(exchange, now)
        self._update_util(exchange, now)
        self.write_snapshot()

    def on_success(self, exchange: str) -> None:
        now = time.time()
        self._trim(exchange, now)
        self._update_util(exchange, now)
        self.write_snapshot()

    def on_429(self, exchange: str, retry_after_sec: float = 0.0) -> None:
        self.rc.on_429(exchange, retry_after_sec)
        self.write_snapshot()

    def _current_hold_until_ts(self, exchange: str) -> str | None:
        return _safe_iso_from_unix(self.rc._next_allowed.get(exchange, 0.0))

    def _current_backoff_sec(self, exchange: str) -> float:
        return float(self.rc._crit_backoff_sec.get(exchange, 0.0) or 0.0)

    def _current_util_ratio(self, exchange: str, eff_max_rps: float) -> float:
        if eff_max_rps <= 0.0:
            return 0.0

        window = _safe_float(self.rate_cfg.get("util_window_warn_sec"), 10.0)
        q = self.requests_sent.get(exchange, [])
        return min(1.0, max(0.0, len(q) / max(eff_max_rps * window, 1e-9)))

    def _current_recovery_phase(
        self,
        exchange: str,
        *,
        mode: str,
        last_429_ts: str | None,
        hold_until_ts: str | None,
    ) -> str:
        if not last_429_ts:
            return "steady"

        if hold_until_ts and mode == "CRIT":
            return "cooldown"

        if mode == "WARN":
            return "recovering_warn"

        if mode == "NORMAL":
            return "released"

        return "steady"

    def _visibility_item(self, exchange: str, item: dict) -> dict:
        """
        Convert RateController snapshot item to visibility contract required by P0.
        """

        mode = str(item.get("mode") or "NORMAL").upper()
        official_max_rps = float(item.get("official_max_rps") or 0.0)

        policy = self.rc.get_policy(exchange)
        if policy is not None:
            official_max_rps = float(policy.official_max_rps)
            internal_safe_max_rps = float(policy.official_max_rps) * float(policy.soft_ratio)
        else:
            internal_safe_max_rps = official_max_rps

        eff_max_rps = float(item.get("eff_max_rps") or 0.0)
        util_ratio = self._current_util_ratio(exchange, eff_max_rps)

        last_429_ts = _safe_iso_from_unix(item.get("last_429_ts"))
        hold_until_ts = self._current_hold_until_ts(exchange)
        backoff_sec = self._current_backoff_sec(exchange)
        recovery_phase = self._current_recovery_phase(
            exchange,
            mode=mode,
            last_429_ts=last_429_ts,
            hold_until_ts=hold_until_ts,
        )

        return {
            "exchange": exchange,
            "summary_state": mode,
            "engaged": mode != "NORMAL",
            "reason": str(item.get("reason") or ""),
            "official_max_rps": official_max_rps,
            "internal_safe_max_rps": internal_safe_max_rps,
            "eff_max_rps": eff_max_rps,
            "wait_ms": int(item.get("wait_ms") or 0),
            "util_ratio": util_ratio,
            "last_429_ts": last_429_ts,
            "last_retry_after_sec": (
                float(item.get("last_retry_after_sec") or 0.0)
                if item.get("last_retry_after_sec") is not None
                else None
            ),
            "hold_until_ts": hold_until_ts,
            "backoff_sec": backoff_sec,
            "recovery_phase": recovery_phase,
            "ts": _safe_iso_from_unix(item.get("ts")) or _safe_iso_from_unix(time.time()),
        }

    def snapshot(self) -> dict:
        snap = self.rc.snapshot()

        if not isinstance(snap, dict):
            return {"ts": time.time(), "items": {}}

        items = snap.get("items")
        if not isinstance(items, dict):
            return {"ts": time.time(), "items": {}}

        visible_items = {}

        for exchange, item in items.items():
            if not isinstance(item, dict):
                continue

            visible_items[exchange] = self._visibility_item(exchange, item)

        return {
            "ts": snap.get("ts") or time.time(),
            "items": visible_items,
        }

    def write_snapshot(self) -> None:
        write_json_state(self.cfg, "rate_state.json", self.snapshot())

    def _trim(self, exchange: str, now: float) -> None:
        window = _safe_float(self.rate_cfg.get("util_window_warn_sec"), 10.0)
        q = self.requests_sent.setdefault(exchange, [])
        cut = now - window
        self.requests_sent[exchange] = [ts for ts in q if ts >= cut]

    def _update_util(self, exchange: str, now: float) -> None:
        snap = self.snapshot()
        items = snap.get("items") if isinstance(snap, dict) else {}
        st = items.get(exchange) if isinstance(items, dict) else None
        if not isinstance(st, dict):
            return

        eff = _safe_float(st.get("eff_max_rps"), 0.0)
        if eff <= 0.0:
            return

        window = _safe_float(self.rate_cfg.get("util_window_warn_sec"), 10.0)
        q = self.requests_sent.get(exchange, [])
        util = min(1.0, max(0.0, len(q) / max(eff * window, 1e-9)))
        self.rc.set_mode_by_util(exchange, util)
        self.write_snapshot()