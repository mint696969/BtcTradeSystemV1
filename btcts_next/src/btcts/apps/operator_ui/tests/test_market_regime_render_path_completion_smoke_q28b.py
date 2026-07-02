# path: ./btcts_next/src/btcts/apps/operator_ui/tests/test_market_regime_render_path_completion_smoke_q28b.py
# desc: PS-Q28B render-path smoke. WarRoom market-regime render function stores real-preview ps_q27z packet in session_state. No production code change.

from __future__ import annotations

import json
import sys
from pathlib import Path
from types import SimpleNamespace

_SRC_ROOT = Path(__file__).resolve().parents[4]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

from btcts.apps.operator_ui.prediction_warroom.panels import warroom_market_regime_card_panel as panel  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parents[6]
DOC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q28B_WARROOM_MARKET_REGIME_RENDER_PATH_COMPLETION_SMOKE_2026-07-02.md"
WARROOM_PAGE = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/views/warroom_page.py"
PANEL = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/prediction_warroom/panels/warroom_market_regime_card_panel.py"


def _write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")


def _write_jsonl(path: Path, records: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(json.dumps(record, ensure_ascii=False) for record in records) + "\n", encoding="utf-8")


def _build_fixture(root: Path) -> None:
    forecast_path = root / "prediction/runs/2026-07-02/021500/forecast_records.jsonl"
    _write_json(root / "prediction/latest_manifest.json", {
        "generated_at": "2026-07-02T02:15:00Z",
        "legacy_latest_path": "prediction/latest_prediction_system_result.json",
        "sidecars": {"forecast_records": "prediction/runs/2026-07-02/021500/forecast_records.jsonl"},
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
            "horizon_sec": 1800,
            "primary_label": "breakout_candidate",
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


class _FakeStreamlit:
    def __init__(self) -> None:
        self.session_state: dict = {}
        self.markdown_calls: list[tuple[str, bool]] = []

    def markdown(self, html: str, *, unsafe_allow_html: bool = False) -> None:
        self.markdown_calls.append((html, unsafe_allow_html))


def test_q28b_doc_records_render_path_completion_boundary() -> None:
    text = DOC.read_text(encoding="utf-8-sig")
    assert "ps_q28b_warroom_market_regime_render_path_completion_smoke=true" in text
    assert "production_code_changed=false" in text
    assert "ui_copy_added=false" in text
    assert "renderer_session_state_stage_versions_verified=true" in text
    assert "would_send_to_broker=false" in text


def test_q28b_render_function_stores_real_preview_packet_and_outputs_cards(monkeypatch, tmp_path: Path) -> None:
    _build_fixture(tmp_path)
    fake_st = _FakeStreamlit()
    monkeypatch.setattr(panel, "st", fake_st)
    panel.render_warroom_market_regime_card_shell(
        preview_enabled=True,
        hot_root=tmp_path,
        generated_at="2026-07-02T02:15:03Z",
    )
    assert len(fake_st.markdown_calls) == 1
    html, unsafe = fake_st.markdown_calls[0]
    assert unsafe is True
    assert "market-regime-card-shell" in html
    assert "mr-card-detail-overlay" in html
    assert "上昇トレンド" in html
    assert "ブレイク" in html
    packet = fake_st.session_state["warroom_market_regime_card_renderer"]
    assert packet["preview_cards_used"] is True
    assert packet["sample_data_only"] is False
    assert packet["stage_versions"]["classifier"] == "prediction.market_regime.regime_classifier.ps_q27z.v1"
    assert packet["dry_run_version"] is not None
    assert packet["card_count"] == 8
    by_horizon = {card["horizon"]: card for card in packet["cards"]}
    assert by_horizon["5分後"]["regime_code"] == "UP_TREND"
    assert by_horizon["30分後"]["regime_code"] == "BREAKOUT"
    assert by_horizon["24時間後"]["regime_code"] == "BREAKOUT"
    assert packet["would_send_to_broker"] is False


def test_q28b_render_function_explicit_off_stores_sample_fallback(monkeypatch, tmp_path: Path) -> None:
    fake_st = _FakeStreamlit()
    monkeypatch.setattr(panel, "st", fake_st)
    panel.render_warroom_market_regime_card_shell(
        preview_enabled=False,
        hot_root=tmp_path / "must_not_be_read",
        generated_at="2026-07-02T02:15:03Z",
    )
    packet = fake_st.session_state["warroom_market_regime_card_renderer"]
    assert packet["sample_data_only"] is True
    assert packet["preview_cards_used"] is False
    assert packet["explicit_source_root_read_performed"] is False
    assert packet["stage_versions"] == {}
    assert packet["cards"][0]["extra"]["sample_only"] is True
    assert packet["would_send_to_broker"] is False


def test_q28b_page_and_panel_keep_ui_copy_and_execution_paths_stable() -> None:
    page_text = WARROOM_PAGE.read_text(encoding="utf-8-sig")
    panel_text = PANEL.read_text(encoding="utf-8-sig")
    assert '"地合い preview"' in page_text
    assert "value=True" in page_text
    assert "地合いカード preview はデフォルトOFF" not in page_text
    assert "勝率ではありません" not in panel_text
    assert "分類信頼度" not in panel_text
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
