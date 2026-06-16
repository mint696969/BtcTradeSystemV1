# path: ./btcts_next/src/btcts/autotrade/ledger/decision_log.py
# desc: Shadow decision ledger helpers for AutoTrade.

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Dict, Iterable

from btcts.autotrade.config.models import ParameterSetBundle
from btcts.autotrade.modes import AutoTradeMode
from btcts.autotrade.read_model.models import AutoTradeSnapshot, Forecast5m
from btcts.autotrade.risk.models import RiskGateResult
from btcts.autotrade.strategy.models import ActionCandidate


DECISION_RATIONALE_VERSION = "autotrade_decision_rationale.v1"


def _unique_values(*groups: Iterable[str]) -> tuple[str, ...]:
    values: list[str] = []
    seen: set[str] = set()
    for group in groups:
        for raw in group:
            value = str(raw or "").strip()
            if not value or value in seen:
                continue
            seen.add(value)
            values.append(value)
    return tuple(values)


def _default_regime_result(snapshot: AutoTradeSnapshot) -> Dict[str, Any]:
    ground = snapshot.ground.to_dict()
    return {
        "source": "snapshot.ground",
        "direction": ground["direction"],
        "confidence": ground["confidence"],
        "reason_codes": list(snapshot.ground.reason_codes),
    }


def _thresholds_from_bundle(bundle: ParameterSetBundle | None) -> Dict[str, Any]:
    if bundle is None:
        return {}
    trade = bundle.trade_parameter_set
    return {
        "regime": asdict(bundle.regime_parameter_set.thresholds),
        "trade": {
            "entry_quality": asdict(trade.entry_quality),
            "freshness": asdict(trade.freshness),
            "loss_limits": asdict(trade.loss_limits),
        },
    }


@dataclass(frozen=True)
class ShadowDecisionRecord:
    decision_id: str
    mode: AutoTradeMode
    snapshot: AutoTradeSnapshot
    forecast_5m: Forecast5m | None
    candidate: ActionCandidate
    risk_gate: RiskGateResult
    final_action: str
    parameter_bundle_id: str | None = None
    regime_parameter_set_id: str | None = None
    trade_parameter_set_id: str | None = None
    regime_result: Dict[str, Any] | None = None
    used_thresholds: Dict[str, Any] | None = None

    def to_dict(self) -> Dict[str, Any]:
        blocked_reasons = _unique_values(self.candidate.blocked_hint, self.risk_gate.blocked_by)
        triggered_rules = _unique_values(self.candidate.reason_codes, self.candidate.blocked_hint, self.risk_gate.blocked_by)
        trade_parameter_set_id = self.trade_parameter_set_id or self.candidate.parameter_set_id
        regime_result = self.regime_result or _default_regime_result(self.snapshot)
        used_thresholds = self.used_thresholds or {}

        return {
            "decision_id": self.decision_id,
            "decision_rationale_version": DECISION_RATIONALE_VERSION,
            "mode": self.mode.value,
            "snapshot_id": self.snapshot.snapshot_id,
            "forecast_id": self.forecast_5m.forecast_id if self.forecast_5m is not None else None,
            "parameter_set_id": self.candidate.parameter_set_id,
            "parameter_bundle_id": self.parameter_bundle_id,
            "regime_parameter_set_id": self.regime_parameter_set_id,
            "trade_parameter_set_id": trade_parameter_set_id,
            "logic_version": self.candidate.logic_version,
            "base_ground": self.snapshot.ground.to_dict(),
            "regime_result": regime_result,
            "forecast_5m": self.forecast_5m.to_dict() if self.forecast_5m is not None else None,
            "candidate": self.candidate.to_dict(),
            "risk_gate": self.risk_gate.to_dict(),
            "final_action": self.final_action,
            "trade_decision": {
                "final_action": self.final_action,
                "candidate_action": self.candidate.action.value,
                "side": self.candidate.side,
                "entry_quality": self.candidate.entry_quality,
                "strategy_profile": self.candidate.strategy_profile.value,
                "risk_allowed": self.risk_gate.allowed,
                "risk_executable": self.risk_gate.executable,
                "reason_codes": list(self.candidate.reason_codes),
                "blocked_reasons": list(blocked_reasons),
                "used_thresholds": used_thresholds.get("trade", {}),
            },
            "used_thresholds": used_thresholds,
            "triggered_rules": list(triggered_rules),
            "reason_codes": list(self.candidate.reason_codes),
            "blocked_by": list(self.risk_gate.blocked_by),
            "blocked_reasons": list(blocked_reasons),
            "would_order": None,
        }


def build_decision_id(snapshot_id: str, candidate_id: str) -> str:
    return f"dec_{snapshot_id.removeprefix('snap_')}_{candidate_id.removeprefix('cand_')[:24]}"


def build_shadow_decision_record(
    *,
    mode: AutoTradeMode,
    snapshot: AutoTradeSnapshot,
    forecast_5m: Forecast5m | None,
    candidate: ActionCandidate,
    risk_gate: RiskGateResult,
    parameter_bundle: ParameterSetBundle | None = None,
    regime_result: Dict[str, Any] | None = None,
    used_thresholds: Dict[str, Any] | None = None,
) -> ShadowDecisionRecord:
    final_action = candidate.action.value if risk_gate.allowed else "WAIT"
    thresholds = _thresholds_from_bundle(parameter_bundle)
    if used_thresholds:
        thresholds.update(used_thresholds)
    return ShadowDecisionRecord(
        decision_id=build_decision_id(snapshot.snapshot_id, candidate.candidate_id),
        mode=mode,
        snapshot=snapshot,
        forecast_5m=forecast_5m,
        candidate=candidate,
        risk_gate=risk_gate,
        final_action=final_action,
        parameter_bundle_id=parameter_bundle.parameter_bundle_id if parameter_bundle is not None else None,
        regime_parameter_set_id=parameter_bundle.regime_parameter_set_id if parameter_bundle is not None else None,
        trade_parameter_set_id=parameter_bundle.trade_parameter_set_id if parameter_bundle is not None else candidate.parameter_set_id,
        regime_result=regime_result or _default_regime_result(snapshot),
        used_thresholds=thresholds,
    )


def append_decision_jsonl(path: Path, record: ShadowDecisionRecord) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(record.to_dict(), ensure_ascii=False, sort_keys=True) + "\n")
