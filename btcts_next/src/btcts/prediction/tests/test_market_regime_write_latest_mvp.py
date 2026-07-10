# path: ./btcts_next/src/btcts/prediction/tests/test_market_regime_write_latest_mvp.py
# desc: CP5 tests for manual market-regime latest artifact writer MVP. Uses tmp fixture root only; no UI, scheduler, broker, AutoTrade, or ledger behavior.

from __future__ import annotations

import json
import sys
from pathlib import Path

_SRC_ROOT = Path(__file__).resolve().parents[3]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

from btcts.prediction.market_regime.artifact_contracts import validate_market_regime_latest_cards_artifact, validate_market_regime_status_artifact  # noqa: E402
from btcts.prediction.market_regime.parameter_set_comparison_artifacts import PARAMETER_SET_COMPARISON_LATEST_READ_MODEL_RELPATH  # noqa: E402
from btcts.prediction.market_regime.parameter_set_comparison_read_model import validate_market_regime_parameter_set_comparison_read_model  # noqa: E402
from btcts.prediction.scenario_guidance import (  # noqa: E402
    PARENT_SCENARIO_GUIDANCE_LATEST_READ_MODEL_RELPATH,
    validate_parent_scenario_guidance_latest_read_model_artifact,
)
from btcts.prediction.market_regime.tools.write_latest import (  # noqa: E402
    build_market_regime_latest_artifact_set,
    main,
    write_market_regime_latest_artifacts_once,
)


def _write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")


def _write_jsonl(path: Path, records: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(json.dumps(record, ensure_ascii=False) for record in records) + "\n", encoding="utf-8")



def _write_outcome_rows(root: Path) -> None:
    path = root / "prediction/market_regime/outcomes/date=2026-07-08/part-00001.jsonl"
    rows = [
        {
            "outcome_id": "market_regime_fixture:300s:market_regime_engine_parameter_set.v1:hit",
            "run_id": "market_regime_fixture",
            "generated_at": "2026-07-08T09:00:00Z",
            "resolved_at": "2026-07-08T09:05:00Z",
            "horizon_key": "300s",
            "horizon_sec": 300,
            "predicted_regime_code": "RANGE",
            "observed_regime_code": "RANGE",
            "outcome_label": "hit",
            "observation_source": "candle_summary",
            "confidence_percent": 70,
            "parameter_set_id": "market_regime_engine_parameter_set.v1",
        },
        {
            "outcome_id": "market_regime_fixture:900s:market_regime_engine_parameter_set.v1:miss",
            "run_id": "market_regime_fixture",
            "generated_at": "2026-07-08T09:00:00Z",
            "resolved_at": "2026-07-08T09:15:00Z",
            "horizon_key": "900s",
            "horizon_sec": 900,
            "predicted_regime_code": "RANGE",
            "observed_regime_code": "DOWN_TREND",
            "outcome_label": "miss",
            "observation_source": "candle_summary",
            "confidence_percent": 68,
            "parameter_set_id": "market_regime_engine_parameter_set.v1",
        },
    ]
    _write_jsonl(path, rows)

def _fixture_root(root: Path) -> None:
    forecast_path = root / "prediction/runs/2026-07-08/091000/forecast_records.jsonl"
    _write_json(root / "prediction/latest_manifest.json", {
        "generated_at": "2026-07-08T09:10:00Z",
        "legacy_latest_path": "prediction/latest_prediction_system_result.json",
        "sidecars": {"forecast_records": "prediction/runs/2026-07-08/091000/forecast_records.jsonl"},
    })
    _write_json(root / "prediction/latest_prediction_system_result.json", {"read_only": True, "non_executing": True})
    _write_jsonl(forecast_path, [
        {"family": "market_regime", "horizon_sec": 300, "primary_label": "range_candidate", "score": 0.80, "values_snapshot": {"estimated_signal_strength_percent": 70, "estimated_reference_hit_rate_percent": 65, "volatility_state": "normal", "cross_venue_agreement": "aligned"}},
        {"family": "market_regime", "horizon_sec": 900, "primary_label": "trend_candidate", "score": 0.88, "values_snapshot": {"estimated_signal_strength_percent": 82, "estimated_reference_hit_rate_percent": 74, "volatility_state": "normal", "cross_venue_agreement": "aligned"}},
        {"family": "market_regime", "horizon_sec": 21600, "primary_label": "breakout_candidate", "score": 0.72, "values_snapshot": {"estimated_signal_strength_percent": 68, "estimated_reference_hit_rate_percent": 60, "volatility_state": "normal", "cross_venue_agreement": "aligned"}},
    ])
    _write_json(root / "state/collector_vnext/unified_market_state_status.json", {
        "last_symbol_raw": "FX_BTC_JPY",
        "last_best_bid": 9729064.0,
        "last_best_ask": 9730264.0,
        "last_spread": 1200.0,
        "read_only": True,
        "would_send_to_broker": False,
    })
    _write_json(root / "state/collector_vnext/unified_health.json", {"ok": True, "ws_state": "LIVE", "read_only": True, "would_send_to_broker": False})
    _write_json(root / "state/collector_vnext/unified_executions_status.json", {"ws_state": "LIVE", "trade_count": 20450, "read_only": True, "would_send_to_broker": False})
    _write_json(root / "state/collector_vnext/unified_daemon_status.json", {"read_only": True, "would_send_to_broker": False})
    _write_outcome_rows(root)


def test_cp5_build_artifact_set_without_filesystem_write(tmp_path: Path) -> None:
    _fixture_root(tmp_path)
    artifacts = build_market_regime_latest_artifact_set(
        hot_root=tmp_path,
        generated_at="2026-07-08T09:11:00Z",
        run_id="market_regime_test_run",
    )
    assert artifacts["run_id"] == "market_regime_test_run"
    assert artifacts["card_count"] == 8
    assert artifacts["latest_cards"]["horizon_count"] == 8
    assert artifacts["latest_cards"]["cards"][0]["regime_label"] == "レンジ"
    assert artifacts["latest_read_model"]["horizons"][0]["primary_regime"] == "RANGE"
    assert artifacts["latest_cards"]["compact_summary"]["source_snapshot_ok"] is True
    assert artifacts["validation"]["ok"] is True
    assert not (tmp_path / "prediction/market_regime/latest_cards.json").exists()


def test_cp5_write_latest_artifacts_once_writes_expected_files(tmp_path: Path) -> None:
    _fixture_root(tmp_path)
    result = write_market_regime_latest_artifacts_once(
        hot_root=tmp_path,
        generated_at="2026-07-08T09:12:00Z",
        run_id="market_regime_test_run",
    )
    assert result["ok"] is True
    assert result["card_count"] == 8
    assert result["scheduler_enabled"] is False
    assert result["producer_loop_enabled"] is False
    assert result["broker_private_api_allowed"] is False
    assert result["autotrade_trigger_allowed"] is False
    assert result["would_send_to_broker"] is False
    assert result["parameter_set_comparison_refresh_ok"] is True
    assert result["parameter_set_comparison_refresh_skipped"] is False
    assert result["parent_scenario_guidance_refresh_ok"] is True
    assert result["parent_scenario_guidance_refresh_skipped"] is False
    assert PARAMETER_SET_COMPARISON_LATEST_READ_MODEL_RELPATH in result["written"]
    assert PARENT_SCENARIO_GUIDANCE_LATEST_READ_MODEL_RELPATH in result["written"]

    latest = json.loads((tmp_path / "prediction/market_regime/latest.json").read_text(encoding="utf-8"))
    latest_cards = json.loads((tmp_path / "prediction/market_regime/latest_cards.json").read_text(encoding="utf-8"))
    read_model = json.loads((tmp_path / "prediction/market_regime/latest_read_model.json").read_text(encoding="utf-8"))
    status = json.loads((tmp_path / "prediction/market_regime/status.json").read_text(encoding="utf-8"))
    manifest = json.loads((tmp_path / "prediction/market_regime/runs/market_regime_test_run/manifest.json").read_text(encoding="utf-8"))
    parameter_set_comparison = json.loads((tmp_path / PARAMETER_SET_COMPARISON_LATEST_READ_MODEL_RELPATH).read_text(encoding="utf-8"))
    parent_scenario_guidance = json.loads((tmp_path / PARENT_SCENARIO_GUIDANCE_LATEST_READ_MODEL_RELPATH).read_text(encoding="utf-8"))

    assert latest["prediction_family_id"] == "market_regime"
    assert latest_cards["artifact_kind"] == "latest_cards"
    assert validate_market_regime_latest_cards_artifact(latest_cards)["ok"] is True
    assert read_model["artifact_kind"] == "latest_read_model"
    assert "not win rate" in read_model["explanation_note"]
    assert status["status"] == "latest_ready"
    assert status["latest_cards_available"] is True
    assert status["trace_ledger_available"] is True
    assert status["outcome_resolver_available"] is True
    assert validate_market_regime_status_artifact(status)["ok"] is True
    assert manifest["refs"]["latest_cards_json"] == "prediction/market_regime/latest_cards.json"
    assert latest_cards["safety"]["ui_render_invokes_classifier"] is False
    assert latest_cards["safety"]["broker_private_api_allowed"] is False
    assert parameter_set_comparison["artifact_kind"] == "parameter_set_comparison_read_model"
    assert parameter_set_comparison["promotion_candidates"] == []
    assert validate_market_regime_parameter_set_comparison_read_model(parameter_set_comparison)["ok"] is True
    assert parent_scenario_guidance["artifact_kind"] == "parent_scenario_guidance_latest_read_model"
    assert parent_scenario_guidance["horizon_count"] == 8
    assert parent_scenario_guidance["family_part_count"] == 8
    assert parent_scenario_guidance["prediction_family_ids"] == ["market_regime"]
    assert parent_scenario_guidance["safety"]["broker_private_api_allowed"] is False
    assert parent_scenario_guidance["safety"]["autotrade_trigger_allowed"] is False
    assert validate_parent_scenario_guidance_latest_read_model_artifact(parent_scenario_guidance)["ok"] is True


def test_cp5_cli_requires_once_and_writes_when_acknowledged(tmp_path: Path, capsys) -> None:
    _fixture_root(tmp_path)
    try:
        main(["--hot-root", str(tmp_path), "--generated-at", "2026-07-08T09:13:00Z", "--run-id", "market_regime_cli_run"])
    except SystemExit as exc:
        assert exc.code == 2
    else:  # pragma: no cover
        raise AssertionError("main without --once should fail")

    assert main(["--hot-root", str(tmp_path), "--generated-at", "2026-07-08T09:13:00Z", "--run-id", "market_regime_cli_run", "--once"]) == 0
    out = capsys.readouterr().out
    assert "market_regime_cli_run" in out
    assert (tmp_path / "prediction/market_regime/latest_cards.json").exists()
    assert (tmp_path / PARENT_SCENARIO_GUIDANCE_LATEST_READ_MODEL_RELPATH).exists()


def test_mr_a1_write_latest_compact_summary_surfaces_stale_forecast_warning(tmp_path: Path) -> None:
    _fixture_root(tmp_path)
    artifacts = build_market_regime_latest_artifact_set(
        hot_root=tmp_path,
        generated_at="2026-07-10T09:12:00Z",
        run_id="market_regime_stale_warning_test",
    )
    compact = artifacts["latest_cards"]["compact_summary"]
    assert "forecast_records_stale" in compact["warnings"]
    first = artifacts["latest_read_model"]["horizons"][0]
    assert first["diagnostic_record"]["forecast_records_currentness_gate_applied"] is True
    assert first["freshness_state"] == "STALE"


def test_mr_a2_latest_cards_source_refs_include_warroom_candles(tmp_path: Path) -> None:
    _fixture_root(tmp_path)
    artifacts = build_market_regime_latest_artifact_set(
        hot_root=tmp_path,
        generated_at="2026-07-08T09:12:00Z",
        run_id="market_regime_source_refs_test",
    )
    refs = artifacts["latest_cards"]["source_refs"]
    assert "warroom_candles" in refs
    assert refs["warroom_candles"]["relpath"].endswith("timeframe=60s/closed.jsonl")
    assert refs["warroom_candles"]["ok"] is False

def test_mr_vs3_shadow_confidence_is_diagnostic_only(tmp_path: Path) -> None:
    _fixture_root(tmp_path)
    artifacts = build_market_regime_latest_artifact_set(
        hot_root=tmp_path,
        generated_at="2026-07-08T09:12:00Z",
        run_id="market_regime_shadow_confidence_test",
    )

    shadow_by_horizon = artifacts["shadow_confidence_by_horizon"]
    assert len(shadow_by_horizon) == 8
    assert artifacts["latest_cards"]["compact_summary"]["shadow_confidence_available"] is True
    assert artifacts["latest_cards"]["compact_summary"]["shadow_confidence_only"] is True
    assert artifacts["latest_cards"]["compact_summary"]["display_confidence_replaced"] is False

    for card, horizon in zip(
        artifacts["latest_cards"]["cards"],
        artifacts["latest_read_model"]["horizons"],
        strict=True,
    ):
        card_shadow = card["detail"]["shadow_confidence"]
        read_shadow = horizon["diagnostic_record"]["shadow_confidence"]
        assert card_shadow["horizon_key"] == read_shadow["horizon_key"] == card["horizon_key"]
        assert card_shadow["legacy_confidence_percent"] == read_shadow["legacy_confidence_percent"] == card["confidence_percent"]
        assert card_shadow["shadow_display_confidence_percent"] == read_shadow["shadow_display_confidence_percent"]
        assert "source_signals" not in card_shadow
        assert "estimator" not in card_shadow
        assert "source_signals" in read_shadow
        assert "estimator" in read_shadow
        assert card["detail"]["shadow_confidence_only"] is True
        assert card["detail"]["display_confidence_replaced"] is False
        assert horizon["diagnostic_record"]["shadow_confidence_only"] is True
        assert horizon["diagnostic_record"]["display_confidence_replaced"] is False
        assert horizon["confidence_percent"] == card["confidence_percent"]

def test_mr_vs3_card_shadow_projection_is_smaller_than_full_read_model_diagnostic(tmp_path: Path) -> None:
    _fixture_root(tmp_path)
    artifacts = build_market_regime_latest_artifact_set(
        hot_root=tmp_path,
        generated_at="2026-07-08T09:12:00Z",
        run_id="market_regime_shadow_size_test",
    )
    card_shadow = artifacts["latest_cards"]["cards"][0]["detail"]["shadow_confidence"]
    read_shadow = artifacts["latest_read_model"]["horizons"][0]["diagnostic_record"]["shadow_confidence"]
    card_bytes = len(json.dumps(card_shadow, ensure_ascii=False, sort_keys=True).encode("utf-8"))
    read_bytes = len(json.dumps(read_shadow, ensure_ascii=False, sort_keys=True).encode("utf-8"))
    assert card_bytes < read_bytes
    assert card_bytes < 2048
