# path: ./tools/run_replay_export.py
# desc: Thin CLI wrapper for replay run + export flow.

from __future__ import annotations

from _btcts_bootstrap import ensure_btcts_on_syspath
ensure_btcts_on_syspath()

import json
import os
from pathlib import Path

from btcts.replay import run_and_export_replay


REPO_ROOT = Path(__file__).resolve().parents[1]


def _env_str(name: str, default: str) -> str:
    raw = os.getenv(name, "").strip()
    return raw if raw else default


def _env_float(name: str, default: float) -> float:
    raw = os.getenv(name, "").strip()
    if not raw:
        return default
    try:
        return float(raw)
    except Exception:
        return default


def _split_path_list(raw: str) -> list[str]:
    out: list[str] = []
    for item in raw.split(os.pathsep):
        text = item.strip()
        if text:
            out.append(text)
    return out


def _resolve_input_paths(repo_root: Path) -> list[Path]:
    input_list_raw = os.getenv("BTCTS_REPLAY_INPUT_JSONL_LIST", "").strip()
    if input_list_raw:
        return [Path(p).resolve() for p in _split_path_list(input_list_raw)]

    input_default = str(repo_root / "tmp" / "replay_input.jsonl")
    single_path = Path(
        _env_str("BTCTS_REPLAY_INPUT_JSONL", input_default)
    ).resolve()
    return [single_path]


def _validate_input_paths(paths: list[Path]) -> None:
    if not paths:
        raise RuntimeError("replay input jsonl path list is empty")

    missing = [str(path) for path in paths if not path.exists()]
    if missing:
        raise RuntimeError(
            "replay input jsonl not found:\n- " + "\n- ".join(missing)
        )


def main() -> int:
    out_default = str(REPO_ROOT / "tmp" / "replay_exports")

    input_paths = _resolve_input_paths(REPO_ROOT)
    out_root = Path(_env_str("BTCTS_REPLAY_OUTPUT_ROOT", out_default)).resolve()
    replay_name = _env_str("BTCTS_REPLAY_NAME", "replay_run")
    profile_name = _env_str("BTCTS_REPLAY_PROFILE_NAME", "bitflyer")
    speed = _env_float("BTCTS_REPLAY_SPEED", 1000.0)

    _validate_input_paths(input_paths)

    session, artifacts = run_and_export_replay(
        name=replay_name,
        paths=input_paths,
        out_root=out_root,
        speed=speed,
        profile_name=profile_name,
    )

    print(
        json.dumps(
            {
                "input_path_count": len(input_paths),
                "session_summary": session.summary(),
                "artifacts": artifacts,
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())