# path: ./btcts_next/src/btcts/prediction/market_regime/parameter_set_registry.py
# desc: Pure parameter-set registry for market-regime engine. Active/candidate/shadow/deprecated/rollback metadata only; no live apply, filesystem write, scheduler, broker, or AutoTrade behavior.

from __future__ import annotations

from dataclasses import asdict, dataclass, field, replace
from typing import Any, Dict, Mapping, Tuple

from .parameter_set import MarketRegimeParameterSet, build_default_market_regime_parameter_set

MARKET_REGIME_PARAMETER_SET_REGISTRY_VERSION = "prediction.market_regime.parameter_set_registry.2026_07_08.v1"
MARKET_REGIME_DEFAULT_ACTIVE_PARAMETER_SET_ID = "market_regime_engine_parameter_set.v1"
_ALLOWED_STATES = ("active", "candidate", "shadow", "deprecated", "rollback")


@dataclass(frozen=True)
class MarketRegimeParameterSetRegistrySafety:
    read_only: bool = True
    immutable_parameter_sets: bool = True
    active_pointer_read_only: bool = True
    live_parameter_apply_allowed: bool = False
    candidate_auto_promotion_allowed: bool = False
    human_gate_required_for_active_change: bool = True
    scheduler_enabled: bool = False
    producer_enabled: bool = False
    broker_private_api_allowed: bool = False
    autotrade_trigger_allowed: bool = False
    ledger_append_allowed: bool = False
    would_send_to_broker: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class MarketRegimeParameterSetRegistryEntry:
    parameter_set: MarketRegimeParameterSet
    registry_state: str = "active"
    created_at_utc: str = "2026-07-08T00:00:00Z"
    activated_at_utc: str = ""
    deprecated_at_utc: str = ""
    parent_parameter_set_id: str = ""
    rollback_target_parameter_set_id: str = ""
    change_reason: str = "initial_default_active_parameter_set"
    human_gate_ref: str = ""
    evidence_ref: str = ""

    def __post_init__(self) -> None:
        if self.registry_state not in _ALLOWED_STATES:
            raise ValueError(f"unsupported registry_state: {self.registry_state}")

    @property
    def parameter_set_id(self) -> str:
        return self.parameter_set.parameter_set_id

    def with_state(self, registry_state: str, *, change_reason: str) -> "MarketRegimeParameterSetRegistryEntry":
        return replace(self, registry_state=registry_state, change_reason=change_reason)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "parameter_set_id": self.parameter_set_id,
            "registry_state": self.registry_state,
            "created_at_utc": self.created_at_utc,
            "activated_at_utc": self.activated_at_utc,
            "deprecated_at_utc": self.deprecated_at_utc,
            "parent_parameter_set_id": self.parent_parameter_set_id,
            "rollback_target_parameter_set_id": self.rollback_target_parameter_set_id,
            "change_reason": self.change_reason,
            "human_gate_ref": self.human_gate_ref,
            "evidence_ref": self.evidence_ref,
            "parameter_set": self.parameter_set.to_dict(),
        }


@dataclass(frozen=True)
class MarketRegimeParameterSetRegistry:
    registry_id: str = "market_regime_parameter_set_registry.v1"
    registry_version: str = MARKET_REGIME_PARAMETER_SET_REGISTRY_VERSION
    active_parameter_set_id: str = MARKET_REGIME_DEFAULT_ACTIVE_PARAMETER_SET_ID
    entries: Tuple[MarketRegimeParameterSetRegistryEntry, ...] = field(default_factory=tuple)
    rollback_parameter_set_id: str = ""
    safety: MarketRegimeParameterSetRegistrySafety = field(default_factory=MarketRegimeParameterSetRegistrySafety)

    def entry_by_id(self, parameter_set_id: str) -> MarketRegimeParameterSetRegistryEntry:
        for entry in self.entries:
            if entry.parameter_set_id == parameter_set_id:
                return entry
        raise KeyError(parameter_set_id)

    def active_entry(self) -> MarketRegimeParameterSetRegistryEntry:
        return self.entry_by_id(self.active_parameter_set_id)

    def active_parameter_set(self) -> MarketRegimeParameterSet:
        return self.active_entry().parameter_set

    def entries_by_state(self, state: str) -> Tuple[MarketRegimeParameterSetRegistryEntry, ...]:
        return tuple(entry for entry in self.entries if entry.registry_state == state)

    def with_candidate(self, parameter_set: MarketRegimeParameterSet, *, change_reason: str, evidence_ref: str = "") -> "MarketRegimeParameterSetRegistry":
        if any(entry.parameter_set_id == parameter_set.parameter_set_id for entry in self.entries):
            raise ValueError(f"duplicate parameter_set_id: {parameter_set.parameter_set_id}")
        entry = MarketRegimeParameterSetRegistryEntry(
            parameter_set=parameter_set,
            registry_state="candidate",
            parent_parameter_set_id=self.active_parameter_set_id,
            change_reason=change_reason,
            evidence_ref=evidence_ref,
        )
        return replace(self, entries=tuple(self.entries) + (entry,))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "registry_id": self.registry_id,
            "registry_version": self.registry_version,
            "active_parameter_set_id": self.active_parameter_set_id,
            "rollback_parameter_set_id": self.rollback_parameter_set_id,
            "entries": [entry.to_dict() for entry in self.entries],
            "states_present": sorted({entry.registry_state for entry in self.entries}),
            "safety": self.safety.to_dict(),
        }


def build_default_market_regime_parameter_set_registry() -> MarketRegimeParameterSetRegistry:
    active = build_default_market_regime_parameter_set().with_status("active", change_reason="registry_default_active")
    entry = MarketRegimeParameterSetRegistryEntry(
        parameter_set=active,
        registry_state="active",
        created_at_utc="2026-07-08T00:00:00Z",
        activated_at_utc="2026-07-08T00:00:00Z",
        change_reason="registry_default_active",
    )
    return MarketRegimeParameterSetRegistry(entries=(entry,), rollback_parameter_set_id=active.parameter_set_id)


def validate_market_regime_parameter_set_registry(registry: MarketRegimeParameterSetRegistry | Mapping[str, Any]) -> Dict[str, Any]:
    payload = registry.to_dict() if isinstance(registry, MarketRegimeParameterSetRegistry) else dict(registry)
    failures: list[str] = []
    entries = payload.get("entries")
    if not isinstance(entries, list) or not entries:
        failures.append("entries_missing_or_empty")
        entries = []
    ids = [str(entry.get("parameter_set_id")) for entry in entries if isinstance(entry, Mapping)]
    if len(ids) != len(set(ids)):
        failures.append("duplicate_parameter_set_id")
    active_id = str(payload.get("active_parameter_set_id") or "")
    if active_id not in ids:
        failures.append("active_parameter_set_id_not_found")
    active_entries = [entry for entry in entries if isinstance(entry, Mapping) and entry.get("registry_state") == "active"]
    if len(active_entries) != 1:
        failures.append("active_entry_count_not_one")
    safety = payload.get("safety") if isinstance(payload.get("safety"), Mapping) else {}
    for key in (
        "live_parameter_apply_allowed",
        "candidate_auto_promotion_allowed",
        "scheduler_enabled",
        "producer_enabled",
        "broker_private_api_allowed",
        "autotrade_trigger_allowed",
        "ledger_append_allowed",
        "would_send_to_broker",
    ):
        if safety.get(key) is not False:
            failures.append(f"safety_{key}_not_false")
    return {
        "ok": not failures,
        "registry_version": MARKET_REGIME_PARAMETER_SET_REGISTRY_VERSION,
        "failure_count": len(failures),
        "failures": failures,
        "entry_count": len(entries),
        "active_parameter_set_id": active_id,
    }
