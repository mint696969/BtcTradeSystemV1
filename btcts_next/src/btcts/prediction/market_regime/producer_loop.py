# path: ./btcts_next/src/btcts/prediction/market_regime/producer_loop.py
# desc: Controlled MarketRegime inference producer loop. Reads explicit hot root, preflights each cycle, writes latest artifacts only when safe, and obeys control.json stop/restart requests. No broker, AutoTrade, order, trade ledger, or parameter auto-promotion.

from __future__ import annotations

import argparse
import json
import time
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Mapping
from uuid import uuid4

from .operator_ui_runtime import market_regime_hot_root, market_regime_operator_ui_paths
from .tools.write_latest import preflight_market_regime_latest_artifacts_once, write_market_regime_latest_artifacts_once

MARKET_REGIME_PRODUCER_LOOP_VERSION = "prediction.market_regime.producer_loop.2026_07_08.v1"
DEFAULT_INTERVAL_SEC = 30


def _now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}
    return dict(payload) if isinstance(payload, dict) else {}


def _write_json(path: Path, payload: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(dict(payload), ensure_ascii=False, sort_keys=True, indent=2) + "\n", encoding="utf-8")


def market_regime_producer_loop_paths(hot_root: Path | None = None) -> dict[str, Path]:
    base = market_regime_operator_ui_paths(hot_root)
    state_dir = base["state_dir"]
    return {
        **base,
        "control": state_dir / "control.json",
        "loop_status": state_dir / "producer_loop_status.json",
        "loop_heartbeat": state_dir / "producer_loop_heartbeat.json",
    }


@dataclass(frozen=True)
class MarketRegimeProducerLoopConfig:
    hot_root: str
    interval_sec: int = DEFAULT_INTERVAL_SEC
    max_iterations: int = 0
    preflight_required: bool = True
    write_when_preflight_blocks: bool = False

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _safety() -> dict[str, Any]:
    return {
        "preflight_required": True,
        "write_when_preflight_blocks": False,
        "controlled_loop_only": True,
        "detached_process_started": False,
        "collector_button_linked": False,
        "scheduler_external_enabled": False,
        "broker_private_api_allowed": False,
        "autotrade_trigger_allowed": False,
        "order_intent_submitted": False,
        "trade_ledger_append_allowed": False,
        "parameter_auto_promotion_allowed": False,
        "would_send_to_broker": False,
    }


def write_market_regime_producer_control_request(
    hot_root: str | Path | None,
    *,
    action: str,
    reason: str = "operator_request",
    requested_by: str = "operator_ui",
) -> dict[str, Any]:
    root = Path(hot_root) if hot_root is not None else market_regime_hot_root()
    paths = market_regime_producer_loop_paths(root)
    action_norm = str(action or "").strip().lower()
    if action_norm not in {"safe_stop", "restart", "clear"}:
        raise ValueError(f"unsupported market-regime producer control action: {action}")
    if action_norm == "clear":
        try:
            paths["control"].unlink(missing_ok=True)
        except Exception:
            pass
        return {"ok": True, "action": "clear", "control_path": str(paths["control"])}
    request = {
        "ok": True,
        "version": MARKET_REGIME_PRODUCER_LOOP_VERSION,
        "request_id": uuid4().hex,
        "action": action_norm,
        "requested_at": _now_iso(),
        "requested_by": requested_by,
        "reason": reason,
        "safety": _safety(),
    }
    _write_json(paths["control"], request)
    return {"ok": True, "action": action_norm, "request": request, "control_path": str(paths["control"])}


def market_regime_producer_loop_snapshot(hot_root: str | Path | None = None) -> dict[str, Any]:
    root = Path(hot_root) if hot_root is not None else market_regime_hot_root()
    paths = market_regime_producer_loop_paths(root)
    status = _read_json(paths["loop_status"])
    heartbeat = _read_json(paths["loop_heartbeat"])
    control = _read_json(paths["control"])
    return {
        "ok": True,
        "version": MARKET_REGIME_PRODUCER_LOOP_VERSION,
        "hot_root": str(paths["hot_root"]),
        "state_dir": str(paths["state_dir"]),
        "control_path": str(paths["control"]),
        "loop_status_path": str(paths["loop_status"]),
        "heartbeat_path": str(paths["loop_heartbeat"]),
        "mode": str(status.get("mode") or "STOPPED"),
        "active": bool(status.get("active", False)),
        "iteration": int(status.get("iteration") or 0),
        "latest_run_id": str(status.get("latest_run_id") or ""),
        "last_error": str(status.get("last_error") or ""),
        "pending_action": str(control.get("action") or ""),
        "last_heartbeat_ts": heartbeat.get("ts") or status.get("ts") or "",
        "status": status,
        "heartbeat": heartbeat,
        "control": control,
        "safety": _safety(),
    }


def _write_status(paths: Mapping[str, Path], payload: Mapping[str, Any]) -> None:
    _write_json(paths["loop_status"], {"version": MARKET_REGIME_PRODUCER_LOOP_VERSION, **dict(payload), "safety": _safety()})


def _write_heartbeat(paths: Mapping[str, Path], payload: Mapping[str, Any]) -> None:
    _write_json(paths["loop_heartbeat"], {"version": MARKET_REGIME_PRODUCER_LOOP_VERSION, **dict(payload), "safety": _safety()})


def run_market_regime_producer_loop(
    *,
    hot_root: str | Path | None = None,
    interval_sec: int = DEFAULT_INTERVAL_SEC,
    max_iterations: int = 0,
    sleep_fn: Callable[[float], None] = time.sleep,
) -> dict[str, Any]:
    root = Path(hot_root) if hot_root is not None else market_regime_hot_root()
    paths = market_regime_producer_loop_paths(root)
    interval = max(0, int(interval_sec))
    max_iter = max(0, int(max_iterations))
    config = MarketRegimeProducerLoopConfig(hot_root=str(paths["hot_root"]), interval_sec=interval, max_iterations=max_iter)
    paths["state_dir"].mkdir(parents=True, exist_ok=True)
    _write_status(
        paths,
        {
            "ok": True,
            "mode": "RUNNING",
            "active": True,
            "ts": _now_iso(),
            "iteration": 0,
            "config": config.to_dict(),
            "latest_run_id": "",
            "last_error": "",
        },
    )
    iterations = 0
    writes = 0
    blocked = 0
    stop_reason = "max_iterations_reached" if max_iter else "control_stop_required"
    last_result: dict[str, Any] = {}
    while True:
        control = _read_json(paths["control"])
        action = str(control.get("action") or "").strip().lower()
        if action in {"safe_stop", "stop"}:
            stop_reason = "safe_stop_requested"
            break
        if action == "restart":
            stop_reason = "restart_requested"
            break
        iterations += 1
        now = _now_iso()
        try:
            preflight = preflight_market_regime_latest_artifacts_once(hot_root=paths["hot_root"])
            can_write = bool(preflight.get("can_write_live_once"))
            if can_write:
                write_result = write_market_regime_latest_artifacts_once(hot_root=paths["hot_root"])
                writes += 1
                last_result = dict(write_result)
                mode = "RUNNING_WRITE_OK"
                latest_run_id = str(write_result.get("run_id") or "")
                last_error = ""
            else:
                blocked += 1
                last_result = dict(preflight)
                mode = "RUNNING_PREFLIGHT_BLOCKED"
                latest_run_id = ""
                last_error = "preflight_blocked"
            _write_heartbeat(
                paths,
                {
                    "ok": True,
                    "mode": mode,
                    "active": True,
                    "ts": now,
                    "iteration": iterations,
                    "writes": writes,
                    "blocked": blocked,
                    "latest_run_id": latest_run_id,
                    "last_error": last_error,
                    "preflight_can_write": can_write,
                    "card_count": int(last_result.get("card_count") or 0),
                    "source_snapshot_ok": bool(last_result.get("source_snapshot_ok")),
                },
            )
            _write_status(
                paths,
                {
                    "ok": True,
                    "mode": mode,
                    "active": True,
                    "ts": now,
                    "iteration": iterations,
                    "writes": writes,
                    "blocked": blocked,
                    "latest_run_id": latest_run_id,
                    "last_error": last_error,
                    "config": config.to_dict(),
                },
            )
        except Exception as exc:
            blocked += 1
            last_result = {"ok": False, "error": str(exc)}
            _write_status(
                paths,
                {
                    "ok": False,
                    "mode": "RUNNING_ERROR",
                    "active": True,
                    "ts": now,
                    "iteration": iterations,
                    "writes": writes,
                    "blocked": blocked,
                    "latest_run_id": "",
                    "last_error": str(exc),
                    "config": config.to_dict(),
                },
            )
        if max_iter and iterations >= max_iter:
            stop_reason = "max_iterations_reached"
            break
        if interval > 0:
            sleep_fn(float(interval))
    finished = {
        "ok": True,
        "version": MARKET_REGIME_PRODUCER_LOOP_VERSION,
        "mode": "STOPPED",
        "active": False,
        "ts": _now_iso(),
        "hot_root": str(paths["hot_root"]),
        "iteration": iterations,
        "writes": writes,
        "blocked": blocked,
        "stop_reason": stop_reason,
        "last_result_ok": bool(last_result.get("ok", False)),
        "last_error": str(last_result.get("error") or ""),
        "config": config.to_dict(),
        "safety": _safety(),
    }
    _write_json(paths["loop_status"], finished)
    return finished


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run controlled MarketRegime producer loop.")
    parser.add_argument("--hot-root", default=None, help="Hot root. Defaults to Operator UI hot root resolution.")
    parser.add_argument("--interval-sec", type=int, default=DEFAULT_INTERVAL_SEC)
    parser.add_argument("--max-iterations", type=int, default=0, help="0 means run until control safe_stop/restart request.")
    parser.add_argument("--once-loop", action="store_true", help="Required acknowledgement for loop execution entrypoint.")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)
    if not args.once_loop:
        parser.error("--once-loop acknowledgement is required; loop must be started by explicit operator control")
    result = run_market_regime_producer_loop(hot_root=args.hot_root, interval_sec=args.interval_sec, max_iterations=args.max_iterations)
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
