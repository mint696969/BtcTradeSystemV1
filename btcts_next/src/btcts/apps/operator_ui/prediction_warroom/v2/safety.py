# path: ./btcts_next/src/btcts/apps/operator_ui/prediction_warroom/v2/safety.py
# desc: Shared read-only/display-only safety flags for WarRoom v2 widget contracts.

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any


@dataclass(frozen=True)
class WidgetSafetyFlags:
    read_only: bool = True
    display_only: bool = True
    non_executing: bool = True
    runtime_artifact_write_allowed: bool = False
    status_artifact_write_allowed: bool = False
    prediction_artifact_write_allowed: bool = False
    view_artifact_write_allowed: bool = False
    scheduler_enabled: bool = False
    producer_enabled: bool = False
    autotrade_trigger_allowed: bool = False
    broker_private_api_allowed: bool = False
    ledger_append_allowed: bool = False
    mode_apply_allowed: bool = False
    parameter_apply_allowed: bool = False
    would_send_to_broker: bool = False

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def warroom_v2_safety_flags() -> dict[str, Any]:
    return WidgetSafetyFlags().to_dict()
