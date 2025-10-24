# path: ./tmp/test_snapshot_rate.py
# desc: force=False 連打では mtime が更新されないことを確認する
import time, pathlib
from btc_trade_system.features.audit_dev.boost import export_and_build_text

LOG = pathlib.Path(r"D:\BtcTS_V1\logs") / "boost_snapshot.json"

# 事前に一度強制生成
export_and_build_text(mode="BOOST", force=True)
t1 = LOG.stat().st_mtime

# 2秒後に通常生成（force=False）
time.sleep(2)
export_and_build_text(mode="BOOST", force=False)
t2 = LOG.stat().st_mtime

print("t1=", t1, " t2=", t2, " delta=", t2 - t1)
# 10秒未満なら変わらないのが期待
print("rate_limit_ok=", (t2 == t1))
