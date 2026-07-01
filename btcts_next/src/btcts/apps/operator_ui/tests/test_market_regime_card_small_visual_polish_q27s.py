# path: ./btcts_next/src/btcts/apps/operator_ui/tests/test_market_regime_card_small_visual_polish_q27s.py
# desc: PS-Q27S small visual polish guard. Reduces redundant copy while preserving card geometry and safety boundaries.

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
DOC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q27S_WARROOM_MARKET_REGIME_SMALL_VISUAL_POLISH_2026-07-02.md"
PANEL = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/prediction_warroom/panels/warroom_market_regime_card_panel.py"
WARROOM_PAGE = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/views/warroom_page.py"


def _write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")


def _write_jsonl(path: Path, records: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(json.dumps(record, ensure_ascii=False) for record in records) + "\n", encoding="utf-8")


def _build_fixture(root: Path) -> None:
    forecast_path = root / "prediction/runs/2026-07-01/193000/forecast_records.jsonl"
    _write_json(root / "prediction/latest_manifest.json", {
        "generated_at": "2026-07-01T19:30:00Z",
        "legacy_latest_path": "prediction/latest_prediction_system_result.json",
        "sidecars": {"forecast_records": "prediction/runs/2026-07-01/193000/forecast_records.jsonl"},
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


def test_q27s_doc_records_compact_copy_boundaries() -> None:
    text = DOC.read_text(encoding="utf-8-sig")
    assert "ps_q27s_warroom_market_regime_small_visual_polish=true" in text
    assert "redundant_copy_reduced=true" in text
    assert "caption_compacted=true" in text
    assert "confidence_explainer_added=false" in text
    assert "card_width_changed=false" in text
    assert "card_body_three_lines_unchanged=true" in text
    assert "would_send_to_broker=false" in text


def test_q27s_panel_caption_strings_are_not_redundant_and_do_not_add_explainer() -> None:
    panel_text = PANEL.read_text(encoding="utf-8-sig")
    page_text = WARROOM_PAGE.read_text(encoding="utf-8-sig")
    assert "地合いカード: sample" not in panel_text
    assert "地合いカード: preview / read-only" not in panel_text
    assert "勝率ではありません" not in panel_text
    assert "分類信頼度は" not in panel_text
    assert "実行系なし" not in panel_text
    assert "preview_enabled=True" not in page_text


def test_q27s_detail_overlay_keeps_japanese_headings_without_extra_explainer(tmp_path: Path) -> None:
    _build_fixture(tmp_path)
    packet = build_warroom_market_regime_card_preview_switch_packet(preview_enabled=True, hot_root=tmp_path, generated_at="2026-07-01T19:30:03Z")
    html = market_regime_cards_html(packet["cards"])
    assert "読み方" in html
    assert "理由" in html
    assert "情報源" in html
    assert "注意" in html
    assert "根拠" in html
    assert "勝率ではありません" not in html
    assert "分類信頼度" not in html
    assert "mr-card-detail-overlay" in html
    assert "position: absolute" in html


def test_q27s_preserves_q26w_q27e_card_shape_and_safety(tmp_path: Path) -> None:
    _build_fixture(tmp_path)
    packet = build_warroom_market_regime_card_preview_switch_packet(preview_enabled=True, hot_root=tmp_path, generated_at="2026-07-01T19:30:03Z")
    assert packet["card_width_px"] == 208
    assert packet["cards_do_not_shrink"] is True
    assert packet["horizontal_scroll_required"] is True
    assert packet["freshness_encoded_by_badge_only"] is True
    assert packet["border_meaning"] == "evidence_quality"
    assert packet["confidence_meaning"] == "market_regime_classification_certainty_not_win_rate"
    assert packet["detail_disclosure_mode"] == "card_overlay"
    assert all(len(card["card_lines"]) == 3 for card in packet["cards"])
    assert packet["runtime_artifact_write_allowed"] is False
    assert packet["would_send_to_broker"] is False


def test_q27s_panel_has_no_new_execution_or_write_tokens() -> None:
    text = PANEL.read_text(encoding="utf-8-sig")
    for token in (
        "send_to_broker(",
        "append_ledger(",
        "ledger.append(",
        "write_runtime_artifact(",
        "write_status_artifact(",
        "write_prediction_artifact(",
        "open(\"D:",
    ):
        assert token not in text
