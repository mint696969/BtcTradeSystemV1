from btc_trade_system.features.audit_dev import writer
writer.set_mode("DEBUG")
writer.emit("ui.test_once", level="INFO", feature="audit_dev", payload={"n": 1})
