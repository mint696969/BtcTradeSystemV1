# path: ./btcts_next/src/btcts/prediction/tests/test_market_regime_live_once_preflight_cp11.py
# desc: CP11 tests for market-regime live once-run preflight. Preflight builds artifact set but writes nothing; --once still required for writes.

from __future__ import annotations

import json
import sys
from pathlib import Path

_SRC_ROOT = Path(__file__).resolve().parents[3]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

from btcts.prediction.market_regime.tools.write_latest import (  # noqa: E402
    main,
    preflight_market_regime_latest_artifacts_once,
)


def _write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")


def _write_jsonl(path: Path, records: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(json.dumps(record, ensure_ascii=False) for record in records) + "\n", encoding="utf-8")


def _collector_only_root(root: Path) -> None:
    _write_json(root / "state/collector_vnext/unified_market_state_status.json", {
        "last_symbol_raw": "FX_BTC_JPY",
        "last_best_bid": 9729000.0,
        "last_best_ask": 9730000.0,
        "last_spread": 1000.0,
        "lane_state": "live",
        "read_only": True,
        "would_send_to_broker": False,
    })
    _write_json(root / "state/collector_vnext/unified_health.json", {"ok": True, "status": "healthy", "ws_state": "LIVE", "ws_freshness": "LIVE", "read_only": True, "would_send_to_broker": False})
    _write_json(root / "state/collector_vnext/unified_executions_status.json", {"ws_state": "LIVE", "lane_state": "live", "trade_count": 20450, "read_only": True, "would_send_to_broker": False})
    _write_json(root / "state/collector_vnext/unified_daemon_status.json", {"read_only": True, "would_send_to_broker": False})


def _complete_fixture_root(root: Path) -> None:
    _collector_only_root(root)
    forecast_path = root / "prediction/runs/2026-07-08/120000/forecast_records.jsonl"
    _write_json(root / "prediction/latest_manifest.json", {
        "generated_at": "2026-07-08T12:00:00Z",
        "legacy_latest_path": "prediction/latest_prediction_system_result.json",
        "sidecars": {"forecast_records": "prediction/runs/2026-07-08/120000/forecast_records.jsonl"},
    })
    _write_json(root / "prediction/latest_prediction_system_result.json", {"read_only": True, "non_executing": True})
    _write_jsonl(forecast_path, [
        {"family": "market_regime", "horizon_sec": 300, "primary_label": "range_candidate", "score": 0.80, "values_snapshot": {"estimated_signal_strength_percent": 70, "estimated_reference_hit_rate_percent": 65, "volatility_state": "normal", "cross_venue_agreement": "aligned"}},
        {"family": "market_regime", "horizon_sec": 900, "primary_label": "trend_candidate", "score": 0.88, "values_snapshot": {"estimated_signal_strength_percent": 82, "estimated_reference_hit_rate_percent": 74, "volatility_state": "normal", "cross_venue_agreement": "aligned"}},
    ])


def test_cp11_preflight_complete_fixture_can_write_but_writes_nothing(tmp_path: Path) -> None:
    _complete_fixture_root(tmp_path)
    result = preflight_market_regime_latest_artifacts_once(
        hot_root=tmp_path,
        generated_at="2026-07-08T12:01:00Z",
        run_id="market_regime_cp11_preflight_ok",
    )
    assert result["ok"] is True
    assert result["preflight_only"] is True
    assert result["would_write"] is False
    assert result["can_write_live_once"] is True
    assert result["source_snapshot_ok"] is True
    assert result["latest_cards_validation"]["ok"] is True
    assert result["expected_artifacts"]["latest_cards_json"] == "prediction/market_regime/latest_cards.json"
    assert not (tmp_path / "prediction/market_regime/latest_cards.json").exists()
    assert result["broker_private_api_allowed"] is False
    assert result["autotrade_trigger_allowed"] is False


def test_cp11_preflight_collector_only_root_blocks_write_and_writes_nothing(tmp_path: Path) -> None:
    _collector_only_root(tmp_path)
    result = preflight_market_regime_latest_artifacts_once(
        hot_root=tmp_path,
        generated_at="2026-07-08T12:02:00Z",
        run_id="market_regime_cp11_preflight_missing_prediction",
    )
    assert result["ok"] is True
    assert result["preflight_only"] is True
    assert result["would_write"] is False
    assert result["can_write_live_once"] is False
    assert result["source_snapshot_ok"] is False
    assert "latest_manifest" in result["missing_sources"]
    assert "forecast_records" in result["missing_sources"]
    assert result["latest_cards_validation"]["ok"] is True
    assert not (tmp_path / "prediction/market_regime/latest_cards.json").exists()
    assert not (tmp_path / "prediction/market_regime/ledgers/date=2026-07-08/hour=12/part-00001.jsonl").exists()


def test_cp11_cli_preflight_does_not_require_once_and_writes_nothing(tmp_path: Path, capsys) -> None:
    _complete_fixture_root(tmp_path)
    assert main(["--hot-root", str(tmp_path), "--generated-at", "2026-07-08T12:03:00Z", "--run-id", "market_regime_cp11_cli_preflight", "--preflight"]) == 0
    out = capsys.readouterr().out
    payload = json.loads(out)
    assert payload["preflight_only"] is True
    assert payload["can_write_live_once"] is True
    assert not (tmp_path / "prediction/market_regime/latest_cards.json").exists()


def test_cp11_cli_still_requires_once_for_write(tmp_path: Path) -> None:
    _complete_fixture_root(tmp_path)
    try:
        main(["--hot-root", str(tmp_path), "--generated-at", "2026-07-08T12:04:00Z", "--run-id", "market_regime_cp11_no_once"])
    except SystemExit as exc:
        assert exc.code == 2
    else:  # pragma: no cover
        raise AssertionError("main without --once or --preflight should fail")
    assert not (tmp_path / "prediction/market_regime/latest_cards.json").exists()
