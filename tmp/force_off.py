from btc_trade_system.features.audit_dev import writer
writer.set_mode("OFF")
print("forced OFF; now =", writer.get_mode())
