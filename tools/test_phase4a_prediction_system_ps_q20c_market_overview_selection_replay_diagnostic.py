# path: ./tools/test_phase4a_prediction_system_ps_q20c_market_overview_selection_replay_diagnostic.py
# desc: Focused guard for PS-Q20C compact market.overview selection replay diagnostic.

from __future__ import annotations

import json
import sys
from pathlib import Path
from tempfile import TemporaryDirectory

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = REPO_ROOT / "btcts_next" / "src"
for item in (REPO_ROOT, SRC_ROOT):
    if str(item) not in sys.path:
        sys.path.insert(0, str(item))

from tools.replay_market_overview_selection_ps_q20c import (  # noqa: E402
    HARD_MAX_SECOND_SAMPLES,
    replay_market_overview_selection_ps_q20c,
)

SPEC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q20C_MARKET_OVERVIEW_SELECTION_REPLAY_DIAGNOSTIC_2026-06-26.md"
TOOL = REPO_ROOT / "tools/replay_market_overview_selection_ps_q20c.py"

REQUIRED_MARKERS = (
    "ps_q20c_market_overview_selection_replay_diagnostic=true",
    "uses_ps_q20b_consumer_row_selection_contract=true",
    "bounded_gpt_friendly_output=true",
    "no_new_giant_files=true",
    "canonical_timestamp_axis=UTC_ISO8601_Z",
    "ps_q19r_scoring_policy_changed=false",
)

FALSE_BOUNDARIES = (
    "runtime_artifact_write_performed_by_replay=false",
    "collector_state_write_performed_by_replay=false",
    "collector_runtime_behavior_changed=false",
    "scheduler_enabled=false",
    "producer_enabled=false",
    "warroom_ui_trigger_enabled=false",
    "autotrade_trigger_allowed=false",
    "broker_private_api_allowed=false",
    "would_send_to_broker=false",
)


def _row(ts: str, *, trust: str = "trusted", bucket: str = "allow_structural_use", semantic: str = "healthy", bid: float = 100.0, ask: float = 102.0, series: str = "series:1") -> dict:
    return {
        "collector_ts": ts,
        "exchange_ts": None,
        "trust_state": trust,
        "boundary_reason": "none" if trust == "trusted" else "profile_rule",
        "continuity_state": "continuous",
        "interpretation_bucket": bucket,
        "interpretation_reason": "unit",
        "semantic_observer_status": semantic,
        "best_bid": bid,
        "best_ask": ask,
        "spread": ask - bid,
        "mid_price": (bid + ask) / 2,
        "source_series_id": series,
        "source_stream_session_id": "stream:1",
    }


def _write_jsonl(path: Path, rows: list[dict]) -> None:
    path.write_text("".join(json.dumps(row, sort_keys=True) + "\n" for row in rows), encoding="utf-8")


def test_spec_declares_replay_diagnostic_boundaries() -> None:
    text = SPEC.read_text(encoding="utf-8-sig")
    for marker in REQUIRED_MARKERS:
        assert marker in text, marker
    for marker in FALSE_BOUNDARIES:
        assert marker in text, marker


def test_replay_counts_mixed_preferred_and_diagnostic_seconds() -> None:
    with TemporaryDirectory() as tmp:
        path = Path(tmp) / "part-00001.jsonl"
        _write_jsonl(
            path,
            [
                _row("2026-06-25T12:04:13Z", bid=100.0, ask=102.0),
                _row("2026-06-25T12:04:14Z", trust="quarantined", bucket="reanchor_required", semantic="broken", bid=105.0, ask=104.0),
                _row("2026-06-25T12:04:14Z", bid=101.0, ask=103.0),
                _row("2026-06-25T12:04:15Z", trust="quarantined", bucket="reanchor_required", semantic="broken", bid=106.0, ask=105.0),
            ],
        )
        packet = replay_market_overview_selection_ps_q20c(
            market_path=path,
            target_ts="2026-06-25T21:04:14+09:00",
            window_sec=2,
            max_second_samples=1,
        )
    assert packet["ok"] is True
    assert packet["time_axis"]["target_ts_utc"] == "2026-06-25T12:04:14Z"
    assert packet["scan_summary"]["second_count"] == 3
    assert packet["scan_summary"]["preferred_second_count"] == 2
    assert packet["scan_summary"]["fail_closed_second_count"] == 1
    assert packet["scan_summary"]["mixed_preferred_and_diagnostic_second_count"] == 1
    assert packet["scan_summary"]["false_quality_block_candidate_second_count"] == 1
    assert packet["selection_distribution"]["selection_state_counts"]["consumer_preferred"] == 2
    assert packet["selection_distribution"]["selection_state_counts"]["fail_closed"] == 1
    assert packet["selection_distribution"]["row_role_counts"]["consumer_preferred"] == 2
    assert packet["selection_distribution"]["row_role_counts"]["diagnostic_transition"] == 2
    assert len(packet["samples"]["mixed_preferred_and_diagnostic_seconds"]) == 1
    assert len(packet["samples"]["fail_closed_seconds"]) == 1
    assert packet["policy_observation"]["preferred_contract_likely_useful"] is True
    assert packet["policy_observation"]["ps_q19r_scoring_policy_changed"] is False
    assert packet["would_send_to_broker"] is False


def test_missing_path_blocks_and_hard_cap_is_declared() -> None:
    packet = replay_market_overview_selection_ps_q20c(
        market_path=Path("does_not_exist.jsonl"),
        target_ts="2026-06-25T12:04:14Z",
        max_second_samples=9999,
    )
    assert packet["ok"] is False
    assert "market_overview_path_missing" in packet["blocked_reasons"]
    assert packet["bounded_gpt_friendly_output"] is True
    assert HARD_MAX_SECOND_SAMPLES == 100


def test_tool_has_no_execution_or_unbounded_raw_dump_behavior() -> None:
    text = TOOL.read_text(encoding="utf-8")
    forbidden = (
        "send_order(",
        "place_order(",
        "append_decision_jsonl(",
        "append_jsonl(",
        "while True:",
        "raw_full_window_records_included\": True",
        "would_send_to_broker: bool = True",
        "collector_runtime_behavior_changed: bool = True",
        "ps_q19r_scoring_policy_changed: bool = True",
    )
    for token in forbidden:
        assert token not in text, token
    assert "HARD_OUTPUT_MAX_BYTES" in text
    assert "HARD_MAX_SECOND_SAMPLES" in text


if __name__ == "__main__":
    test_spec_declares_replay_diagnostic_boundaries()
    test_replay_counts_mixed_preferred_and_diagnostic_seconds()
    test_missing_path_blocks_and_hard_cap_is_declared()
    test_tool_has_no_execution_or_unbounded_raw_dump_behavior()
    print('{"ok": true}')
