# path: ./btcts_next/src/btcts/collector_vnext/unified_runtime.py
# desc: Unified Collector の REST 主系 runtime。U1 では exploration REST を unified family へ移植する。

from __future__ import annotations

import json
import os
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .telemetry_policy import emit_collector_event

from .config import load_config
from .emit_rest import (
    RestRequestFailedError,
    emit_rest_board_snapshot,
    emit_rest_trades,
)
from .events import now_iso_utc
from .exploration_config import load_exploration_runtime_config
from .exploration_scheduler import ExplorationScheduler
from .ids import SequenceManager
from .unified_state import (
    write_unified_checkpoint,
    write_unified_health,
    write_unified_rate_state,
    write_unified_scheduler_state,
    write_unified_status,
)


def _emit_runtime_audit(
    event: str,
    *,
    collector_id: str,
    collector_role: str,
    symbol: str,
    session_id: str,
    topic: str,
    ok: bool,
    elapsed_ms: float | None = None,
    extra: dict | None = None,
) -> None:
    payload = {
        "collector_id": collector_id,
        "collector_role": collector_role,
        "symbol": symbol,
        "session_id": session_id,
        "exchange": "bitflyer",
        "topic": topic,
        "ok": ok,
    }
    if elapsed_ms is not None:
        payload["elapsed_ms"] = elapsed_ms
    if extra:
        payload.update(extra)

    emit_collector_event(
        event,
        level="INFO" if ok else "WARN",
        feature="collector_vnext",
        actor="collector_vnext.unified_runtime",
        site="collector_vnext.unified_runtime.run_once",
        payload=payload,
    )


def _env_force_429_request_class() -> str:
    return str(os.getenv("BTCTS_UNIFIED_FORCE_429_CLASS", "") or "").strip().lower()


def _env_force_429_retry_after_sec() -> float:
    raw = str(os.getenv("BTCTS_UNIFIED_FORCE_429_RETRY_AFTER_SEC", "") or "").strip()
    if not raw:
        return 0.0
    try:
        return max(float(raw), 0.0)
    except Exception:
        return 0.0


def _load_scheduler_state(cfg) -> dict:
    if str(os.getenv("BTCTS_UNIFIED_TEST_RESET_STATE", "") or "").strip().lower() in {
        "1",
        "true",
        "yes",
        "on",
    }:
        return {}

    path = Path(cfg.roots()["state"]) / "unified_scheduler_state.json"
    if not path.exists():
        return {}

    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


def _load_previous_request_class(cfg, exchange: str) -> str | None:
    path = Path(cfg.roots()["state"]) / "unified_rate_state.json"
    if not path.exists():
        return None

    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None

    items = payload.get("items") if isinstance(payload, dict) else {}
    item = items.get(exchange) if isinstance(items, dict) else {}
    request_classes = item.get("request_classes") if isinstance(item, dict) else {}

    if not isinstance(request_classes, dict):
        return None

    best_class: str | None = None
    best_count = -1

    for request_class, class_item in request_classes.items():
        if not isinstance(class_item, dict):
            continue
        count = int(class_item.get("requests_300s") or 0)
        if count > best_count:
            best_count = count
            best_class = str(request_class)

    return best_class


def _load_unified_origin_status(cfg) -> dict[str, Any]:
    path = Path(cfg.roots()["state"]) / "unified_origin_status.json"
    if not path.exists():
        return {}

    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}

    return payload if isinstance(payload, dict) else {}


def _load_unified_executions_status(cfg) -> dict[str, Any]:
    path = Path(cfg.roots()["state"]) / "unified_executions_status.json"
    if not path.exists():
        return {}

    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}

    return payload if isinstance(payload, dict) else {}


def _build_status_payload(
    *,
    cfg,
    session_id: str,
    scheduler: ExplorationScheduler,
    exchange: str,
    last_result: dict | None,
) -> dict:
    snapshot = scheduler.snapshot()
    rate_item = ((snapshot.get("items") or {}).get(exchange) or {}) if isinstance(snapshot, dict) else {}
    rate_domains = (rate_item.get("domains") or {}) if isinstance(rate_item, dict) else {}
    market_data_rate = (rate_domains.get("market_data") or {}) if isinstance(rate_domains, dict) else {}
    rate_view = market_data_rate or rate_item
    mode = str(rate_view.get("mode") or "NORMAL")
    origin_status = _load_unified_origin_status(cfg)
    executions_status = _load_unified_executions_status(cfg)

    ws_state = str(origin_status.get("ws_state") or "NOT_STARTED")
    ws_lane_state = str(origin_status.get("lane_state") or "not_started")
    ws_last_event_ts = origin_status.get("last_event_ts") or origin_status.get("ts")
    ws_freshness = _infer_ws_freshness(
        ws_state=ws_state,
        last_event_ts=ws_last_event_ts,
    )

    ws_executions_state = str(executions_status.get("ws_state") or "NOT_STARTED")
    ws_executions_lane_state = str(executions_status.get("lane_state") or "not_started")
    ws_executions_last_event_ts = executions_status.get("ts")
    ws_executions_freshness = _infer_ws_freshness(
        ws_state=ws_executions_state,
        last_event_ts=ws_executions_last_event_ts,
        connected_ts=executions_status.get("connected_ts"),
    )

    message = (
        f"collector_vnext unified runtime active "
        f"mode={mode} requests_60s={rate_view.get('requests_60s', 0)} "
        f"requests_300s={rate_view.get('requests_300s', 0)}"
    )

    status_mode = "DEGRADED" if mode == "CRIT" or ws_freshness == "BROKEN" else "RUNNING"

    return {
        "ts": now_iso_utc(),
        "collector_id": cfg.collector_id,
        "collector_role": cfg.collector_role,
        "mode": status_mode,
        "message": message,
        "session_id": session_id,
        "last_success_ts": now_iso_utc(),
        "runtime_kind": "unified",
        "exchange": exchange,
        "rest_lane": {
            "enabled": True,
            "state": mode.lower(),
            "request_classes": list((rate_item.get("request_classes") or {}).keys()),
        },
        "ws_board_lane": {
            "enabled": ws_lane_state != "not_started",
            "state": ws_lane_state,
            "ws_state": ws_state,
            "ws_freshness": ws_freshness,
            "last_event_ts": ws_last_event_ts,
            "last_error": origin_status.get("last_error"),
            "saw_snapshot": origin_status.get("saw_snapshot"),
            "saw_delta": origin_status.get("saw_delta"),
            "restart_count": origin_status.get("restart_count"),
        },
        "ws_executions_lane": {
            "enabled": ws_executions_lane_state != "not_started",
            "state": ws_executions_lane_state,
            "ws_state": ws_executions_state,
            "ws_freshness": ws_executions_freshness,
            "connected_ts": executions_status.get("connected_ts"),
            "last_event_ts": executions_status.get("last_event_ts") or ws_executions_last_event_ts,
            "last_error": executions_status.get("last_error"),
            "trade_count": executions_status.get("trade_count"),
            "restart_count": executions_status.get("restart_count"),
        },
        "rate_control": {
            "summary_state": mode,
            "engaged": bool(rate_view.get("engaged", False)),
            "util_ratio": rate_view.get("utilization"),
            "last_429_ts": rate_view.get("last_429_ts"),
            "hold_until_ts": rate_view.get("hold_until_ts"),
        },
        "last_result": last_result or {},
    }


def _build_health_payload(
    *,
    cfg,
    exchange: str,
    scheduler: ExplorationScheduler,
) -> dict:
    snapshot = scheduler.snapshot()
    rate_item = ((snapshot.get("items") or {}).get(exchange) or {}) if isinstance(snapshot, dict) else {}
    rate_domains = (rate_item.get("domains") or {}) if isinstance(rate_item, dict) else {}
    market_data_rate = (rate_domains.get("market_data") or {}) if isinstance(rate_domains, dict) else {}
    rate_view = market_data_rate or rate_item
    mode = str(rate_view.get("mode") or "NORMAL")
    origin_status = _load_unified_origin_status(cfg)
    executions_status = _load_unified_executions_status(cfg)

    ws_state = str(origin_status.get("ws_state") or "NOT_STARTED")
    ws_last_event_ts = origin_status.get("last_event_ts") or origin_status.get("ts")
    ws_freshness = _infer_ws_freshness(
        ws_state=ws_state,
        last_event_ts=ws_last_event_ts,
    )

    ws_executions_state = str(executions_status.get("ws_state") or "NOT_STARTED")
    ws_executions_freshness = _infer_ws_freshness(
        ws_state=ws_executions_state,
        last_event_ts=executions_status.get("last_event_ts") or executions_status.get("ts"),
        connected_ts=executions_status.get("connected_ts"),
    )

    health_ok = mode != "CRIT" and ws_freshness != "BROKEN"
    health_status = "healthy" if health_ok else "degraded"

    return {
        "ts": now_iso_utc(),
        "ok": health_ok,
        "status": health_status,
        "runtime_kind": "unified",
        "exchange": exchange,
        "rest_mode": mode,
        "ws_state": ws_state,
        "ws_freshness": ws_freshness,
        "gap_detected": bool(origin_status.get("gap_detected", False)),
        "resync_active": bool(origin_status.get("resync_active", False)),
        "requests_60s": rate_view.get("requests_60s"),
        "requests_300s": rate_view.get("requests_300s"),
        "utilization": rate_view.get("utilization"),
        "last_429_ts": rate_view.get("last_429_ts"),
        "hold_until_ts": rate_view.get("hold_until_ts"),
        "ws_last_event_ts": ws_last_event_ts,
        "ws_last_error": origin_status.get("last_error"),
        "ws_executions_state": ws_executions_state,
        "ws_executions_freshness": ws_executions_freshness,
        "ws_executions_connected_ts": executions_status.get("connected_ts"),
        "ws_executions_last_event_ts": executions_status.get("last_event_ts") or executions_status.get("ts"),
        "ws_executions_last_error": executions_status.get("last_error"),
        "ws_executions_trade_count": executions_status.get("trade_count"),
    }


def _extract_scheduler_mode(state_payload: dict | None, exchange: str) -> str:
    if not isinstance(state_payload, dict):
        return "NORMAL"
    items = state_payload.get("items") or {}
    item = items.get(exchange) or {}
    domains = item.get("domains") or {}
    market_data = domains.get("market_data") or {}
    return str(market_data.get("mode") or item.get("mode") or "NORMAL")


def _parse_runtime_ts(value: str | None) -> datetime | None:
    text = str(value or "").strip()
    if not text:
        return None

    try:
        if text.endswith("Z"):
            return datetime.fromisoformat(text.replace("Z", "+00:00"))
        return datetime.fromisoformat(text)
    except Exception:
        return None


def _infer_ws_freshness(
    *,
    ws_state: str,
    last_event_ts: str | None,
    connected_ts: str | None = None,
) -> str:
    state = str(ws_state or "").upper()
    if state in {"BROKEN", "STOPPED"}:
        return "BROKEN"

    event_dt = _parse_runtime_ts(last_event_ts)
    connected_dt = _parse_runtime_ts(connected_ts)

    now = datetime.now(timezone.utc)

    if event_dt is not None:
        age_sec = max(0.0, (now - event_dt.astimezone(timezone.utc)).total_seconds())

        if age_sec <= 5:
            return "LIVE"
        if age_sec <= 30:
            return "QUIET"
        if age_sec <= 300:
            return "STALE"
        return "BROKEN"

    if state == "SYNCING":
        return "SYNCING"

    if connected_dt is not None:
        connected_age_sec = max(
            0.0,
            (now - connected_dt.astimezone(timezone.utc)).total_seconds(),
        )

        if connected_age_sec <= 30:
            return "QUIET"
        if connected_age_sec <= 300:
            return "STALE"
        return "BROKEN"

    if state == "CONNECTING":
        return "CONNECTING"

    return "UNKNOWN"


class UnifiedRuntime:
    def __init__(self) -> None:
        self.cfg = load_config()
        self.runtime_cfg = load_exploration_runtime_config()
        self.scheduler = ExplorationScheduler(self.runtime_cfg)
        self.exchange = "bitflyer"
        self.session_id = f"{self.cfg.collector_id}-unified"
        self.seq = SequenceManager.start()

        self.scheduler.restore_state(_load_scheduler_state(self.cfg))

        previous_request_class = _load_previous_request_class(self.cfg, self.exchange)
        self.scheduler.restore_last_dispatched_class(
            self.exchange,
            previous_request_class,
        )

    def run_once(self) -> int:
        exchange_cfg = self.runtime_cfg.get_exchange(self.exchange)
        if exchange_cfg is None or not exchange_cfg.enabled:
            raise RuntimeError("unified runtime is not enabled for bitflyer")

        started_at = time.perf_counter()
        before_mode = _extract_scheduler_mode(
            self.scheduler.export_state(),
            self.exchange,
        )

        dispatch = self.scheduler.next_dispatch(self.exchange)

        if dispatch is None:
            snapshot = self.scheduler.snapshot()
            scheduler_state = self.scheduler.export_state()
            after_mode = _extract_scheduler_mode(scheduler_state, self.exchange)

            write_unified_rate_state(self.cfg, snapshot)
            write_unified_scheduler_state(self.cfg, scheduler_state)

            if after_mode != before_mode:
                _emit_runtime_audit(
                    "collector_vnext.unified.mode.changed",
                    collector_id=self.cfg.collector_id,
                    collector_role=self.cfg.collector_role,
                    symbol=self.cfg.symbol,
                    session_id=self.session_id,
                    topic=after_mode.lower(),
                    ok=True,
                    extra={
                        "from_mode": before_mode,
                        "to_mode": after_mode,
                        "exchange": self.exchange,
                        "idle": True,
                    },
                )

            write_unified_status(
                self.cfg,
                _build_status_payload(
                    cfg=self.cfg,
                    session_id=self.session_id,
                    scheduler=self.scheduler,
                    exchange=self.exchange,
                    last_result={
                        "request_class": None,
                        "ok": True,
                        "idle": True,
                    },
                ),
            )
            write_unified_health(
                self.cfg,
                _build_health_payload(
                    cfg=self.cfg,
                    exchange=self.exchange,
                    scheduler=self.scheduler,
                ),
            )
            return 0

        self.scheduler.note_request_sent(self.exchange, dispatch)

        last_result: dict | None = None
        ok = False
        status_code: int | None = None
        retry_after_sec: float | None = None

        forced_429_class = _env_force_429_request_class()
        forced_429_retry_after_sec = _env_force_429_retry_after_sec()

        try:
            if forced_429_class and (
                forced_429_class == "all" or dispatch == forced_429_class
            ):
                raise RestRequestFailedError(
                    f"forced unified 429 for request_class={dispatch}",
                    status_code=429,
                    retry_after_sec=forced_429_retry_after_sec,
                )

            if dispatch == "board_snapshot":
                last_result = emit_rest_board_snapshot(
                    seq=self.seq,
                    session_id=self.session_id,
                    rate_runtime=None,
                )
            elif dispatch == "rest_trades":
                last_result = emit_rest_trades(
                    seq=self.seq,
                    session_id=self.session_id,
                    rate_runtime=None,
                )
            else:
                raise RuntimeError(f"unsupported unified request_class: {dispatch}")

            ok = True

        except RestRequestFailedError as exc:
            status_code = exc.status_code
            retry_after_sec = exc.retry_after_sec
            last_result = {
                "request_class": dispatch,
                "error": str(exc),
                "status_code": exc.status_code,
                "retry_after_sec": exc.retry_after_sec,
            }
            ok = False

        except Exception as exc:
            last_result = {
                "request_class": dispatch,
                "error": str(exc),
            }
            ok = False

        self.scheduler.note_request_result(
            self.exchange,
            dispatch,
            ok=ok,
            status_code=status_code,
            retry_after_sec=retry_after_sec,
        )

        elapsed_ms = round((time.perf_counter() - started_at) * 1000.0, 1)
        snapshot = self.scheduler.snapshot()
        scheduler_state = self.scheduler.export_state()
        after_mode = _extract_scheduler_mode(scheduler_state, self.exchange)

        write_unified_rate_state(self.cfg, snapshot)
        write_unified_scheduler_state(self.cfg, scheduler_state)
        write_unified_status(
            self.cfg,
            _build_status_payload(
                cfg=self.cfg,
                session_id=self.session_id,
                scheduler=self.scheduler,
                exchange=self.exchange,
                last_result={
                    "request_class": dispatch,
                    "ok": ok,
                    **(last_result or {}),
                },
            ),
        )
        write_unified_health(
            self.cfg,
            _build_health_payload(
                cfg=self.cfg,
                exchange=self.exchange,
                scheduler=self.scheduler,
            ),
        )
        write_unified_checkpoint(
            self.cfg,
            {
                "ts": now_iso_utc(),
                "collector_id": self.cfg.collector_id,
                "session_id": self.session_id,
                "runtime_kind": "unified",
                "exchange": self.exchange,
                "last_rest_request_class": dispatch,
                "last_ws_event_ts": None,
                "ok": ok,
            },
        )

        _emit_runtime_audit(
            f"collector_vnext.unified.{dispatch}.completed"
            if ok
            else f"collector_vnext.unified.{dispatch}.failed",
            collector_id=self.cfg.collector_id,
            collector_role=self.cfg.collector_role,
            symbol=self.cfg.symbol,
            session_id=self.session_id,
            topic=dispatch,
            ok=ok,
            elapsed_ms=elapsed_ms,
            extra=last_result or {},
        )

        if after_mode != before_mode:
            _emit_runtime_audit(
                "collector_vnext.unified.mode.changed",
                collector_id=self.cfg.collector_id,
                collector_role=self.cfg.collector_role,
                symbol=self.cfg.symbol,
                session_id=self.session_id,
                topic=after_mode.lower(),
                ok=True,
                extra={
                    "from_mode": before_mode,
                    "to_mode": after_mode,
                    "exchange": self.exchange,
                    "request_class": dispatch,
                    "status_code": status_code,
                    "retry_after_sec": retry_after_sec,
                },
            )

        print(
            json.dumps(
                {
                    "ok": ok,
                    "collector_id": self.cfg.collector_id,
                    "collector_role": self.cfg.collector_role,
                    "runtime_kind": "unified",
                    "exchange": self.exchange,
                    "request_class": dispatch,
                    "result": last_result,
                    "rate_state": snapshot,
                },
                ensure_ascii=False,
            )
        )
        return 0 if ok else 1


_RUNTIME = UnifiedRuntime()


def run_once() -> int:
    return _RUNTIME.run_once()


def main() -> int:
    return run_once()


if __name__ == "__main__":
    raise SystemExit(main())