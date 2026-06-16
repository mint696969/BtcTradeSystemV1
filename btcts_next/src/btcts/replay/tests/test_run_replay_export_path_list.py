# path: ./btcts_next/src/btcts/replay/tests/test_run_replay_export_path_list.py
# desc: Verify run_replay_export tool resolves multi-path replay inputs safely.

from __future__ import annotations

import importlib.util
import os
import sys
import tempfile
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[5]
_TOOLS_DIR = _REPO_ROOT / "tools"
if str(_TOOLS_DIR) not in sys.path:
    sys.path.insert(0, str(_TOOLS_DIR))


def _load_tool_module():
    module_path = _TOOLS_DIR / "run_replay_export.py"
    spec = importlib.util.spec_from_file_location("run_replay_export", module_path)
    if spec is None or spec.loader is None:
        raise RuntimeError("failed to load run_replay_export module spec")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main() -> int:
    module = _load_tool_module()

    with tempfile.TemporaryDirectory() as tmp_dir:
        base = Path(tmp_dir)
        first = base / "snapshot.jsonl"
        second = base / "diff.jsonl"
        first.write_text("{}\n", encoding="utf-8")
        second.write_text("{}\n", encoding="utf-8")

        original_list = os.environ.get("BTCTS_REPLAY_INPUT_JSONL_LIST")
        original_single = os.environ.get("BTCTS_REPLAY_INPUT_JSONL")
        try:
            os.environ["BTCTS_REPLAY_INPUT_JSONL_LIST"] = (
                f"{first}{os.pathsep}{second}"
            )
            os.environ.pop("BTCTS_REPLAY_INPUT_JSONL", None)

            resolved = module._resolve_input_paths(_REPO_ROOT)
            assert resolved == [first.resolve(), second.resolve()]

            module._validate_input_paths(resolved)
        finally:
            if original_list is None:
                os.environ.pop("BTCTS_REPLAY_INPUT_JSONL_LIST", None)
            else:
                os.environ["BTCTS_REPLAY_INPUT_JSONL_LIST"] = original_list

            if original_single is None:
                os.environ.pop("BTCTS_REPLAY_INPUT_JSONL", None)
            else:
                os.environ["BTCTS_REPLAY_INPUT_JSONL"] = original_single

    print("ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())