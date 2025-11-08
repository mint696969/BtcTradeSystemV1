# path: ./btc_trade_system/features/settings/settings_svc.py
# desc: 設定SVC（v2）：外部CONFIG強制／def→current合成／差分保存／原子的保存／キー単位ロック／監査emit一元。

from __future__ import annotations

from pathlib import Path
import os, time
import yaml
import streamlit as st

# 監査（実保存/既定適用の記録はSVCで一元emit）
from btc_trade_system.features.audit_dev import writer as W

REPO_ROOT = Path(__file__).resolve().parents[3]
INTERNAL_UI_DIR = REPO_ROOT / "btc_trade_system" / "config" / "ui"

# ===== 外部CONFIGディレクトリの解決（常に外部currentを採用。無ければ自動生成） =====
def _ext_config_dir() -> Path:
    """
    外部設定ルートの解決：
      1) ENV: BTC_TS_CONFIG_DIR（最優先） → 無ければ作成
      2) <repo>/data/config/ui → 無ければ作成
    ※ INTERNAL_UI_DIR は def 読み取り専用。書き込みには使用しない。
    """
    env = os.environ.get("BTC_TS_CONFIG_DIR")
    if env:
        p = Path(env)
        p.mkdir(parents=True, exist_ok=True)
        return p
    p = REPO_ROOT / "data" / "config" / "ui"
    p.mkdir(parents=True, exist_ok=True)
    return p

def _locks_dir() -> Path:
    d = _ext_config_dir().parent / ".locks"
    d.mkdir(parents=True, exist_ok=True)
    return d

# ===== def/current パス解決 =====
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
    """外部currentは外部設定ディレクトリ直下（存在しなくても良い。保存時に自動生成）"""
    return _ext_config_dir() / f"{feature}.yaml"

def get_paths(feature: str = "dash") -> tuple[Path, Path]:
    """(def_path, active_path) を返す"""
    return _feature_def_path(feature), _feature_active_path(feature)

# ===== 低レベル I/O =====
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

# ===== ロック（キー単位・簡易） =====
class _KeyLock:
    def __init__(self, key: str, timeout: float = 2.0):
        self.path = _locks_dir() / f"{key}.lock"
        self.timeout = timeout
        self.acquired = False

    def __enter__(self):
        start = time.time()
        while True:
            try:
                # O_EXCL を使いたいがOS差を避け、存在チェック→作成の最小実装
                if not self.path.exists():
                    self.path.write_text(str(os.getpid()), encoding="utf-8")
                    self.acquired = True
                    return self
            except Exception:
                pass
            if time.time() - start > self.timeout:
                raise TimeoutError(f"lock timeout: {self.path}")
            time.sleep(0.05)

    def __exit__(self, exc_type, exc, tb):
        if self.acquired and self.path.exists():
            try:
                self.path.unlink(missing_ok=True)
            except Exception:
                pass

# ===== 合成／差分 =====
def _shallow_merge(base: dict, override: dict) -> dict:
    merged = dict(base or {})
    for k, v in (override or {}).items():
        if isinstance(v, dict) and isinstance(merged.get(k), dict):
            merged[k] = {**merged[k], **v}
        else:
            merged[k] = v
    return merged

def _diff_from_def(cur_merged: dict, d_def: dict) -> dict:
    """
    def と比較して“差分だけ”を返す（保存は最小差分）。
    値が辞書なら再帰。差分なしは {}。
    """
    out = {}
    for k, v in cur_merged.items():
        dv = d_def.get(k)
        if isinstance(v, dict) and isinstance(dv, dict):
            sub = _diff_from_def(v, dv)
            if sub:
                out[k] = sub
        else:
            if v != dv:
                out[k] = v
    return out

# ===== 公開I/F =====
def load_def_yaml(feature: str = "dash") -> dict:
    """defのみ返す"""
    def_path, _ = get_paths(feature)
    d = _load_yaml(def_path)
    return d if isinstance(d, dict) else {}

def load_yaml(feature: str = "dash") -> dict:
    """
    def＋active（active優先の浅いマージ）を返す。
    """
    def_path, active_path = get_paths(feature)
    d_def = _load_yaml(def_path)
    d_cur = _load_yaml(active_path)
    if not isinstance(d_def, dict): d_def = {}
    if not isinstance(d_cur, dict): d_cur = {}
    return _shallow_merge(d_def, d_cur)

def has_default(feature: str = "dash") -> bool:
    """def存在チェック"""
    def_path, _ = get_paths(feature)
    return def_path.exists()

def save_yaml(feature: str, new_merged: dict) -> None:
    """
    差分保存：new_merged（= UI表示値：def+current合成済）から def を引き、差分のみを current に原子的保存。
    競合はキー単位ロックで fail fast。
    """
    d_def = load_def_yaml(feature)
    delta = _diff_from_def(new_merged or {}, d_def or {})

    _, active_path = get_paths(feature)
    with _KeyLock(feature):
        _write_yaml_atomic(active_path, delta)

    try:
        changed_keys = sorted(list(delta.keys()))
        W.emit(f"settings.write.{feature}", level="INFO", feature=feature,
               payload={"changed_keys": changed_keys, "path": str(active_path)})
    except Exception:
        pass

def reset_to_default(feature: str) -> None:
    """
    デフォルトに戻して保存（= def を current へ丸ごと書き出し）。
    """
    d_def = load_def_yaml(feature)
    _, active_path = get_paths(feature)
    with _KeyLock(feature):
        _write_yaml_atomic(active_path, d_def if isinstance(d_def, dict) else {})

    try:
        W.emit(f"settings.default.apply.{feature}", level="INFO", feature=feature,
               payload={"path": str(active_path)})
    except Exception:
        pass

# ===== 既存ユーティリティ（UIタイトル／配色） =====
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
    """既定（dash_def.yaml）に戻す（セッション内だけ）"""
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
    """dash.yaml（外部current）へ原子的保存（差分抽出は colors.alert_chip に限定）"""
    try:
        data = load_yaml("dash")  # def+active の合成 → UI表示値同等
        data.setdefault("colors", {}).setdefault("alert_chip", {})
        for lv, pair in (picks or {}).items():
            if lv not in ("warn", "crit", "urgent"):
                continue
            cur = data["colors"]["alert_chip"].get(lv, {})
            cur["fg"] = pair.get("fg", cur.get("fg", "#000000"))
            cur["bg"] = pair.get("bg", cur.get("bg", "#FFF2CC"))
            data["colors"]["alert_chip"][lv] = cur

        # alert_chip セクションのみ差分抽出して dash に保存
        save_yaml("dash", data)
        return True
    except Exception as e:
        try:
            W.emit("settings.write.error.dash", level="ERROR", feature="dash",
                   payload={"error": str(e)})
        except Exception:
            pass
        st.warning(f"配色の保存に失敗しました: {e}")
        return False
