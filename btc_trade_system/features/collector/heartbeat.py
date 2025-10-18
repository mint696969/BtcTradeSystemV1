# path: ./btc_trade_system/features/collector/heartbeat.py
# desc: LeaderLock の renew と status.leader の heartbeat を一定間隔で更新する最小ループ（開発フェーズ用）

from __future__ import annotations
import os, signal, time
from typing import Optional
from btc_trade_system.features.collector.leader_lock import LeaderLock
from btc_trade_system.features.collector.status import StatusWriter
from btc_trade_system.common.audit import audit_ok, audit_warn, audit_err

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

    # 監査：起動
    audit_ok("collector.heartbeat.start", feature="collector",
             payload={"beat_sec": beat, "stale_after_sec": stale_after_sec,
                      "host": lk.host, "pid": lk.pid})

    # 監査：リーダー取得に成功した場合
    if acquired:
        audit_ok("collector.leader.transition", feature="collector",
                 to="ACQUIRE", host=lk.host, pid=lk.pid)

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

    prev_owned = False

    while not stop:
        # renew (自分が所有者のときのみ True)
        t0 = time.perf_counter()
        try:
            owned = lk.renew()

            latency_ms = (time.perf_counter() - t0) * 1000.0
            # 周期の 2倍を超えたら遅延警告（DEBUG 以上で採取）
            if latency_ms > (beat * 2000):
                audit_warn("collector.heartbeat.slow", feature="collector",
                           host=lk.host, pid=lk.pid, latency_ms=int(latency_ms))
            # リーダーの取得/喪失を検知
            if owned != prev_owned:
                audit_ok("collector.leader.transition", feature="collector",
                         to=("ACQUIRE" if owned else "RELEASE"),
                         host=lk.host, pid=lk.pid)
                prev_owned = owned

            # status.json の leader も併せて更新（UI 注釈用）
            sw.set_leader(host=lk.host, pid=lk.pid, started_ms=lk.started_ms, heartbeat_ms=lk._utc_ms())
            sw.flush()

        except Exception as e:
            # renew / status 書き込みの失敗は監査して継続（本流を止めない）
            audit_err("collector.heartbeat.fail", feature="collector",
                      host=lk.host, pid=lk.pid, cause=type(e).__name__, message=str(e))

        time.sleep(beat)

    # 所有していれば RELEASE 遷移を監査
    try:
        if lk.is_owner():
            audit_ok("collector.leader.transition", feature="collector",
                     to="RELEASE", host=lk.host, pid=lk.pid)
    except Exception:
        pass

    # 監査：停止
    audit_ok("collector.heartbeat.stop", feature="collector",
             host=lk.host, pid=lk.pid)

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
