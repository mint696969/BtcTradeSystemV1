# path: ./btcts_next/src/btcts/autotrade/runtime_paths.py
# desc: AutoTrade hot/cold runtime path contract. Lightweight path resolution only.

from __future__ import annotations

import os
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Dict, Tuple

from btcts.core import paths as core_paths

ENV_AUTOTRADE_RUNTIME_ROOT = "BTC_TS_AUTOTRADE_RUNTIME_ROOT"
DEFAULT_HOT_RUNTIME_ROOT = Path("D:/btc_ts_hot")
COLD_RUNTIME_NAMES = frozenset({"btc_ts", "btc_ts_archive", "btc_ts_cold"})
HOT_RUNTIME_NAMES = frozenset({"btc_ts_hot", "btc_ts_live", "btc_ts_runtime"})


@dataclass(frozen=True)
class AutoTradeRuntimePaths:
    runtime_root: Path
    source: str
    core_runtime_root: Path
    command_ledger_path: Path
    decision_ledger_dir: Path
    parameter_registry_path: Path
    parameter_sets_dir: Path
    diagnostics_dir: Path

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        for key, value in list(data.items()):
            if isinstance(value, Path):
                data[key] = str(value)
        return data


@dataclass(frozen=True)
class AutoTradeRuntimePathDiagnostics:
    paths: AutoTradeRuntimePaths
    expected_hot_runtime_root: Path
    live_ready: bool
    blocked_by: Tuple[str, ...]
    warnings: Tuple[str, ...]
    cold_runtime_detected: bool
    hot_runtime_detected: bool

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["paths"] = self.paths.to_dict()
        data["expected_hot_runtime_root"] = str(self.expected_hot_runtime_root)
        return data


def _normalize(value: str | Path) -> Path:
    return Path(os.path.expandvars(os.path.expanduser(str(value)))).resolve()


def _explicit_runtime_root() -> Path | None:
    value = os.environ.get(ENV_AUTOTRADE_RUNTIME_ROOT)
    if value and value.strip():
        return _normalize(value.strip())
    return None


def _is_cold_root(path: Path) -> bool:
    name = path.name.lower()
    return name in COLD_RUNTIME_NAMES or name.endswith("_cold") or name.endswith("_archive")


def _is_hot_root(path: Path) -> bool:
    name = path.name.lower()
    return name in HOT_RUNTIME_NAMES or name.endswith("_hot") or name.endswith("_live")


def resolve_autotrade_runtime_root(*, prefer_existing_hot: bool = True) -> tuple[Path, str, Path]:
    core_root = core_paths.runtime_root(ensure=False)
    explicit = _explicit_runtime_root()
    if explicit is not None:
        return explicit, "env:BTC_TS_AUTOTRADE_RUNTIME_ROOT", core_root
    if prefer_existing_hot and DEFAULT_HOT_RUNTIME_ROOT.exists():
        return DEFAULT_HOT_RUNTIME_ROOT.resolve(), "default_existing_hot:D:/btc_ts_hot", core_root
    if _is_cold_root(core_root):
        # Do not silently treat the cold/archive root as live-ready. Use the hot
        # default as the AutoTrade runtime target, even if it still needs to be
        # created or explicitly confirmed by deployment.
        return DEFAULT_HOT_RUNTIME_ROOT, "default_hot_due_cold_core_runtime:D:/btc_ts_hot", core_root
    return core_root, "core_paths.runtime_root", core_root


def autotrade_runtime_paths(*, ensure: bool = False) -> AutoTradeRuntimePaths:
    root, source, core_root = resolve_autotrade_runtime_root()
    if ensure:
        root.mkdir(parents=True, exist_ok=True)
    command_dir = root / "autotrade" / "commands"
    decision_dir = root / "autotrade" / "decisions"
    parameter_dir = root / "autotrade" / "parameter_sets"
    diagnostics_dir = root / "autotrade" / "diagnostics"
    if ensure:
        for path in (command_dir, decision_dir, parameter_dir / "sets", diagnostics_dir):
            path.mkdir(parents=True, exist_ok=True)
    return AutoTradeRuntimePaths(
        runtime_root=root,
        source=source,
        core_runtime_root=core_root,
        command_ledger_path=command_dir / "command_requests.jsonl",
        decision_ledger_dir=decision_dir,
        parameter_registry_path=parameter_dir / "registry.json",
        parameter_sets_dir=parameter_dir / "sets",
        diagnostics_dir=diagnostics_dir,
    )


def autotrade_runtime_path_diagnostics(*, expected_hot_runtime_root: str | Path = DEFAULT_HOT_RUNTIME_ROOT) -> AutoTradeRuntimePathDiagnostics:
    expected_hot = _normalize(expected_hot_runtime_root)
    paths = autotrade_runtime_paths(ensure=False)
    blocked: list[str] = []
    warnings: list[str] = []
    cold = _is_cold_root(paths.runtime_root)
    hot = _is_hot_root(paths.runtime_root)

    if cold:
        blocked.append("autotrade_runtime_points_to_cold_or_archive_root")
    if not hot:
        warnings.append("autotrade_runtime_root_not_named_hot")
    if _is_cold_root(paths.core_runtime_root):
        warnings.append("core_runtime_root_looks_cold_or_archive")
    if paths.runtime_root != expected_hot and os.environ.get(ENV_AUTOTRADE_RUNTIME_ROOT) is None:
        warnings.append("autotrade_runtime_root_differs_from_expected_hot_default")

    live_ready = not blocked and hot
    return AutoTradeRuntimePathDiagnostics(
        paths=paths,
        expected_hot_runtime_root=expected_hot,
        live_ready=live_ready,
        blocked_by=tuple(blocked),
        warnings=tuple(warnings),
        cold_runtime_detected=cold,
        hot_runtime_detected=hot,
    )


def command_ledger_path(*, ensure: bool = True) -> Path:
    return autotrade_runtime_paths(ensure=ensure).command_ledger_path


def parameter_registry_path(*, ensure: bool = True) -> Path:
    return autotrade_runtime_paths(ensure=ensure).parameter_registry_path


def parameter_sets_dir(*, ensure: bool = True) -> Path:
    return autotrade_runtime_paths(ensure=ensure).parameter_sets_dir

def decision_ledger_path(name: str = "shadow_decisions.jsonl", *, ensure: bool = True) -> Path:
    filename = (name or "shadow_decisions.jsonl").strip()
    if not filename.endswith(".jsonl"):
        filename = f"{filename}.jsonl"
    paths = autotrade_runtime_paths(ensure=ensure)
    if ensure:
        paths.decision_ledger_dir.mkdir(parents=True, exist_ok=True)
    return paths.decision_ledger_dir / filename
