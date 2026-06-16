# path: ./tools/test_phase4a_operator_ui_polish_roadmap_guard.py
# desc: CP-0 guard for Operator UI polish roadmap / phase design / responsibility boundaries before implementation.

from __future__ import annotations

from _btcts_bootstrap import ensure_btcts_on_syspath
ensure_btcts_on_syspath()

import json
import py_compile
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
SELF_PATH = "tools/test_phase4a_operator_ui_polish_roadmap_guard.py"
ROADMAP = REPO_ROOT / "tmp" / "gpt_room" / "memory" / "roadmaps" / "2026-06-11_operator_ui_polish_to_prediction_entry_roadmap.md"
PHASE_DESIGN = REPO_ROOT / "tmp" / "gpt_room" / "memory" / "roadmaps" / "2026-06-11_operator_ui_polish_phase_design.md"
STATUS = REPO_ROOT / "tmp" / "gpt_room" / "08_STATUS.md"
FOCUS = REPO_ROOT / "tmp" / "gpt_room" / "09_FOCUS.json"
STATE = REPO_ROOT / "tmp" / "gpt_room" / "11_STATE.json"

REQUIRED_ROADMAP_FRAGMENTS = [
    "Operator UI polish to Prediction entry roadmap",
    "Starting repo truth: d0bdb027 or later",
    "Bring the Operator UI to a coherent first-complete state",
    "Dashboard = top-level hub for tabs and alerts.",
    "Widgets = independent real-time display units inside each tab.",
    "Health tab",
    "Collector tab",
    "WarRoom tab",
    "CP-0: UI roadmap and boundary checkpoint",
    "CP-1: Health tab widget readability checkpoint",
    "CP-2: Health tab language presentation checkpoint",
    "CP-3: Collector tab widget structure checkpoint",
    "CP-4: WarRoom tab widget structure checkpoint",
    "CP-5: Other tabs consistency checkpoint",
    "CP-6: Dashboard hub alerts and navigation checkpoint",
    "CP-7: UI first-complete close checkpoint",
    "payload loader",
    "dataset reader",
    "copy executor",
    "delete executor",
    "archive GC execution",
    "inference/training",
    "broker/order/execution",
    "market_engine integration",
    "collector writer/backfill/runtime behavior",
    "app.py routing/layout rewrite",
    "full UI architecture rewrite",
]

REQUIRED_PHASE_DESIGN_FRAGMENTS = [
    "Operator UI polish phase design",
    "Status: design-before-implementation",
    "prevent ad-hoc UI changes across threads",
    "app.py = existing sidebar/page dispatch/language/scale/refresh owner",
    "components/live_shell.py = common panel/widget/slot shell",
    "ui_text.py = current language text lookup entry",
    "Do not start with app.py rewrite.",
    "Do not build a second UI framework.",
    "Use live_shell as the common widget shell",
    "Use ui_text / text-layer keys for display language work.",
    "Phase CP-0: Roadmap and boundary design checkpoint",
    "Phase CP-1: Health tab widget readability",
    "Phase CP-2: Health language presentation",
    "Phase CP-3: Collector tab widget structure",
    "Phase CP-4: WarRoom tab widget structure",
    "Phase CP-5: Other tabs consistency",
    "Phase CP-6: Dashboard hub alerts and navigation",
    "Phase CP-7: UI first-complete close",
    "L3 = market meaning owner",
    "L4 = shared-first read-model / shape owner",
    "UI = display and orchestration owner",
]

REQUIRED_STATUS_FRAGMENTS = [
    "2026-06-11 current HEAD sync before UI work",
    "current_repo_head = d0bdb027",
    "2026-06-11 Operator UI polish to Prediction entry roadmap",
    "2026-06-11 Operator UI polish phase design",
    "Health -> Collector -> WarRoom -> other tabs",
    "Start CP-0 guard/design close, then CP-1 Health widget readability planning.",
]

ROOM_FRAGMENTS = [
    "phase4a_dashboard_hub_display_source_final_bundle_closed_next_thread_ready",
    "dashboard_hub_display_source_final_bundle_sync_closed",
]

FORBIDDEN_ROADMAP_CLAIMS = [
    "payload_loader_status = opened",
    "dataset_reader_status = opened",
    "copy executor opened",
    "delete executor opened",
    "archive GC enabled",
    "inference/training opened",
    "broker/order/execution opened",
    "market_engine integration opened",
]


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.exists() else ""


def _compile(rel_path: str, failures: list[str]) -> dict[str, Any]:
    path = REPO_ROOT / rel_path
    cache = REPO_ROOT / "tmp" / "_guard_py_compile_cache" / "operator_ui_polish_roadmap"
    cache.mkdir(parents=True, exist_ok=True)
    try:
        py_compile.compile(str(path), cfile=str(cache / (rel_path.replace("/", "__") + ".pyc")), doraise=True)
        return {"ok": True}
    except Exception as exc:
        failures.append(f"py_compile failed: {rel_path}: {exc}")
        return {"ok": False, "error": str(exc)}


def _require_fragments(path: Path, fragments: list[str], label: str, failures: list[str]) -> dict[str, Any]:
    text = _read(path)
    missing: list[str] = []
    if not path.exists():
        missing.append("<file exists>")
    for fragment in fragments:
        if fragment not in text:
            missing.append(fragment)
    for fragment in missing:
        failures.append(f"{label} missing fragment: {fragment}")
    return {"path": str(path.relative_to(REPO_ROOT)), "missing": missing}


def _check_room_current_focus(failures: list[str]) -> dict[str, Any]:
    results: dict[str, Any] = {}
    for path in (FOCUS, STATE):
        text = _read(path)
        missing = [fragment for fragment in ROOM_FRAGMENTS if fragment not in text]
        for fragment in missing:
            failures.append(f"room focus/state missing stable close fragment: {path.relative_to(REPO_ROOT)}::{fragment}")
        results[str(path.relative_to(REPO_ROOT))] = {"missing": missing}
    return results


def _check_forbidden(failures: list[str]) -> dict[str, Any]:
    joined = "\n".join(_read(path) for path in (ROADMAP, PHASE_DESIGN, STATUS))
    hits = [token for token in FORBIDDEN_ROADMAP_CLAIMS if token in joined]
    for token in hits:
        failures.append(f"operator UI polish roadmap/design contains forbidden opened-boundary claim: {token}")
    return {"hits": hits}


def main() -> int:
    failures: list[str] = []
    checks = {
        "compile_self": _compile(SELF_PATH, failures),
        "roadmap_required_fragments": _require_fragments(ROADMAP, REQUIRED_ROADMAP_FRAGMENTS, "roadmap", failures),
        "phase_design_required_fragments": _require_fragments(PHASE_DESIGN, REQUIRED_PHASE_DESIGN_FRAGMENTS, "phase_design", failures),
        "status_required_fragments": _require_fragments(STATUS, REQUIRED_STATUS_FRAGMENTS, "status", failures),
        "room_current_focus": _check_room_current_focus(failures),
        "forbidden_opened_boundary_claims": _check_forbidden(failures),
    }
    payload = {
        "ok": not failures,
        "phase": "phase4a_operator_ui_polish_roadmap_guard_cp0",
        "cp": "CP-0",
        "status": "closed" if not failures else "open",
        "next_recommended_cp": "CP-1 Health tab widget readability" if not failures else "fix_cp0_docs_or_status",
        "responsibility_separation": {
            "l3": "market meaning owner",
            "l4": "shared read-model / shape owner",
            "ui": "display and orchestration owner",
            "live_shell": "common widget shell",
        },
        "failures": failures,
        "checks": checks,
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
