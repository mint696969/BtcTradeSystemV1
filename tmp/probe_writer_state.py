import inspect, os, sys
from pathlib import Path
from btc_trade_system.features.audit_dev import writer

print("== writer module ==", inspect.getfile(writer))
# 1) 使っているログパス候補を総当りで出力（存在しなくても出す）
candidates = []
for name in ("LOG_PATH", "LOG_FILE", "LOGS_DIR", "DEV_AUDIT_FILE", "PATH", "FILE"):
    if hasattr(writer, name):
        candidates.append((name, getattr(writer, name)))
if hasattr(writer, "logs_dir"):
    try:
        candidates.append(("logs_dir()", writer.logs_dir()))
    except Exception as e:
        candidates.append(("logs_dir()", f"ERR:{e!r}"))

print("== writer path candidates ==")
for k,v in candidates:
    print(f"{k} =", v)

# 2) モード取得が可能なら出力
mode = None
if hasattr(writer, "get_mode"):
    try:
        mode = writer.get_mode()
    except Exception as e:
        mode = f"ERR:{e!r}"
print("mode(get_mode) =", mode)

# 3) サイズ閾値やサンプリング設定っぽい定数を列挙
print("== numeric constants ==")
for name in dir(writer):
    if name.isupper():
        val = getattr(writer, name)
        if isinstance(val, (int, float)):
            print(name, "=", val)

# 4) emit の戻り値があれば確認
ok = None
try:
    writer.set_mode("BOOST") if hasattr(writer, "set_mode") else None
    ok = writer.emit("diag.probe", level="INFO", feature="audit_dev", payload={"n": 0})
except Exception as e:
    ok = f"ERR:{e!r}"
print("emit() return =", ok)

# 5) 実際にどこへ書いたかザックリ推測
#   一般には D:\BtcTS_V1\logs\dev_audit.jsonl が本命だが、ズレ検知のため直近 mtime の候補を出す
logs_dir = os.environ.get("BTC_TS_LOGS_DIR", r"D:\BtcTS_V1\logs")
p = Path(logs_dir)
print("logs_dir(env) =", p)
if p.exists():
    latest = sorted(p.glob("*.jsonl"), key=lambda x: x.stat().st_mtime, reverse=True)[:5]
    print("recent jsonl in logs_dir:")
    for f in latest:
        print(" -", f.name, "size=", f.stat().st_size)
else:
    print("logs_dir missing")
