# path: ./tools/test_phase4a_prediction_system_ps_q18af_schema_probe_guard.py
# desc: Focused guard for PS-Q18AF bounded JSON schema probe.

from __future__ import annotations

import ast
import json
import subprocess
import sys
from pathlib import Path

BTCTS_SRC = Path(__file__).resolve().parents[1] / "btcts_next" / "src"
if str(BTCTS_SRC) not in sys.path:
    sys.path.insert(0, str(BTCTS_SRC))

from btcts.apps.operator_ui.prediction_warroom.sources.latest_prediction_summary_widget_q18af_schema_probe import FALSE_BOUNDARIES, LATEST_PREDICTION_SUMMARY_WIDGET_Q18AF_SCHEMA_PROBE_ACK, TRUE_BOUNDARIES  # noqa: E402
from btcts.apps.operator_ui.prediction_warroom.presenters.latest_prediction_summary_widget_q18af_schema_probe_rows import build_latest_prediction_summary_widget_q18af_schema_probe_result_packet  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parents[1]
SOURCE = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/prediction_warroom/sources/latest_prediction_summary_widget_q18af_schema_probe.py"
PRESENTER = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/prediction_warroom/presenters/latest_prediction_summary_widget_q18af_schema_probe_rows.py"
UNIT = REPO_ROOT / "tools/test_phase4a_prediction_system_ps_q18af_latest_prediction_summary_widget_schema_probe.py"
DOC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q18AF_LATEST_PREDICTION_SUMMARY_WIDGET_SCHEMA_PROBE_2026-06-24.md"
EXPECTED_DIRTY = {
    "btcts_next/src/btcts/apps/operator_ui/prediction_warroom/sources/latest_prediction_summary_widget_q18af_schema_probe.py",
    "btcts_next/src/btcts/apps/operator_ui/prediction_warroom/presenters/latest_prediction_summary_widget_q18af_schema_probe_rows.py",
    "docs/strategy/PREDICTION_SYSTEM_PS_Q18AF_LATEST_PREDICTION_SUMMARY_WIDGET_SCHEMA_PROBE_2026-06-24.md",
    "tools/test_phase4a_prediction_system_ps_q18af_close_guard.py",
    "tools/test_phase4a_prediction_system_ps_q18af_latest_prediction_summary_widget_schema_probe.py",
    "tools/test_phase4a_prediction_system_ps_q18af_schema_probe_guard.py",
}


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8-sig")


def _dirty_paths() -> set[str]:
    proc = subprocess.run(["git", "status", "--short"], cwd=REPO_ROOT, text=True, capture_output=True, check=True)
    paths: set[str] = set()
    for line in proc.stdout.splitlines():
        if line.strip():
            rel = line[3:].replace(chr(92), "/")
            if "/__pycache__/" not in rel and not rel.endswith(".pyc"):
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
    for required in ("path.read_bytes()", "json.loads", "path.stat().st_size", "max_schema_probe_bytes"):
        if required not in source_text:
            failures.append(f"missing bounded schema probe marker: {required}")
    for forbidden in ("open(", "write_text(", "write_bytes(", "glob(", "rglob(", "send_order(", "create_order(", "render_latest_prediction_summary_widget("):
        if forbidden in source_text:
            failures.append(f"forbidden token in source: {forbidden}")
    packet = build_latest_prediction_summary_widget_q18af_schema_probe_result_packet(
        execute_schema_probe=True,
        explicit_ack=LATEST_PREDICTION_SUMMARY_WIDGET_Q18AF_SCHEMA_PROBE_ACK,
    )
    if packet.get("ok") is not True:
        failures.append(f"schema probe packet should be ok: {packet}")
    if packet.get("source_artifact_schema_valid") is not True:
        failures.append("source artifact schema must be valid")
    if packet.get("schema_probe_row_count") != 12:
        failures.append("expected 12 schema probe rows")
    for key in TRUE_BOUNDARIES:
        if packet.get(key) is not True:
            failures.append(f"{key} must be true")
    for key in FALSE_BOUNDARIES:
        if packet.get(key) is not False:
            failures.append(f"{key} must stay false")
    doc_text = _read(DOC) if DOC.exists() else ""
    for marker in ("PS-Q18AF", "source_artifact_schema_valid=true", "schema_probe_file_read_invoked=true", "actual_source_read_invoked=false", "Next: actual source read handoff or payload-to-widget props mapping preflight"):
        if marker not in doc_text:
            failures.append(f"missing doc marker: {marker}")
    dirty = _dirty_paths()
    unexpected = dirty - EXPECTED_DIRTY
    missing = EXPECTED_DIRTY - dirty
    if unexpected:
        failures.append(f"unexpected dirty paths: {sorted(unexpected)}")
    if missing:
        failures.append(f"missing expected dirty paths: {sorted(missing)}")
    result = {"ok": not failures, "guard": "ps_q18af_schema_probe_guard", "dirty_paths": sorted(dirty), "unexpected_dirty": sorted(unexpected), "missing_dirty": sorted(missing), "failures": failures, "record_count": packet.get("record_count")}
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if not failures else 1


def test_ps_q18af_schema_probe_guard() -> None:
    assert main_guard() == 0


if __name__ == "__main__":
    raise SystemExit(main_guard())
