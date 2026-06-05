# path: ./btcts_next/src/btcts/replay/replay_runner.py
# desc: High-level replay runner connecting JSONL source, replay engine, and replay pipeline.

from __future__ import annotations

from pathlib import Path
from typing import Iterable

from btcts.market_engine.profiles import create_exchange_profile

from .replay_clock import ReplayClock
from .replay_engine import ReplayEngine
from .replay_export import export_replay_session
from .replay_pipeline import ReplayPipeline
from .replay_prediction_artifacts import ReplayPredictionArtifactBuilder
from .replay_session import ReplaySession
from .replay_source import JsonlReplaySource


def run_replay(
    name: str,
    paths: Iterable[Path],
    *,
    speed: float = 1000.0,
    profile_name: str = "bitflyer",
) -> ReplaySession:
    source = JsonlReplaySource(paths)
    records = source.load()

    clock = ReplayClock(speed=speed)
    engine = ReplayEngine(records, clock=clock)
    pipeline = ReplayPipeline(
        exchange_profile=create_exchange_profile(profile_name),
    )

    session = ReplaySession(
        name=name,
        source_paths=[str(Path(p)) for p in paths],
    )
    prediction_artifact_builder = ReplayPredictionArtifactBuilder(
        exchange=profile_name,
        symbol_raw="BTC_JPY",
        realized_horizon="5m",
    )

    while engine.has_next():
        record = engine.next_event()
        if record is None:
            continue

        result = pipeline.process_record(record)
        if result is not None:
            session.add(result)

            prediction_artifacts = prediction_artifact_builder.consume_result_artifacts(
                result
            )

            evaluation_entry = prediction_artifacts["evaluation_entry"]
            if evaluation_entry is not None:
                session.add_prediction_evaluation_entry(evaluation_entry)

            calibration_review = prediction_artifacts["calibration_review"]
            if calibration_review is not None:
                session.add_prediction_calibration_review(calibration_review)

            tactic_proposal_output = prediction_artifacts["tactic_proposal_output"]
            if tactic_proposal_output is not None:
                session.add_tactic_proposal_output(tactic_proposal_output)

            tactic_review_record = prediction_artifacts["tactic_review_record"]
            if tactic_review_record is not None:
                session.add_tactic_review_record(tactic_review_record)

            tactic_operation_record = prediction_artifacts["tactic_operation_record"]
            if tactic_operation_record is not None:
                session.add_tactic_operation_record(tactic_operation_record)

            prediction_direction_snapshot = prediction_artifacts[
                "prediction_direction_snapshot"
            ]
            if prediction_direction_snapshot is not None:
                session.add_prediction_direction_snapshot(
                    prediction_direction_snapshot
                )

            prediction_position_review_hint_snapshot = prediction_artifacts[
                "prediction_position_review_hint_snapshot"
            ]
            if prediction_position_review_hint_snapshot is not None:
                session.add_prediction_position_review_hint_snapshot(
                    prediction_position_review_hint_snapshot
                )

            prediction_execution_review_hint_snapshot = prediction_artifacts[
                "prediction_execution_review_hint_snapshot"
            ]
            if prediction_execution_review_hint_snapshot is not None:
                session.add_prediction_execution_review_hint_snapshot(
                    prediction_execution_review_hint_snapshot
                )

    return session


def run_and_export_replay(
    name: str,
    paths: Iterable[Path],
    *,
    out_root: Path,
    speed: float = 1000.0,
    profile_name: str = "bitflyer",
) -> tuple[ReplaySession, dict[str, str]]:
    session = run_replay(
        name=name,
        paths=paths,
        speed=speed,
        profile_name=profile_name,
    )
    artifacts = export_replay_session(
        session=session,
        out_root=out_root,
    )
    return session, artifacts