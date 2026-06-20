# path: ./btcts_next/src/btcts/apps/operator_ui/components/prediction_warroom_page_insertion_contract.py
# desc: Display-only insertion contract for adding Prediction WarRoom mount presenter into warroom_page in a future slice. Contract metadata only; no Streamlit rendering, no page mutation, no runtime loader, file access, payload decode, Collector, AutoTrade, broker, mode, or append behavior.

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Iterable, Mapping, Tuple

from .prediction_warroom_ui_mount_presenter import (
    PREDICTION_WARROOM_UI_MOUNT_PRESENTER_VERSION,
    build_prediction_warroom_ui_mount_presenter_packet,
)

PREDICTION_WARROOM_PAGE_INSERTION_CONTRACT_VERSION = "prediction_warroom_page_insertion_contract.ps_q8c.v1"
PREDICTION_WARROOM_PAGE_INSERTION_CONTRACT_ID = "prediction_warroom_page_insertion_contract"
TARGET_VIEW_MODULE = "btcts.apps.operator_ui.views.warroom_page"
TARGET_VIEW_FILE_HINT = "btcts_next/src/btcts/apps/operator_ui/views/warroom_page.py"
PROPOSED_SECTION_ID = "prediction_warroom_ui_mount_review_section"
PROPOSED_SECTION_LABEL = "Prediction WarRoom mount review"
PROPOSED_SECTION_ANCHOR = "after_operator_support_zone_before_slot_diagnostics"
PROPOSED_RENDER_HELPER_NAME = "_render_prediction_warroom_ui_mount_review_section"
PROPOSED_IMPORT_SYMBOL = "build_prediction_warroom_ui_mount_presenter_packet"


@dataclass(frozen=True)
class PredictionWarRoomPageInsertionContract:
    contract_version: str
    contract_id: str
    contract_kind: str
    insertion_state: str
    source_presenter_version: str = PREDICTION_WARROOM_UI_MOUNT_PRESENTER_VERSION
    target_view_module: str = TARGET_VIEW_MODULE
    target_view_file_hint: str = TARGET_VIEW_FILE_HINT
    proposed_section_id: str = PROPOSED_SECTION_ID
    proposed_section_label: str = PROPOSED_SECTION_LABEL
    proposed_section_anchor: str = PROPOSED_SECTION_ANCHOR
    proposed_render_helper_name: str = PROPOSED_RENDER_HELPER_NAME
    proposed_import_symbol: str = PROPOSED_IMPORT_SYMBOL
    presenter_display_state: str | None = None
    presenter_compact_line: str | None = None
    zone_section_count: int = 0
    mount_entry_row_count: int = 0
    blocked_entry_row_count: int = 0
    insertion_steps: Tuple[Mapping[str, Any], ...] = ()
    insertion_blockers: Tuple[Mapping[str, Any], ...] = ()
    insertion_metrics: Mapping[str, Any] = field(default_factory=dict)
    operator_guidance_ja: Tuple[str, ...] = ()
    integration_contract: Mapping[str, Any] = field(default_factory=dict)
    boundaries: Mapping[str, Any] = field(default_factory=dict)
    read_only: bool = True
    non_executing: bool = True
    contract_only: bool = True
    insertion_plan_only: bool = True
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
            "insertion_state": self.insertion_state,
            "source_presenter_version": self.source_presenter_version,
            "target_view_module": self.target_view_module,
            "target_view_file_hint": self.target_view_file_hint,
            "proposed_section_id": self.proposed_section_id,
            "proposed_section_label": self.proposed_section_label,
            "proposed_section_anchor": self.proposed_section_anchor,
            "proposed_render_helper_name": self.proposed_render_helper_name,
            "proposed_import_symbol": self.proposed_import_symbol,
            "presenter_display_state": self.presenter_display_state,
            "presenter_compact_line": self.presenter_compact_line,
            "zone_section_count": self.zone_section_count,
            "mount_entry_row_count": self.mount_entry_row_count,
            "blocked_entry_row_count": self.blocked_entry_row_count,
            "insertion_steps": [dict(item) for item in self.insertion_steps],
            "insertion_blockers": [dict(item) for item in self.insertion_blockers],
            "insertion_metrics": dict(self.insertion_metrics),
            "operator_guidance_ja": list(self.operator_guidance_ja),
            "integration_contract": dict(self.integration_contract),
            "boundaries": dict(self.boundaries),
            "read_only": self.read_only,
            "non_executing": self.non_executing,
            "contract_only": self.contract_only,
            "insertion_plan_only": self.insertion_plan_only,
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
        "contract_only": True,
        "insertion_plan_only": True,
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


def _step(*, step_id: str, description_ja: str, required: bool = True) -> Mapping[str, Any]:
    return {
        "step_id": step_id,
        "description_ja": description_ja,
        "required": required,
        "completed_in_this_slice": False,
        "allowed_in_future_guarded_slice": True,
        "streamlit_render_allowed_in_this_slice": False,
        "warroom_page_mutation_allowed_in_this_slice": False,
        **_safe_flags(),
    }


def _blocker(issue_code: str, *, severity: str = "blocker") -> Mapping[str, Any]:
    return {
        "issue_code": issue_code,
        "severity": severity,
        **_safe_flags(),
    }


def _insertion_steps() -> Tuple[Mapping[str, Any], ...]:
    return (
        _step(
            step_id="add_presenter_import",
            description_ja="future sliceでQ8B presenter builder importをwarroom_page.pyへ追加する",
        ),
        _step(
            step_id="add_folded_render_helper",
            description_ja="future sliceで折りたたみ表示専用helperを追加する",
        ),
        _step(
            step_id="insert_after_operator_support_before_slot_diagnostics",
            description_ja="operator support zoneの後、slot diagnosticsの前に折りたたみsectionを配置する",
        ),
        _step(
            step_id="keep_section_collapsed_by_default",
            description_ja="sectionは初期collapsedで、operatorが確認時だけ開く",
        ),
        _step(
            step_id="render_compact_line_and_zone_rows_only",
            description_ja="compact line・zone summary・mount rowsのみを表示し、runtime payload decodeやloaderは呼ばない",
        ),
    )


def build_prediction_warroom_page_insertion_contract(
    *,
    presenter_packet: Mapping[str, Any] | Any | None = None,
    mount_catalog: Mapping[str, Any] | Any | None = None,
    catalog_entry: Mapping[str, Any] | Any | None = None,
    handoff_bundle: Mapping[str, Any] | Any | None = None,
    display_packet: Mapping[str, Any] | Any | None = None,
    artifact_metadata_inputs: Iterable[Mapping[str, Any]] | None = None,
    hot_latest_root_hint: str = "D:\\btc_ts_hot",
) -> PredictionWarRoomPageInsertionContract:
    """Build a future WarRoom page insertion contract without mutating or rendering the page."""
    presenter = dict(_as_mapping(presenter_packet)) if presenter_packet is not None else build_prediction_warroom_ui_mount_presenter_packet(
        mount_catalog=mount_catalog,
        catalog_entry=catalog_entry,
        handoff_bundle=handoff_bundle,
        display_packet=display_packet,
        artifact_metadata_inputs=artifact_metadata_inputs,
        hot_latest_root_hint=hot_latest_root_hint,
    ).to_dict()
    steps = _insertion_steps()
    blockers: list[Mapping[str, Any]] = []
    if presenter.get("display_state") != "ready_for_operator_review_render_disabled":
        blockers.append(_blocker("presenter_not_ready_for_operator_review"))
    if int(presenter.get("mount_entry_row_count") or 0) != 12:
        blockers.append(_blocker("unexpected_mount_entry_row_count"))
    if int(presenter.get("zone_section_count") or 0) != 3:
        blockers.append(_blocker("unexpected_zone_section_count"))
    if int(presenter.get("blocked_entry_row_count") or 0) != 0:
        blockers.append(_blocker("presenter_has_blocked_entry_rows"))
    ready = not blockers
    insertion_state = "ready_for_future_guarded_warroom_page_insertion" if ready else "blocked_before_future_guarded_warroom_page_insertion"
    metrics = {
        "presenter_ready": presenter.get("display_state") == "ready_for_operator_review_render_disabled",
        "mount_entry_row_count": int(presenter.get("mount_entry_row_count") or 0),
        "zone_section_count": int(presenter.get("zone_section_count") or 0),
        "blocked_entry_row_count": int(presenter.get("blocked_entry_row_count") or 0),
        "required_step_count": sum(1 for item in steps if item.get("required") is True),
        "completed_in_this_slice_count": sum(1 for item in steps if item.get("completed_in_this_slice") is True),
        "insertion_blocker_count": len(blockers),
        "future_insertion_allowed_by_contract": ready,
        "insertion_allowed_in_this_slice": False,
        "streamlit_render_allowed": False,
        "warroom_page_mutation_allowed": False,
        "actual_loader_execution_allowed": False,
        "actual_file_read_allowed_by_this_contract": False,
        "actual_payload_decode_allowed_by_this_contract": False,
    }
    integration_contract = {
        "contract_version": PREDICTION_WARROOM_PAGE_INSERTION_CONTRACT_VERSION,
        "source_presenter_contract": PREDICTION_WARROOM_UI_MOUNT_PRESENTER_VERSION,
        "integration_kind": "future_guarded_warroom_page_insertion_contract",
        "contract_metadata_only": True,
        "does_not_call_streamlit": True,
        "does_not_mutate_warroom_page": True,
        "does_not_mutate_app_routing": True,
        "does_not_register_widgets": True,
        "does_not_grant_approval": True,
        "does_not_grant_authorization": True,
        "future_slice_must_keep_section_folded_by_default": True,
        "future_slice_must_use_existing_live_shell_folded_section": True,
        "future_slice_must_not_decode_payload_or_read_hot_latest": True,
        "requires_streamlit_rendering": False,
        "requires_runtime_loader": False,
        "requires_hot_file_read": False,
        "requires_payload_decode": False,
        **_safe_flags(),
    }
    return PredictionWarRoomPageInsertionContract(
        contract_version=PREDICTION_WARROOM_PAGE_INSERTION_CONTRACT_VERSION,
        contract_id=PREDICTION_WARROOM_PAGE_INSERTION_CONTRACT_ID,
        contract_kind="prediction_warroom_future_page_insertion_contract",
        insertion_state=insertion_state,
        presenter_display_state=str(presenter.get("display_state")) if presenter.get("display_state") else None,
        presenter_compact_line=str(presenter.get("compact_line")) if presenter.get("compact_line") else None,
        zone_section_count=int(presenter.get("zone_section_count") or 0),
        mount_entry_row_count=int(presenter.get("mount_entry_row_count") or 0),
        blocked_entry_row_count=int(presenter.get("blocked_entry_row_count") or 0),
        insertion_steps=steps,
        insertion_blockers=tuple(blockers),
        insertion_metrics=metrics,
        operator_guidance_ja=(
            "このcontractはWarRoom pageへ将来挿入するための条件整理だけです。",
            "このsliceではwarroom_page.py変更・Streamlit描画・loader・file read・payload decodeは行いません。",
            "実挿入sliceでは折りたたみsectionを初期collapsedにし、Q8B presenter packetのcompact/zone/rowだけを表示してください。",
        ),
        integration_contract=integration_contract,
        boundaries=_safe_flags(),
    )


def build_prediction_warroom_page_insertion_contract_index(
    *,
    presenter_packet: Mapping[str, Any] | Any | None = None,
    mount_catalog: Mapping[str, Any] | Any | None = None,
    catalog_entry: Mapping[str, Any] | Any | None = None,
    handoff_bundle: Mapping[str, Any] | Any | None = None,
    display_packet: Mapping[str, Any] | Any | None = None,
    artifact_metadata_inputs: Iterable[Mapping[str, Any]] | None = None,
    hot_latest_root_hint: str = "D:\\btc_ts_hot",
) -> Dict[str, Any]:
    """Return a compact contract index for a future guarded WarRoom page insertion slice."""
    contract = build_prediction_warroom_page_insertion_contract(
        presenter_packet=presenter_packet,
        mount_catalog=mount_catalog,
        catalog_entry=catalog_entry,
        handoff_bundle=handoff_bundle,
        display_packet=display_packet,
        artifact_metadata_inputs=artifact_metadata_inputs,
        hot_latest_root_hint=hot_latest_root_hint,
    ).to_dict()
    return {
        "contract_index_version": PREDICTION_WARROOM_PAGE_INSERTION_CONTRACT_VERSION,
        "contract_id": contract.get("contract_id"),
        "contract_kind": contract.get("contract_kind"),
        "insertion_state": contract.get("insertion_state"),
        "target_view_module": contract.get("target_view_module"),
        "proposed_section_id": contract.get("proposed_section_id"),
        "proposed_section_anchor": contract.get("proposed_section_anchor"),
        "presenter_display_state": contract.get("presenter_display_state"),
        "presenter_compact_line": contract.get("presenter_compact_line"),
        "zone_section_count": contract.get("zone_section_count"),
        "mount_entry_row_count": contract.get("mount_entry_row_count"),
        "blocked_entry_row_count": contract.get("blocked_entry_row_count"),
        "insertion_steps": [dict(item) for item in _list(contract.get("insertion_steps"))],
        "insertion_blockers": [dict(item) for item in _list(contract.get("insertion_blockers"))],
        "insertion_metrics": dict(_as_mapping(contract.get("insertion_metrics"))),
        "integration_contract": dict(_as_mapping(contract.get("integration_contract"))),
        "boundaries": dict(_as_mapping(contract.get("boundaries"))),
        **_safe_flags(),
    }
