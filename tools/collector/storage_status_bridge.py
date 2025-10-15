# path: ./tools/collector/storage_status_bridge.py
# desc: StorageRouter の現状を書き出し、status.json の storage メタへ反映（開発確認用）

from __future__ import annotations
from pathlib import Path
from btc_trade_system.common.storage_router import StorageRouter
from btc_trade_system.features.collector.core.status import StatusWriter

def main() -> int:
    sr = StorageRouter(Path("."))
    # 現在の書き込み先（primary/fallback いずれか）を取得
    logs_root = str(sr.current_root("logs"))
    data_root = str(sr.current_root("data"))
    # primary 可用性は logs で代表判定（両方見るなら and でもOK）
    primary_ok = sr.is_primary_available("logs") and sr.is_primary_available("data")

    sw = StatusWriter()
    sw.set_storage(logs_root=logs_root, data_root=data_root, primary_ok=primary_ok)
    sw.flush()
    print("storage -> status.json updated")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
