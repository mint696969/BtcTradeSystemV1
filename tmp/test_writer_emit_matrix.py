# path: ./tmp/test_writer_emit_matrix.py
# desc: writer.set_mode() ごとに各レベルを emit → event/feature で末尾集計（payload依存なし）
import sys, json, time, uuid, pathlib
root = pathlib.Path.cwd()
sys.path.insert(0, str(root))

from btc_trade_system.features.audit_dev import writer as W
from btc_trade_system.common import paths

sid = "TST-" + uuid.uuid4().hex[:8]
LOG = (paths.logs_dir() / "dev_audit.jsonl")

levels = ["DEBUG","INFO","WARN","ERROR","CRIT"]

def do(mode):
    W.set_mode(mode)
    for lv in levels:
        # event/feature に sid を焼き込む（payloadに依らず確実に拾う）
        W.emit(f"matrix {sid}", level=lv, feature="dev.tst.matrix", payload={"lv":lv})
    time.sleep(0.2)

def pick_rows():
    rows=[]
    if LOG.exists():
        # 直近1000行だけ見る
        for s in LOG.read_text(encoding="utf-8", errors="ignore").splitlines()[-1000:]:
            try:
                o=json.loads(s)
            except Exception:
                continue
            if o.get("feature")=="dev.tst.matrix" and isinstance(o.get("event"),str) and sid in o["event"]:
                rows.append(o)
    return rows

for m in ["OFF","DEBUG","BOOST"]:
    do(m)
    rs = pick_rows()
    lvls = [r.get("level") for r in rs]
    print(m, "rows=", len(rs), "levels=", lvls[-5:])  # 直近5つだけ表示
