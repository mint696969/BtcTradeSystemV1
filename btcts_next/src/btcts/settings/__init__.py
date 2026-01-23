# path: ./btcts_next/src/btcts/settings/__init__.py
# desc: settings の公開口（svc のみ公開）。UIやcollectorはここ経由で読む/保存する。

from __future__ import annotations

# load 系（I/O 専用）
from .load_yaml import (
    load_yaml,
    load_yaml_with_path,
    LoadedYaml,
)

# svc 系（意味解釈・操作）
from .svc import (
    SCHEMA_MAP,
    SettingRef,
    get_paths,
    reset_to_default,
    resolve,
    save_yaml,
)

__all__ = [
    # load
    "load_yaml",
    "load_yaml_with_path",
    "LoadedYaml",
    # svc
    "SCHEMA_MAP",
    "SettingRef",
    "get_paths",
    "reset_to_default",
    "resolve",
    "save_yaml",
]
