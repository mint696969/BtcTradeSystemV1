# path: ./btcts_next/src/btcts/replay/replay_prediction_feedback.py
# desc: Thin replay-side bridge that converts replay session prediction artifacts into shared replay feedback.

from __future__ import annotations

from typing import Any

from btcts.processing.l4_consumer_models.shared import (
    PredictionReplayFeedbackBuildInput,
    build_prediction_replay_feedback,
)

from .prediction_evaluation_report import build_prediction_evaluation_report
from .replay_session import ReplaySession


def _normalize_dict(value: Any) -> dict[str, Any]:
    if not isinstance(value, dict):
        return {}
    return dict(value)


def build_prediction_replay_feedback_from_artifacts(
    *,
    name: str,
    prediction_evaluation_entries: list[dict[str, Any]] | None = None,
    prediction_calibration_review: dict[str, Any] | None = None,
    source_kind: str = "replay_session_prediction_feedback",
    diagnostics: dict[str, Any] | None = None,
) -> dict[str, Any]:
    entries = list(prediction_evaluation_entries or [])
    calibration_review = _normalize_dict(prediction_calibration_review)

    evaluation_report = build_prediction_evaluation_report(
        name=f"{name}_prediction_evaluation",
        entries=entries,
    )

    return build_prediction_replay_feedback(
        PredictionReplayFeedbackBuildInput(
            calibration_review=calibration_review,
            evaluation_report=evaluation_report,
            source_kind=source_kind,
            diagnostics={
                "builder_type": "replay_prediction_feedback",
                "session_name": name,
                **dict(diagnostics or {}),
            },
        )
    )


def build_prediction_replay_feedback_from_session(
    session: ReplaySession,
) -> dict[str, Any] | None:
    if (
        not session.prediction_evaluation_entries
        and not session.prediction_calibration_reviews
    ):
        return None

    latest_review = {}
    if session.prediction_calibration_reviews:
        latest_review = _normalize_dict(session.prediction_calibration_reviews[-1])

    return build_prediction_replay_feedback_from_artifacts(
        name=session.name,
        prediction_evaluation_entries=session.prediction_evaluation_entries,
        prediction_calibration_review=latest_review,
        diagnostics={
            "source_paths": tuple(session.source_paths),
            "prediction_evaluation_entry_count": len(
                session.prediction_evaluation_entries
            ),
            "prediction_calibration_review_count": len(
                session.prediction_calibration_reviews
            ),
        },
    )