# path: ./tools/test_prediction_system_ps_c_contracts_close_guard.py
# desc: Close guard for PS-C standalone Prediction System contracts guard syntax and importability.

from __future__ import annotations

import importlib
import py_compile
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "btcts_next" / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

FILES = [
    ROOT / "btcts_next" / "src" / "btcts" / "prediction" / "system_contract.py",
    ROOT / "tools" / "test_prediction_system_ps_c_contracts_guard.py",
    ROOT / "tools" / "test_prediction_system_ps_c_contracts_close_guard.py",
]


def test_ps_c_contract_files_compile_and_import() -> None:
    for path in FILES:
        if not path.exists():
            raise AssertionError(f"missing file: {path}")
        py_compile.compile(str(path), doraise=True)
    module = importlib.import_module("btcts.prediction.system_contract")
    assert module.LOGIC_VERSION == "prediction_system_contract.ps_c.v1"
    public = importlib.import_module("btcts.prediction")
    assert hasattr(public, "PredictionSystemResult")
    assert hasattr(public, "ScenarioCoreOutput")


def main() -> int:
    test_ps_c_contract_files_compile_and_import()
    print("[OK] Prediction System PS-C standalone contracts close guard passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
