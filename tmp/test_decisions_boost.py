# path: ./tmp/test_decisions_boost.py
import sys, pathlib, re
root = pathlib.Path.cwd(); sys.path.insert(0, str(root))
from btc_trade_system.features.audit_dev.boost import export_and_build_text
from btc_trade_system.common import paths
p, t = export_and_build_text(mode="BOOST", force=True)
body = (paths.logs_dir() / "handover_gpt.txt").read_text(encoding="utf-8", errors="ignore")
print("BOOST_RET_HAS_DECISIONS =", bool(re.search(r'^## Decisions \(last \d+\)', t, flags=re.M)))
print("BOOST_FILE_HAS_DECISIONS=", bool(re.search(r'^## Decisions \(last \d+\)', body, flags=re.M)))
print("SNAP_PATH               =", p)
