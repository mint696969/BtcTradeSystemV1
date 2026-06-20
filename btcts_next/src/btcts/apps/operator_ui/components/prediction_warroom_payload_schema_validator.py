# path: ./btcts_next/src/btcts/apps/operator_ui/components/prediction_warroom_payload_schema_validator.py
# desc: Schema validator for Prediction WarRoom display/widget/explanation payloads. Pure validation only; no runtime reads, rendering, Collector, AutoTrade, broker, mode, or append behavior.

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Mapping, Tuple

VALIDATOR_VERSION = "prediction_warroom_payload_schema_validator.ps_q5c.v1"

DISPLAY_PACKET_VERSION = "prediction_warroom_display_packet.ps_q4a.v1"
WIDGET_GROUP_INDEX_VERSION = "prediction_warroom_widget_groups.ps_q4b.v1"
EXPLANATION_PANEL_VERSION = "prediction_warroom_source_quality_explanations.ps_q5a.v1"
EXPLANATION_WIDGET_GROUP_INDEX_VERSION = "prediction_warroom_explanation_widget_groups.ps_q5b.v1"

_DANGEROUS_FALSE_FIELDS = (
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


@dataclass(frozen=True)
class PredictionWarRoomPayloadSchemaIssue:
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
class PredictionWarRoomPayloadSchemaValidationReport:
    report_version: str
    schema_target: str
    valid: bool
    issue_count: int = 0
    blocker_count: int = 0
    warning_count: int = 0
    info_count: int = 0
    issues: Tuple[PredictionWarRoomPayloadSchemaIssue, ...] = ()
    summary_ja: str = ""
    read_only: bool = True
    non_executing: bool = True
    validator_only: bool = True
    display_only: bool = True
    render_intent_only: bool = True
    not_loaded_as_runtime_display_source: bool = True
    would_load_hot_latest_artifacts: bool = False
    would_read_runtime_file: bool = False
    would_collect_public_source: bool = False
    would_write_runtime_artifact: bool = False
    would_send_to_broker: bool = False
    broker_execution_requested: bool = False
    mode_apply_requested: bool = False
    command_ledger_append_requested: bool = False
    approval_append_requested: bool = False
    checked_sections: Tuple[str, ...] = ()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "report_version": self.report_version,
            "schema_target": self.schema_target,
            "valid": self.valid,
            "issue_count": self.issue_count,
            "blocker_count": self.blocker_count,
            "warning_count": self.warning_count,
            "info_count": self.info_count,
            "issues": [item.to_dict() for item in self.issues],
            "summary_ja": self.summary_ja,
            "read_only": self.read_only,
            "non_executing": self.non_executing,
            "validator_only": self.validator_only,
            "display_only": self.display_only,
            "render_intent_only": self.render_intent_only,
            "not_loaded_as_runtime_display_source": self.not_loaded_as_runtime_display_source,
            "would_load_hot_latest_artifacts": self.would_load_hot_latest_artifacts,
            "would_read_runtime_file": self.would_read_runtime_file,
            "would_collect_public_source": self.would_collect_public_source,
            "would_write_runtime_artifact": self.would_write_runtime_artifact,
            "would_send_to_broker": self.would_send_to_broker,
            "broker_execution_requested": self.broker_execution_requested,
            "mode_apply_requested": self.mode_apply_requested,
            "command_ledger_append_requested": self.command_ledger_append_requested,
            "approval_append_requested": self.approval_append_requested,
            "checked_sections": list(self.checked_sections),
        }


def _as_mapping(value: Any) -> Mapping[str, Any]:
    if hasattr(value, "to_dict"):
        converted = value.to_dict()
        return converted if isinstance(converted, Mapping) else {}
    return value if isinstance(value, Mapping) else {}


def _list(value: Any) -> list[Any]:
    return list(value) if isinstance(value, (list, tuple)) else []


def _issue(issue_code: str, severity: str, path: str, message_ja: str, *, expected: Any = None, actual: Any = None) -> PredictionWarRoomPayloadSchemaIssue:
    return PredictionWarRoomPayloadSchemaIssue(issue_code=issue_code, severity=severity, path=path, message_ja=message_ja, expected=expected, actual=actual)


def _finish(schema_target: str, issues: list[PredictionWarRoomPayloadSchemaIssue], checked_sections: tuple[str, ...]) -> PredictionWarRoomPayloadSchemaValidationReport:
    blocker_count = sum(1 for item in issues if item.severity == "blocker")
    warning_count = sum(1 for item in issues if item.severity == "warning")
    info_count = sum(1 for item in issues if item.severity == "info")
    valid = blocker_count == 0
    summary_ja = "schema valid" if valid else f"schema blockers: {blocker_count}"
    if warning_count:
        summary_ja += f", warnings: {warning_count}"
    return PredictionWarRoomPayloadSchemaValidationReport(
        report_version=VALIDATOR_VERSION,
        schema_target=schema_target,
        valid=valid,
        issue_count=len(issues),
        blocker_count=blocker_count,
        warning_count=warning_count,
        info_count=info_count,
        issues=tuple(issues),
        summary_ja=summary_ja,
        checked_sections=checked_sections,
    )


def _require_keys(payload: Mapping[str, Any], required: tuple[str, ...], prefix: str, issues: list[PredictionWarRoomPayloadSchemaIssue]) -> None:
    for key in required:
        if key not in payload:
            issues.append(_issue("missing_required_key", "blocker", f"{prefix}.{key}", "必須キーがありません。", expected="present", actual="missing"))


def _require_version(payload: Mapping[str, Any], key: str, expected: str, prefix: str, issues: list[PredictionWarRoomPayloadSchemaIssue]) -> None:
    actual = payload.get(key)
    if actual != expected:
        issues.append(_issue("unexpected_contract_version", "blocker", f"{prefix}.{key}", "契約バージョンが一致しません。", expected=expected, actual=actual))


def _require_safe_flags(payload: Mapping[str, Any], prefix: str, issues: list[PredictionWarRoomPayloadSchemaIssue], *, require_all_safe: bool = False) -> None:
    for key in _SAFE_TRUE_FIELDS:
        if key in payload:
            if payload.get(key) is not True:
                issues.append(_issue("unsafe_true_flag", "blocker", f"{prefix}.{key}", "安全系フラグがTrueではありません。", expected=True, actual=payload.get(key)))
        elif require_all_safe:
            issues.append(_issue("missing_safe_flag", "warning", f"{prefix}.{key}", "安全系フラグが明示されていません。", expected=True, actual="missing"))
    for key in _DANGEROUS_FALSE_FIELDS:
        if key in payload and payload.get(key) is not False:
            issues.append(_issue("dangerous_flag_enabled", "blocker", f"{prefix}.{key}", "危険系フラグがFalseではありません。", expected=False, actual=payload.get(key)))


def _require_list(payload: Mapping[str, Any], key: str, prefix: str, issues: list[PredictionWarRoomPayloadSchemaIssue], *, allow_empty: bool = False) -> None:
    value = payload.get(key)
    if not isinstance(value, (list, tuple)):
        issues.append(_issue("expected_list", "blocker", f"{prefix}.{key}", "list/tupleが必要です。", expected="list", actual=type(value).__name__))
    elif not allow_empty and len(value) == 0:
        issues.append(_issue("empty_required_list", "warning", f"{prefix}.{key}", "空ではないlistが期待されます。", expected="non_empty", actual="empty"))


def _validate_signal_percent(value: Any, path: str, issues: list[PredictionWarRoomPayloadSchemaIssue]) -> None:
    if not isinstance(value, int):
        issues.append(_issue("invalid_signal_percent_type", "blocker", path, "参考度percentはintである必要があります。", expected="int 0-99", actual=type(value).__name__))
        return
    if value < 0 or value > 99:
        issues.append(_issue("invalid_signal_percent_range", "blocker", path, "参考度percentは0-99です。100は使いません。", expected="0-99", actual=value))


def validate_prediction_warroom_display_packet_schema(display_packet: Mapping[str, Any] | Any) -> PredictionWarRoomPayloadSchemaValidationReport:
    """Validate a Prediction WarRoom display packet shape without reading runtime artifacts."""
    packet = _as_mapping(display_packet)
    issues: list[PredictionWarRoomPayloadSchemaIssue] = []
    prefix = "display_packet"
    _require_keys(
        packet,
        (
            "packet_version",
            "packet_id",
            "generated_at",
            "market_uid",
            "prediction_run_id",
            "primary_signal_summary",
            "horizon_cards",
            "family_cards",
            "source_quality_panel",
            "warning_panel",
            "ui_contract",
            "boundaries",
        ),
        prefix,
        issues,
    )
    _require_version(packet, "packet_version", DISPLAY_PACKET_VERSION, prefix, issues)
    _require_list(packet, "horizon_cards", prefix, issues)
    _require_list(packet, "family_cards", prefix, issues)
    # Q4A display packets expose read_only/non_executing at top level while
    # display_only/render_intent/not_loaded_as_runtime_display_source are carried
    # in ui_contract/boundaries. Do not create missing-flag warnings for fields
    # that are not part of the Q4A top-level contract.
    _require_safe_flags(packet, prefix, issues)
    primary = _as_mapping(packet.get("primary_signal_summary"))
    _require_keys(primary, ("estimated_signal_strength_percent", "estimated_reference_hit_rate_percent", "signal_strength_band"), f"{prefix}.primary_signal_summary", issues)
    if "estimated_signal_strength_percent" in primary:
        _validate_signal_percent(primary.get("estimated_signal_strength_percent"), f"{prefix}.primary_signal_summary.estimated_signal_strength_percent", issues)
    if "estimated_reference_hit_rate_percent" in primary:
        _validate_signal_percent(primary.get("estimated_reference_hit_rate_percent"), f"{prefix}.primary_signal_summary.estimated_reference_hit_rate_percent", issues)
    for idx, card in enumerate(_list(packet.get("horizon_cards"))):
        item = _as_mapping(card)
        item_prefix = f"{prefix}.horizon_cards[{idx}]"
        _require_keys(item, ("horizon_group", "estimated_signal_strength_percent", "signal_strength_band"), item_prefix, issues)
        if "estimated_signal_strength_percent" in item:
            _validate_signal_percent(item.get("estimated_signal_strength_percent"), f"{item_prefix}.estimated_signal_strength_percent", issues)
        _require_safe_flags(item, item_prefix, issues)
    for idx, card in enumerate(_list(packet.get("family_cards"))):
        item = _as_mapping(card)
        item_prefix = f"{prefix}.family_cards[{idx}]"
        _require_keys(item, ("family", "horizon_sec", "estimated_signal_strength_percent"), item_prefix, issues)
        if "estimated_signal_strength_percent" in item:
            _validate_signal_percent(item.get("estimated_signal_strength_percent"), f"{item_prefix}.estimated_signal_strength_percent", issues)
        _require_safe_flags(item, item_prefix, issues)
    source_quality = _as_mapping(packet.get("source_quality_panel"))
    _require_keys(source_quality, ("tier0_source_quality_gate",), f"{prefix}.source_quality_panel", issues)
    warning_panel = _as_mapping(packet.get("warning_panel"))
    _require_keys(warning_panel, ("blockers", "warnings"), f"{prefix}.warning_panel", issues)
    ui_contract = _as_mapping(packet.get("ui_contract"))
    if ui_contract.get("trigger_buttons_allowed") is True or ui_contract.get("broker_controls_allowed") is True or ui_contract.get("mode_controls_allowed") is True:
        issues.append(_issue("interactive_controls_enabled", "blocker", f"{prefix}.ui_contract", "表示packetで操作系controlが有効です。", expected=False, actual="enabled"))
    boundaries = _as_mapping(packet.get("boundaries"))
    _require_safe_flags(boundaries, f"{prefix}.boundaries", issues)
    return _finish("display_packet", issues, ("display_packet", "primary_signal_summary", "horizon_cards", "family_cards", "source_quality_panel", "warning_panel", "ui_contract", "boundaries"))


def validate_prediction_warroom_widget_group_index_schema(widget_group_index: Mapping[str, Any] | Any) -> PredictionWarRoomPayloadSchemaValidationReport:
    """Validate a Q4B widget group index or compatible supplemental index without loading runtime files."""
    index = _as_mapping(widget_group_index)
    issues: list[PredictionWarRoomPayloadSchemaIssue] = []
    prefix = "widget_group_index"
    _require_keys(index, ("index_version", "widget_groups", "auto_refresh_groups"), prefix, issues)
    if index.get("index_version") not in (WIDGET_GROUP_INDEX_VERSION, EXPLANATION_WIDGET_GROUP_INDEX_VERSION):
        issues.append(_issue("unexpected_contract_version", "blocker", f"{prefix}.index_version", "widget group index versionが未対応です。", expected=f"{WIDGET_GROUP_INDEX_VERSION} or {EXPLANATION_WIDGET_GROUP_INDEX_VERSION}", actual=index.get("index_version")))
    _require_list(index, "widget_groups", prefix, issues)
    _require_list(index, "auto_refresh_groups", prefix, issues)
    _require_safe_flags(index, prefix, issues)
    groups = [_as_mapping(item) for item in _list(index.get("widget_groups"))]
    declared_count = index.get("widget_group_count", index.get("supplemental_widget_group_count"))
    if isinstance(declared_count, int) and declared_count != len(groups):
        issues.append(_issue("widget_group_count_mismatch", "blocker", f"{prefix}.widget_group_count", "widget group countが実体数と一致しません。", expected=len(groups), actual=declared_count))
    for idx, group in enumerate(groups):
        item_prefix = f"{prefix}.widget_groups[{idx}]"
        _require_keys(group, ("packet_version", "widget_group_id", "refresh_group_id", "payload"), item_prefix, issues)
        _require_safe_flags(group, item_prefix, issues)
        payload = _as_mapping(group.get("payload"))
        _require_safe_flags(payload, f"{item_prefix}.payload", issues)
    for idx, refresh in enumerate(_list(index.get("auto_refresh_groups"))):
        item = _as_mapping(refresh)
        item_prefix = f"{prefix}.auto_refresh_groups[{idx}]"
        _require_keys(item, ("widget_group_id", "refresh_group_id", "refresh_interval_sec", "refresh_priority"), item_prefix, issues)
        interval = item.get("refresh_interval_sec")
        if not isinstance(interval, int) or interval <= 0:
            issues.append(_issue("invalid_refresh_interval", "blocker", f"{item_prefix}.refresh_interval_sec", "refresh intervalは正のintです。", expected="positive int", actual=interval))
    return _finish("widget_group_index", issues, ("widget_groups", "auto_refresh_groups", "safe_flags"))


def validate_prediction_warroom_explanation_panel_schema(explanation_panel: Mapping[str, Any] | Any) -> PredictionWarRoomPayloadSchemaValidationReport:
    """Validate a Q5A source-quality explanation panel shape without rendering or runtime access."""
    panel = _as_mapping(explanation_panel)
    issues: list[PredictionWarRoomPayloadSchemaIssue] = []
    prefix = "explanation_panel"
    _require_keys(panel, ("panel_version", "signal_cap_explanations", "source_quality_gate_cards", "missing_source_cards", "family_cap_cards", "watch_points"), prefix, issues)
    _require_version(panel, "panel_version", EXPLANATION_PANEL_VERSION, prefix, issues)
    for key in ("signal_cap_explanations", "source_quality_gate_cards", "missing_source_cards", "family_cap_cards", "watch_points"):
        _require_list(panel, key, prefix, issues, allow_empty=True)
    _require_safe_flags(panel, prefix, issues, require_all_safe=True)
    for section in ("signal_cap_explanations", "source_quality_gate_cards", "missing_source_cards", "family_cap_cards", "watch_points"):
        for idx, raw in enumerate(_list(panel.get(section))):
            card = _as_mapping(raw)
            item_prefix = f"{prefix}.{section}[{idx}]"
            _require_keys(card, ("card_version", "operator_action_kind"), item_prefix, issues)
            if card.get("operator_action_kind") != "observe_only":
                issues.append(_issue("operator_action_not_observe_only", "blocker", f"{item_prefix}.operator_action_kind", "説明カードはobserve_onlyのみです。", expected="observe_only", actual=card.get("operator_action_kind")))
            _require_safe_flags(card, item_prefix, issues)
    return _finish("explanation_panel", issues, ("explanation_panel", "explanation_cards", "safe_flags"))


def validate_prediction_warroom_payload_contract_bundle(
    *,
    display_packet: Mapping[str, Any] | Any | None = None,
    widget_group_index: Mapping[str, Any] | Any | None = None,
    explanation_panel: Mapping[str, Any] | Any | None = None,
    explanation_widget_group_index: Mapping[str, Any] | Any | None = None,
) -> PredictionWarRoomPayloadSchemaValidationReport:
    """Validate a supplied WarRoom payload bundle by combining display/widget/explanation checks."""
    issues: list[PredictionWarRoomPayloadSchemaIssue] = []
    checked: list[str] = []
    if display_packet is not None:
        report = validate_prediction_warroom_display_packet_schema(display_packet)
        checked.append("display_packet")
        issues.extend(report.issues)
    if widget_group_index is not None:
        report = validate_prediction_warroom_widget_group_index_schema(widget_group_index)
        checked.append("widget_group_index")
        issues.extend(report.issues)
    if explanation_panel is not None:
        report = validate_prediction_warroom_explanation_panel_schema(explanation_panel)
        checked.append("explanation_panel")
        issues.extend(report.issues)
    if explanation_widget_group_index is not None:
        report = validate_prediction_warroom_widget_group_index_schema(explanation_widget_group_index)
        checked.append("explanation_widget_group_index")
        issues.extend(report.issues)
    if not checked:
        issues.append(_issue("empty_payload_bundle", "blocker", "payload_bundle", "検証対象payloadがありません。", expected="at least one payload", actual="none"))
    return _finish("payload_contract_bundle", issues, tuple(checked))
