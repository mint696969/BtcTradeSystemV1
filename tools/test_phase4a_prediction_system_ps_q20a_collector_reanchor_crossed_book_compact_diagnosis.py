# path: ./tools/test_phase4a_prediction_system_ps_q20a_collector_reanchor_crossed_book_compact_diagnosis.py
# desc: Focused guard for PS-Q20A compact collector/reanchor/crossed-book diagnosis.

from __future__ import annotations

import json
import sys
from pathlib import Path
from tempfile import TemporaryDirectory

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tools.diagnose_collector_reanchor_crossed_book_ps_q20a import (  # noqa: E402
    HARD_MAX_SAMPLES,
    diagnose_collector_reanchor_crossed_book_ps_q20a,
)

SPEC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q20A_COLLECTOR_REANCHOR_CROSSED_BOOK_COMPACT_DIAGNOSIS_2026-06-26.md"
TOOL = REPO_ROOT / "tools/diagnose_collector_reanchor_crossed_book_ps_q20a.py"

REQUIRED_MARKERS = (
    "ps_q20a_collector_reanchor_crossed_book_compact_diagnosis=true",
    "canonical_timestamp_axis=UTC_ISO8601_Z",
    "ui_display_timezone=Asia/Tokyo_JST",
    "bounded_gpt_friendly_output=true",
    "no_new_giant_files=true",
    "responsibility_separated_from_ps_q19w=true",
)

FALSE_BOUNDARIES = (
    "ps_q19r_scoring_policy_changed=false",
    "runtime_artifact_write_performed_by_diagnosis=false",
    "collector_state_write_performed_by_diagnosis=false",
    "scheduler_enabled=false",
    "producer_enabled=false",
    "warroom_ui_trigger_enabled=false",
    "autotrade_trigger_allowed=false",
    "broker_private_api_allowed=false",
    "would_send_to_broker=false",
)


def _row(
    ts: str,
    *,
    trust: str,
    bucket: str,
    bid: float,
    ask: float,
    boundary: str = "none",
    continuity: str = "continuous",
    semantic: str = "healthy",
    source_series_id: str = "series:A",
    source_stream_session_id: str = "stream:A",
) -> dict:
    return {
        "collector_ts": ts,
        "exchange_ts": None,
        "trust_state": trust,
        "boundary_reason": boundary,
        "continuity_state": continuity,
        "interpretation_bucket": bucket,
        "interpretation_reason": "unit_test",
        "semantic_observer_status": semantic,
        "best_bid": bid,
        "best_ask": ask,
        "spread": ask - bid,
        "mid_price": (bid + ask) / 2,
        "source_series_id": source_series_id,
        "source_stream_session_id": source_stream_session_id,
    }


def _write_jsonl(path: Path, rows: list[dict]) -> None:
    path.write_text("".join(json.dumps(row, sort_keys=True) + "\n" for row in rows), encoding="utf-8")


def test_spec_declares_ps_q20a_boundaries() -> None:
    text = SPEC.read_text(encoding="utf-8-sig")
    for marker in REQUIRED_MARKERS:
        assert marker in text, marker
    for marker in FALSE_BOUNDARIES:
        assert marker in text, marker


def test_compact_diagnosis_normalizes_jst_to_utc_and_detects_recovery() -> None:
    with TemporaryDirectory() as tmp:
        path = Path(tmp) / "part-00001.jsonl"
        _write_jsonl(
            path,
            [
                _row("2026-06-25T12:04:13Z", trust="trusted", bucket="allow_structural_use", bid=100.0, ask=102.0, source_series_id="series:1"),
                _row(
                    "2026-06-25T12:04:14Z",
                    trust="quarantined",
                    bucket="reanchor_required",
                    bid=105.0,
                    ask=104.0,
                    boundary="invalid_diff_attach",
                    semantic="broken",
                    source_series_id="series:1",
                    source_stream_session_id="stream:1",
                ),
                _row("2026-06-25T12:04:14Z", trust="trusted", bucket="allow_structural_use", bid=101.0, ask=103.0, source_series_id="series:2", source_stream_session_id="stream:1"),
                _row("2026-06-25T12:04:15Z", trust="trusted", bucket="allow_structural_use", bid=102.0, ask=105.0, source_series_id="series:2", source_stream_session_id="stream:1"),
            ],
        )
        packet = diagnose_collector_reanchor_crossed_book_ps_q20a(
            market_path=path,
            target_ts="2026-06-25T21:04:14+09:00",
            window_sec=2,
            max_samples=1,
        )
    assert packet["ok"] is True
    assert packet["time_axis"]["canonical_timezone"] == "UTC"
    assert packet["time_axis"]["display_timezone"] == "Asia/Tokyo"
    assert packet["time_axis"]["target_ts_utc"] == "2026-06-25T12:04:14Z"
    assert packet["time_axis"]["target_ts_display"].startswith("2026-06-25T21:04:14+09:00")
    assert packet["scan_summary"]["parsed_window_record_count"] == 4
    assert packet["scan_summary"]["mixed_quality_second_count"] == 1
    assert packet["quality_distribution"]["crossed_book_count"] == 1
    assert packet["quality_distribution"]["negative_spread_count"] == 1
    assert packet["source_distribution"]["source_series_id_counts"]["series:1"] == 2
    assert packet["source_distribution"]["source_series_id_counts"]["series:2"] == 2
    assert packet["bad_to_good_transition"]["transition_state"] == "bad_to_good_recovery_observed"
    assert packet["bad_to_good_transition"]["bad_to_good_row_gap"] == 1
    assert len(packet["samples"]["trusted_rows"]) == 1
    assert len(packet["samples"]["rejected_rows"]) == 1
    assert packet["size_policy"]["bounded_gpt_friendly_output"] is True
    assert packet["size_policy"]["raw_full_window_records_included"] is False
    assert packet["policy_observation"]["ps_q19r_scoring_policy_changed"] is False
    assert packet["would_send_to_broker"] is False


def test_hard_caps_max_samples_and_blocks_missing_path() -> None:
    packet = diagnose_collector_reanchor_crossed_book_ps_q20a(
        market_path=Path("does_not_exist.jsonl"),
        target_ts="2026-06-25T12:04:14Z",
        max_samples=9999,
    )
    assert packet["ok"] is False
    assert "market_overview_path_missing" in packet["blocked_reasons"]
    assert packet["bounded_gpt_friendly_output"] is True
    assert HARD_MAX_SAMPLES == 100


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
    )
    for token in forbidden:
        assert token not in text, token
    assert "HARD_OUTPUT_MAX_BYTES" in text
    assert "HARD_MAX_SAMPLES" in text
    assert "canonical_timezone" in text


if __name__ == "__main__":
    test_spec_declares_ps_q20a_boundaries()
    test_compact_diagnosis_normalizes_jst_to_utc_and_detects_recovery()
    test_hard_caps_max_samples_and_blocks_missing_path()
    test_tool_has_no_execution_or_unbounded_raw_dump_behavior()
    print('{"ok": true}')
