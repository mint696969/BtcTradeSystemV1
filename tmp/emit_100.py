from btc_trade_system.features.audit_dev import writer
writer.set_mode("BOOST")
for i in range(100):
    writer.emit("ui.mass_test_boost", level="INFO", feature="audit_dev", payload={"n": i})
