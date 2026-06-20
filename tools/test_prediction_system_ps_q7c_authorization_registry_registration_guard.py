# path: ./tools/test_prediction_system_ps_q7c_authorization_registry_registration_guard.py
# desc: Guard for PS-Q7C authorization widget registration in supplemental registry/catalog path. Registration only; no approval write, runtime reads, payload decode, rendering, Collector, AutoTrade, or broker behavior.

from __future__ import annotations

import ast
from pathlib import Path

from _btcts_bootstrap import ensure_btcts_on_syspath
ensure_btcts_on_syspath()

from btcts.apps.operator_ui.components.prediction_warroom_handoff_catalog_visibility import build_prediction_warroom_handoff_catalog_visibility_entry
from btcts.apps.operator_ui.components.prediction_warroom_latest_payload_loader_permission_contract import build_prediction_warroom_latest_payload_loader_permission_contract
from btcts.apps.operator_ui.components.prediction_warroom_supplemental_handoff_bundle import build_prediction_warroom_supplemental_handoff_bundle
from btcts.apps.operator_ui.components.prediction_warroom_supplemental_widget_registry import build_prediction_warroom_supplemental_widget_registry
from btcts.apps.operator_ui.components.prediction_warroom_supplemental_widget_registry_preflight import validate_prediction_warroom_supplemental_widget_registry_schema
from btcts.apps.operator_ui.components.prediction_warroom_sample_packets import build_prediction_warroom_sample_display_packet

REPO_ROOT = Path(__file__).resolve().parents[1]
MODULES = (
    REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/components/prediction_warroom_supplemental_widget_registry.py",
    REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/components/prediction_warroom_supplemental_widget_registry_preflight.py",
    REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/components/prediction_warroom_supplemental_handoff_bundle.py",
    REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/components/prediction_warroom_handoff_catalog_visibility.py",
)
FORBIDDEN_IMPORT_PREFIXES = (
    "btcts.prediction",
    "btcts.collector_vnext",
    "btcts.autotrade.execution",
    "btcts.autotrade.live_shadow",
    "btcts.processing.l4_consumer_models.shared",
    "streamlit",
    "requests",
    "httpx",
    "ccxt",
    "pybitflyer",
    "websocket",
    "json",
    "pathlib",
)
FORBIDDEN_TOKENS = (
    "open(",
    "Path(",
    "read_text",
    "read_bytes",
    "json.load",
    "json.loads",
    ".exists(",
    ".stat(",
    "build_prediction_system_result",
    "assess_source_quality",
    "place_order(",
    "send_order(",
    "create_order(",
    "append_decision_jsonl",
    "append_command_ledger_record",
    "requests.get",
    "requests.post",
    "httpx.get",
    "httpx.post",
    "st.button",
    "st.form",
    "persist=True",
    "actual_file_read_allowed_by_this_contract: bool = True",
    "actual_payload_decode_allowed_by_this_contract: bool = True",
    "actual_loader_execution_allowed: bool = True",
    "approval_granted_by_this_contract: bool = True",
    "authorization_granted_by_this_contract: bool = True",
    "would_load_hot_latest_artifacts: bool = True",
    "would_read_runtime_file: bool = True",
    "would_write_runtime_artifact: bool = True",
    "would_send_to_broker: bool = True",
    "broker_execution_requested: bool = True",
    "mode_apply_requested: bool = True",
    "command_ledger_append_requested: bool = True",
)
EXPECTED_ORDER = [
    "source_quality_explanation_widgets",
    "prediction_latest_payload_dry_run_status_widget",
    "prediction_latest_payload_loader_authorization_widget",
    "prediction_latest_payload_loader_authorization_registry_summary_widget",
    "prediction_authorization_handoff_status_widget",
    "prediction_supplemental_handoff_readiness_summary_widget",
]


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


def test_ps_q7c_static_boundaries_and_markers() -> None:
    for path in MODULES:
        text = path.read_text(encoding="utf-8")
        imports = _imports_from(path)
        for prefix in FORBIDDEN_IMPORT_PREFIXES:
            assert not any(item == prefix or item.startswith(prefix + ".") for item in imports), f"{path}:{prefix}"
        for token in FORBIDDEN_TOKENS:
            assert token not in text, f"{path}:{token}"
    registry_text = MODULES[0].read_text(encoding="utf-8")
    assert "AUTHORIZATION_WIDGET_GROUP_VERSION" in registry_text
    assert "include_latest_payload_loader_authorization" in registry_text
    preflight_text = MODULES[1].read_text(encoding="utf-8")
    assert "prediction_latest_payload_loader_authorization_widget" in preflight_text
    catalog_text = MODULES[3].read_text(encoding="utf-8")
    assert "prediction_warroom_loader_authorization_visibility" in catalog_text


def test_ps_q7c_default_registry_includes_authorization_widget() -> None:
    registry = build_prediction_warroom_supplemental_widget_registry(display_packet=build_prediction_warroom_sample_display_packet()).to_dict()
    assert registry["supplemental_index_count"] == 6
    assert registry["supplemental_widget_group_count"] == 6
    assert registry["supplemental_widget_group_order"] == EXPECTED_ORDER
    assert len(registry["auto_refresh_groups"]) == 6
    assert len(registry["widget_groups"]) == 6
    widgets = {item["widget_group_id"]: item for item in registry["widget_groups"]}
    assert widgets["prediction_latest_payload_loader_authorization_widget"]["attach_after_widget_group_id"] == "prediction_latest_payload_dry_run_status_widget"
    assert widgets["prediction_latest_payload_loader_authorization_widget"]["payload"]["status_badge"]["badge_kind"] == "review_ready_loader_disabled"
    for payload in (registry, registry["boundaries"], registry["integration_contract"], *registry["widget_groups"], *registry["auto_refresh_groups"]):
        _assert_safe(payload)
    assert registry["integration_contract"]["latest_payload_loader_authorization_widget_contract"] == "prediction_warroom_latest_payload_loader_authorization_widget_groups.ps_q7b.v1"


def test_ps_q7c_include_flag_can_disable_authorization_widget() -> None:
    registry = build_prediction_warroom_supplemental_widget_registry(
        display_packet=build_prediction_warroom_sample_display_packet(),
        include_latest_payload_loader_authorization=False,
        include_latest_payload_loader_authorization_registry_summary=False,
        include_authorization_handoff_status=False,
        include_supplemental_handoff_readiness=False,
    ).to_dict()
    assert registry["supplemental_widget_group_order"] == ["source_quality_explanation_widgets", "prediction_latest_payload_dry_run_status_widget"]
    assert registry["supplemental_index_count"] == 2
    assert registry["supplemental_widget_group_count"] == 2


def test_ps_q7c_preflight_accepts_authorization_widget_and_blocks_bad_attach() -> None:
    registry = build_prediction_warroom_supplemental_widget_registry(display_packet=build_prediction_warroom_sample_display_packet()).to_dict()
    report = validate_prediction_warroom_supplemental_widget_registry_schema(registry).to_dict()
    assert report["valid"] is True
    assert report["supplemental_index_count"] == 6
    assert report["supplemental_widget_group_count"] == 6
    assert "prediction_warroom_latest_payload_loader_authorization_widget_groups.ps_q7b.v1" in report["checked_contracts"]
    registry["widget_groups"][2]["attach_after_widget_group_id"] = "warning_refresh_widget"
    blocked = validate_prediction_warroom_supplemental_widget_registry_schema(registry).to_dict()
    assert blocked["valid"] is False
    assert "unexpected_attach_after_widget_group_id" in {item["issue_code"] for item in blocked["issues"]}


def test_ps_q7c_handoff_bundle_and_catalog_counts_update_after_q7l() -> None:
    bundle = build_prediction_warroom_supplemental_handoff_bundle().to_dict()
    assert bundle["handoff_index"]["base_widget_group_count"] == 6
    assert bundle["handoff_index"]["supplemental_widget_group_count"] == 6
    assert bundle["handoff_index"]["total_widget_group_count"] == 12
    assert bundle["handoff_index"]["combined_widget_group_order"][-6:] == EXPECTED_ORDER
    entry = build_prediction_warroom_handoff_catalog_visibility_entry().to_dict()
    assert entry["visibility_group_count"] == 7
    assert entry["supplemental_widget_group_count"] == 6
    assert entry["total_widget_group_count"] == 12
    visibility = {item["visibility_group_id"]: item for item in entry["visibility_groups"]}
    assert visibility["prediction_warroom_loader_authorization_visibility"]["widget_group_ids"] == ["prediction_latest_payload_loader_authorization_widget"]
    assert visibility["prediction_warroom_loader_authorization_visibility"]["attach_after_widget_group_id"] == "prediction_latest_payload_dry_run_status_widget"
    for payload in (bundle, entry, visibility["prediction_warroom_loader_authorization_visibility"]):
        _assert_safe(payload)


def test_ps_q7c_unsafe_permission_contract_reaches_widget_as_blocked_but_safe() -> None:
    permission = build_prediction_warroom_latest_payload_loader_permission_contract().to_dict()
    permission["actual_file_read_allowed_by_this_contract"] = True
    registry = build_prediction_warroom_supplemental_widget_registry(
        display_packet=build_prediction_warroom_sample_display_packet(),
        latest_payload_loader_permission_contract=permission,
    ).to_dict()
    widget = {item["widget_group_id"]: item for item in registry["widget_groups"]}["prediction_latest_payload_loader_authorization_widget"]
    assert widget["payload"]["authorization_request_state"] == "blocked_permission_contract_unsafe"
    assert widget["payload"]["status_badge"]["badge_kind"] == "blocked_loader_disabled"
    _assert_safe(widget)
    _assert_safe(widget["payload"])


def main() -> int:
    test_ps_q7c_static_boundaries_and_markers()
    test_ps_q7c_default_registry_includes_authorization_widget()
    test_ps_q7c_include_flag_can_disable_authorization_widget()
    test_ps_q7c_preflight_accepts_authorization_widget_and_blocks_bad_attach()
    test_ps_q7c_handoff_bundle_and_catalog_counts_update_after_q7l()
    test_ps_q7c_unsafe_permission_contract_reaches_widget_as_blocked_but_safe()
    print("[OK] Prediction System PS-Q7C authorization registry registration guard passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
