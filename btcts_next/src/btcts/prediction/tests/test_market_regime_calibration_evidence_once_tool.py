# path: ./btcts_next/src/btcts/prediction/tests/test_market_regime_calibration_evidence_once_tool.py
# desc: Tests the read-only MR-F7 calibration evidence once tool, including bounded scans, truncation, parse failures, and safety guarantees.

from __future__ import annotations

import json
from pathlib import Path

from btcts.prediction.market_regime.tools.calibration_evidence_once import (
    MARKET_REGIME_CALIBRATION_EVIDENCE_ONCE_TOOL_VERSION,
    build_market_regime_calibration_evidence_once_report,
)
from btcts.prediction.market_regime.trace_ledger import (
    MARKET_REGIME_SOURCE_FLAG_CONTRIBUTION_LEDGER_VERSION,
)


def _write_jsonl(path: Path, rows: list[object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "".join(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n" for row in rows),
        encoding="utf-8",
    )


def _outcome(outcome_id: str, run_id: str, *, source: str = "candle_summary") -> dict:
    return {
        "outcome_id": outcome_id,
        "run_id": run_id,
        "horizon_key": "300s",
        "horizon_sec": 300,
        "outcome_label": "hit",
        "observation_source": source,
    }


def _trace(run_id: str, *, full: bool = False) -> dict:
    signal_summary = {
        "horizons": [
            {
                "horizon_key": "300s",
                "source_flag_contributions": (
                    [
                        {
                            "source_id": "ticker",
                            "flag_id": "ticker_spread_expansion",
                            "supports_regime": "HIGH_VOLATILITY",
                            "strength": 0.8,
                            "weighted_strength": 0.6,
                        }
                    ]
                    if full
                    else None
                ),
            }
        ]
    }
    if full:
        signal_summary["source_flag_contribution_ledger_version"] = (
            MARKET_REGIME_SOURCE_FLAG_CONTRIBUTION_LEDGER_VERSION
        )
    return {
        "artifact_kind": "trace_row",
        "run_id": run_id,
        "signal_summary": signal_summary,
    }


def test_once_report_scans_complete_fixture_and_separates_cohorts(tmp_path: Path) -> None:
    _write_jsonl(
        tmp_path / "prediction/market_regime/outcomes/date=2026-07-09/part-00001.jsonl",
        [_outcome("o1", "legacy"), _outcome("o2", "full")],
    )
    _write_jsonl(
        tmp_path / "prediction/market_regime/ledgers/date=2026-07-09/hour=00/part-00001.jsonl",
        [_trace("legacy"), _trace("full", full=True), _trace("irrelevant")],
    )

    report = build_market_regime_calibration_evidence_once_report(hot_root=tmp_path)

    assert report["tool_version"] == MARKET_REGIME_CALIBRATION_EVIDENCE_ONCE_TOOL_VERSION
    assert report["ok"] is True
    assert report["input_complete"] is True
    assert report["outcome_scan"]["selected_row_count"] == 2
    assert report["trace_scan"]["selected_row_count"] == 2
    assert report["trace_scan"]["selected_run_id_count"] == 2
    assert report["trace_scan"]["filtered_selection_count"] == 1
    assert report["readiness"]["coarse_calibration_ready"] is True
    assert report["readiness"]["detailed_source_flag_calibration_ready"] is False
    assert report["readiness"]["counts"]["legacy_coarse_trace_count"] == 1
    assert report["readiness"]["counts"]["full_contribution_trace_count"] == 1
    assert report["safety"]["writes_hot_data"] is False
    assert report["safety"]["fits_calibration_model"] is False


def test_once_report_marks_row_limit_as_incomplete(tmp_path: Path) -> None:
    _write_jsonl(
        tmp_path / "prediction/market_regime/outcomes/date=2026-07-09/part-00001.jsonl",
        [_outcome("o1", "r1"), _outcome("o2", "r2")],
    )
    _write_jsonl(
        tmp_path / "prediction/market_regime/ledgers/date=2026-07-09/hour=00/part-00001.jsonl",
        [_trace("r1"), _trace("r2")],
    )

    report = build_market_regime_calibration_evidence_once_report(
        hot_root=tmp_path,
        max_outcome_rows=1,
    )

    assert report["ok"] is False
    assert report["input_complete"] is False
    assert report["outcome_scan"]["truncated"] is True
    assert report["closeout_interpretation"]["coarse_calibration_evidence_available"] is False


def test_once_report_exposes_parse_failures_without_writing(tmp_path: Path) -> None:
    outcome_path = tmp_path / "prediction/market_regime/outcomes/date=2026-07-09/part-00001.jsonl"
    outcome_path.parent.mkdir(parents=True, exist_ok=True)
    outcome_path.write_text("{not-json}\n", encoding="utf-8")

    report = build_market_regime_calibration_evidence_once_report(hot_root=tmp_path)

    assert report["ok"] is False
    assert report["reader_ok"] is False
    assert report["outcome_scan"]["failure_count"] == 1
    assert report["outcome_scan"]["failures"][0].startswith("invalid_json:")
    assert list(tmp_path.rglob("*.json")) == []


def test_once_tool_source_has_no_write_or_runtime_fit_paths() -> None:
    path = Path(__file__).resolve().parents[1] / "market_regime/tools/calibration_evidence_once.py"
    text = path.read_text(encoding="utf-8")
    forbidden = [
        "write_text(",
        'open("w',
        "open('w",
        "append_market_regime_outcome",
        "write_market_regime_calibration",
        "fit_market_regime_calibration",
        "replace_display_confidence=True",
        "subprocess.Popen",
        '"broker_private_api_allowed": True',
        '"autotrade_trigger_allowed": True',
        '"parameter_auto_promotion_allowed": True',
    ]
    assert [token for token in forbidden if token in text] == []
    required = [
        "--preflight",
        "build_market_regime_calibration_evidence_readiness",
        "outcomes/date=*/part-*.jsonl",
        "ledgers/date=*/hour=*/part-*.jsonl",
    ]
    assert [token for token in required if token not in text] == []

def test_once_report_scans_all_trace_bytes_but_retains_only_outcome_run_ids(tmp_path: Path) -> None:
    _write_jsonl(
        tmp_path / "prediction/market_regime/outcomes/date=2026-07-09/part-00001.jsonl",
        [_outcome("o1", "needed")],
    )
    _write_jsonl(
        tmp_path / "prediction/market_regime/ledgers/date=2026-07-09/hour=00/part-00001.jsonl",
        [_trace("needed"), *[_trace(f"irrelevant-{index}") for index in range(50)]],
    )

    report = build_market_regime_calibration_evidence_once_report(
        hot_root=tmp_path,
        max_total_bytes=1024 * 1024,
    )

    assert report["ok"] is True
    assert report["input_complete"] is True
    assert report["trace_scan"]["scanned_line_count"] == 51
    assert report["trace_scan"]["selected_row_count"] == 1
    assert report["trace_scan"]["filtered_selection_count"] == 50
    assert report["readiness"]["counts"]["matched_trace_count"] == 1
