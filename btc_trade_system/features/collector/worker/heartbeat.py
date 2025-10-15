# path: ./btc_trade_system/features/collector/worker/heartbeat.py
# desc: LeaderLock の renew と status.leader の heartbeat を一定間隔で更新する最小ループ（開発フェーズ用）

from __future__ import annotations
import os, signal, time
from typing import Optional

from btc_trade_system.features.collector.core.leader_lock import LeaderLock
from btc_trade_system.features.collector.core.status import StatusWriter


def _int(name: str, default: int) -> int:
    try:
        return int(os.environ.get(name, default))
    except Exception:
        return default


def run(interval_sec: Optional[int] = None, stale_after_sec: int = 30) -> int:
    """
    interval_sec: 心拍周期（秒）; ENV BTC_TS_HEARTBEAT_SEC があれば優先
    stale_after_sec: リーダーのステール判定（秒）
    終了は Ctrl+C (KeyboardInterrupt) または SIGTERM
    """
    beat = interval_sec or _int("BTC_TS_HEARTBEAT_SEC", 10)
    lk = LeaderLock.from_env(stale_after_sec=stale_after_sec)

    acquired = lk.acquire()
    # acquire できなくても renew 試行は続ける（他プロセスに切り替わる可能性を考慮）

    sw = StatusWriter()
    stop = False

    def _on_term(signum, frame):
        nonlocal stop
        stop = True

    for sig in (signal.SIGINT, signal.SIGTERM):
        try:
            signal.signal(sig, _on_term)
        except Exception:
            pass

    while not stop:
        # renew (自分が所有者のときのみ True)
        owned = lk.renew()
        # status.json の leader も併せて更新（UI 注釈用）
        sw.set_leader(host=lk.host, pid=lk.pid, started_ms=lk.started_ms, heartbeat_ms=lk._utc_ms())
        sw.flush()
        time.sleep(beat)

    # 明示解放（所有者の場合のみ）
    lk.release()
    return 0


if __name__ == "__main__":
    import argparse

    ap = argparse.ArgumentParser(description="collector heartbeat loop")
    ap.add_argument("--interval", type=int, default=None, help="heartbeat interval seconds (default env BTC_TS_HEARTBEAT_SEC or 10)")
    ap.add_argument("--stale", type=int, default=30, help="stale seconds")
    ns = ap.parse_args()
    raise SystemExit(run(interval_sec=ns.interval, stale_after_sec=ns.stale))
