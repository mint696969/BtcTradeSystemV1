# path: ./tools/test_phase4a_prediction_system_ps_q21g_source_mapping_trust_blocker_drilldown.py
# desc: Focused guard for PS-Q21G source mapping / market overview trust blocker drilldown.

from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tools.diagnose_phase4a_prediction_system_ps_q21g_source_mapping_trust_blocker_drilldown import (  # noqa: E402
    DIAGNOSTIC_VERSION,
    build_source_mapping_trust_blocker_drilldown,
)

TOOL = REPO_ROOT / "tools/diagnose_phase4a_prediction_system_ps_q21g_source_mapping_trust_blocker_drilldown.py"
SPEC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q21G_SOURCE_MAPPING_TRUST_BLOCKER_DRILLDOWN_2026-06-26.md"

REQUIRED_MARKERS = (
    "ps_q21g_source_mapping_trust_blocker_drilldown=true",
    "market_overview_trust_state_visible=true",
    "market_overview_interpretation_bucket_visible=true",
    "q9z_probe_readiness_visible=true",
    "q10a_mapping_readiness_visible=true",
    "read_only_diagnostic_only=true",
)

FALSE_BOUNDARIES = (
    "prediction_build_allowed=false",
    "latest_prediction_artifact_export_allowed=false",
    "runtime_enablement_allowed=false",
    "scheduler_enablement_allowed=false",
    "producer_enablement_allowed=false",
    "runtime_artifact_write_allowed=false",
    "status_artifact_write_allowed=false",
    "prediction_artifact_write_allowed=false",
    "view_artifact_write_allowed=false",
    "autotrade_trigger_allowed=false",
    "broker_private_api_allowed=false",
    "would_send_to_broker=false",
)


def _fixture_packet() -> dict:
    return {
        "runner_state": "source_mapping_probe_runner_blocked",
        "hot_latest_root_hint": r"D:\btc_ts_hot",
        "blocker_count": 2,
        "blocked_reasons": ["source_mapping_runner_not_ready_for_prediction_system_result_builder"],
        "warning_reasons": ["orderbook_snapshot_missing_exchange_ts_context_only"],
        "q9z_probe_packet": {
            "probe_state": "hot_source_probe_blocked",
            "ready_for_future_prediction_source_mapping": False,
            "blocked_reasons": ["market_overview_trust_state_not_trusted", "market_overview_interpretation_bucket_not_allow_structural_use"],
            "source_summaries": [
                {
                    "source_role": "market_overview",
                    "source_state": "source_probe_blocked",
                    "latest_part_path": "data\\market_state\\...\\part-00001.jsonl",
                    "latest_date_partition": "date=2026-06-26",
                    "parsed_row_count": 8,
                    "latest_collector_ts": "2026-06-26T03:45:57Z",
                    "latest_event_ts": "2026-06-26T03:45:57Z",
                    "latest_market_uid": "bitflyer.fx.FX_BTC_JPY",
                    "latest_trust_state": "untrusted",
                    "latest_continuity_state": "continuous",
                    "latest_interpretation_bucket": "blocked_for_prediction",
                    "overview_mid_price": 9630000.0,
                    "overview_spread": 402.0,
                    "blocker_reasons": ["market_overview_trust_state_not_trusted", "market_overview_interpretation_bucket_not_allow_structural_use"],
                },
                {"source_role": "market_trade", "source_state": "source_probe_ready", "parsed_row_count": 8, "latest_event_ts": "2026-06-26T03:45:57Z", "trade_price_sample": [9630000.0]},
                {"source_role": "orderbook_snapshot", "source_state": "source_probe_ready", "parsed_row_count": 2, "latest_event_ts": "2026-06-26T03:45:57Z", "orderbook_bid_level_count": 10, "orderbook_ask_level_count": 10},
            ],
        },
        "q10a_preflight_packet": {
            "contract_state": "source_mapping_preflight_blocked",
            "ready_for_future_prediction_system_result_builder": False,
            "blocked_reasons": ["ps_q9z_probe_not_ready_for_future_prediction_source_mapping"],
        },
    }


def test_spec_declares_drilldown_and_safety_boundaries() -> None:
    text = SPEC.read_text(encoding="utf-8-sig")
    for marker in REQUIRED_MARKERS:
        assert marker in text, marker
    for marker in FALSE_BOUNDARIES:
        assert marker in text, marker


def test_drilldown_identifies_market_overview_trust_as_primary_root_cause() -> None:
    result = build_source_mapping_trust_blocker_drilldown(probe_runner_packet=_fixture_packet())
    assert result["ok"] is True
    assert result["diagnostic_version"] == DIAGNOSTIC_VERSION
    assert result["market_overview_trust_state_not_trusted"] is True
    assert result["market_overview_interpretation_bucket_not_allow_structural_use"] is True
    assert result["ps_q9z_probe_not_ready_for_future_prediction_source_mapping"] is True
    assert result["source_mapping_runner_not_ready_for_prediction_system_result_builder"] is True
    assert result["primary_root_cause"] == "market_overview_not_trusted_for_prediction_source_mapping"
    assert result["next_focus"] == "market_overview_row_selection_or_trust_contract_repair_read_only"
    assert result["market_overview"]["latest_trust_state"] == "untrusted"
    assert result["market_overview"]["latest_interpretation_bucket"] == "blocked_for_prediction"
    assert "market_overview_trust_state_not_trusted" in result["target_blockers_present"]
    assert result["read_only_diagnostic_only"] is True
    assert result["prediction_build_allowed"] is False
    assert result["latest_prediction_artifact_export_allowed"] is False
    assert result["runtime_artifact_write_allowed"] is False
    assert result["autotrade_trigger_allowed"] is False
    assert result["broker_private_api_allowed"] is False
    assert result["would_send_to_broker"] is False


def test_tool_is_stdout_only_bounded_hot_read_no_write_or_enablement() -> None:
    text = TOOL.read_text(encoding="utf-8")
    forbidden = (
        "write_text(",
        "open(\"w",
        "subprocess.run(",
        "allow_prediction_build=True",
        "execute_export=True",
        "allow_runtime_artifact_write=True",
        "scheduler_enabled: bool = True",
        "producer_enabled: bool = True",
        "send_order(",
        "place_order(",
    )
    for token in forbidden:
        assert token not in text, token
    assert "build_prediction_warroom_source_mapping_probe_runner" in text
    assert "operator_acknowledged=True" in text
    assert "allow_actual_read=True" in text
    assert "BTCTS_HOT_ROOT" in text
    assert "BTC_TS_HOT_ROOT" in text
    assert "print(json.dumps" in text


if __name__ == "__main__":
    test_spec_declares_drilldown_and_safety_boundaries()
    test_drilldown_identifies_market_overview_trust_as_primary_root_cause()
    test_tool_is_stdout_only_bounded_hot_read_no_write_or_enablement()
    print('{"ok": true}')
