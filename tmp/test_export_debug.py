# path: ./tmp/test_export_debug.py
# desc: export_and_build_text(DEBUG)の返値と handover_gpt.txt の中身を検査（PYTHONPATH不要版）
import sys, re, pathlib
root = pathlib.Path.cwd()  # リポ直下で実行前提
sys.path.insert(0, str(root))  # ← これで import 可能に

from btc_trade_system.features.audit_dev.boost import export_and_build_text
from btc_trade_system.common import paths

snap_path, text = export_and_build_text(mode="DEBUG", force=True)
out = paths.logs_dir() / "handover_gpt.txt"
body = out.read_text(encoding="utf-8", errors="ignore")

def has(pat, s): return bool(re.search(pat, s, flags=re.M))
print("SNAP_PATH     =", snap_path)
print("RET_HAS_SUM   =", has(r'^## errors_summary', text))
print("RET_HAS_TAIL  =", has(r'^## audit_tail \(errors-only, last 20\)', text))
print("FILE_PATH     =", out)
print("FILE_HAS_SUM  =", has(r'^## errors_summary', body))
print("FILE_HAS_TAIL =", has(r'^## audit_tail \(errors-only, last 20\)', body))

# デバッグ用：返値テキスト内の '## audit_tail' 行を1行だけ表示
for line in text.splitlines():
    if line.startswith("## audit_tail"):
        print("RET_TAIL_HEAD =", line)
        break
