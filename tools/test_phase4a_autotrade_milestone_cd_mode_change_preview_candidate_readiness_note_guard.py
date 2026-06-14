# path: ./tools/test_phase4a_autotrade_milestone_cd_mode_change_preview_candidate_readiness_note_guard.py
# desc: Guard Mode Change Apply Preview surfaces candidate command readiness note context. Read-only; no append/runner/broker.

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

from btcts.autotrade.execution import default_command_ledger_path, default_mode_state_ledger_path, read_command_ledger, read_mode_state_records, preview_latest_mode_change_command_apply_with_readiness_recheck  # noqa: E402
from btcts.autotrade.runtime_paths import ENV_AUTOTRADE_RUNTIME_ROOT  # noqa: E402

APPLIER_FILE = REPO_ROOT / "btcts_next/src/btcts/autotrade/execution/mode_command_applier.py"
UI_FILE = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/views/autotrade_page.py"
PROTECTED_PREFIXES = (
    "btcts_next/src/btcts/collector_vnext/",
    "btcts_next/src/btcts/ingestion/",
    "btcts_next/src/btcts/processing/l3_market_semantics/",
    "btcts_next/src/btcts/processing/l4_consumer_models/",
)
CANDIDATE_FIELDS = (
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
EXPECTED_NOTE_BLOCKED_BY = [
    "observer_run_latest_blocked_for_live_target",
    "mode_off",
    "mode_runtime_gate_blocked_shadow_decision_append",
]
EXPECTED_OBSERVER_BLOCKED_BY = [
    "mode_off",
    "mode_runtime_gate_blocked_shadow_decision_append",
]
EXPECTED_WARNINGS = ["candidate_note_is_persisted_snapshot", "readiness_recheck_may_differ"]
FORBIDDEN_PREVIEW_TOKENS = (
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
FORBIDDEN_UI_STATUS_TOKENS = (
    "append_mode_state_record",
    "append_observer_run_record",
    "validate_and_append_command",
    "append_command_ledger_record",
    "submit_mode_change_command_request",
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


class FakeColumn:
    def __init__(self, owner: "FakeStreamlit | None" = None) -> None:
        self.owner = owner

    def metric(self, *args: Any, **kwargs: Any) -> None:
        if self.owner is not None:
            self.owner.metric_count += 1
        return None


class FakeStreamlit(types.ModuleType):
    def __init__(self) -> None:
        super().__init__("streamlit")
        self.__path__ = []
        self.session_state: dict[str, Any] = {}
        self.metric_count = 0
        self.subheaders: list[str] = []

    def subheader(self, text: str, *args: Any, **kwargs: Any) -> None:
        self.subheaders.append(str(text))
        return None

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


def readiness_note() -> str:
    return json.dumps(
        {
            "kind": "autotrade.mode_change_readiness_snapshot",
            "ready": False,
            "current_mode": "ARMED_DRY_RUN",
            "target_mode": "LIVE_MIN_SIZE",
            "blocked_by": EXPECTED_NOTE_BLOCKED_BY,
            "warnings": EXPECTED_WARNINGS,
            "health_state": "warn",
            "observer_run_fresh": True,
            "observer_latest_run_id": "obs_cd_candidate_note",
            "observer_latest_blocked_by": EXPECTED_OBSERVER_BLOCKED_BY,
            "observer_latest_would_send_to_broker": False,
            "observer_latest_bounded": True,
            "runtime_live_ready": True,
            "mode_changed": False,
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
        "blocked_by": [],
        "command": {
            "command_id": command_id,
            "command_type": "REQUEST_MODE_CHANGE",
            "requested_by": "operator_ui",
            "requested_at": now_z(-10),
            "current_mode": "ARMED_DRY_RUN",
            "target": "LIVE_MIN_SIZE",
            "confirmation": True,
            "reason_codes": ["guard", "candidate_readiness_note"],
            "note": readiness_note(),
            "confirmation_required": True,
        },
    }


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(json.dumps(row, ensure_ascii=False, sort_keys=True) for row in rows) + "\n", encoding="utf-8")


def main() -> int:
    failures: list[str] = []
    original_runtime = os.environ.get(ENV_AUTOTRADE_RUNTIME_ROOT)
    previous_streamlit = sys.modules.get("streamlit")
    previous_components = sys.modules.get("streamlit.components")
    previous_components_v1 = sys.modules.get("streamlit.components.v1")
    fake_st = FakeStreamlit()
    hot_root = REPO_ROOT / "tmp/btc_ts_mode_change_preview_candidate_readiness_note_hot"
    render_exception = None
    import_exception = None
    before_command_count = -1
    after_preview_command_count = -2
    after_render_command_count = -3
    before_mode_count = -1
    after_preview_mode_count = -2
    after_render_mode_count = -3
    try:
        os.environ[ENV_AUTOTRADE_RUNTIME_ROOT] = str(hot_root)
        command_path = default_command_ledger_path(ensure=True)
        mode_state_path = default_mode_state_ledger_path(ensure=True)
        if command_path.exists():
            command_path.unlink()
        if mode_state_path.exists():
            mode_state_path.unlink()
        write_jsonl(command_path, [command_row("cmd_cd_candidate_live_request")])
        before_command_count = len(read_command_ledger(command_path))
        before_mode_count = len(read_mode_state_records(mode_state_path).rows)
        preview = preview_latest_mode_change_command_apply_with_readiness_recheck(max_lines=100, max_observer_run_age_sec=120, allow_warnings=False)
        after_preview_command_count = len(read_command_ledger(command_path))
        after_preview_mode_count = len(read_mode_state_records(mode_state_path).rows)
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
                module._render_mode_change_apply_preview_status()
            except Exception as exc:
                render_exception = repr(exc)
        after_render_command_count = len(read_command_ledger(command_path))
        after_render_mode_count = len(read_mode_state_records(mode_state_path).rows)
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

    preview_data = preview.to_dict()
    applier_text = APPLIER_FILE.read_text(encoding="utf-8")
    preview_source = function_source(APPLIER_FILE, "preview_latest_mode_change_command_apply_with_readiness_recheck")
    ui_source = function_source(UI_FILE, "_render_mode_change_apply_preview_status")
    checks = {
        "preview_dataclass_has_candidate_readiness_note_fields": all(field in applier_text for field in CANDIDATE_FIELDS),
        "preview_surfaces_candidate_readiness_note_context": preview_data.get("command_id") == "cmd_cd_candidate_live_request" and preview_data.get("candidate_readiness_note_present") is True and preview_data.get("candidate_readiness_ready") is False and preview_data.get("candidate_readiness_current_mode") == "ARMED_DRY_RUN" and preview_data.get("candidate_readiness_target_mode") == "LIVE_MIN_SIZE" and tuple(preview_data.get("candidate_readiness_blocked_by") or ()) == tuple(EXPECTED_NOTE_BLOCKED_BY) and tuple(preview_data.get("candidate_readiness_warnings") or ()) == tuple(EXPECTED_WARNINGS) and preview_data.get("candidate_readiness_health_state") == "warn",
        "preview_surfaces_candidate_observer_note_details": preview_data.get("candidate_readiness_observer_latest_run_id") == "obs_cd_candidate_note" and tuple(preview_data.get("candidate_readiness_observer_latest_blocked_by") or ()) == tuple(EXPECTED_OBSERVER_BLOCKED_BY) and preview_data.get("candidate_readiness_observer_latest_would_send_to_broker") is False and preview_data.get("candidate_readiness_observer_latest_bounded") is True,
        "preview_keeps_recheck_result_separate": preview_data.get("readiness") is not None and preview_data.get("would_reject_by_readiness") is True and preview_data.get("readiness_ready") is False,
        "ui_preview_displays_candidate_readiness_note_fields": all(field in ui_source for field in CANDIDATE_FIELDS),
        "preview_read_only_no_append_runner_broker": bool(preview_source) and not any(token in preview_source for token in FORBIDDEN_PREVIEW_TOKENS),
        "ui_preview_read_only_no_append_runner_broker": bool(ui_source) and not any(token in ui_source for token in FORBIDDEN_UI_STATUS_TOKENS),
        "preview_did_not_append_command_or_mode_state": before_command_count == 1 and after_preview_command_count == before_command_count and before_mode_count == 0 and after_preview_mode_count == before_mode_count,
        "render_did_not_append_command_or_mode_state": before_command_count == 1 and after_render_command_count == before_command_count and before_mode_count == 0 and after_render_mode_count == before_mode_count,
        "render_smoke_ok": import_exception is None and render_exception is None and "Mode Change Apply Preview" in fake_st.subheaders,
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
    failures.extend(f"protected lower-layer dirty during milestone CD: {hit}" for hit in protected_dirty_hits)

    payload = {
        "ok": not failures,
        "phase": "phase4a_autotrade_milestone_cd_mode_change_preview_candidate_readiness_note_guard",
        "status": "closed" if not failures else "open",
        "contract": {
            "preview_dataclass_has_candidate_readiness_note_fields": checks["preview_dataclass_has_candidate_readiness_note_fields"],
            "preview_surfaces_candidate_readiness_note_context": checks["preview_surfaces_candidate_readiness_note_context"],
            "preview_surfaces_candidate_observer_note_details": checks["preview_surfaces_candidate_observer_note_details"],
            "preview_keeps_recheck_result_separate": checks["preview_keeps_recheck_result_separate"],
            "ui_preview_displays_candidate_readiness_note_fields": checks["ui_preview_displays_candidate_readiness_note_fields"],
            "preview_read_only_no_append_runner_broker": checks["preview_read_only_no_append_runner_broker"],
            "ui_preview_read_only_no_append_runner_broker": checks["ui_preview_read_only_no_append_runner_broker"],
            "preview_did_not_append_command_or_mode_state": checks["preview_did_not_append_command_or_mode_state"],
            "render_did_not_append_command_or_mode_state": checks["render_did_not_append_command_or_mode_state"],
            "protected_lower_layers_untouched": not protected_dirty_hits,
        },
        "preview": preview_data,
        "before_command_count": before_command_count,
        "after_preview_command_count": after_preview_command_count,
        "after_render_command_count": after_render_command_count,
        "before_mode_count": before_mode_count,
        "after_preview_mode_count": after_preview_mode_count,
        "after_render_mode_count": after_render_mode_count,
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
