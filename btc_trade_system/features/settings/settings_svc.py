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
    with p.open("r", encoding="utf-8-sig") as f:
        return yaml.safe_load(f) or {}

def _write_yaml_atomic(p: Path, data: dict) -> None:
    p.parent.mkdir(parents=True, exist_ok=True)
    tmp = p.with_suffix(p.suffix + ".tmp")
    with tmp.open("w", encoding="utf-8-sig") as f:
        yaml.safe_dump(data, f, allow_unicode=True, sort_keys=False)
        f.flush()
        os.fsync(f.fileno())
    os.replace(tmp, p)

# ---- audit helpers (lightweight) -------------------------------------------
def _debug_audit_enabled() -> bool:
    # 既定は“出さない”。必要時のみ環境でON（例: BTC_TS_DEBUG_AUDIT=1）
    return os.environ.get("BTC_TS_DEBUG_AUDIT") == "1"

def _audit_try(op: str, feature: str, path: Path, payload: dict | None = None) -> None:
    if not _debug_audit_enabled():
        return
    try:
        W.emit(f"settings.{op}.try.{feature}", level="INFO", feature="settings",
               payload={"path": str(path), "feature": feature, **(payload or {})})
    except Exception:
        pass

def _audit_done(op: str, feature: str, path: Path, payload: dict | None = None) -> None:
    if not _debug_audit_enabled():
        return
    try:
        W.emit(f"settings.{op}.done.{feature}", level="INFO", feature="settings",
               payload={"path": str(path), "feature": feature, **(payload or {})})
    except Exception:
        pass
def _audit_err(op: str, feature: str, path: Path, err: Exception, payload: dict | None = None) -> None:
    """
    DEBUG監査向けの補助エラー行（常時emitしている settings.*.error.<key> とは別系統）。
    _debug_audit_enabled() が有効のときのみ出力。
    """
    if not _debug_audit_enabled():
        return
    try:
        W.emit(f"settings.{op}.error.{feature}", level="ERROR", feature="settings",
               payload={"path": str(path), "feature": feature, "err": repr(err), **(payload or {})})
    except Exception:
        pass

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
    差分が空のときは“保存も監査も行わない”（無駄な書込みとノイズを避ける）。
    """

    # --- [任意の保護] UI以外の保存を抑止（デフォルト無効） -----------------------
    if os.environ.get("BTC_TS_SAVE_UI_ONLY") == "1":
        if os.environ.get("BTC_TS_ALLOW_SCRIPT_WRITE") != "1":
            ss = _session_state()
            if not (isinstance(ss, dict) and ss.get("_settings_ui_in_progress") is True):
                try:
                    _, _active_path = get_paths(feature)
                    W.emit(f"settings.write.blocked.{feature}", level="INFO", feature="settings",
                           payload={"reason": "UI-only guard", "env_save_ui_only": True,
                                    "path": str(_active_path)})
                except Exception:
                    pass
                return

    d_def = load_def_yaml(feature)
    filtered = _filter_by_schema(new_merged or {}, d_def or {})
    delta = _diff_from_def(filtered, d_def or {})

    # ★ 差分ゼロ：何もしない
    if not delta:
        return

    _, active_path = get_paths(feature)
    _audit_try("write", feature, active_path, {"changed_keys": sorted(list(delta.keys()))})
    try:
        with _KeyLock(feature):
            # ★ ヘッダー生成
            rel_path = f"./btc_trade_system/config/{feature}.yaml"
            header = (
                f"# path: {rel_path}\n"
                f"# desc: {feature} の外部設定（def との差分のみ保存）\n"
            )

            # YAML 本体
            body = yaml.safe_dump(delta, allow_unicode=True, sort_keys=False)

            tmp = active_path.with_suffix(active_path.suffix + ".tmp")
            with tmp.open("w", encoding="utf-8-sig") as f:
                f.write(header)
                f.write(body)
                f.flush()
                os.fsync(f.fileno())
            os.replace(tmp, active_path)

        try:
            changed_keys = sorted(list(delta.keys()))
            W.emit(f"settings.write.{feature}", level="INFO", feature=feature,
                   payload={"changed_keys": changed_keys, "path": str(active_path)})
        except Exception:
            pass

        _audit_done("write", feature, active_path, {"changed_keys": sorted(list(delta.keys()))})

    except Exception as e:
        _audit_err("write", feature, active_path, e, {"changed_keys": sorted(list(delta.keys()))})
        raise

# 追加: スクリプト/テスト用の強制保存API（UIガードをバイパス）
def force_save_yaml(area: str, data: dict) -> bool:
    """
    UIを介さないテスト/スクリプト用途の保存ルート。
    - *_def.yaml のスキーマで未知キーを除去
    - current 側に原子的に書き出し
    - 監査ログは通常の save と同じ規約で記録（可能なら）
    """
    try:
        def_path, active_path = get_paths(area)
        schema = _load_yaml(def_path) or {}
        filtered = _filter_by_schema(data or {}, schema)

        # ★ 追加: 試行ログ
        _audit_try("write", area, active_path, {"keys": list(filtered.keys()), "source": "script"})

        _write_yaml_atomic(active_path, filtered)

        try:
            W.emit(f"settings.write.{area}", level="INFO", feature="settings",
                   payload={"path": str(active_path), "keys": list(filtered.keys())})
        except Exception:
            pass

        # ★ 追加: 完了ログ
        _audit_done("write", area, active_path, {"keys": list(filtered.keys()), "source": "script"})
        return True

    except Exception as e:
        # 既存 error に加え、詳細を統一形で
        try:
            W.emit(f"settings.write.error.{area}", level="ERROR", feature="settings",
                   payload={"err": repr(e)})
        except Exception:
            pass
        _audit_err("write", area, active_path if 'active_path' in locals() else Path(""), e,
                   {"source": "script"})
        return False

def reset_to_default(feature: str) -> None:
    """デフォルトに戻す＝current を物理削除（ファイルなし）"""
    _, active_path = get_paths(feature)
    _audit_try("default", feature, active_path, {"action": "remove_current"})

    try:
        with _KeyLock(feature):
            # ★ 差分なし → ファイル削除（0 バイトや {} ではなく確実に消す）
            active_path.unlink(missing_ok=True)

        try:
            W.emit(f"settings.default.apply.{feature}", level="INFO", feature=feature,
                   payload={"path": str(active_path), "action": "removed"})
        except Exception:
            pass

        _audit_done("default", feature, active_path, {"action": "removed"})

    except Exception as e:
        _audit_err("default", feature, active_path, e, {"action": "remove_current"})
        raise

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
