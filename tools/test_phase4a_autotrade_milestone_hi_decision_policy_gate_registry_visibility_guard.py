# path: ./tools/test_phase4a_autotrade_milestone_hi_decision_policy_gate_registry_visibility_guard.py
# desc: Guard S146 decision policy gate dashboard registry visibility remains read-only/visibility-only with no rendering, commands, runtime wiring, decision append, mode apply, grants, writes, or broker behavior.

from __future__ import annotations

import ast
import json
import subprocess
from pathlib import Path

from _btcts_bootstrap import ensure_btcts_on_syspath
ensure_btcts_on_syspath()

from btcts.apps.operator_ui.hub.decision_policy_gate_visibility import (
    DECISION_POLICY_GATE_DISPLAY_SOURCE_KEY,
    DECISION_POLICY_GATE_REGISTRY_VISIBILITY_CONTRACT,
    build_decision_policy_gate_dashboard_registry_visibility_packet,
    visible_pages_for_decision_policy_gate,
)
from btcts.apps.operator_ui.hub.display_source_registry import load_dashboard_hub_display_source_registry

REPO_ROOT = Path(__file__).resolve().parents[1]
MODULE = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/hub/decision_policy_gate_visibility.py"
REGISTRY = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/hub/display_source_registry.py"
CATALOG = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/components/ai_operator_display_sources.py"
FORBIDDEN_IMPORT_PREFIXES = (
    "streamlit",
    "btcts.autotrade.live_shadow",
    "btcts.autotrade.ledger",
    "btcts.autotrade.execution",
    "btcts.autotrade.runtime_paths",
    "btcts.collector_vnext",
    "requests",
    "httpx",
    "ccxt",
    "pybitflyer",
    "websocket",
)
FORBIDDEN_TOKENS = (
    "st.button",
    "st.checkbox",
    "append_decision_jsonl",
    "run_shadow_decision_from_snapshot",
    "run_latest_market_state_shadow_decision",
    "build_action_candidate",
    "build_shadow_decision_record",
    "decision_ledger_path",
    "default_shadow_decision_ledger_path",
    "persist=True",
    "persist: bool = True",
    "validate_and_append_command",
    "submit_mode_change_command_request",
    "mkdir(",
    "write_text(",
    ".write(",
    "open(",
    "append_jsonl(",
    "json.dump",
    "place_order(",
    "send_order(",
    "create_order(",
    "requests.get",
    "requests.post",
    "httpx.get",
    "httpx.post",
    "decision_append_allowed=True",
    "decision_ledger_integration_allowed=True",
    "live_shadow_behavior_change_allowed=True",
    "persist_true_allowed=True",
    "would_append_shadow_decision=True",
    "would_apply_mode=True",
    "would_execute_prearmed_grant=True",
    "would_write_runtime_artifact=True",
    "would_write_preview_status_artifact=True",
    "would_send_to_broker=True",
)
EXPECTED_FALSE_FLAGS = (
    "decision_append_allowed",
    "decision_ledger_integration_allowed",
    "live_shadow_behavior_change_allowed",
    "persist_true_allowed",
    "would_append_shadow_decision",
    "would_apply_mode",
    "would_execute_prearmed_grant",
    "would_write_runtime_artifact",
    "would_write_preview_status_artifact",
    "would_send_to_broker",
    "broker_execution_requested",
    "mode_apply_requested",
    "command_ledger_append_requested",
    "approval_append_requested",
)


def _imports_from(path: Path) -> set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    out: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            out.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            out.add(node.module)
    return out


def _all_false(payload: dict[str, object]) -> bool:
    return all(payload.get(name) is False for name in EXPECTED_FALSE_FLAGS)


def main() -> int:
    failures: list[str] = []
    for target in (MODULE, REGISTRY, CATALOG):
        text = target.read_text(encoding="utf-8") if target.exists() else ""
        try:
            compile(text, str(target), "exec")
        except Exception as exc:
            failures.append(f"compile failed: {target.relative_to(REPO_ROOT)}: {exc}")
        imports = _imports_from(target)
        for prefix in FORBIDDEN_IMPORT_PREFIXES:
            if any(item == prefix or item.startswith(prefix + ".") for item in imports):
                failures.append(f"forbidden import in {target.relative_to(REPO_ROOT)}: {prefix}")
    text = MODULE.read_text(encoding="utf-8") if MODULE.exists() else ""
    for token in FORBIDDEN_TOKENS:
        if token in text:
            failures.append(f"forbidden token in visibility module: {token}")

    registry = load_dashboard_hub_display_source_registry()
    packet = build_decision_policy_gate_dashboard_registry_visibility_packet(registry)
    visible_pages = visible_pages_for_decision_policy_gate(registry)
    encoded = json.loads(json.dumps(packet, ensure_ascii=False, sort_keys=True))
    source_entry = packet.get("source_entry") or {}
    checks = {
        "contract_shape": DECISION_POLICY_GATE_REGISTRY_VISIBILITY_CONTRACT["visibility_packet_type"] == "decision_policy_gate_dashboard_registry_visibility" and DECISION_POLICY_GATE_REGISTRY_VISIBILITY_CONTRACT["not_ui_rendering"] is True,
        "source_key_constant": DECISION_POLICY_GATE_DISPLAY_SOURCE_KEY == "autotrade_decision_ledger_policy_gate_display",
        "source_entry_available": packet["source_entry_available"] is True and source_entry.get("source_type") == "autotrade_decision_ledger_policy_gate_display_packet",
        "source_entry_read_only": source_entry.get("read_only_contract") is True and source_entry.get("not_runtime_wiring") is True and source_entry.get("not_ui_rendering") is True,
        "health_page_visible": packet["health_page_visible"] is True and "health" in packet["visible_pages"],
        "future_widget_page_visible": packet["future_widget_page_visible"] is True and "logs" in packet["visible_pages"],
        "visible_pages_helper_matches_packet": visible_pages == packet["visible_pages"],
        "page_visibility_has_no_buttons": all(item.get("no_command_buttons") is True for item in packet["page_visibility"]),
        "json_safe": encoded["source_key"] == DECISION_POLICY_GATE_DISPLAY_SOURCE_KEY and encoded["health_page_visible"] is True,
        "visibility_flags_false": _all_false(packet),
    }
    failures.extend(f"check failed: {name}" for name, ok in checks.items() if not ok)

    proc = subprocess.run(["git", "status", "--short"], cwd=REPO_ROOT, text=True, capture_output=True, check=True)
    dirty_lines = [line for line in proc.stdout.splitlines() if line.strip()]
    allowed_dirty_markers = (
        "btcts_next/src/btcts/apps/operator_ui/hub/decision_policy_gate_visibility.py",
        "tools/test_phase4a_autotrade_milestone_hi_decision_policy_gate_registry_visibility_guard.py",
        "tools/test_phase4a_autotrade_milestone_hi_decision_policy_gate_registry_visibility_close_guard.py",
    )
    unexpected_dirty = [line for line in dirty_lines if not any(marker in line for marker in allowed_dirty_markers)]
    failures.extend(f"unexpected dirty file during HI: {line}" for line in unexpected_dirty)

    payload = {
        "ok": not failures,
        "phase": "phase4a_autotrade_milestone_hi_decision_policy_gate_registry_visibility_guard",
        "status": "closed" if not failures else "open",
        "contract": checks | {"only_expected_files_dirty": not unexpected_dirty},
        "sample": {
            "visible_pages": packet["visible_pages"],
            "source_entry": source_entry,
            "display_source_keys_for_page": packet["display_source_keys_for_page"],
        },
        "dirty_lines": dirty_lines,
        "unexpected_dirty": unexpected_dirty,
        "failures": failures,
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if not failures else 1


def test_decision_policy_gate_registry_visibility_guard_closes() -> None:
    assert main() == 0


if __name__ == "__main__":
    raise SystemExit(main())
