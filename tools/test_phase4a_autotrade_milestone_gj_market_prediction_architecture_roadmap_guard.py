# path: ./tools/test_phase4a_autotrade_milestone_gj_market_prediction_architecture_roadmap_guard.py
# desc: Guard S121 market prediction architecture roadmap contains required separation, horizons, families, extensibility, and safety boundaries.

from __future__ import annotations

import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
DOC = REPO_ROOT / "docs/architecture/AUTOTRADE_MARKET_PREDICTION_FOUNDATION_DESIGN_AND_ROADMAP_2026-06-18.md"

REQUIRED_TERMS = (
    "Execution micro",
    "Primary trade",
    "Context",
    "Market-regime prediction",
    "Trend-bias prediction",
    "Reversal-zone prediction",
    "Volatility / risk prediction",
    "Liquidity / execution-quality prediction",
    "Breakout / false-break prediction",
    "Opportunity / participation prediction",
    "Cross-venue confirmation prediction",
    "Macro-risk context prediction",
    "Human technical structure prediction",
    "Algorithmic participant footprint prediction",
    "Collection",
    "Feature generation",
    "Inference",
    "AutoTrade decision",
    "Folder-structure proposal",
    "Extensibility requirements",
    "Roadmap",
    "Connection back to AutoTrade",
    "Non-permissions",
)

REQUIRED_SAFETY_TERMS = (
    "broker execution",
    "real orders",
    "private API calls",
    "mode apply execution",
    "command ledger append",
    "UI command buttons",
    "market manipulation",
    "spoofing",
)

FORBIDDEN_ENABLEMENT_PHRASES = (
    "permit broker execution",
    "enable real orders",
    "execute broker order",
    "place live order",
    "send live order",
)


def main() -> int:
    failures: list[str] = []
    if not DOC.exists():
        failures.append(f"missing doc: {DOC.relative_to(REPO_ROOT)}")
        text = ""
    else:
        text = DOC.read_text(encoding="utf-8")

    for term in REQUIRED_TERMS:
        if term not in text:
            failures.append(f"required term missing: {term}")
    for term in REQUIRED_SAFETY_TERMS:
        if term not in text:
            failures.append(f"required safety term missing: {term}")
    lower = text.lower()
    for phrase in FORBIDDEN_ENABLEMENT_PHRASES:
        if phrase in lower:
            failures.append(f"forbidden enablement phrase present: {phrase}")

    checks = {
        "doc_present": DOC.exists(),
        "all_prediction_families_present": all(term in text for term in REQUIRED_TERMS[3:14]),
        "responsibility_separation_present": all(term in text for term in ("Collection", "Feature generation", "Inference", "AutoTrade decision")),
        "folder_structure_present": "btcts_next/src/btcts/prediction/" in text,
        "extensibility_present": "New prediction family can be added" in text,
        "roadmap_present": "GJ / S121" in text and "GX / S135" in text,
        "autotrade_connection_one_way": "collection -> features -> prediction/inference -> autotrade decision -> risk/execution gates" in text,
        "safety_boundary_present": all(term in text for term in REQUIRED_SAFETY_TERMS),
    }
    failures.extend(f"check failed: {name}" for name, ok in checks.items() if not ok)

    payload = {
        "ok": not failures,
        "phase": "phase4a_autotrade_milestone_gj_market_prediction_architecture_roadmap_guard",
        "status": "closed" if not failures else "open",
        "contract": checks,
        "doc": str(DOC.relative_to(REPO_ROOT)),
        "failures": failures,
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
