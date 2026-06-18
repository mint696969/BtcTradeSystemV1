# path: ./tools/test_phase4a_autotrade_milestone_gz_preview_consumption_design_guard.py
# desc: Guard S137 AutoTrade prediction preview consumption design remains documentation-only and selects read-only status/preflight seam.

from __future__ import annotations

import json
import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
DOC = REPO_ROOT / "docs/architecture/AUTOTRADE_PREDICTION_PREVIEW_CONSUMPTION_DESIGN_2026-06-18.md"
REQUIRED_TERMS = (
    "design-only / documentation / non-executing",
    "Prediction Preview Read-Only Status / Preflight Seam",
    "AutoTradeShadowSignalPreview",
    "PredictionPreArmedReadinessSnapshot",
    "btcts_next/src/btcts/autotrade/live_shadow.py",
    "S138 AutoTrade prediction preview status contract",
    "live_shadow.py is untouched",
    "no append_decision_jsonl",
    "no run_shadow_decision_from_snapshot",
    "no mode apply",
    "no broker",
)
REJECTED_TERMS = (
    "This design packet permits broker execution",
    "mode apply is allowed",
    "grant execution is allowed",
    "append_decision_jsonl usage is allowed",
    "modify run_shadow_decision_from_snapshot now",
)
PROTECTED_CODE_PREFIXES = (
    "btcts_next/src/btcts/autotrade/",
    "btcts_next/src/btcts/collector_vnext/",
    "btcts_next/src/btcts/prediction/",
)
ALLOWED_DIRTY_MARKERS = (
    "docs/architecture/AUTOTRADE_PREDICTION_PREVIEW_CONSUMPTION_DESIGN_2026-06-18.md",
    "tools/test_phase4a_autotrade_milestone_gz_preview_consumption_design_guard.py",
    "tools/test_phase4a_autotrade_milestone_gz_preview_consumption_design_close_guard.py",
)


def main() -> int:
    failures: list[str] = []
    text = DOC.read_text(encoding="utf-8") if DOC.exists() else ""
    checks = {
        "doc_exists": DOC.exists(),
        "required_terms_present": all(term in text for term in REQUIRED_TERMS),
        "rejected_terms_absent": not any(term in text for term in REJECTED_TERMS),
        "chosen_seam_is_read_only": "Chosen first seam" in text and "Prediction Preview Read-Only Status / Preflight Seam" in text,
        "next_slice_s138_status_contract": "S138 AutoTrade prediction preview status contract" in text,
        "non_permissions_include_append_and_shadow_mods": all(term in text for term in ("append_decision_jsonl usage", "run_shadow_decision_from_snapshot modification", "run_latest_market_state_shadow_decision modification", "build_action_candidate modification")),
    }
    failures.extend(f"check failed: {name}" for name, ok in checks.items() if not ok)
    proc = subprocess.run(["git", "status", "--short"], cwd=REPO_ROOT, text=True, capture_output=True, check=True)
    dirty = [line for line in proc.stdout.splitlines() if line.strip()]
    protected_dirty_hits = [line for line in dirty if any(prefix in line for prefix in PROTECTED_CODE_PREFIXES)]
    docs_only_dirty = all(any(marker in line for marker in ALLOWED_DIRTY_MARKERS) for line in dirty)
    checks["docs_and_guard_only_dirty"] = docs_only_dirty
    checks["protected_code_dirs_untouched"] = not protected_dirty_hits
    if not docs_only_dirty:
        failures.append("working tree has unexpected non-doc/guard changes")
    failures.extend(f"protected code dirty during GZ design-only slice: {hit}" for hit in protected_dirty_hits)
    payload = {
        "ok": not failures,
        "phase": "phase4a_autotrade_milestone_gz_preview_consumption_design_guard",
        "status": "closed" if not failures else "open",
        "contract": checks,
        "sample": {
            "doc": str(DOC.relative_to(REPO_ROOT)),
            "chosen_first_seam": "Prediction Preview Read-Only Status / Preflight Seam",
            "next_recommended_slice": "S138 AutoTrade prediction preview status contract",
        },
        "protected_dirty_hits": protected_dirty_hits,
        "failures": failures,
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if not failures else 1


def test_preview_consumption_design_guard_closes() -> None:
    assert main() == 0


if __name__ == "__main__":
    raise SystemExit(main())
