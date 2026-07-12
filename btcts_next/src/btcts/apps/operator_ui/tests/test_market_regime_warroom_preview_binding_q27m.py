# path: ./btcts_next/src/btcts/apps/operator_ui/tests/test_market_regime_warroom_preview_binding_q27m.py
# desc: PS-Q27M tests for gated WarRoom market-regime preview binding. Disabled by default; tmp_path only when enabled.

from __future__ import annotations

import json
import sys
from pathlib import Path

_SRC_ROOT = Path(__file__).resolve().parents[4]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

from btcts.apps.operator_ui.prediction_warroom.market_regime import (  # noqa: E402
    WARROOM_MARKET_REGIME_PREVIEW_BINDING_VERSION,
    build_market_regime_warroom_preview_binding_packet,
)

REPO_ROOT = Path(__file__).resolve().parents[6]
WARROOM_PAGE = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/views/warroom_page.py"
RENDERER = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/prediction_warroom/panels/warroom_market_regime_card_panel.py"
BINDING_MODULE = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/prediction_warroom/market_regime/preview_binding.py"


def _write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")


def _write_jsonl(path: Path, records: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(json.dumps(record, ensure_ascii=False) for record in records) + "\n", encoding="utf-8")


def _build_fixture(root: Path) -> None:
    forecast_path = root / "prediction/runs/2026-07-01/174500/forecast_records.jsonl"
    _write_json(root / "prediction/latest_manifest.json", {
        "generated_at": "2026-07-01T17:45:00Z",
        "legacy_latest_path": "prediction/latest_prediction_system_result.json",
        "sidecars": {"forecast_records": "prediction/runs/2026-07-01/174500/forecast_records.jsonl"},
    })
    _write_json(root / "prediction/latest_prediction_system_result.json", {"read_only": True, "non_executing": True})
    _write_jsonl(forecast_path, [
        {"family": "market_regime", "horizon_sec": 300, "primary_label": "range_candidate", "values": {"volatility_state": "normal", "cross_venue_agreement": "aligned"}},
        {"family": "market_regime", "horizon_sec": 21600, "primary_label": "range_candidate", "values": {"volatility_state": "normal", "cross_venue_agreement": "aligned"}},
    ])
    _write_json(root / "state/collector_vnext/unified_market_state_status.json", {
        "last_symbol_raw": "FX_BTC_JPY",
        "last_best_bid": 9729064.0,
        "last_best_ask": 9727585.0,
        "last_spread": -1479.0,
        "read_only": True,
        "would_send_to_broker": False,
    })
    _write_json(root / "state/collector_vnext/unified_health.json", {"ok": True, "ws_state": "LIVE", "read_only": True, "would_send_to_broker": False})
    _write_json(root / "state/collector_vnext/unified_executions_status.json", {"ws_state": "LIVE", "trade_count": 20450, "read_only": True, "would_send_to_broker": False})
    _write_json(root / "state/collector_vnext/unified_daemon_status.json", {"read_only": True, "would_send_to_broker": False})


def test_q27m_preview_binding_is_disabled_by_default_and_does_not_read_root() -> None:
    packet = build_market_regime_warroom_preview_binding_packet(generated_at="2026-07-01T17:45:03Z")
    assert packet["ok"] is True
    assert packet["binding_version"] == WARROOM_MARKET_REGIME_PREVIEW_BINDING_VERSION
    assert packet["preview_enabled"] is False
    assert packet["default_disabled"] is True
    assert packet["dry_run_invoked"] is False
    assert packet["explicit_source_root_read_performed"] is False
    assert packet["card_count"] == 0
    assert packet["disabled_reason"] == "preview_enabled_false"
    assert packet["warroom_page_mounted"] is False


def test_q27m_enabled_binding_requires_explicit_root() -> None:
    packet = build_market_regime_warroom_preview_binding_packet(preview_enabled=True, generated_at="2026-07-01T17:45:03Z")
    assert packet["ok"] is False
    assert packet["preview_enabled"] is True
    assert packet["dry_run_invoked"] is False
    assert packet["explicit_source_root_read_performed"] is False
    assert packet["disabled_reason"] == "explicit_hot_root_required"
    assert packet["missing_required_inputs"] == ["hot_root"]


def test_q27m_enabled_binding_composes_cards_from_tmp_path_only(tmp_path: Path) -> None:
    _build_fixture(tmp_path)
    packet = build_market_regime_warroom_preview_binding_packet(preview_enabled=True, hot_root=tmp_path, generated_at="2026-07-01T17:45:03Z")
    assert packet["ok"] is True
    assert packet["preview_enabled"] is True
    assert packet["dry_run_invoked"] is True
    assert packet["explicit_source_root_read_performed"] is True
    assert packet["card_count"] == 8
    assert packet["horizons"] == ["現在", "5分後", "15分後", "30分後", "60分後", "6時間後", "12時間後", "24時間後"]
    by_horizon = {card["horizon"]: card for card in packet["cards"]}
    assert by_horizon["現在"]["regime_code"] == "UNKNOWN"
    assert by_horizon["5分後"]["regime_code"] == "RANGE"
    assert by_horizon["5分後"]["short_tag"] == "NO_NEW_ENTRY"
    assert packet["stage_versions"]["classifier"] == "prediction.market_regime.regime_classifier.ps_q27z.v3"


def test_q27m_binding_flags_stay_preview_gated_and_display_only(tmp_path: Path) -> None:
    _build_fixture(tmp_path)
    packet = build_market_regime_warroom_preview_binding_packet(preview_enabled=True, hot_root=tmp_path, generated_at="2026-07-01T17:45:03Z")
    assert packet["preview_binding_gated"] is True
    assert packet["ui_binding_added"] is False
    assert packet["warroom_page_changed"] is False
    assert packet["warroom_page_mounted"] is False
    assert packet["renderer_changed"] is False
    assert packet["streamlit_render_invoked_by_page"] is False
    assert packet["live_data_connected"] is False
    assert packet["read_only"] is True
    assert packet["display_only"] is True
    assert packet["non_executing"] is True
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


def test_q27m_does_not_mount_page_or_renderer() -> None:
    page_text = WARROOM_PAGE.read_text(encoding="utf-8-sig")
    renderer_text = RENDERER.read_text(encoding="utf-8-sig")
    assert "build_market_regime_warroom_preview_binding_packet" not in page_text
    assert "WARROOM_MARKET_REGIME_PREVIEW_BINDING_VERSION" not in page_text
    assert "preview_enabled=True" not in page_text
    assert "build_warroom_market_regime_card_preview_enablement_packet" in page_text
    assert "warroom_market_regime_card_preview_enabled_q27p" in page_text
    assert "render_kwargs" in page_text

    # PS-Q27O intentionally allows the renderer/panel to call the gated binding
    # only through an explicit preview switch. This is not a WarRoom page mount.
    assert "build_warroom_market_regime_card_preview_switch_packet" in renderer_text
    assert "build_market_regime_warroom_preview_binding_packet" in renderer_text
    assert "preview_enabled: bool = False" in renderer_text
    assert "default_sample_only_when_disabled" in renderer_text
    assert "warroom_page_mounted" in renderer_text


def test_q27m_binding_module_has_no_streamlit_or_write_paths() -> None:
    text = BINDING_MODULE.read_text(encoding="utf-8-sig")
    forbidden = ("import streamlit", "from streamlit", "send_to_broker(", "append_ledger(", "ledger.append(", "open(\"D:")
    for token in forbidden:
        assert token not in text, f"forbidden token {token!r} found in binding module"
