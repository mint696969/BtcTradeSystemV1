# path: ./btcts_next/src/btcts/prediction/market_regime/tests/test_market_regime_source_scorecard_artifacts.py
# desc: Focused tests for current-primary MarketRegime source-scorecard artifact preflight and atomic writer.

from __future__ import annotations

import json
import sys
from pathlib import Path

_SRC_ROOT = Path(__file__).resolve().parents[4]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

from btcts.prediction.market_regime.source_scorecard_artifacts import (  # noqa: E402
    build_market_regime_current_primary_source_scorecard_artifact_write_plan,
    preflight_market_regime_current_primary_source_scorecard,
    source_scorecard_current_primary_relpath,
    write_market_regime_current_primary_source_scorecard,
)


def _write_trace(root: Path, *, generated_at: str, with_price_structure: bool = False) -> None:
    path = root / "prediction/market_regime/ledgers/date=2026-07-10/hour=15/part-00001.jsonl"
    path.parent.mkdir(parents=True, exist_ok=True)
    signals = {
        "market_regime.liquidity": {
            "direction": "RANGE",
            "signal_strength_percent": 80,
            "freshness_percent": 100,
            "quality_percent": 90,
            "blocked": False,
        }
    }
    if with_price_structure:
        signals["market_regime.price_structure"] = {
            "direction": "RANGE",
            "signal_strength_percent": 70,
            "freshness_percent": 100,
            "quality_percent": 80,
            "blocked": False,
        }
    row = {
        "trace_id": "run-current:trace",
        "run_id": "run-current",
        "generated_at": generated_at,
        "active_parameter_set_id": "ps-1",
        "source_attribution_by_horizon": {
            "300s": {
                "horizon_key": "300s",
                "predicted_regime": "RANGE",
                "parameter_set_id": "ps-1",
                "logic_version": "logic-v1",
                "source_signals": signals,
            }
        },
    }
    path.write_text(json.dumps(row) + "\n", encoding="utf-8")


def _write_outcome(root: Path, *, generated_at: str) -> None:
    path = root / "prediction/market_regime/outcomes/date=2026-07-10/part-00001.jsonl"
    path.parent.mkdir(parents=True, exist_ok=True)
    row = {
        "outcome_id": "run-current:300s:ps-1:outcome",
        "run_id": "run-current",
        "generated_at": generated_at,
        "horizon_key": "300s",
        "parameter_set_id": "ps-1",
        "predicted_regime_code": "RANGE",
        "outcome_label": "hit",
        "observation_source": "candle_summary",
    }
    path.write_text(json.dumps(row) + "\n", encoding="utf-8")


def test_preflight_uses_current_primary_only_and_does_not_write(tmp_path: Path) -> None:
    _write_trace(tmp_path, generated_at="2026-07-10T15:27:22Z")
    _write_outcome(tmp_path, generated_at="2026-07-10T15:27:22Z")

    result = preflight_market_regime_current_primary_source_scorecard(
        tmp_path,
        min_trusted_samples=1,
    )

    assert result["ok"] is True
    assert result["would_write"] is False
    assert result["trace_row_count"] == 1
    assert result["outcome_row_count"] == 1
    assert result["comparison_ready"] is True
    assert not (tmp_path / source_scorecard_current_primary_relpath()).exists()


def test_writer_persists_current_primary_read_model_atomically(tmp_path: Path) -> None:
    _write_trace(tmp_path, generated_at="2026-07-10T15:27:22Z")
    _write_outcome(tmp_path, generated_at="2026-07-10T15:27:22Z")

    result = write_market_regime_current_primary_source_scorecard(
        tmp_path,
        min_trusted_samples=1,
    )

    assert result["ok"] is True
    assert result["would_write"] is True
    path = tmp_path / source_scorecard_current_primary_relpath()
    payload = json.loads(path.read_text(encoding="utf-8"))
    assert payload["artifact_kind"] == "source_scorecard_current_primary_read_model"
    assert payload["current_primary_cohort_started_at"] == "2026-07-10T15:27:22Z"
    assert payload["comparison_ready"] is True
    assert payload["auto_apply_allowed"] is False
    assert payload["auto_promotion_allowed"] is False
    assert payload["safety"]["would_send_to_broker"] is False
    assert not path.with_name(path.name + ".tmp").exists()


def test_writer_keeps_zero_sample_observed_source_as_not_ready(tmp_path: Path) -> None:
    _write_trace(tmp_path, generated_at="2026-07-10T15:27:22Z", with_price_structure=True)
    _write_outcome(tmp_path, generated_at="2026-07-10T15:27:22Z")

    plan = build_market_regime_current_primary_source_scorecard_artifact_write_plan(
        tmp_path,
        min_trusted_samples=2,
    )

    progress = {row["source_id"]: row for row in plan["read_model"]["source_progress"]}
    assert progress["market_regime.price_structure"]["trusted_sample_count"] == 1
    assert progress["market_regime.price_structure"]["ready"] is False


def test_preflight_excludes_reference_only_outcomes_from_current_primary(tmp_path: Path) -> None:
    _write_trace(tmp_path, generated_at="2026-07-10T15:27:22Z")
    outcome_path = tmp_path / "prediction/market_regime/outcomes/date=2026-07-10/part-00001.jsonl"
    outcome_path.parent.mkdir(parents=True, exist_ok=True)
    trusted = {
        "outcome_id": "run-current:300s:ps-1:trusted",
        "run_id": "run-current",
        "generated_at": "2026-07-10T15:27:22Z",
        "horizon_key": "300s",
        "parameter_set_id": "ps-1",
        "predicted_regime_code": "RANGE",
        "outcome_label": "hit",
        "observation_source": "candle_summary",
    }
    reference_only = dict(trusted)
    reference_only.update({
        "outcome_id": "run-current:300s:ps-1:reference",
        "observation_source": "latest_cards_current",
    })
    outcome_path.write_text(
        json.dumps(trusted) + "\n" + json.dumps(reference_only) + "\n",
        encoding="utf-8",
    )

    plan = build_market_regime_current_primary_source_scorecard_artifact_write_plan(
        tmp_path,
        min_trusted_samples=1,
    )

    assert plan["outcome_row_count"] == 1
    assert plan["read_model"]["outcome_row_count"] == 1
    assert plan["read_model"]["pipeline"]["scorecard"]["trusted_outcome_count"] == 1
