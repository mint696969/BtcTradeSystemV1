# path: ./tools/test_collector_entry.py
# desc: Collector Scheduler 疑似テスト用エントリ（audit / rate_state / status を安全に検証）

import os
import sys
import time
import threading
from pathlib import Path
from typing import Callable

# --- ensure btcts import (no PYTHONPATH required) ---
REPO = Path(__file__).resolve().parents[1]
BTCTS_SRC = REPO / "btcts_next" / "src"
if str(BTCTS_SRC) not in sys.path:
    sys.path.insert(0, str(BTCTS_SRC))

from btcts.collector.scheduler import Scheduler, Endpoint, EndpointSkipped
from btcts.core import audit

# 実行モード: ok | skip | error | hang | ok_then_hang | ok_then_error
MODE = (
    (os.environ.get("BTC_TS_TEST_MODE_FORCE", "") or "").strip()
    or (os.environ.get("BTC_TS_TEST_MODE", "") or "").strip()
    or "ok"
)

# テスト時は audit を確実に出す
if not (os.environ.get("BTC_TS_MODE", "") or "").strip():
    os.environ["BTC_TS_MODE"] = "DEBUG"

def _env_float(name: str, default: float) -> float:
    s = (os.environ.get(name, "") or "").strip()
    if not s:
        return float(default)
    return float(s)

def _env_int(name: str, default: int) -> int:
    s = (os.environ.get(name, "") or "").strip()
    if not s:
        return int(default)
    return int(s)

# -------------------------
# runner 定義（最小ダミー）
# -------------------------
def runner_ok(*_args, **_kwargs):
    return {"ok": True}

def runner_skip(*_args, **_kwargs):
    raise EndpointSkipped("skip for test")

def runner_error(*_args, **_kwargs):
    raise RuntimeError("error for test")

def runner_hang(*_args, **_kwargs):
    sec = _env_int("BTC_TS_TEST_HANG_SEC", 9999)
    if sec < 0:
        raise RuntimeError(f"BTC_TS_TEST_HANG_SEC must be >= 0: {sec}")
    time.sleep(sec)

def runner_ok_then_hang(*_args, **_kwargs):
    time.sleep(1)
    return runner_hang()

def runner_ok_then_error(*_args, **_kwargs):
    time.sleep(1)
    return runner_error()

RUNNERS: dict[str, Callable] = {
    "ok": runner_ok,
    "skip": runner_skip,
    "error": runner_error,
    "hang": runner_hang,
    "ok_then_hang": runner_ok_then_hang,
    "ok_then_error": runner_ok_then_error,
}

# -------------------------
# Dummy RateController
# -------------------------
class DummyRateController:
    def acquire(self, ex: str):
        return True, 0

    def note_util(self, ex: str, util: float):
        return None

    def on_http_429(self, ex: str, retry_after_sec: float | None = None):
        return None

    def snapshot(self):
        return {"testex": {"mode": "NORMAL", "util": 0.0}}

def main():
    run_sec = _env_float("BTC_TS_TEST_RUN_SEC", 0.0)
    exit_code = _env_int("BTC_TS_TEST_EXIT_CODE", 0)
    if run_sec > 0:
        def _force_exit():
            print(f"[test] auto-exit after {run_sec}s (exit_code={exit_code})")
            os._exit(exit_code)
        t = threading.Timer(run_sec, _force_exit)
        t.daemon = True
        t.start()

    print(f"[test] BTC_TS_DATA_DIR={os.environ.get('BTC_TS_DATA_DIR','')}")
    print(f"[test] BTC_TS_LOGS_DIR={os.environ.get('BTC_TS_LOGS_DIR','')}")
    print(f"[test] pid={os.getpid()} mode={MODE}")

    if MODE not in RUNNERS:
        raise RuntimeError(f"Unknown BTC_TS_TEST_MODE={MODE!r}. allowed={sorted(RUNNERS.keys())}")

    dangerous = {"hang", "ok_then_hang"}
    force = (os.environ.get("BTC_TS_TEST_MODE_FORCE", "") or "").strip()
    if MODE in dangerous and not force:
        raise RuntimeError(
            f"Refusing dangerous mode without BTC_TS_TEST_MODE_FORCE: mode={MODE!r}. "
            f"Set BTC_TS_TEST_MODE_FORCE={MODE} explicitly."
        )

    audit.emit(
        "test.start",
        feature="test",
        level="INFO",
        payload={"mode": MODE, "pid": os.getpid(), "runner": MODE},
    )

    rc = DummyRateController()
    sch = Scheduler(rc)
    runner = RUNNERS[MODE]

    sch.add(
        Endpoint(
            exchange="testex",
            endpoint="testtopic",
            priority=0,
            target_interval=1.0,
            runner=runner,
        )
    )

    sch.run_forever(
        tick_sec=_env_float("BTC_TS_TEST_TICK_SEC", 0.1),
        status_every_sec=_env_float("BTC_TS_TEST_STATUS_EVERY_SEC", 2.0),
        rate_state_every_sec=_env_float("BTC_TS_TEST_RATE_STATE_EVERY_SEC", 10.0),
        startup_grace_sec=_env_float("BTC_TS_TEST_STARTUP_GRACE_SEC", 5.0),
        no_data_check_every_sec=_env_float("BTC_TS_TEST_NO_DATA_CHECK_EVERY_SEC", 1.0),
    )

if __name__ == "__main__":
    main()
