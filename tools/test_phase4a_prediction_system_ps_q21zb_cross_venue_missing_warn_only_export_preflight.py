# path: ./tools/test_phase4a_prediction_system_ps_q21zb_cross_venue_missing_warn_only_export_preflight.py
# desc: Focused guard for PS-Q21ZB cross-venue missing warn-only payload/export-preflight behavior. No writes or scheduler/trading behavior.

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC = REPO_ROOT / "btcts_next" / "src"
for candidate in (REPO_ROOT, SRC):
    if str(candidate) not in sys.path:
        sys.path.insert(0, str(candidate))

from btcts.apps.operator_ui.components.prediction_warroom_prediction_system_result_builder_runner import (  # noqa: E402
    build_prediction_warroom_prediction_system_result_builder_runner,
)
from btcts.apps.operator_ui.components.prediction_warroom_latest_payload_export_preflight_bridge import (  # noqa: E402
    build_prediction_warroom_latest_payload_export_preflight_bridge,
)

SPEC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q21ZB_CROSS_VENUE_MISSING_WARN_ONLY_EXPORT_PREFLIGHT_2026-06-27.md"
RULES = REPO_ROOT / "btcts_next/src/btcts/prediction/rule_based_v0.py"
HOT_ROOT = r"D:\btc_ts_hot"


def test_spec_declares_warn_only_boundary() -> None:
    text = SPEC.read_text(encoding="utf-8-sig")
    required = (
        "ps_q21zb_cross_venue_missing_warn_only_export_preflight=true",
        "cross_venue_summary_missing_or_blocked_is_warning_not_payload_blocker=true",
        "no_D_hot_write_by_this_slice",
        "no_scheduler_enablement",
        "no_AutoTrade",
        "no_broker_private_api",
        "would_send_to_broker=false",
    )
    for marker in required:
        assert marker in text, marker


def test_rule_based_cross_venue_missing_is_not_emitted_as_hard_blocker() -> None:
    text = RULES.read_text(encoding="utf-8")
    assert 'return "unknown", None, tuple(), ("cross_venue_summary_missing_or_blocked",), tuple(), {}' not in text
    assert 'blockers.append("cross_venue_summary_missing_or_blocked")' not in text
    assert 'warnings.append("cross_venue_summary_missing_or_blocked")' in text
    assert 'return "unknown", 0.0, tuple(), tuple(), ("cross_venue_summary_missing_or_blocked",)' in text


def test_builder_payload_has_no_cross_venue_hard_blocker_after_q21zb() -> None:
    packet = build_prediction_warroom_prediction_system_result_builder_runner(
        hot_latest_root_hint=HOT_ROOT,
        operator_acknowledged=True,
        allow_actual_read=True,
        allow_prediction_build=True,
        allow_guard_test_root=False,
        requested_latest_payload_export=False,
        requested_runtime_write=False,
        requested_warroom_ui_trigger=False,
        requested_approval_or_ledger_or_autotrade_or_broker=False,
    ).to_dict()
    payload = packet.get("prediction_result_payload") if isinstance(packet.get("prediction_result_payload"), dict) else {}
    blockers = [str(item) for item in payload.get("blockers", []) if item] if isinstance(payload.get("blockers", []), list) else []
    warnings = [str(item) for item in payload.get("warnings", []) if item] if isinstance(payload.get("warnings", []), list) else []
    assert "cross_venue_summary_missing_or_blocked" not in blockers
    assert packet["prediction_system_result_built_by_this_runner"] is True
    assert packet["output_count"] == 110
    assert packet["latest_prediction_artifact_exported_by_this_runner"] is False
    assert packet["runtime_artifact_write_performed_by_this_runner"] is False
    assert packet["would_send_to_broker"] is False
    assert "cross_venue_summary_missing_or_blocked" in warnings or "cross_venue_missing_for_breakout_confirmation" in warnings


def test_export_preflight_reaches_contract_without_d_hot_write() -> None:
    bridge = build_prediction_warroom_latest_payload_export_preflight_bridge(
        hot_latest_root_hint=HOT_ROOT,
        operator_acknowledged=True,
        allow_actual_read=True,
        allow_prediction_build=True,
        allow_export_preflight=True,
        allow_guard_test_root=False,
        requested_latest_payload_export=False,
        requested_runtime_write=False,
        requested_warroom_ui_trigger=False,
        requested_approval_or_ledger_or_autotrade_or_broker=False,
    ).to_dict()
    blockers = [str(item) for item in bridge.get("blocked_reasons", []) if item]
    assert "prediction_system_result_builder_runner_not_ready_for_export_preflight" not in blockers
    assert bridge["prediction_result_payload_present"] is True
    assert bridge["latest_prediction_artifact_exported_by_this_bridge"] is False
    assert bridge["runtime_artifact_write_performed_by_this_bridge"] is False
    assert bridge["would_send_to_broker"] is False


def test_no_write_or_scheduler_or_broker_tokens_added() -> None:
    text = RULES.read_text(encoding="utf-8")
    forbidden = (
        "write_text(",
        "open(\"w",
        "subprocess.run(",
        "Enable-ScheduledTask",
        "New-ScheduledTaskTrigger",
        "send_order(",
        "place_order(",
        "would_send_to_broker: bool = True",
    )
    for token in forbidden:
        assert token not in text, token


if __name__ == "__main__":
    test_spec_declares_warn_only_boundary()
    test_rule_based_cross_venue_missing_is_not_emitted_as_hard_blocker()
    test_builder_payload_has_no_cross_venue_hard_blocker_after_q21zb()
    test_export_preflight_reaches_contract_without_d_hot_write()
    test_no_write_or_scheduler_or_broker_tokens_added()
    print(json.dumps({"ok": True}, ensure_ascii=False))
