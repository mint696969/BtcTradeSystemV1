# path: ./btcts_next/src/btcts/prediction/tests/test_warroom_market_regime_cards_artifact_read.py
# desc: CP4 tests for WarRoom UI market-regime latest_cards artifact read path. Verifies artifact/fallback behavior without classifier or preview inference.

from __future__ import annotations

import json
import sys
from contextlib import nullcontext
from pathlib import Path
from typing import Any, Mapping

_SRC_ROOT = Path(__file__).resolve().parents[3]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

from btcts.prediction.market_regime.artifact_contracts import build_market_regime_latest_cards_artifact  # noqa: E402
from btcts.apps.operator_ui.prediction_warroom.v2.rt_ui import prediction_cards_view  # noqa: E402


class _FakeStreamlit:
    def __init__(self) -> None:
        self.captions: list[str] = []
        self.frames: list[Any] = []

    def caption(self, value: object) -> None:
        self.captions.append(str(value))

    def dataframe(self, value: object, **_: object) -> None:
        self.frames.append(value)

    def expander(self, *_: object, **__: object):
        return nullcontext()


def _artifact_card() -> dict[str, Any]:
    return {
        "horizon": "15分後",
        "regime_code": "RANGE",
        "regime_label": "レンジ",
        "confidence_percent": 70,
        "freshness_badge": "LIVE",
        "evidence_quality": "PARTIAL",
        "short_tag_label": "方向感なし",
        "detail": {"reason_lines": ["fixture_artifact_card"]},
    }


def _fake_renderer_packet(cards: object) -> dict[str, Any]:
    card_rows = [dict(card) for card in cards] if isinstance(cards, list) else [
        {
            "horizon": "現在",
            "regime_code": "UNKNOWN",
            "regime_label": "不明",
            "confidence_percent": 0,
            "freshness_badge": "MISSING",
            "sample_only": True,
        }
    ]
    return {
        "ok": True,
        "cards": card_rows,
        "card_count": len(card_rows),
        "preview_cards_used": False,
        "source_snapshot_ok": None,
        "source_snapshot_missing_sources": [],
        "source_snapshot_warnings": [],
        "prediction_warnings": [],
        "feature_bundle_available_signal_count": 0,
        "preview_disabled_reason": "",
        "classifier_invoked": False,
    }


def test_cp4_warroom_prediction_cards_use_latest_cards_artifact_when_present(tmp_path: Path, monkeypatch) -> None:
    artifact_dir = tmp_path / "prediction" / "market_regime"
    artifact_dir.mkdir(parents=True)
    artifact = build_market_regime_latest_cards_artifact(
        generated_at="2026-07-08T09:10:00Z",
        run_id="market_regime_20260708T091000Z_fixture",
        cards=[_artifact_card()],
        compact_summary={"fixture": True},
    )
    (artifact_dir / "latest_cards.json").write_text(json.dumps(artifact, ensure_ascii=False), encoding="utf-8")
    calls: list[object] = []

    def fake_render_warroom_market_regime_card_shell(cards=None, **kwargs):
        calls.append({"cards": cards, "kwargs": kwargs})
        return _fake_renderer_packet(cards)

    monkeypatch.setenv("BTCTS_HOT_ROOT", str(tmp_path))
    monkeypatch.setattr(prediction_cards_view, "render_warroom_market_regime_card_shell", fake_render_warroom_market_regime_card_shell)

    st = _FakeStreamlit()
    result = prediction_cards_view.render_rt_prediction_cards({"generated_at": "2026-07-08T09:10:01Z"}, st)

    assert result["ok"] is True
    assert result["market_regime_artifact_read_model_only"] is True
    assert result["market_regime_artifact_cards_used"] is True
    assert result["market_regime_artifact_read_error"] == ""
    assert result["market_regime_preview_cards_used"] is False
    assert result["market_regime_preview_inference_invoked"] is False
    assert result["market_regime_raw_market_source_read_performed"] is False
    assert result["prediction_invoked"] is False
    assert result["classifier_invoked"] is False
    assert result["ui_market_regime_preview_inference_removed"] is True
    assert calls and isinstance(calls[0], Mapping)
    assert calls[0]["cards"][0]["regime_label"] == "レンジ"
    assert calls[0]["kwargs"] == {}
    assert any("artifact latest_cards" in caption for caption in st.captions)


def test_cp4_warroom_prediction_cards_fall_back_when_latest_cards_missing(tmp_path: Path, monkeypatch) -> None:
    calls: list[object] = []

    def fake_render_warroom_market_regime_card_shell(cards=None, **kwargs):
        calls.append({"cards": cards, "kwargs": kwargs})
        return _fake_renderer_packet(cards)

    monkeypatch.setenv("BTCTS_HOT_ROOT", str(tmp_path))
    monkeypatch.setattr(prediction_cards_view, "render_warroom_market_regime_card_shell", fake_render_warroom_market_regime_card_shell)

    st = _FakeStreamlit()
    result = prediction_cards_view.render_rt_prediction_cards({"generated_at": "2026-07-08T09:12:01Z"}, st)

    assert result["ok"] is True
    assert result["market_regime_artifact_read_model_only"] is True
    assert result["market_regime_artifact_cards_used"] is False
    assert result["market_regime_artifact_read_error"] == "latest_cards_artifact_missing"
    assert result["market_regime_preview_cards_used"] is False
    assert result["market_regime_preview_inference_invoked"] is False
    assert result["market_regime_raw_market_source_read_performed"] is False
    assert result["prediction_invoked"] is False
    assert result["classifier_invoked"] is False
    assert calls and isinstance(calls[0], Mapping)
    assert calls[0]["cards"] is None
    assert calls[0]["kwargs"] == {}
    assert any("sample/fallback" in caption for caption in st.captions)


def test_cp4_prediction_cards_view_keeps_forbidden_preview_inference_tokens_out() -> None:
    path = Path(prediction_cards_view.__file__)
    text = path.read_text(encoding="utf-8")
    forbidden = [
        "preview_enabled=True",
        "RT_MARKET_REGIME_CARD_PREVIEW_HOT_ROOT",
        "build_market_regime_warroom_preview_binding_packet",
        "classify_market_regime_feature_bundle",
    ]
    assert [token for token in forbidden if token in text] == []
    assert "latest_cards.json" in text
    assert "artifact_read_model_only" in text
    assert "ui_market_regime_preview_inference_removed" in text
