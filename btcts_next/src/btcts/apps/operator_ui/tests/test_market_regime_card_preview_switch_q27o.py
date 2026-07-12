# path: ./btcts_next/src/btcts/apps/operator_ui/tests/test_market_regime_card_preview_switch_q27o.py
# desc: PS-Q27O tests for WarRoom market-regime sample-to-preview switch. Operator can still choose sample-only.

from __future__ import annotations

import json
import sys
from pathlib import Path

_SRC_ROOT = Path(__file__).resolve().parents[4]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

from btcts.apps.operator_ui.prediction_warroom.panels.warroom_market_regime_card_panel import (  # noqa: E402
    WARROOM_MARKET_REGIME_CARD_PREVIEW_SWITCH_VERSION,
    build_warroom_market_regime_card_preview_switch_packet,
)

REPO_ROOT = Path(__file__).resolve().parents[6]
WARROOM_PAGE = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/views/warroom_page.py"
PANEL = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/prediction_warroom/panels/warroom_market_regime_card_panel.py"


def _write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")


def _write_jsonl(path: Path, records: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(json.dumps(record, ensure_ascii=False) for record in records) + "\n", encoding="utf-8")


def _build_fixture(root: Path) -> None:
    forecast_path = root / "prediction/runs/2026-07-01/181000/forecast_records.jsonl"
    _write_json(root / "prediction/latest_manifest.json", {
        "generated_at": "2026-07-01T18:10:00Z",
        "legacy_latest_path": "prediction/latest_prediction_system_result.json",
        "sidecars": {"forecast_records": "prediction/runs/2026-07-01/181000/forecast_records.jsonl"},
    })
    _write_json(root / "prediction/latest_prediction_system_result.json", {"read_only": True, "non_executing": True})
    _write_jsonl(forecast_path, [
        {
            "family": "market_regime",
            "horizon_sec": 15,
            "primary_label": "range_candidate",
            "values_snapshot": {"volatility_state": "compressed", "cross_venue_agreement": "confirmed"},
        },
        {
            "family": "market_regime",
            "horizon_sec": 86400,
            "primary_label": "range_candidate",
            "values_snapshot": {"volatility_state": "compressed", "cross_venue_agreement": "confirmed"},
        },
    ])
    _write_json(root / "state/collector_vnext/unified_market_state_status.json", {
        "last_symbol_raw": "FX_BTC_JPY",
        "last_best_bid": 9764512.0,
        "last_best_ask": 9765366.0,
        "last_spread": 854.0,
        "read_only": True,
        "would_send_to_broker": False,
    })
    _write_json(root / "state/collector_vnext/unified_health.json", {"ok": True, "ws_state": "LIVE", "read_only": True, "would_send_to_broker": False})
    _write_json(root / "state/collector_vnext/unified_executions_status.json", {"ws_state": "LIVE", "trade_count": 22016, "read_only": True, "would_send_to_broker": False})
    _write_json(root / "state/collector_vnext/unified_daemon_status.json", {"read_only": True, "would_send_to_broker": False})


def test_q27o_preview_switch_default_is_sample_only_and_does_not_read_root(tmp_path: Path) -> None:
    packet = build_warroom_market_regime_card_preview_switch_packet(
        preview_enabled=False,
        hot_root=tmp_path / "does_not_exist",
        generated_at="2026-07-01T18:10:03Z",
    )
    assert packet["preview_switch_version"] == WARROOM_MARKET_REGIME_CARD_PREVIEW_SWITCH_VERSION
    assert packet["preview_switch_added"] is True
    assert packet["preview_enabled"] is False
    assert packet["sample_data_only"] is True
    assert packet["explicit_source_root_read_performed"] is False
    assert packet["dry_run_invoked"] is False
    assert packet["live_data_connected"] is False
    assert packet["card_count"] == 8
    assert packet["cards"][0]["extra"]["sample_only"] is True


def test_q27o_preview_switch_enabled_uses_explicit_tmp_root_cards(tmp_path: Path) -> None:
    _build_fixture(tmp_path)
    packet = build_warroom_market_regime_card_preview_switch_packet(
        preview_enabled=True,
        hot_root=tmp_path,
        generated_at="2026-07-01T18:10:03Z",
    )
    assert packet["preview_enabled"] is True
    assert packet["sample_data_only"] is False
    assert packet["preview_cards_used"] is True
    assert packet["explicit_source_root_read_performed"] is True
    assert packet["dry_run_invoked"] is True
    assert packet["card_count"] == 8
    by_horizon = {card["horizon"]: card for card in packet["cards"]}
    assert by_horizon["現在"]["regime_code"] == "UNKNOWN"
    assert by_horizon["現在"]["confidence_percent"] == 15
    assert by_horizon["24時間後"]["regime_code"] == "RANGE"
    assert by_horizon["24時間後"]["short_tag"] == "NO_DIRECTION"
    assert by_horizon["24時間後"]["confidence_percent"] >= 70


def test_q27o_preview_switch_enabled_without_root_falls_back_to_sample() -> None:
    packet = build_warroom_market_regime_card_preview_switch_packet(
        preview_enabled=True,
        hot_root=None,
        generated_at="2026-07-01T18:10:03Z",
    )
    assert packet["preview_enabled"] is True
    assert packet["preview_cards_used"] is False
    assert packet["sample_data_only"] is True
    assert packet["explicit_source_root_read_performed"] is False
    assert packet["dry_run_invoked"] is False
    assert packet["preview_disabled_reason"] == "explicit_hot_root_required"
    assert packet["card_count"] == 8


def test_q27o_preview_switch_page_default_preview_enabled_read_only() -> None:
    page_text = WARROOM_PAGE.read_text(encoding="utf-8-sig")
    assert "build_warroom_market_regime_card_preview_enablement_packet" in page_text
    assert "warroom_market_regime_card_preview_enabled_q27p" in page_text
    assert "value=True" in page_text
    assert "render_kwargs" in page_text
    assert "preview_enabled=True" not in page_text
    assert "build_warroom_market_regime_card_preview_switch_packet" not in page_text
    assert 'render_warroom_focus_section("market_regime_card_sample")' in page_text


def test_q27o_preview_switch_flags_remain_display_only(tmp_path: Path) -> None:
    _build_fixture(tmp_path)
    packet = build_warroom_market_regime_card_preview_switch_packet(
        preview_enabled=True,
        hot_root=tmp_path,
        generated_at="2026-07-01T18:10:03Z",
    )
    assert packet["warroom_page_changed"] is False
    assert packet["warroom_page_mounted"] is False
    assert packet["streamlit_render_function_declared"] is True
    assert packet["streamlit_render_invoked_by_page"] is False
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


def test_q27o_panel_has_no_new_broker_or_artifact_write_paths() -> None:
    text = PANEL.read_text(encoding="utf-8-sig")
    forbidden = ("send_to_broker(", "append_ledger(", "ledger.append(", "write_runtime_artifact(", "write_status_artifact(", "write_prediction_artifact(", "open(\"D:")
    for token in forbidden:
        assert token not in text, f"forbidden token {token!r} found in panel"
