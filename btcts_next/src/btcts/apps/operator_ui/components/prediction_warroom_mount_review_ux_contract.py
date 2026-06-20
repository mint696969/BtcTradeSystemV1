# path: ./btcts_next/src/btcts/apps/operator_ui/components/prediction_warroom_mount_review_ux_contract.py
# desc: Manual visual/UX verification contract for the folded Prediction WarRoom mount review section. Contract metadata only; no Streamlit rendering, no page mutation, no runtime loader, file access, payload decode, Collector, AutoTrade, broker, mode, or append behavior.

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Mapping, Tuple

from .prediction_warroom_page_insertion_contract import (
    PREDICTION_WARROOM_PAGE_INSERTION_CONTRACT_VERSION,
    build_prediction_warroom_page_insertion_contract,
)
from .prediction_warroom_ui_mount_presenter import (
    PREDICTION_WARROOM_UI_MOUNT_PRESENTER_VERSION,
    build_prediction_warroom_ui_mount_presenter_packet,
)

PREDICTION_WARROOM_MOUNT_REVIEW_UX_CONTRACT_VERSION = "prediction_warroom_mount_review_ux_contract.ps_q8e.v1"
PREDICTION_WARROOM_MOUNT_REVIEW_UX_CONTRACT_ID = "prediction_warroom_mount_review_ux_contract"
SECTION_LABEL = "Prediction WarRoom mount review"
SECTION_HELPER_NAME = "_render_prediction_warroom_ui_mount_review_section"
SECTION_ANCHOR = "after_operator_support_zone_before_slot_diagnostics"
EXPECTED_MOUNT_ENTRY_ROW_COUNT = 12
EXPECTED_ZONE_SECTION_COUNT = 3
EXPECTED_BLOCKED_ENTRY_ROW_COUNT = 0
EXPECTED_MANUAL_CHECK_COUNT = 6


@dataclass(frozen=True)
class PredictionWarRoomMountReviewUXContract:
    contract_version: str
    contract_id: str
    contract_kind: str
    ux_state: str
    source_presenter_version: str = PREDICTION_WARROOM_UI_MOUNT_PRESENTER_VERSION
    source_insertion_contract_version: str = PREDICTION_WARROOM_PAGE_INSERTION_CONTRACT_VERSION
    section_label: str = SECTION_LABEL
    section_helper_name: str = SECTION_HELPER_NAME
    section_anchor: str = SECTION_ANCHOR
    expected_initial_expanded: bool = False
    expected_mount_entry_row_count: int = EXPECTED_MOUNT_ENTRY_ROW_COUNT
    expected_zone_section_count: int = EXPECTED_ZONE_SECTION_COUNT
    expected_blocked_entry_row_count: int = EXPECTED_BLOCKED_ENTRY_ROW_COUNT
    presenter_display_state: str | None = None
    presenter_compact_line: str | None = None
    insertion_state: str | None = None
    manual_visual_checks: Tuple[Mapping[str, Any], ...] = ()
    manual_visual_check_count: int = 0
    ux_metrics: Mapping[str, Any] = field(default_factory=dict)
    operator_guidance_ja: Tuple[str, ...] = ()
    integration_contract: Mapping[str, Any] = field(default_factory=dict)
    boundaries: Mapping[str, Any] = field(default_factory=dict)
    read_only: bool = True
    non_executing: bool = True
    ux_contract_only: bool = True
    manual_visual_verification_only: bool = True
    display_only: bool = True
    render_intent_only: bool = True
    not_loaded_as_runtime_display_source: bool = True
    ui_rendering_allowed: bool = False
    streamlit_render_allowed: bool = False
    warroom_page_mutation_allowed: bool = False
    page_mutation_allowed: bool = False
    app_routing_mutation_allowed: bool = False
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
            "contract_version": self.contract_version,
            "contract_id": self.contract_id,
            "contract_kind": self.contract_kind,
            "ux_state": self.ux_state,
            "source_presenter_version": self.source_presenter_version,
            "source_insertion_contract_version": self.source_insertion_contract_version,
            "section_label": self.section_label,
            "section_helper_name": self.section_helper_name,
            "section_anchor": self.section_anchor,
            "expected_initial_expanded": self.expected_initial_expanded,
            "expected_mount_entry_row_count": self.expected_mount_entry_row_count,
            "expected_zone_section_count": self.expected_zone_section_count,
            "expected_blocked_entry_row_count": self.expected_blocked_entry_row_count,
            "presenter_display_state": self.presenter_display_state,
            "presenter_compact_line": self.presenter_compact_line,
            "insertion_state": self.insertion_state,
            "manual_visual_checks": [dict(item) for item in self.manual_visual_checks],
            "manual_visual_check_count": self.manual_visual_check_count,
            "ux_metrics": dict(self.ux_metrics),
            "operator_guidance_ja": list(self.operator_guidance_ja),
            "integration_contract": dict(self.integration_contract),
            "boundaries": dict(self.boundaries),
            "read_only": self.read_only,
            "non_executing": self.non_executing,
            "ux_contract_only": self.ux_contract_only,
            "manual_visual_verification_only": self.manual_visual_verification_only,
            "display_only": self.display_only,
            "render_intent_only": self.render_intent_only,
            "not_loaded_as_runtime_display_source": self.not_loaded_as_runtime_display_source,
            "ui_rendering_allowed": self.ui_rendering_allowed,
            "streamlit_render_allowed": self.streamlit_render_allowed,
            "warroom_page_mutation_allowed": self.warroom_page_mutation_allowed,
            "page_mutation_allowed": self.page_mutation_allowed,
            "app_routing_mutation_allowed": self.app_routing_mutation_allowed,
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


def _safe_flags() -> Dict[str, Any]:
    return {
        "read_only": True,
        "non_executing": True,
        "ux_contract_only": True,
        "manual_visual_verification_only": True,
        "display_only": True,
        "render_intent_only": True,
        "not_loaded_as_runtime_display_source": True,
        "ui_rendering_allowed": False,
        "streamlit_render_allowed": False,
        "warroom_page_mutation_allowed": False,
        "page_mutation_allowed": False,
        "app_routing_mutation_allowed": False,
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


def _manual_check(*, check_id: str, label_ja: str, expected_ja: str, pass_condition_ja: str) -> Mapping[str, Any]:
    return {
        "check_id": check_id,
        "label_ja": label_ja,
        "expected_ja": expected_ja,
        "pass_condition_ja": pass_condition_ja,
        "status": "requires_human_visual_confirmation",
        "completed_by_contract": False,
        "may_be_checked_in_running_ui": True,
        "automated_runtime_check": False,
        **_safe_flags(),
    }


def _manual_visual_checks() -> Tuple[Mapping[str, Any], ...]:
    return (
        _manual_check(
            check_id="section_visible_in_warroom",
            label_ja="WarRoom内でsectionラベルが見える",
            expected_ja="Prediction WarRoom mount review が表示される",
            pass_condition_ja="WarRoomを開いた時にsection見出しが存在する",
        ),
        _manual_check(
            check_id="section_collapsed_by_default",
            label_ja="sectionが初期collapsedである",
            expected_ja="operatorが開くまで中身を展開しない",
            pass_condition_ja="ページ初期表示時にtableが展開表示されていない",
        ),
        _manual_check(
            check_id="compact_line_visible_when_expanded",
            label_ja="展開時にcompact lineが読める",
            expected_ja="ready:true / entries:12 / zones:3 / blocked:0 / render:false を確認できる",
            pass_condition_ja="展開後にQ8B compact lineが1行で読める",
        ),
        _manual_check(
            check_id="zone_summary_rows_visible",
            label_ja="zone summary rowsが読める",
            expected_ja="overview / primary_live / operator_support の3 zoneが確認できる",
            pass_condition_ja="zone tableに3行が見える",
        ),
        _manual_check(
            check_id="mount_entry_rows_visible",
            label_ja="mount entry rowsが読める",
            expected_ja="12 widget group rowが確認できる",
            pass_condition_ja="mount row tableに12件のwidget_group_idが見える",
        ),
        _manual_check(
            check_id="runtime_remains_disconnected",
            label_ja="runtime接続が増えていない",
            expected_ja="loader / file read / payload decode / broker操作の入口がない",
            pass_condition_ja="section内にbutton/form/toggle/approval操作が存在しない",
        ),
    )


def build_prediction_warroom_mount_review_ux_contract(
    *,
    presenter_packet: Mapping[str, Any] | Any | None = None,
    insertion_contract: Mapping[str, Any] | Any | None = None,
) -> PredictionWarRoomMountReviewUXContract:
    """Build a manual visual/UX verification contract for the folded WarRoom mount review section."""
    presenter = dict(_as_mapping(presenter_packet)) if presenter_packet is not None else build_prediction_warroom_ui_mount_presenter_packet().to_dict()
    insertion = dict(_as_mapping(insertion_contract)) if insertion_contract is not None else build_prediction_warroom_page_insertion_contract(
        presenter_packet=presenter,
    ).to_dict()
    checks = _manual_visual_checks()
    presenter_ready = (
        presenter.get("display_state") == "ready_for_operator_review_render_disabled"
        and int(presenter.get("mount_entry_row_count") or 0) == EXPECTED_MOUNT_ENTRY_ROW_COUNT
        and int(presenter.get("zone_section_count") or 0) == EXPECTED_ZONE_SECTION_COUNT
        and int(presenter.get("blocked_entry_row_count") or 0) == EXPECTED_BLOCKED_ENTRY_ROW_COUNT
    )
    insertion_ready = insertion.get("insertion_state") == "ready_for_future_guarded_warroom_page_insertion"
    contract_ready = presenter_ready and insertion_ready and len(checks) == EXPECTED_MANUAL_CHECK_COUNT
    ux_state = "ready_for_manual_visual_confirmation_runtime_disconnected" if contract_ready else "blocked_before_manual_visual_confirmation"
    metrics = {
        "presenter_ready": presenter_ready,
        "insertion_contract_ready": insertion_ready,
        "manual_visual_check_count": len(checks),
        "expected_manual_check_count": EXPECTED_MANUAL_CHECK_COUNT,
        "mount_entry_row_count": int(presenter.get("mount_entry_row_count") or 0),
        "zone_section_count": int(presenter.get("zone_section_count") or 0),
        "blocked_entry_row_count": int(presenter.get("blocked_entry_row_count") or 0),
        "expected_initial_expanded": False,
        "runtime_disconnected": True,
        "loader_disconnected": True,
        "file_read_disconnected": True,
        "payload_decode_disconnected": True,
        "broker_disconnected": True,
        "ux_contract_ready": contract_ready,
    }
    integration_contract = {
        "contract_version": PREDICTION_WARROOM_MOUNT_REVIEW_UX_CONTRACT_VERSION,
        "source_presenter_contract": PREDICTION_WARROOM_UI_MOUNT_PRESENTER_VERSION,
        "source_insertion_contract": PREDICTION_WARROOM_PAGE_INSERTION_CONTRACT_VERSION,
        "integration_kind": "manual_visual_ux_verification_contract",
        "contract_metadata_only": True,
        "human_visual_confirmation_required": True,
        "does_not_call_streamlit": True,
        "does_not_mutate_warroom_page": True,
        "does_not_mutate_app_routing": True,
        "does_not_grant_approval": True,
        "does_not_grant_authorization": True,
        "requires_streamlit_rendering": False,
        "requires_runtime_loader": False,
        "requires_hot_file_read": False,
        "requires_payload_decode": False,
        **_safe_flags(),
    }
    return PredictionWarRoomMountReviewUXContract(
        contract_version=PREDICTION_WARROOM_MOUNT_REVIEW_UX_CONTRACT_VERSION,
        contract_id=PREDICTION_WARROOM_MOUNT_REVIEW_UX_CONTRACT_ID,
        contract_kind="prediction_warroom_mount_review_manual_visual_ux_contract",
        ux_state=ux_state,
        presenter_display_state=str(presenter.get("display_state")) if presenter.get("display_state") else None,
        presenter_compact_line=str(presenter.get("compact_line")) if presenter.get("compact_line") else None,
        insertion_state=str(insertion.get("insertion_state")) if insertion.get("insertion_state") else None,
        manual_visual_checks=checks,
        manual_visual_check_count=len(checks),
        ux_metrics=metrics,
        operator_guidance_ja=(
            "WarRoomで Prediction WarRoom mount review が初期collapsedで見えることを確認してください。",
            "展開時はcompact line・zone summary・mount rowsだけを確認してください。",
            "このcontractはloader・file read・payload decode・runtime・brokerを有効化しません。",
        ),
        integration_contract=integration_contract,
        boundaries=_safe_flags(),
    )


def build_prediction_warroom_mount_review_ux_contract_index(
    *,
    presenter_packet: Mapping[str, Any] | Any | None = None,
    insertion_contract: Mapping[str, Any] | Any | None = None,
) -> Dict[str, Any]:
    """Return a compact index for the manual visual/UX verification contract."""
    contract = build_prediction_warroom_mount_review_ux_contract(
        presenter_packet=presenter_packet,
        insertion_contract=insertion_contract,
    ).to_dict()
    return {
        "contract_index_version": PREDICTION_WARROOM_MOUNT_REVIEW_UX_CONTRACT_VERSION,
        "contract_id": contract.get("contract_id"),
        "contract_kind": contract.get("contract_kind"),
        "ux_state": contract.get("ux_state"),
        "section_label": contract.get("section_label"),
        "section_anchor": contract.get("section_anchor"),
        "expected_initial_expanded": contract.get("expected_initial_expanded"),
        "presenter_display_state": contract.get("presenter_display_state"),
        "presenter_compact_line": contract.get("presenter_compact_line"),
        "insertion_state": contract.get("insertion_state"),
        "manual_visual_check_count": contract.get("manual_visual_check_count"),
        "manual_visual_checks": [dict(item) for item in _list(contract.get("manual_visual_checks"))],
        "ux_metrics": dict(_as_mapping(contract.get("ux_metrics"))),
        "integration_contract": dict(_as_mapping(contract.get("integration_contract"))),
        "boundaries": dict(_as_mapping(contract.get("boundaries"))),
        **_safe_flags(),
    }
