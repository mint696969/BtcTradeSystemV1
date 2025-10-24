# path: ./tmp/test_export_boost.py
# desc: export_and_build_text(BOOST)で余計な章が混ざらないことを確認（PYTHONPATH不要版）
import sys, re, pathlib
root = pathlib.Path.cwd()
sys.path.insert(0, str(root))

from btc_trade_system.features.audit_dev.boost import export_and_build_text
from btc_trade_system.common import paths

snap_path, text = export_and_build_text(mode="BOOST", force=True)
out = paths.logs_dir() / "handover_gpt.txt"
body = out.read_text(encoding="utf-8", errors="ignore")

def has(pat, s): return bool(re.search(pat, s, flags=re.M))
print("SNAP_PATH     =", snap_path)
print("RET_HAS_SUM   =", has(r'^## errors_summary', text))
print("RET_HAS_EONLY =", has(r'^## audit_tail \(errors-only', text))
print("FILE_PATH     =", out)
print("FILE_HAS_SUM  =", has(r'^## errors_summary', body))
print("FILE_HAS_EONLY=", has(r'^## audit_tail \(errors-only', body))
