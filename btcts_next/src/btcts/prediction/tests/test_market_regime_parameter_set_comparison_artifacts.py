# path: ./btcts_next/src/btcts/prediction/tests/test_market_regime_parameter_set_comparison_artifacts.py
# desc: PS_PARAMETER_SET_COMPARISON_WRITER_V1 tests. Verifies artifact path/writer for market-regime parameter-set comparison without raw market read, broker, AutoTrade, or parameter mutation.

from __future__ import annotations

import json
import sys
from pathlib import Path

_SRC_ROOT = Path(__file__).resolve().parents[3]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

from btcts.prediction.market_regime.parameter_set_comparison_artifacts import (  # noqa: E402
    PARAMETER_SET_COMPARISON_LATEST_READ_MODEL_RELPATH,
    build_market_regime_parameter_set_comparison_artifact_write_plan,
    parameter_set_comparison_latest_read_model_relpath,
    parameter_set_comparison_outcome_part_relpath,
    preflight_market_regime_parameter_set_comparison_read_model,
    write_market_regime_parameter_set_comparison_read_model,
)
from btcts.prediction.market_regime.parameter_set_comparison_read_model import validate_market_regime_parameter_set_comparison_read_model  # noqa: E402


def _row(parameter_set_id: str, label: str, *, source: str = "candle_summary", outcome_id: str | None = None) -> dict[str, object]:
    return {
        "outcome_id": outcome_id if outcome_id is not None else f"run:300s:{parameter_set_id}:{label}",
        "run_id": "run",
        "generated_at": "2026-07-08T12:00:00Z",
        "resolved_at": "2026-07-08T12:05:00Z",
        "horizon_key": "300s",
        "horizon_sec": 300,
        "predicted_regime_code": "RANGE",
        "observed_regime_code": "RANGE" if label == "hit" else "HIGH_VOL_CHOP",
        "outcome_label": label,
        "observation_source": source,
        "confidence_percent": 70,
        "parameter_set_id": parameter_set_id,
        "trace_part_jsonl": "prediction/market_regime/ledgers/date=2026-07-08/hour=12/part-00001.jsonl",
    }


def _write_outcomes(root: Path, rows: list[dict[str, object]], *, date: str = "2026-07-08") -> Path:
    path = root / parameter_set_comparison_outcome_part_relpath(date)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(json.dumps(row, ensure_ascii=False) for row in rows) + "\n", encoding="utf-8")
    return path


def test_ps_parameter_set_comparison_artifact_paths_are_stable() -> None:
    assert parameter_set_comparison_latest_read_model_relpath() == PARAMETER_SET_COMPARISON_LATEST_READ_MODEL_RELPATH
    assert PARAMETER_SET_COMPARISON_LATEST_READ_MODEL_RELPATH == "prediction/market_regime/parameter_set_comparison/latest_read_model.json"
    assert parameter_set_comparison_outcome_part_relpath("2026-07-08") == "prediction/market_regime/outcomes/date=2026-07-08/part-00001.jsonl"


def test_ps_parameter_set_comparison_preflight_builds_plan_without_writing(tmp_path: Path) -> None:
    _write_outcomes(tmp_path, [
        _row("active.v1", "hit", outcome_id="run:300s:outcome"),
        _row("shadow.v2", "hit"),
        _row("active.v1", "hit", source="latest_cards_current"),
    ])

    plan = build_market_regime_parameter_set_comparison_artifact_write_plan(
        tmp_path,
        date="2026-07-08",
        active_parameter_set_id="active.v1",
        min_trusted_samples=1,
    )

    assert plan["ok"] is True
    assert plan["preflight_only"] is True
    assert plan["would_write"] is False
    assert plan["outcome_row_count"] == 3
    assert plan["comparison_ready"] is True
    assert plan["trusted_row_count"] == 2
    assert plan["reference_only_row_count"] == 1
    assert plan["legacy_outcome_id_without_parameter_set_count"] == 1
    assert plan["promotion_candidate_count"] == 0
    assert plan["safety"]["writes_parameter_set_comparison_read_model_only"] is True
    assert plan["safety"]["parameter_auto_promotion_allowed"] is False
    assert not (tmp_path / PARAMETER_SET_COMPARISON_LATEST_READ_MODEL_RELPATH).exists()
    assert validate_market_regime_parameter_set_comparison_read_model(plan["read_model"])["ok"] is True

    public = preflight_market_regime_parameter_set_comparison_read_model(
        tmp_path,
        date="2026-07-08",
        active_parameter_set_id="active.v1",
        min_trusted_samples=1,
    )
    assert "read_model" not in public
    assert public["parameter_set_comparison_read_model_json"] == PARAMETER_SET_COMPARISON_LATEST_READ_MODEL_RELPATH


def test_ps_parameter_set_comparison_writer_writes_only_read_model_artifact(tmp_path: Path) -> None:
    _write_outcomes(tmp_path, [
        _row("active.v1", "hit"),
        _row("active.v1", "miss"),
        _row("shadow.v2", "hit"),
        _row("shadow.v2", "hit"),
    ])

    result = write_market_regime_parameter_set_comparison_read_model(
        tmp_path,
        date="2026-07-08",
        active_parameter_set_id="active.v1",
        min_trusted_samples=2,
    )

    assert result["ok"] is True
    assert result["comparison_ready"] is True
    assert result["parameter_set_comparison_read_model_json"] == PARAMETER_SET_COMPARISON_LATEST_READ_MODEL_RELPATH
    assert result["safety"]["broker_private_api_allowed"] is False
    assert result["safety"]["autotrade_trigger_allowed"] is False
    assert result["safety"]["live_parameter_apply_allowed"] is False
    assert result["safety"]["writes_parameter_set_comparison_read_model_only"] is True

    written = tmp_path / PARAMETER_SET_COMPARISON_LATEST_READ_MODEL_RELPATH
    assert written.exists()
    payload = json.loads(written.read_text(encoding="utf-8"))
    assert payload["artifact_kind"] == "parameter_set_comparison_read_model"
    assert payload["comparison_ready"] is True
    assert payload["promotion_candidates"] == []
    assert validate_market_regime_parameter_set_comparison_read_model(payload)["ok"] is True
    assert not (tmp_path / "prediction/market_regime/latest.json").exists()
    assert not (tmp_path / "prediction/market_regime/status.json").exists()


def test_ps_parameter_set_comparison_writer_source_keeps_runtime_boundaries() -> None:
    path = Path(__file__).resolve().parents[1] / "market_regime/parameter_set_comparison_artifacts.py"
    text = path.read_text(encoding="utf-8")
    required = [
        "PARAMETER_SET_COMPARISON_LATEST_READ_MODEL_RELPATH",
        "write_market_regime_parameter_set_comparison_read_model",
        "preflight_market_regime_parameter_set_comparison_read_model",
        "writes_parameter_set_comparison_read_model_only",
        "parameter_auto_promotion_allowed",
    ]
    assert [token for token in required if token not in text] == []
    forbidden = [
        "classify_market_regime_feature_bundle(",
        "build_market_regime_source_snapshot(",
        "build_market_regime_feature_bundle(",
        "append_market_regime_trace_row_once(",
        "append_market_regime_outcome_row_once(",
        "broker_private_api_allowed: bool = True",
        "autotrade_trigger_allowed: bool = True",
        "order_intent_submitted: bool = True",
        "parameter_auto_promotion_allowed: bool = True",
        "live_parameter_apply_allowed: bool = True",
    ]
    assert [token for token in forbidden if token in text] == []
