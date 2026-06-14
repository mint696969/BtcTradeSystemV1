# path: ./btcts_next/src/btcts/autotrade/config/registry.py
# desc: Parameter-set registry serialization helpers.

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .models import ParameterSet, ParameterSetRegistry


def write_parameter_set(path: Path, parameter_set: ParameterSet) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(parameter_set.to_dict(), ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")


def write_registry(path: Path, registry: ParameterSetRegistry) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(registry.to_dict(), ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))
