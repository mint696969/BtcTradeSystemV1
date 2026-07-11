# path: ./btcts_next/src/btcts/apps/operator_ui/tests/test_warroom_v2_market_regime_push_primary_artifact_fallback.py
# desc: MR-VS6.4 guards validated push-primary, artifact fallback, fail-closed unavailable, identity, freshness separation, and no confidence merge.

from __future__ import annotations

import sys
from pathlib import Path

_SRC_ROOT = Path(__file__).resolve().parents[4]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

from btcts.apps.operator_ui.prediction_warroom.v2.rt_ui.market_regime_read_model_source import (  # noqa: E402
    MARKET_REGIME_TOPIC_KEY,
    select_market_regime_read_model_source,
)
from btcts.prediction.family_read_model import (  # noqa: E402
    build_prediction_family_push_message,
    build_prediction_family_read_model,
)
from btcts.apps.operator_ui.prediction_warroom.v2.push_widgets.wp3_per_widget_state_store import (  # noqa: E402
    apply_widget_state_update,
    build_initial_widget_state_store,
)


def _model(*, run_id: str, prediction_id: str, generated_at: str, confidence: int) -> dict:
    return build_prediction_family_read_model(
        prediction_family_id="market_regime",
        generated_at=generated_at,
        run_id=run_id,
        prediction_id=prediction_id,
        model_id="market-regime-model",
        logic_version="market-regime-logic-v1",
        parameter_set_id="market-regime-pset-v1",
        horizon_rows=[
            {
                "horizon_key": "current",
                "horizon_sec": 0,
                "horizon_group": "current",
                "primary_label": "RANGE",
                "primary_label_display": "レンジ",
                "confidence_percent": confidence,
                "freshness_state": "LIVE",
                "evidence_quality": "PARTIAL",
                "family_payload": {"regime_code": "RANGE"},
            }
        ],
    )


def _push(model: dict, *, received_at_ms: int = 999999) -> dict:
    return build_prediction_family_push_message(
        topic_key=MARKET_REGIME_TOPIC_KEY,
        value=model,
        received_at_ms=received_at_ms,
        sequence=7,
    )


def test_valid_push_is_primary_and_artifact_is_not_merged() -> None:
    push_model = _model(run_id="push-run", prediction_id="push-pred", generated_at="2026-07-12T01:00:00Z", confidence=71)
    artifact_model = _model(run_id="artifact-run", prediction_id="artifact-pred", generated_at="2026-07-12T00:59:00Z", confidence=42)

    packet = select_market_regime_read_model_source(
        push_state=_push(push_model, received_at_ms=123456789),
        artifact_read_model=artifact_model,
    )

    assert packet["selected_source"] == "push"
    assert packet["push_valid"] is True
    assert packet["artifact_valid"] is True
    assert packet["fallback_used"] is False
    assert packet["run_id"] == "push-run"
    assert packet["prediction_id"] == "push-pred"
    assert packet["prediction_generated_at"] == "2026-07-12T01:00:00Z"
    assert packet["transport_received_at_ms"] == 123456789
    assert packet["read_model"]["horizon_rows"][0]["confidence_percent"] == 71
    assert packet["confidence_merge_performed"] is False
    assert packet["confidence_recalculation_performed"] is False


def test_actual_wp3_widget_state_is_accepted_as_push_primary() -> None:
    model = _model(run_id="state-run", prediction_id="state-pred", generated_at="2026-07-12T01:00:00Z", confidence=67)
    store = apply_widget_state_update(
        build_initial_widget_state_store(),
        topic_key=MARKET_REGIME_TOPIC_KEY,
        value=model,
        updated_at_ms=777777,
        sequence=11,
    )

    packet = select_market_regime_read_model_source(push_state=store)

    assert packet["selected_source"] == "push"
    assert packet["push_valid"] is True
    assert packet["transport_received_at_ms"] == 777777
    assert packet["run_id"] == "state-run"
    assert packet["prediction_id"] == "state-pred"


def test_invalid_push_falls_back_to_valid_artifact() -> None:
    artifact_model = _model(run_id="artifact-run", prediction_id="artifact-pred", generated_at="2026-07-12T00:59:00Z", confidence=42)
    invalid_push = _push(_model(run_id="bad", prediction_id="bad", generated_at="2026-07-12T01:00:00Z", confidence=80))
    invalid_push["value"]["safety"]["would_send_to_broker"] = True

    packet = select_market_regime_read_model_source(
        push_state=invalid_push,
        artifact_read_model=artifact_model,
    )

    assert packet["selected_source"] == "artifact"
    assert packet["push_present"] is True
    assert packet["push_valid"] is False
    assert packet["artifact_valid"] is True
    assert packet["fallback_used"] is True
    assert packet["fallback_reason"] == "push_invalid"
    assert packet["run_id"] == "artifact-run"
    assert packet["read_model"]["horizon_rows"][0]["confidence_percent"] == 42


def test_missing_push_falls_back_to_valid_artifact() -> None:
    artifact_model = _model(run_id="artifact-run", prediction_id="artifact-pred", generated_at="2026-07-12T00:59:00Z", confidence=42)
    packet = select_market_regime_read_model_source(artifact_read_model=artifact_model)
    assert packet["selected_source"] == "artifact"
    assert packet["fallback_used"] is True
    assert packet["fallback_reason"] == "push_missing"


def test_both_invalid_fail_closed_unavailable() -> None:
    packet = select_market_regime_read_model_source(
        push_state={"topic_key": MARKET_REGIME_TOPIC_KEY, "value": {"raw_candles": [1]}},
        artifact_read_model={"prediction_family_id": "market_regime", "raw_orderbook": {}},
    )
    assert packet["selected_source"] == "unavailable"
    assert packet["read_model"] == {}
    assert packet["fallback_used"] is False
    assert packet["fallback_reason"] == "push_and_artifact_invalid"
    assert packet["prediction_invoked"] is False
    assert packet["classifier_invoked"] is False
    assert packet["render_invoked"] is False
    assert packet["mount_enabled"] is False
    assert packet["would_send_to_broker"] is False


def test_wrong_family_or_topic_is_rejected() -> None:
    other = _model(run_id="x", prediction_id="y", generated_at="2026-07-12T01:00:00Z", confidence=50)
    other["prediction_family_id"] = "trend_bias"
    wrong_topic = _push(_model(run_id="x", prediction_id="y", generated_at="2026-07-12T01:00:00Z", confidence=50))
    wrong_topic["topic_key"] = "prediction.family.trend_bias"

    family_packet = select_market_regime_read_model_source(artifact_read_model=other)
    topic_packet = select_market_regime_read_model_source(push_state=wrong_topic)

    assert family_packet["selected_source"] == "unavailable"
    assert family_packet["artifact_valid"] is False
    assert topic_packet["selected_source"] == "unavailable"
    assert topic_packet["push_valid"] is False


def test_bounding_that_breaks_contract_fails_closed() -> None:
    model = _model(run_id="run", prediction_id="pred", generated_at="2026-07-12T01:00:00Z", confidence=60)
    nested = {"leaf": "ok"}
    for index in range(12):
        nested = {f"level_{index}": nested}
    model["horizon_rows"][0]["family_payload"]["deep"] = nested

    packet = select_market_regime_read_model_source(artifact_read_model=model)

    assert packet["selected_source"] == "unavailable"
    assert packet["artifact_valid"] is False
    assert packet["read_model"] == {}
    assert packet["fallback_reason"] == "selected_model_bounding_invalid"


def test_selected_payload_is_bounded_without_mutating_source() -> None:
    model = _model(run_id="run", prediction_id="pred", generated_at="2026-07-12T01:00:00Z", confidence=60)
    model["horizon_rows"][0]["family_payload"]["long_text"] = "x" * 5000
    packet = select_market_regime_read_model_source(artifact_read_model=model)

    assert packet["selected_source"] == "artifact"
    assert len(packet["read_model"]["horizon_rows"][0]["family_payload"]["long_text"]) == 512
    assert len(model["horizon_rows"][0]["family_payload"]["long_text"]) == 5000
