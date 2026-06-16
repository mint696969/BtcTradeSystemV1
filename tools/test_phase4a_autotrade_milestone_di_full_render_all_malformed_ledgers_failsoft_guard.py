# path: ./tools/test_phase4a_autotrade_milestone_di_full_render_all_malformed_ledgers_failsoft_guard.py
# desc: Full AutoTrade render remains fail-soft/read-only when command/mode_state/decision ledgers all contain malformed rows.

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

from btcts.autotrade.execution import default_command_ledger_path, default_mode_state_ledger_path, preview_latest_mode_change_command_apply_with_readiness_recheck, read_command_ledger_rows, read_mode_state_records, summarize_command_ledger, summarize_mode_state  # noqa: E402
from btcts.autotrade.health import build_autotrade_runtime_health_snapshot  # noqa: E402
from btcts.autotrade.ledger.decision_status import default_shadow_decision_status_path, summarize_shadow_decision_ledger  # noqa: E402
from btcts.autotrade.ledger.forecast_outcome_status import summarize_forecast_outcome_ledger  # noqa: E402
from btcts.autotrade.ledger.forecast_resolution import default_forecast_outcome_ledger_path  # noqa: E402
from btcts.autotrade.ledger.observer_run_status import default_observer_run_ledger_path, summarize_observer_run_ledger  # noqa: E402
from btcts.autotrade.runtime_paths import ENV_AUTOTRADE_RUNTIME_ROOT  # noqa: E402

UI_FILE = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/views/autotrade_page.py"
PROTECTED_PREFIXES = (
    "btcts_next/src/btcts/collector_vnext/",
    "btcts_next/src/btcts/ingestion/",
    "btcts_next/src/btcts/processing/l3_market_semantics/",
    "btcts_next/src/btcts/processing/l4_consumer_models/",
)
REQUIRED_SUBHEADERS = [
    "Critical State / Emergency",
    "Mode State",
    "Mode Runtime Gate",
    "Mode Change Apply Preview",
    "Command Requests",
    "Runtime Health",
    "Live Readiness Preflight",
    "Operation / Decision Visibility",
    "Observer Runs",
    "Shadow Decision Ledger",
    "Forecast Outcomes / Calibration",
    "Settings / Parameter Set v0.1",
]
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
FORBIDDEN_STATUS_TOKENS = (
    "apply_latest_mode_change_command_once",
    "append_mode_state_record",
    "append_observer_run_record",
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
STATUS_FUNCTIONS = (
    "_render_mode_state_status",
    "_render_mode_runtime_gate_status",
    "_render_mode_change_apply_preview_status",
    "_render_command_request_status",
    "_render_runtime_health_status",
    "_render_observer_run_status",
    "_render_shadow_decision_status",
    "_render_forecast_calibration_status",
)
LATEST = "cmd_di_latest_live_request"
MIDDLE = "cmd_di_middle_live_request"
OLDEST = "cmd_di_oldest_live_request"


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
            self.owner.selectbox_values.append(str(options[index]) if options else "")
        return str(options[index]) if options else ""
    def markdown(self, *args: Any, **kwargs: Any) -> None:
        if self.owner is not None:
            self.owner.markdown_call_count += 1
    def caption(self, *args: Any, **kwargs: Any) -> None:
        if self.owner is not None:
            self.owner.caption_call_count += 1


class FakeStreamlit(types.ModuleType):
    def __init__(self) -> None:
        super().__init__("streamlit")
        self.__path__ = []
        self.session_state: dict[str, Any] = {}
        self.subheaders: list[str] = []
        self.selectbox_values: list[str] = []
        self.button_call_count = 0
        self.checkbox_call_count = 0
        self.selectbox_call_count = 0
        self.metric_call_count = 0
        self.markdown_call_count = 0
        self.caption_call_count = 0
        self.divider_call_count = 0
    def title(self, *args: Any, **kwargs: Any) -> None:
        return None
    def subheader(self, text: str, *args: Any, **kwargs: Any) -> None:
        self.subheaders.append(str(text))
    def caption(self, *args: Any, **kwargs: Any) -> None:
        self.caption_call_count += 1
    def markdown(self, *args: Any, **kwargs: Any) -> None:
        self.markdown_call_count += 1
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
        value = str(options[index]) if options else ""
        self.selectbox_values.append(value)
        return value


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
            "warnings": ["full_render_all_malformed_ledgers_snapshot"],
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
            "reason_codes": ["guard", "full_render_all_malformed_ledgers", command_id],
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
        "reason_codes": ["guard", "full_render_all_malformed_ledgers", command_id, "readiness_recheck"],
        "blocked_by": ["readiness_recheck_not_ready", blocker],
        "ledger_event": "autotrade.mode_state_readiness_recheck_rejected",
        "would_send_to_broker": False,
    }


def observer_row(run_id: str, offset_seconds: int, blocker: str = "") -> dict[str, Any]:
    return {
        "run_id": run_id,
        "started_at": now_z(offset_seconds - 1),
        "finished_at": now_z(offset_seconds),
        "requested_cycles": 1,
        "completed_cycles": 1,
        "appended_shadow_decision_count": 1,
        "appended_forecast_outcome_count": 1,
        "duplicate_snapshot_skipped_count": 0,
        "skip_duplicate_snapshot": True,
        "blocked_by": [blocker] if blocker else [],
        "would_send_to_broker": False,
        "bounded": True,
        "source": "autotrade.observer_cycle_bounded",
    }


def shadow_row(decision_id: str, action: str, blocker: str = "") -> dict[str, Any]:
    return {
        "decision_id": decision_id,
        "mode": "SHADOW",
        "snapshot_id": f"snap_{decision_id}",
        "forecast_id": f"fcst_{decision_id}",
        "parameter_set_id": "params_fx_balanced_v0_1",
        "logic_version": "autotrade_logic_v0_1",
        "forecast_5m": {"forecast_id": f"fcst_{decision_id}", "forecast_direction": "down", "confidence": "medium"},
        "candidate": {"action": action},
        "risk_gate": {"allowed": False, "executable": False},
        "final_action": action,
        "reason_codes": ["guard", "full_render_all_malformed_ledgers", decision_id],
        "blocked_by": [blocker] if blocker else [],
        "would_order": None,
    }


def outcome_row(forecast_id: str, result: str, confidence: str = "medium") -> dict[str, Any]:
    return {
        "forecast_id": forecast_id,
        "parameter_set_id": "params_fx_balanced_v0_1",
        "logic_version": "autotrade_logic_v0_1",
        "source_snapshot_id": f"snap_{forecast_id}",
        "target_ts": "2026-06-13T02:00:00Z",
        "actual_snapshot_id": f"actual_{forecast_id}",
        "forecast_direction": "down",
        "forecast_confidence": confidence,
        "expected_change": "strengthen_sell",
        "drivers": ["sell_pressure_or_ground"],
        "blocked_by": [],
        "result": result,
        "direction_hit": result == "hit",
        "change_type_hit": result == "hit",
        "divergence_reasons": [] if result == "hit" else ["direction_mismatch"],
    }


def write_command_jsonl_with_malformed(path: Path) -> None:
    rows = [
        command_row(OLDEST, now_z(-30), "di_oldest_candidate_blocker"),
        command_row(MIDDLE, now_z(-20), "di_middle_candidate_blocker"),
        command_row(LATEST, now_z(-10), "di_latest_candidate_blocker"),
    ]
    path.parent.mkdir(parents=True, exist_ok=True)
    text = json.dumps(rows[0], ensure_ascii=False, sort_keys=True) + "\n"
    text += "{not-json\n"
    text += json.dumps(rows[1], ensure_ascii=False, sort_keys=True) + "\n"
    text += json.dumps(rows[2], ensure_ascii=False, sort_keys=True) + "\n"
    path.write_text(text, encoding="utf-8")


def write_mode_state_jsonl_with_malformed(path: Path) -> None:
    rows = [mode_state_rejection_row(LATEST, "di_latest_candidate_blocker"), mode_state_rejection_row(MIDDLE, "di_middle_candidate_blocker")]
    path.parent.mkdir(parents=True, exist_ok=True)
    text = json.dumps(rows[0], ensure_ascii=False, sort_keys=True) + "\n"
    text += "{not-json\n"
    text += json.dumps(rows[1], ensure_ascii=False, sort_keys=True) + "\n"
    path.write_text(text, encoding="utf-8")


def write_jsonl_with_malformed(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    text = json.dumps(rows[0], ensure_ascii=False, sort_keys=True) + "\n"
    text += "{not-json\n"
    text += json.dumps(rows[1], ensure_ascii=False, sort_keys=True) + "\n"
    path.write_text(text, encoding="utf-8")


def main() -> int:
    failures: list[str] = []
    original_runtime = os.environ.get(ENV_AUTOTRADE_RUNTIME_ROOT)
    previous_streamlit = sys.modules.get("streamlit")
    previous_components = sys.modules.get("streamlit.components")
    previous_components_v1 = sys.modules.get("streamlit.components.v1")
    hot_root = REPO_ROOT / "tmp/btc_ts_full_render_all_malformed_ledgers_hot"
    fake_st = FakeStreamlit()
    import_exception = None
    render_exception = None
    try:
        os.environ[ENV_AUTOTRADE_RUNTIME_ROOT] = str(hot_root)
        command_path = default_command_ledger_path(ensure=True)
        mode_state_path = default_mode_state_ledger_path(ensure=True)
        observer_path = default_observer_run_ledger_path(ensure=True)
        shadow_path = default_shadow_decision_status_path(ensure=True)
        outcome_path = default_forecast_outcome_ledger_path(ensure=True)
        for path in (command_path, mode_state_path, observer_path, shadow_path, outcome_path):
            if path.exists():
                path.unlink()
        write_command_jsonl_with_malformed(command_path)
        write_mode_state_jsonl_with_malformed(mode_state_path)
        write_jsonl_with_malformed(observer_path, [observer_row("obs_di_old", -20, "di_old_observer_blocker"), observer_row("obs_di_latest", -5, "di_latest_observer_blocker")])
        write_jsonl_with_malformed(shadow_path, [shadow_row("di_old", "WAIT", "di_old_shadow_blocker"), shadow_row("di_latest", "WAIT", "di_latest_shadow_blocker")])
        write_jsonl_with_malformed(outcome_path, [outcome_row("fcst_di_old", "hit", "medium"), outcome_row("fcst_di_latest", "miss", "high")])

        before_line_counts = {
            "command": len(command_path.read_text(encoding="utf-8").splitlines()),
            "mode_state": len(mode_state_path.read_text(encoding="utf-8").splitlines()),
            "observer": len(observer_path.read_text(encoding="utf-8").splitlines()),
            "shadow": len(shadow_path.read_text(encoding="utf-8").splitlines()),
            "outcome": len(outcome_path.read_text(encoding="utf-8").splitlines()),
        }
        command_before = summarize_command_ledger(command_path, max_lines=100).to_dict()
        mode_before = summarize_mode_state(mode_state_path, max_lines=100).to_dict()
        observer_before = summarize_observer_run_ledger(observer_path, max_lines=100).to_dict()
        shadow_before = summarize_shadow_decision_ledger(shadow_path, max_lines=100).to_dict()
        outcome_before = summarize_forecast_outcome_ledger(outcome_path, max_lines=100).to_dict()
        preview_before = preview_latest_mode_change_command_apply_with_readiness_recheck(max_lines=100, max_observer_run_age_sec=120, allow_warnings=False).to_dict()
        health_before = build_autotrade_runtime_health_snapshot(max_observer_run_age_sec=120, max_lines=100).to_dict()

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

        command_after = summarize_command_ledger(command_path, max_lines=100).to_dict()
        mode_after = summarize_mode_state(mode_state_path, max_lines=100).to_dict()
        observer_after = summarize_observer_run_ledger(observer_path, max_lines=100).to_dict()
        shadow_after = summarize_shadow_decision_ledger(shadow_path, max_lines=100).to_dict()
        outcome_after = summarize_forecast_outcome_ledger(outcome_path, max_lines=100).to_dict()
        preview_after = preview_latest_mode_change_command_apply_with_readiness_recheck(max_lines=100, max_observer_run_age_sec=120, allow_warnings=False).to_dict()
        health_after = build_autotrade_runtime_health_snapshot(max_observer_run_age_sec=120, max_lines=100).to_dict()
        after_line_counts = {
            "command": len(command_path.read_text(encoding="utf-8").splitlines()),
            "mode_state": len(mode_state_path.read_text(encoding="utf-8").splitlines()),
            "observer": len(observer_path.read_text(encoding="utf-8").splitlines()),
            "shadow": len(shadow_path.read_text(encoding="utf-8").splitlines()),
            "outcome": len(outcome_path.read_text(encoding="utf-8").splitlines()),
        }
        command_valid_after = len(read_command_ledger_rows(command_path, max_lines=100).rows)
        mode_valid_after = len(read_mode_state_records(mode_state_path, max_lines=100).rows)
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
    status_sources = {name: function_source(UI_FILE, name) for name in STATUS_FUNCTIONS}
    health_warnings = tuple(health_before.get("warnings") or ())
    checks = {
        "all_ledger_summaries_before_render_are_failsoft": command_before.get("total_rows") == 3 and command_before.get("skipped_rows") == 1 and mode_before.get("total_rows") == 2 and mode_before.get("skipped_rows") == 1 and observer_before.get("total_rows") == 2 and observer_before.get("skipped_rows") == 1 and shadow_before.get("total_rows") == 2 and shadow_before.get("skipped_rows") == 1 and outcome_before.get("total_rows") == 2,
        "preview_before_render_selects_oldest_unapplied_with_command_and_mode_skips": preview_before.get("command_id") == OLDEST and preview_before.get("candidate_command_count") == 1 and tuple(preview_before.get("already_applied_command_ids") or ()) == tuple(sorted((LATEST, MIDDLE))) and preview_before.get("command_read_skipped_count") == 1 and preview_before.get("mode_state_read_skipped_count") == 1,
        "runtime_health_before_render_uses_valid_decision_rows_and_warns_on_skips": health_before.get("observer_runs", {}).get("latest_run_id") == "obs_di_latest" and health_before.get("shadow_decisions", {}).get("latest_decision_id") == "di_latest" and health_before.get("forecast_outcomes", {}).get("latest_forecast_id") == "fcst_di_latest" and "observer_run_ledger_has_skipped_rows" in health_warnings and "shadow_decision_ledger_has_skipped_rows" in health_warnings,
        "autotrade_page_full_render_smoke_all_malformed_ledgers": import_exception is None and render_exception is None and fake_st.subheaders == REQUIRED_SUBHEADERS and fake_st.metric_call_count >= 55 and fake_st.divider_call_count >= 11,
        "full_render_calls_all_panels": all(call in render_source for call in REQUIRED_RENDER_CALLS),
        "full_render_did_not_append_any_ledgers": after_line_counts == before_line_counts == {"command": 4, "mode_state": 3, "observer": 3, "shadow": 3, "outcome": 3} and command_valid_after == 3 and mode_valid_after == 2,
        "summaries_after_render_preserve_failsoft_state": command_after == command_before and mode_after == mode_before and observer_after == observer_before and shadow_after == shadow_before and outcome_after == outcome_before,
        "preview_after_render_still_selects_oldest_unapplied_with_skips": preview_after.get("command_id") == OLDEST and preview_after.get("candidate_command_count") == 1 and tuple(preview_after.get("already_applied_command_ids") or ()) == tuple(sorted((LATEST, MIDDLE))) and preview_after.get("command_read_skipped_count") == 1 and preview_after.get("mode_state_read_skipped_count") == 1,
        "runtime_health_after_render_still_readonly_and_warn": health_after.get("health_state") == health_before.get("health_state") and health_after.get("observer_runs", {}).get("skipped_rows") == 1 and health_after.get("shadow_decisions", {}).get("skipped_rows") == 1 and health_after.get("would_send_to_broker") is False and health_after.get("read_only") is True,
        "status_functions_remain_read_only_no_runner_broker": all(bool(source) and not any(token in source for token in FORBIDDEN_STATUS_TOKENS) for source in status_sources.values()),
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
    failures.extend(f"protected lower-layer dirty during milestone DI: {hit}" for hit in protected_dirty_hits)

    payload = {
        "ok": not failures,
        "phase": "phase4a_autotrade_milestone_di_full_render_all_malformed_ledgers_failsoft_guard",
        "status": "closed" if not failures else "open",
        "contract": {
            "all_ledger_summaries_before_render_are_failsoft": checks["all_ledger_summaries_before_render_are_failsoft"],
            "preview_before_render_selects_oldest_unapplied_with_command_and_mode_skips": checks["preview_before_render_selects_oldest_unapplied_with_command_and_mode_skips"],
            "runtime_health_before_render_uses_valid_decision_rows_and_warns_on_skips": checks["runtime_health_before_render_uses_valid_decision_rows_and_warns_on_skips"],
            "autotrade_page_full_render_smoke_all_malformed_ledgers": checks["autotrade_page_full_render_smoke_all_malformed_ledgers"],
            "full_render_calls_all_panels": checks["full_render_calls_all_panels"],
            "full_render_did_not_append_any_ledgers": checks["full_render_did_not_append_any_ledgers"],
            "summaries_after_render_preserve_failsoft_state": checks["summaries_after_render_preserve_failsoft_state"],
            "preview_after_render_still_selects_oldest_unapplied_with_skips": checks["preview_after_render_still_selects_oldest_unapplied_with_skips"],
            "runtime_health_after_render_still_readonly_and_warn": checks["runtime_health_after_render_still_readonly_and_warn"],
            "status_functions_remain_read_only_no_runner_broker": checks["status_functions_remain_read_only_no_runner_broker"],
            "protected_lower_layers_untouched": not protected_dirty_hits,
        },
        "command_before": command_before,
        "mode_before": mode_before,
        "observer_before": observer_before,
        "shadow_before": shadow_before,
        "outcome_before": outcome_before,
        "preview_before": preview_before,
        "health_before": health_before,
        "command_after": command_after,
        "mode_after": mode_after,
        "observer_after": observer_after,
        "shadow_after": shadow_after,
        "outcome_after": outcome_after,
        "preview_after": preview_after,
        "health_after": health_after,
        "fake_ui": {
            "subheaders": fake_st.subheaders,
            "selectbox_values": fake_st.selectbox_values,
            "metric_call_count": fake_st.metric_call_count,
            "button_call_count": fake_st.button_call_count,
            "checkbox_call_count": fake_st.checkbox_call_count,
            "selectbox_call_count": fake_st.selectbox_call_count,
            "markdown_call_count": fake_st.markdown_call_count,
            "caption_call_count": fake_st.caption_call_count,
            "divider_call_count": fake_st.divider_call_count,
        },
        "before_line_counts": before_line_counts,
        "after_line_counts": after_line_counts,
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
