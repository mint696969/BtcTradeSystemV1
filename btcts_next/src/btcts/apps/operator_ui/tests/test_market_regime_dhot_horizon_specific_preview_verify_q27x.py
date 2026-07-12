# path: ./btcts_next/src/btcts/apps/operator_ui/tests/test_market_regime_dhot_horizon_specific_preview_verify_q27x.py
# desc: PS-Q27X guard. Verifies D-hot-like read-only preview path uses the current horizon-specific classifier. No production code change.

from __future__ import annotations

import json
import sys
from pathlib import Path

_SRC_ROOT = Path(__file__).resolve().parents[4]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

from btcts.apps.operator_ui.prediction_warroom.market_regime import build_market_regime_warroom_preview_binding_packet  # noqa: E402
from btcts.prediction.market_regime import FeatureGroup, MarketRegimeCode  # noqa: E402
from btcts.prediction.market_regime.features import build_market_regime_feature_bundle  # noqa: E402
from btcts.prediction.market_regime.inference import classify_market_regime_feature_bundle  # noqa: E402
from btcts.prediction.market_regime.sources import build_market_regime_source_snapshot  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parents[6]
DOC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q27X_MARKET_REGIME_DHOT_HORIZON_SPECIFIC_PREVIEW_VERIFY_2026-07-02.md"
WARROOM_PAGE = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/views/warroom_page.py"
PANEL = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/prediction_warroom/panels/warroom_market_regime_card_panel.py"


def _write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")


def _write_jsonl(path: Path, records: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(json.dumps(record, ensure_ascii=False) for record in records) + "\n", encoding="utf-8")


def _build_dhot_like_fixture(root: Path) -> None:
    forecast_path = root / "prediction/runs/2026-07-02/012022_generated_at_2026-07-02T01_20_22Z/forecast_records.jsonl"
    _write_json(root / "prediction/latest_manifest.json", {
        "generated_at": "2026-07-02T01:20:22Z",
        "legacy_latest_path": "prediction/latest_prediction_system_result.json",
        "record_count": 110,
        "sidecars": {"forecast_records": "prediction/runs/2026-07-02/012022_generated_at_2026-07-02T01_20_22Z/forecast_records.jsonl"},
    })
    _write_json(root / "prediction/latest_prediction_system_result.json", {"read_only": True, "non_executing": True})
    records = []
    for horizon, label in (
        (15, "range_candidate"),
        (30, "range_candidate"),
        (60, "volatile_or_divergent"),
        (300, "trend_candidate"),
        (900, "range_candidate"),
        (1800, "breakout_candidate"),
        (3600, "reversal_watch"),
        (14400, "range_candidate"),
        (86400, "breakout_candidate"),
    ):
        records.append({
            "family": "market_regime",
            "horizon_sec": horizon,
            "primary_label": label,
            "values_snapshot": {"volatility_state": "compressed", "cross_venue_agreement": "confirmed"},
            "read_only": True,
            "would_send_to_broker": False,
            "would_write_runtime_artifact": False,
        })
    _write_jsonl(forecast_path, records)
    _write_json(root / "state/collector_vnext/unified_market_state_status.json", {
        "last_symbol_raw": "FX_BTC_JPY",
        "last_best_bid": 9764512.0,
        "last_best_ask": 9765366.0,
        "last_spread": 854.0,
        "read_only": True,
        "would_send_to_broker": False,
    })
    _write_json(root / "state/collector_vnext/unified_health.json", {"ok": True, "ws_state": "LIVE", "read_only": True, "would_send_to_broker": False})
    _write_json(root / "state/collector_vnext/unified_executions_status.json", {"ws_state": "LIVE", "trade_count": 31500, "read_only": True, "would_send_to_broker": False})
    _write_json(root / "state/collector_vnext/unified_daemon_status.json", {"read_only": True, "would_send_to_broker": False})


def test_q27x_doc_records_dhot_horizon_specific_verify_boundary() -> None:
    text = DOC.read_text(encoding="utf-8-sig")
    assert "ps_q27x_market_regime_dhot_horizon_specific_preview_verify=true" in text
    assert "production_code_changed=false" in text
    assert "production_ui_code_changed=false" in text
    assert "real_dhot_probe_runner_added=true" in text
    assert "classifier_version=prediction.market_regime.regime_classifier.ps_q27z.v1" in text
    assert "would_send_to_broker=false" in text


def test_q27x_dhot_like_source_snapshot_exposes_horizon_specific_labels(tmp_path: Path) -> None:
    _build_dhot_like_fixture(tmp_path)
    snapshot = build_market_regime_source_snapshot(tmp_path)
    bundle = build_market_regime_feature_bundle(snapshot, generated_at="2026-07-02T01:20:23Z")
    price_signals = {signal.name: signal for signal in bundle.signals_by_group(FeatureGroup.PRICE_STRUCTURE)}
    labels = price_signals["market_regime_labels_by_horizon_sec"].value
    assert labels["15"] == "range_candidate"
    assert labels["300"] == "trend_candidate"
    assert labels["1800"] == "breakout_candidate"
    assert labels["3600"] == "reversal_watch"
    assert labels["86400"] == "breakout_candidate"
    assert bundle.source_snapshot_ok is True


def test_q27x_classifier_uses_dhot_like_horizon_specific_labels(tmp_path: Path) -> None:
    _build_dhot_like_fixture(tmp_path)
    snapshot = build_market_regime_source_snapshot(tmp_path)
    bundle = build_market_regime_feature_bundle(snapshot, generated_at="2026-07-02T01:20:23Z")
    packet = classify_market_regime_feature_bundle(bundle, generated_at="2026-07-02T01:20:24Z")
    by_horizon = {prediction.horizon_sec: prediction for prediction in packet.predictions}
    assert packet.logic_version == "prediction.market_regime.regime_classifier.ps_q27z.v3"
    assert by_horizon[0].diagnostic_record["selected_forecast_horizon_sec"] is None
    assert by_horizon[0].diagnostic_record["label_selection_reason"] == "current_state_estimator_unavailable"
    assert by_horizon[0].diagnostic_record["future_forecast_label_used_for_current"] is False
    assert by_horizon[0].regime_code == MarketRegimeCode.UNKNOWN
    assert by_horizon[300].regime_code == MarketRegimeCode.UP_TREND
    assert by_horizon[1800].regime_code == MarketRegimeCode.BREAKOUT
    assert by_horizon[3600].regime_code == MarketRegimeCode.REVERSAL_WATCH
    assert by_horizon[86400].regime_code == MarketRegimeCode.BREAKOUT
    missing_horizon = by_horizon[43200]
    assert missing_horizon.diagnostic_record["label_selection_reason"] == "forecast_horizon_label_missing"
    assert missing_horizon.diagnostic_record["selected_label"] == ""
    assert missing_horizon.diagnostic_record["selected_label_source"] == "none"
    assert missing_horizon.regime_code == MarketRegimeCode.UNKNOWN
    assert missing_horizon.confidence_percent == 15
    assert missing_horizon.freshness_state.value == "STALE"
    assert missing_horizon.evidence_quality.value == "MISSING"
    assert all(prediction.diagnostic_record["horizon_specific_classifier"] is True for prediction in packet.predictions)
    assert packet.safety.would_send_to_broker is False


def test_q27x_warroom_preview_binding_uses_ps_q27z_stage_version_without_ui_change(tmp_path: Path) -> None:
    _build_dhot_like_fixture(tmp_path)
    packet = build_market_regime_warroom_preview_binding_packet(preview_enabled=True, hot_root=tmp_path, generated_at="2026-07-02T01:20:24Z")
    assert packet["ok"] is True
    assert packet["dry_run_invoked"] is True
    assert packet["explicit_source_root_read_performed"] is True
    assert packet["source_snapshot_ok"] is True
    assert packet["stage_versions"]["classifier"] == "prediction.market_regime.regime_classifier.ps_q27z.v3"
    assert packet["card_count"] == 8
    by_horizon = {card["horizon"]: card for card in packet["cards"]}
    assert by_horizon["現在"]["regime_code"] == "UNKNOWN"
    assert by_horizon["5分後"]["regime_code"] == "UP_TREND"
    assert by_horizon["30分後"]["regime_code"] == "BREAKOUT"
    assert by_horizon["60分後"]["regime_code"] == "REVERSAL_WATCH"
    assert by_horizon["24時間後"]["regime_code"] == "BREAKOUT"
    assert packet["live_data_connected"] is False
    assert packet["would_send_to_broker"] is False


def test_q27x_no_ui_or_execution_paths_changed() -> None:
    page_text = WARROOM_PAGE.read_text(encoding="utf-8-sig")
    panel_text = PANEL.read_text(encoding="utf-8-sig")
    assert "地合い preview" in page_text
    assert "preview_enabled=True" not in page_text
    for text in (page_text, panel_text):
        for token in (
            "send_to_broker(",
            "append_ledger(",
            "ledger.append(",
            "write_runtime_artifact(",
            "write_prediction_artifact(",
            "open(\"D:",
        ):
            assert token not in text
