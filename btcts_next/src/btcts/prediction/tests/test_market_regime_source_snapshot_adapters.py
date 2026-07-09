# path: ./btcts_next/src/btcts/prediction/tests/test_market_regime_source_snapshot_adapters.py
# desc: PS-Q27H tests for read-only market-regime source snapshot adapters. Uses tmp_path only; no real D-hot access.

from __future__ import annotations

import json
import sys
from pathlib import Path

_SRC_ROOT = Path(__file__).resolve().parents[3]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

from btcts.prediction.market_regime.source_snapshot import SourceAdapterSafetyFlags  # noqa: E402
from btcts.prediction.market_regime.sources import (  # noqa: E402
    build_market_regime_source_snapshot,
    load_forecast_records_snapshot,
    load_latest_manifest,
    resolve_forecast_records_relative_path,
    resolve_latest_prediction_relative_path,
    resolve_under_root,
)


def _write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")


def _write_jsonl(path: Path, records: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(json.dumps(record, ensure_ascii=False) for record in records) + "\n", encoding="utf-8")


def _build_fixture(root: Path) -> None:
    run_dir = root / "prediction/runs/2026-07-01/165500"
    forecast_path = run_dir / "forecast_records.jsonl"
    _write_json(root / "prediction/latest_manifest.json", {
        "generated_at": "2026-07-01T16:55:00Z",
        "legacy_latest_path": "prediction/latest_prediction_system_result.json",
        "sidecars": {"forecast_records": "prediction/runs/2026-07-01/165500/forecast_records.jsonl"},
    })
    _write_json(root / "prediction/latest_prediction_system_result.json", {
        "generated_at": "2026-07-01T16:55:00Z",
        "read_only": True,
        "non_executing": True,
    })
    _write_jsonl(forecast_path, [
        {"family": "trend_bias", "horizon_sec": 300, "primary_label": "neutral_bias"},
        {"family": "market_regime", "horizon_sec": 300, "primary_label": "range_candidate", "read_only": True, "would_send_to_broker": False},
        {"family": "market_regime", "horizon_sec": 21600, "primary_label": "range_candidate", "read_only": True, "would_send_to_broker": False},
    ])
    _write_json(root / "state/collector_vnext/unified_market_state_status.json", {
        "ts": "2026-07-01T16:55:02Z",
        "lane_state": "live",
        "last_symbol_raw": "FX_BTC_JPY",
        "read_only": True,
        "would_send_to_broker": False,
    })
    _write_json(root / "state/collector_vnext/unified_health.json", {
        "ts": "2026-07-01T16:55:02Z",
        "ok": True,
        "ws_state": "LIVE",
        "read_only": True,
        "would_send_to_broker": False,
    })
    _write_json(root / "state/collector_vnext/unified_executions_status.json", {
        "ts": "2026-07-01T16:55:02Z",
        "ws_state": "LIVE",
        "read_only": True,
        "would_send_to_broker": False,
    })
    _write_json(root / "state/collector_vnext/unified_daemon_status.json", {
        "ts": "2026-07-01T16:55:02Z",
        "read_only": True,
        "would_send_to_broker": False,
    })


def test_q27h_manifest_resolvers_are_read_only(tmp_path: Path) -> None:
    _build_fixture(tmp_path)
    manifest = load_latest_manifest(tmp_path)
    assert manifest.ok is True
    assert manifest.exists is True
    assert resolve_latest_prediction_relative_path(manifest.data) == "prediction/latest_prediction_system_result.json"
    assert resolve_forecast_records_relative_path(manifest.data) == "prediction/runs/2026-07-01/165500/forecast_records.jsonl"
    assert manifest.safety.read_only is True
    assert manifest.safety.runtime_artifact_write_allowed is False


def test_q27h_forecast_records_reader_filters_market_regime(tmp_path: Path) -> None:
    _build_fixture(tmp_path)
    snapshot = load_forecast_records_snapshot(tmp_path, "prediction/runs/2026-07-01/165500/forecast_records.jsonl")
    assert snapshot.ok is True
    assert snapshot.record_count == 3
    assert snapshot.market_regime_record_count == 2
    assert snapshot.market_regime_horizons_sec == (300, 21600)
    assert all(record["family"] == "market_regime" for record in snapshot.market_regime_records)
    assert snapshot.safety.would_send_to_broker is False


def test_q27h_snapshot_builder_composes_manifest_records_and_nowcast(tmp_path: Path) -> None:
    _build_fixture(tmp_path)
    snapshot = build_market_regime_source_snapshot(tmp_path)
    data = snapshot.to_dict()
    assert data["ok"] is True
    assert data["latest_manifest"]["ok"] is True
    assert data["latest_prediction"]["ok"] is True
    assert data["forecast_records"]["market_regime_horizons_sec"] == [300, 21600]
    assert data["nowcast"]["ok"] is True
    assert data["warroom_candles"]["ok"] is False
    assert "warroom_candles_missing_or_unavailable" in data["warnings"]
    assert data["missing_sources"] == []
    assert data["safety"]["read_only"] is True
    for key in (
        "runtime_artifact_write_allowed",
        "scheduler_enabled",
        "producer_enabled",
        "autotrade_trigger_allowed",
        "broker_private_api_allowed",
        "ledger_append_allowed",
        "mode_apply_allowed",
        "parameter_apply_allowed",
        "would_send_to_broker",
    ):
        assert data["safety"][key] is False


def test_q27h_missing_sources_are_reported_without_exception(tmp_path: Path) -> None:
    snapshot = build_market_regime_source_snapshot(tmp_path)
    assert snapshot.ok is False
    assert "latest_manifest" in snapshot.missing_sources
    assert "forecast_records" in snapshot.missing_sources
    assert "collector_market_state" in snapshot.missing_sources
    assert "collector_health" in snapshot.missing_sources


def test_q27h_resolve_under_root_blocks_path_escape(tmp_path: Path) -> None:
    try:
        resolve_under_root(tmp_path, "../outside.json")
    except ValueError as exc:
        assert "escapes source root" in str(exc)
    else:
        raise AssertionError("path escape was not blocked")


def test_q27h_source_adapter_contract_has_no_write_or_ui_defaults() -> None:
    safety = SourceAdapterSafetyFlags().to_dict()
    assert safety["read_only"] is True
    assert safety["non_executing"] is True
    for key in (
        "runtime_artifact_write_allowed",
        "status_artifact_write_allowed",
        "prediction_artifact_write_allowed",
        "view_artifact_write_allowed",
        "scheduler_enabled",
        "producer_enabled",
        "autotrade_trigger_allowed",
        "broker_private_api_allowed",
        "ledger_append_allowed",
        "mode_apply_allowed",
        "parameter_apply_allowed",
        "would_send_to_broker",
    ):
        assert safety[key] is False


def test_q27h_source_modules_do_not_import_ui_or_runtime_paths() -> None:
    package_root = Path(__file__).resolve().parents[1] / "market_regime"
    forbidden = ("import streamlit", "from streamlit", "runtime_root(", "send_to_broker(", "append_ledger(", "ledger.append(", "open(\"D:")
    for path in list(package_root.glob("*.py")) + list((package_root / "sources").glob("*.py")):
        text = path.read_text(encoding="utf-8-sig")
        for token in forbidden:
            assert token not in text, f"forbidden token {token!r} found in {path}"
