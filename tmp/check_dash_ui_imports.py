import importlib

mods = [
  "btc_trade_system.features.dash.ui_audit",
  "btc_trade_system.features.dash.ui_health",
  "btc_trade_system.features.dash.ui_settings",
]

for m in mods:
    print("TRY:", m)
    importlib.import_module(m)
    print("OK:", m)
