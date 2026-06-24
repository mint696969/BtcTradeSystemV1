# path: ./tools/test_phase4a_prediction_system_ps_q18ae_candidate_resolver_refresh_guard.py
# desc: Focused guard for PS-Q18AE latest_prediction_summary_widget candidate resolver refresh.

from __future__ import annotations

import ast
import json
import subprocess
import sys
from pathlib import Path

BTCTS_SRC = Path(__file__).resolve().parents[1] / "btcts_next" / "src"
if str(BTCTS_SRC) not in sys.path:
    sys.path.insert(0, str(BTCTS_SRC))

from btcts.apps.operator_ui.prediction_warroom.sources.latest_prediction_summary_widget_q18ae_candidate_resolver_refresh import FALSE_BOUNDARIES, LATEST_PREDICTION_SUMMARY_WIDGET_Q18AE_CANDIDATE_RESOLVER_REFRESH_ACK, TRUE_BOUNDARIES  # noqa: E402
from btcts.apps.operator_ui.prediction_warroom.presenters.latest_prediction_summary_widget_q18ae_candidate_resolver_refresh_rows import build_latest_prediction_summary_widget_q18ae_candidate_resolver_refresh_result_packet  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parents[1]
SOURCE = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/prediction_warroom/sources/latest_prediction_summary_widget_q18ae_candidate_resolver_refresh.py"
PRESENTER = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/prediction_warroom/presenters/latest_prediction_summary_widget_q18ae_candidate_resolver_refresh_rows.py"
UNIT = REPO_ROOT / "tools/test_phase4a_prediction_system_ps_q18ae_latest_prediction_summary_widget_candidate_resolver_refresh.py"
DOC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q18AE_LATEST_PREDICTION_SUMMARY_WIDGET_CANDIDATE_RESOLVER_REFRESH_2026-06-24.md"
EXPECTED_DIRTY = {
    "btcts_next/src/btcts/apps/operator_ui/prediction_warroom/sources/latest_prediction_summary_widget_q18ae_candidate_resolver_refresh.py",
    "btcts_next/src/btcts/apps/operator_ui/prediction_warroom/presenters/latest_prediction_summary_widget_q18ae_candidate_resolver_refresh_rows.py",
    "docs/strategy/PREDICTION_SYSTEM_PS_Q18AE_LATEST_PREDICTION_SUMMARY_WIDGET_CANDIDATE_RESOLVER_REFRESH_2026-06-24.md",
    "tools/test_phase4a_prediction_system_ps_q18ae_candidate_resolver_refresh_guard.py",
    "tools/test_phase4a_prediction_system_ps_q18ae_close_guard.py",
    "tools/test_phase4a_prediction_system_ps_q18ae_latest_prediction_summary_widget_candidate_resolver_refresh.py",
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
    for forbidden in ("open(", "read_text(", "read_bytes(", "write_text(", "write_bytes(", ".read(", "json.load", "json.loads", "stat(", "glob(", "rglob(", "send_order(", "create_order("):
        if forbidden in source_text:
            failures.append(f"forbidden token in source: {forbidden}")
    if "Path(REFRESHED_CANDIDATE_PATH).exists()" not in source_text:
        failures.append("source must execute only bounded Path(REFRESHED_CANDIDATE_PATH).exists() check")
    packet = build_latest_prediction_summary_widget_q18ae_candidate_resolver_refresh_result_packet(
        execute_refreshed_candidate_exists_check=True,
        explicit_ack=LATEST_PREDICTION_SUMMARY_WIDGET_Q18AE_CANDIDATE_RESOLVER_REFRESH_ACK,
    )
    if packet.get("ok") is not True:
        failures.append(f"candidate resolver refresh packet should be ok: {packet}")
    if packet.get("refreshed_candidate_exists_result_state") != "present":
        failures.append("refreshed candidate must be present")
    if packet.get("candidate_resolver_refresh_row_count") != 12:
        failures.append("expected 12 candidate resolver refresh rows")
    for key in TRUE_BOUNDARIES:
        if packet.get(key) is not True:
            failures.append(f"{key} must be true")
    for key in FALSE_BOUNDARIES:
        if packet.get(key) is not False:
            failures.append(f"{key} must stay false")
    doc_text = _read(DOC) if DOC.exists() else ""
    for marker in ("PS-Q18AE", "refreshed_candidate_exists_result_state=present", "source_artifact_schema_checked=false", "actual_source_read_invoked=false", "Next: schema validation against refreshed present latest prediction artifact"):
        if marker not in doc_text:
            failures.append(f"missing doc marker: {marker}")
    dirty = _dirty_paths()
    unexpected = dirty - EXPECTED_DIRTY
    missing = EXPECTED_DIRTY - dirty
    if unexpected:
        failures.append(f"unexpected dirty paths: {sorted(unexpected)}")
    if missing:
        failures.append(f"missing expected dirty paths: {sorted(missing)}")
    result = {"ok": not failures, "guard": "ps_q18ae_candidate_resolver_refresh_guard", "dirty_paths": sorted(dirty), "unexpected_dirty": sorted(unexpected), "missing_dirty": sorted(missing), "failures": failures, "refreshed_candidate_exists_result_state": packet.get("refreshed_candidate_exists_result_state")}
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if not failures else 1


def test_ps_q18ae_candidate_resolver_refresh_guard() -> None:
    assert main_guard() == 0


if __name__ == "__main__":
    raise SystemExit(main_guard())
