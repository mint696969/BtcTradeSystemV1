# path: ./btcts_next/src/btcts/prediction/market_regime/sources/json_io.py
# desc: Small root-bound read-only JSON helpers for market-regime source adapters.

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping

from ..source_snapshot import JsonSourceArtifact

DEFAULT_JSON_MAX_BYTES = 2_000_000


def resolve_under_root(root: str | Path, relative_path: str | Path) -> Path:
    root_path = Path(root).resolve(strict=False)
    candidate = Path(relative_path)
    if not candidate.is_absolute():
        candidate = root_path / candidate
    candidate = candidate.resolve(strict=False)
    try:
        candidate.relative_to(root_path)
    except ValueError as exc:
        raise ValueError(f"path escapes source root: {relative_path}") from exc
    return candidate


def relative_to_root(root: str | Path, path: str | Path) -> str:
    root_path = Path(root).resolve(strict=False)
    candidate = Path(path).resolve(strict=False)
    try:
        return candidate.relative_to(root_path).as_posix()
    except ValueError:
        return str(path).replace("\\", "/")


def read_json_artifact(root: str | Path, relative_path: str | Path, *, max_bytes: int = DEFAULT_JSON_MAX_BYTES) -> JsonSourceArtifact:
    rel = str(relative_path).replace("\\", "/")
    try:
        path = resolve_under_root(root, relative_path)
    except Exception as exc:
        return JsonSourceArtifact(relative_path=rel, exists=False, ok=False, error=str(exc))
    if not path.exists():
        return JsonSourceArtifact(relative_path=rel, exists=False, ok=False, error="missing")
    try:
        raw = path.read_bytes()
        truncated = len(raw) > max_bytes
        raw = raw[:max_bytes]
        text = raw.decode("utf-8-sig")
        data: Mapping[str, Any] = json.loads(text)
        if not isinstance(data, dict):
            return JsonSourceArtifact(relative_path=rel, exists=True, ok=False, bytes_read=len(raw), truncated=truncated, error="json_root_not_object")
        return JsonSourceArtifact(relative_path=rel, exists=True, ok=True, data=data, bytes_read=len(raw), truncated=truncated)
    except Exception as exc:
        return JsonSourceArtifact(relative_path=rel, exists=True, ok=False, error=str(exc))
