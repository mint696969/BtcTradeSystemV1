# path: ./tools/test_health_eval.py
# desc: Health(read_health) の最小スモーク（monitoring.yaml + status.json を用意して読む）

import os
import sys
from pathlib import Path
import time

REPO = Path(__file__).resolve().parents[1]
BTCTS_SRC = REPO / "btcts_next" / "src"
if str(BTCTS_SRC) not in sys.path:
    sys.path.insert(0, str(BTCTS_SRC))

# env: config は repo 内の既定を使い、data/logs は tmp に逃がす
tmp_root = REPO / "tmp" / "_health_test"
data_dir = tmp_root / "data"
logs_dir = tmp_root / "logs"

os.environ.setdefault("BTC_TS_MODE", "DEBUG")
os.environ["BTC_TS_CONFIG_DIR"] = str(REPO / "config" / "ui")
os.environ["BTC_TS_DATA_DIR"]   = str(data_dir)
os.environ["BTC_TS_LOGS_DIR"]   = str(logs_dir)

from btcts.collector.status import CollectorStatus, EndpointStatus, write_status
from btcts.health.svc import read_health

def main():
    print("[ENV] BTC_TS_CONFIG_DIR =", os.environ.get("BTC_TS_CONFIG_DIR"))
    print("[ENV] BTC_TS_DATA_DIR   =", os.environ.get("BTC_TS_DATA_DIR"))
    print("[ENV] BTC_TS_LOGS_DIR   =", os.environ.get("BTC_TS_LOGS_DIR"))

    now = time.time()
    st = CollectorStatus(
        ts_unix=now,
        mode="RUNNING",
        pid=os.getpid(),
        items=[
            EndpointStatus(exchange="testex", endpoint="testtopic", ok=True, last_ok_ts=now, last_try_ts=now),
        ],
        rate_state={"testex": {"mode": "NORMAL", "util": 0.1}},
    )
    write_status(st, emit_audit=True)

    h = read_health()
    # health dict をざっと表示（壊れてないか見る）
    import json
    print(json.dumps(h, ensure_ascii=False, indent=2))
    print("DONE")

if __name__ == "__main__":
    main()
