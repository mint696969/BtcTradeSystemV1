# path: ./btcts_next/src/btcts/replay/replay_report.py
# desc: Build replay summary reports from fusion results.

from __future__ import annotations

from typing import Dict, List


def build_replay_report(name: str, source_paths: List[str], results: List[Dict]) -> Dict:
    board_count = 0
    trade_count = 0
    microstructure_event_count = 0
    signal_count = 0

    event_name_counts: Dict[str, int] = {}

    for row in results:
        kind = row.get("kind")

        if kind == "board":
            board_count += 1
            result = row.get("result")
            if isinstance(result, dict) and result.get("signal") is not None:
                signal_count += 1

                for event in result.get("events", []):
                    event_name = str(event.get("event_name") or "")
                    if event_name:
                        event_name_counts[event_name] = event_name_counts.get(event_name, 0) + 1

        elif kind == "trade":
            trade_count += 1
            for event in row.get("microstructure", []):
                event_name = str(event.get("event_name") or "")
                if event_name:
                    microstructure_event_count += 1
                    event_name_counts[event_name] = event_name_counts.get(event_name, 0) + 1

    return {
        "name": name,
        "source_paths": source_paths,
        "result_count": len(results),
        "board_count": board_count,
        "trade_count": trade_count,
        "signal_count": signal_count,
        "microstructure_event_count": microstructure_event_count,
        "event_name_counts": dict(sorted(event_name_counts.items())),
    }