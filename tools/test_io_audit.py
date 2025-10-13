# path: tools/test_io_audit.py
# desc: io_safe / audit の最小動作テスト
from btc_trade_system.common import io_safe, audit, paths
from pathlib import Path

paths.ensure_dirs()

# 1) atomic 書き込みテスト
target = paths.data_dir() / "latest" / "signal-latest.csv"
io_safe.write_atomic_text(target, "ts,symbol,score\n1730000000000,BTC/USDT,0.51\n")

# 2) 監査テスト
audit.audit("unittest.io_safe", feature="common", payload={"target": str(target)})

print("OK atomic->", target)
print("OK audit ->", paths.logs_dir() / "audit.jsonl")
