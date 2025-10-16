# path: ./btc_trade_system/features/dash/providers.py
# desc: ダッシュボード用データ供給（健全性サマリ/表）

from __future__ import annotations
from pathlib import Path
from ...common import paths
from .health_svc import evaluate
from collections import deque
import json

def _cfg_root() -> Path:
    # features/dash/providers.py から見た pkg ルート（parents[2]）
    return Path(__file__).resolve().parents[2]  # => .../btc_trade_system

def _load_order(cfg_root: Path) -> list[str]:
    """
    表示順序（カード順）:
    - config/ui/health.yaml の order を最優先
    - なければ config/ui_defaults/health.yaml
    - それも無ければ evaluate() の items の出現順
    """
    def _yload(p: Path):
        try:
            import yaml  # type: ignore
            if p.exists():
                return (yaml.safe_load(p.read_text(encoding="utf-8")) or {})
        except Exception:
            pass
        return {}
    ui = cfg_root / "config" / "ui" / "health.yaml"
    ui_def = cfg_root / "config" / "ui_defaults" / "health.yaml"
    for p in (ui, ui_def):
        y = _yload(p)
        if isinstance(y, dict) and isinstance(y.get("order"), list):
            return [str(x) for x in y["order"]]
    return []

def get_health_summary() -> dict:
    """
    UIカード/グラフ向け:
    {
      "updated_at": "...Z",
      "order": ["bitflyer","binance","bybit","okx"],
      "cards": [
        {"exchange":"binance","status":"OK","age_sec":2.1,"notes":""}, ...
      ],
      "all_ok": false
    }
    """
    cfg_root = _cfg_root()
    status = paths.data_dir() / "collector" / "status.json"
    try:
        summary = evaluate(status, cfg_root)
    except Exception:
        summary = {"items": [], "updated_at": None, "all_ok": False}
    order = _load_order(cfg_root)
    items = summary.get("items", [])

    # order 指定があればそれに並べ替え（未指定は末尾）
    if order:
        order_index = {ex: i for i, ex in enumerate(order)}
        items = sorted(items, key=lambda x: order_index.get(x.get("exchange",""), 10**6))

    cards = [
        {
            "exchange": i.get("exchange"),
            "status":   i.get("status"),
            "age_sec":  i.get("age_sec"),
            "notes":    i.get("notes",""),
        }
        for i in items
    ]
    return {
        "updated_at": summary.get("updated_at"),
        "order": order or [i.get("exchange") for i in items],
        "cards": cards,
        "all_ok": summary.get("all_ok", False),
    }

def get_health_table() -> list[dict]:
    """
    詳細表向け（色分けせず情報重視）:
    [ {exchange, topic, last_iso, age_sec, status, notes, source}, ... ]
    順序は get_health_summary() の order に合わせる。
    """
    cfg_root = _cfg_root()
    status = paths.data_dir() / "collector" / "status.json"
    try:
        summary = evaluate(status, cfg_root)
    except Exception:
        summary = {"items": [], "updated_at": None, "all_ok": False}
    order = _load_order(cfg_root)
    items = summary.get("items", [])
    if order:
        order_index = {ex: i for i, ex in enumerate(order)}
        items = sorted(items, key=lambda x: (order_index.get(x.get("exchange",""), 10**6), x.get("topic","")))

    table = []
    for i in items:
        table.append({
            "exchange": i.get("exchange"),
            "topic":    i.get("topic"),
            "last_iso": i.get("last_iso"),
            "age_sec":  i.get("age_sec"),
            "status":   i.get("status"),
            "notes":    i.get("notes",""),
            "source":   i.get("source"),
        })
    return table

def get_audit_rows(limit: int = 500) -> list[dict]:
    """
    logs/audit.jsonl を末尾から最大 limit 件だけ読み返し（新しい順）。
    メモリ効率のため deque(maxlen=limit) を使用。
    """
    log = paths.logs_dir() / "audit.jsonl"
    if not log.exists():
        return []

    buf: deque[dict] = deque(maxlen=limit)
    with open(log, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                buf.append(json.loads(line))
            except Exception:
                continue

    # buf は古い→新しいの順で詰まっている想定。新しい順で返すために逆順に。
    return list(reversed(buf))