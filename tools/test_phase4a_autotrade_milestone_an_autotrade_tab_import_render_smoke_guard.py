# path: ./tools/test_phase4a_autotrade_milestone_an_autotrade_tab_import_render_smoke_guard.py
# desc: Smoke guard AutoTrade tab import/render with fake Streamlit. Buttons are false; no append/broker/runtime loop.

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

from btcts.autotrade.execution import read_command_ledger  # noqa: E402
from btcts.autotrade.runtime_paths import ENV_AUTOTRADE_RUNTIME_ROOT  # noqa: E402

UI_FILE = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/views/autotrade_page.py"
PROTECTED_PREFIXES = (
    "btcts_next/src/btcts/collector_vnext/",
    "btcts_next/src/btcts/ingestion/",
    "btcts_next/src/btcts/processing/l3_market_semantics/",
    "btcts_next/src/btcts/processing/l4_consumer_models/",
)
STATUS_FUNCTIONS = (
    "_render_command_request_status",
    "_render_runtime_health_status",
    "_render_observer_run_status",
    "_render_shadow_decision_status",
    "_render_forecast_calibration_status",
)
STATUS_FORBIDDEN_TOKENS = (
    "submit_mode_change_command_request",
    "validate_and_append_command",
    "append_command_ledger_record",
    "st.button(",
    "run_observer_cycle_bounded",
    "run_observer_cycle_once",
    "run_shadow_cycle_once",
    "run_shadow_cycle_bounded",
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
        self.__path__ = []  # make fake streamlit package-like for streamlit.components.v1 imports
        self.session_state: dict[str, Any] = {}
        self.button_call_count = 0
        self.checkbox_call_count = 0
        self.selectbox_call_count = 0

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


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(json.dumps(row, ensure_ascii=False, sort_keys=True) for row in rows) + "\n", encoding="utf-8")


def command_row(command_id: str, *, command_type: str, accepted: bool, target: str | None, blocked_by: list[str]) -> dict[str, Any]:
    return {
        "ledger_event": "autotrade.command_request_validated",
        "command_id": command_id,
        "accepted": accepted,
        "blocked_by": blocked_by,
        "command": {
            "command_id": command_id,
            "command_type": command_type,
            "requested_by": "guard",
            "requested_at": "2026-06-13T04:20:00Z",
            "current_mode": "SHADOW",
            "target": target,
            "confirmation": True,
            "reason_codes": ["guard"],
            "note": "{}",
            "confirmation_required": False,
        },
    }


def observer_row(finished_at: str) -> dict[str, Any]:
    return {
        "run_id": "obs_render_smoke",
        "started_at": finished_at,
        "finished_at": finished_at,
        "requested_cycles": 2,
        "completed_cycles": 2,
        "appended_shadow_decision_count": 1,
        "appended_forecast_outcome_count": 1,
        "duplicate_snapshot_skipped_count": 1,
        "skip_duplicate_snapshot": True,
        "blocked_by": [],
        "would_send_to_broker": False,
        "bounded": True,
        "source": "autotrade.observer_cycle_bounded",
    }


def shadow_row() -> dict[str, Any]:
    return {
        "decision_id": "dec_render_smoke",
        "mode": "SHADOW",
        "snapshot_id": "snap_render_smoke",
        "forecast_id": "fcst_render_smoke",
        "parameter_set_id": "params_fx_balanced_v0_1",
        "logic_version": "autotrade_logic_v0_1",
        "forecast_5m": {"forecast_id": "fcst_render_smoke", "forecast_direction": "down", "confidence": "medium"},
        "candidate": {"action": "NO_NEW_ENTRY"},
        "risk_gate": {"allowed": False, "executable": False},
        "final_action": "WAIT",
        "reason_codes": ["render_smoke_guard"],
        "blocked_by": [],
        "would_order": None,
    }


def outcome_row() -> dict[str, Any]:
    return {
        "forecast_id": "fcst_render_smoke",
        "parameter_set_id": "params_fx_balanced_v0_1",
        "logic_version": "autotrade_logic_v0_1",
        "source_snapshot_id": "snap_render_smoke",
        "target_ts": "2026-06-13T02:00:00Z",
        "actual_snapshot_id": "actual_render_smoke",
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
    hot_root = REPO_ROOT / "tmp/btc_ts_autotrade_ui_smoke_hot"
    command_path = hot_root / "autotrade/commands/command_requests.jsonl"
    now = datetime.now(timezone.utc).replace(microsecond=0)
    fresh_ts = (now - timedelta(seconds=10)).isoformat().replace("+00:00", "Z")
    render_exception = None
    import_exception = None
    before_count = -1
    after_count = -2
    try:
        os.environ[ENV_AUTOTRADE_RUNTIME_ROOT] = str(hot_root)
        write_jsonl(command_path, [command_row("cmd_render_smoke", command_type="REQUEST_HALT_NEW", accepted=True, target="halt_new", blocked_by=[])])
        write_jsonl(hot_root / "autotrade/decisions/observer_runs.jsonl", [observer_row(fresh_ts)])
        write_jsonl(hot_root / "autotrade/decisions/shadow_decisions.jsonl", [shadow_row()])
        write_jsonl(hot_root / "autotrade/decisions/forecast_outcomes.jsonl", [outcome_row()])
        before_count = len(read_command_ledger(command_path))
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
        except Exception as exc:  # pragma: no cover - guard reports it
            import_exception = repr(exc)
            module = None
        if module is not None:
            try:
                module.render()
            except Exception as exc:  # pragma: no cover - guard reports it
                render_exception = repr(exc)
        after_count = len(read_command_ledger(command_path))
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

    status_sources = {name: function_source(UI_FILE, name) for name in STATUS_FUNCTIONS}
    status_sources_present = all(bool(source) for source in status_sources.values())
    status_read_only = status_sources_present and all(
        not any(token in source for token in STATUS_FORBIDDEN_TOKENS) for source in status_sources.values()
    )
    checks = {
        "autotrade_page_imports": import_exception is None,
        "autotrade_page_render_smoke": import_exception is None and render_exception is None,
        "fake_streamlit_exercised": fake_st.button_call_count >= 4 and fake_st.checkbox_call_count >= 2 and fake_st.selectbox_call_count >= 2,
        "render_did_not_append_commands": before_count == 1 and after_count == before_count,
        "status_functions_read_only": status_read_only,
        "registry_snapshot_rendered_without_error": render_exception is None and "Registry snapshot" in UI_FILE.read_text(encoding="utf-8"),
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
    failures.extend(f"protected lower-layer dirty during milestone AN: {hit}" for hit in protected_dirty_hits)

    payload = {
        "ok": not failures,
        "phase": "phase4a_autotrade_milestone_an_autotrade_tab_import_render_smoke_guard",
        "status": "closed" if not failures else "open",
        "contract": {
            "autotrade_page_imports": checks["autotrade_page_imports"],
            "autotrade_page_render_smoke": checks["autotrade_page_render_smoke"],
            "render_did_not_append_commands": checks["render_did_not_append_commands"],
            "status_functions_read_only": checks["status_functions_read_only"],
            "registry_snapshot_rendered_without_error": checks["registry_snapshot_rendered_without_error"],
            "protected_lower_layers_untouched": not protected_dirty_hits,
        },
        "button_call_count": fake_st.button_call_count,
        "checkbox_call_count": fake_st.checkbox_call_count,
        "selectbox_call_count": fake_st.selectbox_call_count,
        "command_count_before": before_count,
        "command_count_after": after_count,
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
