# path: ./btcts_next/src/btcts/autotrade/ledger/decision_log.py
# desc: Shadow decision ledger helpers for AutoTrade.

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict

from btcts.autotrade.modes import AutoTradeMode
from btcts.autotrade.read_model.models import AutoTradeSnapshot, Forecast5m
from btcts.autotrade.risk.models import RiskGateResult
from btcts.autotrade.strategy.models import ActionCandidate


@dataclass(frozen=True)
class ShadowDecisionRecord:
    decision_id: str
    mode: AutoTradeMode
    snapshot: AutoTradeSnapshot
    forecast_5m: Forecast5m | None
    candidate: ActionCandidate
    risk_gate: RiskGateResult
    final_action: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "decision_id": self.decision_id,
            "mode": self.mode.value,
            "snapshot_id": self.snapshot.snapshot_id,
            "forecast_id": self.forecast_5m.forecast_id if self.forecast_5m is not None else None,
            "parameter_set_id": self.candidate.parameter_set_id,
            "logic_version": self.candidate.logic_version,
            "base_ground": self.snapshot.ground.to_dict(),
            "forecast_5m": self.forecast_5m.to_dict() if self.forecast_5m is not None else None,
            "candidate": self.candidate.to_dict(),
            "risk_gate": self.risk_gate.to_dict(),
            "final_action": self.final_action,
            "reason_codes": list(self.candidate.reason_codes),
            "blocked_by": list(self.risk_gate.blocked_by),
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
) -> ShadowDecisionRecord:
    final_action = candidate.action.value if risk_gate.allowed else "WAIT"
    return ShadowDecisionRecord(
        decision_id=build_decision_id(snapshot.snapshot_id, candidate.candidate_id),
        mode=mode,
        snapshot=snapshot,
        forecast_5m=forecast_5m,
        candidate=candidate,
        risk_gate=risk_gate,
        final_action=final_action,
    )


def append_decision_jsonl(path: Path, record: ShadowDecisionRecord) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(record.to_dict(), ensure_ascii=False, sort_keys=True) + "\n")
