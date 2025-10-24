# path: ./tmp/test_writer_emit_matrix.py
# desc: writer.set_mode() ごとに各レベルを emit → dev_audit.jsonl の末尾から当該セッション分を集計
import json, time, uuid, os
from pathlib import Path
from btc_trade_system.features.audit_dev import writer as W
from btc_trade_system.common import paths

sid = "TST-" + uuid.uuid4().hex[:8]
LOG = paths.logs_dir() / "dev_audit.jsonl"

levels = ["DEBUG","INFO","WARN","ERROR","CRIT"]
def do(mode):
    W.set_mode(mode)
    for lv in levels:
        W.emit("tst.matrix", level=lv, feature="matrix", payload={"sid":sid,"lv":lv})
    # 少し待ってから読み出し
    time.sleep(0.2)

def count_sid():
    rows = []
    if LOG.exists():
        for s in LOG.read_text(encoding="utf-8", errors="ignore").splitlines()[-800:]:
            try:
                o = json.loads(s)
            except Exception:
                continue
            p = o.get("payload") or {}
            if isinstance(p, dict) and p.get("sid")==sid:
                rows.append(o)
        return rows
    return []

for m in ["OFF","DEBUG","BOOST"]:
    do(m)
    rows = count_sid()
    lvls = [r.get("level") for r in rows]
    print(m, "rows=", len(rows), "levels=", lvls)
