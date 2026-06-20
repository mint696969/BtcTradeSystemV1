# path: ./btcts_next/src/btcts/apps/operator_ui/components/prediction_warroom_supplemental_widget_registry_preflight.py
# desc: Preflight/schema validator for Prediction WarRoom supplemental widget registry bundles. Validation only; no rendering, file access, payload decode, Collector, AutoTrade, broker, mode, or append behavior.

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Iterable, Mapping, Tuple

from .prediction_warroom_explanation_widget_groups import EXPLANATION_WIDGET_GROUP_VERSION
from .prediction_warroom_latest_payload_dry_run_widget_groups import DRY_RUN_WIDGET_GROUP_VERSION
from .prediction_warroom_payload_schema_validator import (
    VALIDATOR_VERSION as BASE_PAYLOAD_VALIDATOR_VERSION,
    validate_prediction_warroom_payload_contract_bundle,
)
from .prediction_warroom_sample_packets import build_prediction_warroom_sample_display_packet
from .prediction_warroom_supplemental_widget_registry import (
    SUPPLEMENTAL_WIDGET_REGISTRY_VERSION,
    build_prediction_warroom_supplemental_widget_registry,
)
from .prediction_warroom_widget_groups import WIDGET_GROUP_PACKET_VERSION, build_prediction_warroom_widget_group_packet_index

SUPPLEMENTAL_WIDGET_REGISTRY_PREFLIGHT_VERSION = "prediction_warroom_supplemental_widget_registry_preflight.ps_q6g.v1"

_DANGEROUS_FALSE_FIELDS = (
    "actual_loader_execution_allowed",
    "actual_file_read_allowed_by_this_contract",
    "actual_payload_decode_allowed_by_this_contract",
    "would_load_hot_latest_artifacts",
    "would_read_runtime_file",
    "would_collect_public_source",
    "would_write_runtime_artifact",
    "would_write_collector_state",
    "would_send_to_broker",
    "broker_execution_requested",
    "mode_apply_requested",
    "command_ledger_append_requested",
    "approval_append_requested",
    "trigger_enabled",
    "autotrade_trigger_enabled",
)
_SAFE_TRUE_FIELDS = (
    "read_only",
    "non_executing",
    "display_only",
    "render_intent_only",
    "not_loaded_as_runtime_display_source",
)
_EXPECTED_ATTACH_POINTS = {
    "source_quality_explanation_widgets": "source_quality_widget",
    "prediction_latest_payload_dry_run_status_widget": "warning_refresh_widget",
}
_EXPECTED_INDEX_VERSIONS = {EXPLANATION_WIDGET_GROUP_VERSION, DRY_RUN_WIDGET_GROUP_VERSION}


@dataclass(frozen=True)
class PredictionWarRoomSupplementalWidgetRegistryPreflightIssue:
    issue_code: str
    severity: str
    path: str
    message_ja: str
    expected: Any = None
    actual: Any = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "issue_code": self.issue_code,
            "severity": self.severity,
            "path": self.path,
            "message_ja": self.message_ja,
            "expected": self.expected,
            "actual": self.actual,
        }


@dataclass(frozen=True)
class PredictionWarRoomSupplementalWidgetRegistryPreflightReport:
    report_version: str
    report_id: str
    preflight_state: str
    valid: bool
    schema_target: str
    base_payload_validator_version: str
    registry_version: str | None = None
    supplemental_index_count: int = 0
    supplemental_widget_group_count: int = 0
    auto_refresh_group_count: int = 0
    issue_count: int = 0
    blocker_count: int = 0
    warning_count: int = 0
    info_count: int = 0
    issues: Tuple[PredictionWarRoomSupplementalWidgetRegistryPreflightIssue, ...] = ()
    checked_sections: Tuple[str, ...] = ()
    checked_contracts: Tuple[str, ...] = ()
    summary_ja: str = ""
    boundaries: Mapping[str, Any] = field(default_factory=dict)
    read_only: bool = True
    non_executing: bool = True
    validator_only: bool = True
    preflight_only: bool = True
    display_only: bool = True
    render_intent_only: bool = True
    not_loaded_as_runtime_display_source: bool = True
    actual_loader_execution_allowed: bool = False
    actual_file_read_allowed_by_this_contract: bool = False
    actual_payload_decode_allowed_by_this_contract: bool = False
    would_load_hot_latest_artifacts: bool = False
    would_read_runtime_file: bool = False
    would_collect_public_source: bool = False
    would_write_runtime_artifact: bool = False
    would_write_collector_state: bool = False
    would_send_to_broker: bool = False
    broker_execution_requested: bool = False
    mode_apply_requested: bool = False
    command_ledger_append_requested: bool = False
    approval_append_requested: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return {
            "report_version": self.report_version,
            "report_id": self.report_id,
            "preflight_state": self.preflight_state,
            "valid": self.valid,
            "schema_target": self.schema_target,
            "base_payload_validator_version": self.base_payload_validator_version,
            "registry_version": self.registry_version,
            "supplemental_index_count": self.supplemental_index_count,
            "supplemental_widget_group_count": self.supplemental_widget_group_count,
            "auto_refresh_group_count": self.auto_refresh_group_count,
            "issue_count": self.issue_count,
            "blocker_count": self.blocker_count,
            "warning_count": self.warning_count,
            "info_count": self.info_count,
            "issues": [item.to_dict() for item in self.issues],
            "checked_sections": list(self.checked_sections),
            "checked_contracts": list(self.checked_contracts),
            "summary_ja": self.summary_ja,
            "boundaries": dict(self.boundaries),
            "read_only": self.read_only,
            "non_executing": self.non_executing,
            "validator_only": self.validator_only,
            "preflight_only": self.preflight_only,
            "display_only": self.display_only,
            "render_intent_only": self.render_intent_only,
            "not_loaded_as_runtime_display_source": self.not_loaded_as_runtime_display_source,
            "actual_loader_execution_allowed": self.actual_loader_execution_allowed,
            "actual_file_read_allowed_by_this_contract": self.actual_file_read_allowed_by_this_contract,
            "actual_payload_decode_allowed_by_this_contract": self.actual_payload_decode_allowed_by_this_contract,
            "would_load_hot_latest_artifacts": self.would_load_hot_latest_artifacts,
            "would_read_runtime_file": self.would_read_runtime_file,
            "would_collect_public_source": self.would_collect_public_source,
            "would_write_runtime_artifact": self.would_write_runtime_artifact,
            "would_write_collector_state": self.would_write_collector_state,
            "would_send_to_broker": self.would_send_to_broker,
            "broker_execution_requested": self.broker_execution_requested,
            "mode_apply_requested": self.mode_apply_requested,
            "command_ledger_append_requested": self.command_ledger_append_requested,
            "approval_append_requested": self.approval_append_requested,
        }


def _as_mapping(value: Any) -> Mapping[str, Any]:
    if hasattr(value, "to_dict"):
        converted = value.to_dict()
        return converted if isinstance(converted, Mapping) else {}
    return value if isinstance(value, Mapping) else {}


def _list(value: Any) -> list[Any]:
    return list(value) if isinstance(value, (list, tuple)) else []


def _issue(issue_code: str, severity: str, path: str, message_ja: str, *, expected: Any = None, actual: Any = None) -> PredictionWarRoomSupplementalWidgetRegistryPreflightIssue:
    return PredictionWarRoomSupplementalWidgetRegistryPreflightIssue(
        issue_code=issue_code,
        severity=severity,
        path=path,
        message_ja=message_ja,
        expected=expected,
        actual=actual,
    )


def _require_keys(payload: Mapping[str, Any], required: tuple[str, ...], prefix: str, issues: list[PredictionWarRoomSupplementalWidgetRegistryPreflightIssue]) -> None:
    for key in required:
        if key not in payload:
            issues.append(_issue("missing_required_key", "blocker", f"{prefix}.{key}", "必須キーがありません。", expected="present", actual="missing"))


def _require_list(payload: Mapping[str, Any], key: str, prefix: str, issues: list[PredictionWarRoomSupplementalWidgetRegistryPreflightIssue], *, allow_empty: bool = False) -> None:
    value = payload.get(key)
    if not isinstance(value, (list, tuple)):
        issues.append(_issue("expected_list", "blocker", f"{prefix}.{key}", "list/tupleが必要です。", expected="list", actual=type(value).__name__))
    elif not allow_empty and len(value) == 0:
        issues.append(_issue("empty_required_list", "warning", f"{prefix}.{key}", "空ではないlistが期待されます。", expected="non_empty", actual="empty"))


def _require_safe_flags(payload: Mapping[str, Any], prefix: str, issues: list[PredictionWarRoomSupplementalWidgetRegistryPreflightIssue], *, require_safe_true: bool = False) -> None:
    for key in _SAFE_TRUE_FIELDS:
        if key in payload:
            if payload.get(key) is not True:
                issues.append(_issue("unsafe_true_flag", "blocker", f"{prefix}.{key}", "安全系フラグがTrueではありません。", expected=True, actual=payload.get(key)))
        elif require_safe_true:
            issues.append(_issue("missing_safe_flag", "warning", f"{prefix}.{key}", "安全系フラグが明示されていません。", expected=True, actual="missing"))
    for key in _DANGEROUS_FALSE_FIELDS:
        if key in payload and payload.get(key) is not False:
            issues.append(_issue("dangerous_flag_enabled", "blocker", f"{prefix}.{key}", "危険系フラグがFalseではありません。", expected=False, actual=payload.get(key)))


def _finish(
    *,
    registry: Mapping[str, Any],
    issues: list[PredictionWarRoomSupplementalWidgetRegistryPreflightIssue],
    checked_sections: tuple[str, ...],
    checked_contracts: tuple[str, ...],
) -> PredictionWarRoomSupplementalWidgetRegistryPreflightReport:
    blocker_count = sum(1 for item in issues if item.severity == "blocker")
    warning_count = sum(1 for item in issues if item.severity == "warning")
    info_count = sum(1 for item in issues if item.severity == "info")
    valid = blocker_count == 0
    preflight_state = "ready_for_warroom_supplemental_handoff" if valid else "blocked_before_warroom_supplemental_handoff"
    summary_ja = "supplemental registry preflight valid" if valid else f"supplemental registry blockers: {blocker_count}"
    if warning_count:
        summary_ja += f", warnings: {warning_count}"
    boundaries = {
        "read_only": True,
        "non_executing": True,
        "validator_only": True,
        "preflight_only": True,
        "display_only": True,
        "render_intent_only": True,
        "not_loaded_as_runtime_display_source": True,
        "actual_loader_execution_allowed": False,
        "actual_file_read_allowed_by_this_contract": False,
        "actual_payload_decode_allowed_by_this_contract": False,
        "would_load_hot_latest_artifacts": False,
        "would_read_runtime_file": False,
        "would_collect_public_source": False,
        "would_write_runtime_artifact": False,
        "would_write_collector_state": False,
        "would_send_to_broker": False,
        "broker_execution_requested": False,
        "mode_apply_requested": False,
        "command_ledger_append_requested": False,
        "approval_append_requested": False,
    }
    return PredictionWarRoomSupplementalWidgetRegistryPreflightReport(
        report_version=SUPPLEMENTAL_WIDGET_REGISTRY_PREFLIGHT_VERSION,
        report_id=f"{SUPPLEMENTAL_WIDGET_REGISTRY_PREFLIGHT_VERSION}:{registry.get('registry_id') or 'unknown'}",
        preflight_state=preflight_state,
        valid=valid,
        schema_target="supplemental_widget_registry",
        base_payload_validator_version=BASE_PAYLOAD_VALIDATOR_VERSION,
        registry_version=str(registry.get("registry_version")) if registry.get("registry_version") else None,
        supplemental_index_count=len(_list(registry.get("supplemental_indexes"))),
        supplemental_widget_group_count=len(_list(registry.get("widget_groups"))),
        auto_refresh_group_count=len(_list(registry.get("auto_refresh_groups"))),
        issue_count=len(issues),
        blocker_count=blocker_count,
        warning_count=warning_count,
        info_count=info_count,
        issues=tuple(issues),
        checked_sections=checked_sections,
        checked_contracts=checked_contracts,
        summary_ja=summary_ja,
        boundaries=boundaries,
    )


def _validate_attach_point(widget_group_id: str, attach_after: Any, path: str, issues: list[PredictionWarRoomSupplementalWidgetRegistryPreflightIssue]) -> None:
    expected = _EXPECTED_ATTACH_POINTS.get(widget_group_id)
    if expected and attach_after != expected:
        issues.append(_issue("unexpected_attach_after_widget_group_id", "blocker", path, "supplemental widgetの差し込み位置が期待と違います。", expected=expected, actual=attach_after))


def _validate_widget_group(group: Mapping[str, Any], idx: int, issues: list[PredictionWarRoomSupplementalWidgetRegistryPreflightIssue]) -> None:
    prefix = f"supplemental_registry.widget_groups[{idx}]"
    _require_keys(group, ("packet_version", "widget_group_id", "refresh_group_id", "payload"), prefix, issues)
    _require_safe_flags(group, prefix, issues)
    widget_group_id = str(group.get("widget_group_id") or "")
    if group.get("packet_version") not in _EXPECTED_INDEX_VERSIONS:
        issues.append(_issue("unexpected_widget_packet_version", "blocker", f"{prefix}.packet_version", "supplemental widget packet versionが未対応です。", expected=sorted(_EXPECTED_INDEX_VERSIONS), actual=group.get("packet_version")))
    _validate_attach_point(widget_group_id, group.get("attach_after_widget_group_id"), f"{prefix}.attach_after_widget_group_id", issues)
    payload = _as_mapping(group.get("payload"))
    _require_safe_flags(payload, f"{prefix}.payload", issues)
    _validate_attach_point(widget_group_id, payload.get("attach_after_widget_group_id"), f"{prefix}.payload.attach_after_widget_group_id", issues)
    if not widget_group_id:
        issues.append(_issue("missing_widget_group_id", "blocker", f"{prefix}.widget_group_id", "widget_group_idが必要です。", expected="non_empty", actual=widget_group_id))


def _validate_auto_refresh_group(group: Mapping[str, Any], idx: int, issues: list[PredictionWarRoomSupplementalWidgetRegistryPreflightIssue]) -> None:
    prefix = f"supplemental_registry.auto_refresh_groups[{idx}]"
    _require_keys(group, ("widget_group_id", "refresh_group_id", "refresh_interval_sec", "refresh_priority"), prefix, issues)
    _require_safe_flags(group, prefix, issues)
    widget_group_id = str(group.get("widget_group_id") or "")
    _validate_attach_point(widget_group_id, group.get("attach_after_widget_group_id"), f"{prefix}.attach_after_widget_group_id", issues)
    interval = group.get("refresh_interval_sec")
    priority = group.get("refresh_priority")
    if not isinstance(interval, int) or interval <= 0:
        issues.append(_issue("invalid_refresh_interval", "blocker", f"{prefix}.refresh_interval_sec", "refresh intervalは正のintです。", expected="positive int", actual=interval))
    if not isinstance(priority, int):
        issues.append(_issue("invalid_refresh_priority", "blocker", f"{prefix}.refresh_priority", "refresh priorityはintです。", expected="int", actual=priority))


def _validate_supplemental_index(index: Mapping[str, Any], idx: int, issues: list[PredictionWarRoomSupplementalWidgetRegistryPreflightIssue]) -> None:
    prefix = f"supplemental_registry.supplemental_indexes[{idx}]"
    _require_keys(index, ("index_version", "source_kind", "widget_groups", "auto_refresh_groups", "attach_after_widget_group_id"), prefix, issues)
    _require_safe_flags(index, prefix, issues)
    if index.get("index_version") not in _EXPECTED_INDEX_VERSIONS:
        issues.append(_issue("unexpected_supplemental_index_version", "blocker", f"{prefix}.index_version", "supplemental index versionが未対応です。", expected=sorted(_EXPECTED_INDEX_VERSIONS), actual=index.get("index_version")))
    _require_list(index, "widget_groups", prefix, issues)
    _require_list(index, "auto_refresh_groups", prefix, issues)


def validate_prediction_warroom_supplemental_widget_registry_schema(
    registry_packet: Mapping[str, Any] | Any,
) -> PredictionWarRoomSupplementalWidgetRegistryPreflightReport:
    """Validate a Q6F supplemental widget registry without rendering, file reads, or runtime side effects."""
    registry = _as_mapping(registry_packet)
    issues: list[PredictionWarRoomSupplementalWidgetRegistryPreflightIssue] = []
    prefix = "supplemental_registry"
    _require_keys(
        registry,
        (
            "registry_version",
            "registry_kind",
            "base_widget_group_contract",
            "supplemental_index_count",
            "supplemental_widget_group_count",
            "supplemental_widget_group_order",
            "supplemental_indexes",
            "auto_refresh_groups",
            "widget_groups",
            "integration_contract",
            "boundaries",
        ),
        prefix,
        issues,
    )
    if registry.get("registry_version") != SUPPLEMENTAL_WIDGET_REGISTRY_VERSION:
        issues.append(_issue("unexpected_registry_version", "blocker", f"{prefix}.registry_version", "registry versionが一致しません。", expected=SUPPLEMENTAL_WIDGET_REGISTRY_VERSION, actual=registry.get("registry_version")))
    if registry.get("base_widget_group_contract") != WIDGET_GROUP_PACKET_VERSION:
        issues.append(_issue("unexpected_base_widget_group_contract", "blocker", f"{prefix}.base_widget_group_contract", "base widget group contractが一致しません。", expected=WIDGET_GROUP_PACKET_VERSION, actual=registry.get("base_widget_group_contract")))
    _require_list(registry, "supplemental_indexes", prefix, issues)
    _require_list(registry, "widget_groups", prefix, issues)
    _require_list(registry, "auto_refresh_groups", prefix, issues)
    _require_list(registry, "supplemental_widget_group_order", prefix, issues)
    _require_safe_flags(registry, prefix, issues, require_safe_true=True)
    _require_safe_flags(_as_mapping(registry.get("boundaries")), f"{prefix}.boundaries", issues, require_safe_true=True)
    supplemental_indexes = [_as_mapping(item) for item in _list(registry.get("supplemental_indexes"))]
    widget_groups = [_as_mapping(item) for item in _list(registry.get("widget_groups"))]
    auto_refresh_groups = [_as_mapping(item) for item in _list(registry.get("auto_refresh_groups"))]
    order = [str(item) for item in _list(registry.get("supplemental_widget_group_order"))]
    if isinstance(registry.get("supplemental_index_count"), int) and registry.get("supplemental_index_count") != len(supplemental_indexes):
        issues.append(_issue("supplemental_index_count_mismatch", "blocker", f"{prefix}.supplemental_index_count", "supplemental index countが実体数と一致しません。", expected=len(supplemental_indexes), actual=registry.get("supplemental_index_count")))
    if isinstance(registry.get("supplemental_widget_group_count"), int) and registry.get("supplemental_widget_group_count") != len(widget_groups):
        issues.append(_issue("supplemental_widget_group_count_mismatch", "blocker", f"{prefix}.supplemental_widget_group_count", "supplemental widget group countが実体数と一致しません。", expected=len(widget_groups), actual=registry.get("supplemental_widget_group_count")))
    actual_order = [str(group.get("widget_group_id") or "") for group in widget_groups]
    if order != actual_order:
        issues.append(_issue("supplemental_widget_group_order_mismatch", "blocker", f"{prefix}.supplemental_widget_group_order", "supplemental widget group orderがwidget_groupsと一致しません。", expected=actual_order, actual=order))
    for idx, index in enumerate(supplemental_indexes):
        _validate_supplemental_index(index, idx, issues)
    for idx, group in enumerate(widget_groups):
        _validate_widget_group(group, idx, issues)
    for idx, group in enumerate(auto_refresh_groups):
        _validate_auto_refresh_group(group, idx, issues)
    integration = _as_mapping(registry.get("integration_contract"))
    _require_keys(integration, ("contract_version", "base_widget_group_contract", "integration_kind", "does_not_modify_base_q4b_group_order"), f"{prefix}.integration_contract", issues)
    _require_safe_flags(integration, f"{prefix}.integration_contract", issues)
    if integration.get("contract_version") != SUPPLEMENTAL_WIDGET_REGISTRY_VERSION:
        issues.append(_issue("unexpected_integration_contract_version", "blocker", f"{prefix}.integration_contract.contract_version", "integration contract versionが一致しません。", expected=SUPPLEMENTAL_WIDGET_REGISTRY_VERSION, actual=integration.get("contract_version")))
    if integration.get("does_not_modify_base_q4b_group_order") is not True:
        issues.append(_issue("base_group_order_mutation_allowed", "blocker", f"{prefix}.integration_contract.does_not_modify_base_q4b_group_order", "base Q4B順序を変更しない保証がありません。", expected=True, actual=integration.get("does_not_modify_base_q4b_group_order")))
    for key in ("requires_runtime_loader", "requires_hot_file_read", "requires_payload_decode", "requires_streamlit_rendering", "actual_loader_execution_allowed", "actual_file_read_allowed_by_this_contract"):
        if integration.get(key) is not False:
            issues.append(_issue("unsafe_integration_contract_flag", "blocker", f"{prefix}.integration_contract.{key}", "integration contractの危険/未許可flagがFalseではありません。", expected=False, actual=integration.get(key)))
    return _finish(
        registry=registry,
        issues=issues,
        checked_sections=("registry", "supplemental_indexes", "widget_groups", "auto_refresh_groups", "integration_contract", "boundaries"),
        checked_contracts=(SUPPLEMENTAL_WIDGET_REGISTRY_VERSION, EXPLANATION_WIDGET_GROUP_VERSION, DRY_RUN_WIDGET_GROUP_VERSION, WIDGET_GROUP_PACKET_VERSION),
    )


def build_prediction_warroom_supplemental_widget_registry_preflight_report(
    *,
    display_packet: Mapping[str, Any] | Any | None = None,
    registry_packet: Mapping[str, Any] | Any | None = None,
    artifact_metadata_inputs: Iterable[Mapping[str, Any]] | None = None,
    hot_latest_root_hint: str = "D:\\btc_ts_hot",
) -> PredictionWarRoomSupplementalWidgetRegistryPreflightReport:
    """Build and validate a supplemental registry bundle using supplied packets or deterministic samples."""
    packet = _as_mapping(display_packet) or build_prediction_warroom_sample_display_packet()
    base_widget_index = build_prediction_warroom_widget_group_packet_index(packet)
    base_report = validate_prediction_warroom_payload_contract_bundle(display_packet=packet, widget_group_index=base_widget_index)
    registry = _as_mapping(registry_packet) or build_prediction_warroom_supplemental_widget_registry(
        display_packet=packet,
        artifact_metadata_inputs=artifact_metadata_inputs,
        hot_latest_root_hint=hot_latest_root_hint,
    ).to_dict()
    registry_report = validate_prediction_warroom_supplemental_widget_registry_schema(registry)
    issues = list(registry_report.issues)
    for raw in _list(base_report.to_dict().get("issues")):
        item = _as_mapping(raw)
        issues.append(_issue(
            str(item.get("issue_code") or "base_payload_issue"),
            str(item.get("severity") or "blocker"),
            f"base_payload.{item.get('path') or 'unknown'}",
            str(item.get("message_ja") or "base payload validation issue"),
            expected=item.get("expected"),
            actual=item.get("actual"),
        ))
    return _finish(
        registry=registry,
        issues=issues,
        checked_sections=("base_display_packet", "base_q4b_widget_group_index", "supplemental_registry", "supplemental_widget_groups"),
        checked_contracts=(SUPPLEMENTAL_WIDGET_REGISTRY_VERSION, EXPLANATION_WIDGET_GROUP_VERSION, DRY_RUN_WIDGET_GROUP_VERSION, WIDGET_GROUP_PACKET_VERSION, BASE_PAYLOAD_VALIDATOR_VERSION),
    )
