# path: ./btcts_next/src/btcts/apps/operator_ui/tests/test_market_regime_live_preview_dry_run_q27l.py
# desc: PS-Q27L tests for read-only live-preview dry-run composition. Uses tmp_path only; no real D-hot access or UI mount.

from __future__ import annotations

import json
import sys
from pathlib import Path

_SRC_ROOT = Path(__file__).resolve().parents[4]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

from btcts.apps.operator_ui.prediction_warroom.market_regime import (  # noqa: E402
    WARROOM_MARKET_REGIME_LIVE_PREVIEW_DRY_RUN_VERSION,
    build_market_regime_live_preview_dry_run_packet,
)

REPO_ROOT = Path(__file__).resolve().parents[6]
WARROOM_PAGE = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/views/warroom_page.py"
RENDERER = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/prediction_warroom/panels/warroom_market_regime_card_panel.py"
DRY_RUN_MODULE = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/prediction_warroom/market_regime/live_preview_dry_run.py"


def _write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")


def _write_jsonl(path: Path, records: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(json.dumps(record, ensure_ascii=False) for record in records) + "\n", encoding="utf-8")


def _build_fixture(root: Path, *, label: str = "range_candidate", spread: float = -1479.0) -> None:
    forecast_path = root / "prediction/runs/2026-07-01/173500/forecast_records.jsonl"
    _write_json(root / "prediction/latest_manifest.json", {
        "generated_at": "2026-07-01T17:35:00Z",
        "legacy_latest_path": "prediction/latest_prediction_system_result.json",
        "sidecars": {"forecast_records": "prediction/runs/2026-07-01/173500/forecast_records.jsonl"},
    })
    _write_json(root / "prediction/latest_prediction_system_result.json", {"read_only": True, "non_executing": True})
    _write_jsonl(forecast_path, [
        {"family": "market_regime", "horizon_sec": 300, "primary_label": label, "values": {"volatility_state": "normal", "cross_venue_agreement": "aligned"}},
        {"family": "market_regime", "horizon_sec": 21600, "primary_label": label, "values": {"volatility_state": "normal", "cross_venue_agreement": "aligned"}},
    ])
    _write_json(root / "state/collector_vnext/unified_market_state_status.json", {
        "last_symbol_raw": "FX_BTC_JPY",
        "last_best_bid": 9729064.0,
        "last_best_ask": 9727585.0,
        "last_spread": spread,
        "read_only": True,
        "would_send_to_broker": False,
    })
    _write_json(root / "state/collector_vnext/unified_health.json", {"ok": True, "ws_state": "LIVE", "read_only": True, "would_send_to_broker": False})
    _write_json(root / "state/collector_vnext/unified_executions_status.json", {"ws_state": "LIVE", "trade_count": 20450, "read_only": True, "would_send_to_broker": False})
    _write_json(root / "state/collector_vnext/unified_daemon_status.json", {"read_only": True, "would_send_to_broker": False})


def test_q27l_live_preview_dry_run_composes_full_pipeline_with_tmp_path(tmp_path: Path) -> None:
    _build_fixture(tmp_path)
    packet = build_market_regime_live_preview_dry_run_packet(tmp_path, generated_at="2026-07-01T17:35:03Z")
    assert packet["ok"] is True
    assert packet["dry_run_version"] == WARROOM_MARKET_REGIME_LIVE_PREVIEW_DRY_RUN_VERSION
    assert packet["source_snapshot_ok"] is True
    assert packet["card_count"] == 8
    assert packet["horizons"] == ["現在", "5分後", "15分後", "30分後", "60分後", "6時間後", "12時間後", "24時間後"]
    assert packet["cards"][0]["regime_code"] == "RANGE"
    assert packet["cards"][0]["short_tag"] == "NO_NEW_ENTRY"
    assert packet["cards"][0]["extra"]["would_send_to_broker"] is False


def test_q27l_stage_versions_and_flags_show_dry_run_only(tmp_path: Path) -> None:
    _build_fixture(tmp_path, label="trend_candidate", spread=1200.0)
    packet = build_market_regime_live_preview_dry_run_packet(tmp_path, generated_at="2026-07-01T17:35:03Z")
    assert packet["stage_versions"]["source_snapshot"] == "prediction.market_regime.source_snapshot.ps_q27h.v1"
    assert packet["stage_versions"]["feature_bundle"] == "prediction.market_regime.feature_bundle.ps_q27i.v1"
    assert packet["stage_versions"]["classifier"] == "prediction.market_regime.regime_classifier.ps_q27y.v1"
    assert packet["stage_versions"]["card_adapter"] == "prediction_warroom.market_regime_card_adapter.ps_q27k.v1"
    assert packet["market_regime_only"] is True
    assert packet["live_preview_dry_run"] is True
    assert packet["explicit_source_root_read_only"] is True
    assert packet["ui_binding_added"] is False
    assert packet["warroom_page_mounted"] is False
    assert packet["renderer_changed"] is False
    assert packet["live_data_connected"] is False
    assert packet["cards"][0]["regime_code"] == "UP_TREND"


def test_q27l_missing_sources_degrade_to_cards_without_exception(tmp_path: Path) -> None:
    packet = build_market_regime_live_preview_dry_run_packet(tmp_path, generated_at="2026-07-01T17:35:03Z")
    assert packet["ok"] is True
    assert packet["source_snapshot_ok"] is False
    assert "latest_manifest" in packet["source_snapshot_missing_sources"]
    assert packet["card_count"] == 8
    assert {card["regime_code"] for card in packet["cards"]} == {"UNKNOWN"}
    assert {card["short_tag"] for card in packet["cards"]} == {"DATA_MISSING"}


def test_q27l_safety_flags_remain_false(tmp_path: Path) -> None:
    _build_fixture(tmp_path)
    packet = build_market_regime_live_preview_dry_run_packet(tmp_path, generated_at="2026-07-01T17:35:03Z")
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
        assert packet[key] is False


def test_q27l_does_not_mount_page_or_renderer() -> None:
    page_text = WARROOM_PAGE.read_text(encoding="utf-8-sig")
    renderer_text = RENDERER.read_text(encoding="utf-8-sig")
    assert "build_market_regime_live_preview_dry_run_packet" not in page_text
    assert "WARROOM_MARKET_REGIME_LIVE_PREVIEW_DRY_RUN_VERSION" not in page_text
    assert "build_market_regime_live_preview_dry_run_packet" not in renderer_text
    assert "WARROOM_MARKET_REGIME_LIVE_PREVIEW_DRY_RUN_VERSION" not in renderer_text


def test_q27l_dry_run_module_has_no_streamlit_or_write_paths() -> None:
    text = DRY_RUN_MODULE.read_text(encoding="utf-8-sig")
    forbidden = ("import streamlit", "from streamlit", "send_to_broker(", "append_ledger(", "ledger.append(", "open(\"D:")
    for token in forbidden:
        assert token not in text, f"forbidden token {token!r} found in dry-run module"
