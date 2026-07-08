# path: ./btcts_next/src/btcts/prediction/tests/test_warroom_market_regime_card_detail_enrichment_cp10.py
# desc: CP10 tests for WarRoom market-regime card detail enrichment from latest_cards artifact. UI remains artifact-only; no classifier/raw read.

from __future__ import annotations

import json
import sys
from pathlib import Path

_SRC_ROOT = Path(__file__).resolve().parents[3]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

from btcts.apps.operator_ui.prediction_warroom.panels.warroom_market_regime_card_panel import market_regime_cards_html  # noqa: E402
from btcts.prediction.market_regime.tools.write_latest import build_market_regime_latest_artifact_set  # noqa: E402


def _write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")


def _write_jsonl(path: Path, records: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(json.dumps(record, ensure_ascii=False) for record in records) + "\n", encoding="utf-8")


def _fixture_root(root: Path) -> None:
    forecast_path = root / "prediction/runs/2026-07-08/113000/forecast_records.jsonl"
    _write_json(root / "prediction/latest_manifest.json", {
        "generated_at": "2026-07-08T11:30:00Z",
        "legacy_latest_path": "prediction/latest_prediction_system_result.json",
        "sidecars": {"forecast_records": "prediction/runs/2026-07-08/113000/forecast_records.jsonl"},
    })
    _write_json(root / "prediction/latest_prediction_system_result.json", {"read_only": True, "non_executing": True})
    _write_jsonl(forecast_path, [
        {
            "family": "market_regime",
            "horizon_sec": 900,
            "primary_label": "range_candidate",
            "score": 0.82,
            "values_snapshot": {
                "estimated_signal_strength_percent": 75,
                "estimated_reference_hit_rate_percent": 68,
                "volatility_state": "normal",
                "cross_venue_agreement": "aligned",
                "range_high": 9800000,
                "range_low": 9700000,
                "vwap": 9750000,
                "ma_slope": -0.12,
                "price_position_in_range": 0.54,
                "break_hold_count": 1,
                "false_break_count": 2,
            },
        }
    ])
    _write_json(root / "state/collector_vnext/unified_market_state_status.json", {
        "last_symbol_raw": "FX_BTC_JPY",
        "last_best_bid": 9749000.0,
        "last_best_ask": 9751000.0,
        "last_spread": 2000.0,
        "bid_depth_size": 18.0,
        "ask_depth_size": 12.0,
        "microprice": 9750200.0,
        "absorption_score": 0.63,
        "read_only": True,
        "would_send_to_broker": False,
    })
    _write_json(root / "state/collector_vnext/unified_health.json", {"ok": True, "ws_state": "LIVE", "read_only": True, "would_send_to_broker": False})
    _write_json(root / "state/collector_vnext/unified_executions_status.json", {
        "ws_state": "LIVE",
        "trade_count": 20450,
        "aggressive_buy_volume": 8.5,
        "aggressive_sell_volume": 4.0,
        "cvd": 3.25,
        "read_only": True,
        "would_send_to_broker": False,
    })
    _write_json(root / "state/collector_vnext/unified_daemon_status.json", {"read_only": True, "would_send_to_broker": False})


def test_cp10_writer_enriches_latest_cards_detail_with_signal_and_trace_refs(tmp_path: Path) -> None:
    _fixture_root(tmp_path)
    artifacts = build_market_regime_latest_artifact_set(
        hot_root=tmp_path,
        generated_at="2026-07-08T11:31:00Z",
        run_id="market_regime_cp10_test",
    )
    cards = artifacts["latest_cards"]["cards"]
    assert cards
    first_detail = cards[0]["detail"]
    assert first_detail["percent_meaning"]
    assert first_detail["trace_part_jsonl"] == "prediction/market_regime/ledgers/date=2026-07-08/hour=11/part-00001.jsonl"
    assert first_detail["active_parameter_set_id"] == "market_regime_engine_parameter_set.v1"
    assert "signal_votes_top_n" in first_detail
    assert "source_family_scores" in first_detail
    assert "regime_scores" in first_detail
    assert artifacts["latest_cards"]["compact_summary"]["card_detail_enrichment_version"] == "prediction_warroom.market_regime_card_detail_enrichment.2026_07_08.v1"


def test_cp10_card_overlay_html_renders_enriched_detail_fields() -> None:
    card = {
        "horizon": "現在",
        "regime_label": "レンジ",
        "confidence_percent": 70,
        "freshness_badge": "LIVE",
        "card_lines": ["レンジ", "70%", "方向感なし"],
        "background_style": {"background": "#FFFAEB", "text": "#101828"},
        "evidence_quality_style": {"border_style": "solid", "border_color": "#F79009"},
        "detail": {
            "reason_lines": ["price remains inside range body"],
            "source_lines": ["forecast_records", "collector_market_state"],
            "warning_lines": ["conflict sample"],
            "invalidation_lines": ["range high break hold"],
            "percent_meaning": "地合い見立ての信頼性であり、勝率ではありません。",
            "signal_votes_top_n": [
                {"signal_id": "absorption_score", "supports_regime": "RANGE", "weighted_strength": 0.63},
                {"signal_id": "orderflow_imbalance", "supports_regime": "UP_TREND", "weighted_strength": 0.32},
            ],
            "signal_conflicts_top_n": [{"primary_regime": "RANGE", "conflicting_regime": "UP_TREND"}],
            "source_family_scores": {"liquidity": 1.12, "orderflow": 0.55},
            "regime_scores": {"RANGE": 1.2, "UP_TREND": 0.4},
            "trace_part_jsonl": "prediction/market_regime/ledgers/date=2026-07-08/hour=11/part-00001.jsonl",
            "active_parameter_set_id": "market_regime_engine_parameter_set.v1",
        },
    }
    html = market_regime_cards_html([card])
    assert "理由:" in html
    assert "無効化:" in html
    assert "主な票:" in html
    assert "競合:" in html
    assert "ソース寄与:" in html
    assert "地合いスコア:" in html
    assert "Trace:" in html
    assert "Parameter:" in html
    assert "absorption_score" in html
    assert "orderflow_imbalance" in html
    assert "勝率ではありません" in html


def test_cp10_panel_file_keeps_no_classifier_import() -> None:
    path = Path(market_regime_cards_html.__code__.co_filename)
    text = path.read_text(encoding="utf-8")
    forbidden = [
        "classify_market_regime_feature_bundle",
        "D:/btc_ts_hot",
        "write_text(",
        "broker_private_api_allowed: bool = True",
        "autotrade_trigger_allowed: bool = True",
    ]
    assert [token for token in forbidden if token in text] == []
