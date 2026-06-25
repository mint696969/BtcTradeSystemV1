# path: ./tools/test_phase4a_prediction_system_ps_q19x_actual_point_selection_policy.py
# desc: Focused guard for PS-Q19X read-only actual-point selection policy comparison helper.

from __future__ import annotations

import json
import sys
from pathlib import Path
from tempfile import TemporaryDirectory

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tools.compare_actual_point_selection_policy_ps_q19x import (  # noqa: E402
    compare_actual_point_selection_policy,
    load_and_compare_actual_point_selection_policy,
)

SPEC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q19X_ACTUAL_POINT_SELECTION_POLICY_2026-06-25.md"
TOOL = REPO_ROOT / "tools/compare_actual_point_selection_policy_ps_q19x.py"

REQUIRED_MARKERS = (
    "ps_q19x_actual_point_selection_policy=true",
    "compares_strict_nearest_vs_quality_ok_within_tolerance=true",
    "read_only_policy_compare=true",
    "ps_q19r_behavior_changed_by_policy_compare=false",
)
FALSE_BOUNDARIES = (
    "runtime_artifact_write_performed_by_policy_compare=false",
    "status_artifact_write_performed_by_policy_compare=false",
    "prediction_artifact_write_performed_by_policy_compare=false",
    "view_artifact_write_performed_by_policy_compare=false",
    "collector_state_write_performed_by_policy_compare=false",
    "scheduler_enabled=false",
    "producer_enabled=false",
    "warroom_ui_trigger_enabled=false",
    "autotrade_trigger_allowed=false",
    "broker_private_api_allowed=false",
    "would_send_to_broker=false",
)


def _row(ts: str, *, trust: str, bucket: str, bid: float, ask: float) -> dict:
    return {
        "collector_ts": ts,
        "exchange_ts": None,
        "trust_state": trust,
        "continuity_state": "continuous",
        "interpretation_bucket": bucket,
        "best_bid": bid,
        "best_ask": ask,
        "spread": ask - bid,
        "mid_price": (bid + ask) / 2,
    }


def _write_jsonl(path: Path, rows: list[dict]) -> None:
    path.write_text("".join(json.dumps(row, sort_keys=True) + "\n" for row in rows), encoding="utf-8")


def test_spec_declares_policy_compare_boundaries() -> None:
    text = SPEC.read_text(encoding="utf-8-sig")
    for marker in REQUIRED_MARKERS:
        assert marker in text, marker
    for marker in FALSE_BOUNDARIES:
        assert marker in text, marker


def test_detects_quality_ok_candidate_when_strict_nearest_is_rejected_same_second() -> None:
    with TemporaryDirectory() as tmp:
        market = Path(tmp) / "part-00001.jsonl"
        _write_jsonl(market, [
            _row("2026-06-25T12:04:14Z", trust="quarantined", bucket="reanchor_required", bid=105.0, ask=104.0),
            _row("2026-06-25T12:04:14Z", trust="trusted", bucket="allow_structural_use", bid=101.0, ask=103.0),
        ])
        packet = compare_actual_point_selection_policy(
            market_path=market,
            generated_at=__import__("datetime").datetime.fromisoformat("2026-06-25T11:59:14+00:00"),
            horizons_sec=(300,),
            tolerance_sec=30,
        )
    assert packet["ok"] is True
    assert packet["strict_rejected_horizon_count"] == 1
    assert packet["quality_ok_alternative_available_count"] == 1
    assert packet["same_second_quality_ok_alternative_count"] == 1
    assert packet["impacted_horizons"] == ["300"]
    result = packet["horizon_results"]["300"]
    assert result["policy_delta"] == "strict_rejected_quality_ok_candidate_available"
    assert result["strict_nearest"]["quality_ok"] is False
    assert result["quality_ok_nearest"]["quality_ok"] is True
    assert packet["policy_comparison"]["ps_q19r_behavior_changed_by_this_helper"] is False
    assert packet["scheduler_enabled"] is False
    assert packet["warroom_ui_trigger_enabled"] is False
    assert packet["would_send_to_broker"] is False


def test_no_delta_when_strict_nearest_is_already_quality_ok() -> None:
    with TemporaryDirectory() as tmp:
        market = Path(tmp) / "part-00001.jsonl"
        _write_jsonl(market, [_row("2026-06-25T12:00:14Z", trust="trusted", bucket="allow_structural_use", bid=101.0, ask=103.0)])
        packet = compare_actual_point_selection_policy(
            market_path=market,
            generated_at=__import__("datetime").datetime.fromisoformat("2026-06-25T11:59:14+00:00"),
            horizons_sec=(60,),
            tolerance_sec=30,
        )
    assert packet["ok"] is True
    assert packet["horizon_results"]["60"]["policy_delta"] == "strict_already_quality_ok"
    assert packet["impacted_horizons"] == []


def test_loader_uses_prediction_generated_at_and_market_file() -> None:
    with TemporaryDirectory() as tmp:
        root = Path(tmp)
        pred = root / "prediction/latest_prediction_system_result.json"
        pred.parent.mkdir(parents=True, exist_ok=True)
        pred.write_text(json.dumps({"forecast_batch": {"generated_at": "2026-06-25T11:59:14Z", "records": []}}), encoding="utf-8")
        market = root / "market.jsonl"
        _write_jsonl(market, [_row("2026-06-25T12:04:14Z", trust="trusted", bucket="allow_structural_use", bid=101.0, ask=103.0)])
        packet = load_and_compare_actual_point_selection_policy(root=str(root), prediction_path=str(pred), market_path=str(market), horizons_sec=(300,), tolerance_sec=30)
    assert packet["ok"] is True
    assert packet["prediction_generated_at"] == "2026-06-25T11:59:14Z"
    assert packet["horizon_results"]["300"]["quality_ok_candidate_available"] is True


def test_missing_market_path_blocks() -> None:
    packet = compare_actual_point_selection_policy(
        market_path=Path("does_not_exist.jsonl"),
        generated_at=__import__("datetime").datetime.fromisoformat("2026-06-25T11:59:14+00:00"),
        horizons_sec=(300,),
    )
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
    assert "read_only_policy_compare" in text
    assert "ps_q19r_behavior_changed_by_policy_compare" in text


if __name__ == "__main__":
    test_spec_declares_policy_compare_boundaries()
    test_detects_quality_ok_candidate_when_strict_nearest_is_rejected_same_second()
    test_no_delta_when_strict_nearest_is_already_quality_ok()
    test_loader_uses_prediction_generated_at_and_market_file()
    test_missing_market_path_blocks()
    test_tool_has_no_write_or_execution_behavior()
    print('{"ok": true}')
