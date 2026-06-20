# path: ./tools/test_prediction_system_ps_q7l_readiness_widget_registry_registration_guard.py
# desc: Guard for PS-Q7L Q7K supplemental handoff readiness widget registration in supplemental registry/catalog path. Registration only; no approval write, runtime reads, payload decode, rendering, Collector, AutoTrade, or broker behavior.

from __future__ import annotations

import ast
from pathlib import Path

from _btcts_bootstrap import ensure_btcts_on_syspath
ensure_btcts_on_syspath()

from btcts.apps.operator_ui.components.prediction_warroom_handoff_catalog_visibility import build_prediction_warroom_handoff_catalog_visibility_entry
from btcts.apps.operator_ui.components.prediction_warroom_supplemental_handoff_bundle import build_prediction_warroom_supplemental_handoff_bundle
from btcts.apps.operator_ui.components.prediction_warroom_supplemental_widget_registry import build_prediction_warroom_supplemental_widget_registry
from btcts.apps.operator_ui.components.prediction_warroom_supplemental_widget_registry_preflight import validate_prediction_warroom_supplemental_widget_registry_schema
from btcts.apps.operator_ui.components.prediction_warroom_supplemental_handoff_readiness_summary import build_prediction_warroom_supplemental_handoff_readiness_summary
from btcts.apps.operator_ui.components.prediction_warroom_supplemental_handoff_readiness_widget_groups import build_prediction_warroom_supplemental_handoff_readiness_widget_group_index

REPO_ROOT = Path(__file__).resolve().parents[1]
MODULES = (
    REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/components/prediction_warroom_supplemental_widget_registry.py",
    REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/components/prediction_warroom_supplemental_widget_registry_preflight.py",
    REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/components/prediction_warroom_handoff_catalog_visibility.py",
    REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/components/prediction_warroom_supplemental_handoff_readiness_summary.py",
)
EXPECTED_ORDER = [
    "source_quality_explanation_widgets",
    "prediction_latest_payload_dry_run_status_widget",
    "prediction_latest_payload_loader_authorization_widget",
    "prediction_latest_payload_loader_authorization_registry_summary_widget",
    "prediction_authorization_handoff_status_widget",
    "prediction_supplemental_handoff_readiness_summary_widget",
]
FORBIDDEN_IMPORT_PREFIXES = (
    "btcts.prediction", "btcts.collector_vnext", "btcts.autotrade.execution", "btcts.autotrade.live_shadow", "btcts.processing.l4_consumer_models.shared",
    "streamlit", "requests", "httpx", "ccxt", "pybitflyer", "websocket", "json", "pathlib",
)
FORBIDDEN_TOKENS = (
    "open(", "Path(", "read_text", "read_bytes", "json.load", "json.loads", ".exists(", ".stat(",
    "build_prediction_system_result", "assess_source_quality", "place_order(", "send_order(", "create_order(",
    "append_decision_jsonl", "append_command_ledger_record", "requests.get", "requests.post", "httpx.get", "httpx.post",
    "st.button", "st.form", "persist=True", "actual_file_read_allowed_by_this_contract: bool = True",
    "actual_payload_decode_allowed_by_this_contract: bool = True", "actual_loader_execution_allowed: bool = True",
    "approval_granted_by_this_contract: bool = True", "authorization_granted_by_this_contract: bool = True",
    "would_load_hot_latest_artifacts: bool = True", "would_read_runtime_file: bool = True", "would_write_runtime_artifact: bool = True",
    "would_send_to_broker: bool = True", "broker_execution_requested: bool = True", "mode_apply_requested: bool = True",
    "command_ledger_append_requested: bool = True",
)


def _imports_from(path: Path) -> set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    imports: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imports.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imports.add(node.module)
    return imports


def _assert_safe(payload: dict) -> None:
    assert payload["read_only"] is True
    assert payload["non_executing"] is True
    assert payload["display_only"] is True
    assert payload["render_intent_only"] is True
    assert payload["not_loaded_as_runtime_display_source"] is True
    assert payload.get("approval_granted_by_this_contract", False) is False
    assert payload.get("authorization_granted_by_this_contract", False) is False
    assert payload["actual_loader_execution_allowed"] is False
    assert payload["actual_file_read_allowed_by_this_contract"] is False
    assert payload["actual_payload_decode_allowed_by_this_contract"] is False
    assert payload["would_load_hot_latest_artifacts"] is False
    assert payload["would_read_runtime_file"] is False
    assert payload["would_write_runtime_artifact"] is False
    assert payload["would_send_to_broker"] is False


def test_ps_q7l_static_boundaries_and_markers() -> None:
    for path in MODULES:
        text = path.read_text(encoding="utf-8")
        imports = _imports_from(path)
        for prefix in FORBIDDEN_IMPORT_PREFIXES:
            assert not any(item == prefix or item.startswith(prefix + ".") for item in imports), f"{path}:{prefix}"
        for token in FORBIDDEN_TOKENS:
            assert token not in text, f"{path}:{token}"
    registry_text = MODULES[0].read_text(encoding="utf-8")
    assert "SUPPLEMENTAL_HANDOFF_READINESS_WIDGET_GROUP_VERSION" in registry_text
    assert "include_supplemental_handoff_readiness" in registry_text
    assert "_supplemental_handoff_readiness_summary_stub" in registry_text
    assert "build_prediction_warroom_supplemental_handoff_readiness_widget_group_index" in registry_text
    assert "supplemental_handoff_readiness_widget_contract" in registry_text
    catalog_text = MODULES[2].read_text(encoding="utf-8")
    assert "prediction_warroom_supplemental_handoff_readiness_visibility" in catalog_text


def test_ps_q7l_default_registry_includes_readiness_widget_after_status() -> None:
    registry = build_prediction_warroom_supplemental_widget_registry().to_dict()
    assert registry["supplemental_index_count"] == 6
    assert registry["supplemental_widget_group_count"] == 6
    assert registry["supplemental_widget_group_order"] == EXPECTED_ORDER
    assert len(registry["auto_refresh_groups"]) == 6
    assert len(registry["widget_groups"]) == 6
    widgets = {item["widget_group_id"]: item for item in registry["widget_groups"]}
    readiness = widgets["prediction_supplemental_handoff_readiness_summary_widget"]
    assert readiness["attach_after_widget_group_id"] == "prediction_authorization_handoff_status_widget"
    payload = readiness["payload"]
    assert payload["readiness_state"] == "ready_supplemental_handoff_visible_loader_disabled"
    assert payload["readiness_metrics"]["supplemental_widget_group_count"] == 6
    assert payload["readiness_metrics"]["total_widget_group_count"] == 12
    assert payload["readiness_metrics"]["visibility_group_count"] == 7
    assert payload["readiness_metrics"]["ready_widget_count"] == 6
    assert payload["readiness_metrics"]["blocker_count"] == 0
    assert registry["integration_contract"]["supplemental_handoff_readiness_widget_contract"] == "prediction_warroom_supplemental_handoff_readiness_widget_groups.ps_q7k.v1"
    for item in (registry, registry["boundaries"], registry["integration_contract"], readiness, payload):
        _assert_safe(item)


def test_ps_q7l_preflight_bundle_catalog_and_q7j_defaults_update_to_six_supplementals() -> None:
    registry = build_prediction_warroom_supplemental_widget_registry().to_dict()
    report = validate_prediction_warroom_supplemental_widget_registry_schema(registry).to_dict()
    assert report["valid"] is True
    assert report["supplemental_index_count"] == 6
    assert report["supplemental_widget_group_count"] == 6
    assert "prediction_warroom_supplemental_handoff_readiness_widget_groups.ps_q7k.v1" in report["checked_contracts"]
    bundle = build_prediction_warroom_supplemental_handoff_bundle().to_dict()
    assert bundle["handoff_index"]["supplemental_widget_group_count"] == 6
    assert bundle["handoff_index"]["total_widget_group_count"] == 12
    assert bundle["handoff_index"]["combined_widget_group_order"][-6:] == EXPECTED_ORDER
    entry = build_prediction_warroom_handoff_catalog_visibility_entry().to_dict()
    assert entry["visibility_group_count"] == 7
    assert entry["supplemental_widget_group_count"] == 6
    assert entry["total_widget_group_count"] == 12
    visibility = {item["visibility_group_id"]: item for item in entry["visibility_groups"]}
    assert visibility["prediction_warroom_supplemental_handoff_readiness_visibility"]["widget_group_ids"] == ["prediction_supplemental_handoff_readiness_summary_widget"]
    assert visibility["prediction_warroom_supplemental_handoff_readiness_visibility"]["attach_after_widget_group_id"] == "prediction_authorization_handoff_status_widget"
    summary = build_prediction_warroom_supplemental_handoff_readiness_summary().to_dict()
    assert summary["readiness_metrics"]["total_widget_group_count"] == 12
    assert summary["readiness_metrics"]["visibility_group_count"] == 7
    assert summary["readiness_metrics"]["ready_widget_count"] == 6
    assert [item["widget_group_id"] for item in summary["supplemental_chain_readiness"]] == EXPECTED_ORDER
    for item in (report, bundle, entry, visibility["prediction_warroom_supplemental_handoff_readiness_visibility"], summary):
        _assert_safe(item)


def test_ps_q7l_include_flag_can_disable_readiness_widget_only() -> None:
    registry = build_prediction_warroom_supplemental_widget_registry(include_supplemental_handoff_readiness=False).to_dict()
    assert registry["supplemental_widget_group_order"] == EXPECTED_ORDER[:-1]
    assert registry["supplemental_index_count"] == 5
    only_readiness = build_prediction_warroom_supplemental_widget_registry(
        include_source_quality_explanations=False,
        include_latest_payload_dry_run=False,
        include_latest_payload_loader_authorization=False,
        include_latest_payload_loader_authorization_registry_summary=False,
        include_authorization_handoff_status=False,
    ).to_dict()
    assert only_readiness["supplemental_widget_group_order"] == ["prediction_supplemental_handoff_readiness_summary_widget"]
    assert only_readiness["widget_groups"][0]["payload"]["readiness_state"] != "ready_supplemental_handoff_visible_loader_disabled"
    assert only_readiness["actual_loader_execution_allowed"] is False


def test_ps_q7l_q7k_index_default_tracks_registered_six_widget_summary() -> None:
    index = build_prediction_warroom_supplemental_handoff_readiness_widget_group_index().to_dict()
    payload = index["widget_groups"][0]["payload"]
    assert index["index_version"] == "prediction_warroom_supplemental_handoff_readiness_widget_groups.ps_q7k.v1"
    assert index["attach_after_widget_group_id"] == "prediction_authorization_handoff_status_widget"
    assert payload["readiness_metrics"]["total_widget_group_count"] == 12
    assert payload["readiness_metrics"]["ready_widget_count"] == 6
    assert payload["readiness_metrics"]["blocker_count"] == 0
    assert index["integration_contract"]["does_not_register_into_q6f_registry_in_this_slice"] is True
    for item in (index, index["widget_groups"][0], payload, index["auto_refresh_groups"][0], index["integration_contract"]):
        _assert_safe(item)


def main() -> int:
    test_ps_q7l_static_boundaries_and_markers()
    test_ps_q7l_default_registry_includes_readiness_widget_after_status()
    test_ps_q7l_preflight_bundle_catalog_and_q7j_defaults_update_to_six_supplementals()
    test_ps_q7l_include_flag_can_disable_readiness_widget_only()
    test_ps_q7l_q7k_index_default_tracks_registered_six_widget_summary()
    print("[OK] Prediction System PS-Q7L readiness widget registry registration guard passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
