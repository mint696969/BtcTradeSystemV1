# path: ./tools/run_market_engine_onboarding.py
# desc: Thin CLI wrapper for market_engine onboarding runner using normalized event jsonl input.

from __future__ import annotations

from _btcts_bootstrap import ensure_btcts_on_syspath
ensure_btcts_on_syspath()

import json
import os
from pathlib import Path
from typing import Any

from btcts.market_engine.assembler.profiles.bitflyer import BitflyerProfile
from btcts.market_engine.onboarding.runner import run_onboarding


REPO_ROOT = Path(__file__).resolve().parents[1]


def _env_str(name: str, default: str) -> str:
    raw = os.getenv(name, "").strip()
    return raw if raw else default


def _env_int(name: str, default: int) -> int:
    raw = os.getenv(name, "").strip()
    if not raw:
        return default
    try:
        return int(raw)
    except Exception:
        return default


def _load_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as f:
        for line_no, line in enumerate(f, start=1):
            text = line.strip()
            if not text:
                continue
            try:
                obj = json.loads(text)
            except Exception as e:
                raise RuntimeError(f"invalid json at line {line_no}: {path}") from e
            if isinstance(obj, dict):
                rows.append(obj)
    return rows


def main() -> int:
    input_default = str(REPO_ROOT / "tmp" / "market_engine_onboarding_input.jsonl")
    input_path = Path(_env_str("BTCTS_ONBOARDING_INPUT_JSONL", input_default)).resolve()
    profile_name_hint = _env_str("BTCTS_ONBOARDING_PROFILE_HINT", "bitflyer")
    capture_limit = _env_int("BTCTS_ONBOARDING_CAPTURE_LIMIT", 20)

    if not input_path.exists():
        raise RuntimeError(f"input jsonl not found: {input_path}")

    normalized_events = _load_jsonl(input_path)

    profile = None
    if profile_name_hint == "bitflyer":
        profile = BitflyerProfile()

    result = run_onboarding(
        normalized_events=normalized_events,
        profile_name_hint=profile_name_hint,
        profile=profile,
        capture_limit=capture_limit,
    )

    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())