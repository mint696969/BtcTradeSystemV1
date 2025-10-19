# path: tmp/dev_audit_stress.py
# desc: dev_audit.jsonl を大きくしてトリム動作を即時確認するストレステスト（安全なダミー書き込みのみ）
import os, json, random, string, time
from pathlib import Path
from btc_trade_system.features.audit_dev import writer as w

w.set_mode("BOOST")
N = 120_000  # 行数。環境に応じて調整可
for i in range(N):
    payload = {"i": i, "msg": "".join(random.choices(string.ascii_letters, k=800))}
    w.emit("stress.line", level="DEBUG", feature="audit_dev", **payload)
    if i % 2000 == 0:
        print("progress:", i)

logp = Path(os.environ.get("BTC_TS_LOGS_DIR", "logs")) / "dev_audit.jsonl"
print("SIZE(MB)=", logp.stat().st_size / (1024 * 1024))
print("DONE")
