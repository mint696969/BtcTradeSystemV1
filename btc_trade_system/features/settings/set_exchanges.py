# path: ./btc_trade_system/features/settings/set_exchanges.py
# desc: 取引所登録タブ(exchanges)の設定SVC：exchanges.yaml と secrets/exchanges.ini の読み書き・マージ保存。

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, Optional
import os
import configparser

from btc_trade_system.features.audit_dev import writer as W
from . import settings_svc as S


REPO_ROOT = Path(__file__).resolve().parents[3]


# ===== CONFIG / SECRETS パス解決 ============================================

def _config_dir() -> Path:
    """settings_svc と同一の外部CONFIG DIR(config/ui 想定)を返す。"""
    return S._config_dir()  # type: ignore[attr-defined]


def _secrets_dir() -> Path:
    """exchanges.ini を配置する secrets DIR を返す。

    優先順位:
      1) ENV BTC_TS_SECRETS_DIR
      2) ENV BTC_TS_DATA_DIR or BTC_TS_DATA_ROOT があればその親ディレクトリ直下の secrets/
      3) CONFIG DIR (config/ui) の親 (= config) の親 直下の secrets/
    """
    env = os.environ.get("BTC_TS_SECRETS_DIR")
    if env:
        p = Path(env)
        p.mkdir(parents=True, exist_ok=True)
        return p

    data_env = os.environ.get("BTC_TS_DATA_DIR") or os.environ.get("BTC_TS_DATA_ROOT")
    if data_env:
        base = Path(data_env).resolve().parent
    else:
        # 最後の手段: config/ui -> config -> <V1_ROOT>
        base = _config_dir().resolve().parents[1]

    secrets_dir = base / "secrets"
    secrets_dir.mkdir(parents=True, exist_ok=True)
    return secrets_dir


def _secrets_path() -> Path:
    """exchanges 用 secrets ファイルパス (…/secrets/exchanges.ini)。"""
    return _secrets_dir() / "exchanges.ini"


# ===== INI 読み書き (atomic) ===============================================

def _load_ini() -> configparser.ConfigParser:
    cp = configparser.ConfigParser()
    p = _secrets_path()
    if p.exists():
        cp.read(p, encoding="utf-8")
    return cp


def _write_ini_atomic(cp: configparser.ConfigParser) -> None:
    p = _secrets_path()
    p.parent.mkdir(parents=True, exist_ok=True)
    tmp = p.with_suffix(p.suffix + ".tmp")
    with tmp.open("w", encoding="utf-8") as f:
        cp.write(f)
        f.flush()
        os.fsync(f.fileno())
    os.replace(tmp, p)


# ===== 公開 I/F：exchanges.yaml (非秘匿設定) ===============================

def load_exchanges() -> Dict[str, Any]:
    """設定タブ UI 向け: exchanges.yaml(def+current 合成) を返すラッパ。

    settings_svc.load_yaml("exchanges") に単純委譲し、dict 以外は {} を返す。
    実際のスキーマは exchanges_def.yaml に従う。
    """
    data = S.load_yaml("exchanges")  # type: ignore[attr-defined]
    return data if isinstance(data, dict) else {}


def save_exchanges(merged: Dict[str, Any]) -> None:
    """設定タブ UI からの保存値をそのまま save_yaml("exchanges") に渡す。"""
    if not isinstance(merged, dict):
        return
    S.save_yaml("exchanges", merged)  # type: ignore[attr-defined]


# ===== 公開 I/F：APIキー (secrets/exchanges.ini) ===========================

def get_api_key_status(exchange: str) -> str:
    """APIキー状態を簡易に返す。

    戻り値:
      - "none"       … セクションなし（キー未登録）
      - "registered" … セクションあり＆いずれかの値が非空
    将来必要になれば "partial" 等を追加する余地を残す。
    """
    cp = _load_ini()
    if not cp.has_section(exchange):
        return "none"
    sec = cp[exchange]
    # 1つでも非空値があれば registered
    for _, v in sec.items():
        if isinstance(v, str) and v.strip():
            return "registered"
    return "none"


def load_secrets(exchange: str) -> Dict[str, str]:
    """指定取引所の secrets を dict で返す（存在しなければ {}）。"""
    cp = _load_ini()
    if not cp.has_section(exchange):
        return {}
    sec = cp[exchange]
    return {k: v for k, v in sec.items()}


def save_secrets(exchange: str, updates: Dict[str, Optional[str]]) -> None:
    """APIキー等の secrets をマージ保存する。

    仕様:
      - 既存セクションを読み込み、updates で指定されたキーのみ変更
      - value が None のキーは "変更しない"（既存値を維持）
      - value が "" (空文字) のキーは "削除"（項目ごと削除）
      - それ以外の文字列はそのまま上書き
    セクション内に項目が 0 件になってもセクション自体は残す（運用で明示削除したい場合は delete_secrets() を利用）。
    """
    if not isinstance(updates, dict):
        return

    cp = _load_ini()
    if not cp.has_section(exchange):
        cp.add_section(exchange)
    sec = cp[exchange]

    changed_keys = []
    for k, v in updates.items():
        if v is None:
            # 変更しない
            continue
        if isinstance(v, str) and v == "":
            if k in sec:
                sec.pop(k, None)
                changed_keys.append(k)
            continue
        # 通常の上書き
        sec[k] = str(v)
        changed_keys.append(k)

    _write_ini_atomic(cp)

    try:
        W.emit(
            "settings.exchanges.secrets.write",
            level="INFO",
            feature="settings",
            payload={"exchange": exchange, "keys": changed_keys, "path": str(_secrets_path())},
        )
    except Exception:
        pass


def delete_secrets(exchange: str) -> None:
    """指定取引所の API キー情報を全削除する。"""
    cp = _load_ini()
    if cp.remove_section(exchange):
        _write_ini_atomic(cp)
        try:
            W.emit(
                "settings.exchanges.secrets.delete",
                level="INFO",
                feature="settings",
                payload={"exchange": exchange, "path": str(_secrets_path())},
            )
        except Exception:
            pass


# ===== API: Scheduler 向け exchange policy 計算 ============================

def _pick_exchange_entry(cfg: Dict[str, Any], exchange: str) -> Optional[Dict[str, Any]]:
    """exchanges.yaml の構造差異を吸収して 1 取引所分の dict を返す。

    想定する2パターン:
      A) ルート直下に取引所キー:
           { bitflyer: {...}, binance: {...}, ... }
      B) ルートに exchanges: サブキー:
           { exchanges: { bitflyer: {...}, ... } }
    どちらでも動くようにしておく。
    """
    if not isinstance(cfg, dict):
        return None

    # Bパターン: cfg["exchanges"][exchange]
    root = cfg
    if "exchanges" in cfg and isinstance(cfg["exchanges"], dict):
        root = cfg["exchanges"]

    entry = root.get(exchange)
    return entry if isinstance(entry, dict) else None


def get_exchange_policy(exchange: str, safety_factor: float) -> Optional[Dict[str, float]]:
    """Scheduler 用: 1 取引所分の max_rps / burst を計算して返す。

    前提スキーマ（exchanges_def.yaml 側）:
      - official_max_rps: float (>0)
      - burst_base_sec:  float (>=0)  … burst = effective_max_rps * burst_base_sec

    計算式:
      effective_max_rps = official_max_rps * safety_factor
      burst             = effective_max_rps * burst_base_sec

    official_max_rps が未設定または <=0 の場合は None を返す。
    """
    try:
        cfg = load_exchanges()
        entry = _pick_exchange_entry(cfg, exchange)
        if not isinstance(entry, dict):
            return None

        official = entry.get("official_max_rps")
        base_sec = entry.get("burst_base_sec", 2.0)

        try:
            official_f = float(official)
            base_sec_f = float(base_sec)
            safety_f = float(safety_factor)
        except (TypeError, ValueError):
            return None

        if official_f <= 0 or safety_f <= 0:
            return None
        if base_sec_f < 0:
            base_sec_f = 0.0

        effective = official_f * safety_f
        burst = effective * base_sec_f

        return {
            "official_max_rps": official_f,
            "safety_factor": safety_f,
            "effective_max_rps": effective,
            "burst_base_sec": base_sec_f,
            "burst": burst,
        }

    except Exception:
        return None
