# path: tools/test_providers_health.py
from pathlib import Path
from btc_trade_system.apps.boards.dashboard.providers import get_health_summary, get_health_table

s = get_health_summary()
print("updated_at:", s["updated_at"])
print("order:", s["order"])
for c in s["cards"]:
    print(f"CARD {c['exchange']:8s} {c['status']:4s} age={c['age_sec']:.1f} notes={c['notes']}")

print("--- table ---")
t = get_health_table()
for row in t:
    print(f"{row['exchange']:8s}  {row['topic']:7s}  {row['status']:4s}  age={row['age_sec']:.1f}  {row['last_iso']}  {row['source']}")
