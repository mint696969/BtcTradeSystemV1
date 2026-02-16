# path: ./tools/test_io_audit.py
# desc: btcts(core) の io/audit を最小スモーク（原子的保存 + audit.jsonl）

import os
import sys
from pathlib import Path

# --- ensure btcts import (no PYTHONPATH required) ---
REPO = Path(__file__).resolve().parents[1]
BTCTS_SRC = REPO / "btcts_next" / "src"
if str(BTCTS_SRC) not in sys.path:
    sys.path.insert(0, str(BTCTS_SRC))

# --- test env (write under repo/tmp) ---
tmp_root = REPO / "tmp" / "_io_audit_test"
logs_dir = tmp_root / "logs"
data_dir = tmp_root / "data"

os.environ.setdefault("BTC_TS_MODE", "DEBUG")  # audit を確実に出す
os.environ["BTC_TS_LOGS_DIR"] = str(logs_dir)
os.environ["BTC_TS_DATA_DIR"] = str(data_dir)

from btcts.core import io as io_safe
from btcts.core import audit
from btcts.core import paths

def main():
    print("[ENV] BTC_TS_MODE     =", os.environ.get("BTC_TS_MODE"))
    print("[ENV] BTC_TS_LOGS_DIR =", os.environ.get("BTC_TS_LOGS_DIR"))
    print("[ENV] BTC_TS_DATA_DIR =", os.environ.get("BTC_TS_DATA_DIR"))

    # 1) atomic write
    out_txt = tmp_root / "atomic" / "hello.txt"
    io_safe.write_atomic_text(out_txt, "hello atomic\n", make_parents=True)
    assert out_txt.exists()
    print("[OK] atomic write:", out_txt)

    # 2) audit emit -> logs/audit.jsonl
    audit.emit(
        "tool.test_io_audit",
        feature="tools",
        level="INFO",
        payload={"note": "smoke", "path": str(out_txt)},
    )
    audit_path = paths.logs_dir() / "audit.jsonl"
    print("[OK] audit path:", audit_path)
    if audit_path.exists():
        # last 1 line
        lines = audit_path.read_text(encoding="utf-8").splitlines()
        print("[OK] audit lines:", len(lines))
        print("[TAIL]", lines[-1])
    else:
        raise SystemExit(f"audit.jsonl not created: {audit_path}")

    print("DONE")

if __name__ == "__main__":
    main()
