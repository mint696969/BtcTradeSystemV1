# path: ./tools/test_market_engine_onboarding_rebuild_accuracy.py
# desc: Validate snapshot->diff rebuild accuracy from onboarding input JSONL.

from __future__ import annotations

from _btcts_bootstrap import ensure_btcts_on_syspath
ensure_btcts_on_syspath()

import json
import os
from pathlib import Path
from typing import Any

from btcts.market_engine.onboarding.bitflyer_rebuild_review import build_bitflyer_rebuild_review


REPO_ROOT = Path(__file__).resolve().parents[1]


def _env_str(name: str, default: str) -> str:
    value = os.environ.get(name)
    return value.strip() if isinstance(value, str) and value.strip() else default


def _load_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as fh:
        for line in fh:
            text = line.strip()
            if not text:
                continue
            raw = json.loads(text)
            if isinstance(raw, dict):
                rows.append(raw)
    return rows


def main() -> int:
    input_default = str(REPO_ROOT / "tmp" / "market_engine_onboarding_input.jsonl")
    input_jsonl = Path(_env_str("BTCTS_ONBOARDING_INPUT_JSONL", input_default)).resolve()
    profile_name_hint = _env_str("BTCTS_ONBOARDING_PROFILE_HINT", "unknown")

    if not input_jsonl.exists():
        raise RuntimeError(f"input jsonl not found: {input_jsonl}")

    normalized_events = _load_jsonl(input_jsonl)

    result = build_bitflyer_rebuild_review(
        normalized_events=normalized_events,
        profile_name_hint=profile_name_hint,
    )
    result["input_jsonl"] = str(input_jsonl)

    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())