# path: ./tools/test_phase4a_prediction_system_ps_q23l_retire_legacy_widget_latest_refs.py
# desc: Focused guard for PS-Q23L retiring legacy Q18 widget/mapping latest refs.

from __future__ import annotations

import json
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = REPO_ROOT / "btcts_next/src"
for candidate in (REPO_ROOT, SRC_ROOT):
    if str(candidate) not in sys.path:
        sys.path.insert(0, str(candidate))

from btcts.apps.operator_ui.prediction_warroom.sources.latest_prediction_summary_widget_q18ae_candidate_resolver_refresh import (  # noqa: E402
    build_latest_prediction_summary_widget_q18ae_candidate_resolver_refresh_packet,
)
from tools.diagnose_phase4a_prediction_system_ps_q23k_legacy_latest_shrink_readiness_no_write import legacy_reference_inventory  # noqa: E402

SPEC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q23L_RETIRE_LEGACY_WIDGET_LATEST_REFS_2026-06-28.md"
Q18_FILES = [
    REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/prediction_warroom/sources/latest_prediction_summary_widget_q18ae_candidate_resolver_refresh.py",
    REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/prediction_warroom/sources/latest_prediction_summary_widget_q18af_schema_probe.py",
    REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/prediction_warroom/mapping/latest_prediction_summary_widget_q18ag_payload_to_props_mapping_preflight.py",
    REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/prediction_warroom/mapping/latest_prediction_summary_widget_q18ah_render_disabled_packet_builder_validation.py",
]


def test_spec_declares_retirement_contract() -> None:
    text = SPEC.read_text(encoding="utf-8-sig")
    for marker in (
        "ps_q23l_retire_legacy_widget_latest_refs=true",
        "legacy_widget_latest_refs_retired=true",
        "legacy_latest_literal_removed_from_q18_chain=true",
        "q18_chain_runtime_reactivation=false",
        "legacy_latest_shrink_executed=false",
        "runtime_artifact_write_changed=false",
        "scheduler_action_changed=false",
        "broker_autotrade=false",
    ):
        assert marker in text, marker


def test_q18_files_no_longer_reference_legacy_latest_literal() -> None:
    for path in Q18_FILES:
        text = path.read_text(encoding="utf-8")
        assert "latest_prediction_system_result.json" not in text, str(path)
        assert "LATEST_PREDICTION_ARTIFACT_RELATIVE_PATH" not in text, str(path)
        assert "hot://prediction/latest_prediction_system_result.json" not in text, str(path)


def test_q18ae_default_retired_packet_is_no_runtime_no_read() -> None:
    packet = build_latest_prediction_summary_widget_q18ae_candidate_resolver_refresh_packet()
    assert packet["ok"] is False
    assert packet["candidate_resolver_refresh_state"] == "legacy_q18_candidate_resolver_retired_after_manifest_first_default"
    assert packet["legacy_q18_candidate_resolver_retired"] is True
    assert packet["refreshed_candidate_relative_path"] == "prediction/latest_manifest.json"
    assert packet["selected_candidate_source_artifact_ref"] == "hot://prediction/latest_manifest.json"
    assert packet["actual_source_read_invoked"] is False
    assert packet["payload_parse_allowed"] is False
    assert packet["real_prediction_widget_rendering_allowed"] is False
    assert packet["refresh_invocation_allowed"] is False
    assert packet["runtime_artifact_write_allowed"] is False
    assert packet["status_artifact_write_allowed"] is False
    assert packet["autotrade_trigger_allowed"] is False
    assert packet["broker_private_api_allowed"] is False
    assert packet["would_send_to_broker"] is False


def test_q23k_inventory_no_longer_has_legacy_widget_blockers() -> None:
    inv = legacy_reference_inventory()
    assert inv["blocking_legacy_reference_count"] == 0
    assert "legacy_widget_or_mapping_reader" not in inv["blocking_legacy_reference_classes"]


def test_q18_files_have_no_scheduler_writer_or_broker_code() -> None:
    for path in Q18_FILES:
        text = path.read_text(encoding="utf-8")
        for forbidden in (
            "Set-ScheduledTask",
            "Enable-ScheduledTask",
            "Disable-ScheduledTask",
            "Register-ScheduledTask",
            "New-ScheduledTaskTrigger",
            "write_distributed_sidecars_once",
            "run_one_shot_write",
            "send_order(",
            "place_order(",
            ".write_text(",
            ".write_bytes(",
            "os.replace",
        ):
            assert forbidden not in text, f"{path}:{forbidden}"


if __name__ == "__main__":
    test_spec_declares_retirement_contract()
    test_q18_files_no_longer_reference_legacy_latest_literal()
    test_q18ae_default_retired_packet_is_no_runtime_no_read()
    test_q23k_inventory_no_longer_has_legacy_widget_blockers()
    test_q18_files_have_no_scheduler_writer_or_broker_code()
    print(json.dumps({"ok": True}))
