# path: ./tools/test_phase4a_autotrade_milestone_bq_mode_change_request_readiness_observer_visibility_guard.py
# desc: Guard UI mode-change request result includes readiness observer latest blocked details. Existing command append only; no mode/observer append, no runner/broker.

from __future__ import annotations

import ast
import importlib
import json
import os
import subprocess
import sys
import types
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = REPO_ROOT / "btcts_next/src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from btcts.autotrade.execution import append_mode_state_record, default_command_ledger_path, default_mode_state_ledger_path, read_command_ledger, read_mode_state_records  # noqa: E402
from btcts.autotrade.execution.mode_state import ModeStateRecord  # noqa: E402
from btcts.autotrade.ledger import ObserverRunRecord, append_observer_run_record, default_observer_run_ledger_path  # noqa: E402
from btcts.autotrade.modes import AutoTradeMode  # noqa: E402
from btcts.autotrade.runtime_paths import ENV_AUTOTRADE_RUNTIME_ROOT  # noqa: E402

UI_FILE = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/views/autotrade_page.py"
PROTECTED_PREFIXES = (
    "btcts_next/src/btcts/collector_vnext/",
    "btcts_next/src/btcts/ingestion/",
    "btcts_next/src/btcts/processing/l3_market_semantics/",
    "btcts_next/src/btcts/processing/l4_consumer_models/",
)
READINESS_OBSERVER_FIELDS = (
    "observer_latest_run_id",
    "observer_latest_blocked_by",
    "observer_latest_would_send_to_broker",
    "observer_latest_bounded",
)
FORBIDDEN_TOKENS = (
    "append_mode_state_record",
    "append_observer_run_record",
    "run_observer_cycle_bounded",
    "run_observer_cycle_once",
    "run_shadow_cycle_once",
    "run_shadow_cycle_bounded",
    "resolve_due_shadow_forecast_outcomes",
    "run_latest_market_state_shadow_decision",
    "apply_latest_mode_change_command_once",
    "place_order(",
    "send_order(",
    "broker_order(",
    "private_api",
    "pybitflyer",
    "ccxt",
    "requests.post",
    "httpx.post",
)


class FakeStreamlit(types.ModuleType):
    def __init__(self) -> None:
        super().__init__("streamlit")
        self.__path__ = []
        self.session_state: dict[str, Any] = {}

    def __getattr__(self, name: str) -> Any:
        if name == "components":
            return types.SimpleNamespace(v1=types.SimpleNamespace(html=lambda *args, **kwargs: None))
        if name == "columns":
            return lambda count: [self for _ in range(int(count))]
        if name in {"button", "checkbox"}:
            return lambda *args, **kwargs: False
        if name == "selectbox":
            return lambda label, options, index=0, **kwargs: str(options[index]) if options else ""
        return lambda *args, **kwargs: None

    def __enter__(self) -> "FakeStreamlit":
        return self

    def __exit__(self, exc_type: object, exc: object, tb: object) -> bool:
        return False


def now_z() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def function_source(path: Path, function_name: str) -> str:
    text = path.read_text(encoding="utf-8")
    tree = ast.parse(text)
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == function_name:
            return ast.get_source_segment(text, node) or ""
    return ""


def seed_runtime() -> tuple[Path, Path, Path]:
    command_path = default_command_ledger_path(ensure=True)
    mode_state_path = default_mode_state_ledger_path(ensure=True)
    observer_path = default_observer_run_ledger_path(ensure=True)
    for path in (command_path, mode_state_path, observer_path):
        if path.exists():
            path.unlink()
    append_mode_state_record(
        mode_state_path,
        ModeStateRecord(
            current_mode=AutoTradeMode.ARMED_DRY_RUN,
            previous_mode=AutoTradeMode.PAPER_OR_REPLAY,
            changed_at=now_z(),
            source_command_id="cmd_bq_seed_armed",
            requested_by="guard",
            accepted=True,
            mode_changed=True,
            reason_codes=("guard", "seed_armed"),
            blocked_by=(),
            would_send_to_broker=False,
        ),
    )
    z = now_z()
    append_observer_run_record(
        observer_path,
        ObserverRunRecord(
            run_id="obs_bq_blocked_off",
            started_at=z,
            finished_at=z,
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
    return command_path, mode_state_path, observer_path


def main() -> int:
    failures: list[str] = []
    original_runtime = os.environ.get(ENV_AUTOTRADE_RUNTIME_ROOT)
    previous_streamlit = sys.modules.get("streamlit")
    previous_components = sys.modules.get("streamlit.components")
    previous_components_v1 = sys.modules.get("streamlit.components.v1")
    fake_st = FakeStreamlit()
    hot_root = REPO_ROOT / "tmp/btc_ts_mode_change_request_readiness_observer_visibility_hot"
    import_exception = None
    request_exception = None
    result: dict[str, Any] | None = None
    before_command_count = -1
    after_command_count = -2
    before_mode_count = -1
    after_mode_count = -2
    before_observer_count = -1
    after_observer_count = -2
    try:
        os.environ[ENV_AUTOTRADE_RUNTIME_ROOT] = str(hot_root)
        command_path, mode_state_path, observer_path = seed_runtime()
        before_command_count = len(read_command_ledger(command_path))
        before_mode_count = len(read_mode_state_records(mode_state_path, max_lines=100).rows)
        before_observer_count = len(observer_path.read_text(encoding="utf-8").splitlines())
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
                result = module._submit_mode_change_request(
                    current_mode=AutoTradeMode.ARMED_DRY_RUN.value,
                    target_mode=AutoTradeMode.LIVE_MIN_SIZE.value,
                    human_confirmed=True,
                    allow_warnings=True,
                )
            except Exception as exc:
                request_exception = repr(exc)
        after_command_count = len(read_command_ledger(command_path))
        after_mode_count = len(read_mode_state_records(mode_state_path, max_lines=100).rows)
        after_observer_count = len(observer_path.read_text(encoding="utf-8").splitlines())
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

    source = function_source(UI_FILE, "_submit_mode_change_request")
    readiness = (result or {}).get("readiness") if isinstance((result or {}).get("readiness"), dict) else {}
    observer_latest_blocked_by = tuple(readiness.get("observer_latest_blocked_by") or ())
    expected_observer_latest_blocked_by = (
        "mode_off",
        "mode_runtime_gate_blocked_shadow_decision_append",
        "mode_runtime_gate_blocked_forecast_outcome_resolution",
    )
    checks = {
        "mode_change_request_payload_has_observer_fields": all(field in source for field in READINESS_OBSERVER_FIELDS),
        "mode_change_request_result_exposes_observer_blocked": readiness.get("observer_latest_run_id") == "obs_bq_blocked_off" and observer_latest_blocked_by == expected_observer_latest_blocked_by and readiness.get("observer_latest_would_send_to_broker") is False and readiness.get("observer_latest_bounded") is True,
        "mode_change_request_rejected_by_readiness": result is not None and result.get("accepted") is False and "observer_run_latest_blocked_for_live_target" in tuple(result.get("blocked_by") or ()),
        "mode_change_request_appended_exactly_one_command": before_command_count == 0 and after_command_count == 1,
        "mode_change_request_did_not_append_mode_state": before_mode_count == 1 and after_mode_count == before_mode_count,
        "mode_change_request_did_not_append_observer_runs": before_observer_count == 1 and after_observer_count == before_observer_count,
        "no_runner_applier_or_broker_in_submit_helper": bool(source) and not any(token in source for token in FORBIDDEN_TOKENS),
    }
    failures.extend(f"check failed: {name}" for name, ok in checks.items() if not ok)
    if import_exception:
        failures.append(f"import_exception: {import_exception}")
    if request_exception:
        failures.append(f"request_exception: {request_exception}")

    protected_dirty_hits: list[str] = []
    status = subprocess.run(["git", "status", "--short"], cwd=REPO_ROOT, text=True, capture_output=True, check=True).stdout.splitlines()
    for line in status:
        rel = line[3:] if len(line) > 3 else line
        if any(rel.startswith(prefix) for prefix in PROTECTED_PREFIXES):
            protected_dirty_hits.append(line)
    failures.extend(f"protected lower-layer dirty during milestone BQ: {hit}" for hit in protected_dirty_hits)

    payload = {
        "ok": not failures,
        "phase": "phase4a_autotrade_milestone_bq_mode_change_request_readiness_observer_visibility_guard",
        "status": "closed" if not failures else "open",
        "contract": {
            "mode_change_request_payload_has_observer_fields": checks["mode_change_request_payload_has_observer_fields"],
            "mode_change_request_result_exposes_observer_blocked": checks["mode_change_request_result_exposes_observer_blocked"],
            "mode_change_request_rejected_by_readiness": checks["mode_change_request_rejected_by_readiness"],
            "mode_change_request_appended_exactly_one_command": checks["mode_change_request_appended_exactly_one_command"],
            "mode_change_request_did_not_append_mode_state": checks["mode_change_request_did_not_append_mode_state"],
            "mode_change_request_did_not_append_observer_runs": checks["mode_change_request_did_not_append_observer_runs"],
            "no_runner_applier_or_broker_in_submit_helper": checks["no_runner_applier_or_broker_in_submit_helper"],
            "protected_lower_layers_untouched": not protected_dirty_hits,
        },
        "result": result,
        "before_command_count": before_command_count,
        "after_command_count": after_command_count,
        "before_mode_count": before_mode_count,
        "after_mode_count": after_mode_count,
        "before_observer_count": before_observer_count,
        "after_observer_count": after_observer_count,
        "import_exception": import_exception,
        "request_exception": request_exception,
        "checks": checks,
        "protected_dirty_hits": protected_dirty_hits,
        "failures": failures,
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2, default=str))
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
