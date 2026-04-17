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

    while engine.has_next():
        record = engine.next_event()
        if record is None:
            continue

        result = pipeline.process_record(record)
        if result is not None:
            session.add(result)

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