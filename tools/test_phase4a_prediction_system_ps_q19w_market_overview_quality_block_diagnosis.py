# path: ./tools/test_phase4a_prediction_system_ps_q19w_market_overview_quality_block_diagnosis.py
# desc: Focused guard for PS-Q19W read-only market.overview quality-block diagnosis helper.

from __future__ import annotations

import json
import sys
from pathlib import Path
from tempfile import TemporaryDirectory

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tools.diagnose_market_overview_quality_block_ps_q19w import diagnose_market_overview_quality_block  # noqa: E402

SPEC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q19W_MARKET_OVERVIEW_QUALITY_BLOCK_DIAGNOSIS_2026-06-25.md"
TOOL = REPO_ROOT / "tools/diagnose_market_overview_quality_block_ps_q19w.py"

REQUIRED_MARKERS = (
    "ps_q19w_market_overview_quality_block_diagnosis=true",
    "diagnoses_market_overview_quality_window=true",
    "same_second_mixed_quality_detection=true",
    "read_only_diagnosis=true",
)
FALSE_BOUNDARIES = (
    "runtime_artifact_write_performed_by_diagnosis=false",
    "status_artifact_write_performed_by_diagnosis=false",
    "prediction_artifact_write_performed_by_diagnosis=false",
    "view_artifact_write_performed_by_diagnosis=false",
    "collector_state_write_performed_by_diagnosis=false",
    "scheduler_enabled=false",
    "producer_enabled=false",
    "warroom_ui_trigger_enabled=false",
    "autotrade_trigger_allowed=false",
    "broker_private_api_allowed=false",
    "would_send_to_broker=false",
)


def _row(ts: str, *, trust: str, bucket: str, bid: float, ask: float, semantic: str = "healthy") -> dict:
    return {
        "collector_ts": ts,
        "exchange_ts": None,
        "trust_state": trust,
        "boundary_reason": "profile_rule" if trust != "trusted" else "none",
        "continuity_state": "continuous",
        "interpretation_bucket": bucket,
        "interpretation_reason": "trust_state=quarantined" if trust != "trusted" else "trusted state with continuous series",
        "semantic_observer_status": semantic,
        "best_bid": bid,
        "best_ask": ask,
        "spread": ask - bid,
        "mid_price": (bid + ask) / 2,
    }


def _write_jsonl(path: Path, rows: list[dict]) -> None:
    path.write_text("".join(json.dumps(row, sort_keys=True) + "\n" for row in rows), encoding="utf-8")


def test_spec_declares_diagnosis_boundaries() -> None:
    text = SPEC.read_text(encoding="utf-8-sig")
    for marker in REQUIRED_MARKERS:
        assert marker in text, marker
    for marker in FALSE_BOUNDARIES:
        assert marker in text, marker


def test_detects_same_second_mixed_quality_and_crossed_book() -> None:
    with TemporaryDirectory() as tmp:
        path = Path(tmp) / "part-00001.jsonl"
        rows = [
            _row("2026-06-25T12:04:13Z", trust="trusted", bucket="allow_structural_use", bid=100.0, ask=102.0),
            _row("2026-06-25T12:04:14Z", trust="quarantined", bucket="reanchor_required", bid=105.0, ask=104.0, semantic="broken"),
            _row("2026-06-25T12:04:14Z", trust="trusted", bucket="allow_structural_use", bid=101.0, ask=103.0),
            _row("2026-06-25T12:04:15Z", trust="trusted", bucket="allow_structural_use", bid=102.0, ask=105.0),
        ]
        _write_jsonl(path, rows)
        packet = diagnose_market_overview_quality_block(market_path=path, target_ts="2026-06-25T12:04:14Z", window_sec=5)
    assert packet["ok"] is True
    assert packet["parsed_window_record_count"] == 2
    assert packet["exact_second_record_count"] == 2
    assert packet["exact_second_quality_ok_count"] == 1
    assert packet["exact_second_rejected_count"] == 1
    assert packet["exact_second_mixed_quality"] is True
    assert packet["trust_state_counts"]["quarantined"] == 1
    assert packet["interpretation_bucket_counts"]["reanchor_required"] == 1
    assert packet["spread_summary"]["negative_count"] == 1
    assert packet["crossed_book_count"] == 1
    assert packet["quality_reason_counts"]["market_overview_negative_spread"] == 1
    assert packet["quality_reason_counts"]["market_overview_crossed_book"] == 1
    assert packet["diagnosis"] == "same_second_mixed_quality_reanchor_and_trusted_records"
    assert packet["policy_observation"]["quality_rejected_records_should_not_be_scored"] is True
    assert packet["scheduler_enabled"] is False
    assert packet["warroom_ui_trigger_enabled"] is False
    assert packet["would_send_to_broker"] is False


def test_all_window_records_includes_neighbor_rows() -> None:
    with TemporaryDirectory() as tmp:
        path = Path(tmp) / "part-00001.jsonl"
        _write_jsonl(path, [
            _row("2026-06-25T12:04:13Z", trust="trusted", bucket="allow_structural_use", bid=100.0, ask=102.0),
            _row("2026-06-25T12:04:14Z", trust="quarantined", bucket="reanchor_required", bid=105.0, ask=104.0, semantic="broken"),
            _row("2026-06-25T12:04:15Z", trust="trusted", bucket="allow_structural_use", bid=102.0, ask=105.0),
        ])
        packet = diagnose_market_overview_quality_block(market_path=path, target_ts="2026-06-25T12:04:14Z", window_sec=5, exact_second=False)
    assert packet["ok"] is True
    assert packet["parsed_window_record_count"] == 3
    assert packet["quality_ok_record_count"] == 2
    assert packet["rejected_record_count"] == 1


def test_missing_market_path_blocks() -> None:
    packet = diagnose_market_overview_quality_block(market_path=Path("does_not_exist.jsonl"), target_ts="2026-06-25T12:04:14Z")
    assert packet["ok"] is False
    assert "market_overview_path_missing" in packet["blocked_reasons"]


def test_tool_has_no_write_or_execution_behavior() -> None:
    text = TOOL.read_text(encoding="utf-8")
    forbidden = (
        "append_jsonl(",
        "write_canonical(",
        "write_raw(",
        "place_order(",
        "send_order(",
        "build_ps_q19k_periodic_producer_packet(",
        "build_prediction_warroom_bounded_manual_refresh_runner(",
        "would_send_to_broker: bool = True",
    )
    for token in forbidden:
        assert token not in text, token
    assert "read_only_diagnosis" in text
    assert "runtime_artifact_write_performed_by_diagnosis" in text


if __name__ == "__main__":
    test_spec_declares_diagnosis_boundaries()
    test_detects_same_second_mixed_quality_and_crossed_book()
    test_all_window_records_includes_neighbor_rows()
    test_missing_market_path_blocks()
    test_tool_has_no_write_or_execution_behavior()
    print('{"ok": true}')
