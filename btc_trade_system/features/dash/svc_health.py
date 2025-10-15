# path: ./btc_trade_system/features/dash/svc_health.py
# desc: status.json を読み、UI向け Health API（summary/table）を提供（UTC→ローカル変換含む）

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

# --- public API expected by ui_health.py ------------------------------------
def get_health_summary(*, base_dir: Optional[Path] = None, tz_name: str = "Asia/Tokyo") -> Dict[str, Any]:
    """
    ui_health.py が期待する“旧フォーマット”で返す:
      - updated_at: str（ローカル優先）
      - all_ok: bool
      - cards: list[dict] … {exchange, topic, status, age_sec, notes}
    """
    from datetime import datetime

    def _age_seconds_from_iso(iso: Optional[str]) -> Optional[float]:
        if not iso:
            return None
        s = str(iso)
        # '...Z' は fromisoformat で扱えないため +00:00 に置換
        if s.endswith("Z"):
            s = s[:-1] + "+00:00"
        try:
            dt = datetime.fromisoformat(s)  # 例: '2025-10-15T09:00:00+09:00'
        except Exception:
            return None
        # tz 無しなら UTC として扱う
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=UTC)
        now = datetime.now(dt.tzinfo)
        return max(0.0, (now - dt).total_seconds())

    doc = load_for_ui(base_dir=base_dir, tz_name=tz_name)
    items: List[Dict[str, Any]] = list(doc.get("items") or [])
    updated = doc.get("updated_at_local") or doc.get("updated_at") or None

    cards: List[Dict[str, Any]] = []
    errs = 0
    for it in items:
        status = (it.get("status") or "OK").upper()
        if status != "OK":
            errs += 1
        # last_local（tz付き）→ last_iso（UTC '...Z'）の順に見る
        age_sec = _age_seconds_from_iso(it.get("last_local") or it.get("last_iso") or it.get("last"))

        cards.append({
            "exchange": it.get("exchange") or "?",
            "topic": it.get("topic") or "?",
            "status": status,
            "age_sec": age_sec,
            "notes": it.get("notes") or "",
        })

    all_ok = (len(items) > 0 and errs == 0)

    return {
        "updated_at": updated,
        "all_ok": all_ok,
        "cards": cards,
    }

def get_health_table(*, base_dir: Optional[Path] = None, tz_name: str = "Asia/Tokyo"):
    """
    テーブル表示用の行データを返す。まずは list[dict] で返し、必要に応じて DataFrame 化は UI 側で実施。
    """
    doc = load_for_ui(base_dir=base_dir, tz_name=tz_name)
    return doc.get("items") or []
