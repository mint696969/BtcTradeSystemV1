# path: ./btc_trade_system/features/settings/settings_svc.py
# desc: 設定タブ用サービス層。def→current→session の解決、保存、デフォルト復元を提供。

from __future__ import annotations

from pathlib import Path
import os
import yaml
import streamlit as st

REPO_ROOT = Path(__file__).resolve().parents[3]
INTERNAL_UI_DIR = REPO_ROOT / "btc_trade_system" / "config" / "ui"

def _ext_config_dir() -> Path:
    """
    外部設定ルートの解決：
      1) ENV: BTC_TS_CONFIG_DIR
      2) <repo>/data/config/ui
      3) 無ければ INTERNAL_UI_DIR（読取り専用運用を想定、書込はmkdirで外部を作成）
    """
    env = os.environ.get("BTC_TS_CONFIG_DIR")
    if env:
        return Path(env)
    candidate = REPO_ROOT / "data" / "config" / "ui"
    return candidate if candidate.exists() else INTERNAL_UI_DIR

def _feature_def_path(feature: str) -> Path:
    """
    機能内デフォルト優先：
      <repo>/btc_trade_system/features/<feature>/config/<feature>_def.yaml
      無ければ <repo>/btc_trade_system/config/ui/<feature>_def.yaml
    """
    local = REPO_ROOT / "btc_trade_system" / "features" / feature / "config" / f"{feature}_def.yaml"
    if local.exists():
        return local
    return INTERNAL_UI_DIR / f"{feature}_def.yaml"

def _feature_active_path(feature: str) -> Path:
    """
    外部currentは外部設定ディレクトリ直下（存在しなければ、将来保存時に自動生成）
    """
    return _ext_config_dir() / f"{feature}.yaml"

def get_paths(feature: str = "dash") -> tuple[Path, Path]:
    """(def_path, active_path) を返す"""
    return _feature_def_path(feature), _feature_active_path(feature)

def _load_yaml(p: Path) -> dict:
    if not p.exists():
        return {}
    with p.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}

def _write_yaml_atomic(p: Path, data: dict) -> None:
    p.parent.mkdir(parents=True, exist_ok=True)
    tmp = p.with_suffix(p.suffix + ".tmp")
    with tmp.open("w", encoding="utf-8") as f:
        yaml.safe_dump(data, f, allow_unicode=True, sort_keys=False)
        f.flush()
        os.fsync(f.fileno())
    os.replace(tmp, p)

def load_yaml(feature: str = "dash") -> dict:
    """
    def＋active（active優先の浅いマージ）を返す。
    """
    def_path, active_path = get_paths(feature)
    d_def = _load_yaml(def_path)
    d_cur = _load_yaml(active_path)
    if not isinstance(d_def, dict): d_def = {}
    if not isinstance(d_cur, dict): d_cur = {}
    # 浅いマージ（ネストは必要箇所以外は浅くてOK）
    merged = dict(d_def)
    for k, v in d_cur.items():
        if isinstance(v, dict) and isinstance(merged.get(k), dict):
            merged[k] = {**merged[k], **v}
        else:
            merged[k] = v
    return merged

def load_def_yaml(feature: str = "dash") -> dict:
    """defのみ返す"""
    def_path, _ = get_paths(feature)
    d = _load_yaml(def_path)
    return d if isinstance(d, dict) else {}

def save_yaml(feature: str, data: dict) -> None:
    """外部currentへ原子的保存。保存前に tmp へ退避は上位で実施する方針なら省略可"""
    _, active_path = get_paths(feature)
    _write_yaml_atomic(active_path, data)

def has_default(feature: str = "dash") -> bool:
    """def存在チェック"""
    def_path, _ = get_paths(feature)
    return def_path.exists()

def get_ui_title(default: str = "BtcTradeSystem V1") -> str:
    d = load_yaml("dash")
    t = d.get("title") if isinstance(d, dict) else None
    return t.strip() if isinstance(t, str) and t.strip() else default

def get_alert_palette() -> dict:
    """def → current → session override の優先で配色（alert_chip）を返す"""
    base = (load_def_yaml("dash").get("colors") or {}).get("alert_chip") or {}
    cur  = (load_yaml("dash").get("colors") or {}).get("alert_chip") or {}

    pal = {
        "warn":   {"fg": (cur.get("warn")  or {}).get("fg", (base.get("warn")  or {}).get("fg", "#000000")),
                   "bg": (cur.get("warn")  or {}).get("bg", (base.get("warn")  or {}).get("bg", "#FFF2CC"))},
        "crit":   {"fg": (cur.get("crit")  or {}).get("fg", (base.get("crit")  or {}).get("fg", "#000000")),
                   "bg": (cur.get("crit")  or {}).get("bg", (base.get("crit")  or {}).get("bg", "#FFCCCC"))},
        "urgent": {"fg": (cur.get("urgent")or {}).get("fg", (base.get("urgent")or {}).get("fg", "#FFFFFF")),
                   "bg": (cur.get("urgent")or {}).get("bg", (base.get("urgent")or {}).get("bg", "#FF6666"))},
    }

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
    """既定（<feature>/config/dash_def.yaml または internal）に戻す（セッション内だけ）"""
    base = (load_def_yaml("dash").get("colors") or {}).get("alert_chip") or {}
    def pick(sec, dfg, dbg):
        b = base.get(sec, {})
        return {"fg": b.get("fg", dfg), "bg": b.get("bg", dbg)}
    st.session_state["_alerts_palette_overrides"] = {
        "urgent": pick("urgent", "#FFFFFF", "#FF6666"),
        "crit":   pick("crit",   "#000000", "#FFCCCC"),
        "warn":   pick("warn",   "#000000", "#FFF2CC"),
    }

def save_palette(picks: dict) -> bool:
    """dash.yaml（外部current）へ原子的保存"""
    try:
        data = load_yaml("dash")  # def+activeの浅いマージを取得 → 上書きでcurrentへ保存
        data.setdefault("colors", {}).setdefault("alert_chip", {})
        for lv, pair in picks.items():
            if lv not in ("warn","crit","urgent"):
                continue
            cur = data["colors"]["alert_chip"].get(lv, {})
            cur["fg"] = pair.get("fg", cur.get("fg", "#000000"))
            cur["bg"] = pair.get("bg", cur.get("bg", "#FFF2CC"))
            data["colors"]["alert_chip"][lv] = cur
        save_yaml("dash", data)
        return True
    except Exception as e:
        st.warning(f"配色の保存に失敗しました: {e}")
        return False
