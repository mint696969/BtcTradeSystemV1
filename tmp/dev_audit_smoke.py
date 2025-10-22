# path: ./tmp/dev_audit_smoke.py
# desc: dev監査の書き込み→Errors only 抽出のスモーク（writer/search の最短動作確認）

from __future__ import annotations
import sys, time
from pathlib import Path

# --- ensure repo root on sys.path ---
REPO_ROOT = Path(__file__).resolve().parent.parent  # .../BtcTradeSystemV1
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from btc_trade_system.features.audit_dev.writer import audit_info, audit_error, set_mode, get_mode
from btc_trade_system.features.audit_dev.search import errors_only_tail
from btc_trade_system.common import paths

def main() -> int:
    logs = paths.logs_dir()
    target = logs / "dev_audit.jsonl"

    # 0) まずはモードを DEBUG に（OFF だと間引かれる場合があります）
    set_mode("DEBUG")
    cur = get_mode()
    print(f"MODE={cur}")

    # 1) 書き込み（INFO と ERROR）
    audit_info("dev.smoke.info", feature="audit_dev", payload={"ok": True, "msg": "hello"})
    audit_error("dev.smoke.error", feature="audit_dev", payload={"ng": True, "msg": "boom"})
    time.sleep(0.1)  # fsync済みでも念のため

    # 2) Errors only tail を取得
    rows = errors_only_tail(target, limit=50)

    # 3) 期待：直近の ERROR が >=1
    hits = sum("dev.smoke.error" in r for r in rows)
    ok = hits >= 1
    print(f"FILE: {target}")
    print(f"ROWS(HITS): {len(rows)}  EXPECT>=1  FOUND: {hits}")
    return 0 if ok else 2

if __name__ == "__main__":
    sys.exit(main())
