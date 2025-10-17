# path: ./btc_trade_system/features/dash/health_svc.py
# desc: 健全性評価（Monitoring読込の骨 + 簡易判定）

from __future__ import annotations
import os, json, time, datetime as dt
from pathlib import Path

# ---- Monitoring 読込（PyYAMLが無ければ既定にフォールバック） ----
_DEFAULTS = {
    "health": {
        "age_sec":   {"ok": 10, "warn": 20, "crit": 30},
        "latency_ms":{"warn": 400, "crit": 1200},
        "gap_rate":  {"warn": 0.05, "crit": 0.15},
        "window_min": 5,
        "require_all_ok": True,
    },
    "slo": {
        "trades":    {"exp_intv_s": 1.0, "max_stale_s": 5},
        "ticker":    {"exp_intv_s": 1.0, "max_stale_s": 5},
        "orderbook": {"exp_intv_s": 2.0, "max_stale_s": 6},
    },
    "audit": {"success_sample_n": 50},
}

def _load_yaml(path: Path) -> dict|None:
    try:
        import yaml  # type: ignore
        with open(path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f) or {}
    except Exception:
        return None

def load_monitoring(cfg_root: Path) -> dict:
    # 優先: config/ui/monitoring.yaml → 次: config/ui/monitoring_def.yaml → 既定
    ui = cfg_root / "config" / "ui" / "monitoring.yaml"
    ui_def = cfg_root / "config" / "ui" / "monitoring_def.yaml"
    data = {}
    # 先に defaults → 後から user を当てて「user が最優先」になるようにする
    for p in (ui_def, ui):  # ← 順序を逆転（ui が最後）
        if p.exists():
            y = _load_yaml(p)
            if y:
                data.update(y)

    if not data:
        data = _DEFAULTS
    # 足りない所は既定で埋める
    def deepmerge(a, b):
        for k, v in b.items():
            if isinstance(v, dict):
                a.setdefault(k, {})
                deepmerge(a[k], v)
            else:
                a.setdefault(k, v)
        return a
    return deepmerge(data, _DEFAULTS)

# ---- 評価ロジック（簡易版：status.json優先） ----
def _now_ms() -> int:
    return int(time.time() * 1000)

def evaluate(status_json: Path, cfg_root: Path) -> dict:
    conf = load_monitoring(cfg_root)
    thr = conf["health"]
    slo = conf["slo"]
    require_all = thr.get("require_all_ok", True)

    items = []
    now = _now_ms()

    # status.json が無ければ空で返す
    if not status_json.exists():
        return {"items": [], "updated_at": dt.datetime.utcnow().isoformat() + "Z", "all_ok": False}

    with open(status_json, "r", encoding="utf-8") as f:
        st = json.load(f)

    for it in st.get("items", []):
        ex   = it.get("exchange")
        tp   = it.get("topic")
        last = it.get("last_ok_ms") or it.get("last_ok")  # 互換
        lat  = it.get("latency_ms")
        cause= it.get("cause")
        retries = it.get("retries", 0)

        age_sec = None
        if isinstance(last, (int, float)):
            age_sec = max(0.0, (now - int(last)) / 1000.0)

        # 1) 外因（cause）優先
        status = "OK"
        notes = []
        if cause in ("NET_BLOCK","AUTH_FAIL","RATE_LIMIT","DNS_FAIL","SRC_DOWN"):
            status = "CRIT"; notes.append(f"cause={cause}")

        # 2) SLO違反（topicごとの max_stale_s）
        if status == "OK" and age_sec is not None:
            slo_key = "trades" if tp == "trades" else ("orderbook" if tp == "orderbook" else "ticker")
            max_stale = slo.get(slo_key, {}).get("max_stale_s", 30)
            if age_sec > max_stale:
                status = "CRIT"; notes.append(f"age={age_sec:.1f}s>max_stale={max_stale}")

        # 3) 閾値判定
        if status == "OK" and age_sec is not None:
            if age_sec > thr["age_sec"]["crit"]:
                status = "CRIT"; notes.append(f"age>{thr['age_sec']['crit']}")
            elif age_sec > thr["age_sec"]["warn"]:
                status = "WARN"; notes.append(f"age>{thr['age_sec']['warn']}")

        if status == "OK" and lat is not None:
            if lat >= thr["latency_ms"]["crit"]:
                status = "CRIT"; notes.append(f"lat>={thr['latency_ms']['crit']}")
            elif lat >= thr["latency_ms"]["warn"]:
                status = "WARN"; notes.append(f"lat>={thr['latency_ms']['warn']}")

        items.append({
            "exchange": ex, "topic": tp, "status": status,
            "last_iso": dt.datetime.utcfromtimestamp((last or now)/1000).isoformat()+"Z",
            "age_sec": age_sec, "cause": cause, "retries": retries,
            "source": "status", "notes": " / ".join(notes),
        })

    all_ok = all(i["status"]=="OK" for i in items) if require_all else (all(i["status"]!="CRIT" for i in items) and any(i["status"]=="OK" for i in items))
    return {"items": items, "updated_at": dt.datetime.utcnow().isoformat() + "Z", "all_ok": all_ok}




