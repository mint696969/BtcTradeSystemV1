# path: ./tools/test_phase4a_prediction_system_ps_q13f_warroom_uicheck_redaction_tolerance_guard.py
# desc: Guard for PS-Q13F redaction-aware WarRoom realtime review UI Check checker behavior.

from __future__ import annotations

import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
CHECKER = REPO_ROOT / "tools/check_phase4a_prediction_system_ps_q13e_warroom_realtime_review_uicheck_snapshot.py"

REQUIRED_CHECKER_MARKERS = (
    "REDACTED_SAFE_BOUNDARY_KEYS",
    "REDACTED_VALUE",
    "<redacted>",
    "approval_or_authorization_allowed_false",
    "broker_private_api_allowed_false",
    "authorization_grant_requested_false",
    "redacted_safe_boundary_keys",
    "redaction_tolerance",
    "test_ps_q13f_warroom_realtime_review_uicheck_snapshot_checker_redaction_tolerance",
    "parameter_apply_allowed_any must be false",
    "parameter_staging_write_allowed_any must be false",
)

FORBIDDEN_CHECKER_MARKERS = (
    "append_decision(",
    "append_command(",
    "send_order(",
    "create_order(",
    "call_private_api(",
    "apply_live_parameters(",
    "mutate_live_parameters(",
    "staging_write_allowed=True",
    "apply_allowed=True",
)


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8-sig")


def main() -> int:
    failures: list[str] = []
    if not CHECKER.exists():
        failures.append(f"missing file: {CHECKER.relative_to(REPO_ROOT)}")
    checker_text = _read(CHECKER) if CHECKER.exists() else ""
    for marker in REQUIRED_CHECKER_MARKERS:
        if marker not in checker_text:
            failures.append(f"missing checker marker: {marker}")
    for marker in FORBIDDEN_CHECKER_MARKERS:
        if marker in checker_text:
            failures.append(f"forbidden checker marker present: {marker}")
    payload = {
        "ok": not failures,
        "guard": "ps_q13f_warroom_uicheck_redaction_tolerance",
        "redaction_tolerance": {
            "checker_present": CHECKER.exists(),
            "allowed_redacted_boundary_keys": [
                "approval_or_authorization_allowed_false",
                "broker_private_api_allowed_false",
                "authorization_grant_requested_false",
            ],
            "parameter_apply_allowed_any": False,
            "parameter_staging_write_allowed_any": False,
            "display_only_checker": True,
        },
        "failures": failures,
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if not failures else 1


def test_ps_q13f_warroom_uicheck_redaction_tolerance_guard() -> None:
    assert main() == 0


if __name__ == "__main__":
    raise SystemExit(main())
