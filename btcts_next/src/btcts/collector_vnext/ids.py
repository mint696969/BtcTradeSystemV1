# path: ./btcts_next/src/btcts/collector_vnext/ids.py
# desc: ID and local sequence helpers for Collector vNext.

from __future__ import annotations

import itertools
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Iterator
from uuid import uuid4


def utc_compact_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def make_session_id(collector_id: str) -> str:
    return f"{collector_id}-sess-{utc_compact_now()}-{uuid4().hex[:8]}"


def make_stream_session_id(collector_id: str, exchange: str, channel: str) -> str:
    safe_exchange = exchange.replace("/", "_").replace(" ", "_")
    safe_channel = channel.replace("/", "_").replace(" ", "_")
    return f"{collector_id}-stream-{safe_exchange}-{safe_channel}-{utc_compact_now()}-{uuid4().hex[:8]}"


@dataclass
class SequenceManager:
    _counter: Iterator[int]
    _current: int

    @classmethod
    def start(cls, start_from: int = 1) -> "SequenceManager":
        return cls(
            _counter=itertools.count(start_from),
            _current=start_from - 1,
        )

    def next(self) -> int:
        self._current = int(next(self._counter))
        return self._current

    def current(self) -> int:
        return int(self._current)


def make_record_id(
    *,
    exchange: str,
    stream: str,
    stream_session_id: str,
    event_type: str,
    sequence_id: int,
) -> str:
    """
    Canonical record_id

    Format:
        {exchange}:{stream}:{stream_session_id}:{event_type}:{sequence_id}

    Guarantees:
        - globally unique across canonical records
        - monotonic within a stream_session when sequence_id is monotonic
        - human-readable and traceable
    """
    return f"{exchange}:{stream}:{stream_session_id}:{event_type}:{sequence_id}"