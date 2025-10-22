# path: ./tmp/dev_snapshot_smoke.py
# desc: export_and_build_text() によるスナップショット生成のスモーク（DEBUG/BOOST どちらでもOK）

from __future__ import annotations
import sys
from pathlib import Path

# --- ensure repo root on sys.path ---
REPO_ROOT = Path(__file__).resolve().parent.parent  # .../BtcTradeSystemV1
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from btc_trade_system.features.audit_dev.boost import export_and_build_text

def main(mode: str = "DEBUG") -> int:
    snap_path_str, text = export_and_build_text(mode=mode, force=True)
    p = Path(snap_path_str)
    ok = p.exists() and p.is_file() and isinstance(text, str) and len(text) > 0
    print(f"MODE={mode}  SNAP_PATH={p}  TEXT_LEN={len(text)}")
    return 0 if ok else 2

if __name__ == "__main__":
    mode = (sys.argv[1] if len(sys.argv) > 1 else "DEBUG").upper()
    sys.exit(main(mode))
