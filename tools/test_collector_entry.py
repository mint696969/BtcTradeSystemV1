# path: ./tools/test_io_audit.py
# desc: core/io の atomic_write_text と core/audit.emit の最小スモーク（tmp配下へ書込 + audit.jsonl生成確認）

from _btcts_bootstrap import ensure_btcts_on_syspath

ensure_btcts_on_syspath()

import os
from pathlib import Path

from btcts.core import io as io_safe
from btcts.core import audit
from btcts.core import paths


def main() -> int:
    # テスト用のデフォルト（未指定なら repo/tmp 配下）
    repo = Path(__file__).resolve().parents[1]
    os.environ.setdefault("BTC_TS_DATA_DIR", str(repo / "tmp" / "_io_audit_test" / "data"))
    os.environ.setdefault("BTC_TS_LOGS_DIR", str(repo / "tmp" / "_io_audit_test" / "logs"))

    # audit は OFF だと書かない仕様なので、テストでは明示的に DEBUG にする
    os.environ.setdefault("BTC_TS_MODE", "DEBUG")

    data_dir = paths.data_dir()
    logs_dir = paths.logs_dir()
    data_dir.mkdir(parents=True, exist_ok=True)
    logs_dir.mkdir(parents=True, exist_ok=True)

    print("[ENV] BTC_TS_MODE     =", os.getenv("BTC_TS_MODE"))
    print("[ENV] BTC_TS_LOGS_DIR =", str(logs_dir))
    print("[ENV] BTC_TS_DATA_DIR =", str(data_dir))

    out_txt = data_dir / "io_atomic_test" / "hello.txt"
    io_safe.atomic_write_text(out_txt, "hello atomic\n")
    print("[OK] atomic_write_text ->", str(out_txt))

    audit.emit(
        "test.io_audit",
        feature="test",
        payload={"path": str(out_txt), "note": "smoke"},
    )
    print("[OK] audit.emit(test.io_audit)")

    audit_path = logs_dir / "audit.jsonl"
    if not audit_path.exists():
        raise SystemExit(f"ERROR: audit.jsonl not created: {audit_path}")

    print("[OK] audit.jsonl exists ->", str(audit_path))
    print("DONE")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
