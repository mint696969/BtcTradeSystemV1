# path: ./tools/test_phase4a_prediction_system_ps_q19k_non_ui_periodic_producer_and_source_quality_gap_audit.py
# desc: Focused guard for PS-Q19K non-UI periodic producer and source-quality gap audit.

from __future__ import annotations

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tools.check_prediction_source_quality_gaps_ps_q19k import build_prediction_source_quality_gap_audit_packet  # noqa: E402
from tools.run_prediction_warroom_periodic_producer_ps_q19k import (  # noqa: E402
    PS_Q19K_PERIODIC_PRODUCER_ACK,
    build_ps_q19k_periodic_producer_packet,
)

SPEC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q19K_NON_UI_PERIODIC_PRODUCER_AND_SOURCE_QUALITY_GAP_AUDIT_2026-06-25.md"
PERIODIC_TOOL = REPO_ROOT / "tools/run_prediction_warroom_periodic_producer_ps_q19k.py"
GAP_TOOL = REPO_ROOT / "tools/check_prediction_source_quality_gaps_ps_q19k.py"

REQUIRED_MARKERS = (
    "ps_q19k_non_ui_periodic_producer_and_source_quality_gap_audit=true",
    "periodic_producer_entrypoint_added=true",
    "source_quality_gap_audit_added=true",
    "q16d_bounded_refresh_runner_reused=true",
    "explicit_ack_required=true",
    "PS-Q19L_SOURCE_QUALITY_INPUT_REPAIR",
)

FALSE_BOUNDARIES = (
    "scheduler_install_performed=false",
    "scheduler_enabled=false",
    "scheduled_loop_enabled=false",
    "warroom_ui_trigger_enabled=false",
    "ui_triggered_runner_execution=false",
    "autotrade_trigger_allowed=false",
    "broker_private_api_allowed=false",
    "parameter_apply_allowed=false",
    "parameter_staging_write_allowed=false",
    "ledger_append_allowed=false",
    "would_send_to_broker=false",
)


def _fake_export_runner(**kwargs):
    root = Path(str(kwargs["hot_latest_root_hint"]))
    target = root / "prediction" / "latest_prediction_system_result.json"
    target.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "read_only": True,
        "non_executing": True,
        "broker_execution_requested": False,
        "command_ledger_append_requested": False,
        "approval_append_requested": False,
        "forecast_batch": {
            "generated_at": "2026-06-25T00:00:00Z",
            "record_count": 1,
            "records": [
                {
                    "family": "market_regime",
                    "horizon_sec": 15,
                    "read_only": True,
                    "non_executing": True,
                    "would_send_to_broker": False,
                    "would_write_runtime_artifact": False,
                    "would_append_ledger": False,
                }
            ],
        },
    }
    target.write_text(json.dumps(payload), encoding="utf-8")
    return {
        "target_file_written": True,
        "target_artifact_path": str(target),
        "target_file_size_bytes": target.stat().st_size,
        "prediction_run_id": "fake-run",
        "generated_at": "2026-06-25T00:00:00Z",
        "exported_at": "2026-06-25T00:00:01Z",
        "blocked_reasons": [],
        "warning_reasons": [],
    }


def test_spec_declares_periodic_producer_and_gap_audit_boundaries() -> None:
    text = SPEC.read_text(encoding="utf-8-sig")
    for marker in REQUIRED_MARKERS:
        assert marker in text, marker
    for marker in FALSE_BOUNDARIES:
        assert marker in text, marker


def test_periodic_default_is_dry_run_no_write() -> None:
    packet = build_ps_q19k_periodic_producer_packet(hot_latest_root_hint="D:/btc_ts_hot")
    assert packet["ok"] is True
    assert packet["request_state"] == "dry_run_no_write"
    assert packet["cycle_count"] == 0
    assert packet["latest_prediction_artifact_written_count"] == 0
    assert packet["scheduler_install_performed"] is False
    assert packet["scheduler_enabled"] is False
    assert packet["scheduled_loop_enabled"] is False
    assert packet["autotrade_trigger_allowed"] is False
    assert packet["broker_private_api_allowed"] is False
    assert packet["would_send_to_broker"] is False


def test_periodic_requires_exact_ack() -> None:
    packet = build_ps_q19k_periodic_producer_packet(
        hot_latest_root_hint="D:/btc_ts_hot",
        execute_periodic_producer=True,
        ack="WRONG",
    )
    assert packet["ok"] is False
    assert "explicit_ps_q19k_periodic_producer_ack_required" in packet["blocked_reasons"]
    assert packet["cycle_count"] == 0


def test_periodic_runs_bounded_cycles_with_fake_export(tmp_path: Path) -> None:
    slept: list[float] = []
    packet = build_ps_q19k_periodic_producer_packet(
        hot_latest_root_hint=str(tmp_path),
        execute_periodic_producer=True,
        ack=PS_Q19K_PERIODIC_PRODUCER_ACK,
        max_cycles=2,
        interval_sec=0,
        allow_guard_test_root=True,
        actual_export_runner=_fake_export_runner,
        sleep_func=lambda sec: slept.append(sec),
    )
    assert packet["ok"] is True
    assert packet["request_state"] == "periodic_producer_completed_bounded_cycles"
    assert packet["cycle_count"] == 2
    assert packet["latest_prediction_artifact_written_count"] == 2
    assert packet["status_artifact_written_count"] == 2
    assert slept == [0.0]
    assert (tmp_path / "prediction" / "latest_prediction_system_result.json").exists()
    assert (tmp_path / "prediction" / "status" / "non_ui_scheduled_producer_status.json").exists()
    assert packet["scheduler_install_performed"] is False
    assert packet["warroom_ui_trigger_enabled"] is False
    assert packet["autotrade_trigger_allowed"] is False
    assert packet["broker_private_api_allowed"] is False
    assert packet["would_send_to_broker"] is False


def test_periodic_stop_file_stops_before_first_cycle(tmp_path: Path) -> None:
    stop = tmp_path / "prediction" / "status" / "stop_periodic_producer_ps_q19k.flag"
    stop.parent.mkdir(parents=True, exist_ok=True)
    stop.write_text("stop", encoding="utf-8")
    packet = build_ps_q19k_periodic_producer_packet(
        hot_latest_root_hint=str(tmp_path),
        execute_periodic_producer=True,
        ack=PS_Q19K_PERIODIC_PRODUCER_ACK,
        max_cycles=2,
        interval_sec=0,
        allow_guard_test_root=True,
        actual_export_runner=_fake_export_runner,
        sleep_func=lambda sec: None,
    )
    assert packet["ok"] is True
    assert packet["stopped_by_stop_file"] is True
    assert packet["cycle_count"] == 0


def test_gap_audit_summarizes_missing_sources_warnings_and_labels() -> None:
    payload = {
        "forecast_batch": {
            "records": [
                {
                    "family": "liquidity_execution_quality",
                    "horizon_sec": 15,
                    "primary_label": "poor_liquidity",
                    "warnings": ["tier0_source_quality_gate_not_passed", "context_evidence_profile_minimum_sources_missing"],
                    "signal_strength_cap_reasons": ["tier0_source_quality_missing_or_degraded"],
                    "drivers": ["range_boundary_visible"],
                    "gpt_review_digest": {
                        "context_evidence_profiles": [
                            {"missing_minimum_required_sources": ["bitflyer_board_summary", "bitflyer_trades"]}
                        ]
                    },
                }
            ]
        }
    }
    packet = build_prediction_source_quality_gap_audit_packet(payload=payload, source_path="fixture")
    assert packet["ok"] is True
    assert packet["priority_gap_summary"]["tier0_source_quality_warnings_present"] is True
    assert packet["priority_gap_summary"]["missing_bitflyer_board_summary"] == 1
    assert packet["priority_gap_summary"]["missing_bitflyer_trades"] == 1
    assert packet["top_labels"][0]["token"] == "poor_liquidity"
    assert packet["runtime_artifact_write_performed_by_gap_audit"] is False
    assert packet["would_send_to_broker"] is False


def test_tool_text_declares_no_scheduler_or_broker_paths() -> None:
    combined = PERIODIC_TOOL.read_text(encoding="utf-8") + "\n" + GAP_TOOL.read_text(encoding="utf-8")
    assert "scheduler_install_performed" in combined
    assert "warroom_ui_trigger_enabled" in combined
    assert "broker_private_api_allowed" in combined
    assert "would_send_to_broker" in combined


if __name__ == "__main__":
    test_spec_declares_periodic_producer_and_gap_audit_boundaries()
    test_periodic_default_is_dry_run_no_write()
    test_periodic_requires_exact_ack()
    from tempfile import TemporaryDirectory
    with TemporaryDirectory() as d:
        test_periodic_runs_bounded_cycles_with_fake_export(Path(d))
    with TemporaryDirectory() as d:
        test_periodic_stop_file_stops_before_first_cycle(Path(d))
    test_gap_audit_summarizes_missing_sources_warnings_and_labels()
    test_tool_text_declares_no_scheduler_or_broker_paths()
    print('{"ok": true}')
