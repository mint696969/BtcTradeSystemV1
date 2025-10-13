# path: btc_trade_system/common/paths.py
# desc: データ/ログ等のパス解決（ENV優先・無ければ安全既定）
from __future__ import annotations
import os, pathlib, datetime as dt

def root() -> pathlib.Path:
    return pathlib.Path(__file__).resolve().parents[2]

def data_dir() -> pathlib.Path:
    p = os.getenv("BTC_TS_DATA_DIR") or r"D:\BtcTS_V1\data"
    return pathlib.Path(p)

def logs_dir() -> pathlib.Path:
    p = os.getenv("BTC_TS_LOGS_DIR") or r"D:\BtcTS_V1\logs"
    return pathlib.Path(p)

def ensure_dirs() -> None:
    for d in (data_dir(), logs_dir()):
        d.mkdir(parents=True, exist_ok=True)

def daily_log_path(prefix: str) -> pathlib.Path:
    d = logs_dir(); d.mkdir(parents=True, exist_ok=True)
    today = dt.datetime.utcnow().strftime("%Y%m%d")
    return d / f"{prefix}.{today}.log"
