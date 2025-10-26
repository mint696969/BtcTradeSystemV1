# path: ./tools/collector/leader_status_bridge.py
# desc: LeaderLockのメタをstatus.jsonのleaderへワンショット反映（開発テスト用）

from __future__ import annotations
from btc_trade_system.features.collector.core.leader_lock import LeaderLock
from btc_trade_system.features.collector.core.status import StatusWriter

def main() -> int:
    lk = LeaderLock.from_env(stale_after_sec=30)
    acquired = lk.acquire()
    try:
        sw = StatusWriter()
        sw.set_leader(host=lk.host, pid=lk.pid, started_ms=lk.started_ms, heartbeat_ms=lk._utc_ms())
        sw.flush()
        print("leader -> status.json updated")
    finally:
        if acquired:
            lk.renew()
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
