# path: ./tools/test_phase4a_autotrade_milestone_bj_observer_run_latest_blocked_visibility_guard.py
# desc: Guard observer_run summary/UI exposes latest blocked run details read-only. No runner/broker execution.

from __future__ import annotations

import ast
import json
import os
import subprocess
import sys
import types
import importlib
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = REPO_ROOT / "btcts_next/src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from btcts.autotrade.ledger import ObserverRunRecord, append_observer_run_record, default_observer_run_ledger_path, summarize_observer_run_ledger  # noqa: E402
from btcts.autotrade.execution import read_command_ledger, read_mode_state_records  # noqa: E402
from btcts.autotrade.runtime_paths import ENV_AUTOTRADE_RUNTIME_ROOT  # noqa: E402

OBSERVER_STATUS_FILE = REPO_ROOT / "btcts_next/src/btcts/autotrade/ledger/observer_run_status.py"
UI_FILE = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/views/autotrade_page.py"
PROTECTED_PREFIXES = (
    "btcts_next/src/btcts/collector_vnext/",
    "btcts_next/src/btcts/ingestion/",
    "btcts_next/src/btcts/processing/l3_market_semantics/",
    "btcts_next/src/btcts/processing/l4_consumer_models/",
)
LATEST_FIELDS = (
    "latest_skip_duplicate_snapshot",
    "latest_blocked_by",
    "latest_would_send_to_broker",
    "latest_bounded",
)
STATUS_FORBIDDEN_TOKENS = (
    "append_observer_run_record",
    "append_mode_state_record",
    "validate_and_append_command",
    "append_command_ledger_record",
    "submit_mode_change_command_request",
    "run_observer_cycle_bounded",
    "run_observer_cycle_once",
    "run_shadow_cycle_once",
    "run_shadow_cycle_bounded",
    "resolve_due_shadow_forecast_outcomes",
    "run_latest_market_state_shadow_decision",
    "apply_latest_mode_change_command_once",
    "st.button(",
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

    def subheader(self, *args: Any, **kwargs: Any) -> None:
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

    def title(self, *args: Any, **kwargs: Any) -> None:
        return None

    def caption(self, *args: Any, **kwargs: Any) -> None:
        return None

    def subheader(self, *args: Any, **kwargs: Any) -> None:
        return None

    def markdown(self, *args: Any, **kwargs: Any) -> None:
        return None

    def divider(self, *args: Any, **kwargs: Any) -> None:
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
    previous_streamlit = sys.modules.get("streamlit")
    previous_components = sys.modules.get("streamlit.components")
    previous_components_v1 = sys.modules.get("streamlit.components.v1")
    fake_st = FakeStreamlit()
    hot_root = REPO_ROOT / "tmp/btc_ts_observer_run_latest_blocked_visibility_hot"
    render_exception = None
    import_exception = None
    before_observer_rows = -1
    after_observer_rows = -2
    before_command_count = -1
    after_command_count = -2
    before_mode_count = -1
    after_mode_count = -2
    try:
        os.environ[ENV_AUTOTRADE_RUNTIME_ROOT] = str(hot_root)
        path = default_observer_run_ledger_path(ensure=True)
        if path.exists():
            path.unlink()
        append_observer_run_record(
            path,
            ObserverRunRecord(
                run_id="obs_bj_allowed",
                started_at="2026-06-13T08:00:00Z",
                finished_at="2026-06-13T08:00:01Z",
                requested_cycles=2,
                completed_cycles=2,
                appended_shadow_decision_count=2,
                appended_forecast_outcome_count=2,
                duplicate_snapshot_skipped_count=0,
                skip_duplicate_snapshot=True,
                blocked_by=(),
                would_send_to_broker=False,
                bounded=True,
            ),
        )
        append_observer_run_record(
            path,
            ObserverRunRecord(
                run_id="obs_bj_blocked_off",
                started_at="2026-06-13T08:01:00Z",
                finished_at="2026-06-13T08:01:01Z",
                requested_cycles=2,
                completed_cycles=2,
                appended_shadow_decision_count=0,
                appended_forecast_outcome_count=0,
                duplicate_snapshot_skipped_count=0,
                skip_duplicate_snapshot=True,
                blocked_by=("mode_off", "mode_runtime_gate_blocked_shadow_decision_append", "mode_runtime_gate_blocked_forecast_outcome_resolution"),
                would_send_to_broker=False,
                bounded=True,
            ),
        )
        summary = summarize_observer_run_ledger(max_lines=100)
        command_path = hot_root / "autotrade/commands/command_requests.jsonl"
        mode_path = hot_root / "autotrade/decisions/mode_state.jsonl"
        command_path.parent.mkdir(parents=True, exist_ok=True)
        command_path.write_text("", encoding="utf-8")
        before_observer_rows = len(path.read_text(encoding="utf-8").splitlines())
        before_command_count = len(read_command_ledger(command_path))
        before_mode_count = len(read_mode_state_records(mode_path, max_lines=100).rows)
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
        after_observer_rows = len(path.read_text(encoding="utf-8").splitlines())
        after_command_count = len(read_command_ledger(command_path))
        after_mode_count = len(read_mode_state_records(mode_path, max_lines=100).rows)
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

    status_text = OBSERVER_STATUS_FILE.read_text(encoding="utf-8")
    ui_source = function_source(UI_FILE, "_render_observer_run_status")
    checks = {
        "summary_fields_present": all(token in status_text for token in LATEST_FIELDS),
        "summary_exposes_latest_blocked_run": summary.latest_run_id == "obs_bj_blocked_off" and tuple(summary.latest_blocked_by) == ("mode_off", "mode_runtime_gate_blocked_shadow_decision_append", "mode_runtime_gate_blocked_forecast_outcome_resolution") and summary.latest_skip_duplicate_snapshot is True and summary.latest_bounded is True and summary.latest_would_send_to_broker is False,
        "json_safe_summary": json.loads(json.dumps(summary.to_dict(), ensure_ascii=False))["latest_blocked_by"] == ["mode_off", "mode_runtime_gate_blocked_shadow_decision_append", "mode_runtime_gate_blocked_forecast_outcome_resolution"],
        "ui_observer_runs_displays_latest_blocked_fields": all(token in ui_source for token in LATEST_FIELDS),
        "ui_observer_run_status_read_only": bool(ui_source) and not any(token in ui_source for token in STATUS_FORBIDDEN_TOKENS),
        "render_smoke_ok": import_exception is None and render_exception is None,
        "render_did_not_append_observer_runs": before_observer_rows == 2 and after_observer_rows == before_observer_rows,
        "render_did_not_append_commands_or_mode_state": before_command_count == after_command_count and before_mode_count == after_mode_count,
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
    failures.extend(f"protected lower-layer dirty during milestone BJ: {hit}" for hit in protected_dirty_hits)

    payload = {
        "ok": not failures,
        "phase": "phase4a_autotrade_milestone_bj_observer_run_latest_blocked_visibility_guard",
        "status": "closed" if not failures else "open",
        "contract": {
            "observer_run_summary_latest_blocked_fields_present": checks["summary_fields_present"],
            "summary_exposes_latest_blocked_run": checks["summary_exposes_latest_blocked_run"],
            "ui_observer_runs_displays_latest_blocked_fields": checks["ui_observer_runs_displays_latest_blocked_fields"],
            "ui_observer_run_status_read_only_no_runner_no_broker": checks["ui_observer_run_status_read_only"],
            "render_did_not_append_observer_runs": checks["render_did_not_append_observer_runs"],
            "protected_lower_layers_untouched": not protected_dirty_hits,
        },
        "summary": summary.to_dict(),
        "before_observer_rows": before_observer_rows,
        "after_observer_rows": after_observer_rows,
        "before_command_count": before_command_count,
        "after_command_count": after_command_count,
        "before_mode_count": before_mode_count,
        "after_mode_count": after_mode_count,
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
