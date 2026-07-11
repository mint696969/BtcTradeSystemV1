# path: ./btcts_next/src/btcts/apps/operator_ui/tests/test_market_regime_card_ui_smoke_q27q.py
# desc: PS-Q27Q WarRoom market-regime card UI smoke. Verifies preview OFF/ON paths against Q26W/Q27E card specs; tmp_path only.

from __future__ import annotations

import json
import sys
from pathlib import Path

_SRC_ROOT = Path(__file__).resolve().parents[4]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

from btcts.apps.operator_ui.views.warroom_page import (  # noqa: E402
    build_warroom_market_regime_card_preview_enablement_packet,
)
from btcts.apps.operator_ui.prediction_warroom.panels.warroom_market_regime_card_panel import (  # noqa: E402
    build_warroom_market_regime_card_preview_switch_packet,
    market_regime_cards_html,
)

REPO_ROOT = Path(__file__).resolve().parents[6]
SPEC_Q26W = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q26W_MARKET_REGIME_CARD_SPEC_2026-07-01.md"
SPEC_Q27E = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q27E_WARROOM_CARD_UI_REUSE_SPEC_2026-07-02.md"
PANEL = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/prediction_warroom/panels/warroom_market_regime_card_panel.py"
WARROOM_PAGE = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/views/warroom_page.py"

EXPECTED_HORIZONS = ["現在", "5分後", "15分後", "30分後", "60分後", "6時間後", "12時間後", "24時間後"]


def _write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")


def _write_jsonl(path: Path, records: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(json.dumps(record, ensure_ascii=False) for record in records) + "\n", encoding="utf-8")


def _build_fixture(root: Path) -> None:
    forecast_path = root / "prediction/runs/2026-07-01/183000/forecast_records.jsonl"
    _write_json(root / "prediction/latest_manifest.json", {
        "generated_at": "2026-07-01T18:30:00Z",
        "legacy_latest_path": "prediction/latest_prediction_system_result.json",
        "sidecars": {"forecast_records": "prediction/runs/2026-07-01/183000/forecast_records.jsonl"},
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


def _assert_card_spec_shape(packet: dict) -> None:
    assert packet["card_count"] == 8
    assert packet["horizons"] == EXPECTED_HORIZONS
    assert packet["horizontal_scroll_required"] is True
    assert packet["cards_do_not_shrink"] is True
    assert packet["card_width_px"] == 208
    assert packet["freshness_encoded_by_badge_only"] is True
    assert packet["border_meaning"] == "evidence_quality"
    assert packet["confidence_meaning"] == "market_regime_classification_certainty_not_win_rate"
    assert packet["detail_disclosure_mode"] == "card_overlay"
    assert packet["card_detail_overlay_enabled"] is True
    assert packet["no_vertical_layout_shift_on_detail_open"] is True
    for card in packet["cards"]:
        assert len(card["card_lines"]) == 3
        assert card["freshness_badge"] in {"LIVE", "WARM", "STALE", "MISSING"}
        assert card["confidence_percent"] <= 99
        assert isinstance(card.get("detail"), dict)


def test_q27q_specs_are_loaded_and_match_current_card_ui_contract() -> None:
    q26w = SPEC_Q26W.read_text(encoding="utf-8-sig")
    q27e = SPEC_Q27E.read_text(encoding="utf-8-sig")
    assert "line_1=market_regime_label" in q26w
    assert "confidence_percent=certainty_of_the_market_regime_classification" in q26w
    assert "freshness_not_encoded_by_border=true" in q26w
    assert "card_width_px=208" in q27e
    assert "detail_disclosure_mode=card_overlay" in q27e
    assert "background_color_never_encodes_freshness=true" in q27e


def test_q27q_preview_off_smoke_is_sample_only_and_does_not_read_root(tmp_path: Path) -> None:
    enablement = build_warroom_market_regime_card_preview_enablement_packet(preview_enabled=False, operator_confirmed_read_only=False, generated_at="2026-07-01T18:30:03Z")
    assert enablement["preview_enabled_effective"] is False
    assert enablement["render_kwargs"] == {"preview_enabled": False, "hot_root": None, "generated_at": "2026-07-01T18:30:03Z"}
    packet = build_warroom_market_regime_card_preview_switch_packet(**enablement["render_kwargs"])
    assert packet["sample_data_only"] is True
    assert packet["preview_cards_used"] is False
    assert packet["explicit_source_root_read_performed"] is False
    assert packet["dry_run_invoked"] is False
    assert not (tmp_path / "prediction").exists()
    _assert_card_spec_shape(packet)
    assert packet["cards"][0]["extra"]["sample_only"] is True


def test_q27q_preview_on_smoke_uses_explicit_tmp_root_read_only(tmp_path: Path) -> None:
    _build_fixture(tmp_path)
    enablement = build_warroom_market_regime_card_preview_enablement_packet(
        preview_enabled=True,
        operator_confirmed_read_only=True,
        hot_root=str(tmp_path),
        generated_at="2026-07-01T18:30:03Z",
    )
    assert enablement["preview_enabled_effective"] is True
    packet = build_warroom_market_regime_card_preview_switch_packet(**enablement["render_kwargs"])
    assert packet["sample_data_only"] is False
    assert packet["preview_cards_used"] is True
    assert packet["explicit_source_root_read_performed"] is True
    assert packet["dry_run_invoked"] is True
    assert packet["source_snapshot_ok"] is True
    _assert_card_spec_shape(packet)
    range_cards = [card for card in packet["cards"] if card["regime_code"] == "RANGE"]
    unknown_cards = [card for card in packet["cards"] if card["regime_code"] == "UNKNOWN"]
    assert len(range_cards) == 2
    assert len(unknown_cards) == 6
    assert {card["short_tag"] for card in range_cards} == {"NO_DIRECTION"}
    assert all(card["confidence_percent"] == 15 for card in unknown_cards)
    assert all(card["freshness_badge"] in {"STALE", "MISSING"} for card in unknown_cards)
    assert all(card["short_tag"] in {"STALE_INPUT", "DATA_MISSING"} for card in unknown_cards)
    assert all(card["extra"].get("sample_only") is not True for card in packet["cards"])
    assert packet["runtime_artifact_write_allowed"] is False
    assert packet["would_send_to_broker"] is False


def test_q27q_html_smoke_keeps_card_overlay_detail_not_vertical_push(tmp_path: Path) -> None:
    _build_fixture(tmp_path)
    packet = build_warroom_market_regime_card_preview_switch_packet(preview_enabled=True, hot_root=tmp_path, generated_at="2026-07-01T18:30:03Z")
    html = market_regime_cards_html(packet["cards"])
    assert "market-regime-card-shell" in html
    assert "mr-card-detail-overlay" in html
    assert "mr-overlay-close" in html
    assert "display: none" in html
    assert "position: absolute" in html
    assert "詳細" in html
    assert "Freshness" not in html


def test_q27q_page_and_panel_remain_read_only_and_no_auto_preview_literal() -> None:
    page_text = WARROOM_PAGE.read_text(encoding="utf-8-sig")
    panel_text = PANEL.read_text(encoding="utf-8-sig")
    assert "preview_enabled=True" not in page_text
    assert "value=True" in page_text
    assert "warroom_market_regime_card_preview_enabled_q27p" in page_text
    for text in (page_text, panel_text):
        for token in (
            "send_to_broker(",
            "append_ledger(",
            "ledger.append(",
            "write_runtime_artifact(",
            "write_status_artifact(",
            "write_prediction_artifact(",
        ):
            assert token not in text
