# path: ./btc_trade_system/features/settings/settings_svc.py
# desc: 設定SVC（v2）：外部CONFIG強制／def→current合成／差分保存／原子的保存／キー単位ロック／監査emit一元。

from __future__ import annotations

from pathlib import Path
import os, time
import yaml
# NOTE: UI依存を避けるため、Streamlitは遅延参照に変更（必要時に取得）
st = None  # lazy import in functions

# 監査（実保存/既定適用の記録はSVCで一元emit）
from btc_trade_system.features.audit_dev import writer as W

REPO_ROOT = Path(__file__).resolve().parents[3]
CONFIG_DIR = REPO_ROOT / "btc_trade_system" / "config"  # current を一元管理

def _config_dir() -> Path:
    """
    設定の current を保存/読込するディレクトリ。
    - ENV: BTC_TS_CONFIG_DIR があれば最優先（複数PC運用・同期用）
    - それ以外はリポ内 CONFIG_DIR を使用
    """
    env = os.environ.get("BTC_TS_CONFIG_DIR")
    if env:
        p = Path(env)
        p.mkdir(parents=True, exist_ok=True)
        return p
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    return CONFIG_DIR

def _locks_dir() -> Path:
    d = _config_dir() / ".locks"
    d.mkdir(parents=True, exist_ok=True)
    return d

# ===== def/current パス解決 =====
def _feature_def_path(feature: str) -> Path:
    """
    機能内デフォルトのみ：
      <repo>/btc_trade_system/features/<feature>/config/<feature>_def.yaml
    """
    return REPO_ROOT / "btc_trade_system" / "features" / feature / "config" / f"{feature}_def.yaml"

def _feature_active_path(feature: str) -> Path:
    """current はリポ内 CONFIG_DIR に保存/読込する"""
    return _config_dir() / f"{feature}.yaml"

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
    """深い後勝ちマージに置き換え（互換のため関数名は維持）。"""
    if not isinstance(base, dict):
        return override if isinstance(override, dict) else {}
    out = dict(base)
    for k, v in (override or {}).items():
        bv = out.get(k)
        if isinstance(bv, dict) and isinstance(v, dict):
            out[k] = _shallow_merge(bv, v)
        else:
            out[k] = v
    return out

def _filter_by_schema(data: dict, schema: dict) -> dict:
    """def(=schema)に存在しないキーは破棄（再帰）。"""
    if not isinstance(data, dict) or not isinstance(schema, dict):
        return {}
    out = {}
    for k, v in data.items():
        if k not in schema:
            continue
        sv = schema[k]
        if isinstance(v, dict) and isinstance(sv, dict):
            sub = _filter_by_schema(v, sv)
            if sub:
                out[k] = sub
        else:
            out[k] = v
    return out

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
    """def＋current（currentはdefに存在するキーのみ）を深い後勝ちで返す。"""
    def_path, active_path = get_paths(feature)
    d_def = _load_yaml(def_path)
    d_cur = _load_yaml(active_path)
    if not isinstance(d_def, dict): d_def = {}
    if not isinstance(d_cur, dict): d_cur = {}
    d_cur = _filter_by_schema(d_cur, d_def)  # 未知キーは破棄
    return _shallow_merge(d_def, d_cur)

def has_default(feature: str = "dash") -> bool:
    """def存在チェック"""
    def_path, _ = get_paths(feature)
    return def_path.exists()

def save_yaml(feature: str, new_merged: dict) -> None:
    """
    差分保存：new_merged（= UI表示値：def+current合成済）から def を引き、差分のみを current に原子的保存。
    def に存在しないキーは保存対象外（破棄）とする。
    競合はキー単位ロックで fail fast。
    """
    d_def = load_def_yaml(feature)
    # ★ 追加：未知キーは保存前に除去
    filtered = _filter_by_schema(new_merged or {}, d_def or {})
    delta = _diff_from_def(filtered, d_def or {})

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
    """デフォルトに戻す＝current を空辞書にする（差分ゼロ）。"""
    _, active_path = get_paths(feature)
    with _KeyLock(feature):
        _write_yaml_atomic(active_path, {})

    try:
        W.emit(f"settings.default.apply.{feature}", level="INFO", feature=feature,
               payload={"path": str(active_path)})
    except Exception:
        pass

# ===== 既存ユーティリティ（UIタイトル／配色） =====
def get_ui_title(default: str = "BtcTradeSystem V1") -> str:
    d = load_yaml("dash")
    t = None
    if isinstance(d, dict):
        t = d.get("title")
        if not (isinstance(t, str) and t.strip()):
            t = (d.get("ui") or {}).get("title")
    return t.strip() if isinstance(t, str) and t.strip() else default

def _session_state() -> dict:
    """Streamlit未ロード時でも例外にしない薄い取得。"""
    global st
    try:
        if st is None:
            import streamlit as st  # type: ignore
            globals()['st'] = st
        return st.session_state  # type: ignore[attr-defined]
    except Exception:
        return {}

def get_alert_palette() -> dict:
    """def → current → session override の優先で配色（alert_chip）を返す。UI依存は任意化。"""
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

    ss = _session_state()
    ov = ss.get("_alerts_palette_overrides", {}) if isinstance(ss, dict) else {}
    for lv in ("warn", "crit", "urgent"):
        if lv in ov:
            if "fg" in ov[lv]: pal[lv]["fg"] = ov[lv]["fg"]
            if "bg" in ov[lv]: pal[lv]["bg"] = ov[lv]["bg"]
    return pal

def apply_palette_once(picks: dict) -> None:
    """今回のみ適用（セッションオーバーライドへ格納）。Streamlit非依存化。"""
    ss = _session_state()
    if isinstance(ss, dict):
        ss["_alerts_palette_overrides"] = picks

def reset_palette_to_default() -> None:
    """既定（dash_def.yaml）へ戻す（セッション内だけ）。"""
    base = (load_def_yaml("dash").get("colors") or {}).get("alert_chip") or {}
    def pick(sec, dfg, dbg):
        b = base.get(sec, {})
        return {"fg": b.get("fg", dfg), "bg": b.get("bg", dbg)}
    ss = _session_state()
    if isinstance(ss, dict):
        ss["_alerts_palette_overrides"] = {
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
            W.emit("settings.write.error.dash", level="ERROR", feature="dash", payload={"error": str(e)})
        except Exception:
            pass
        return False
