# path: ./tools/test_collector_vnext_dummy_429.py
# desc: Dummy 429 injection test for Collector vNext rate control visibility.

from __future__ import annotations

from _btcts_bootstrap import ensure_btcts_on_syspath
ensure_btcts_on_syspath()

import json
import os
import time
from pathlib import Path

from btcts.collector_vnext.config import load_config
from btcts.collector_vnext.events import now_iso_utc
from btcts.collector_vnext.rate_runtime import VNextRateRuntime
from btcts.collector_vnext.run_smoke import build_status
from btcts.collector_vnext.state import write_daemon_health, write_status


def _setup_env() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    tmp_root = repo_root / "tmp" / "_dummy_429_test"

    data_root = tmp_root / "data"
    logs_root = tmp_root / "logs"
    state_root = tmp_root / "state"

    os.environ["BTCTS_DATA_ROOT"] = str(data_root)
    os.environ["BTCTS_LOGS_ROOT"] = str(logs_root)
    os.environ["BTCTS_STATE_ROOT"] = str(state_root)

    # core.audit 側も同じ logs へ寄せる
    os.environ["BTC_TS_LOGS_DIR"] = str(logs_root)
    os.environ["BTC_TS_DATA_DIR"] = str(data_root)

    logs_root.mkdir(parents=True, exist_ok=True)
    state_root.mkdir(parents=True, exist_ok=True)


def _read_json(path: Path) -> dict:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def _write_statuses(cfg, rate_runtime: VNextRateRuntime, note: str) -> None:
    snap = rate_runtime.snapshot()
    items = snap.get("items") if isinstance(snap, dict) else {}
    bitflyer = items.get("bitflyer") if isinstance(items, dict) else {}

    rate_control = {
        "summary_state": str(bitflyer.get("summary_state") or "NORMAL"),
        "engaged": bool(bitflyer.get("engaged", False)),
        "reason": str(bitflyer.get("reason") or ""),
        "wait_ms": int(bitflyer.get("wait_ms") or 0),
        "util_ratio": float(bitflyer.get("util_ratio") or 0.0),
        "last_429_ts": bitflyer.get("last_429_ts"),
        "recovery_phase": str(bitflyer.get("recovery_phase") or "steady"),
    }

    write_status(
        cfg,
        build_status(
            mode="RUNNING" if rate_control["summary_state"] == "NORMAL" else "DEGRADED",
            message=note,
            session_id=f"{cfg.collector_id}-dummy-429",
            stream_session_id=f"{cfg.collector_id}-dummy-429-bitflyer",
            consecutive_failures=0,
            last_error=None,
            last_success_ts=now_iso_utc(),
            ws_trades_warn_streak=0,
            rate_control=rate_control,
        ),
    )

    write_daemon_health(
        cfg,
        {
            "ts": now_iso_utc(),
            "ok": rate_control["summary_state"] == "NORMAL",
            "status": "healthy" if rate_control["summary_state"] == "NORMAL" else "degraded",
            "collector_vnext": True,
            "daemon": True,
            "cycle_no": 0,
            "interval_sec": 0,
            "consecutive_failures": 0,
            "last_error": None,
            "last_success_ts": now_iso_utc(),
            "ws_trades_warn_streak": 0,
            "rate_control": rate_control,
        },
    )


def _print_phase(cfg, title: str) -> None:
    state_dir = Path(cfg.roots()["state"])
    rate_state = _read_json(state_dir / "rate_state.json")
    status = _read_json(state_dir / "status.json")
    daemon_health = _read_json(state_dir / "daemon_health.json")

    print("\n" + "=" * 80)
    print(title)
    print("=" * 80)
    print(json.dumps(
        {
            "rate_state": rate_state,
            "status": status,
            "daemon_health": daemon_health,
        },
        ensure_ascii=False,
        indent=2,
    ))


def main() -> int:
    _setup_env()

    cfg = load_config()
    rate_runtime = VNextRateRuntime.build(cfg)

    # baseline util
    for _ in range(3):
        rate_runtime.note_request_sent("bitflyer")
        rate_runtime.on_success("bitflyer")

    _write_statuses(cfg, rate_runtime, "baseline")
    _print_phase(cfg, "BASELINE")

    # Case A: Retry-Afterあり
    rate_runtime.on_429("bitflyer", retry_after_sec=5.0)
    _write_statuses(cfg, rate_runtime, "case_a_retry_after")
    _print_phase(cfg, "CASE A - Retry-After = 5.0")

    # 少し待って still hold
    time.sleep(1.0)
    rate_runtime.on_success("bitflyer")
    _write_statuses(cfg, rate_runtime, "case_a_still_holding")
    _print_phase(cfg, "CASE A - still holding")

    # Case B: Retry-Afterなし
    rate_runtime.on_429("bitflyer", retry_after_sec=0.0)
    _write_statuses(cfg, rate_runtime, "case_b_no_retry_after")
    _print_phase(cfg, "CASE B - Retry-After = 0.0")

    # Case C: 連続429
    rate_runtime.on_429("bitflyer", retry_after_sec=0.0)
    rate_runtime.on_429("bitflyer", retry_after_sec=0.0)
    _write_statuses(cfg, rate_runtime, "case_c_repeated_429")
    _print_phase(cfg, "CASE C - repeated 429")

    # Case D: 回復確認
    # cooldown 明け後に util を WARN -> NORMAL へ寄せる
    time.sleep(4.0)
    rate_runtime.note_request_sent("bitflyer")
    rate_runtime.on_success("bitflyer")
    rate_runtime.rc.set_mode_by_util("bitflyer", 0.5)
    rate_runtime.write_snapshot()
    _write_statuses(cfg, rate_runtime, "case_d_recovering_warn")
    _print_phase(cfg, "CASE D - recovering WARN")

    time.sleep(4.0)
    rate_runtime.rc.set_mode_by_util("bitflyer", 0.0)
    rate_runtime.write_snapshot()
    _write_statuses(cfg, rate_runtime, "case_d_released_normal")
    _print_phase(cfg, "CASE D - released NORMAL")

    print("\nstate_dir =", cfg.roots()["state"])
    print("logs_dir  =", os.environ.get("BTC_TS_LOGS_DIR"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())