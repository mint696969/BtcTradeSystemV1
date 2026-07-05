# path: ./docs/operations/HOT_COLD_DATA_FILE_POLICY.md
# desc: Operational policy for hot/cold data file sharding, retention, archive verification, and reader tolerance.

# Hot/Cold data file policy

## Purpose

BtcTradeSystem must not produce or retain huge single hot JSONL files.  Hot data is for live/current operation and short recent history only.  Cold data is the verified archive of closed history.

## Roots

- Hot/latest/live root: `D:/btc_ts_hot`
- Cold/archive root: `E:/btc_ts`

## Retention rule

- D-hot keeps live/current data and the latest 10 date partitions only.
- A hot file older than 10 days is delete-eligible only after a cold copy exists and is verified.
- Open or actively written files are never deleted by hot GC.

## Writer rule

- Writers must not append forever to `part-00001.jsonl`.
- Writers must use ordered shards: `part-00001.jsonl`, `part-00002.jsonl`, ...
- Default target close/rollover size: 256 MiB.
- Default hard rollover size: 512 MiB.
- Existing oversized parts are not appended further; the next write rolls to the next part.
- One JSONL line schema must not change when a file is split.

## Archive rule

- Only stable closed shards are cold-copy eligible.
- Archive copy and GC planners must exclude incomplete file names such as `.open`, `.tmp`, `.partial`, `.inprogress`, `.writing`, and `.lock`.
- Cold copy must preserve the same relative path under the cold root.
- Hot GC requires cold existence and verification before delete.
- Size equality is the minimum compatibility check; new manifest flows should prefer checksum verification.

## Reader rule

Readers for Collector, L1-L4, inference, and UI must read ordered `part-*.jsonl` files for a date partition.  Missing part numbers, corrupt lines, and absent old hot partitions must be handled as warnings rather than hard failures when a cold/derived source can continue the sequence.
- Reader implementation must use tolerant sharded readers that report missing part numbers and skipped corrupt lines while continuing with valid rows.

## High-volume streams

- `market.trade` raw files may be retained short-term in hot but should be converted to compact derived/indexed data for inference and chart windows.
- `board_snapshot` raw full-depth retention is high volume and should be short-retention or opt-in.  UI and inference should prefer derived summaries such as best bid/ask, spread, depth zones, imbalance, and wall events.

## Non-goals

This policy does not enable broker/order/autotrade behavior and does not invoke prediction/classifier execution.
