# path: ./btcts_next/src/btcts/core/env.py
# desc: 環境変数（DATA/LOGS/CONFIG/SECRETS/DATASET 等）を正準化して取得する。

from __future__ import annotations

import os
from pathlib import Path
from typing import Optional


def repo_root() -> Path:
    """btcts_next のリポルート（btcts_next/）を返す。"""
    # .../btcts_next/src/btcts/core/env.py -> parents[3] == btcts_next
    return Path(__file__).resolve().parents[3]


def _expand(p: str) -> Path:
    return Path(os.path.expandvars(os.path.expanduser(p))).resolve()


def env_or_default(var_name: str, default: str) -> Path:
    """環境変数 var_name を Path として返す（未設定なら default）。"""
    v = os.environ.get(var_name)
    if v and v.strip():
        return _expand(v.strip())
    return _expand(default)


def env_str(var_name: str, default: Optional[str] = None) -> Optional[str]:
    v = os.environ.get(var_name)
    if v and v.strip():
        return v.strip()
    return default


# ---- 正準 ENV 名（本番で固定） --------------------------------------------
ENV_DATA_DIR = "BTC_TS_DATA_DIR"
ENV_LOGS_DIR = "BTC_TS_LOGS_DIR"
ENV_CONFIG_DIR = "BTC_TS_CONFIG_DIR"
ENV_SECRETS_DIR = "BTC_TS_SECRETS_DIR"
ENV_DATASET_DIR = "BTC_TS_DATASET_DIR"
ENV_MODE = "BTC_TS_MODE"  # OFF/DEBUG/BOOST 等（未設定でも動作させる）


def default_data_dir() -> Path:
    return repo_root() / "data"


def default_logs_dir() -> Path:
    return repo_root() / "logs"


def default_config_dir() -> Path:
    return repo_root() / "config" / "ui"


def default_secrets_dir() -> Path:
    return repo_root() / "secrets"


def default_dataset_dir() -> Path:
    return repo_root() / "dataset"


def mode() -> str:
    return (env_str(ENV_MODE, "OFF") or "OFF").upper()
