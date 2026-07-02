# path: ./btcts_next/src/btcts/apps/operator_ui/tests/test_market_regime_real_preview_default_q28a.py
# desc: PS-Q28A guard. WarRoom market-regime cards default to real D-hot read-only preview with sample fallback. No new UI copy.

from __future__ import annotations

import json
import sys
from pathlib import Path

_SRC_ROOT = Path(__file__).resolve().parents[4]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

from btcts.apps.operator_ui.views.warroom_page import (  # noqa: E402
    WARROOM_MARKET_REGIME_CARD_PREVIEW_HOT_ROOT_HINT,
    build_warroom_market_regime_card_preview_enablement_packet,
)
from btcts.apps.operator_ui.prediction_warroom.panels.warroom_market_regime_card_panel import (  # noqa: E402
    build_warroom_market_regime_card_preview_switch_packet,
)

REPO_ROOT = Path(__file__).resolve().parents[6]
WARROOM_PAGE = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/views/warroom_page.py"
PANEL = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/prediction_warroom/panels/warroom_market_regime_card_panel.py"
DOC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q28A_WARROOM_MARKET_REGIME_REAL_PREVIEW_DEFAULT_2026-07-02.md"


def _write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")


def _write_jsonl(path: Path, records: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(json.dumps(record, ensure_ascii=False) for record in records) + "\n", encoding="utf-8")


def _build_fixture(root: Path) -> None:
    forecast_path = root / "prediction/runs/2026-07-02/020000/forecast_records.jsonl"
    _write_json(root / "prediction/latest_manifest.json", {
        "generated_at": "2026-07-02T02:00:00Z",
        "legacy_latest_path": "prediction/latest_prediction_system_result.json",
        "sidecars": {"forecast_records": "prediction/runs/2026-07-02/020000/forecast_records.jsonl"},
    })
    _write_json(root / "prediction/latest_prediction_system_result.json", {"read_only": True, "non_executing": True})
    _write_jsonl(forecast_path, [
        {
            "family": "market_regime",
            "horizon_sec": 15,
            "primary_label": "range_candidate",
            "score": 0.52,
            "values_snapshot": {"estimated_signal_strength_percent": 51, "estimated_reference_hit_rate_percent": 51, "volatility_state": "compressed", "cross_venue_agreement": "confirmed"},
        },
        {
            "family": "market_regime",
            "horizon_sec": 300,
            "primary_label": "trend_candidate",
            "score": 0.92,
            "values_snapshot": {"estimated_signal_strength_percent": 90, "estimated_reference_hit_rate_percent": 85, "volatility_state": "compressed", "cross_venue_agreement": "confirmed"},
        },
        {
            "family": "market_regime",
            "horizon_sec": 86400,
            "primary_label": "breakout_candidate",
            "score": 0.92,
            "values_snapshot": {"estimated_signal_strength_percent": 90, "estimated_reference_hit_rate_percent": 85, "volatility_state": "compressed", "cross_venue_agreement": "confirmed"},
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
    _write_json(root / "state/collector_vnext/unified_executions_status.json", {"ws_state": "LIVE", "trade_count": 31500, "read_only": True, "would_send_to_broker": False})
    _write_json(root / "state/collector_vnext/unified_daemon_status.json", {"read_only": True, "would_send_to_broker": False})


def test_q28a_doc_records_real_preview_default_boundary() -> None:
    text = DOC.read_text(encoding="utf-8-sig")
    assert "ps_q28a_warroom_market_regime_real_preview_default=true" in text
    assert "warroom_market_regime_real_preview_default_on=true" in text
    assert "ui_copy_added=false" in text
    assert "would_send_to_broker=false" in text


def test_q28a_enablement_default_is_real_preview_read_only() -> None:
    packet = build_warroom_market_regime_card_preview_enablement_packet(generated_at="2026-07-02T02:00:03Z")
    assert packet["preview_enabled_requested"] is True
    assert packet["operator_confirmed_read_only"] is True
    assert packet["preview_enabled_effective"] is True
    assert packet["disabled_reason"] == ""
    assert packet["warroom_page_preview_default_on"] is True
    assert packet["explicit_operator_checkbox_required"] is False
    assert packet["explicit_source_root_read_allowed"] is True
    assert packet["render_kwargs"] == {
        "preview_enabled": True,
        "hot_root": WARROOM_MARKET_REGIME_CARD_PREVIEW_HOT_ROOT_HINT,
        "generated_at": "2026-07-02T02:00:03Z",
    }
    assert packet["would_send_to_broker"] is False


def test_q28a_operator_can_still_disable_preview_to_sample_only() -> None:
    packet = build_warroom_market_regime_card_preview_enablement_packet(
        preview_enabled=False,
        operator_confirmed_read_only=False,
        generated_at="2026-07-02T02:00:03Z",
    )
    assert packet["preview_enabled_effective"] is False
    assert packet["disabled_reason"] == "preview_checkbox_off"
    assert packet["render_kwargs"] == {"preview_enabled": False, "hot_root": None, "generated_at": "2026-07-02T02:00:03Z"}
    renderer_packet = build_warroom_market_regime_card_preview_switch_packet(**packet["render_kwargs"])
    assert renderer_packet["sample_data_only"] is True
    assert renderer_packet["explicit_source_root_read_performed"] is False


def test_q28a_default_enablement_feeds_real_preview_cards_when_root_available(tmp_path: Path) -> None:
    _build_fixture(tmp_path)
    packet = build_warroom_market_regime_card_preview_enablement_packet(
        hot_root=str(tmp_path),
        generated_at="2026-07-02T02:00:03Z",
    )
    renderer_packet = build_warroom_market_regime_card_preview_switch_packet(**packet["render_kwargs"])
    assert renderer_packet["preview_cards_used"] is True
    assert renderer_packet["sample_data_only"] is False
    assert renderer_packet["explicit_source_root_read_performed"] is True
    assert renderer_packet["dry_run_version"] is not None
    assert renderer_packet["stage_versions"]["classifier"] == "prediction.market_regime.regime_classifier.ps_q27z.v1"
    by_horizon = {card["horizon"]: card for card in renderer_packet["cards"]}
    assert by_horizon["現在"]["regime_code"] == "RANGE"
    assert by_horizon["5分後"]["regime_code"] == "UP_TREND"
    assert by_horizon["24時間後"]["regime_code"] == "BREAKOUT"
    assert renderer_packet["would_send_to_broker"] is False


def test_q28a_warroom_page_default_checkbox_on_without_new_copy() -> None:
    page_text = WARROOM_PAGE.read_text(encoding="utf-8-sig")
    panel_text = PANEL.read_text(encoding="utf-8-sig")
    assert "warroom_market_regime_card_preview_enabled_q27p" in page_text
    assert '"地合い preview"' in page_text
    assert "value=True" in page_text
    assert "value=False" not in page_text.split('"地合い preview"', 1)[1].split("key=\"warroom_market_regime_card_preview_enabled_q27p\"", 1)[0]
    assert "preview_enabled=True" not in page_text
    assert "地合いカード preview はデフォルトOFF" not in page_text
    for text in (page_text, panel_text):
        for token in (
            "send_to_broker(",
            "append_ledger(",
            "ledger.append(",
            "write_runtime_artifact(",
            "write_prediction_artifact(",
            "write_status_artifact(",
        ):
            assert token not in text
