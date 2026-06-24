# path: ./tools/test_phase4a_prediction_system_ps_q18ad_schema_validation_gate_guard.py
# desc: Focused guard for PS-Q18AD latest_prediction_summary_widget schema validation gate blocked by missing source.

from __future__ import annotations

import ast
import json
import subprocess
import sys
from pathlib import Path

BTCTS_SRC = Path(__file__).resolve().parents[1] / "btcts_next" / "src"
if str(BTCTS_SRC) not in sys.path:
    sys.path.insert(0, str(BTCTS_SRC))

from btcts.apps.operator_ui.prediction_warroom.sources.latest_prediction_summary_widget_q18ad_schema_validation_gate import FALSE_BOUNDARIES, TRUE_BOUNDARIES  # noqa: E402
from btcts.apps.operator_ui.prediction_warroom.presenters.latest_prediction_summary_widget_q18ad_schema_validation_gate_rows import build_latest_prediction_summary_widget_q18ad_schema_validation_gate_result_packet  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parents[1]
SOURCE = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/prediction_warroom/sources/latest_prediction_summary_widget_q18ad_schema_validation_gate.py"
PRESENTER = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/prediction_warroom/presenters/latest_prediction_summary_widget_q18ad_schema_validation_gate_rows.py"
UNIT = REPO_ROOT / "tools/test_phase4a_prediction_system_ps_q18ad_latest_prediction_summary_widget_schema_validation_gate.py"
DOC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q18AD_LATEST_PREDICTION_SUMMARY_WIDGET_SCHEMA_VALIDATION_GATE_2026-06-24.md"
EXPECTED_DIRTY = {
    "btcts_next/src/btcts/apps/operator_ui/prediction_warroom/sources/latest_prediction_summary_widget_q18ad_schema_validation_gate.py",
    "btcts_next/src/btcts/apps/operator_ui/prediction_warroom/presenters/latest_prediction_summary_widget_q18ad_schema_validation_gate_rows.py",
    "docs/strategy/PREDICTION_SYSTEM_PS_Q18AD_LATEST_PREDICTION_SUMMARY_WIDGET_SCHEMA_VALIDATION_GATE_2026-06-24.md",
    "tools/test_phase4a_prediction_system_ps_q18ad_close_guard.py",
    "tools/test_phase4a_prediction_system_ps_q18ad_latest_prediction_summary_widget_schema_validation_gate.py",
    "tools/test_phase4a_prediction_system_ps_q18ad_schema_validation_gate_guard.py",
}


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8-sig")


def _is_noise_path(rel: str) -> bool:
    return "/__pycache__/" in rel or rel.endswith(".pyc")


def _dirty_paths() -> set[str]:
    proc = subprocess.run(["git", "status", "--short"], cwd=REPO_ROOT, text=True, capture_output=True, check=True)
    paths: set[str] = set()
    for line in proc.stdout.splitlines():
        if not line.strip():
            continue
        rel = line[3:].replace(chr(92), "/")
        absolute = REPO_ROOT / rel
        if rel.endswith("/") and absolute.exists():
            for child in absolute.rglob("*"):
                if child.is_file():
                    child_rel = child.relative_to(REPO_ROOT).as_posix()
                    if not _is_noise_path(child_rel):
                        paths.add(child_rel)
        elif not _is_noise_path(rel):
            paths.add(rel)
    return paths


def main_guard() -> int:
    failures: list[str] = []
    for path in (SOURCE, PRESENTER, UNIT, DOC):
        if not path.exists():
            failures.append(f"missing file: {path.relative_to(REPO_ROOT)}")
            continue
        if path.suffix == ".py":
            try:
                ast.parse(_read(path), filename=str(path))
            except SyntaxError as exc:
                failures.append(f"syntax failed: {path.relative_to(REPO_ROOT)}: {exc}")
    source_text = _read(SOURCE) if SOURCE.exists() else ""
    for forbidden in ("Path(", "open(", "read_text(", "read_bytes(", "write_text(", "write_bytes(", ".read(", "json.load", "json.loads", "exists(", "stat(", "glob(", "rglob(", "send_order(", "create_order("):
        if forbidden in source_text:
            failures.append(f"forbidden token in source: {forbidden}")
    packet = build_latest_prediction_summary_widget_q18ad_schema_validation_gate_result_packet()
    if packet.get("ok") is not True:
        failures.append(f"schema validation gate packet should be ok: {packet}")
    if packet.get("source_artifact_exists_result_state") != "missing":
        failures.append("source artifact exists result state must be missing")
    if packet.get("schema_validation_blocked") is not True:
        failures.append("schema validation must be blocked")
    if packet.get("schema_validation_gate_row_count") != 12:
        failures.append("expected 12 schema validation gate rows")
    for key in TRUE_BOUNDARIES:
        if packet.get(key) is not True:
            failures.append(f"{key} must be true")
    for key in FALSE_BOUNDARIES:
        if packet.get(key) is not False:
            failures.append(f"{key} must stay false")
    doc_text = _read(DOC) if DOC.exists() else ""
    for marker in ("PS-Q18AD", "schema_validation_blocked=true", "source_artifact_schema_checked=false", "actual_source_read_invoked=false", "filesystem_exists_check_reexecuted=false", "Next: source availability repair"):
        if marker not in doc_text:
            failures.append(f"missing doc marker: {marker}")
    dirty = _dirty_paths()
    unexpected = dirty - EXPECTED_DIRTY
    missing = EXPECTED_DIRTY - dirty
    if unexpected:
        failures.append(f"unexpected dirty paths: {sorted(unexpected)}")
    if missing:
        failures.append(f"missing expected dirty paths: {sorted(missing)}")
    result = {"ok": not failures, "guard": "ps_q18ad_schema_validation_gate_guard", "dirty_paths": sorted(dirty), "unexpected_dirty": sorted(unexpected), "missing_dirty": sorted(missing), "failures": failures}
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if not failures else 1


def test_ps_q18ad_schema_validation_gate_guard() -> None:
    assert main_guard() == 0


if __name__ == "__main__":
    raise SystemExit(main_guard())
