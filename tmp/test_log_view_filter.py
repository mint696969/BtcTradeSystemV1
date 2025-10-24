# path: ./tmp/test_log_view_filter.py
# desc: dev_audit.jsonl から 24h 内の行を読み、log_ui.py と同じ閾値で擬似表示件数を検証
import json, sys
from pathlib import Path
from datetime import datetime, timezone, timedelta

LOG = Path(r"D:\BtcTS_V1\logs\dev_audit.jsonl")
if not LOG.exists():
    print("no dev_audit.jsonl")
    sys.exit(0)

LEVEL = {"DEBUG":10,"INFO":20,"WARN":30,"WARNING":30,"ERROR":40,"CRIT":50,"CRITICAL":50}
def min_rank(mode):
    m = (mode or "OFF").upper()
    if m=="OFF": return LEVEL["ERROR"]
    if m=="DEBUG": return LEVEL["WARN"]
    return 0  # BOOST

now = datetime.now(timezone.utc)
since = now - timedelta(hours=24)
lines = LOG.read_text(encoding="utf-8", errors="ignore").splitlines()
recs = []
for s in lines:
    try:
        o = json.loads(s)
        ts = o.get("ts")
        if ts and ts.endswith("Z"):
            try:
                dt = datetime.strptime(ts, "%Y-%m-%dT%H:%M:%S.%fZ").replace(tzinfo=timezone.utc)
            except ValueError:
                dt = datetime.strptime(ts, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
        else:
            dt = datetime.fromisoformat(ts).astimezone(timezone.utc) if ts else now
        if dt >= since:
            recs.append(o)
    except Exception:
        pass

for m in ["OFF","DEBUG","BOOST"]:
    keep = [r for r in recs if LEVEL.get(str(r.get("level","")).upper(),999) >= min_rank(m)]
    print(m, "visible=", len(keep))
