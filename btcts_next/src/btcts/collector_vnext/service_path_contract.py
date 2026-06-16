# path: ./btcts_next/src/btcts/collector_vnext/service_path_contract.py
# desc: Read-only SR-FX hot/cold/service path contract diagnostics.

from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Dict, Tuple

from btcts.autotrade.runtime_paths import autotrade_runtime_path_diagnostics
from btcts.collector_vnext.config import load_config
from btcts.core import paths as core_paths

STATE_TYPE = "market.overview"


@dataclass(frozen=True)
class SrFxServicePathContract:
    collector_data_root: Path
    collector_logs_root: Path
    collector_state_root: Path
    core_runtime_root: Path
    autotrade_runtime_root: Path
    autotrade_decision_ledger_dir: Path
    execution_exchange: str
    execution_product_code: str
    execution_market_uid: str
    execution_market_state_dir: Path
    execution_market_state_state_type: str
    service_readable_market_state_root: Path
    hot_runtime_detected: bool
    cold_core_runtime_detected: bool
    blocked_by: Tuple[str, ...]
    warnings: Tuple[str, ...]
    read_only: bool = True
    would_send_to_broker: bool = False

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        for key, value in list(data.items()):
            if isinstance(value, Path):
                data[key] = str(value)
        data["blocked_by"] = list(self.blocked_by)
        data["warnings"] = list(self.warnings)
        return data


def _is_cold_like(path: Path) -> bool:
    name = path.name.lower()
    return name in {"btc_ts", "btc_ts_archive", "btc_ts_cold"} or name.endswith("_cold") or name.endswith("_archive")


def build_sr_fx_service_path_contract() -> SrFxServicePathContract:
    cfg = load_config()
    exe = cfg.execution_market.normalized()
    runtime_diag = autotrade_runtime_path_diagnostics()
    service_root = core_paths.data_dir(ensure=False) / "market_state"
    execution_dir = (
        service_root
        / f"exchange={exe.exchange}"
        / f"symbol={exe.product_code}"
        / f"type={STATE_TYPE}"
    )

    blocked: list[str] = []
    warnings: list[str] = list(runtime_diag.warnings)

    if runtime_diag.blocked_by:
        blocked.extend(runtime_diag.blocked_by)
    if not runtime_diag.hot_runtime_detected:
        blocked.append("autotrade_hot_runtime_not_detected")
    if _is_cold_like(runtime_diag.paths.core_runtime_root):
        warnings.append("core_runtime_root_is_cold_or_service_root")
    if cfg.data_root.parent != runtime_diag.paths.core_runtime_root:
        warnings.append("collector_data_root_parent_differs_from_core_runtime_root")
    if cfg.data_root.parent == runtime_diag.paths.runtime_root:
        warnings.append("collector_data_root_points_to_autotrade_hot_runtime")

    return SrFxServicePathContract(
        collector_data_root=cfg.data_root,
        collector_logs_root=cfg.logs_root,
        collector_state_root=cfg.state_root,
        core_runtime_root=runtime_diag.paths.core_runtime_root,
        autotrade_runtime_root=runtime_diag.paths.runtime_root,
        autotrade_decision_ledger_dir=runtime_diag.paths.decision_ledger_dir,
        execution_exchange=exe.exchange,
        execution_product_code=exe.product_code,
        execution_market_uid=exe.market_uid,
        execution_market_state_dir=execution_dir,
        execution_market_state_state_type=STATE_TYPE,
        service_readable_market_state_root=service_root,
        hot_runtime_detected=runtime_diag.hot_runtime_detected,
        cold_core_runtime_detected=_is_cold_like(runtime_diag.paths.core_runtime_root),
        blocked_by=tuple(dict.fromkeys(blocked)),
        warnings=tuple(dict.fromkeys(warnings)),
        read_only=True,
        would_send_to_broker=False,
    )
