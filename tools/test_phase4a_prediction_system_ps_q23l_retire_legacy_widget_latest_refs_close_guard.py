# path: ./tools/test_phase4a_prediction_system_ps_q23l_retire_legacy_widget_latest_refs_close_guard.py
# desc: Close guard for PS-Q23L retiring legacy Q18 widget latest refs.

from __future__ import annotations

import json
import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
EXPECTED = {
    "btcts_next/src/btcts/apps/operator_ui/prediction_warroom/sources/latest_prediction_summary_widget_q18ae_candidate_resolver_refresh.py",
    "btcts_next/src/btcts/apps/operator_ui/prediction_warroom/sources/latest_prediction_summary_widget_q18af_schema_probe.py",
    "btcts_next/src/btcts/apps/operator_ui/prediction_warroom/mapping/latest_prediction_summary_widget_q18ag_payload_to_props_mapping_preflight.py",
    "btcts_next/src/btcts/apps/operator_ui/prediction_warroom/mapping/latest_prediction_summary_widget_q18ah_render_disabled_packet_builder_validation.py",
    "tools/test_phase4a_prediction_system_ps_q23k_legacy_latest_shrink_readiness_no_write.py",
    "docs/strategy/PREDICTION_SYSTEM_PS_Q23L_RETIRE_LEGACY_WIDGET_LATEST_REFS_2026-06-28.md",
    "tools/test_phase4a_prediction_system_ps_q23l_retire_legacy_widget_latest_refs.py",
    "tools/test_phase4a_prediction_system_ps_q23l_retire_legacy_widget_latest_refs_close_guard.py",
}


def _dirty() -> set[str]:
    proc = subprocess.run(["git", "status", "--short", "--untracked-files=all"], cwd=REPO_ROOT, text=True, capture_output=True, check=True)
    out: set[str] = set()
    for line in proc.stdout.splitlines():
        path = line[3:].strip().replace(chr(92), "/")
        if path.startswith("tmp/work/") or path.startswith("tmp/gpt_room/") or path.endswith(".pyc") or "/__pycache__/" in path:
            continue
        out.add(path)
    return out


def main_guard() -> int:
    dirty = _dirty()
    result = {
        "ok": dirty == EXPECTED,
        "guard": "ps_q23l_retire_legacy_widget_latest_refs_close_guard",
        "dirty_paths": sorted(dirty),
        "missing_dirty": sorted(EXPECTED - dirty),
        "unexpected_dirty": sorted(dirty - EXPECTED),
        "contract": {
            "legacy_widget_latest_refs_retired": True,
            "q18_chain_runtime_reactivation": False,
            "legacy_latest_shrink_executed": False,
            "scheduler_action_changed": False,
            "runtime_artifact_write_changed": False,
            "broker_autotrade": False,
        },
    }
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main_guard())
