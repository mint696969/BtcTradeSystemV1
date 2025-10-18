# path: ./tmp/audit_where.py
# desc: 監査ログの実際の出力先を特定し、1行書き込む診断

import os, datetime as dt
from pathlib import Path
from btc_trade_system.common import paths, io_safe

print("cwd        :", os.getcwd())
print("ENV BTC_TS_MODE:", os.getenv("BTC_TS_MODE"))
try:
    logs_dir = paths.logs_dir()
    print("paths.logs_dir():", logs_dir, "(exists:", Path(logs_dir).exists(), ")")
except Exception as e:
    print("paths.logs_dir() error:", e)
    raise

# ここで ./logs/audit.jsonl とは別に、paths.logs_dir() 直下に必ず書く
dst = Path(logs_dir) / "audit.jsonl"
print("target file:", dst)

try:
    os.makedirs(logs_dir, exist_ok=True)
    line = {"ts": dt.datetime.utcnow().isoformat(timespec="milliseconds")+"Z",
            "event":"diag.write", "feature":"audit", "level":"INFO", "payload":{"probe":"where"}}
    io_safe.append_jsonl(dst, line)
    print("write ok")
except Exception as e:
    print("write failed:", e)

print("exists after write:", dst.exists(), " size:", (dst.stat().st_size if dst.exists() else 0))
