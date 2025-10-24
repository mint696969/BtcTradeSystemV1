# path: ./tmp/test_decisions_section.py
# desc: export_and_build_text(DEBUG) の返値と handover_gpt.txt の両方に "## Decisions (last" があるか確認
import sys, pathlib, re
root = pathlib.Path.cwd(); sys.path.insert(0, str(root))
from btc_trade_system.features.audit_dev.boost import export_and_build_text
from btc_trade_system.common import paths
p, t = export_and_build_text(mode="DEBUG", force=True)
body = (paths.logs_dir() / "handover_gpt.txt").read_text(encoding="utf-8", errors="ignore")
def has_decisions(s): return bool(re.search(r'^## Decisions \(last \d+\)', s, flags=re.M))
print("RET_HAS_DECISIONS =", has_decisions(t))
print("FILE_HAS_DECISIONS=", has_decisions(body))
print("SNAP_PATH         =", p)
