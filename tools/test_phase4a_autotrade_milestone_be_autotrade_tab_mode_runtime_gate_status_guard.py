# path: ./tools/test_phase4a_autotrade_milestone_be_autotrade_tab_mode_runtime_gate_status_guard.py
# desc: Guard AutoTrade UI displays read-only mode runtime gate status. No runner execution, no ledger append, no broker.

from __future__ import annotations

import ast
import importlib
import json
import os
import subprocess
import sys
import types
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = REPO_ROOT / "btcts_next/src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from btcts.autotrade.execution import append_mode_state_record, default_mode_state_ledger_path, read_command_ledger, read_mode_state_records  # noqa: E402
from btcts.autotrade.execution.mode_state import ModeStateRecord  # noqa: E402
from btcts.autotrade.modes import AutoTradeMode  # noqa: E402
from btcts.autotrade.runtime_paths import ENV_AUTOTRADE_RUNTIME_ROOT  # noqa: E402

UI_FILE = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/views/autotrade_page.py"
PROTECTED_PREFIXES = (
    "btcts_next/src/btcts/collector_vnext/",
    "btcts_next/src/btcts/ingestion/",
    "btcts_next/src/btcts/processing/l3_market_semantics/",
    "btcts_next/src/btcts/processing/l4_consumer_models/",
)
REQUIRED_FIELDS = (
    "current_mode",
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
FORBIDDEN_STATUS_TOKENS = (
    "append_mode_state_record",
    "append_command_ledger_record",
    "validate_and_append_command",
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


def function_source(path: Path, function_name: str) -> str:
    text = path.read_text(encoding="utf-8")
    tree = ast.parse(text)
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == function_name:
            return ast.get_source_segment(text, node) or ""
    return ""


def write_mode(path: Path, mode: AutoTradeMode) -> None:
    if path.exists():
        path.unlink()
    append_mode_state_record(
        path,
        ModeStateRecord(
            current_mode=mode,
            previous_mode=AutoTradeMode.OFF,
            changed_at="2026-06-13T07:10:00Z",
            source_command_id=f"cmd_be_{mode.value.lower()}",
            requested_by="guard",
            accepted=True,
            mode_changed=mode != AutoTradeMode.OFF,
            reason_codes=("guard", "ui_runtime_gate"),
            blocked_by=(),
            would_send_to_broker=False,
        ),
    )


def main() -> int:
    failures: list[str] = []
    original_runtime = os.environ.get(ENV_AUTOTRADE_RUNTIME_ROOT)
    previous_streamlit = sys.modules.get("streamlit")
    previous_components = sys.modules.get("streamlit.components")
    previous_components_v1 = sys.modules.get("streamlit.components.v1")
    fake_st = FakeStreamlit()
    hot_root = REPO_ROOT / "tmp/btc_ts_ui_mode_runtime_gate_hot"
    render_exception = None
    import_exception = None
    before_mode_count = -1
    after_mode_count = -2
    before_command_count = -1
    after_command_count = -2
    try:
        os.environ[ENV_AUTOTRADE_RUNTIME_ROOT] = str(hot_root)
        mode_path = default_mode_state_ledger_path(ensure=True)
        write_mode(mode_path, AutoTradeMode.OFF)
        command_path = hot_root / "autotrade/commands/command_requests.jsonl"
        command_path.parent.mkdir(parents=True, exist_ok=True)
        command_path.write_text("", encoding="utf-8")
        before_mode_count = len(read_mode_state_records(mode_path, max_lines=100).rows)
        before_command_count = len(read_command_ledger(command_path))
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
        after_mode_count = len(read_mode_state_records(mode_path, max_lines=100).rows)
        after_command_count = len(read_command_ledger(command_path))
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

    text = UI_FILE.read_text(encoding="utf-8")
    status_source = function_source(UI_FILE, "_render_mode_runtime_gate_status")
    render_source = function_source(UI_FILE, "render")
    checks = {
        "ui_imports_mode_runtime_gate": "from btcts.autotrade.mode_runtime_gate import build_mode_runtime_gate" in text,
        "ui_has_mode_runtime_gate_panel": bool(status_source) and "Mode Runtime Gate" in status_source,
        "ui_displays_runtime_gate_fields": all(token in status_source for token in REQUIRED_FIELDS),
        "ui_mode_runtime_gate_status_read_only": bool(status_source) and not any(token in status_source for token in FORBIDDEN_STATUS_TOKENS),
        "ui_renders_gate_after_mode_state": "_render_mode_state_status()" in render_source and "_render_mode_runtime_gate_status()" in render_source and render_source.index("_render_mode_state_status()") < render_source.index("_render_mode_runtime_gate_status()"),
        "render_smoke_ok": import_exception is None and render_exception is None and "Mode Runtime Gate" in fake_st.subheaders,
        "render_did_not_append_mode_state": before_mode_count == 1 and after_mode_count == before_mode_count,
        "render_did_not_append_commands": before_command_count == 0 and after_command_count == before_command_count,
        "fake_streamlit_exercised": fake_st.metric_call_count >= 55 and fake_st.button_call_count >= 4 and fake_st.checkbox_call_count >= 6,
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
    failures.extend(f"protected lower-layer dirty during milestone BE: {hit}" for hit in protected_dirty_hits)

    payload = {
        "ok": not failures,
        "phase": "phase4a_autotrade_milestone_be_autotrade_tab_mode_runtime_gate_status_guard",
        "status": "closed" if not failures else "open",
        "contract": {
            "autotrade_tab_mode_runtime_gate_present": checks["ui_has_mode_runtime_gate_panel"],
            "runtime_gate_fields_displayed": checks["ui_displays_runtime_gate_fields"],
            "mode_runtime_gate_status_read_only_no_runner_no_broker": checks["ui_mode_runtime_gate_status_read_only"],
            "render_did_not_append_mode_state": checks["render_did_not_append_mode_state"],
            "render_did_not_append_commands": checks["render_did_not_append_commands"],
            "protected_lower_layers_untouched": not protected_dirty_hits,
        },
        "subheaders": fake_st.subheaders,
        "metric_call_count": fake_st.metric_call_count,
        "button_call_count": fake_st.button_call_count,
        "checkbox_call_count": fake_st.checkbox_call_count,
        "before_mode_count": before_mode_count,
        "after_mode_count": after_mode_count,
        "before_command_count": before_command_count,
        "after_command_count": after_command_count,
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
