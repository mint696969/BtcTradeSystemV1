# path: ./btc_trade_system/features/dash/health/leader_annotations.py
# desc: status.json から leader 情報を読み取り、items に leader.host / leader_age_sec を付与（UIは読取専用）

from __future__ import annotations
import json, os, time
from pathlib import Path
from typing import Dict, List, Any, Tuple

def _data_root() -> Path:
    return Path(os.environ.get("BTC_TS_DATA_DIR", "data"))

def _status_path(data_root: Path) -> Path:
    return data_root / "collector" / "status.json"

def _now_ms() -> int:
    return int(time.time() * 1000)

def load_status_with_leader() -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
    try:
        p = _status_path(_data_root())
        raw = json.loads(p.read_text(encoding="utf-8"))
        items = list(raw.get("items", []))
        leader = raw.get("leader") or {}
        host = leader.get("host")
        hb_ms = int(leader.get("heartbeat_ms", 0) or 0)
        age_ms = max(0, _now_ms() - hb_ms) if hb_ms else None
        age_sec = int(age_ms / 1000) if age_ms is not None else None
        if host is not None or age_sec is not None:
            for it in items:
                it["leader.host"] = host
                it["leader_age_sec"] = age_sec
        return items, leader
    except Exception:
        return [], {}
