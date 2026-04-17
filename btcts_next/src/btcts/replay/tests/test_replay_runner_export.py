# path: ./btcts_next/src/btcts/replay/tests/test_replay_runner_export.py
# desc: Verify replay runner can delegate session export through a thin helper without changing run_replay itself.

from __future__ import annotations

import sys
import tempfile
from pathlib import Path

_SRC_ROOT = Path(__file__).resolve().parents[4]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

import btcts.replay.replay_runner as replay_runner  # noqa: E402
from btcts.replay.replay_session import ReplaySession  # noqa: E402


def main() -> int:
    original_run_replay = replay_runner.run_replay
    original_export_replay_session = replay_runner.export_replay_session

    try:
        replay_runner.run_replay = lambda **kwargs: ReplaySession(
            name=kwargs["name"],
            source_paths=[str(Path(p)) for p in kwargs["paths"]],
        )
        replay_runner.export_replay_session = lambda **kwargs: {
            "session_dir": str(Path(kwargs["out_root"]) / "dummy_session"),
            "report_path": str(Path(kwargs["out_root"]) / "dummy_report.json"),
            "manifest_path": str(Path(kwargs["out_root"]) / "dummy_manifest.json"),
            "results_path": str(Path(kwargs["out_root"]) / "dummy_results.jsonl"),
            "prediction_evaluation_report_path": None,
        }

        with tempfile.TemporaryDirectory() as tmp_dir:
            session, artifacts = replay_runner.run_and_export_replay(
                name="runner_export_test",
                paths=[Path("D:/dummy/replay_source.jsonl")],
                out_root=Path(tmp_dir),
            )

        assert session.name == "runner_export_test"
        assert session.source_paths == ["D:\\dummy\\replay_source.jsonl"]
        assert artifacts["session_dir"].endswith("dummy_session")
        assert artifacts["report_path"].endswith("dummy_report.json")
        assert artifacts["manifest_path"].endswith("dummy_manifest.json")
        assert artifacts["results_path"].endswith("dummy_results.jsonl")
        assert artifacts["prediction_evaluation_report_path"] is None
    finally:
        replay_runner.run_replay = original_run_replay
        replay_runner.export_replay_session = original_export_replay_session

    print("ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())