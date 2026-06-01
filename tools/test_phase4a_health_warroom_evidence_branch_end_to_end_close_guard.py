# path: ./tools/test_phase4a_health_warroom_evidence_branch_end_to_end_close_guard.py
# desc: Phase 4-A Health/WarRoom evidence presentation branch end-to-end close guard.

from __future__ import annotations

from _btcts_bootstrap import ensure_btcts_on_syspath
ensure_btcts_on_syspath()

import json
import py_compile
import subprocess
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]

SELF_PATH = "tools/test_phase4a_health_warroom_evidence_branch_end_to_end_close_guard.py"
SPEC_PATH = "tmp/docs/architecture/PHASE4A_HEALTH_WARROOM_EVIDENCE_BRANCH_END_TO_END_CLOSE_2026-06-01.md"
PAGE_LOCAL_GUARD_PATH = "tools/test_phase4a_health_warroom_evidence_payload_lowering_page_local_wiring_guard.py"
BRIDGE_GUARD_PATH = "tools/test_phase4a_health_warroom_evidence_presentation_payload_lowering_channel_wiring_bridge_guard.py"
LOWERING_GUARD_PATH = "tools/test_phase4a_health_warroom_evidence_presentation_payload_lowering_channel_guard.py"
UPSTREAM_GUARD_PATH = "tools/test_phase4a_health_warroom_evidence_presentation_upstream_payload_producer_guard.py"
HEALTH_PAGE_PATH = "btcts_next/src/btcts/apps/operator_ui/views/health_page.py"
WARROOM_PAGE_PATH = "btcts_next/src/btcts/apps/operator_ui/views/warroom_page.py"
BRIDGE_PATH = "btcts_next/src/btcts/apps/operator_ui/components/evidence_presentation_lowering_bridge.py"
FOCUS_PATH = "tmp/gpt_room/09_FOCUS.json"
STATE_PATH = "tmp/gpt_room/11_STATE.json"
PRIMARY_COMPACT_PATH = "tmp/work/phase4a_health_warroom_evidence_consumption_ui_rendering/run_primary_guard_compact_v1.py"

FORBIDDEN_RUNTIME_ROOTS = [
    "btcts_next/src/btcts/market_engine",
    "btcts_next/src/btcts/collector",
    "btcts_next/src/btcts/collector_vnext",
    "btcts_next/src/btcts/execution",
    "btcts_next/src/btcts/broker",
]

BRIDGE_HELPERS = [
    "lower_health_snapshot_evidence_presentation_for_ui",
    "lower_warroom_session_state_evidence_presentation_for_ui",
]


def _read(rel_path: str) -> str:
    path = REPO_ROOT / rel_path
    return path.read_text(encoding="utf-8") if path.exists() else ""


def _compile(rel_path: str, failures: list[str]) -> dict[str, Any]:
    path = REPO_ROOT / rel_path
    if not path.exists():
        failures.append(f"missing compile target: {rel_path}")
        return {"ok": False, "missing": True}
    cache = REPO_ROOT / "tmp" / "_guard_py_compile_cache" / "health_warroom_evidence_branch_close"
    cache.mkdir(parents=True, exist_ok=True)
    try:
        py_compile.compile(str(path), cfile=str(cache / (rel_path.replace("/", "__") + ".pyc")), doraise=True)
        return {"ok": True}
    except Exception as exc:
        failures.append(f"py_compile failed: {rel_path}: {exc}")
        return {"ok": False, "error": str(exc)}


def _run_json_guard(rel_path: str, failures: list[str], *, timeout: int = 1200) -> dict[str, Any]:
    proc = subprocess.run(
        [sys.executable, str(REPO_ROOT / rel_path)],
        cwd=str(REPO_ROOT),
        text=True,
        capture_output=True,
        timeout=timeout,
    )
    try:
        parsed = json.loads(proc.stdout)
    except Exception as exc:
        failures.append(f"{rel_path} did not emit JSON: {exc}")
        return {
            "ok": False,
            "returncode": proc.returncode,
            "stdout_tail": (proc.stdout or "")[-1800:],
            "stderr_tail": (proc.stderr or "")[-1800:],
        }
    ok = proc.returncode == 0 and parsed.get("ok") is True and parsed.get("failures") == []
    if not ok:
        failures.append(f"{rel_path} must return ok true and failures []")
    return {
        "ok": ok,
        "returncode": proc.returncode,
        "phase": parsed.get("phase"),
        "stdout_tail": (proc.stdout or "")[-1800:],
        "stderr_tail": (proc.stderr or "")[-1800:],
    }


def _run_primary_compact(failures: list[str]) -> dict[str, Any]:
    proc = subprocess.run(
        [sys.executable, str(REPO_ROOT / PRIMARY_COMPACT_PATH)],
        cwd=str(REPO_ROOT),
        text=True,
        capture_output=True,
        timeout=3600,
    )
    try:
        parsed = json.loads(proc.stdout)
    except Exception as exc:
        failures.append(f"primary compact did not emit JSON: {exc}")
        return {"ok": False, "returncode": proc.returncode, "stdout_tail": (proc.stdout or "")[-1800:], "stderr_tail": (proc.stderr or "")[-1800:]}
    ok = proc.returncode == 0 and parsed.get("ok") is True and parsed.get("failed_guard_count") == 0 and parsed.get("top_failure_count") == 0
    if not ok:
        failures.append("primary compact must be ok with no failed guards")
    return {
        "ok": ok,
        "returncode": proc.returncode,
        "failed_guard_count": parsed.get("failed_guard_count"),
        "top_failure_count": parsed.get("top_failure_count"),
        "json_path": parsed.get("json_path"),
        "log_path": parsed.get("log_path"),
        "failed_guards": parsed.get("failed_guards"),
    }


def _check_spec(failures: list[str]) -> dict[str, Any]:
    required = [
        "Health / WarRoom evidence branch end-to-end close",
        "upstream payload producer",
        "pure lowering helpers",
        "operator-ui lowering bridge",
        "Health / WarRoom page-local wiring",
        "render_evidence_presentation_panel",
        "runtime state writer",
        "route wiring",
        "market_engine integration",
        "collector writer/backfill behavior changes",
        "broker/order/execution",
        "inference/training",
        "raw D/E scanner",
        SELF_PATH,
    ]
    text = _read(SPEC_PATH)
    missing = [fragment for fragment in required if fragment not in text]
    for fragment in missing:
        failures.append(f"missing spec fragment: {fragment}")
    return {"missing_count": len(missing), "missing": missing}


def _check_pages_and_bridge(failures: list[str]) -> dict[str, Any]:
    health = _read(HEALTH_PAGE_PATH)
    warroom = _read(WARROOM_PAGE_PATH)
    bridge = _read(BRIDGE_PATH)
    required = {
        HEALTH_PAGE_PATH: [
            "lower_health_snapshot_evidence_presentation_for_ui(snapshot, payload)",
            "Return bridge-normalized evidence presentation payload from the Health snapshot only.",
            "render_evidence_presentation_panel(evidence_payload",
        ],
        WARROOM_PAGE_PATH: [
            "lower_warroom_session_state_evidence_presentation_for_ui(st.session_state, payload)",
            "Return bridge-normalized evidence presentation payload from session_state only.",
            "render_evidence_presentation_panel(evidence_payload",
        ],
        BRIDGE_PATH: [
            "def lower_health_snapshot_evidence_presentation_for_ui",
            "def lower_warroom_session_state_evidence_presentation_for_ui",
            "not_runtime_wiring",
            "not_market_engine_input",
            "not_collector_writer",
            "not_broker_or_order_automation",
            "not_inference_or_training",
        ],
    }
    missing: list[dict[str, str]] = []
    for rel_path, fragments in required.items():
        text = {HEALTH_PAGE_PATH: health, WARROOM_PAGE_PATH: warroom, BRIDGE_PATH: bridge}[rel_path]
        for fragment in fragments:
            if fragment not in text:
                failures.append(f"missing page/bridge fragment: {rel_path}: {fragment}")
                missing.append({"path": rel_path, "fragment": fragment})
    forbidden = [
        "build_real_data_validation_evidence_summary(",
        "D:" + "\\",
        "E:" + "\\",
        "market_engine_signal",
        "collector_write_path",
        "place" + "_" + "order(",
        "broker" + "_" + "order(",
        "training_dataset",
        "inference_job",
    ]
    page_hits = []
    for rel_path, text in [(HEALTH_PAGE_PATH, health), (WARROOM_PAGE_PATH, warroom)]:
        for token in forbidden:
            if token in text:
                failures.append(f"page contains forbidden close-boundary token: {rel_path}: {token}")
                page_hits.append({"path": rel_path, "token": token})
    return {"missing": missing, "forbidden_page_hits": page_hits}


def _scan_runtime_references(failures: list[str]) -> dict[str, Any]:
    hits: list[str] = []
    patterns = [*BRIDGE_HELPERS, "evidence_presentation_lowering_bridge"]
    for rel_root in FORBIDDEN_RUNTIME_ROOTS:
        root = REPO_ROOT / rel_root
        if not root.exists():
            continue
        for path in root.rglob("*.py"):
            try:
                text = path.read_text(encoding="utf-8")
            except Exception:
                continue
            if any(pattern in text for pattern in patterns):
                rel = path.relative_to(REPO_ROOT).as_posix()
                hits.append(rel)
                failures.append(f"runtime path references closed evidence branch bridge: {rel}")
    return {"hit_count": len(hits), "hits": hits}


def _check_gpt_room_checkpoint(failures: list[str]) -> dict[str, Any]:
    focus = _read(FOCUS_PATH)
    state = _read(STATE_PATH)
    required_fragments = [
        "91d14cfd",
        "Health / WarRoom evidence payload lowering page-local wiring",
        "working_tree",
        "clean",
        "route wiring",
        "runtime state writer",
        "market_engine integration",
        "collector writer/backfill",
        "broker/order/execution",
        "inference/training",
        "raw D/E scanner",
        "preserve_primary_guard_compatibility_fragments",
    ]
    missing: list[str] = []
    for fragment in required_fragments:
        if fragment not in focus and fragment not in state:
            failures.append(f"gpt_room checkpoint missing fragment: {fragment}")
            missing.append(fragment)
    return {"missing": missing}


def main() -> int:
    failures: list[str] = []
    checks = {
        "compile_self": _compile(SELF_PATH, failures),
        "page_local_guard": _run_json_guard(PAGE_LOCAL_GUARD_PATH, failures),
        "bridge_guard": _run_json_guard(BRIDGE_GUARD_PATH, failures),
        "lowering_guard": _run_json_guard(LOWERING_GUARD_PATH, failures),
        "upstream_guard": _run_json_guard(UPSTREAM_GUARD_PATH, failures),
        "spec": _check_spec(failures),
        "pages_and_bridge": _check_pages_and_bridge(failures),
        "runtime_references": _scan_runtime_references(failures),
        "gpt_room_checkpoint": _check_gpt_room_checkpoint(failures),
        "primary_compact": _run_primary_compact(failures),
    }
    payload = {
        "ok": not failures,
        "phase": "phase4a_health_warroom_evidence_branch_end_to_end_close_guard",
        "failures": failures,
        "checks": checks,
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
