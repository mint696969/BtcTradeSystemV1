# path: ./tools/test_rate_control_phase1.py
# desc: Phase1 APIレート制御の簡易テスト（RateController+Scheduler接続、WARN(util)→CRIT(429)→復帰の確認）。

from __future__ import annotations

import os
import sys
import time
import threading
from typing import Any, Dict

# --- 開発用 import パス調整 -----------------------------------------------
# リポ直実行時に btcts パッケージを見つけられるようにする
_THIS_DIR = os.path.dirname(__file__)
_REPO_ROOT = os.path.abspath(os.path.join(_THIS_DIR, ".."))
_SRC_ROOT = os.path.join(_REPO_ROOT, "btcts_next", "src")
if _SRC_ROOT not in sys.path:
    sys.path.insert(0, _SRC_ROOT)
# ---------------------------------------------------------------------------


def _setup_test_env() -> None:
    """本番を汚さないため、DATA_DIR/LOGS_DIR を ./tmp 配下へ寄せる。"""
    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    tmp_root = os.path.join(repo_root, "tmp", "_rate_test")
    os.makedirs(tmp_root, exist_ok=True)

    # 既存の環境変数があっても本番を汚さないよう、テストでは強制上書きする
    os.environ["BTC_TS_DATA_DIR"] = os.path.join(tmp_root, "data")
    os.environ["BTC_TS_LOGS_DIR"] = os.path.join(tmp_root, "logs")


_setup_test_env()

# ここから先は btcts の import
from btcts.core import paths  # noqa: E402

from btcts.collector.rate import RateController, RatePolicy  # noqa: E402
from btcts.collector.scheduler import Endpoint, Scheduler  # noqa: E402


def _mk_rate_control_cfg() -> Dict[str, Any]:
    """テスト用：わざと閾値を低めにして WARN/CRIT を再現しやすくする。"""
    return {
        # util window
        "util_window_warn_sec": 5,
        "util_window_clear_sec": 10,
        # thresholds
        "warn_util": 0.40,
        "warn_clear_util": 0.20,
        "crit_util": 0.90,
        # caps
        "warn_cap": 0.50,
        "crit_cap": 0.20,
        # floor
        "floor_rps": 0.10,
        # 429/backoff
        "crit_backoff_initial_sec": 1,
        "crit_backoff_max_sec": 4,
        "crit_hold_min_sec": 1,
        "no_429_for_sec": 3,
    }


def _mk_collector_cfg() -> Dict[str, Any]:
    return {
        "tick_sec": 0.02,
        "rate_state_every_sec": 0.5,
        "status_every_sec": 0.5,
        "startup_grace_sec": 1.0,
        "no_data_check_every_sec": 0.5,
    }


def _run_scheduler_for(sch: Scheduler, sec: float) -> None:
    """Scheduler を別スレで回し、指定秒数後に stop する。"""

    def _worker() -> None:
        sch.run_forever(
            tick_sec=float(getattr(sch, "_btcts_collector_cfg", {}).get("tick_sec", 0.05)),
            rate_state_every_sec=float(getattr(sch, "_btcts_collector_cfg", {}).get("rate_state_every_sec", 1.0)),
            status_every_sec=float(getattr(sch, "_btcts_collector_cfg", {}).get("status_every_sec", 2.0)),
            startup_grace_sec=float(getattr(sch, "_btcts_collector_cfg", {}).get("startup_grace_sec", 30.0)),
            no_data_check_every_sec=float(
                getattr(sch, "_btcts_collector_cfg", {}).get("no_data_check_every_sec", 1.0)
            ),
        )

    th = threading.Thread(target=_worker, daemon=True)
    th.start()
    time.sleep(sec)
    sch.stop()
    th.join(timeout=5.0)


def _unit_test_rate_controller() -> None:
    print("[UNIT] RateController basic transitions")

    rc = RateController()
    rc.set_common_policy(_mk_rate_control_cfg())

    # max_rps は低め（=utilが上がりやすい）
    rc.set_policy("bitflyer", RatePolicy(official_max_rps=2.0, soft_ratio=0.9, hard_ratio=0.8, burst_base_sec=1.0))

    # util で WARN
    mode1 = rc.set_mode_by_util("bitflyer", 0.5)
    snap1 = rc.snapshot()
    print("  mode(after util=0.5):", mode1, "eff=", snap1.get("items", {}).get("bitflyer", {}).get("eff_max_rps"))

    # 429 で CRIT + hold
    rc.on_429("bitflyer", retry_after_sec=1.0)
    snap2 = rc.snapshot()
    print("  mode(after 429):", snap2.get("items", {}).get("bitflyer", {}).get("mode"))

    # no_429_for_sec 未経過は utilで戻らない
    mode3 = rc.set_mode_by_util("bitflyer", 0.0)
    print("  mode(during no_429_for_sec):", mode3)

    time.sleep(float(_mk_rate_control_cfg()["no_429_for_sec"]) + 0.2)
    mode4 = rc.set_mode_by_util("bitflyer", 0.0)
    print("  mode(after cool down):", mode4)


def _integration_test_scheduler() -> None:
    print("[INTEG] Scheduler+RateController wiring")

    sch = Scheduler()

    # inject cfg (main.py相当)
    sch._btcts_collector_cfg = _mk_collector_cfg()  # type: ignore[attr-defined]
    sch._btcts_rate_control_cfg = _mk_rate_control_cfg()  # type: ignore[attr-defined]
    sch.rc.set_common_policy(sch._btcts_rate_control_cfg)  # type: ignore[attr-defined]

    sch.rc.set_policy("bitflyer", RatePolicy(official_max_rps=2.0, soft_ratio=0.9, hard_ratio=0.8, burst_base_sec=1.0))

    # runner: 最初は連続成功でutilを上げ、その後 429 を1回発生させる
    st = {"n": 0}

    def runner() -> bool:
        st["n"] += 1

        # まずは「データが出た」扱いを確実に作る（no_data回避）
        if st["n"] < 30:
            return True

        # 429 を模擬（仕様どおり：CRITへ落とす、ただし scheduler を例外で殺さない）
        if st["n"] == 30:
            sch.rc.on_429("bitflyer", retry_after_sec=1.0)
            return False

        # その後もデータは出続ける想定（完全停止回避）
        return True

    sch.add(
        Endpoint(
            exchange="bitflyer",
            endpoint="test",
            priority=0,
            target_interval=0.0,  # できるだけ回す（RateControllerが抑制する）
            runner=runner,
        )
    )

    t0 = time.time()
    _run_scheduler_for(sch, sec=6.0)
    dt = time.time() - t0

    snap = sch.rc.snapshot()
    bf = (snap.get("items") or {}).get("bitflyer") or {}

    print("  ran_sec=", round(dt, 2))
    print("  final_mode=", bf.get("mode"), "eff_max_rps=", bf.get("eff_max_rps"), "wait_ms=", bf.get("wait_ms"))

    # rate_state.json が生成されているか（パスは実装依存なので data_dir 配下を確認）
    data_dir = str(paths.data_dir())
    rate_state_path = os.path.join(data_dir, "collector", "rate_state.json")
    print("  rate_state_path=", rate_state_path)
    print("  rate_state_exists=", os.path.exists(rate_state_path))


def main() -> int:
    print("BTC_TS_DATA_DIR=", os.environ.get("BTC_TS_DATA_DIR"))
    print("BTC_TS_LOGS_DIR=", os.environ.get("BTC_TS_LOGS_DIR"))
    _unit_test_rate_controller()
    _integration_test_scheduler()
    print("DONE")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
