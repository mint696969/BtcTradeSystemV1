# path: ./tmp/test_settings_roundtrip.py
# desc: svc_settings を使った monitoring.yaml の保存→読込の往復テスト（副作用なし）
import sys
from pathlib import Path

# リポ直下を PYTHONPATH に追加
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from btc_trade_system.features.dash.svc_settings import (
    load_monitoring,
    save_monitoring,
)

# テスト用の一時ディレクトリ（./tmp/ui 配下に書くが、終わりに片付け可）
base = ROOT / "config" / "ui"
target = base / "monitoring.yaml"

# 1) 現在値の取得（なければ空dict）
before = {}
try:
    before = load_monitoring()
except Exception:
    before = {}

# 2) 既存キーの中で安全に上書き（period_min を +1）
before = before or {}
presets = dict(before.get("presets") or {})
orig_val = int(presets.get("period_min") or 10)
test_val = orig_val + 1
presets["period_min"] = test_val

patched = dict(before)
patched["presets"] = presets
save_monitoring(patched)

# 3) 読み直して一致確認（既存スキーマ内なので保持されるはず）
after = load_monitoring()
ok = (int((after.get("presets") or {}).get("period_min") or 0) == test_val)

print("roundtrip_ok:", ok)
print("after.presets.period_min:", (after.get("presets") or {}).get("period_min"))

# 4) 復元（元が空だった場合はテストで作ったキーを戻す/削除）
if before:
    save_monitoring(before)
else:
    # 元が無い＝初回生成だった場合は period_min を 10 に戻す
    after_fix = dict(after)
    ps = dict(after_fix.get("presets") or {})
    ps["period_min"] = orig_val
    after_fix["presets"] = ps
    save_monitoring(after_fix)
