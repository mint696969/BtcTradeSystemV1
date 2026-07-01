# path: ./btcts_next/src/btcts/apps/operator_ui/tests/test_market_regime_detail_density_reduction_q27u.py
# desc: PS-Q27U guard. Reduces market-regime card detail overlay density without changing card geometry or safety boundaries.

from __future__ import annotations

import json
import sys
from pathlib import Path

_SRC_ROOT = Path(__file__).resolve().parents[4]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

from btcts.apps.operator_ui.prediction_warroom.panels.warroom_market_regime_card_panel import (  # noqa: E402
    build_warroom_market_regime_card_preview_switch_packet,
    market_regime_cards_html,
)

REPO_ROOT = Path(__file__).resolve().parents[6]
DOC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q27U_WARROOM_MARKET_REGIME_DETAIL_DENSITY_REDUCTION_2026-07-02.md"
PANEL = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/prediction_warroom/panels/warroom_market_regime_card_panel.py"


def _write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")


def _write_jsonl(path: Path, records: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(json.dumps(record, ensure_ascii=False) for record in records) + "\n", encoding="utf-8")


def _build_fixture(root: Path) -> None:
    forecast_path = root / "prediction/runs/2026-07-01/200500/forecast_records.jsonl"
    _write_json(root / "prediction/latest_manifest.json", {
        "generated_at": "2026-07-01T20:05:00Z",
        "legacy_latest_path": "prediction/latest_prediction_system_result.json",
        "sidecars": {"forecast_records": "prediction/runs/2026-07-01/200500/forecast_records.jsonl"},
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


def test_q27u_doc_records_detail_density_reduction_boundary() -> None:
    text = DOC.read_text(encoding="utf-8-sig")
    assert "ps_q27u_warroom_market_regime_detail_density_reduction=true" in text
    assert "detail_reading_row_removed=true" in text
    assert "detail_evidence_row_removed=true" in text
    assert "empty_fallback_copy_removed=true" in text
    assert "detail_reason_source_limited=true" in text
    assert "would_send_to_broker=false" in text


def test_q27u_detail_overlay_removes_low_value_rows_and_fallbacks(tmp_path: Path) -> None:
    _build_fixture(tmp_path)
    packet = build_warroom_market_regime_card_preview_switch_packet(preview_enabled=True, hot_root=tmp_path, generated_at="2026-07-01T20:05:03Z")
    html = market_regime_cards_html(packet["cards"])
    assert "理由" in html
    assert "情報源" in html
    assert "読み方" not in html
    assert "根拠" not in html
    assert "sample shell" not in html
    assert "Q26X sample card" not in html
    assert "live data not connected" not in html
    assert "勝率ではありません" not in html
    assert "分類信頼度" not in html


def test_q27u_detail_overlay_keeps_overlay_shape_not_inline_push(tmp_path: Path) -> None:
    _build_fixture(tmp_path)
    packet = build_warroom_market_regime_card_preview_switch_packet(preview_enabled=True, hot_root=tmp_path, generated_at="2026-07-01T20:05:03Z")
    html = market_regime_cards_html(packet["cards"])
    assert "mr-card-detail-overlay" in html
    assert "mr-overlay-close" in html
    assert "position: absolute" in html
    assert "display: none" in html
    assert "地合いカード詳細" in html


def test_q27u_panel_has_detail_limit_helper_and_no_redundant_detail_rows() -> None:
    text = PANEL.read_text(encoding="utf-8-sig")
    assert "def _joined_detail_items" in text
    assert "limit: int = 3" in text
    assert "<b>読み方:</b>" not in text
    assert "<b>根拠:</b>" not in text
    assert "sample shell" not in text
    assert "Q26X sample card" not in text
    assert "live data not connected" not in text


def test_q27u_card_specs_and_safety_flags_unchanged(tmp_path: Path) -> None:
    _build_fixture(tmp_path)
    packet = build_warroom_market_regime_card_preview_switch_packet(preview_enabled=True, hot_root=tmp_path, generated_at="2026-07-01T20:05:03Z")
    assert packet["card_width_px"] == 208
    assert packet["cards_do_not_shrink"] is True
    assert packet["horizontal_scroll_required"] is True
    assert packet["freshness_encoded_by_badge_only"] is True
    assert packet["border_meaning"] == "evidence_quality"
    assert packet["detail_disclosure_mode"] == "card_overlay"
    assert all(len(card["card_lines"]) == 3 for card in packet["cards"])
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
