# path: ./btcts_next/src/btcts/collector_vnext/exploration_runtime.py
# desc: Exploration Runtime の最小本体。scheduler に従って REST support layer を高密度で回す。

from __future__ import annotations

import json
import os
import time
from pathlib import Path

from btcts.core import audit

from .config import load_config
from .emit_rest import (
    RestRequestFailedError,
    emit_rest_board_snapshot,
    emit_rest_trades,
)
from .events import now_iso_utc
from .exploration_config import load_exploration_runtime_config
from .exploration_scheduler import ExplorationScheduler
from .exploration_state import (
    write_exploration_checkpoint,
    write_exploration_health,
    write_exploration_rate_state,
    write_exploration_scheduler_state,
    write_exploration_status,
)
from .ids import SequenceManager


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

    audit.emit(
        event,
        level="INFO" if ok else "WARN",
        feature="collector_vnext",
        actor="collector_vnext.exploration_runtime",
        site="collector_vnext.exploration_runtime.run_once",
        payload=payload,
    )


def _env_force_429_request_class() -> str:
    return str(os.getenv("BTCTS_EXPLORATION_FORCE_429_CLASS", "") or "").strip().lower()


def _env_force_429_retry_after_sec() -> float:
    raw = str(os.getenv("BTCTS_EXPLORATION_FORCE_429_RETRY_AFTER_SEC", "") or "").strip()
    if not raw:
        return 0.0
    try:
        return max(float(raw), 0.0)
    except Exception:
        return 0.0


def _load_scheduler_state(cfg) -> dict:
    if str(os.getenv("BTCTS_EXPLORATION_TEST_RESET_STATE", "") or "").strip() in {"1", "true", "yes", "on"}:
        return {}

    path = Path(cfg.roots()["state"]) / "exploration_scheduler_state.json"
    if not path.exists():
        return {}

    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


def _load_previous_request_class(cfg, exchange: str) -> str | None:
    path = Path(cfg.roots()["state"]) / "exploration_rate_state.json"
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
    mode = str(rate_item.get("mode") or "NORMAL")

    message = (
        f"collector_vnext exploration runtime active "
        f"mode={mode} requests_60s={rate_item.get('requests_60s', 0)} "
        f"requests_300s={rate_item.get('requests_300s', 0)}"
    )

    if mode == "CRIT":
        status_mode = "DEGRADED"
    else:
        status_mode = "RUNNING"

    return {
        "ts": now_iso_utc(),
        "collector_id": cfg.collector_id,
        "collector_role": cfg.collector_role,
        "mode": status_mode,
        "message": message,
        "session_id": session_id,
        "last_success_ts": now_iso_utc(),
        "runtime_kind": "exploration",
        "exchange": exchange,
        "rate_control": {
            "summary_state": mode,
            "engaged": bool(rate_item.get("engaged", False)),
            "util_ratio": rate_item.get("utilization"),
            "last_429_ts": rate_item.get("last_429_ts"),
            "hold_until_ts": rate_item.get("hold_until_ts"),
        },
        "last_result": last_result or {},
    }


def _build_health_payload(
    *,
    exchange: str,
    scheduler: ExplorationScheduler,
) -> dict:
    snapshot = scheduler.snapshot()
    rate_item = ((snapshot.get("items") or {}).get(exchange) or {}) if isinstance(snapshot, dict) else {}
    mode = str(rate_item.get("mode") or "NORMAL")

    ok = mode in {"NORMAL", "WARN", "RECOVERY", "CRIT"}

    return {
        "ts": now_iso_utc(),
        "ok": ok,
        "status": "healthy" if ok else "degraded",
        "runtime_kind": "exploration",
        "exchange": exchange,
        "mode": mode,
        "requests_60s": rate_item.get("requests_60s"),
        "requests_300s": rate_item.get("requests_300s"),
        "utilization": rate_item.get("utilization"),
        "last_429_ts": rate_item.get("last_429_ts"),
        "hold_until_ts": rate_item.get("hold_until_ts"),
    }


class ExplorationRuntime:
    def __init__(self) -> None:
        self.cfg = load_config()
        self.runtime_cfg = load_exploration_runtime_config()
        self.scheduler = ExplorationScheduler(self.runtime_cfg)
        self.exchange = "bitflyer"
        self.session_id = f"{self.cfg.collector_id}-exploration"
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
            raise RuntimeError("exploration runtime is not enabled for bitflyer")

        started_at = time.perf_counter()
        dispatch = self.scheduler.next_dispatch(self.exchange)

        if dispatch is None:
            snapshot = self.scheduler.snapshot()
            write_exploration_rate_state(self.cfg, snapshot)
            write_exploration_scheduler_state(self.cfg, self.scheduler.export_state())
            write_exploration_status(
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
            write_exploration_health(
                self.cfg,
                _build_health_payload(
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
                    f"forced exploration 429 for request_class={dispatch}",
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
                raise RuntimeError(f"unsupported exploration request_class: {dispatch}")

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

        write_exploration_rate_state(self.cfg, snapshot)
        write_exploration_scheduler_state(self.cfg, self.scheduler.export_state())
        write_exploration_status(
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
        write_exploration_health(
            self.cfg,
            _build_health_payload(
                exchange=self.exchange,
                scheduler=self.scheduler,
            ),
        )
        write_exploration_checkpoint(
            self.cfg,
            {
                "ts": now_iso_utc(),
                "collector_id": self.cfg.collector_id,
                "session_id": self.session_id,
                "runtime_kind": "exploration",
                "exchange": self.exchange,
                "request_class": dispatch,
                "ok": ok,
            },
        )

        _emit_runtime_audit(
            f"collector_vnext.exploration.{dispatch}.completed"
            if ok
            else f"collector_vnext.exploration.{dispatch}.failed",
            collector_id=self.cfg.collector_id,
            collector_role=self.cfg.collector_role,
            symbol=self.cfg.symbol,
            session_id=self.session_id,
            topic=dispatch,
            ok=ok,
            elapsed_ms=elapsed_ms,
            extra=last_result or {},
        )

        print(
            json.dumps(
                {
                    "ok": ok,
                    "collector_id": self.cfg.collector_id,
                    "collector_role": self.cfg.collector_role,
                    "runtime_kind": "exploration",
                    "exchange": self.exchange,
                    "request_class": dispatch,
                    "result": last_result,
                    "rate_state": snapshot,
                },
                ensure_ascii=False,
            )
        )
        return 0 if ok else 1


_RUNTIME = ExplorationRuntime()


def run_once() -> int:
    return _RUNTIME.run_once()


def main() -> int:
    return run_once()


if __name__ == "__main__":
    raise SystemExit(main())