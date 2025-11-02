# path: ./btc_trade_system/features/settings/settings_svc.py
# desc: 設定タブ用サービス層。def→current→session の解決、保存、デフォルト復元を提供。

from __future__ import annotations
from pathlib import Path
import os, yaml
import streamlit as st

REPO_ROOT = Path(__file__).resolve().parents[3]
CONFIG_UI_DIR = REPO_ROOT / "btc_trade_system" / "config" / "ui"
DASH_PATH      = CONFIG_UI_DIR / "dash.yaml"
DASH_DEF_PATH  = CONFIG_UI_DIR / "dash_def.yaml"

def _load_yaml(p: Path) -> dict:
    if not p.exists():
        return {}
    with p.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}

def get_ui_title(default: str = "BtcTradeSystem V1") -> str:
    d = _load_yaml(DASH_PATH)
    t = d.get("title") if isinstance(d, dict) else None
    return t.strip() if isinstance(t, str) and t.strip() else default

def get_alert_palette() -> dict:
    """def → current → session override の優先で配色（alert_chip）を返す"""
    base = (_load_yaml(DASH_DEF_PATH).get("colors") or {}).get("alert_chip") or {}
    cur  = (_load_yaml(DASH_PATH).get("colors") or {}).get("alert_chip") or {}

    # マージ（current 優先、なければ base）
    pal = {
        "warn":   {"fg": (cur.get("warn")  or {}).get("fg", (base.get("warn")  or {}).get("fg", "#000000")),
                   "bg": (cur.get("warn")  or {}).get("bg", (base.get("warn")  or {}).get("bg", "#FFF2CC"))},
        "crit":   {"fg": (cur.get("crit")  or {}).get("fg", (base.get("crit")  or {}).get("fg", "#000000")),
                   "bg": (cur.get("crit")  or {}).get("bg", (base.get("crit")  or {}).get("bg", "#FFCCCC"))},
        "urgent": {"fg": (cur.get("urgent")or {}).get("fg", (base.get("urgent")or {}).get("fg", "#FFFFFF")),
                   "bg": (cur.get("urgent")or {}).get("bg", (base.get("urgent")or {}).get("bg", "#FF6666"))},
    }

    # セッション上書き
    ov = st.session_state.get("_alerts_palette_overrides", {}) or {}
    for lv in ("warn", "crit", "urgent"):
        if lv in ov:
            if "fg" in ov[lv]:
                pal[lv]["fg"] = ov[lv]["fg"]
            if "bg" in ov[lv]:
                pal[lv]["bg"] = ov[lv]["bg"]

    return pal

def apply_palette_once(picks: dict) -> None:
    """今回のみ適用（セッションオーバーライドへ格納）"""
    st.session_state["_alerts_palette_overrides"] = picks

def reset_palette_to_default() -> None:
    """既定（dash_def.yaml）に戻す（セッション内だけ）"""
    base = (_load_yaml(DASH_DEF_PATH).get("colors") or {}).get("alert_chip") or {}
    def pick(sec, dfg, dbg):
        b = base.get(sec, {})
        return {"fg": b.get("fg", dfg), "bg": b.get("bg", dbg)}
    st.session_state["_alerts_palette_overrides"] = {
        "urgent": pick("urgent", "#FFFFFF", "#FF6666"),
        "crit":   pick("crit",   "#000000", "#FFCCCC"),
        "warn":   pick("warn",   "#000000", "#FFF2CC"),
    }

def save_palette(picks: dict) -> bool:
    """dash.yaml へ原子的保存（.tmp→fsync→replace）。必要時のみ親dir作成。"""
    try:
        data = _load_yaml(DASH_PATH)
        data.setdefault("colors", {}).setdefault("alert_chip", {})
        for lv, pair in picks.items():
            if lv not in ("warn","crit","urgent"):
                continue
            cur = data["colors"]["alert_chip"].get(lv, {})
            cur["fg"] = pair.get("fg", cur.get("fg", "#000000"))
            cur["bg"] = pair.get("bg", cur.get("bg", "#FFF2CC"))
            data["colors"]["alert_chip"][lv] = cur
        DASH_PATH.parent.mkdir(parents=True, exist_ok=True)
        tmp = DASH_PATH.with_suffix(".yaml.tmp")
        with tmp.open("w", encoding="utf-8") as f:
            yaml.safe_dump(data, f, allow_unicode=True, sort_keys=False)
            f.flush(); os.fsync(f.fileno())
        os.replace(tmp, DASH_PATH)
        return True
    except Exception as e:
        st.warning(f"配色の保存に失敗しました: {e}")
        return False
