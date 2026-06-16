# path: ./btcts_next/src/btcts/autotrade/config/bundle_runtime_loader.py
# desc: Read stored parameter bundle JSON and load active runtime bundle from registry.

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Tuple, TypeVar

from btcts.autotrade.config.bundle_lifecycle import parameter_bundle_json_path
from btcts.autotrade.config.bundle_runtime_store import (
    read_parameter_bundle_registry_or_default,
    runtime_parameter_bundle_root,
)
from btcts.autotrade.config.models import (
    AggressivenessProfile,
    AttackModePolicy,
    AutoManualPolicy,
    CancelRepricePolicy,
    CostModelPolicy,
    EntryQualityThresholds,
    ExposurePolicy,
    ForecastPolicy,
    FreshnessThresholds,
    LossLimits,
    MarginPolicy,
    ParameterSet,
    ParameterSetBundle,
    ParameterSetBundleRegistry,
    ParameterSetBundleStatus,
    ParameterSetStatus,
    ParticipationPolicy,
    ProductType,
    RegimeParameterSet,
    RegimeParameterSetStatus,
    RegimeThresholds,
    TemporalFlowPolicy,
)
from btcts.autotrade.config.registry import read_json
from btcts.autotrade.runtime_paths import parameter_registry_path

EnumT = TypeVar("EnumT")


@dataclass(frozen=True)
class ParameterBundleRuntimeLoadResult:
    registry: ParameterSetBundleRegistry
    stage: str | None
    bundle_id: str | None
    bundle: ParameterSetBundle | None
    registry_path: Path
    bundle_path: Path | None
    found: bool
    blocked_by: Tuple[str, ...]
    warnings: Tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            "ok": self.found and not self.blocked_by,
            "schema_version": "autotrade_parameter_bundle_runtime_load.v1",
            "stage": self.stage,
            "bundle_id": self.bundle_id,
            "registry_path": str(self.registry_path),
            "bundle_path": str(self.bundle_path) if self.bundle_path is not None else None,
            "found": self.found,
            "registry": self.registry.to_dict(),
            "bundle": self.bundle.to_dict() if self.bundle is not None else None,
            "blocked_by": list(self.blocked_by),
            "warnings": list(self.warnings),
            "would_send_to_broker": False,
        }


def _enum(enum_cls: type[EnumT], value: Any) -> EnumT:
    if isinstance(value, enum_cls):
        return value
    return enum_cls(str(value))


def regime_parameter_set_from_dict(data: dict[str, Any]) -> RegimeParameterSet:
    payload = dict(data)
    payload.pop("kind", None)
    thresholds = payload.get("thresholds") or {}
    return RegimeParameterSet(
        regime_parameter_set_id=str(payload["regime_parameter_set_id"]),
        parent_regime_parameter_set_id=payload.get("parent_regime_parameter_set_id"),
        status=_enum(RegimeParameterSetStatus, payload["status"]),
        product_type=_enum(ProductType, payload["product_type"]),
        exchange=str(payload["exchange"]),
        symbol=str(payload["symbol"]),
        created_at=str(payload["created_at"]),
        created_by=str(payload["created_by"]),
        change_reason=str(payload["change_reason"]),
        logic_version=str(payload["logic_version"]),
        thresholds=RegimeThresholds(**thresholds),
        notes=str(payload.get("notes") or ""),
    )


def parameter_set_from_dict(data: dict[str, Any]) -> ParameterSet:
    payload = dict(data)
    payload.pop("kind", None)
    return ParameterSet(
        parameter_set_id=str(payload["parameter_set_id"]),
        parent_parameter_set_id=payload.get("parent_parameter_set_id"),
        status=_enum(ParameterSetStatus, payload["status"]),
        product_type=_enum(ProductType, payload["product_type"]),
        exchange=str(payload["exchange"]),
        symbol=str(payload["symbol"]),
        created_at=str(payload["created_at"]),
        created_by=str(payload["created_by"]),
        change_reason=str(payload["change_reason"]),
        logic_version=str(payload["logic_version"]),
        aggressiveness=_enum(AggressivenessProfile, payload.get("aggressiveness", AggressivenessProfile.BALANCED.value)),
        margin_policy=MarginPolicy(**dict(payload.get("margin_policy") or {})),
        exposure_policy=ExposurePolicy(**dict(payload.get("exposure_policy") or {})),
        loss_limits=LossLimits(**dict(payload.get("loss_limits") or {})),
        freshness=FreshnessThresholds(**dict(payload.get("freshness") or {})),
        entry_quality=EntryQualityThresholds(**dict(payload.get("entry_quality") or {})),
        participation=ParticipationPolicy(**dict(payload.get("participation") or {})),
        forecast=ForecastPolicy(**dict(payload.get("forecast") or {})),
        temporal_flow=TemporalFlowPolicy(**dict(payload.get("temporal_flow") or {})),
        cancel_reprice=CancelRepricePolicy(**dict(payload.get("cancel_reprice") or {})),
        attack_mode=AttackModePolicy(**dict(payload.get("attack_mode") or {})),
        cost_model=CostModelPolicy(**dict(payload.get("cost_model") or {})),
        auto_manual=AutoManualPolicy(**dict(payload.get("auto_manual") or {})),
        notes=str(payload.get("notes") or ""),
    )


def parameter_set_bundle_from_dict(data: dict[str, Any]) -> ParameterSetBundle:
    payload = dict(data)
    return ParameterSetBundle(
        parameter_bundle_id=str(payload["parameter_bundle_id"]),
        parent_parameter_bundle_id=payload.get("parent_parameter_bundle_id"),
        status=_enum(ParameterSetBundleStatus, payload["status"]),
        regime_parameter_set=regime_parameter_set_from_dict(dict(payload["regime_parameter_set"])),
        trade_parameter_set=parameter_set_from_dict(dict(payload["trade_parameter_set"])),
        created_at=str(payload["created_at"]),
        created_by=str(payload["created_by"]),
        change_reason=str(payload["change_reason"]),
        market_uid=str(payload["market_uid"]),
        product_code=str(payload["product_code"]),
        logic_version=str(payload["logic_version"]),
        notes=str(payload.get("notes") or ""),
    )


def read_parameter_set_bundle(path: Path) -> ParameterSetBundle:
    return parameter_set_bundle_from_dict(read_json(path))


def _bundle_id_for_stage(registry: ParameterSetBundleRegistry, stage: str) -> str | None:
    normalized = str(stage).strip().lower()
    if normalized == "shadow":
        return registry.active_shadow_bundle_id
    if normalized == "paper":
        return registry.active_paper_bundle_id
    if normalized == "live":
        return registry.active_live_bundle_id
    if normalized == "rollback":
        return registry.rollback_bundle_id
    if normalized == "last_known_good":
        return registry.last_known_good_bundle_id
    if normalized == "pending_draft":
        return registry.pending_draft_bundle_id
    raise ValueError(f"stage must be shadow, paper, live, rollback, last_known_good, or pending_draft: {stage!r}")


def load_parameter_bundle_runtime(
    *,
    registry_path: Path | None = None,
    stage: str = "shadow",
    bundle_id: str | None = None,
) -> ParameterBundleRuntimeLoadResult:
    resolved_registry_path = registry_path or parameter_registry_path(ensure=False)
    warnings: list[str] = []
    blocked: list[str] = []

    if not resolved_registry_path.exists():
        warnings.append("parameter_bundle_registry_missing")

    registry = read_parameter_bundle_registry_or_default(resolved_registry_path)
    resolved_bundle_id = bundle_id or _bundle_id_for_stage(registry, stage)

    if not resolved_bundle_id:
        blocked.append("parameter_bundle_id_missing_for_stage")
        return ParameterBundleRuntimeLoadResult(
            registry=registry,
            stage=stage,
            bundle_id=None,
            bundle=None,
            registry_path=resolved_registry_path,
            bundle_path=None,
            found=False,
            blocked_by=tuple(blocked),
            warnings=tuple(warnings),
        )

    bundle_path = parameter_bundle_json_path(runtime_parameter_bundle_root(resolved_registry_path), resolved_bundle_id)
    if not bundle_path.exists():
        blocked.append("parameter_bundle_file_missing")
        return ParameterBundleRuntimeLoadResult(
            registry=registry,
            stage=stage,
            bundle_id=resolved_bundle_id,
            bundle=None,
            registry_path=resolved_registry_path,
            bundle_path=bundle_path,
            found=False,
            blocked_by=tuple(blocked),
            warnings=tuple(warnings),
        )

    bundle = read_parameter_set_bundle(bundle_path)
    if bundle.parameter_bundle_id != resolved_bundle_id:
        blocked.append("parameter_bundle_id_mismatch")

    return ParameterBundleRuntimeLoadResult(
        registry=registry,
        stage=stage,
        bundle_id=resolved_bundle_id,
        bundle=bundle,
        registry_path=resolved_registry_path,
        bundle_path=bundle_path,
        found=not blocked,
        blocked_by=tuple(blocked),
        warnings=tuple(warnings),
    )
