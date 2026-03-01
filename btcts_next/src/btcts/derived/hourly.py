# path: ./btcts_next/src/btcts/derived/hourly.py
# desc: Phase2：監査（audit.jsonl）と supervisor_collector.jsonl をカーソル方式で増分集計し、1時間サマリ（derived/hourly_*.json）を生成する。

from __future__ import annotations

import hashlib
import json
import time
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, Optional, Tuple

from btcts.core import audit, env, io, paths
from btcts.settings import svc as settings_svc


# -----------------------------
# time helpers
# -----------------------------
def _now_dt_utc() -> datetime:
    return datetime.now(timezone.utc)


def _floor_hour(dt: datetime) -> datetime:
    return dt.replace(minute=0, second=0, microsecond=0)


def _parse_iso_utc(s: Any) -> Optional[datetime]:
    if s is None:
        return None
    if isinstance(s, (int, float)):
        return datetime.fromtimestamp(float(s), tz=timezone.utc)
    if not isinstance(s, str):
        return None
    t = s.strip()
    if not t:
        return None
    try:
        if t.endswith("Z"):
            t = t[:-1] + "+00:00"
        dt = datetime.fromisoformat(t)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt.astimezone(timezone.utc)
    except Exception:
        return None


def _hour_key(dt: datetime) -> str:
    # UTC: YYYYMMDD_HH
    return dt.strftime("%Y%m%d_%H")


# -----------------------------
# file/cursor helpers
# -----------------------------
@dataclass
class Cursor:
    pos: int = 0
    size: int = 0
    mtime_utc: str = ""


def _sha256_file(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest().upper()


def _stat_utc(p: Path) -> Dict[str, Any]:
    if not p.exists():
        return {"exists": False}
    st = p.stat()
    return {
        "exists": True,
        "size": int(st.st_size),
        "mtime_utc": datetime.fromtimestamp(st.st_mtime, tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    }


def _read_new_jsonl(path: Path, cur: Cursor) -> Tuple[Iterable[Dict[str, Any]], Cursor]:
    """
    cursor.pos (byte offset) から増分だけ JSONL を読む。
    """
    if not path.exists():
        return [], Cursor(pos=0, size=0, mtime_utc="")

    st = path.stat()
    size = int(st.st_size)
    mtime_utc = datetime.fromtimestamp(st.st_mtime, tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    pos = int(cur.pos or 0)
    if pos < 0 or pos > size:
        pos = 0  # rotated/truncated 等はリセット

    rows: list[Dict[str, Any]] = []
    with open(path, "rb") as f:
        f.seek(pos)
        while True:
            b = f.readline()
            if not b:
                break
            pos = f.tell()
            try:
                line = b.decode("utf-8", errors="replace").strip()
            except Exception:
                continue
            if not line:
                continue
            try:
                rows.append(json.loads(line))
            except Exception:
                continue

    return rows, Cursor(pos=pos, size=size, mtime_utc=mtime_utc)


# -----------------------------
# aggregation structures
# -----------------------------
def _new_topic() -> Dict[str, Any]:
    return {
        "ok_count": 0,
        "err_count": 0,
        "max_age_sec": None,
        "max_retries": None,
        "last_ok_ts": None,
    }


def _bucket_init(ts_start: datetime) -> Dict[str, Any]:
    return {
        "ts_start": ts_start.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "ts_end": (ts_start + timedelta(hours=1)).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "modes": {},  # {MODE: count}
        "collector": {
            "proc_restart_count": 0,
            "topics": {},  # "<ex>/<topic>" -> stats
            "http": {
                "total": 0,
                "status_2xx": 0,
                "status_4xx": 0,
                "status_5xx": 0,
                "status_429": 0,
                "retry_after_max_sec": 0.0,
            },
        },
        "watchdog": {
            "restart_count": 0,
            "stop_events": {},  # reason -> count
            "hang_detected_count": 0,
        },
        "health": {"warn_count": 0, "crit_count": 0},
        "files": {
            "data_bytes_delta": {},  # "<ex>/<topic>" -> bytes (end-start)
            "audit_bytes_delta": None,
            "supervisor_bytes_delta": None,
        },
        # internal (state only)
        "_written": False,
        "_baseline": {
            "data": {},  # "<ex>/<topic>" -> start_size
            "audit_size": None,
            "supervisor_size": None,
        },
    }


def _inc_map(m: Dict[str, Any], k: str, n: int = 1) -> None:
    m[k] = int(m.get(k, 0)) + int(n)


def _topic_key(payload: Dict[str, Any]) -> Optional[str]:
    ex = payload.get("exchange")
    tp = payload.get("topic")
    if not ex or not tp:
        return None
    return f"{str(ex).strip().lower()}/{str(tp).strip().lower()}"


def _apply_audit(bucket: Dict[str, Any], row: Dict[str, Any]) -> None:
    md = (row.get("mode") or "NORMAL").upper()
    _inc_map(bucket["modes"], md, 1)

    event = str(row.get("event") or "")
    level = str(row.get("level") or "").upper()
    payload = row.get("payload") if isinstance(row.get("payload"), dict) else {}

    # health
    if event == "health.warn":
        bucket["health"]["warn_count"] += 1
        return
    if event == "health.crit":
        bucket["health"]["crit_count"] += 1
        return

    # collector (ok)
    if event == "collector.endpoint.ok":
        k = _topic_key(payload) or "unknown/unknown"
        topics = bucket["collector"]["topics"]
        if k not in topics:
            topics[k] = _new_topic()
        topics[k]["ok_count"] += 1

        bucket["collector"]["http"]["total"] += 1
        bucket["collector"]["http"]["status_2xx"] += 1
        return

    # collector 429
    if event == "collector.http.429":
        k = _topic_key(payload) or "unknown/unknown"
        topics = bucket["collector"]["topics"]
        if k not in topics:
            topics[k] = _new_topic()
        topics[k]["err_count"] += 1

        bucket["collector"]["http"]["total"] += 1
        bucket["collector"]["http"]["status_429"] += 1
        ra = float(payload.get("retry_after_sec") or 0.0)
        if ra > float(bucket["collector"]["http"]["retry_after_max_sec"] or 0.0):
            bucket["collector"]["http"]["retry_after_max_sec"] = ra
        return

    # collector http fail (best-effort categorize)
    if event == "collector.http.fail":
        k = _topic_key(payload) or "unknown/unknown"
        topics = bucket["collector"]["topics"]
        if k not in topics:
            topics[k] = _new_topic()
        topics[k]["err_count"] += 1

        bucket["collector"]["http"]["total"] += 1
        code = payload.get("status_code")
        try:
            c = int(code)
            if 400 <= c <= 499:
                bucket["collector"]["http"]["status_4xx"] += 1
            elif 500 <= c <= 599:
                bucket["collector"]["http"]["status_5xx"] += 1
        except Exception:
            pass
        return

    # それ以外：最低限、WARN/ERROR なら topic へ err を寄せる（原因追跡用）
    if level in ("WARN", "ERROR"):
        k = _topic_key(payload)
        if k:
            topics = bucket["collector"]["topics"]
            if k not in topics:
                topics[k] = _new_topic()
            topics[k]["err_count"] += 1


def _apply_supervisor(bucket: Dict[str, Any], row: Dict[str, Any]) -> None:
    event = str(row.get("event") or "")
    if not event:
        return

    if event == "collector.exited":
        bucket["watchdog"]["restart_count"] += 1
        bucket["collector"]["proc_restart_count"] += 1
        return

    if event == "collector.hang":
        bucket["watchdog"]["hang_detected_count"] += 1
        return

    if event.startswith("watchdog.stop"):
        _inc_map(bucket["watchdog"]["stop_events"], event, 1)
        return


def _enabled_topics() -> list[str]:
    """
    collector.yaml の feeds + enabled_exchanges から、"<ex>/<topic>" のリストを作る。
    """
    cfg = settings_svc.load_effective("collector")
    if not isinstance(cfg, dict):
        return []

    enabled_ex = cfg.get("enabled_exchanges")
    enabled_ex_set: Optional[set[str]] = None
    if isinstance(enabled_ex, list) and enabled_ex:
        enabled_ex_set = {str(x).strip().lower() for x in enabled_ex if str(x).strip()}

    feeds = cfg.get("feeds")
    if not isinstance(feeds, dict):
        return []

    out: list[str] = []
    for ex, mp in feeds.items():
        ex_l = str(ex).strip().lower()
        if enabled_ex_set is not None and ex_l not in enabled_ex_set:
            continue
        if not isinstance(mp, dict):
            continue
        for topic, tcfg in mp.items():
            tp_l = str(topic).strip().lower()
            if isinstance(tcfg, dict) and ("enabled" in tcfg) and (not bool(tcfg.get("enabled"))):
                continue
            out.append(f"{ex_l}/{tp_l}")
    return sorted(set(out))


def _data_path_for(key: str, hour_start: datetime) -> Path:
    ex, tp = key.split("/", 1)
    ymd = hour_start.strftime("%Y%m%d")
    return paths.data_dir() / "collector" / ex / tp / f"{ymd}.jsonl"


def _load_status_snapshot() -> Optional[Dict[str, Any]]:
    p = paths.data_dir() / "collector" / "status.json"
    if not p.exists():
        return None
    try:
        return io.read_json(p, default=None)
    except Exception:
        return None


def _load_rate_state_snapshot() -> Optional[Dict[str, Any]]:
    p = paths.data_dir() / "collector" / "rate_state.json"
    if not p.exists():
        return None
    try:
        return io.read_json(p, default=None)
    except Exception:
        return None


def _flatten_rate_state(rs: Dict[str, Any]) -> Dict[str, Any]:
    """
    rate_state.json の形が揺れても、{exchange -> state} に寄せる。
    例）{"items":{"items":{"bitflyer":{...}},"ts":...},"ts":...} などを吸収。
    """
    if not isinstance(rs, dict):
        return {}
    items = rs.get("items")
    if isinstance(items, dict) and "items" in items and isinstance(items.get("items"), dict):
        return items["items"]
    if isinstance(items, dict):
        return items
    return {}


def _choose_mode(modes: Dict[str, Any]) -> str:
    if not modes:
        return env.mode()
    # 最頻値
    best = sorted(modes.items(), key=lambda kv: int(kv[1]), reverse=True)[0][0]
    return str(best).upper()


def run_hourly(*, now_utc: Optional[datetime] = None) -> Path:
    """
    1回分の増分処理 + 確定した時間バケットの書き出しを行う。
    戻り値：latest_hourly.json のパス（生成されなければ derived/state.json）
    """
    now = now_utc or _now_dt_utc()
    hour_now = _floor_hour(now)

    logs_dir = paths.logs_dir()
    derived_dir = logs_dir / "derived"
    state_path = derived_dir / "state.json"

    # Phase2: derived 出力先は必ず作る（file_lock が lock を作るため）
    derived_dir.mkdir(parents=True, exist_ok=True)

    audit_path = logs_dir / "audit.jsonl"
    super_path = logs_dir / "supervisor_collector.jsonl"

    latest_path = derived_dir / "latest_hourly.json"

    with io.file_lock(state_path, timeout_sec=10.0, stale_sec=120.0):
        state = io.read_json(state_path, default=None)
        if not isinstance(state, dict):
            state = {"version": 1, "updated_utc": "", "files": {}, "buckets": {}}

        files = state.get("files") if isinstance(state.get("files"), dict) else {}
        buckets = state.get("buckets") if isinstance(state.get("buckets"), dict) else {}

        # load cursors
        cur_a = files.get("audit") if isinstance(files.get("audit"), dict) else {}
        cur_s = files.get("supervisor") if isinstance(files.get("supervisor"), dict) else {}
        c_a = Cursor(pos=int(cur_a.get("pos", 0)), size=int(cur_a.get("size", 0)), mtime_utc=str(cur_a.get("mtime_utc", "")))
        c_s = Cursor(pos=int(cur_s.get("pos", 0)), size=int(cur_s.get("size", 0)), mtime_utc=str(cur_s.get("mtime_utc", "")))

        # read new lines
        audit_rows, c_a2 = _read_new_jsonl(audit_path, c_a)
        super_rows, c_s2 = _read_new_jsonl(super_path, c_s)

        # apply
        for r in audit_rows:
            dt = _parse_iso_utc(r.get("ts"))
            if dt is None:
                continue
            hk = _hour_key(_floor_hour(dt))
            b = buckets.get(hk)
            if not isinstance(b, dict):
                b = _bucket_init(_floor_hour(dt))
                buckets[hk] = b
            _apply_audit(b, r)

        for r in super_rows:
            dt = _parse_iso_utc(r.get("ts"))
            if dt is None:
                continue
            hk = _hour_key(_floor_hour(dt))
            b = buckets.get(hk)
            if not isinstance(b, dict):
                b = _bucket_init(_floor_hour(dt))
                buckets[hk] = b
            _apply_supervisor(b, r)

        # baseline file sizes for open buckets (best-effort)
        topics = _enabled_topics()
        for hk, b in list(buckets.items()):
            if not isinstance(b, dict):
                continue
            try:
                ts_start = _parse_iso_utc(b.get("ts_start"))
                if ts_start is None:
                    continue
            except Exception:
                continue

            bl = b.get("_baseline") if isinstance(b.get("_baseline"), dict) else {"data": {}, "audit_size": None, "supervisor_size": None}
            data_bl = bl.get("data") if isinstance(bl.get("data"), dict) else {}

            for k in topics:
                if k not in data_bl:
                    p = _data_path_for(k, ts_start)
                    data_bl[k] = int(p.stat().st_size) if p.exists() else 0

            if bl.get("audit_size") is None:
                bl["audit_size"] = int(audit_path.stat().st_size) if audit_path.exists() else 0
            if bl.get("supervisor_size") is None:
                bl["supervisor_size"] = int(super_path.stat().st_size) if super_path.exists() else 0

            bl["data"] = data_bl
            b["_baseline"] = bl

        # finalize buckets whose hour is complete (< hour_now)
        wrote_any = False
        out_latest: Optional[Path] = None

        for hk, b in sorted(buckets.items()):
            if not isinstance(b, dict):
                continue
            if bool(b.get("_written")):
                continue

            ts_start = _parse_iso_utc(b.get("ts_start"))
            ts_end = _parse_iso_utc(b.get("ts_end"))
            if ts_start is None or ts_end is None:
                continue
            if ts_end > hour_now:
                continue  # current hour (not complete)

            # enrich snapshot status/rate_state (at finalize time)
            st = _load_status_snapshot()
            rs = _load_rate_state_snapshot()
            rs_flat = _flatten_rate_state(rs or {})

            # fill topic info from status.json (last snapshot)
            topics_map = b["collector"]["topics"]
            if not isinstance(topics_map, dict):
                topics_map = {}
                b["collector"]["topics"] = topics_map

            if isinstance(st, dict) and isinstance(st.get("items"), list):
                for it in st["items"]:
                    if not isinstance(it, dict):
                        continue
                    ex = str(it.get("exchange") or "").strip().lower()
                    tp = str(it.get("topic") or "").strip().lower()
                    if not ex or not tp:
                        continue
                    k = f"{ex}/{tp}"
                    if k not in topics_map:
                        topics_map[k] = _new_topic()
                    try:
                        age = float(it.get("age_sec")) if it.get("age_sec") is not None else None
                    except Exception:
                        age = None
                    if age is not None:
                        cur = topics_map[k].get("max_age_sec")
                        if (cur is None) or (float(age) > float(cur)):
                            topics_map[k]["max_age_sec"] = float(age)

                    # retries
                    try:
                        r = int(it.get("retries")) if it.get("retries") is not None else None
                    except Exception:
                        r = None
                    if r is not None:
                        cur = topics_map[k].get("max_retries")
                        if (cur is None) or (int(r) > int(cur)):
                            topics_map[k]["max_retries"] = int(r)

                    lok = it.get("last_ok")
                    if isinstance(lok, str) and lok:
                        topics_map[k]["last_ok_ts"] = lok

            # file deltas
            bl = b.get("_baseline") if isinstance(b.get("_baseline"), dict) else {}
            data_bl = bl.get("data") if isinstance(bl.get("data"), dict) else {}
            data_delta: Dict[str, int] = {}
            for k, start_sz in data_bl.items():
                p = _data_path_for(k, ts_start)
                end_sz = int(p.stat().st_size) if p.exists() else 0
                data_delta[k] = int(end_sz) - int(start_sz)

            b["files"]["data_bytes_delta"] = data_delta
            a0 = int(bl.get("audit_size") or 0)
            s0 = int(bl.get("supervisor_size") or 0)
            a1 = int(audit_path.stat().st_size) if audit_path.exists() else 0
            s1 = int(super_path.stat().st_size) if super_path.exists() else 0
            b["files"]["audit_bytes_delta"] = a1 - a0
            b["files"]["supervisor_bytes_delta"] = s1 - s0

            # mode
            b["mode"] = _choose_mode(b.get("modes") if isinstance(b.get("modes"), dict) else {})

            # attach small rate_state snapshot
            b["rate_state"] = rs_flat

            # cfg sha snapshot (small)
            cfg_dir = paths.config_dir()
            cfg_items = []
            cfile = cfg_dir / "collector.yaml"
            if cfile.exists():
                cfg_items.append({"path": str(cfile), "sha256": _sha256_file(cfile)})
            b["cfg"] = cfg_items

            # write output
            out = derived_dir / f"hourly_{hk}.json"
            io.write_json(out, b, indent=2, sort_keys=True)
            io.write_json(latest_path, b, indent=2, sort_keys=True)

            b["_written"] = True
            wrote_any = True
            out_latest = latest_path

            # audit marker (optional)
            try:
                audit.emit(
                    "derived.hourly.write",
                    feature="derived",
                    level="INFO",
                    payload={"path": str(out), "hour": hk},
                )
            except Exception:
                pass

        # prune buckets (keep last 72 hours in state for safety)
        keep_after = _floor_hour(now) - timedelta(hours=72)
        for hk in list(buckets.keys()):
            b = buckets.get(hk)
            if not isinstance(b, dict):
                buckets.pop(hk, None)
                continue
            ts_start = _parse_iso_utc(b.get("ts_start"))
            if ts_start is None or ts_start < keep_after:
                buckets.pop(hk, None)

        # save cursors
        files["audit"] = {"pos": c_a2.pos, "size": c_a2.size, "mtime_utc": c_a2.mtime_utc}
        files["supervisor"] = {"pos": c_s2.pos, "size": c_s2.size, "mtime_utc": c_s2.mtime_utc}
        state["files"] = files
        state["buckets"] = buckets
        state["updated_utc"] = now.strftime("%Y-%m-%dT%H:%M:%SZ")

        io.write_json(state_path, state, indent=2, sort_keys=True)

    return out_latest or state_path


if __name__ == "__main__":
    out = run_hourly()
    print(f"OK derived_hourly: {out}")
