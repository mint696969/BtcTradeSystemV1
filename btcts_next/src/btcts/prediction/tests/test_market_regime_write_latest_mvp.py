# path: ./btcts_next/src/btcts/prediction/tests/test_market_regime_write_latest_mvp.py
# desc: CP5 tests for manual market-regime latest artifact writer MVP. Uses tmp fixture root only; no UI, scheduler, broker, AutoTrade, or ledger behavior.

from __future__ import annotations

import json
import sys
from pathlib import Path

_SRC_ROOT = Path(__file__).resolve().parents[3]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

from btcts.prediction.market_regime.artifact_contracts import validate_market_regime_latest_cards_artifact  # noqa: E402
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

    latest = json.loads((tmp_path / "prediction/market_regime/latest.json").read_text(encoding="utf-8"))
    latest_cards = json.loads((tmp_path / "prediction/market_regime/latest_cards.json").read_text(encoding="utf-8"))
    read_model = json.loads((tmp_path / "prediction/market_regime/latest_read_model.json").read_text(encoding="utf-8"))
    status = json.loads((tmp_path / "prediction/market_regime/status.json").read_text(encoding="utf-8"))
    manifest = json.loads((tmp_path / "prediction/market_regime/runs/market_regime_test_run/manifest.json").read_text(encoding="utf-8"))

    assert latest["prediction_family_id"] == "market_regime"
    assert latest_cards["artifact_kind"] == "latest_cards"
    assert validate_market_regime_latest_cards_artifact(latest_cards)["ok"] is True
    assert read_model["artifact_kind"] == "latest_read_model"
    assert "not win rate" in read_model["explanation_note"]
    assert status["status"] == "latest_ready"
    assert status["latest_cards_available"] is True
    assert manifest["refs"]["latest_cards_json"] == "prediction/market_regime/latest_cards.json"
    assert latest_cards["safety"]["ui_render_invokes_classifier"] is False
    assert latest_cards["safety"]["broker_private_api_allowed"] is False


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
