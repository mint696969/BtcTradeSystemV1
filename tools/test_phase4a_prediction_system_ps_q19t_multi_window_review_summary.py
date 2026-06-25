# path: ./tools/test_phase4a_prediction_system_ps_q19t_multi_window_review_summary.py
# desc: Focused guard for PS-Q19T read-only multi-window PS-Q19R review summary helper.

from __future__ import annotations

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tools.summarize_prediction_actual_market_reviews_ps_q19t import (  # noqa: E402
    load_and_summarize_review_files,
    summarize_prediction_actual_market_reviews,
)

SPEC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q19T_MULTI_WINDOW_REVIEW_SUMMARY_2026-06-25.md"
TOOL = REPO_ROOT / "tools/summarize_prediction_actual_market_reviews_ps_q19t.py"

REQUIRED_MARKERS = (
    "ps_q19t_multi_window_review_summary=true",
    "summarizes_ps_q19r_review_json=true",
    "read_only_summary=true",
)
FALSE_BOUNDARIES = (
    "runtime_artifact_write_performed_by_summary=false",
    "status_artifact_write_performed_by_summary=false",
    "prediction_artifact_write_performed_by_summary=false",
    "view_artifact_write_performed_by_summary=false",
    "scheduler_enabled=false",
    "producer_enabled=false",
    "warroom_ui_trigger_enabled=false",
    "autotrade_trigger_allowed=false",
    "broker_private_api_allowed=false",
    "would_send_to_broker=false",
)


def _review(generated_at: str, directions: dict[int, str], returns: dict[int, float]) -> dict:
    rows = []
    actual_by_horizon = {}
    for horizon, direction in directions.items():
        actual_by_horizon[str(horizon)] = {
            "available": True,
            "actual_quality_ok": True,
            "actual_quality_reasons": [],
            "realized_direction": direction,
            "return_bps": returns[horizon],
        }
        rows.append({"family": "market_regime", "horizon_sec": horizon, "alignment_hint": "range_or_neutral_match" if direction == "flat" else "range_or_neutral_broken", "realized_direction": direction, "actual_available": True})
        rows.append({"family": "trend_bias", "horizon_sec": horizon, "alignment_hint": "direction_match" if direction == "down" else "direction_mismatch", "realized_direction": direction, "actual_available": True})
    alignment: dict[str, int] = {}
    for row in rows:
        alignment[row["alignment_hint"]] = alignment.get(row["alignment_hint"], 0) + 1
    return {
        "ok": True,
        "prediction_generated_at": generated_at,
        "actual_by_horizon": actual_by_horizon,
        "review_rows": rows,
        "review_row_count": len(rows),
        "actual_available_row_count": len(rows),
        "alignment_summary": alignment,
        "blocked_reasons": [],
        "warning_reasons": [],
        "read_only_review": True,
        "would_send_to_broker": False,
    }


def test_spec_declares_read_only_summary_boundaries() -> None:
    text = SPEC.read_text(encoding="utf-8-sig")
    for marker in REQUIRED_MARKERS:
        assert marker in text, marker
    for marker in FALSE_BOUNDARIES:
        assert marker in text, marker


def test_multi_window_summary_aggregates_horizons_families_and_alignment() -> None:
    a = _review("2026-06-25T07:33:22Z", {15: "flat", 60: "flat", 300: "up", 600: "up", 900: "up"}, {15: -1.6, 60: 1.4, 300: 5.2, 600: 10.8, 900: 10.4})
    b = _review("2026-06-25T09:16:39Z", {15: "flat", 60: "flat", 300: "down", 600: "down", 900: "down"}, {15: 0.6, 60: 1.4, 300: -3.9, 600: -16.0, 900: -9.1})
    summary = summarize_prediction_actual_market_reviews([a, b], source_paths=["a.json", "b.json"])
    assert summary["ok"] is True
    assert summary["source_review_count"] == 2
    assert summary["review_row_total"] == 20
    assert summary["actual_available_row_total"] == 20
    assert summary["actual_available_ratio"] == 1.0
    assert summary["horizon_direction_summary"]["15"]["flat"] == 2
    assert summary["horizon_direction_summary"]["300"]["up"] == 1
    assert summary["horizon_direction_summary"]["300"]["down"] == 1
    assert summary["horizon_return_summary"]["600"]["count"] == 2
    assert summary["family_alignment_summary"]["trend_bias"]["direction_match"] == 3
    assert summary["family_alignment_summary"]["trend_bias"]["direction_mismatch"] == 7
    assert summary["scheduler_enabled"] is False
    assert summary["warroom_ui_trigger_enabled"] is False
    assert summary["would_send_to_broker"] is False


def test_loader_reads_review_files(tmp_path: Path) -> None:
    a = tmp_path / "a.json"
    b = tmp_path / "b.json"
    a.write_text(json.dumps(_review("a", {15: "flat"}, {15: 0.1})), encoding="utf-8")
    b.write_text(json.dumps(_review("b", {15: "down"}, {15: -5.0})), encoding="utf-8")
    summary = load_and_summarize_review_files([a, b])
    assert summary["ok"] is True
    assert summary["source_review_count"] == 2
    assert summary["horizon_direction_summary"]["15"]["flat"] == 1
    assert summary["horizon_direction_summary"]["15"]["down"] == 1


def test_missing_reviews_blocks_summary() -> None:
    summary = summarize_prediction_actual_market_reviews([])
    assert summary["ok"] is False
    assert "review_packets_missing" in summary["blocked_reasons"]


def test_tool_has_no_write_or_execution_behavior() -> None:
    text = TOOL.read_text(encoding="utf-8")
    forbidden = (
        "append_jsonl(",
        "write_canonical(",
        "write_raw(",
        "place_order(",
        "send_order(",
        "would_send_to_broker: bool = True",
    )
    for token in forbidden:
        assert token not in text, token
    assert "read_only_summary" in text
    assert "runtime_artifact_write_performed_by_summary" in text


if __name__ == "__main__":
    test_spec_declares_read_only_summary_boundaries()
    test_multi_window_summary_aggregates_horizons_families_and_alignment()
    from tempfile import TemporaryDirectory
    with TemporaryDirectory() as tmp:
        test_loader_reads_review_files(Path(tmp))
    test_missing_reviews_blocks_summary()
    test_tool_has_no_write_or_execution_behavior()
    print('{"ok": true}')
