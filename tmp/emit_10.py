from btc_trade_system.features.audit_dev import writer
writer.set_mode("DEBUG")
for i in range(10):
    writer.emit("ui.mass_test", level="INFO", feature="audit_dev", payload={"n": i})
