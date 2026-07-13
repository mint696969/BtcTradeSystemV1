# path: ./btcts_next/src/btcts/apps/operator_ui/tests/test_ui_check_retention.py
# desc: Verifies UI Check snapshot retention keeps only the latest snapshots.

from __future__ import annotations

from pathlib import Path

from btcts.apps.operator_ui import ui_check_exporter


def test_prune_uicheck_keeps_latest_ten_and_preserves_management_files(tmp_path: Path) -> None:
    for index in range(13):
        name = f"uicheck_20260713_1200{index:02d}_000000_health.json"
        (tmp_path / name).write_text("{}", encoding="utf-8")

    autosave = tmp_path / "autosave_state.json"
    autosave.write_text('{"enabled": true}', encoding="utf-8")
    unrelated = tmp_path / "notes.json"
    unrelated.write_text("{}", encoding="utf-8")

    deleted = ui_check_exporter.prune_gpt_ui_check_snapshots(
        out_dir=tmp_path,
        keep=10,
    )

    remaining = sorted(path.name for path in tmp_path.glob("uicheck_*.json"))
    assert len(remaining) == 10
    assert remaining[0] == "uicheck_20260713_120003_000000_health.json"
    assert remaining[-1] == "uicheck_20260713_120012_000000_health.json"
    assert len(deleted) == 3
    assert autosave.exists()
    assert unrelated.exists()


def test_prune_uicheck_rejects_non_positive_keep(tmp_path: Path) -> None:
    try:
        ui_check_exporter.prune_gpt_ui_check_snapshots(out_dir=tmp_path, keep=0)
    except ValueError as exc:
        assert "keep must be at least 1" in str(exc)
    else:
        raise AssertionError("ValueError was not raised")


def test_snapshot_save_invokes_retention_after_write() -> None:
    text = Path(ui_check_exporter.__file__).read_text(encoding="utf-8-sig")
    write_pos = text.index("out_path.write_text(")
    prune_pos = text.index(
        "prune_gpt_ui_check_snapshots(out_dir=out_dir, keep=UICHK_MAX_SNAPSHOTS)"
    )
    return_pos = text.index("return str(out_path)", prune_pos)

    assert write_pos < prune_pos < return_pos
    assert ui_check_exporter.UICHK_MAX_SNAPSHOTS == 10
