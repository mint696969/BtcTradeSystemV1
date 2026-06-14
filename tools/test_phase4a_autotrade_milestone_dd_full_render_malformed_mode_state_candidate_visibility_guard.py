# path: ./tools/test_phase4a_autotrade_milestone_dd_full_render_malformed_mode_state_candidate_visibility_guard.py
# desc: Full AutoTrade render with malformed mode_state rows. Mode State panel surfaces skipped/errors; apply preview keeps candidate visibility and render is read-only.

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

from btcts.autotrade.execution import default_command_ledger_path, default_mode_state_ledger_path, preview_latest_mode_change_command_apply_with_readiness_recheck, read_command_ledger_rows, read_mode_state_records, summarize_mode_state  # noqa: E402
from btcts.autotrade.runtime_paths import ENV_AUTOTRADE_RUNTIME_ROOT  # noqa: E402

UI_FILE = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/views/autotrade_page.py"
MODE_STATE_FILE = REPO_ROOT / "btcts_next/src/btcts/autotrade/execution/mode_state.py"
APPLIER_FILE = REPO_ROOT / "btcts_next/src/btcts/autotrade/execution/mode_command_applier.py"
PROTECTED_PREFIXES = (
    "btcts_next/src/btcts/collector_vnext/",
    "btcts_next/src/btcts/ingestion/",
    "btcts_next/src/btcts/processing/l3_market_semantics/",
    "btcts_next/src/btcts/processing/l4_consumer_models/",
)
LATEST = "cmd_dd_latest_live_request"
MIDDLE = "cmd_dd_middle_live_request"
OLDEST = "cmd_dd_oldest_live_request"
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
MODE_STATE_PANEL_FIELDS = (
    "skipped_rows",
    "latest_source_command_id",
    "latest_ledger_event",
    "latest_blocked_by",
    "blocked_by_counts",
    "error_samples",
)
PREVIEW_PANEL_FIELDS = (
    "command_id",
    "candidate_command_count",
    "already_applied_command_ids",
    "command_read_skipped_count",
    "mode_state_read_skipped_count",
    "candidate_command_type",
    "candidate_accepted",
    "candidate_blocked_by",
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
LIVE_READINESS_FORBIDDEN_TOKENS = tuple(token for token in STATUS_FORBIDDEN_TOKENS if token not in {"st.button(", "submit_mode_change_command_request", "validate_and_append_command"})
PREVIEW_FORBIDDEN_TOKENS = (
    "append_mode_state_record(",
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
        return str(options[index]) if options else ""
    def markdown(self, *args: Any, **kwargs: Any) -> None:
        return None
    def caption(self, *args: Any, **kwargs: Any) -> None:
        return None
    def subheader(self, text: str, *args: Any, **kwargs: Any) -> None:
        if self.owner is not None:
            self.owner.subheaders.append(str(text))


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
    def markdown(self, *args: Any, **kwargs: Any) -> None:
        return None
    def divider(self, *args: Any, **kwargs: Any) -> None:
        self.divider_call_count += 1
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
        return str(options[index]) if options else ""


def now_z(offset_seconds: int = 0) -> str:
    return (datetime.now(timezone.utc).replace(microsecond=0) + timedelta(seconds=offset_seconds)).isoformat().replace("+00:00", "Z")


def function_source(path: Path, function_name: str) -> str:
    text = path.read_text(encoding="utf-8")
    tree = ast.parse(text)
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == function_name:
            return ast.get_source_segment(text, node) or ""
    return ""


def readiness_note(command_id: str) -> str:
    return json.dumps(
        {
            "kind": "autotrade.mode_change_readiness_snapshot",
            "ready": False,
            "current_mode": "ARMED_DRY_RUN",
            "target_mode": "LIVE_MIN_SIZE",
            "blocked_by": ["observer_run_latest_blocked_for_live_target", f"{command_id}_persisted_blocker"],
            "warnings": ["full_render_malformed_mode_state_candidate_visibility_snapshot"],
            "health_state": "warn",
            "observer_latest_run_id": f"obs_{command_id}",
            "observer_latest_blocked_by": [f"{command_id}_observer_blocker"],
            "observer_latest_would_send_to_broker": False,
            "observer_latest_bounded": True,
            "would_send_to_broker": False,
        },
        ensure_ascii=False,
        sort_keys=True,
    )


def command_row(command_id: str, requested_at: str, blocker: str) -> dict[str, Any]:
    return {
        "ledger_event": "autotrade.mode_change_command_request_validated",
        "command_id": command_id,
        "accepted": True,
        "blocked_by": [blocker],
        "command": {
            "command_id": command_id,
            "command_type": "REQUEST_MODE_CHANGE",
            "requested_by": "operator_ui",
            "requested_at": requested_at,
            "current_mode": "ARMED_DRY_RUN",
            "target": "LIVE_MIN_SIZE",
            "confirmation": True,
            "reason_codes": ["guard", "full_render_malformed_mode_state_candidate_visibility", command_id],
            "note": readiness_note(command_id),
            "confirmation_required": True,
        },
    }


def mode_state_rejection_row(command_id: str, blocker: str) -> dict[str, Any]:
    return {
        "current_mode": "OFF",
        "previous_mode": "OFF",
        "changed_at": now_z(),
        "source_command_id": command_id,
        "requested_by": "operator_ui",
        "accepted": False,
        "mode_changed": False,
        "reason_codes": ["guard", "full_render_malformed_mode_state_candidate_visibility", command_id, "readiness_recheck"],
        "blocked_by": [
            "readiness_recheck_not_ready",
            "mode_transition_not_allowed_or_unconfirmed",
            "runtime_health_blocked",
            "observer_run_missing",
            "observer_run_not_fresh_for_live_target",
            "runtime_health_warnings_present",
            blocker,
        ],
        "ledger_event": "autotrade.mode_state_readiness_recheck_rejected",
        "would_send_to_broker": False,
    }


def write_command_jsonl(path: Path) -> None:
    rows = [
        command_row(OLDEST, now_z(-30), "dd_oldest_candidate_blocker"),
        command_row(MIDDLE, now_z(-20), "dd_middle_candidate_blocker"),
        command_row(LATEST, now_z(-10), "dd_latest_candidate_blocker"),
    ]
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(json.dumps(row, ensure_ascii=False, sort_keys=True) for row in rows) + "\n", encoding="utf-8")


def write_mode_state_with_malformed(path: Path) -> None:
    rows = [
        mode_state_rejection_row(LATEST, "dd_latest_candidate_blocker"),
        mode_state_rejection_row(MIDDLE, "dd_middle_candidate_blocker"),
    ]
    path.parent.mkdir(parents=True, exist_ok=True)
    text = json.dumps(rows[0], ensure_ascii=False, sort_keys=True) + "\n"
    text += "{not-json\n"
    text += json.dumps(rows[1], ensure_ascii=False, sort_keys=True) + "\n"
    path.write_text(text, encoding="utf-8")


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(json.dumps(row, ensure_ascii=False, sort_keys=True) for row in rows) + ("\n" if rows else ""), encoding="utf-8")


def shadow_row() -> dict[str, Any]:
    return {
        "decision_id": "dec_dd_full_render_malformed_mode_state_candidate_visibility",
        "mode": "SHADOW",
        "snapshot_id": "snap_dd_full_render_malformed_mode_state_candidate_visibility",
        "forecast_id": "fcst_dd_full_render_malformed_mode_state_candidate_visibility",
        "parameter_set_id": "params_fx_balanced_v0_1",
        "logic_version": "autotrade_logic_v0_1",
        "forecast_5m": {"forecast_id": "fcst_dd_full_render_malformed_mode_state_candidate_visibility", "forecast_direction": "down", "confidence": "medium"},
        "candidate": {"action": "NO_NEW_ENTRY"},
        "risk_gate": {"allowed": False, "executable": False},
        "final_action": "WAIT",
        "reason_codes": ["dd_full_render_malformed_mode_state_candidate_visibility_guard"],
        "blocked_by": [],
        "would_order": None,
    }


def outcome_row() -> dict[str, Any]:
    return {
        "forecast_id": "fcst_dd_full_render_malformed_mode_state_candidate_visibility",
        "parameter_set_id": "params_fx_balanced_v0_1",
        "logic_version": "autotrade_logic_v0_1",
        "source_snapshot_id": "snap_dd_full_render_malformed_mode_state_candidate_visibility",
        "target_ts": "2026-06-13T02:00:00Z",
        "actual_snapshot_id": "actual_dd_full_render_malformed_mode_state_candidate_visibility",
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
    hot_root = REPO_ROOT / "tmp/btc_ts_full_render_malformed_mode_state_candidate_visibility_hot"
    import_exception = None
    render_exception = None
    before_command_count = -1
    after_render_command_count = -2
    before_mode_count = -1
    after_render_mode_count = -2
    before_observer_count = 0
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
        write_command_jsonl(command_path)
        write_mode_state_with_malformed(mode_state_path)
        write_jsonl(shadow_path, [shadow_row()])
        write_jsonl(outcome_path, [outcome_row()])
        before_command_count = len(read_command_ledger_rows(command_path, max_lines=100).rows)
        mode_read_before = read_mode_state_records(mode_state_path, max_lines=100)
        before_mode_count = len(mode_read_before.rows)
        before_observer_count = 0 if not observer_path.exists() else len(observer_path.read_text(encoding="utf-8").splitlines())
        mode_summary_before = summarize_mode_state(mode_state_path, max_lines=100).to_dict()
        preview_before_render = preview_latest_mode_change_command_apply_with_readiness_recheck(max_lines=100, max_observer_run_age_sec=120, allow_warnings=False).to_dict()
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
        mode_read_after = read_mode_state_records(mode_state_path, max_lines=100)
        mode_summary_after = summarize_mode_state(mode_state_path, max_lines=100).to_dict()
        preview_after_render = preview_latest_mode_change_command_apply_with_readiness_recheck(max_lines=100, max_observer_run_age_sec=120, allow_warnings=False).to_dict()
        after_render_command_count = len(read_command_ledger_rows(command_path, max_lines=100).rows)
        after_render_mode_count = len(mode_read_after.rows)
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

    render_source = function_source(UI_FILE, "render")
    mode_state_panel_source = function_source(UI_FILE, "_render_mode_state_status")
    apply_preview_panel_source = function_source(UI_FILE, "_render_mode_change_apply_preview_status")
    live_readiness_source = function_source(UI_FILE, "_render_live_readiness_preflight")
    status_sources = {name: function_source(UI_FILE, name) for name in READ_ONLY_STATUS_FUNCTIONS}
    read_mode_source = function_source(MODE_STATE_FILE, "read_mode_state_records")
    summarize_mode_source = function_source(MODE_STATE_FILE, "summarize_mode_state")
    applied_ids_source = function_source(APPLIER_FILE, "_applied_command_ids")
    preview_source = function_source(APPLIER_FILE, "preview_latest_mode_change_command_apply_with_readiness_recheck")
    checks = {
        "mode_state_reader_before_render_skips_malformed_but_keeps_valid_rows": before_mode_count == 2 and mode_read_before.skipped_count == 1 and tuple(mode_read_before.error_samples) != (),
        "mode_state_summary_before_render_surfaces_skipped_and_latest_valid": mode_summary_before.get("total_rows") == 2 and mode_summary_before.get("skipped_rows") == 1 and tuple(mode_summary_before.get("error_samples") or ()) != () and mode_summary_before.get("latest_source_command_id") == MIDDLE and mode_summary_before.get("read_only") is True,
        "preview_before_render_selects_oldest_unapplied_and_surfaces_mode_state_skip": preview_before_render.get("command_id") == OLDEST and preview_before_render.get("candidate_command_count") == 1 and tuple(preview_before_render.get("already_applied_command_ids") or ()) == tuple(sorted((LATEST, MIDDLE))) and preview_before_render.get("mode_state_read_skipped_count") == 1 and preview_before_render.get("would_reject_by_readiness") is True,
        "mode_state_summary_after_render_still_surfaces_skipped_and_latest_valid": mode_summary_after.get("total_rows") == 2 and mode_summary_after.get("skipped_rows") == 1 and tuple(mode_summary_after.get("error_samples") or ()) != () and mode_summary_after.get("latest_source_command_id") == MIDDLE and mode_summary_after.get("read_only") is True,
        "preview_after_render_still_selects_oldest_unapplied_and_surfaces_mode_state_skip": preview_after_render.get("command_id") == OLDEST and preview_after_render.get("candidate_command_count") == 1 and tuple(preview_after_render.get("already_applied_command_ids") or ()) == tuple(sorted((LATEST, MIDDLE))) and preview_after_render.get("mode_state_read_skipped_count") == 1 and preview_after_render.get("would_reject_by_readiness") is True,
        "mode_state_panel_displays_skipped_error_and_latest_fields": all(field in mode_state_panel_source for field in MODE_STATE_PANEL_FIELDS),
        "apply_preview_panel_displays_candidate_applied_and_mode_state_skip_fields": all(field in apply_preview_panel_source for field in PREVIEW_PANEL_FIELDS),
        "autotrade_page_imports": import_exception is None,
        "autotrade_page_full_render_smoke": import_exception is None and render_exception is None,
        "full_render_calls_all_panels": all(call in render_source for call in REQUIRED_RENDER_CALLS),
        "full_render_exercised_expected_ui_controls": fake_st.button_call_count >= 4 and fake_st.checkbox_call_count >= 6 and fake_st.selectbox_call_count >= 2 and fake_st.metric_call_count >= 55,
        "full_render_did_not_append_commands": after_render_command_count == before_command_count == 3,
        "full_render_did_not_append_mode_state": after_render_mode_count == before_mode_count == 2 and mode_read_after.skipped_count == 1,
        "full_render_did_not_append_observer_runs": after_render_observer_count == before_observer_count,
        "status_functions_read_only_no_append_runner_broker": all(bool(source) and not any(token in source for token in STATUS_FORBIDDEN_TOKENS) for source in status_sources.values()),
        "live_readiness_no_runner_broker_apply": bool(live_readiness_source) and not any(token in live_readiness_source for token in LIVE_READINESS_FORBIDDEN_TOKENS),
        "mode_state_reader_summary_and_applied_ids_failsoft": bool(read_mode_source) and "skipped += 1" in read_mode_source and bool(summarize_mode_source) and "skipped_rows=read.skipped_count" in summarize_mode_source and bool(applied_ids_source) and "read.skipped_count" in applied_ids_source,
        "preview_source_surfaces_mode_state_skipped_count_no_runner_broker": bool(preview_source) and "mode_state_read_skipped_count=state_skipped" in preview_source and not any(token in preview_source for token in PREVIEW_FORBIDDEN_TOKENS),
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
    failures.extend(f"protected lower-layer dirty during milestone DD: {hit}" for hit in protected_dirty_hits)

    payload = {
        "ok": not failures,
        "phase": "phase4a_autotrade_milestone_dd_full_render_malformed_mode_state_candidate_visibility_guard",
        "status": "closed" if not failures else "open",
        "contract": {
            "mode_state_reader_before_render_skips_malformed_but_keeps_valid_rows": checks["mode_state_reader_before_render_skips_malformed_but_keeps_valid_rows"],
            "mode_state_summary_before_render_surfaces_skipped_and_latest_valid": checks["mode_state_summary_before_render_surfaces_skipped_and_latest_valid"],
            "preview_before_render_selects_oldest_unapplied_and_surfaces_mode_state_skip": checks["preview_before_render_selects_oldest_unapplied_and_surfaces_mode_state_skip"],
            "mode_state_summary_after_render_still_surfaces_skipped_and_latest_valid": checks["mode_state_summary_after_render_still_surfaces_skipped_and_latest_valid"],
            "preview_after_render_still_selects_oldest_unapplied_and_surfaces_mode_state_skip": checks["preview_after_render_still_selects_oldest_unapplied_and_surfaces_mode_state_skip"],
            "mode_state_panel_displays_skipped_error_and_latest_fields": checks["mode_state_panel_displays_skipped_error_and_latest_fields"],
            "apply_preview_panel_displays_candidate_applied_and_mode_state_skip_fields": checks["apply_preview_panel_displays_candidate_applied_and_mode_state_skip_fields"],
            "autotrade_page_imports": checks["autotrade_page_imports"],
            "autotrade_page_full_render_smoke": checks["autotrade_page_full_render_smoke"],
            "full_render_calls_all_panels": checks["full_render_calls_all_panels"],
            "full_render_did_not_append_commands": checks["full_render_did_not_append_commands"],
            "full_render_did_not_append_mode_state": checks["full_render_did_not_append_mode_state"],
            "full_render_did_not_append_observer_runs": checks["full_render_did_not_append_observer_runs"],
            "status_functions_read_only_no_append_runner_broker": checks["status_functions_read_only_no_append_runner_broker"],
            "live_readiness_no_runner_broker_apply": checks["live_readiness_no_runner_broker_apply"],
            "mode_state_reader_summary_and_applied_ids_failsoft": checks["mode_state_reader_summary_and_applied_ids_failsoft"],
            "preview_source_surfaces_mode_state_skipped_count_no_runner_broker": checks["preview_source_surfaces_mode_state_skipped_count_no_runner_broker"],
            "protected_lower_layers_untouched": not protected_dirty_hits,
        },
        "mode_read_before": mode_read_before.to_dict(),
        "mode_summary_before": mode_summary_before,
        "preview_before_render": preview_before_render,
        "mode_read_after": mode_read_after.to_dict(),
        "mode_summary_after": mode_summary_after,
        "preview_after_render": preview_after_render,
        "subheaders": fake_st.subheaders,
        "button_call_count": fake_st.button_call_count,
        "checkbox_call_count": fake_st.checkbox_call_count,
        "selectbox_call_count": fake_st.selectbox_call_count,
        "metric_call_count": fake_st.metric_call_count,
        "before_command_count": before_command_count,
        "after_render_command_count": after_render_command_count,
        "before_mode_count": before_mode_count,
        "after_render_mode_count": after_render_mode_count,
        "before_observer_count": before_observer_count,
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
