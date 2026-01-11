# path: ./btcts_next/src/btcts/core/paths.py
# desc: パス解決の正。ENV優先＋btcts_next内フォールバック。必要ディレクトリは確実に作成する。

from __future__ import annotations

from pathlib import Path

from .env import (
    env_or_default,
    repo_root as _repo_root,
    ENV_CONFIG_DIR,
    ENV_DATASET_DIR,
    ENV_DATA_DIR,
    ENV_LOGS_DIR,
    ENV_SECRETS_DIR,
    default_config_dir,
    default_dataset_dir,
    default_data_dir,
    default_logs_dir,
    default_secrets_dir,
)


def _ensure_dir(p: Path) -> Path:
    p.mkdir(parents=True, exist_ok=True)
    return p


def data_dir(*, ensure: bool = True) -> Path:
    """Collector の RAW 出力ルート。"""
    p = env_or_default(ENV_DATA_DIR, str(default_data_dir()))
    return _ensure_dir(p) if ensure else p


def logs_dir(*, ensure: bool = True) -> Path:
    """ログ出力ルート（audit.jsonl 等）。"""
    p = env_or_default(ENV_LOGS_DIR, str(default_logs_dir()))
    return _ensure_dir(p) if ensure else p


def config_dir(*, ensure: bool = True) -> Path:
    """UI設定(current)のルート。"""
    p = env_or_default(ENV_CONFIG_DIR, str(default_config_dir()))
    return _ensure_dir(p) if ensure else p


def secrets_dir(*, ensure: bool = True) -> Path:
    """secrets（機微）配置ルート。"""
    p = env_or_default(ENV_SECRETS_DIR, str(default_secrets_dir()))
    return _ensure_dir(p) if ensure else p


def dataset_dir(*, ensure: bool = True) -> Path:
    """学習・推論向けデータセットのルート。"""
    p = env_or_default(ENV_DATASET_DIR, str(default_dataset_dir()))
    return _ensure_dir(p) if ensure else p


# ---- config: schema/defaults -------------------------------------------------


def repo_root() -> Path:
    """btcts_next ルート。"""
    return _repo_root()


def schema_dir(*, ensure: bool = True) -> Path:
    """設定スキーマ（*_def.yaml など）の格納場所。"""
    p = repo_root() / "config" / "schema"
    return _ensure_dir(p) if ensure else p


def defaults_dir(*, ensure: bool = True) -> Path:
    """配布用デフォルト（将来用）。通常運用は schema + current 差分で成立する。"""
    p = repo_root() / "config" / "defaults"
    return _ensure_dir(p) if ensure else p


# ---- helpers -----------------------------------------------------------------


def ui_yaml_path(name: str) -> Path:
    """config_dir() 配下の <name>.yaml を返す（current）。"""
    n = (name or "").strip()
    if not n:
        raise ValueError("name is empty")
    if n.endswith(".yaml"):
        n = n[:-5]
    return config_dir() / f"{n}.yaml"


def schema_yaml_path(name: str) -> Path:
    """schema_dir() 配下の <name>.yaml を返す。"""
    n = (name or "").strip()
    if not n:
        raise ValueError("name is empty")
    if n.endswith(".yaml"):
        n = n[:-5]
    return schema_dir() / f"{n}.yaml"


def health_paths() -> dict:
    """Healthが参照する主要パスまとめ（表示/監査用・副作用なし）。"""
    return {
        "data_dir": str(data_dir(ensure=False)),
        "logs_dir": str(logs_dir(ensure=False)),
        "config_dir": str(config_dir(ensure=False)),
        "secrets_dir": str(secrets_dir(ensure=False)),
        "dataset_dir": str(dataset_dir(ensure=False)),
        "schema_dir": str(schema_dir(ensure=False)),
        "defaults_dir": str(defaults_dir(ensure=False)),
    }
