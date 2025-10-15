# path: ./tools/test_providers_health.py
# desc: Health関連の最小動作テスト（svc_healthのサマリ/テーブルを出力）
# repo 直下を PYTHONPATH に追加（tools/ からの相対）
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]  # リポのルート
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from btc_trade_system.features.dash.svc_health import (
    get_health_summary,
    get_health_table,
)

s = get_health_summary()
print("updated_at:", s.get("updated_at"))
print("all_ok:", s.get("all_ok"))

for c in s.get("cards", []):
    age = c.get("age_sec")
    age_s = f"{age:.1f}s" if isinstance(age, (int, float)) else "-"
    print(f"CARD {c.get('exchange','?'):8s} {c.get('status','-'):4s} age={age_s} notes={c.get('notes','')}")

print("--- table ---")
t = get_health_table()
for row in t:
    age = row.get("age_sec")
    age_s = f"{age:.1f}s" if isinstance(age, (int, float)) else "-"
    print(
        f"{row.get('exchange','?'):8s}  {row.get('topic','?'):7s}  "
        f"{row.get('status','-'):4s}  age={age_s}  {row.get('last_iso','-')}  {row.get('source','-')}"
    )
