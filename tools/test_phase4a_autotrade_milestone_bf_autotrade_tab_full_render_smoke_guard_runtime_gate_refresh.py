# path: ./tools/test_phase4a_autotrade_milestone_bf_autotrade_tab_full_render_smoke_guard_runtime_gate_refresh.py
# desc: Full AutoTrade tab render smoke after Mode Runtime Gate panel. Fake Streamlit; no command/mode append; no runner/broker.

from __future__ import annotations

import ast
import importlib
import json
import os
import subprocess
import sys
import types
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = REPO_ROOT / "btcts_next/src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from btcts.autotrade.execution import read_command_ledger, read_mode_state_records  # noqa: E402
from btcts.autotrade.runtime_paths import ENV_AUTOTRADE_RUNTIME_ROOT  # noqa: E402

UI_FILE = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/views/autotrade_page.py"
PROTECTED_PREFIXES = (
    "btcts_next/src/btcts/collector_vnext/",
    "btcts_next/src/btcts/ingestion/",
    "btcts_next/src/btcts/processing/l3_market_semantics/",
    "btcts_next/src/btcts/processing/l4_consumer_models/",
)
READ_ONLY_STATUS_FUNCTIONS = (
    "_render_mode_state_status",
    "_render_mode_runtime_gate_status",
    "_render_mode_change_apply_preview_status",
    "_render_command_request_status",
    "_render_runtime_health_status",
    "_render_observer_run_status",
    "_render_shadow_decision_status",
    "_render_forecast_calibration_status",
)
STATUS_FORBIDDEN_TOKENS = (
    "apply_latest_mode_change_command_once",
    "append_mode_state_record",
    "submit_mode_change_command_request",
    "validate_and_append_command",
    "append_command_ledger_record",
    "st.button(",
    "run_observer_cycle_bounded",
    "run_observer_cycle_once",
    "run_shadow_cycle_once",
    "run_shadow_cycle_bounded",
    "resolve_due_shadow_forecast_outcomes",
    "run_latest_market_state_shadow_decision",
    "place_order(",
    "send_order(",
    "broker_order(",
    "private_api",
    "pybitflyer",
    "ccxt",
    "requests.post",
    "httpx.post",
)
REQUIRED_RENDER_CALLS = (
    "_render_top_critical_state()",
    "_render_mode_state_status()",
    "_render_mode_runtime_gate_status()",
    "_render_mode_change_apply_preview_status()",
    "_render_command_request_status()",
    "_render_runtime_health_status()",
    "_render_live_readiness_preflight()",
    "_render_operation_visibility()",
    "_render_observer_run_status()",
    "_render_shadow_decision_status()",
    "_render_forecast_calibration_status()",
    "_render_parameter_settings()",
)
MODE_STATE_REJECTION_FIELDS = (
    "latest_ledger_event",
    "latest_reason_codes",
    "latest_blocked_by",
    "latest_would_send_to_broker",
)
MODE_RUNTIME_GATE_FIELDS = (
    "current_mode",
    "source_command_id",
    "changed_at",
    "allow_observer_cycle",
    "allow_shadow_decision_append",
    "allow_forecast_outcome_resolution",
    "allow_paper_order",
    "allow_armed_dry_run",
    "allow_live_order_capability",
    "live_requires_readiness_risk_execution_safety",
    "blocked_by",
    "warnings",
)
RECHECK_PREVIEW_FIELDS = (
    "would_reject_by_readiness",
    "readiness_ready",
    "health_state",
    "readiness",
)


class FakeColumn:
    def __init__(self, owner: "FakeStreamlit | None" = None) -> None:
        self.owner = owner

    def __enter__(self) -> "FakeColumn":
        return self

    def __exit__(self, exc_type: object, exc: object, tb: object) -> bool:
        return False

    def metric(self, *args: Any, **kwargs: Any) -> None:
        if self.owner is not None:
            self.owner.metric_call_count += 1
        return None

    def checkbox(self, *args: Any, **kwargs: Any) -> bool:
        if self.owner is not None:
            self.owner.checkbox_call_count += 1
        return bool(kwargs.get("value", False))

    def button(self, *args: Any, **kwargs: Any) -> bool:
        if self.owner is not None:
            self.owner.button_call_count += 1
        return False

    def selectbox(self, label: str, options: list[str] | tuple[str, ...], *, index: int = 0, **kwargs: Any) -> str:
        if self.owner is not None:
            self.owner.selectbox_call_count += 1
        if not options:
            return ""
        return str(options[index])

    def markdown(self, *args: Any, **kwargs: Any) -> None:
        return None

    def caption(self, *args: Any, **kwargs: Any) -> None:
        return None

    def subheader(self, text: str, *args: Any, **kwargs: Any) -> None:
        if self.owner is not None:
            self.owner.subheaders.append(str(text))
        return None


class FakeStreamlit(types.ModuleType):
    def __init__(self) -> None:
        super().__init__("streamlit")
        self.__path__ = []
        self.session_state: dict[str, Any] = {}
        self.button_call_count = 0
        self.checkbox_call_count = 0
        self.selectbox_call_count = 0
        self.metric_call_count = 0
        self.divider_call_count = 0
        self.subheaders: list[str] = []

    def title(self, *args: Any, **kwargs: Any) -> None:
        return None

    def caption(self, *args: Any, **kwargs: Any) -> None:
        return None

    def subheader(self, text: str, *args: Any, **kwargs: Any) -> None:
        self.subheaders.append(str(text))
        return None

    def markdown(self, *args: Any, **kwargs: Any) -> None:
        return None

    def divider(self, *args: Any, **kwargs: Any) -> None:
        self.divider_call_count += 1
        return None

    def columns(self, count: int) -> list[FakeColumn]:
        return [FakeColumn(self) for _ in range(int(count))]

    def checkbox(self, *args: Any, **kwargs: Any) -> bool:
        self.checkbox_call_count += 1
        return bool(kwargs.get("value", False))

    def button(self, *args: Any, **kwargs: Any) -> bool:
        self.button_call_count += 1
        return False

    def selectbox(self, label: str, options: list[str] | tuple[str, ...], *, index: int = 0, **kwargs: Any) -> str:
        self.selectbox_call_count += 1
        if not options:
            return ""
        return str(options[index])


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(json.dumps(row, ensure_ascii=False, sort_keys=True) for row in rows) + "\n", encoding="utf-8")


def command_row(command_id: str, *, command_type: str, accepted: bool, current_mode: str, target: str | None, blocked_by: list[str]) -> dict[str, Any]:
    return {
        "ledger_event": "autotrade.mode_change_command_request_validated" if command_type == "REQUEST_MODE_CHANGE" else "autotrade.command_request_validated",
        "command_id": command_id,
        "accepted": accepted,
        "blocked_by": blocked_by,
        "command": {
            "command_id": command_id,
            "command_type": command_type,
            "requested_by": "guard",
            "requested_at": "2026-06-13T07:20:00Z",
            "current_mode": current_mode,
            "target": target,
            "confirmation": True,
            "reason_codes": ["guard", "full_render_runtime_gate_refresh"],
            "note": "{}",
            "confirmation_required": True,
        },
    }


def mode_state_rejection_row() -> dict[str, Any]:
    return {
        "current_mode": "OFF",
        "previous_mode": "OFF",
        "changed_at": "2026-06-13T07:19:00Z",
        "source_command_id": "cmd_render_mode_state_rejected_live_bf",
        "requested_by": "guard",
        "accepted": False,
        "mode_changed": False,
        "reason_codes": ["guard", "readiness_recheck"],
        "blocked_by": ["readiness_recheck_not_ready", "observer_run_stale"],
        "ledger_event": "autotrade.mode_state_readiness_recheck_rejected",
        "would_send_to_broker": False,
    }


def observer_row(finished_at: str) -> dict[str, Any]:
    return {
        "run_id": "obs_full_render_runtime_gate_refresh",
        "started_at": finished_at,
        "finished_at": finished_at,
        "requested_cycles": 2,
        "completed_cycles": 2,
        "appended_shadow_decision_count": 0,
        "appended_forecast_outcome_count": 0,
        "duplicate_snapshot_skipped_count": 0,
        "skip_duplicate_snapshot": True,
        "blocked_by": ["mode_off", "mode_runtime_gate_blocked_shadow_decision_append"],
        "would_send_to_broker": False,
        "bounded": True,
        "source": "autotrade.observer_cycle_bounded",
    }


def shadow_row() -> dict[str, Any]:
    return {
        "decision_id": "dec_full_render_runtime_gate_refresh",
        "mode": "SHADOW",
        "snapshot_id": "snap_full_render_runtime_gate_refresh",
        "forecast_id": "fcst_full_render_runtime_gate_refresh",
        "parameter_set_id": "params_fx_balanced_v0_1",
        "logic_version": "autotrade_logic_v0_1",
        "forecast_5m": {"forecast_id": "fcst_full_render_runtime_gate_refresh", "forecast_direction": "down", "confidence": "medium"},
        "candidate": {"action": "NO_NEW_ENTRY"},
        "risk_gate": {"allowed": False, "executable": False},
        "final_action": "WAIT",
        "reason_codes": ["full_render_runtime_gate_refresh_guard"],
        "blocked_by": [],
        "would_order": None,
    }


def outcome_row() -> dict[str, Any]:
    return {
        "forecast_id": "fcst_full_render_runtime_gate_refresh",
        "parameter_set_id": "params_fx_balanced_v0_1",
        "logic_version": "autotrade_logic_v0_1",
        "source_snapshot_id": "snap_full_render_runtime_gate_refresh",
        "target_ts": "2026-06-13T02:00:00Z",
        "actual_snapshot_id": "actual_full_render_runtime_gate_refresh",
        "forecast_direction": "down",
        "forecast_confidence": "medium",
        "expected_change": "strengthen_sell",
        "drivers": ["sell_pressure_or_ground"],
        "blocked_by": [],
        "result": "hit",
        "direction_hit": True,
        "change_type_hit": True,
        "divergence_reasons": [],
    }


def function_source(path: Path, function_name: str) -> str:
    text = path.read_text(encoding="utf-8")
    tree = ast.parse(text)
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == function_name:
            return ast.get_source_segment(text, node) or ""
    return ""


def main() -> int:
    failures: list[str] = []
    original_runtime = os.environ.get(ENV_AUTOTRADE_RUNTIME_ROOT)
    fake_st = FakeStreamlit()
    previous_streamlit = sys.modules.get("streamlit")
    previous_components = sys.modules.get("streamlit.components")
    previous_components_v1 = sys.modules.get("streamlit.components.v1")
    hot_root = REPO_ROOT / "tmp/btc_ts_autotrade_ui_full_smoke_runtime_gate_refresh_hot"
    command_path = hot_root / "autotrade/commands/command_requests.jsonl"
    mode_state_path = hot_root / "autotrade/decisions/mode_state.jsonl"
    now = datetime.now(timezone.utc).replace(microsecond=0)
    fresh_ts = (now - timedelta(seconds=10)).isoformat().replace("+00:00", "Z")
    render_exception = None
    import_exception = None
    before_command_count = -1
    after_command_count = -2
    before_mode_count = -1
    after_mode_count = -2
    try:
        os.environ[ENV_AUTOTRADE_RUNTIME_ROOT] = str(hot_root)
        write_jsonl(
            command_path,
            [
                command_row("cmd_full_render_halt_bf", command_type="REQUEST_HALT_NEW", accepted=True, current_mode="OFF", target="halt_new", blocked_by=[]),
                command_row("cmd_full_render_live_bf", command_type="REQUEST_MODE_CHANGE", accepted=True, current_mode="OFF", target="PAPER_OR_REPLAY", blocked_by=[]),
            ],
        )
        write_jsonl(mode_state_path, [mode_state_rejection_row()])
        write_jsonl(hot_root / "autotrade/decisions/observer_runs.jsonl", [observer_row(fresh_ts)])
        write_jsonl(hot_root / "autotrade/decisions/shadow_decisions.jsonl", [shadow_row()])
        write_jsonl(hot_root / "autotrade/decisions/forecast_outcomes.jsonl", [outcome_row()])
        before_command_count = len(read_command_ledger(command_path))
        before_mode_count = len(read_mode_state_records(mode_state_path).rows)
        fake_components = types.ModuleType("streamlit.components")
        fake_components.__path__ = []
        fake_components_v1 = types.ModuleType("streamlit.components.v1")
        fake_components_v1.html = lambda *args, **kwargs: None
        fake_components.v1 = fake_components_v1
        fake_st.components = fake_components
        sys.modules["streamlit"] = fake_st
        sys.modules["streamlit.components"] = fake_components
        sys.modules["streamlit.components.v1"] = fake_components_v1
        try:
            module = importlib.import_module("btcts.apps.operator_ui.views.autotrade_page")
            module = importlib.reload(module)
        except Exception as exc:
            import_exception = repr(exc)
            module = None
        if module is not None:
            try:
                module.render()
            except Exception as exc:
                render_exception = repr(exc)
        after_command_count = len(read_command_ledger(command_path))
        after_mode_count = len(read_mode_state_records(mode_state_path).rows)
    finally:
        if previous_components_v1 is None:
            sys.modules.pop("streamlit.components.v1", None)
        else:
            sys.modules["streamlit.components.v1"] = previous_components_v1
        if previous_components is None:
            sys.modules.pop("streamlit.components", None)
        else:
            sys.modules["streamlit.components"] = previous_components
        if previous_streamlit is None:
            sys.modules.pop("streamlit", None)
        else:
            sys.modules["streamlit"] = previous_streamlit
        if original_runtime is None:
            os.environ.pop(ENV_AUTOTRADE_RUNTIME_ROOT, None)
        else:
            os.environ[ENV_AUTOTRADE_RUNTIME_ROOT] = original_runtime

    render_source = function_source(UI_FILE, "render")
    status_sources = {name: function_source(UI_FILE, name) for name in READ_ONLY_STATUS_FUNCTIONS}
    mode_state_source = status_sources.get("_render_mode_state_status", "")
    runtime_gate_source = status_sources.get("_render_mode_runtime_gate_status", "")
    apply_preview_source = status_sources.get("_render_mode_change_apply_preview_status", "")
    status_sources_present = all(bool(source) for source in status_sources.values())
    status_read_only = status_sources_present and all(
        not any(token in source for token in STATUS_FORBIDDEN_TOKENS) for source in status_sources.values()
    )
    render_calls_present = all(call in render_source for call in REQUIRED_RENDER_CALLS)
    runtime_gate_after_mode_state = "_render_mode_state_status()" in render_source and "_render_mode_runtime_gate_status()" in render_source and render_source.index("_render_mode_state_status()") < render_source.index("_render_mode_runtime_gate_status()")
    checks = {
        "autotrade_page_imports": import_exception is None,
        "autotrade_page_render_smoke": import_exception is None and render_exception is None,
        "render_calls_all_panels": render_calls_present,
        "runtime_gate_panel_rendered": "Mode Runtime Gate" in fake_st.subheaders,
        "runtime_gate_after_mode_state": runtime_gate_after_mode_state,
        "fake_streamlit_exercised": fake_st.button_call_count >= 4 and fake_st.checkbox_call_count >= 4 and fake_st.selectbox_call_count >= 2 and fake_st.metric_call_count >= 55,
        "render_did_not_append_commands": before_command_count == 2 and after_command_count == before_command_count,
        "render_did_not_append_mode_state": before_mode_count == 1 and after_mode_count == before_mode_count,
        "read_only_status_functions_checked": status_read_only,
        "mode_state_latest_rejection_fields_checked": all(token in mode_state_source for token in MODE_STATE_REJECTION_FIELDS),
        "mode_runtime_gate_fields_checked": all(token in runtime_gate_source for token in MODE_RUNTIME_GATE_FIELDS),
        "rechecked_apply_preview_fields_checked": all(token in apply_preview_source for token in RECHECK_PREVIEW_FIELDS),
    }
    failures.extend(f"check failed: {name}" for name, ok in checks.items() if not ok)
    if import_exception:
        failures.append(f"import_exception: {import_exception}")
    if render_exception:
        failures.append(f"render_exception: {render_exception}")

    protected_dirty_hits: list[str] = []
    status = subprocess.run(["git", "status", "--short"], cwd=REPO_ROOT, text=True, capture_output=True, check=True).stdout.splitlines()
    for line in status:
        rel = line[3:] if len(line) > 3 else line
        if any(rel.startswith(prefix) for prefix in PROTECTED_PREFIXES):
            protected_dirty_hits.append(line)
    failures.extend(f"protected lower-layer dirty during milestone BF: {hit}" for hit in protected_dirty_hits)

    payload = {
        "ok": not failures,
        "phase": "phase4a_autotrade_milestone_bf_autotrade_tab_full_render_smoke_guard_runtime_gate_refresh",
        "status": "closed" if not failures else "open",
        "contract": {
            "autotrade_page_imports": checks["autotrade_page_imports"],
            "autotrade_page_render_smoke": checks["autotrade_page_render_smoke"],
            "all_panels_rendered": checks["render_calls_all_panels"],
            "runtime_gate_panel_rendered": checks["runtime_gate_panel_rendered"],
            "render_did_not_append_commands": checks["render_did_not_append_commands"],
            "render_did_not_append_mode_state": checks["render_did_not_append_mode_state"],
            "mode_state_latest_rejection_fields_checked": checks["mode_state_latest_rejection_fields_checked"],
            "mode_runtime_gate_fields_checked": checks["mode_runtime_gate_fields_checked"],
            "rechecked_apply_preview_fields_checked": checks["rechecked_apply_preview_fields_checked"],
            "read_only_status_functions_checked": checks["read_only_status_functions_checked"],
            "protected_lower_layers_untouched": not protected_dirty_hits,
        },
        "subheaders": fake_st.subheaders,
        "button_call_count": fake_st.button_call_count,
        "checkbox_call_count": fake_st.checkbox_call_count,
        "selectbox_call_count": fake_st.selectbox_call_count,
        "metric_call_count": fake_st.metric_call_count,
        "command_count_before": before_command_count,
        "command_count_after": after_command_count,
        "mode_state_count_before": before_mode_count,
        "mode_state_count_after": after_mode_count,
        "import_exception": import_exception,
        "render_exception": render_exception,
        "checks": checks,
        "protected_dirty_hits": protected_dirty_hits,
        "failures": failures,
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2, default=str))
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
