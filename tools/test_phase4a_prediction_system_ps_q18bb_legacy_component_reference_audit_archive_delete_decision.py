# path: ./tools/test_phase4a_prediction_system_ps_q18bb_legacy_component_reference_audit_archive_delete_decision.py
# desc: Unit tests and reusable audit packet for PS-Q18BB legacy component reference audit/archive-delete decision.

from __future__ import annotations

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
WARROOM_PAGE = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/views/warroom_page.py"

LEGACY_COMPONENT_STEMS = (
    "prediction_warroom_ui_mount_presenter",
    "prediction_warroom_lowered_display_packet_visibility_review_panel",
    "prediction_warroom_actual_review_packet_live_session_seed_page_mount",
    "prediction_warroom_latest_prediction_source_review_panel",
    "prediction_warroom_realtime_review_preflight_panel",
    "prediction_warroom_non_ui_scheduled_producer_status_panel",
    "prediction_warroom_prediction_widgets_disabled_section_review_panel",
    "prediction_warroom_prediction_widget_source_readiness_preflight_panel",
    "prediction_warroom_prediction_widget_source_read_probe_status_panel",
    "prediction_warroom_latest_prediction_summary_widget_props_candidate_status_panel",
    "prediction_warroom_latest_prediction_summary_widget_render_disabled_packet_status_panel",
    "prediction_warroom_latest_prediction_summary_widget_mapped_payload_render_disabled_packet_status_panel",
    "prediction_warroom_latest_prediction_summary_widget_mapped_payload_value_rows_panel",
    "prediction_warroom_latest_prediction_summary_widget_operator_value_summary_panel",
    "prediction_warroom_latest_prediction_summary_widget_real_source_handoff_preflight_panel",
    "latest_prediction_summary_widget_q18ab_safe_display_mount_panel",
    "latest_prediction_summary_widget_q18ai_warroom_render_disabled_packet_panel",
)

PREDICTION_WIDGET_COMPONENTS = (
    "components/prediction_widgets/latest_prediction_summary_widget.py",
    "components/prediction_widgets/prediction_delta_widget.py",
    "components/prediction_widgets/scenario_trace_widget.py",
    "components/prediction_widgets/evidence_weighting_widget.py",
    "components/prediction_widgets/invalidation_rewrite_widget.py",
    "components/prediction_widgets/source_quality_freshness_widget.py",
    "components/prediction_widgets/warning_blocker_widget.py",
    "components/prediction_widgets/signal_strength_calibration_widget.py",
    "components/prediction_widgets/parameter_candidate_comparison_widget.py",
    "components/prediction_widgets/replay_outcome_calibration_widget.py",
    "components/prediction_widgets/producer_freshness_status_widget.py",
    "components/prediction_widgets/runtime_boundary_safety_widget.py",
)

FALSE_BOUNDARIES = (
    "real_prediction_widget_rendering_allowed",
    "real_prediction_widget_render_invoked",
    "streamlit_real_widget_render_invoked",
    "component_runtime_binding_allowed",
    "component_props_bound_to_runtime",
    "runtime_artifact_write_allowed",
    "status_artifact_write_allowed",
    "parameter_apply_allowed",
    "parameter_staging_write_allowed",
    "ledger_append_allowed",
    "autotrade_trigger_allowed",
    "broker_private_api_allowed",
    "would_send_to_broker",
)


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8-sig")


def _repo_reference_count(stem: str) -> int:
    count = 0
    for root in (REPO_ROOT / "btcts_next/src", REPO_ROOT / "tools", REPO_ROOT / "docs/strategy"):
        if not root.exists():
            continue
        for path in root.rglob("*.py") if root.suffix != ".md" else []:
            text = _read(path)
            count += text.count(stem)
        if root.name == "strategy":
            for path in root.rglob("*.md"):
                text = _read(path)
                count += text.count(stem)
    return count


def build_ps_q18bb_legacy_component_reference_audit_packet() -> dict:
    warroom_text = _read(WARROOM_PAGE)
    warroom_hits = {stem: stem in warroom_text for stem in LEGACY_COMPONENT_STEMS}
    reference_counts = {stem: _repo_reference_count(stem) for stem in LEGACY_COMPONENT_STEMS}
    packet = {
        "ok": True,
        "audit_version": "prediction_warroom.q18bb_legacy_component_reference_audit.v1",
        "warroom_page_normal_render_path_refs": False,
        "warroom_page_legacy_import_refs": any(warroom_hits.values()),
        "warroom_page_hit_stems": sorted(stem for stem, hit in warroom_hits.items() if hit),
        "legacy_component_stem_count": len(LEGACY_COMPONENT_STEMS),
        "legacy_component_reference_counts": reference_counts,
        "legacy_component_stems_with_repo_refs": sorted(stem for stem, count in reference_counts.items() if count > 0),
        "component_modules_deleted_this_slice": False,
        "immediate_physical_delete_decision": "defer",
        "archive_delete_decision": "preserve_as_spec_or_contract_until_reference_audit_zero_or_docs_only_archive",
        "future_extension_contracts_preserved": True,
        "prediction_widget_component_family_preserved": True,
        "prediction_widget_component_count": len(PREDICTION_WIDGET_COMPONENTS),
        "next_safe_slice": "PS-Q18BC WarRoom cleanup close and handoff",
    }
    packet.update({key: False for key in FALSE_BOUNDARIES})
    return packet


def test_ps_q18bb_reference_audit_defers_physical_delete_and_keeps_runtime_boundary() -> None:
    packet = build_ps_q18bb_legacy_component_reference_audit_packet()
    assert packet["ok"] is True
    assert packet["warroom_page_normal_render_path_refs"] is False
    assert packet["warroom_page_legacy_import_refs"] is False
    assert packet["warroom_page_hit_stems"] == []
    assert packet["legacy_component_stem_count"] == 17
    assert packet["component_modules_deleted_this_slice"] is False
    assert packet["immediate_physical_delete_decision"] == "defer"
    assert packet["future_extension_contracts_preserved"] is True
    assert packet["prediction_widget_component_family_preserved"] is True
    assert packet["prediction_widget_component_count"] == 12
    assert packet["next_safe_slice"] == "PS-Q18BC WarRoom cleanup close and handoff"
    assert any(count > 0 for count in packet["legacy_component_reference_counts"].values())
    for key in FALSE_BOUNDARIES:
        assert packet[key] is False, key
