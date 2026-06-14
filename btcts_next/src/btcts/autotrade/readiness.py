# path: ./btcts_next/src/btcts/autotrade/readiness.py
# desc: Read-only AutoTrade live readiness preflight. No mode changes, no broker execution.

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Dict, Mapping, Tuple

from btcts.autotrade.health import AutoTradeRuntimeHealthSnapshot, build_autotrade_runtime_health_snapshot
from btcts.autotrade.modes import AutoTradeMode, DANGEROUS_MODES, is_transition_allowed, requires_human_confirmation
from btcts.collector_vnext.config import load_config


@dataclass(frozen=True)
class AutoTradeReadinessResult:
    current_mode: AutoTradeMode
    target_mode: AutoTradeMode
    ready: bool
    transition_allowed: bool
    human_confirmation_required: bool
    human_confirmed: bool
    allow_warnings: bool
    health: AutoTradeRuntimeHealthSnapshot
    blocked_by: Tuple[str, ...]
    warnings: Tuple[str, ...]
    sr_fx_live_readiness: Dict[str, Any] | None = None
    would_send_to_broker: bool = False
    read_only: bool = True
    mode_changed: bool = False

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["current_mode"] = self.current_mode.value
        data["target_mode"] = self.target_mode.value
        data["health"] = self.health.to_dict()
        return data


def _coerce_mode(value: AutoTradeMode | str) -> AutoTradeMode:
    if isinstance(value, AutoTradeMode):
        return value
    return AutoTradeMode(str(value))


def _default_sr_fx_live_contract_path() -> Path:
    cfg = load_config()
    return cfg.roots()["state"] / "private" / "bitflyer_fx_live_readiness_contract.json"


def _read_json(path: Path) -> Dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8-sig"))
    if not isinstance(data, dict):
        raise ValueError(f"JSON root must be object: {path}")
    return data


def _load_sr_fx_live_readiness_contract(path: Path | None = None) -> Dict[str, Any] | None:
    target = path or _default_sr_fx_live_contract_path()
    if not target.exists():
        return None
    payload = _read_json(target)
    contract = payload.get("live_readiness_contract") if isinstance(payload.get("live_readiness_contract"), dict) else payload
    return contract if isinstance(contract, dict) else None


def _sr_fx_contract_summary(contract: Mapping[str, Any] | None, *, source: str) -> Dict[str, Any]:
    if contract is None:
        return {
            "source": source,
            "present": False,
            "ready": False,
            "blocked_by": ["sr_fx_live_readiness_contract_missing"],
            "warnings": [],
            "would_send_to_broker": False,
            "read_only": True,
        }
    return {
        "source": source,
        "present": True,
        "ready": bool(contract.get("ready", False)),
        "product_code": contract.get("product_code"),
        "market_uid": contract.get("market_uid"),
        "private_state_known_and_fresh": bool(contract.get("private_state_known_and_fresh", False)),
        "account_clear_for_new_auto_entry": bool(contract.get("account_clear_for_new_auto_entry", False)),
        "reconciliation_ok": bool(contract.get("reconciliation_ok", False)),
        "preview_ok": bool(contract.get("preview_ok", False)),
        "bitflyer_order_send_enabled": bool(contract.get("bitflyer_order_send_enabled", False)),
        "autotrade_live_order_enabled": bool(contract.get("autotrade_live_order_enabled", False)),
        "order_sender_implemented": bool(contract.get("order_sender_implemented", False)),
        "blocked_by": list(contract.get("blocked_by") or ()),
        "warnings": list(contract.get("warnings") or ()),
        "would_send_to_broker": bool(contract.get("would_send_to_broker", False)),
        "read_only": bool(contract.get("read_only", True)),
        "contract_version": contract.get("contract_version"),
    }


def evaluate_autotrade_live_readiness(
    *,
    current_mode: AutoTradeMode | str,
    target_mode: AutoTradeMode | str,
    human_confirmed: bool = False,
    allow_warnings: bool = False,
    max_observer_run_age_sec: float = 120.0,
    max_lines: int | None = 1000,
    enforce_sr_fx_live_contract: bool = True,
    sr_fx_live_contract: Mapping[str, Any] | None = None,
    sr_fx_live_contract_path: Path | None = None,
) -> AutoTradeReadinessResult:
    current = _coerce_mode(current_mode)
    target = _coerce_mode(target_mode)
    health = build_autotrade_runtime_health_snapshot(
        max_observer_run_age_sec=max_observer_run_age_sec,
        max_lines=max_lines,
    )
    blocked: list[str] = []
    warnings: list[str] = list(health.warnings)

    transition_allowed = is_transition_allowed(current, target, human_confirmed=human_confirmed)
    confirmation_required = requires_human_confirmation(current, target)
    if not transition_allowed:
        blocked.append("mode_transition_not_allowed_or_unconfirmed")
    if confirmation_required and not human_confirmed:
        blocked.append("human_confirmation_required")

    if health.blocked_by:
        blocked.append("runtime_health_blocked")
        blocked.extend(health.blocked_by)
    if target in DANGEROUS_MODES and not health.runtime.live_ready:
        blocked.append("autotrade_runtime_not_live_ready")
    if target in DANGEROUS_MODES and not health.observer_run_fresh:
        blocked.append("observer_run_not_fresh_for_live_target")
    latest_observer_blocked_by = tuple(health.observer_runs.latest_blocked_by or ())
    if target in DANGEROUS_MODES and latest_observer_blocked_by:
        blocked.append("observer_run_latest_blocked_for_live_target")
        blocked.extend(latest_observer_blocked_by)

    sr_fx_summary: Dict[str, Any] | None = None
    if enforce_sr_fx_live_contract and target in DANGEROUS_MODES:
        if sr_fx_live_contract is None:
            try:
                sr_fx_live_contract = _load_sr_fx_live_readiness_contract(sr_fx_live_contract_path)
                sr_fx_source = str(sr_fx_live_contract_path or _default_sr_fx_live_contract_path())
            except Exception as exc:
                sr_fx_live_contract = None
                sr_fx_source = f"load_error:{exc}"
        else:
            sr_fx_source = "provided"
        sr_fx_summary = _sr_fx_contract_summary(sr_fx_live_contract, source=sr_fx_source)
        if not sr_fx_summary.get("present"):
            blocked.append("sr_fx_live_readiness_contract_missing")
        if not sr_fx_summary.get("ready"):
            blocked.append("sr_fx_live_readiness_not_ready")
            blocked.extend(str(x) for x in sr_fx_summary.get("blocked_by") or ())
        if sr_fx_summary.get("would_send_to_broker"):
            blocked.append("sr_fx_live_readiness_attempted_broker_send")
        warnings.extend(str(x) for x in sr_fx_summary.get("warnings") or ())

    if health.warnings and not allow_warnings:
        blocked.append("runtime_health_warnings_present")

    blocked_tuple = tuple(dict.fromkeys(blocked))
    warnings_tuple = tuple(dict.fromkeys(warnings))
    return AutoTradeReadinessResult(
        current_mode=current,
        target_mode=target,
        ready=not blocked_tuple,
        transition_allowed=transition_allowed,
        human_confirmation_required=confirmation_required,
        human_confirmed=bool(human_confirmed),
        allow_warnings=bool(allow_warnings),
        health=health,
        blocked_by=blocked_tuple,
        warnings=warnings_tuple,
        sr_fx_live_readiness=sr_fx_summary,
        would_send_to_broker=False,
        read_only=True,
        mode_changed=False,
    )
