# path: ./tools/test_phase4a_autotrade_milestone_cp_full_render_after_rechecked_apply_rejection_guard.py
# desc: Full AutoTrade render after rechecked apply rejection. Mode State rejection remains visible; render read-only, no command/mode/observer append, runner, or broker.

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

from btcts.autotrade.execution import apply_latest_mode_change_command_once_with_readiness_recheck, default_command_ledger_path, default_mode_state_ledger_path, preview_latest_mode_change_command_apply_with_readiness_recheck, read_command_ledger, read_mode_state_records, summarize_mode_state  # noqa: E402
from btcts.autotrade.runtime_paths import ENV_AUTOTRADE_RUNTIME_ROOT  # noqa: E402

UI_FILE = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/views/autotrade_page.py"
APPLIER_FILE = REPO_ROOT / "btcts_next/src/btcts/autotrade/execution/mode_command_applier.py"
PROTECTED_PREFIXES = (
    "btcts_next/src/btcts/collector_vnext/",
    "btcts_next/src/btcts/ingestion/",
    "btcts_next/src/btcts/processing/l3_market_semantics/",
    "btcts_next/src/btcts/processing/l4_consumer_models/",
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
    "append_observer_run_record",
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
LIVE_READINESS_FORBIDDEN_TOKENS = (
    "apply_latest_mode_change_command_once",
    "append_mode_state_record",
    "append_observer_run_record",
    "append_command_ledger_record",
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
APPLY_FORBIDDEN_TOKENS = (
    "append_observer_run_record",
    "validate_and_append_command",
    "append_command_ledger_record",
    "submit_mode_change_command_request",
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
MODE_STATE_REJECTION_FIELDS = (
    "latest_source_command_id",
    "latest_requested_by",
    "latest_accepted",
    "latest_mode_changed",
    "latest_ledger_event",
    "latest_reason_codes",
    "latest_blocked_by",
    "latest_would_send_to_broker",
)
MODE_CHANGE_PREVIEW_CANDIDATE_METADATA_FIELDS = (
    "candidate_command_type",
    "candidate_requested_by",
    "candidate_requested_at",
    "candidate_current_mode",
    "candidate_target_mode",
    "candidate_accepted",
    "candidate_blocked_by",
)
MODE_CHANGE_PREVIEW_CANDIDATE_READINESS_FIELDS = (
    "candidate_readiness_note_present",
    "candidate_readiness_ready",
    "candidate_readiness_current_mode",
    "candidate_readiness_target_mode",
    "candidate_readiness_blocked_by",
    "candidate_readiness_warnings",
    "candidate_readiness_health_state",
    "candidate_readiness_observer_latest_run_id",
    "candidate_readiness_observer_latest_blocked_by",
    "candidate_readiness_observer_latest_would_send_to_broker",
    "candidate_readiness_observer_latest_bounded",
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


def now_z(offset_seconds: int = 0) -> str:
    return (datetime.now(timezone.utc).replace(microsecond=0) + timedelta(seconds=offset_seconds)).isoformat().replace("+00:00", "Z")


def function_source(path: Path, function_name: str) -> str:
    text = path.read_text(encoding="utf-8")
    tree = ast.parse(text)
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == function_name:
            return ast.get_source_segment(text, node) or ""
    return ""


def readiness_note() -> str:
    return json.dumps(
        {
            "kind": "autotrade.mode_change_readiness_snapshot",
            "ready": False,
            "current_mode": "ARMED_DRY_RUN",
            "target_mode": "LIVE_MIN_SIZE",
            "blocked_by": ["observer_run_latest_blocked_for_live_target", "mode_off"],
            "warnings": ["full_render_after_rechecked_apply_rejection_guard"],
            "health_state": "warn",
            "observer_latest_run_id": "obs_cp_candidate_note",
            "observer_latest_blocked_by": ["mode_off"],
            "observer_latest_would_send_to_broker": False,
            "observer_latest_bounded": True,
            "would_send_to_broker": False,
        },
        ensure_ascii=False,
        sort_keys=True,
    )


def command_row(command_id: str) -> dict[str, Any]:
    return {
        "ledger_event": "autotrade.mode_change_command_request_validated",
        "command_id": command_id,
        "accepted": True,
        "blocked_by": ["cp_candidate_command_blocker"],
        "command": {
            "command_id": command_id,
            "command_type": "REQUEST_MODE_CHANGE",
            "requested_by": "operator_ui",
            "requested_at": now_z(-10),
            "current_mode": "ARMED_DRY_RUN",
            "target": "LIVE_MIN_SIZE",
            "confirmation": True,
            "reason_codes": ["guard", "full_render_after_rechecked_apply_rejection"],
            "note": readiness_note(),
            "confirmation_required": True,
        },
    }


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(json.dumps(row, ensure_ascii=False, sort_keys=True) for row in rows) + "\n", encoding="utf-8")


def shadow_row() -> dict[str, Any]:
    return {
        "decision_id": "dec_cp_full_render_after_apply_rejection",
        "mode": "SHADOW",
        "snapshot_id": "snap_cp_full_render_after_apply_rejection",
        "forecast_id": "fcst_cp_full_render_after_apply_rejection",
        "parameter_set_id": "params_fx_balanced_v0_1",
        "logic_version": "autotrade_logic_v0_1",
        "forecast_5m": {"forecast_id": "fcst_cp_full_render_after_apply_rejection", "forecast_direction": "down", "confidence": "medium"},
        "candidate": {"action": "NO_NEW_ENTRY"},
        "risk_gate": {"allowed": False, "executable": False},
        "final_action": "WAIT",
        "reason_codes": ["cp_full_render_after_apply_rejection_guard"],
        "blocked_by": [],
        "would_order": None,
    }


def outcome_row() -> dict[str, Any]:
    return {
        "forecast_id": "fcst_cp_full_render_after_apply_rejection",
        "parameter_set_id": "params_fx_balanced_v0_1",
        "logic_version": "autotrade_logic_v0_1",
        "source_snapshot_id": "snap_cp_full_render_after_apply_rejection",
        "target_ts": "2026-06-13T02:00:00Z",
        "actual_snapshot_id": "actual_cp_full_render_after_apply_rejection",
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


def main() -> int:
    failures: list[str] = []
    original_runtime = os.environ.get(ENV_AUTOTRADE_RUNTIME_ROOT)
    fake_st = FakeStreamlit()
    previous_streamlit = sys.modules.get("streamlit")
    previous_components = sys.modules.get("streamlit.components")
    previous_components_v1 = sys.modules.get("streamlit.components.v1")
    hot_root = REPO_ROOT / "tmp/btc_ts_full_render_after_rechecked_apply_rejection_hot"
    render_exception = None
    import_exception = None
    before_command_count = -1
    after_apply_command_count = -2
    after_render_command_count = -3
    before_mode_count = -1
    after_apply_mode_count = -2
    after_render_mode_count = -3
    before_observer_count = 0
    after_apply_observer_count = 0
    after_render_observer_count = 0
    try:
        os.environ[ENV_AUTOTRADE_RUNTIME_ROOT] = str(hot_root)
        command_path = default_command_ledger_path(ensure=True)
        mode_state_path = default_mode_state_ledger_path(ensure=True)
        observer_path = hot_root / "autotrade/decisions/observer_runs.jsonl"
        shadow_path = hot_root / "autotrade/decisions/shadow_decisions.jsonl"
        outcome_path = hot_root / "autotrade/decisions/forecast_outcomes.jsonl"
        for path in (command_path, mode_state_path, observer_path, shadow_path, outcome_path):
            if path.exists():
                path.unlink()
        write_jsonl(command_path, [command_row("cmd_cp_candidate_live_request")])
        write_jsonl(shadow_path, [shadow_row()])
        write_jsonl(outcome_path, [outcome_row()])
        before_command_count = len(read_command_ledger(command_path))
        before_mode_count = len(read_mode_state_records(mode_state_path).rows)
        before_observer_count = 0 if not observer_path.exists() else len(observer_path.read_text(encoding="utf-8").splitlines())
        apply_result = apply_latest_mode_change_command_once_with_readiness_recheck(max_lines=100, max_observer_run_age_sec=120, allow_warnings=False)
        after_apply_command_count = len(read_command_ledger(command_path))
        after_apply_mode_count = len(read_mode_state_records(mode_state_path).rows)
        after_apply_observer_count = 0 if not observer_path.exists() else len(observer_path.read_text(encoding="utf-8").splitlines())
        summary = summarize_mode_state(mode_state_path, max_lines=100)
        preview_after_apply = preview_latest_mode_change_command_apply_with_readiness_recheck(command_path=command_path, mode_state_path=mode_state_path, max_lines=100, max_observer_run_age_sec=120, allow_warnings=False)
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
        after_render_command_count = len(read_command_ledger(command_path))
        after_render_mode_count = len(read_mode_state_records(mode_state_path).rows)
        after_render_observer_count = 0 if not observer_path.exists() else len(observer_path.read_text(encoding="utf-8").splitlines())
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

    apply_data = apply_result.to_dict()
    summary_data = summary.to_dict()
    preview_data = preview_after_apply.to_dict()
    render_source = function_source(UI_FILE, "render")
    mode_state_source = function_source(UI_FILE, "_render_mode_state_status")
    apply_preview_source = function_source(UI_FILE, "_render_mode_change_apply_preview_status")
    live_readiness_source = function_source(UI_FILE, "_render_live_readiness_preflight")
    status_sources = {name: function_source(UI_FILE, name) for name in READ_ONLY_STATUS_FUNCTIONS}
    apply_source = function_source(APPLIER_FILE, "apply_latest_mode_change_command_once_with_readiness_recheck")
    checks = {
        "apply_rejection_appended_exactly_one_mode_state": before_mode_count == 0 and after_apply_mode_count == 1 and apply_data.get("record_appended") is True and apply_data.get("rejected_by_readiness") is True and (apply_data.get("mode_state_record") or {}).get("source_command_id") == "cmd_cp_candidate_live_request",
        "mode_state_summary_surfaces_rejection_after_apply": summary_data.get("latest_source_command_id") == "cmd_cp_candidate_live_request" and summary_data.get("latest_requested_by") == "operator_ui" and summary_data.get("latest_accepted") is False and summary_data.get("latest_mode_changed") is False and summary_data.get("latest_ledger_event") == "autotrade.mode_state_readiness_recheck_rejected" and "readiness_recheck" in tuple(summary_data.get("latest_reason_codes") or ()) and "readiness_recheck_not_ready" in tuple(summary_data.get("latest_blocked_by") or ()) and "cp_candidate_command_blocker" in tuple(summary_data.get("latest_blocked_by") or ()) and summary_data.get("latest_would_send_to_broker") is False,
        "mode_state_ui_displays_rejection_fields": all(field in mode_state_source for field in MODE_STATE_REJECTION_FIELDS),
        "preview_after_apply_sees_command_already_applied": preview_data.get("would_apply") is False and preview_data.get("would_reject_by_readiness") is False and preview_data.get("skip_reason") == "no_unapplied_accepted_mode_change_command" and preview_data.get("command_id") is None and tuple(preview_data.get("already_applied_command_ids") or ()) == ("cmd_cp_candidate_live_request",) and preview_data.get("candidate_command_count") == 0,
        "apply_preview_ui_keeps_candidate_context_fields": all(field in apply_preview_source for field in MODE_CHANGE_PREVIEW_CANDIDATE_METADATA_FIELDS) and all(field in apply_preview_source for field in MODE_CHANGE_PREVIEW_CANDIDATE_READINESS_FIELDS),
        "autotrade_page_imports": import_exception is None,
        "autotrade_page_full_render_smoke": import_exception is None and render_exception is None,
        "full_render_calls_all_panels": all(call in render_source for call in REQUIRED_RENDER_CALLS),
        "full_render_exercised_expected_ui_controls": fake_st.button_call_count >= 4 and fake_st.checkbox_call_count >= 6 and fake_st.selectbox_call_count >= 2 and fake_st.metric_call_count >= 55,
        "full_render_did_not_append_commands": after_render_command_count == after_apply_command_count == before_command_count,
        "full_render_did_not_append_mode_state": after_render_mode_count == after_apply_mode_count == 1,
        "full_render_did_not_append_observer_runs": after_render_observer_count == after_apply_observer_count == before_observer_count,
        "status_functions_read_only_no_append_runner_broker": all(bool(source) and not any(token in source for token in STATUS_FORBIDDEN_TOKENS) for source in status_sources.values()),
        "live_readiness_no_runner_broker_apply": bool(live_readiness_source) and not any(token in live_readiness_source for token in LIVE_READINESS_FORBIDDEN_TOKENS),
        "apply_no_command_or_observer_append_no_runner_broker": bool(apply_source) and not any(token in apply_source for token in APPLY_FORBIDDEN_TOKENS) and after_apply_command_count == before_command_count and after_apply_observer_count == before_observer_count,
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
    failures.extend(f"protected lower-layer dirty during milestone CP: {hit}" for hit in protected_dirty_hits)

    payload = {
        "ok": not failures,
        "phase": "phase4a_autotrade_milestone_cp_full_render_after_rechecked_apply_rejection_guard",
        "status": "closed" if not failures else "open",
        "contract": {
            "apply_rejection_appended_exactly_one_mode_state": checks["apply_rejection_appended_exactly_one_mode_state"],
            "mode_state_summary_surfaces_rejection_after_apply": checks["mode_state_summary_surfaces_rejection_after_apply"],
            "mode_state_ui_displays_rejection_fields": checks["mode_state_ui_displays_rejection_fields"],
            "preview_after_apply_sees_command_already_applied": checks["preview_after_apply_sees_command_already_applied"],
            "apply_preview_ui_keeps_candidate_context_fields": checks["apply_preview_ui_keeps_candidate_context_fields"],
            "autotrade_page_imports": checks["autotrade_page_imports"],
            "autotrade_page_full_render_smoke": checks["autotrade_page_full_render_smoke"],
            "full_render_calls_all_panels": checks["full_render_calls_all_panels"],
            "full_render_did_not_append_commands": checks["full_render_did_not_append_commands"],
            "full_render_did_not_append_mode_state": checks["full_render_did_not_append_mode_state"],
            "full_render_did_not_append_observer_runs": checks["full_render_did_not_append_observer_runs"],
            "status_functions_read_only_no_append_runner_broker": checks["status_functions_read_only_no_append_runner_broker"],
            "live_readiness_no_runner_broker_apply": checks["live_readiness_no_runner_broker_apply"],
            "apply_no_command_or_observer_append_no_runner_broker": checks["apply_no_command_or_observer_append_no_runner_broker"],
            "protected_lower_layers_untouched": not protected_dirty_hits,
        },
        "apply_result": apply_data,
        "mode_state_summary": summary_data,
        "preview_after_apply": preview_data,
        "subheaders": fake_st.subheaders,
        "button_call_count": fake_st.button_call_count,
        "checkbox_call_count": fake_st.checkbox_call_count,
        "selectbox_call_count": fake_st.selectbox_call_count,
        "metric_call_count": fake_st.metric_call_count,
        "before_command_count": before_command_count,
        "after_apply_command_count": after_apply_command_count,
        "after_render_command_count": after_render_command_count,
        "before_mode_count": before_mode_count,
        "after_apply_mode_count": after_apply_mode_count,
        "after_render_mode_count": after_render_mode_count,
        "before_observer_count": before_observer_count,
        "after_apply_observer_count": after_apply_observer_count,
        "after_render_observer_count": after_render_observer_count,
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
