# path: ./btcts_next/src/btcts/derived/daily.py
# desc: Phase2：derived/hourly_*.json を合算して日次サマリ（derived/daily_YYYYMMDD.json）を生成する。

from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, Optional

from btcts.core import io, paths


def _now_utc() -> datetime:
    return datetime.now(timezone.utc)


def _day_key(dt: datetime) -> str:
    return dt.strftime("%Y%m%d")


def _parse_utc_iso(s: Any) -> Optional[datetime]:
    if not isinstance(s, str) or not s.strip():
        return None
    t = s.strip()
    if t.endswith("Z"):
        t = t[:-1] + "+00:00"
    try:
        d = datetime.fromisoformat(t)
        if d.tzinfo is None:
            d = d.replace(tzinfo=timezone.utc)
        return d.astimezone(timezone.utc)
    except Exception:
        return None


def _inc(d: Dict[str, Any], k: str, n: int = 1) -> None:
    d[k] = int(d.get(k, 0)) + int(n)


def _max(dst: Dict[str, Any], k: str, v: Any) -> None:
    if v is None:
        return
    cur = dst.get(k)
    if cur is None:
        dst[k] = v
        return
    try:
        if float(v) > float(cur):
            dst[k] = v
    except Exception:
        pass


def run_daily(*, day: Optional[str] = None) -> Path:
    logs_dir = paths.logs_dir()
    derived_dir = logs_dir / "derived"
    derived_dir.mkdir(parents=True, exist_ok=True)

    if day is None:
        # “確定済み日”を作りたいので、基本は前日（UTC）
        day = _day_key(_now_utc() - timedelta(days=1))

    # hourly files for the day
    hourly_files = sorted(derived_dir.glob(f"hourly_{day}_*.json"))
    out = derived_dir / f"daily_{day}.json"
    latest = derived_dir / "latest_daily.json"

    agg: Dict[str, Any] = {
        "day": day,
        "ts_start": f"{day[:4]}-{day[4:6]}-{day[6:8]}T00:00:00Z",
        "ts_end": (datetime(int(day[:4]), int(day[4:6]), int(day[6:8]), tzinfo=timezone.utc) + timedelta(days=1)).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "hours": len(hourly_files),
        "collector": {"proc_restart_count": 0, "http": {}, "topics": {}},
        "watchdog": {"restart_count": 0, "hang_detected_count": 0, "stop_events": {}},
        "health": {"warn_count": 0, "crit_count": 0},
        "files": {"data_bytes_delta": {}, "audit_bytes_delta": 0, "supervisor_bytes_delta": 0},
        "modes": {},
        "mode": None,
        "generated_utc": _now_utc().strftime("%Y-%m-%dT%H:%M:%SZ"),
    }

    def ensure_topic(k: str) -> Dict[str, Any]:
        topics = agg["collector"]["topics"]
        if k not in topics:
            topics[k] = {"ok_count": 0, "err_count": 0, "max_age_sec": None, "max_retries": None, "last_ok_ts": None}
        return topics[k]

    # aggregate
    for fp in hourly_files:
        try:
            row = io.read_json(fp, default=None)
        except Exception:
            continue
        if not isinstance(row, dict):
            continue

        # modes
        m = row.get("modes")
        if isinstance(m, dict):
            for mk, mv in m.items():
                _inc(agg["modes"], str(mk).upper(), int(mv))

        # collector
        col = row.get("collector")
        if isinstance(col, dict):
            agg["collector"]["proc_restart_count"] += int(col.get("proc_restart_count") or 0)

            http = col.get("http")
            if isinstance(http, dict):
                for hk in ("total", "status_2xx", "status_4xx", "status_5xx", "status_429"):
                    agg["collector"]["http"][hk] = int(agg["collector"]["http"].get(hk, 0)) + int(http.get(hk) or 0)
                # max
                ra = http.get("retry_after_max_sec")
                cur = float(agg["collector"]["http"].get("retry_after_max_sec", 0.0) or 0.0)
                try:
                    agg["collector"]["http"]["retry_after_max_sec"] = max(cur, float(ra or 0.0))
                except Exception:
                    agg["collector"]["http"]["retry_after_max_sec"] = cur

            topics = col.get("topics")
            if isinstance(topics, dict):
                for tk, tv in topics.items():
                    if not isinstance(tv, dict):
                        continue
                    t = ensure_topic(str(tk))
                    t["ok_count"] += int(tv.get("ok_count") or 0)
                    t["err_count"] += int(tv.get("err_count") or 0)
                    _max(t, "max_age_sec", tv.get("max_age_sec"))
                    _max(t, "max_retries", tv.get("max_retries"))
                    lok = tv.get("last_ok_ts")
                    if isinstance(lok, str) and lok:
                        # keep latest timestamp
                        cur = t.get("last_ok_ts")
                        if cur is None:
                            t["last_ok_ts"] = lok
                        else:
                            a = _parse_utc_iso(cur)
                            b = _parse_utc_iso(lok)
                            if a is None or (b is not None and b > a):
                                t["last_ok_ts"] = lok

        # watchdog
        wd = row.get("watchdog")
        if isinstance(wd, dict):
            agg["watchdog"]["restart_count"] += int(wd.get("restart_count") or 0)
            agg["watchdog"]["hang_detected_count"] += int(wd.get("hang_detected_count") or 0)
            se = wd.get("stop_events")
            if isinstance(se, dict):
                for rk, rv in se.items():
                    _inc(agg["watchdog"]["stop_events"], str(rk), int(rv))

        # health
        hl = row.get("health")
        if isinstance(hl, dict):
            agg["health"]["warn_count"] += int(hl.get("warn_count") or 0)
            agg["health"]["crit_count"] += int(hl.get("crit_count") or 0)

        # files
        fl = row.get("files")
        if isinstance(fl, dict):
            agg["files"]["audit_bytes_delta"] += int(fl.get("audit_bytes_delta") or 0)
            agg["files"]["supervisor_bytes_delta"] += int(fl.get("supervisor_bytes_delta") or 0)
            dd = fl.get("data_bytes_delta")
            if isinstance(dd, dict):
                for dk, dv in dd.items():
                    agg["files"]["data_bytes_delta"][dk] = int(agg["files"]["data_bytes_delta"].get(dk, 0)) + int(dv or 0)

    # decide mode
    if agg["modes"]:
        agg["mode"] = sorted(agg["modes"].items(), key=lambda kv: int(kv[1]), reverse=True)[0][0]
    else:
        agg["mode"] = None

    io.write_json(out, agg, indent=2, sort_keys=True)
    io.write_json(latest, agg, indent=2, sort_keys=True)
    return latest


if __name__ == "__main__":
    out = run_daily()
    print(f"OK derived_daily: {out}")
