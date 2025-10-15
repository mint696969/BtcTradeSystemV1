# path: ./btc_trade_system/features/dash/providers/status_view.py
# desc: data/collector/status.json を読み、UI向けに ts_local を付与して返す最小プロバイダ（UTC保存→JST表示）。

from __future__ import annotations
import json, re
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, List, Optional
from btc_trade_system.common import paths

UTC = timezone.utc
_ISO_PAT = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$")

# zoneinfo は存在すれば使う（Py3.9+）
try:
    from zoneinfo import ZoneInfo
except Exception:  # pragma: no cover
    ZoneInfo = None  # type: ignore

def _parse_iso_utc(ts: str) -> datetime:
    if not _ISO_PAT.match(ts):
        # status.json の last_iso/updated_at は秒精度固定の想定
        raise ValueError(f"invalid UTC iso: {ts}")
    return datetime.strptime(ts, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=UTC)

def _to_local_iso(ts_utc: str, tz_name: str = "Asia/Tokyo") -> str:
    dt = _parse_iso_utc(ts_utc)
    if ZoneInfo is None:
        return dt.astimezone().isoformat(timespec="seconds")
    return dt.astimezone(ZoneInfo(tz_name)).isoformat(timespec="seconds")

def _status_path_candidates(base_dir: Path) -> List[Path]:
    # primary → secondary(./local) の順で探す
    p1 = paths.data_dir() / "collector" / "status.json"
    p2 = base_dir / "local" / "data" / "collector" / "status.json"
    return [p1, p2]

def load_for_ui(*, base_dir: Optional[Path] = None, tz_name: str = "Asia/Tokyo") -> Dict[str, Any]:
    """
    status.json を読み、UI向けに各 item に last_local、ルートに updated_at_local を付与して返す。
    読み出しは primary → secondary の順で存在確認。
    """
    base_dir = Path(base_dir or ".")
    path: Optional[Path] = None
    for cand in _status_path_candidates(base_dir):
        if cand.exists():
            path = cand
            break
    if path is None:
        return {"items": [], "updated_at": None, "updated_at_local": None, "source": "missing"}

    doc = json.loads(path.read_text(encoding="utf-8"))
    items = doc.get("items") or []

    out_items: List[Dict[str, Any]] = []
    for it in items:
        last_iso = it.get("last_iso")
        it2 = dict(it)
        if isinstance(last_iso, str) and last_iso:
            try:
                it2["last_local"] = _to_local_iso(last_iso, tz_name=tz_name)
            except Exception:
                it2["last_local"] = None
        else:
            it2["last_local"] = None
        out_items.append(it2)

    updated_at = doc.get("updated_at")
    if isinstance(updated_at, str) and updated_at:
        try:
            updated_at_local = _to_local_iso(updated_at, tz_name=tz_name)
        except Exception:
            updated_at_local = None
    else:
        updated_at_local = None

    return {
        "items": out_items,
        "updated_at": updated_at,
        "updated_at_local": updated_at_local,
        "source": str(path),
    }
