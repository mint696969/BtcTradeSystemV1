# path: ./tmp/dev_audit_smoke.py
# desc: 開発監査(OFF/DEBUG/BOOST)のスモーク。dev_audit.jsonl の動作確認。

import sys, pathlib, time
_repo_root = pathlib.Path(__file__).resolve().parents[1]
if str(_repo_root) not in sys.path:
    sys.path.insert(0, str(_repo_root))

from btc_trade_system.features.audit_dev.writer import set_mode, get_mode, dev_ok, dev_err
from btc_trade_system.common.audit import set_context

set_context(trace_id="DEV-TRACE-001", actor="tester", site="local", session="S-DEV", task="dev.audit")

# 1) OFF: 何も出ない
set_mode("OFF")
dev_ok("dev.off.should_skip", feature="audit_dev", payload={"n": 1})

# 2) DEBUG: 重要情報のみ出力(should_emit準拠)
set_mode("DEBUG")
dev_err("dev.debug.err", feature="audit_dev", endpoint="/dbg", code=501, cause="DBG_ERR")
dev_ok("dev.debug.info", feature="audit_dev", payload={"info": "may sample"})

# 3) BOOST: 全部出る + 大きいpayloadはDIAG上限で要約
set_mode("BOOST")
big = {"k": "x" * (10 * 1024)}
dev_ok("dev.boost.big", feature="audit_dev", payload=big)
dev_ok("dev.boost.info", feature="audit_dev", payload={"ok": True})

print("mode:", get_mode())
print("done")
