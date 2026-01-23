# path: ./btcts_next/src/btcts/settings/load_yaml.py
# desc: YAML settings loader (canonical). Prefers BTC_TS_CONFIG_DIR. UTF-8 read. Returns dict safely.

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

import yaml

from btcts.core import paths


@dataclass(frozen=True)
class LoadedYaml:
    name: str
    path: Optional[Path]
    data: Dict[str, Any]


def _config_root() -> Path:
    # 優先: BTC_TS_CONFIG_DIR（collector_test.ps1 などがここを差し替える）
    env = paths.config_dir()
    if isinstance(env, Path):
        return env

    # 念のため。paths.config_dir() が Path を返さない実装だった場合の保険
    return Path(str(env))


def _candidate_paths(name: str) -> Tuple[Path, ...]:
    root = _config_root()
    return (
        root / f"{name}.yaml",
        root / f"{name}.yml",
    )


def load_yaml(name: str) -> Dict[str, Any]:
    """
    設定YAMLを dict として返す。
    - 見つからない/壊れている/型がdictでない → {} を返す（上位で安全に扱える）
    - 読み取りはUTF-8（BOM許容）
    """
    loaded = load_yaml_with_path(name)
    return loaded.data


def load_yaml_with_path(name: str) -> LoadedYaml:
    for p in _candidate_paths(name):
        if not p.exists():
            continue
        try:
            text = p.read_text(encoding="utf-8-sig")
            obj = yaml.safe_load(text)
            if isinstance(obj, dict):
                return LoadedYaml(name=name, path=p, data=obj)
            return LoadedYaml(name=name, path=p, data={})
        except Exception:
            return LoadedYaml(name=name, path=p, data={})

    return LoadedYaml(name=name, path=None, data={})
