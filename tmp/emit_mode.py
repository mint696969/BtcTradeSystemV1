from btc_trade_system.features.audit_dev import writer
writer.set_mode("DEBUG")
writer.emit("ui.mode_check", level="INFO", feature="audit_dev", payload={"mode": writer.get_mode()})
