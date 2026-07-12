# path: ./btcts_next/src/btcts/apps/operator_ui/tests/test_warroom_v2_market_regime_selected_read_model_integration.py
# desc: MR-VS6.5 selected common read model to existing card and explanation rendering integration guards.

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

_SRC_ROOT = Path(__file__).resolve().parents[4]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

from btcts.apps.operator_ui.prediction_warroom.v2.rt_ui import prediction_cards_view as view  # noqa: E402
from btcts.apps.operator_ui.views import warroom_v2_page  # noqa: E402
from btcts.apps.operator_ui.prediction_warroom.v2.push_widgets.wp3_per_widget_state_store import (  # noqa: E402
    apply_widget_state_update,
    build_initial_widget_state_store,
)
from btcts.apps.operator_ui.prediction_warroom.v2.rt_ui.market_regime_selected_read_model_bridge import (  # noqa: E402
    build_market_regime_selected_read_model_bridge,
)
from btcts.prediction.family_read_model import build_prediction_family_read_model  # noqa: E402


class FakeExpander:
    def __enter__(self) -> "FakeExpander":
        return self

    def __exit__(self, exc_type: object, exc: object, tb: object) -> None:
        return None


class FakeStreamlit:
    def __init__(self) -> None:
        self.captions: list[str] = []
        self.tables: list[list[dict[str, object]]] = []
        self.expanders: list[str] = []

    def caption(self, value: object) -> None:
        self.captions.append(str(value))

    def expander(self, label: object, **_kwargs: object) -> FakeExpander:
        self.expanders.append(str(label))
        return FakeExpander()

    def dataframe(self, rows: list[dict[str, object]], **_kwargs: object) -> None:
        self.tables.append(rows)


def _source_packet() -> dict[str, Any]:
    model = build_prediction_family_read_model(
        prediction_family_id="market_regime",
        generated_at="2026-07-12T03:00:00Z",
        run_id="run-selected",
        prediction_id="prediction-selected",
        model_id="market-regime-model",
        logic_version="logic-v1",
        parameter_set_id="pset-v1",
        horizon_rows=[
            {
                "horizon_key": "current",
                "horizon_sec": 0,
                "horizon_group": "current",
                "primary_label": "RANGE",
                "primary_label_display": "レンジ",
                "confidence_percent": 64,
                "confidence_kind": "heuristic_support",
                "freshness_state": "LIVE",
                "evidence_quality": "PARTIAL",
                "drivers": ["price_in_range"],
                "blockers": ["cross_venue_missing"],
                "warnings": ["comparison_not_ready"],
                "invalidation_hints": ["range_break"],
                "family_payload": {"regime_code": "RANGE", "regime_label": "レンジ", "tactical_hint": "RANGE_TACTIC"},
            }
        ],
    )
    return {
        "selected_source": "push",
        "prediction_generated_at": "2026-07-12T03:00:00Z",
        "transport_received_at_ms": 123456,
        "run_id": "run-selected",
        "prediction_id": "prediction-selected",
        "parameter_set_id": "pset-v1",
        "read_model": model,
    }


def test_bridge_preserves_card_explanation_identity_and_confidence() -> None:
    packet = build_market_regime_selected_read_model_bridge(_source_packet())
    assert packet["ok"] is True
    assert packet["selected_source"] == "push"
    assert packet["card_count"] == 1
    card = packet["cards"][0]
    assert card["regime_code"] == "RANGE"
    assert card["confidence_percent"] == 64
    assert card["detail"]["reason_lines"] == ["price_in_range"]
    assert card["detail"]["blocker_lines"] == ["cross_venue_missing"]
    assert card["detail"]["warning_lines"] == ["comparison_not_ready"]
    assert card["detail"]["invalidation_lines"] == ["range_break"]
    explanation = packet["explanation_packet"]["horizons"][0]
    assert explanation["confidence"]["display_confidence_percent"] == 64
    assert explanation["trace"]["run_id"] == "run-selected"
    assert packet["confidence_recalculated"] is False


def test_bridge_preserves_all_eight_horizons_in_order() -> None:
    source = _source_packet()
    base = source["read_model"]["horizon_rows"][0]
    horizon_specs = [
        ("current", 0),
        ("5m", 300),
        ("15m", 900),
        ("30m", 1800),
        ("60m", 3600),
        ("6h", 21600),
        ("12h", 43200),
        ("24h", 86400),
    ]
    source["read_model"]["horizon_rows"] = [
        {**base, "horizon_key": key, "horizon_sec": seconds}
        for key, seconds in horizon_specs
    ]
    source["read_model"]["horizon_count"] = 8

    packet = build_market_regime_selected_read_model_bridge(source)

    assert packet["ok"] is True
    assert packet["card_count"] == 8
    assert [card["horizon_key"] for card in packet["cards"]] == [item[0] for item in horizon_specs]
    assert packet["explanation_packet"]["horizon_count"] == 8


def test_unavailable_source_fails_closed_without_cards() -> None:
    packet = build_market_regime_selected_read_model_bridge({"selected_source": "unavailable", "read_model": {}})
    assert packet["ok"] is False
    assert packet["cards"] == []
    assert packet["explanation_packet"]["ok"] is False
    assert packet["prediction_invoked"] is False
    assert packet["classifier_invoked"] is False
    assert packet["would_send_to_broker"] is False


def test_render_prefers_selected_read_model_and_keeps_legacy_artifact_fallback(monkeypatch, tmp_path: Path) -> None:
    calls: list[dict[str, object]] = []

    def fake_shell(**kwargs: object) -> dict[str, object]:
        calls.append(dict(kwargs))
        cards = kwargs.get("cards") if isinstance(kwargs.get("cards"), list) else []
        return {"cards": cards, "card_count": len(cards), "artifact_cards_used": False, "artifact_path": "", "artifact_read_error": ""}

    monkeypatch.setenv("BTCTS_HOT_ROOT", str(tmp_path))
    monkeypatch.setattr(view, "render_warroom_market_regime_card_shell", fake_shell)
    fake = FakeStreamlit()
    result = view.render_rt_prediction_cards(
        {"cards": [], "market_regime_source_packet": _source_packet()},
        fake,
    )

    assert calls and len(calls[0]["cards"]) == 1
    assert calls[0]["cards"][0]["confidence_percent"] == 64
    assert result["market_regime_selected_read_model_used"] is True
    assert result["market_regime_selected_source"] == "push"
    assert result["market_regime_artifact_read_model_only"] is False
    assert result["market_regime_explanation_packet_ok"] is True
    assert result["market_regime_explanation_confidence_recalculated"] is False
    assert result["prediction_invoked"] is False
    assert result["classifier_invoked"] is False
    assert result["broker_action_allowed"] is False


def test_render_without_source_packet_keeps_legacy_artifact_path(monkeypatch, tmp_path: Path) -> None:
    calls: list[dict[str, object]] = []

    def fake_shell(**kwargs: object) -> dict[str, object]:
        calls.append(dict(kwargs))
        cards = kwargs.get("cards") if isinstance(kwargs.get("cards"), list) else []
        return {"cards": cards, "card_count": len(cards), "artifact_cards_used": True, "artifact_path": "legacy.json", "artifact_read_error": ""}

    monkeypatch.setenv("BTCTS_HOT_ROOT", str(tmp_path))
    monkeypatch.setattr(view, "render_warroom_market_regime_card_shell", fake_shell)
    fake = FakeStreamlit()
    result = view.render_rt_prediction_cards({"cards": []}, fake)

    assert calls
    assert result["market_regime_selected_read_model_used"] is False
    assert result["market_regime_selected_source"] == "unavailable"
    assert result["market_regime_artifact_read_model_only"] is True
    assert result["prediction_invoked"] is False
    assert result["classifier_invoked"] is False


def test_production_page_attaches_valid_wp3_push_to_cards_packet() -> None:
    source = _source_packet()
    store = apply_widget_state_update(
        build_initial_widget_state_store(),
        topic_key="prediction.family.market_regime",
        value=source["read_model"],
        updated_at_ms=123456,
        sequence=9,
    )
    display_packets = {
        "source": {"display_source": "live"},
        "widgets": {},
        "top": {},
        "chart": {},
        "cards": {"cards": []},
    }

    attached = warroom_v2_page._attach_market_regime_selected_source(display_packets, store)

    assert attached["cards"]["market_regime_source_attached"] is True
    assert attached["cards"]["market_regime_selected_source"] == "push"
    assert attached["cards"]["market_regime_prediction_generated_at"] == "2026-07-12T03:00:00Z"
    assert attached["cards"]["market_regime_transport_received_at_ms"] == 123456
    assert attached["cards"]["market_regime_source_packet"]["read_model"]["run_id"] == "run-selected"
    assert "market_regime_source_packet" not in display_packets["cards"]


def test_production_page_keeps_legacy_artifact_path_without_valid_push() -> None:
    display_packets = {
        "source": {"display_source": "retained"},
        "widgets": {},
        "top": {},
        "chart": {},
        "cards": {"cards": []},
    }

    attached = warroom_v2_page._attach_market_regime_selected_source(
        display_packets,
        build_initial_widget_state_store(),
    )

    assert "market_regime_source_packet" not in attached["cards"]
    assert attached["cards"] == display_packets["cards"]


def test_view_source_has_no_prediction_or_classifier_call() -> None:
    text = Path(view.__file__).read_text(encoding="utf-8")
    assert "build_market_regime_selected_read_model_bridge" in text
    forbidden = ["classify_market_regime_feature_bundle(", "build_market_regime_source_snapshot(", "write_market_regime_latest_artifacts_once", "requests.post"]
    assert [token for token in forbidden if token in text] == []
