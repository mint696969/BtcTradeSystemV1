# path: ./btcts_next/src/btcts/processing/l4_consumer_models/tests/test_warroom_candle_store.py
# desc: Verify rolling WarRoom candle store closed/forming and gap policy.

from __future__ import annotations

import sys
from pathlib import Path

_SRC_ROOT = Path(__file__).resolve().parents[2]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

from btcts.processing.l4_consumer_models.operator_ui import warroom_candle_store as candle_store_module  # noqa: E402
from btcts.processing.l4_consumer_models.operator_ui.warroom_candle_store import (  # noqa: E402
    DEFAULT_TIMEFRAMES_SEC,
    WARROOM_CANDLE_STORE_VERSION,
    _merge_record,
    read_candle_store_chart_payload,
    rebuild_candle_store_from_trade_history,
    update_candle_store_from_latest_part,
)


def test_timeframes_include_manual_trade_chart_set() -> None:
    assert DEFAULT_TIMEFRAMES_SEC == (60, 300, 900, 1800, 3600, 86400)


def test_merge_record_keeps_open_and_updates_ohlcv_for_forming_candle() -> None:
    base = {"time": 100, "open": 10.0, "high": 11.0, "low": 9.0, "close": 10.5, "volume": 1.0, "trade_count": 2}
    incoming = {"time": 100, "open": 10.5, "high": 12.0, "low": 8.5, "close": 11.5, "volume": 2.0, "trade_count": 3}
    merged = _merge_record(base, incoming, timeframe_sec=60, status="forming")
    assert merged is not None
    assert merged["open"] == 10.0
    assert merged["high"] == 12.0
    assert merged["low"] == 8.5
    assert merged["close"] == 11.5
    assert merged["volume"] == 3.0
    assert merged["trade_count"] == 5
    assert merged["candle_status"] == "forming"


def test_empty_store_returns_no_candles_without_gap_error(tmp_path: Path) -> None:
    payload = read_candle_store_chart_payload(store_root=tmp_path, max_candles=10)
    assert payload["ok"] is False
    assert payload["candles"] == []
    assert payload["gap_policy"] == "absent_candles_no_synthetic_null"
    assert payload["meta"]["missing_periods_error"] is False


def test_update_missing_raw_root_is_safe_error_payload(tmp_path: Path) -> None:
    payload = update_candle_store_from_latest_part(raw_root=tmp_path / "missing", store_root=tmp_path)
    assert payload["ok"] is False
    assert payload["read_only_source"] is True
    assert payload["broker_send_enabled"] is False
    assert payload["prediction_invoked"] is False


def test_version_declared() -> None:
    assert WARROOM_CANDLE_STORE_VERSION.startswith("warroom_candle_store.")


def test_candle_store_is_canonical_l4_operator_ui_module() -> None:
    import btcts.processing.l4_consumer_models.operator_ui.warroom_candle_store as module

    assert module.WARROOM_CANDLE_STORE_LAYER == "L4_CONSUMER_MODEL_OPERATOR_UI"
    assert module.WARROOM_CANDLE_STORE_CANONICAL_MODULE == "btcts.processing.l4_consumer_models.operator_ui.warroom_candle_store"


def test_read_trade_rows_from_stored_offset_keeps_first_appended_line(tmp_path: Path, monkeypatch) -> None:
    part = tmp_path / "part-00001.jsonl"
    first = b"{\"id\":1}\n"
    second = b"{\"id\":2}\n"
    part.write_bytes(first + second)

    monkeypatch.setattr(candle_store_module, "_json_record_from_line", lambda line: {"raw": line.decode("utf-8").strip()})
    monkeypatch.setattr(
        candle_store_module,
        "market_trade_record_to_trade_row",
        lambda record, source_file: {"record": record["raw"], "source_file": source_file},
    )

    rows, new_offset, lines_read, tail_bootstrap = candle_store_module._read_trade_rows_from_offset(
        part,
        offset=len(first),
        max_bootstrap_bytes=1024,
    )

    assert tail_bootstrap is False
    assert lines_read == 1
    assert rows == [{"record": '{"id":2}', "source_file": str(part)}]
    assert new_offset == len(first + second)


def test_history_rebuild_adopts_latest_source_offset(tmp_path: Path, monkeypatch) -> None:
    raw_root = tmp_path / "raw"
    trade_dir = raw_root / "data" / "market_data" / "exchange=bitflyer" / "symbol=FX_BTC_JPY" / "type=market.trade" / "date=2026-07-06"
    trade_dir.mkdir(parents=True)
    part = trade_dir / "part-00001.jsonl"
    part.write_text(
        "\n".join(
            [
                '{"ts":"2026-07-06T00:00:01Z","price":100,"size":1}',
                '{"ts":"2026-07-06T00:00:20Z","price":105,"size":2}',
                '{"ts":"2026-07-06T00:01:01Z","price":103,"size":3}',
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    import json as _json
    import pandas as _pd

    monkeypatch.setattr(candle_store_module, "_json_record_from_line", lambda line: _json.loads(line.decode("utf-8") if isinstance(line, bytes) else line))
    monkeypatch.setattr(candle_store_module, "_record_event_ts", lambda record: _pd.Timestamp(record["ts"]).tz_convert("UTC"))
    monkeypatch.setattr(
        candle_store_module,
        "market_trade_record_to_trade_row",
        lambda record, source_file: {
            "ts": _pd.Timestamp(record["ts"], tz="UTC"),
            "price": float(record["price"]),
            "size": float(record["size"]),
            "side": "",
            "trade_id": "",
            "source_file": source_file,
        },
    )

    payload = rebuild_candle_store_from_trade_history(
        raw_root=raw_root,
        store_root=tmp_path / "store",
        timeframes_sec=(60,),
        retention_days=92,
        max_days=92,
        chunk_rows=2,
    )

    assert payload["ok"] is True
    assert payload["update_meta"]["history_rebuild"] is True
    assert payload["update_meta"]["new_offset"] == part.stat().st_size
    assert payload["update_meta"]["append_boundary"] == "update_state.source_part_file+byte_offset"
    state_path = Path(payload["state_path"])
    state = _json.loads(state_path.read_text(encoding="utf-8-sig"))
    assert state["source_part_file"] == str(part)
    assert state["byte_offset"] == part.stat().st_size
    assert state["history_rebuild"] is True
    chart = read_candle_store_chart_payload(store_root=tmp_path / "store", timeframe_sec=60, max_candles=10)
    assert chart["ok"] is True
    assert chart["candle_count"] == 2
    assert chart["candles"][0]["candle_status"] == "closed"
    assert chart["candles"][-1]["candle_status"] == "forming"


def test_history_rebuild_multiple_roots_prefers_hot_date_and_adopts_hot_offset(tmp_path: Path, monkeypatch) -> None:
    cold_root = tmp_path / "cold"
    hot_root = tmp_path / "hot"
    cold_dir = cold_root / "data" / "market_data" / "exchange=bitflyer" / "symbol=FX_BTC_JPY" / "type=market.trade" / "date=2026-07-06"
    hot_dir = hot_root / "data" / "market_data" / "exchange=bitflyer" / "symbol=FX_BTC_JPY" / "type=market.trade" / "date=2026-07-06"
    cold_dir.mkdir(parents=True)
    hot_dir.mkdir(parents=True)
    cold_part = cold_dir / "part-00001.jsonl"
    hot_part = hot_dir / "part-00001.jsonl"
    cold_part.write_text('{"ts":"2026-07-06T00:00:01Z","price":100,"size":1}\n', encoding="utf-8")
    hot_part.write_text(
        "\n".join(
            [
                '{"ts":"2026-07-06T00:00:01Z","price":200,"size":1}',
                '{"ts":"2026-07-06T00:00:20Z","price":201,"size":1}',
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    import json as _json
    import pandas as _pd

    monkeypatch.setattr(candle_store_module, "_json_record_from_line", lambda line: _json.loads(line.decode("utf-8") if isinstance(line, bytes) else line))
    monkeypatch.setattr(candle_store_module, "_record_event_ts", lambda record: _pd.Timestamp(record["ts"]).tz_convert("UTC"))
    monkeypatch.setattr(
        candle_store_module,
        "market_trade_record_to_trade_row",
        lambda record, source_file: {
            "ts": _pd.Timestamp(record["ts"]).tz_convert("UTC"),
            "price": float(record["price"]),
            "size": float(record["size"]),
            "side": "",
            "trade_id": "",
            "source_file": source_file,
        },
    )

    payload = rebuild_candle_store_from_trade_history(
        raw_roots=(cold_root, hot_root),
        store_root=tmp_path / "store",
        timeframes_sec=(60,),
        retention_days=92,
        max_days=92,
        chunk_rows=1,
    )

    assert payload["ok"] is True
    assert payload["source_meta"]["selected_root_policy"] == "later_roots_replace_earlier_roots_by_date_partition"
    assert payload["source_meta"]["replaced_date_partitions"][0]["date"] == "2026-07-06"
    assert payload["update_meta"]["source_part_file"] == str(hot_part)
    assert payload["update_meta"]["new_offset"] == hot_part.stat().st_size
    state = _json.loads(Path(payload["state_path"]).read_text(encoding="utf-8-sig"))
    assert state["source_part_file"] == str(hot_part)
    assert state["byte_offset"] == hot_part.stat().st_size
    chart = read_candle_store_chart_payload(store_root=tmp_path / "store", timeframe_sec=60, max_candles=10)
    assert chart["ok"] is True
    assert chart["candle_count"] == 1
    assert chart["candles"][0]["open"] == 200.0
    assert chart["candles"][0]["close"] == 201.0
    assert chart["candles"][0]["trade_count"] == 2


def test_fast_epoch_seconds_handles_collector_iso7() -> None:
    assert candle_store_module._fast_epoch_seconds("2026-06-25T23:59:59.8139216Z") == 1782431999
    assert candle_store_module._fast_epoch_seconds("2026-06-25T23:59:59.813Z") == 1782431999


def test_fast_trade_values_reads_canonical_market_trade() -> None:
    record = {
        "event_ts": "2026-06-25T23:59:59.8139216Z",
        "source_event_id": "2646967875",
        "payload": {"trade_id": 2646967875, "price": 9663121.0, "size": 0.001, "side": "BUY"},
    }
    assert candle_store_module._fast_trade_values(record) == (1782431999, 9663121.0, 0.001, "2646967875")


def test_history_rebuild_uses_streaming_fast_aggregation_marker() -> None:
    source = candle_store_module.Path(candle_store_module.__file__).read_text(encoding="utf-8-sig")
    assert "_merge_fast_trade_into_timeframes" in source
    assert "streaming_fast_ohlc_no_pandas_dataframe" in source
    assert "warroom_candle_rebuild" in source
    assert "[PROGRESS]" in source


def test_fast_rebuild_dedupe_scope_is_date_partition() -> None:
    source = candle_store_module.Path(candle_store_module.__file__).read_text(encoding="utf-8-sig")
    assert 'dedupe_scope = "date_partition_trade_id"' in source
    assert 'part_date = part.parent.name.removeprefix("date=")' in source
    assert "if part_date != current_dedupe_date" in source


def test_live_append_preserves_history_rebuild_lineage_markers(tmp_path: Path, monkeypatch) -> None:
    raw_root = tmp_path / "raw"
    trade_dir = raw_root / "data" / "market_data" / "exchange=bitflyer" / "symbol=FX_BTC_JPY" / "type=market.trade" / "date=2026-07-06"
    trade_dir.mkdir(parents=True)
    rebuild_part = trade_dir / "part-00001.jsonl"
    rebuild_part.write_text(
        "\n".join(
            [
                '{"ts":"2026-07-06T00:00:01Z","price":100,"size":1,"trade_id":"a"}',
                '{"ts":"2026-07-06T00:01:01Z","price":101,"size":1,"trade_id":"b"}',
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    import json as _json
    import pandas as _pd

    monkeypatch.setattr(candle_store_module, "_json_record_from_line", lambda line: _json.loads(line.decode("utf-8") if isinstance(line, bytes) else line))
    monkeypatch.setattr(candle_store_module, "_record_event_ts", lambda record: _pd.Timestamp(record["ts"]).tz_convert("UTC"))
    monkeypatch.setattr(
        candle_store_module,
        "market_trade_record_to_trade_row",
        lambda record, source_file: {
            "ts": _pd.Timestamp(record["ts"]).tz_convert("UTC"),
            "price": float(record["price"]),
            "size": float(record["size"]),
            "side": "",
            "trade_id": str(record.get("trade_id") or ""),
            "source_file": source_file,
        },
    )

    store_root = tmp_path / "store"
    rebuild = rebuild_candle_store_from_trade_history(
        raw_root=raw_root,
        store_root=store_root,
        timeframes_sec=(60,),
        retention_days=92,
        max_days=92,
        chunk_rows=1,
    )
    assert rebuild["ok"] is True

    append_part = trade_dir / "part-00002.jsonl"
    append_part.write_text('{"ts":"2026-07-06T00:02:01Z","price":102,"size":1,"trade_id":"c"}\n', encoding="utf-8")
    appended = update_candle_store_from_latest_part(raw_root=raw_root, store_root=store_root, timeframes_sec=(60,), retention_days=92)
    assert appended["ok"] is True

    state = _json.loads((store_root / "data" / "derived" / "warroom" / "candles" / "exchange=bitflyer" / "symbol=FX_BTC_JPY" / "update_state.json").read_text(encoding="utf-8-sig"))
    assert state["source_part_file"] == str(append_part)
    assert state["append_boundary"] == "update_state.source_part_file+byte_offset"
    assert state["duplicate_policy"] == "resume_from_update_state_no_reaggregate_processed_trades"
    assert state["previous_history_rebuild"] is True
    assert state["previous_history_source_part_file"] == str(rebuild_part)
    assert state["previous_history_byte_offset"] == rebuild_part.stat().st_size
    assert state["previous_history_first_source_ts_utc"]
    assert state["previous_history_part_count"] == 1
    assert appended["update_meta"]["append_boundary"] == "update_state.source_part_file+byte_offset"
    assert appended["update_meta"]["previous_history_rebuild"] is True


def test_history_lineage_recovers_from_completed_progress_when_state_lost_markers() -> None:
    lineage = candle_store_module._history_lineage_from_state(
        {
            "source_part_file": "D:/btc_ts_hot/current.jsonl",
            "byte_offset": 123,
            "previous_history_rebuild": None,
        },
        progress={
            "phase": "completed",
            "source_part_file": "D:/btc_ts_hot/history_part.jsonl",
            "part_offset": 456,
            "part_count": 55,
            "latest_source_ts_utc": "2026-07-06T22:52:51Z",
        },
        first_candle_ts_utc="2026-06-14T16:09:00Z",
    )

    assert lineage["append_boundary"] == "update_state.source_part_file+byte_offset"
    assert lineage["duplicate_policy"] == "resume_from_update_state_no_reaggregate_processed_trades"
    assert lineage["previous_history_rebuild"] is True
    assert lineage["previous_history_source_part_file"] == "D:/btc_ts_hot/history_part.jsonl"
    assert lineage["previous_history_byte_offset"] == 456
    assert lineage["previous_history_first_source_ts_utc"] == "2026-06-14T16:09:00Z"
    assert lineage["previous_history_latest_source_ts_utc"] == "2026-07-06T22:52:51Z"
    assert lineage["previous_history_part_count"] == 55
    assert lineage["previous_history_recovered_from"] == "warroom_candle_rebuild_progress_json"


def test_atomic_write_text_retries_windows_permission_error(tmp_path: Path, monkeypatch) -> None:
    target = tmp_path / "closed.jsonl"
    attempts = {"count": 0}
    original_replace = candle_store_module.Path.replace

    def flaky_replace(self, target_path):
        if str(target_path).endswith("closed.jsonl") and attempts["count"] < 2:
            attempts["count"] += 1
            raise PermissionError("simulated transient Windows lock")
        return original_replace(self, target_path)

    monkeypatch.setattr(candle_store_module.time, "sleep", lambda _seconds: None)
    monkeypatch.setattr(candle_store_module.Path, "replace", flaky_replace)

    candle_store_module._atomic_write_text(target, "ok\n", attempts=4, initial_sleep_sec=0.001)

    assert target.read_text(encoding="utf-8") == "ok\n"
    assert attempts["count"] == 2
    assert not list(tmp_path.glob("closed.jsonl.tmp.*"))


def test_live_append_processes_every_intermediate_part_across_date_rollover(tmp_path: Path, monkeypatch) -> None:
    raw_root = tmp_path / "raw"
    first_dir = raw_root / "data" / "market_data" / "exchange=bitflyer" / "symbol=FX_BTC_JPY" / "type=market.trade" / "date=2026-07-09"
    next_dir = raw_root / "data" / "market_data" / "exchange=bitflyer" / "symbol=FX_BTC_JPY" / "type=market.trade" / "date=2026-07-10"
    first_dir.mkdir(parents=True)
    next_dir.mkdir(parents=True)
    first_part = first_dir / "part-00001.jsonl"
    first_part.write_text('{"ts":"2026-07-09T23:59:01Z","price":100,"size":1,"trade_id":"a"}\n', encoding="utf-8")

    import json as _json
    import pandas as _pd

    monkeypatch.setattr(candle_store_module, "_json_record_from_line", lambda line: _json.loads(line.decode("utf-8") if isinstance(line, bytes) else line))
    monkeypatch.setattr(candle_store_module, "_record_event_ts", lambda record: _pd.Timestamp(record["ts"]).tz_convert("UTC"))
    monkeypatch.setattr(
        candle_store_module,
        "market_trade_record_to_trade_row",
        lambda record, source_file: {
            "ts": _pd.Timestamp(record["ts"]).tz_convert("UTC"),
            "price": float(record["price"]),
            "size": float(record["size"]),
            "side": "",
            "trade_id": str(record.get("trade_id") or ""),
            "source_file": source_file,
        },
    )

    store_root = tmp_path / "store"
    rebuilt = rebuild_candle_store_from_trade_history(
        raw_root=raw_root,
        store_root=store_root,
        timeframes_sec=(60,),
        retention_days=92,
        max_days=92,
        chunk_rows=1,
    )
    assert rebuilt["ok"] is True

    intermediate_part = first_dir / "part-00002.jsonl"
    intermediate_part.write_text('{"ts":"2026-07-09T23:59:31Z","price":101,"size":2,"trade_id":"b"}\n', encoding="utf-8")
    next_part = next_dir / "part-00001.jsonl"
    next_part.write_text('{"ts":"2026-07-10T00:00:31Z","price":102,"size":3,"trade_id":"c"}\n', encoding="utf-8")

    appended = update_candle_store_from_latest_part(
        raw_root=raw_root,
        store_root=store_root,
        timeframes_sec=(60,),
        retention_days=92,
        max_days=7,
    )

    assert appended["ok"] is True
    assert appended["update_meta"]["contiguous_part_rollover"] is True
    assert appended["update_meta"]["processed_part_count"] == 3
    assert appended["update_meta"]["part_rollover_count"] == 2
    assert appended["update_meta"]["processed_part_first_file"] == str(first_part)
    assert appended["update_meta"]["processed_part_latest_file"] == str(next_part)
    assert appended["update_meta"]["trade_rows_read"] == 2

    state = _json.loads((store_root / "data" / "derived" / "warroom" / "candles" / "exchange=bitflyer" / "symbol=FX_BTC_JPY" / "update_state.json").read_text(encoding="utf-8-sig"))
    assert state["source_part_file"] == str(next_part)
    assert state["byte_offset"] == next_part.stat().st_size
    assert state["processed_part_count"] == 3
    assert state["contiguous_part_rollover"] is True

    chart = read_candle_store_chart_payload(
        store_root=store_root,
        timeframe_sec=60,
        max_candles=10,
    )
    assert chart["ok"] is True
    assert chart["candle_count"] == 2
    assert chart["candles"][0]["open"] == 100.0
    assert chart["candles"][0]["close"] == 101.0
    assert chart["candles"][0]["trade_count"] == 2
    assert chart["candles"][1]["close"] == 102.0
    assert chart["candles"][1]["trade_count"] == 1


def test_live_append_fails_closed_when_state_part_is_outside_scan(tmp_path: Path) -> None:
    import json as _json

    raw_root = tmp_path / "raw"
    trade_dir = raw_root / "data" / "market_data" / "exchange=bitflyer" / "symbol=FX_BTC_JPY" / "type=market.trade" / "date=2026-07-10"
    trade_dir.mkdir(parents=True)
    current_part = trade_dir / "part-00001.jsonl"
    current_part.write_text('{"ts":"2026-07-10T00:00:01Z","price":100,"size":1}\n', encoding="utf-8")

    store_root = tmp_path / "store"
    state_path = store_root / "data" / "derived" / "warroom" / "candles" / "exchange=bitflyer" / "symbol=FX_BTC_JPY" / "update_state.json"
    state_path.parent.mkdir(parents=True)
    missing_part = raw_root / "data" / "market_data" / "exchange=bitflyer" / "symbol=FX_BTC_JPY" / "type=market.trade" / "date=2026-06-01" / "part-00099.jsonl"
    state_path.write_text(
        _json.dumps({"source_part_file": str(missing_part), "byte_offset": 123}),
        encoding="utf-8",
    )

    result = update_candle_store_from_latest_part(
        raw_root=raw_root,
        store_root=store_root,
        timeframes_sec=(60,),
        max_days=7,
    )

    assert result["ok"] is False
    assert result["error"] == "state_source_part_not_found_in_scan"
    assert result["state_source_part_file"] == str(missing_part)
    assert result["recovery"] == "run_explicit_history_rebuild_or_expand_max_days"
    assert not (store_root / "data" / "derived" / "warroom" / "candles" / "exchange=bitflyer" / "symbol=FX_BTC_JPY" / "timeframe=60s" / "meta.json").exists()

def test_l4_candle_runtime_has_no_prediction_package_imports() -> None:
    import ast

    package_root = Path(__file__).resolve().parents[1]
    targets = (
        package_root / "operator_ui" / "warroom_candle_store.py",
        package_root / "operator_ui" / "warroom_chart_data_server.py",
        package_root / "market_trade_candle_core.py",
    )
    for path in targets:
        tree = ast.parse(path.read_text(encoding="utf-8-sig"), filename=str(path))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                assert all(
                    not alias.name.startswith("btcts.prediction")
                    and alias.name != "streamlit"
                    for alias in node.names
                ), path
            elif isinstance(node, ast.ImportFrom):
                module = node.module or ""
                assert not module.startswith("btcts.prediction"), path
                assert module != "streamlit", path
            elif isinstance(node, ast.Call):
                name = ""
                if isinstance(node.func, ast.Name):
                    name = node.func.id
                elif isinstance(node.func, ast.Attribute):
                    name = node.func.attr
                assert name not in {"send_to_broker", "submit_order_intent"}, path


def test_l4_candle_core_parses_trade_and_builds_ohlc_without_prediction_import() -> None:
    from btcts.processing.l4_consumer_models.market_trade_candle_core import (
        build_trade_ohlc,
        market_trade_record_to_trade_row,
    )

    first = market_trade_record_to_trade_row({
        "event_ts": "2026-07-10T00:00:01Z",
        "payload": {"price": 100.0, "size": 1.5, "side": "BUY", "trade_id": "a"},
    })
    second = market_trade_record_to_trade_row({
        "event_ts": "2026-07-10T00:00:31Z",
        "payload": {"price": 102.0, "size": 2.0, "side": "SELL", "trade_id": "b"},
    })
    assert first is not None and second is not None
    frame = candle_store_module.pd.DataFrame([first, second])
    candles = build_trade_ohlc(frame, timeframe_sec=60)
    assert len(candles) == 1
    row = candles.iloc[0]
    assert row["open"] == 100.0
    assert row["high"] == 102.0
    assert row["low"] == 100.0
    assert row["close"] == 102.0
    assert row["volume"] == 3.5
    assert row["trade_count"] == 2

def test_l4_legacy_cache_reader_round_trip(tmp_path: Path) -> None:
    import json as _json
    from btcts.processing.l4_consumer_models.market_trade_candle_core import (
        read_legacy_plain_candle_cache,
    )

    directory = (
        tmp_path / "data" / "derived" / "warroom" / "plain_candles"
        / "exchange=bitflyer" / "symbol=FX_BTC_JPY" / "timeframe=60s"
    )
    directory.mkdir(parents=True)
    rows = [
        {
            "time": 1, "time_utc": "2026-07-10T00:00:00Z",
            "candle_index": 0, "open": 100, "high": 102, "low": 99,
            "close": 101, "volume": 1.5, "trade_count": 2,
            "timeframe_sec": 60, "source_family": "fixture",
        },
        {
            "time": 2, "time_utc": "2026-07-10T00:01:00Z",
            "candle_index": 1, "open": 101, "high": 103, "low": 100,
            "close": 102, "volume": 2.5, "trade_count": 3,
            "timeframe_sec": 60, "source_family": "fixture",
        },
    ]
    (directory / "latest.jsonl").write_text(
        "\n".join(_json.dumps(row) for row in rows) + "\n", encoding="utf-8"
    )
    (directory / "latest_meta.json").write_text(
        _json.dumps({"ok": True}), encoding="utf-8"
    )

    frame, meta = read_legacy_plain_candle_cache(tmp_path, max_candles=1)
    assert len(frame) == 1
    assert frame.iloc[0]["close"] == 102
    assert meta["read_ok"] is True
    assert meta["rows_returned"] == 1
