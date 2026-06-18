# path: ./tools/test_phase4a_autotrade_milestone_gy_prediction_foundation_index_guard.py
# desc: Guard S136 prediction foundation integration index remains documentation/status-only and preserves non-execution boundaries.

from __future__ import annotations

import json
import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
DOC = REPO_ROOT / "docs/architecture/AUTOTRADE_PREDICTION_FOUNDATION_INTEGRATION_INDEX_2026-06-18.md"
REQUIRED_SLICES = tuple(f"S{num}" for num in range(121, 136))
REQUIRED_TERMS = (
    "documentation / status-only / non-executing",
    "AutoTradeShadowSignalPreview",
    "PredictionPreArmedReadinessSnapshot",
    "ReplayValidationResult",
    "PredictionCalibrationReport",
    "Still forbidden unless explicitly rescoped",
    "Collector does not trade.",
    "Prediction does not trade.",
    "AutoTrade does not scrape public market data directly.",
    "Execution does not invent market predictions.",
    "UI does not secretly execute.",
    "S137 AutoTrade prediction preview consumption design packet",
)
FORBIDDEN_DOC_TOKENS = (
    "This document permits broker execution",
    "This document authorizes broker execution",
    "grant execution is allowed",
    "mode apply is allowed",
    "real orders are allowed",
)
PROTECTED_DIR_PREFIXES = (
    "btcts_next/src/btcts/autotrade/",
    "btcts_next/src/btcts/collector_vnext/",
    "btcts_next/src/btcts/prediction/",
)


def main() -> int:
    failures: list[str] = []
    if not DOC.exists():
        failures.append(f"missing doc: {DOC.relative_to(REPO_ROOT)}")
        text = ""
    else:
        text = DOC.read_text(encoding="utf-8")
    checks = {
        "doc_exists": DOC.exists(),
        "all_s121_s135_listed": all(item in text for item in REQUIRED_SLICES),
        "required_terms_present": all(term in text for term in REQUIRED_TERMS),
        "forbidden_doc_tokens_absent": not any(token in text for token in FORBIDDEN_DOC_TOKENS),
        "mentions_no_execution_permissions": all(term in text for term in ("broker execution", "real orders", "AutoTrade mode apply", "Pre-Armed grant execution", "actual AutoTrade publication/write")),
        "next_slice_is_design_only": "S137 AutoTrade prediction preview consumption design packet" in text and "without changing behavior" in text,
    }
    failures.extend(f"check failed: {name}" for name, ok in checks.items() if not ok)

    proc = subprocess.run(["git", "status", "--short"], cwd=REPO_ROOT, text=True, capture_output=True, check=True)
    protected_dirty_hits = [line for line in proc.stdout.splitlines() if any(prefix in line for prefix in PROTECTED_DIR_PREFIXES)]
    failures.extend(f"protected code dirty during GY docs-only slice: {hit}" for hit in protected_dirty_hits)
    allowed_dirty = [line for line in proc.stdout.splitlines() if line.strip()]
    docs_only_dirty = all(
        "docs/architecture/AUTOTRADE_PREDICTION_FOUNDATION_INTEGRATION_INDEX_2026-06-18.md" in line
        or "tools/test_phase4a_autotrade_milestone_gy_prediction_foundation_index_guard.py" in line
        or "tools/test_phase4a_autotrade_milestone_gy_prediction_foundation_index_close_guard.py" in line
        for line in allowed_dirty
    )
    checks["docs_and_guard_only_dirty"] = docs_only_dirty
    if not docs_only_dirty:
        failures.append("working tree has unexpected non-doc/guard changes")

    payload = {
        "ok": not failures,
        "phase": "phase4a_autotrade_milestone_gy_prediction_foundation_index_guard",
        "status": "closed" if not failures else "open",
        "contract": checks | {"protected_code_dirs_untouched": not protected_dirty_hits},
        "sample": {
            "doc": str(DOC.relative_to(REPO_ROOT)),
            "listed_slice_count": sum(1 for item in REQUIRED_SLICES if item in text),
            "next_recommended_slice": "S137 AutoTrade prediction preview consumption design packet",
        },
        "protected_dirty_hits": protected_dirty_hits,
        "failures": failures,
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if not failures else 1


def test_prediction_foundation_index_guard_closes() -> None:
    assert main() == 0


if __name__ == "__main__":
    raise SystemExit(main())
