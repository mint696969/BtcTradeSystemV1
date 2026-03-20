# path: ./btcts_next/src/btcts/collector_vnext/app.py
# desc: Smoke entrypoint for Collector vNext that runs one qualification cycle and writes state outputs.

from __future__ import annotations

import json
import time

from btcts.core import audit

from .config import load_config
from .events import now_iso_utc
from .rate_runtime import VNextRateRuntime
from .run_smoke import build_status, run_smoke
from .state import write_checkpoint, write_health, write_status


def _emit_component_audit(
    event: str,
    *,
    collector_id: str,
    collector_role: str,
    symbol: str,
    session_id: str,
    topic: str,
    stream_session_id: str | None = None,
    ok: bool = True,
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
        "stream_session_id": stream_session_id,
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
        actor="collector_vnext.app",
        site="collector_vnext.app.main",
        payload=payload,
    )


def main() -> int:
    cfg = load_config()

    rate_runtime = VNextRateRuntime.build(cfg)

    started_at = time.perf_counter()
    result = run_smoke(cfg, rate_runtime=rate_runtime)
    elapsed_ms = round((time.perf_counter() - started_at) * 1000.0, 1)
    session_id = str(result["session_id"])
    board = result["board"]
    rest_trades = result["rest_trades"]
    ws_trades = result["ws_trades"]
    ws_board = result["ws_board"]

    rate_runtime.write_snapshot()

    _emit_component_audit(
        "collector_vnext.board_snapshot.completed",
        collector_id=cfg.collector_id,
        collector_role=cfg.collector_role,
        symbol=cfg.symbol,
        session_id=session_id,
        topic="board_snapshot",
        stream_session_id=board.get("stream_session_id"),
        ok=True,
        extra={
            "raw_path": board.get("raw_path"),
            "canonical_path": board.get("canonical_path"),
        },
    )

    _emit_component_audit(
        "collector_vnext.rest_trades.completed",
        collector_id=cfg.collector_id,
        collector_role=cfg.collector_role,
        symbol=cfg.symbol,
        session_id=session_id,
        topic="executions",
        stream_session_id=rest_trades.get("stream_session_id"),
        ok=True,
        extra={
            "raw_path": rest_trades.get("raw_path"),
            "canonical_path": rest_trades.get("canonical_path"),
            "trade_count": rest_trades.get("trade_count"),
        },
    )

    _emit_component_audit(
        "collector_vnext.ws_trades.completed" if ws_trades.get("ok") else "collector_vnext.ws_trades.failed",
        collector_id=cfg.collector_id,
        collector_role=cfg.collector_role,
        symbol=cfg.symbol,
        session_id=session_id,
        topic="executions_ws",
        stream_session_id=ws_trades.get("info", {}).get("stream_session_id"),
        ok=bool(ws_trades.get("ok")),
        extra={
            "raw_path": ws_trades.get("info", {}).get("raw_path"),
            "canonical_path": ws_trades.get("info", {}).get("canonical_path"),
            "trade_count": ws_trades.get("info", {}).get("trade_count"),
            "error": ws_trades.get("error"),
            "ssl_verify": ws_trades.get("info", {}).get("ssl_verify"),
        },
    )

    _emit_component_audit(
        "collector_vnext.ws_board.completed" if ws_board.get("ok") else "collector_vnext.ws_board.failed",
        collector_id=cfg.collector_id,
        collector_role=cfg.collector_role,
        symbol=cfg.symbol,
        session_id=session_id,
        topic="board_ws",
        stream_session_id=ws_board.get("info", {}).get("stream_session_id"),
        ok=bool(ws_board.get("ok")),
        extra={
            "raw_path": ws_board.get("info", {}).get("raw_path"),
            "canonical_path": ws_board.get("info", {}).get("canonical_path"),
            "event_type": ws_board.get("info", {}).get("event_type"),
            "error": ws_board.get("error"),
            "ssl_verify": ws_board.get("info", {}).get("ssl_verify"),
        },
    )

    status_message = "collector_vnext smoke cycle completed: bootstrap + rest board/trades"
    status_mode = "RUNNING"

    if ws_trades["ok"]:
        status_message += " + ws trade check completed"
    else:
        status_message += " + ws trade check timeout(warn)"

    if ws_board["ok"]:
        status_message += " + ws board check completed"
    else:
        status_message += " + ws board check failed"
        status_mode = "DEGRADED"

    rate_state = rate_runtime.snapshot()
    rate_items = rate_state.get("items") if isinstance(rate_state, dict) else {}
    if isinstance(rate_items, dict) and rate_items:
        first_item = next(iter(rate_items.values()))
        status_rate_control = {
            "summary_state": str(first_item.get("summary_state") or "NORMAL"),
            "engaged": bool(first_item.get("engaged", False)),
            "reason": str(first_item.get("reason") or ""),
            "wait_ms": int(first_item.get("wait_ms") or 0),
            "util_ratio": float(first_item.get("util_ratio") or 0.0),
            "last_429_ts": first_item.get("last_429_ts"),
            "recovery_phase": str(first_item.get("recovery_phase") or "steady"),
        }
    else:
        status_rate_control = {
            "summary_state": "NORMAL",
            "engaged": False,
            "reason": "",
            "wait_ms": 0,
        }

    ws_board_info = ws_board.get("info", {}) if isinstance(ws_board.get("info"), dict) else {}
    status_origin_continuity = {
        "ws_state": ws_board_info.get("ws_state"),
        "snapshot_to_live_ms": ws_board_info.get("snapshot_to_live_ms"),
        "resync_occurred": ws_board_info.get("resync_occurred"),
        "pre_snapshot_delta_drop_count": ws_board_info.get("pre_snapshot_delta_drop_count"),
        "event_type": ws_board_info.get("event_type"),
        "stream_session_id": ws_board_info.get("stream_session_id"),
    }

    write_status(
        cfg,
        build_status(
            mode=status_mode,
            message=status_message,
            session_id=session_id,
            stream_session_id=str(board["stream_session_id"]),
            consecutive_failures=0,
            last_error=ws_board.get("error") or ws_trades.get("error"),
            last_success_ts=now_iso_utc(),
            ws_trades_warn_streak=0 if ws_trades["ok"] else 1,
            rate_control=status_rate_control,
            origin_continuity=status_origin_continuity,
        ),
    )

    checks = [
        {"name": "bootstrap", "result": "ok"},
        {"name": "bitflyer_rest_board", "result": "ok"},
        {"name": "bitflyer_rest_executions", "result": "ok"},
    ]

    if ws_trades["ok"]:
        checks.append({"name": "bitflyer_ws_executions", "result": "ok"})
    else:
        checks.append(
            {
                "name": "bitflyer_ws_executions",
                "result": "warn",
                "error": ws_trades["error"],
                "ssl_verify": cfg.ws_ssl_verify,
            }
        )

    if ws_board["ok"]:
        checks.append({"name": "bitflyer_ws_board", "result": "ok"})
    else:
        checks.append(
            {
                "name": "bitflyer_ws_board",
                "result": "warn",
                "error": ws_board["error"],
                "ssl_verify": cfg.ws_ssl_verify,
            }
        )

    health_ok = all(
        check.get("result") == "ok"
        or (
            check.get("name") == "bitflyer_ws_executions"
            and check.get("result") == "warn"
        )
        for check in checks
    )
    health_status = "healthy" if health_ok else "degraded"

    _emit_component_audit(
        "collector_vnext.run_smoke.completed",
        collector_id=cfg.collector_id,
        collector_role=cfg.collector_role,
        symbol=cfg.symbol,
        session_id=session_id,
        topic="collector_vnext_smoke",
        ok=health_ok,
        elapsed_ms=elapsed_ms,
        extra={
            "last_sequence_id": result.get("last_sequence_id"),
            "ws_ssl_verify": cfg.ws_ssl_verify,
            "health_status": health_status,
            "rate_state_path": str(cfg.roots()["state"] / "rate_state.json"),
        },
    )

    write_health(
        cfg,
        {
            "ts": now_iso_utc(),
            "ok": health_ok,
            "status": health_status,
            "collector_vnext": True,
            "session_id": session_id,
            "stream_session_id": str(board["stream_session_id"]),
            "checks": checks,
        },
    )

    write_checkpoint(
        cfg,
        {
            "ts": now_iso_utc(),
            "collector_id": cfg.collector_id,
            "session_id": session_id,
            "last_sequence_id": result["last_sequence_id"],
            "last_symbol": cfg.symbol,
            "last_exchange": "bitflyer",
            "last_channel": "board_ws" if ws_board["ok"] else ("executions_ws" if ws_trades["ok"] else "executions"),
        },
    )

    print(
        json.dumps(
            {
                "ok": health_ok,
                "collector_id": cfg.collector_id,
                "collector_role": cfg.collector_role,
                "status": status_mode,
                "session_id": session_id,
                "board": board,
                "rest_trades": rest_trades,
                "ws_trades": ws_trades,
                "ws_board": ws_board,
            },
            ensure_ascii=False,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())