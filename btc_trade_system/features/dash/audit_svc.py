# path: ./btc_trade_system/features/dash/audit_svc.py
# desc: 監査ログのサービス層（UI読み取り専用）— ui_audit から呼ばれるAPIを提供

from __future__ import annotations
import csv, json, re
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Iterable, Iterator, List, Optional, Sequence, Tuple

from btc_trade_system.common import paths

# ---- types -------------------------------------------------------------------
@dataclass(frozen=True)
class AuditRec:
    ts: str               # ISO8601(UTC, ...Z)
    mode: str
    event: str
    feature: Optional[str]
    level: str
    # 任意フィールドは raw に残す
    raw: dict

# ---- utils -------------------------------------------------------------------
UTC = timezone.utc

_ISO_PAT = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d{3})?Z$")

def _parse_iso_utc(ts: str) -> datetime:
    # 2025-10-14T15:22:32Z or 2025-10-14T15:22:32.813Z を許容
    if not _ISO_PAT.match(ts):
        raise ValueError(f"invalid ts format: {ts}")
    if "." in ts:
        return datetime.strptime(ts, "%Y-%m-%dT%H:%M:%S.%fZ").replace(tzinfo=UTC)
    return datetime.strptime(ts, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=UTC)

# zoneinfo はモジュール先頭で一度だけ解決
try:
    from zoneinfo import ZoneInfo  # Py3.9+
except Exception:  # pragma: no cover
    ZoneInfo = None  # type: ignore

def _to_iso_ms(dt: datetime) -> str:
    return dt.astimezone(UTC).strftime("%Y-%m-%dT%H:%M:%S.") + f"{int(dt.microsecond/1000):03d}Z"

def _ts_to_local_iso(ts_utc: str, tz_name: str = "Asia/Tokyo") -> str:
    """UTCのISO(…Z)を指定TZのISO(±HH:MM)へ。表示用。"""
    dt = _parse_iso_utc(ts_utc)  # -> aware UTC
    if ZoneInfo is None:
        # フォールバック: システムローカル
        return dt.astimezone().isoformat(timespec="milliseconds")
    return dt.astimezone(ZoneInfo(tz_name)).isoformat(timespec="milliseconds")

def _summarize_obj(obj: dict, *, max_len: int = 160) -> str:
    parts: List[str] = []
    for k in ("event", "feature", "level", "endpoint", "path", "exchange", "topic", "rate"):
        if k in obj and obj[k] is not None:
            parts.append(f"{k}={obj[k]}")
    for k in ("error", "cause", "code"):
        if k in obj and obj[k] is not None:
            parts.append(f"{k}={obj[k]}")
    if "payload" in obj and obj["payload"]:
        try:
            frag = json.dumps(obj["payload"], ensure_ascii=False)
            parts.append(f"payload={frag}")
        except Exception:
            parts.append("payload=<unrepr>")
    text = " | ".join(parts) if parts else json.dumps(obj, ensure_ascii=False)
    return (text[: max_len - 3] + "...") if len(text) > max_len else text

# ---- core: tail read & filter ------------------------------------------------
def tail_read(path: Path, *, max_lines: int = 5000) -> List[AuditRec]:
    if not path.exists():
        return []
    lines = path.read_text(encoding="utf-8").splitlines()[-max_lines:]
    out: List[AuditRec] = []
    for ln in reversed(lines):
        try:
            obj = json.loads(ln)
            out.append(AuditRec(
                ts=obj.get("ts", ""),
                mode=obj.get("mode", ""),
                event=obj.get("event", ""),
                feature=obj.get("feature"),
                level=obj.get("level", ""),
                raw=obj,
            ))
        except Exception:
            continue
    return out

def filter_recs(
    recs: Iterable[AuditRec],
    *,
    since: Optional[datetime] = None,
    until: Optional[datetime] = None,
    features: Optional[Sequence[str]] = None,
    levels: Optional[Sequence[str]] = None,
    keyword: Optional[str] = None,
) -> Iterator[AuditRec]:
    kw_pat = re.compile(re.escape(keyword), re.IGNORECASE) if keyword else None
    feat_set = set(x.lower() for x in features) if features else None
    lvl_set  = set(x.upper() for x in levels) if levels else None

    for r in recs:
        try:
            t = _parse_iso_utc(r.ts)
        except Exception:
            continue

        if since and t < since: continue
        if until and t >= until: continue
        if feat_set and (r.feature or "").lower() not in feat_set: continue
        if lvl_set and r.level.upper() not in lvl_set: continue

        if kw_pat:
            blob = f"{r.event} {r.feature} {r.level} {json.dumps(r.raw, ensure_ascii=False)}"
            if not kw_pat.search(blob):
                continue

        yield r

def to_csv(recs: Iterable[AuditRec], out_path: Path) -> Path:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["ts","mode","feature","level","event","json"])
        for r in recs:
            w.writerow([r.ts, r.mode, r.feature or "", r.level, r.event, json.dumps(r.raw, ensure_ascii=False)])
    return out_path

def load_for_ui(
    *,
    lookback: str = "1h",
    features: Optional[Sequence[str]] = None,
    levels: Optional[Sequence[str]] = None,
    keyword: Optional[str] = None,
    max_lines: int = 5000,
) -> List[AuditRec]:
    now = datetime.now(tz=UTC)
    amount = int(lookback[:-1])
    unit = lookback[-1].lower()
    if unit == "m": since = now - timedelta(minutes=amount)
    elif unit == "h": since = now - timedelta(hours=amount)
    elif unit == "d": since = now - timedelta(days=amount)
    else: raise ValueError("invalid lookback (use m/h/d)")
    until = now

    p = paths.logs_dir() / "audit.tail.jsonl"
    if not p.exists():
        p = paths.logs_dir() / "audit.jsonl"

    recs = tail_read(p, max_lines=max_lines)
    return list(filter_recs(recs, since=since, until=until, features=features, levels=levels, keyword=keyword))

def export_csv(
    out_rel: str = "export/audit_ui.csv",
    **kwargs
) -> Path:
    recs = load_for_ui(**kwargs)
    out = paths.logs_dir() / out_rel
    return to_csv(recs, out)

def to_compact_rows(recs: Iterable[AuditRec], *, max_summary_len: int = 160) -> List[dict]:
    rows: List[dict] = []
    for r in recs:
        rows.append({
            "ts": r.ts,
            "ts_local": _ts_to_local_iso(r.ts),
            "mode": r.mode,
            "feature": r.feature or "",
            "level": r.level,
            "event": r.event,
            "summary": _summarize_obj(r.raw, max_len=max_summary_len),
        })
    return rows

# --- public API expected by ui_audit.py -------------------------------------
def get_audit_rows(
    *,
    lookback: str = "1h",
    level: Optional[str] = None,
    q: Optional[str] = None,
    feature: Optional[str] = None,
    max_lines: int = 5000,
    max_summary_len: int = 160,
    tz_name: str = "Asia/Tokyo",
) -> List[dict]:
    """
    ui_audit 用の最小API。
    - lookback: '30m' / '1h' / '1d' など
    - level:   'INFO' | 'WARN' | 'ERROR' ...（単一指定・省略可）
    - q:       キーワード（要約・raw含むテキストに対して大小無視で検索）
    - feature: 機能名（単一指定・省略可）
    返り値: list[dict]（ts, ts_local, mode, feature, level, event, summary）
    """
    levels = [level] if level else None
    features = [feature] if feature else None
    recs = load_for_ui(
        lookback=lookback,
        features=features,
        levels=levels,
        keyword=q,
        max_lines=max_lines,
    )
    rows = to_compact_rows(recs, max_summary_len=max_summary_len)
    # ts_local を指定TZで付与（to_compact_rows内はデフォルトローカル→TZで上書き）
    if tz_name:
        for x in rows:
            try:
                x["ts_local"] = _ts_to_local_iso(x["ts"], tz_name=tz_name)
            except Exception:
                pass
    return rows

def export_csv_compact(
    out_rel: str = "export/audit_ui_compact.csv",
    *,
    lookback: str = "1h",
    features: Optional[Sequence[str]] = None,
    levels: Optional[Sequence[str]] = None,
    keyword: Optional[str] = None,
    max_lines: int = 5000,
    max_summary_len: int = 160,
) -> Path:
    recs = load_for_ui(lookback=lookback, features=features, levels=levels, keyword=keyword, max_lines=max_lines)
    rows = to_compact_rows(recs, max_summary_len=max_summary_len)
    out = paths.logs_dir() / out_rel
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["ts","mode","feature","level","event","summary"])
        for x in rows:
            w.writerow([x["ts"], x["mode"], x["feature"], x["level"], x["event"], x["summary"]])
    return out

def export_csv_compact_localtime(
    out_rel: str = "export/audit_ui_compact_local.csv",
    *,
    lookback: str = "1h",
    features: Optional[Sequence[str]] = None,
    levels: Optional[Sequence[str]] = None,
    keyword: Optional[str] = None,
    max_lines: int = 5000,
    max_summary_len: int = 160,
    tz_name: str = "Asia/Tokyo",
) -> Path:
    recs = load_for_ui(lookback=lookback, features=features, levels=levels, keyword=keyword, max_lines=max_lines)
    rows = to_compact_rows(recs, max_summary_len=max_summary_len)
    out = paths.logs_dir() / out_rel
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["ts","ts_local","mode","feature","level","event","summary"])
        for x in rows:
            ts_local = _ts_to_local_iso(x["ts"], tz_name=tz_name)
            w.writerow([x["ts"], ts_local, x["mode"], x["feature"], x["level"], x["event"], x["summary"]])
    return out


