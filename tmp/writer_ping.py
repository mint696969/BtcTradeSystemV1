# path: ./tmp/writer_ping.py
# desc: writer を BOOST にして INFO を5行 emit する
import time
from btc_trade_system.features.audit_dev import writer as w
w.set_mode("BOOST")
for i in range(5):
    w.emit("dev.diag.ping", level="INFO", feature="audit_dev", note=f"ping {i}")
    time.sleep(0.05)
print("done")
