# path: ./tools/test_phase4a_autotrade_milestone_dg_runtime_health_malformed_decision_ledgers_failsoft_guard.py
# desc: Guard runtime health remains fail-soft/read-only when observer/shadow/outcome decision ledgers contain malformed rows.

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

from btcts.autotrade.execution import default_command_ledger_path, default_mode_state_ledger_path, read_command_ledger_rows, read_mode_state_records  # noqa: E402
from btcts.autotrade.health import build_autotrade_runtime_health_snapshot  # noqa: E402
from btcts.autotrade.ledger.decision_status import default_shadow_decision_status_path, summarize_shadow_decision_ledger  # noqa: E402
from btcts.autotrade.ledger.forecast_resolution import default_forecast_outcome_ledger_path  # noqa: E402
from btcts.autotrade.ledger.forecast_outcome_status import summarize_forecast_outcome_ledger  # noqa: E402
from btcts.autotrade.ledger.observer_run_status import default_observer_run_ledger_path, summarize_observer_run_ledger  # noqa: E402
from btcts.autotrade.runtime_paths import ENV_AUTOTRADE_RUNTIME_ROOT  # noqa: E402

HEALTH_FILE = REPO_ROOT / "btcts_next/src/btcts/autotrade/health.py"
OBSERVER_STATUS_FILE = REPO_ROOT / "btcts_next/src/btcts/autotrade/ledger/observer_run_status.py"
SHADOW_STATUS_FILE = REPO_ROOT / "btcts_next/src/btcts/autotrade/ledger/decision_status.py"
FORECAST_STATUS_FILE = REPO_ROOT / "btcts_next/src/btcts/autotrade/ledger/forecast_outcome_status.py"
FORECAST_RESOLUTION_FILE = REPO_ROOT / "btcts_next/src/btcts/autotrade/ledger/forecast_resolution.py"
UI_FILE = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/views/autotrade_page.py"
PROTECTED_PREFIXES = (
    "btcts_next/src/btcts/collector_vnext/",
    "btcts_next/src/btcts/ingestion/",
    "btcts_next/src/btcts/processing/l3_market_semantics/",
    "btcts_next/src/btcts/processing/l4_consumer_models/",
)
FORBIDDEN_READ_ONLY_TOKENS = (
    "append_mode_state_record",
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
RUNTIME_HEALTH_PANEL_FIELDS = (
    "health_state",
    "observer_run_fresh",
    "observer_run_age_sec",
    "blocked_by",
    "warnings",
    "runtime",
    "observer_runs",
    "shadow_decisions",
    "forecast_outcomes",
    "latest_run_id",
    "latest_action",
    "latest_result",
    "would_send_to_broker",
    "read_only",
)


class FakeColumn:
    def __init__(self, owner: "FakeStreamlit | None" = None) -> None:
        self.owner = owner
    def metric(self, *args: Any, **kwargs: Any) -> None:
        if self.owner is not None:
            self.owner.metric_call_count += 1


class FakeStreamlit(types.ModuleType):
    def __init__(self) -> None:
        super().__init__("streamlit")
        self.__path__ = []
        self.session_state: dict[str, Any] = {}
        self.subheaders: list[str] = []
        self.metric_call_count = 0
    def subheader(self, text: str, *args: Any, **kwargs: Any) -> None:
        self.subheaders.append(str(text))
    def caption(self, *args: Any, **kwargs: Any) -> None:
        return None
    def markdown(self, *args: Any, **kwargs: Any) -> None:
        return None
    def columns(self, count: int) -> list[FakeColumn]:
        return [FakeColumn(self) for _ in range(int(count))]


def now_z(offset_seconds: int = 0) -> str:
    return (datetime.now(timezone.utc).replace(microsecond=0) + timedelta(seconds=offset_seconds)).isoformat().replace("+00:00", "Z")


def function_source(path: Path, function_name: str) -> str:
    text = path.read_text(encoding="utf-8")
    tree = ast.parse(text)
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == function_name:
            return ast.get_source_segment(text, node) or ""
    return ""


def observer_row(run_id: str, offset_seconds: int, blocker: str = "") -> dict[str, Any]:
    ts = now_z(offset_seconds)
    return {
        "run_id": run_id,
        "started_at": now_z(offset_seconds - 1),
        "finished_at": ts,
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
        "forecast_5m": {
            "forecast_id": f"fcst_{decision_id}",
            "forecast_direction": "down",
            "confidence": "medium",
        },
        "candidate": {"action": action},
        "risk_gate": {"allowed": False, "executable": False},
        "final_action": action,
        "reason_codes": ["guard", "runtime_health_malformed_decision_ledgers", decision_id],
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


def write_jsonl_with_malformed(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    text = json.dumps(rows[0], ensure_ascii=False, sort_keys=True) + "\n"
    text += "{not-json\n"
    text += json.dumps(rows[1], ensure_ascii=False, sort_keys=True) + "\n"
    path.write_text(text, encoding="utf-8")


def import_and_render_runtime_health(fake_st: FakeStreamlit) -> tuple[str | None, str | None]:
    previous_streamlit = sys.modules.get("streamlit")
    previous_components = sys.modules.get("streamlit.components")
    previous_components_v1 = sys.modules.get("streamlit.components.v1")
    fake_components = types.ModuleType("streamlit.components")
    fake_components.__path__ = []
    fake_components_v1 = types.ModuleType("streamlit.components.v1")
    fake_components_v1.html = lambda *args, **kwargs: None
    fake_components.v1 = fake_components_v1
    fake_st.components = fake_components
    try:
        sys.modules["streamlit"] = fake_st
        sys.modules["streamlit.components"] = fake_components
        sys.modules["streamlit.components.v1"] = fake_components_v1
        module = importlib.import_module("btcts.apps.operator_ui.views.autotrade_page")
        module = importlib.reload(module)
        module._render_runtime_health_status()
        return None, None
    except Exception as exc:
        return None, repr(exc)
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


def main() -> int:
    failures: list[str] = []
    original_runtime = os.environ.get(ENV_AUTOTRADE_RUNTIME_ROOT)
    hot_root = REPO_ROOT / "tmp/btc_ts_runtime_health_malformed_decision_ledgers_hot"
    fake_st = FakeStreamlit()
    before_command_count = 0
    after_health_command_count = 0
    before_mode_count = 0
    after_health_mode_count = 0
    before_observer_line_count = 0
    after_observer_line_count = 0
    before_shadow_line_count = 0
    after_shadow_line_count = 0
    before_outcome_line_count = 0
    after_outcome_line_count = 0
    ui_exception = None
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
        write_jsonl_with_malformed(observer_path, [observer_row("obs_dg_old", -20), observer_row("obs_dg_latest", -5)])
        write_jsonl_with_malformed(shadow_path, [shadow_row("dg_old", "WAIT", "dg_old_blocker"), shadow_row("dg_latest", "WAIT", "dg_latest_blocker")])
        write_jsonl_with_malformed(outcome_path, [outcome_row("fcst_dg_old", "hit", "medium"), outcome_row("fcst_dg_latest", "miss", "high")])
        before_command_count = len(read_command_ledger_rows(command_path, max_lines=100).rows)
        before_mode_count = len(read_mode_state_records(mode_state_path, max_lines=100).rows)
        before_observer_line_count = len(observer_path.read_text(encoding="utf-8").splitlines())
        before_shadow_line_count = len(shadow_path.read_text(encoding="utf-8").splitlines())
        before_outcome_line_count = len(outcome_path.read_text(encoding="utf-8").splitlines())
        observer_before = summarize_observer_run_ledger(observer_path, max_lines=100).to_dict()
        shadow_before = summarize_shadow_decision_ledger(shadow_path, max_lines=100).to_dict()
        outcome_before = summarize_forecast_outcome_ledger(outcome_path, max_lines=100).to_dict()
        health = build_autotrade_runtime_health_snapshot(max_observer_run_age_sec=120, max_lines=100).to_dict()
        _module, ui_exception = import_and_render_runtime_health(fake_st)
        observer_after = summarize_observer_run_ledger(observer_path, max_lines=100).to_dict()
        shadow_after = summarize_shadow_decision_ledger(shadow_path, max_lines=100).to_dict()
        outcome_after = summarize_forecast_outcome_ledger(outcome_path, max_lines=100).to_dict()
        after_health_command_count = len(read_command_ledger_rows(command_path, max_lines=100).rows)
        after_health_mode_count = len(read_mode_state_records(mode_state_path, max_lines=100).rows)
        after_observer_line_count = len(observer_path.read_text(encoding="utf-8").splitlines())
        after_shadow_line_count = len(shadow_path.read_text(encoding="utf-8").splitlines())
        after_outcome_line_count = len(outcome_path.read_text(encoding="utf-8").splitlines())
    finally:
        if original_runtime is None:
            os.environ.pop(ENV_AUTOTRADE_RUNTIME_ROOT, None)
        else:
            os.environ[ENV_AUTOTRADE_RUNTIME_ROOT] = original_runtime

    health_source = function_source(HEALTH_FILE, "build_autotrade_runtime_health_snapshot")
    observer_summary_source = function_source(OBSERVER_STATUS_FILE, "summarize_observer_run_ledger")
    shadow_read_source = function_source(SHADOW_STATUS_FILE, "read_shadow_decision_rows")
    shadow_summary_source = function_source(SHADOW_STATUS_FILE, "summarize_shadow_decision_ledger")
    forecast_read_source = function_source(FORECAST_RESOLUTION_FILE, "read_forecast_outcome_links")
    forecast_summary_source = function_source(FORECAST_STATUS_FILE, "summarize_forecast_outcome_ledger")
    ui_health_source = function_source(UI_FILE, "_render_runtime_health_status")
    health_warnings = tuple(health.get("warnings") or ())
    checks = {
        "observer_summary_skips_malformed_and_keeps_latest_valid_row": observer_before.get("total_rows") == 2 and observer_before.get("skipped_rows") == 1 and tuple(observer_before.get("error_samples") or ()) != () and observer_before.get("latest_run_id") == "obs_dg_latest" and observer_before.get("latest_would_send_to_broker") is False,
        "shadow_summary_skips_malformed_and_keeps_latest_valid_row": shadow_before.get("total_rows") == 2 and shadow_before.get("skipped_rows") == 1 and tuple(shadow_before.get("error_samples") or ()) != () and shadow_before.get("latest_decision_id") == "dg_latest" and shadow_before.get("latest_action") == "WAIT",
        "forecast_outcome_summary_ignores_malformed_and_keeps_latest_valid_row": outcome_before.get("total_rows") == 2 and outcome_before.get("latest_forecast_id") == "fcst_dg_latest" and outcome_before.get("latest_result") == "miss" and (outcome_before.get("calibration") or {}).get("total_forecast_count") == 2,
        "runtime_health_uses_failsoft_summaries_and_warns_on_skipped_observer_shadow": health.get("observer_runs", {}).get("latest_run_id") == "obs_dg_latest" and health.get("observer_runs", {}).get("skipped_rows") == 1 and health.get("shadow_decisions", {}).get("latest_decision_id") == "dg_latest" and health.get("shadow_decisions", {}).get("skipped_rows") == 1 and health.get("forecast_outcomes", {}).get("latest_forecast_id") == "fcst_dg_latest" and "observer_run_ledger_has_skipped_rows" in health_warnings and "shadow_decision_ledger_has_skipped_rows" in health_warnings,
        "runtime_health_is_fresh_warn_read_only_no_broker": health.get("observer_run_fresh") is True and health.get("health_state") == "warn" and tuple(health.get("blocked_by") or ()) == () and health.get("would_send_to_broker") is False and health.get("read_only") is True,
        "ui_runtime_health_panel_renders_with_malformed_ledgers": ui_exception is None and "Runtime Health" in fake_st.subheaders and fake_st.metric_call_count >= 5,
        "runtime_health_did_not_append_any_ledgers": after_health_command_count == before_command_count == 0 and after_health_mode_count == before_mode_count == 0 and after_observer_line_count == before_observer_line_count == 3 and after_shadow_line_count == before_shadow_line_count == 3 and after_outcome_line_count == before_outcome_line_count == 3,
        "summaries_after_health_are_unchanged": observer_after == observer_before and shadow_after == shadow_before and outcome_after == outcome_before,
        "health_source_uses_readonly_summaries_no_runner_broker": bool(health_source) and "summarize_observer_run_ledger" in health_source and "summarize_shadow_decision_ledger" in health_source and "summarize_forecast_outcome_ledger" in health_source and "would_send_to_broker=False" in health_source and "read_only=True" in health_source and not any(token in health_source for token in FORBIDDEN_READ_ONLY_TOKENS),
        "observer_shadow_forecast_sources_are_failsoft_readonly": bool(observer_summary_source) and "skipped += 1" in observer_summary_source and bool(shadow_read_source) and "skipped += 1" in shadow_read_source and bool(shadow_summary_source) and "read_shadow_decision_rows" in shadow_summary_source and bool(forecast_read_source) and "except Exception" in forecast_read_source and bool(forecast_summary_source) and "read_forecast_outcome_links" in forecast_summary_source,
        "ui_runtime_health_panel_displays_fields_and_no_runner_broker": bool(ui_health_source) and all(field in ui_health_source for field in RUNTIME_HEALTH_PANEL_FIELDS) and not any(token in ui_health_source for token in FORBIDDEN_READ_ONLY_TOKENS),
    }
    failures.extend(f"check failed: {name}" for name, ok in checks.items() if not ok)
    if ui_exception:
        failures.append(f"ui_exception: {ui_exception}")

    protected_dirty_hits: list[str] = []
    status = subprocess.run(["git", "status", "--short"], cwd=REPO_ROOT, text=True, capture_output=True, check=True).stdout.splitlines()
    for line in status:
        rel = line[3:] if len(line) > 3 else line
        if any(rel.startswith(prefix) for prefix in PROTECTED_PREFIXES):
            protected_dirty_hits.append(line)
    failures.extend(f"protected lower-layer dirty during milestone DG: {hit}" for hit in protected_dirty_hits)

    payload = {
        "ok": not failures,
        "phase": "phase4a_autotrade_milestone_dg_runtime_health_malformed_decision_ledgers_failsoft_guard",
        "status": "closed" if not failures else "open",
        "contract": {
            "observer_summary_skips_malformed_and_keeps_latest_valid_row": checks["observer_summary_skips_malformed_and_keeps_latest_valid_row"],
            "shadow_summary_skips_malformed_and_keeps_latest_valid_row": checks["shadow_summary_skips_malformed_and_keeps_latest_valid_row"],
            "forecast_outcome_summary_ignores_malformed_and_keeps_latest_valid_row": checks["forecast_outcome_summary_ignores_malformed_and_keeps_latest_valid_row"],
            "runtime_health_uses_failsoft_summaries_and_warns_on_skipped_observer_shadow": checks["runtime_health_uses_failsoft_summaries_and_warns_on_skipped_observer_shadow"],
            "runtime_health_is_fresh_warn_read_only_no_broker": checks["runtime_health_is_fresh_warn_read_only_no_broker"],
            "ui_runtime_health_panel_renders_with_malformed_ledgers": checks["ui_runtime_health_panel_renders_with_malformed_ledgers"],
            "runtime_health_did_not_append_any_ledgers": checks["runtime_health_did_not_append_any_ledgers"],
            "summaries_after_health_are_unchanged": checks["summaries_after_health_are_unchanged"],
            "health_source_uses_readonly_summaries_no_runner_broker": checks["health_source_uses_readonly_summaries_no_runner_broker"],
            "observer_shadow_forecast_sources_are_failsoft_readonly": checks["observer_shadow_forecast_sources_are_failsoft_readonly"],
            "ui_runtime_health_panel_displays_fields_and_no_runner_broker": checks["ui_runtime_health_panel_displays_fields_and_no_runner_broker"],
            "protected_lower_layers_untouched": not protected_dirty_hits,
        },
        "observer_before": observer_before,
        "shadow_before": shadow_before,
        "outcome_before": outcome_before,
        "health": health,
        "observer_after": observer_after,
        "shadow_after": shadow_after,
        "outcome_after": outcome_after,
        "fake_ui": {"subheaders": fake_st.subheaders, "metric_call_count": fake_st.metric_call_count},
        "before_command_count": before_command_count,
        "after_health_command_count": after_health_command_count,
        "before_mode_count": before_mode_count,
        "after_health_mode_count": after_health_mode_count,
        "before_observer_line_count": before_observer_line_count,
        "after_observer_line_count": after_observer_line_count,
        "before_shadow_line_count": before_shadow_line_count,
        "after_shadow_line_count": after_shadow_line_count,
        "before_outcome_line_count": before_outcome_line_count,
        "after_outcome_line_count": after_outcome_line_count,
        "ui_exception": ui_exception,
        "checks": checks,
        "protected_dirty_hits": protected_dirty_hits,
        "failures": failures,
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2, default=str))
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
