BTC Trade System (BTC-TS)
DATA ARCHITECTURE

1 Data Architecture Overview

BTC-TS は Hybrid Data Architecture を採用する。

理由

real-time execution
research flexibility
AI training
large dataset storage

構造

Operational Database
+
Research Data Lake
2 Data Layers

BTC-TS のデータは6つのストアで管理される。

Event Ledger
Market Store
Feature Store
Strategy Store
Replay Store
Knowledge Store
3 Event Ledger

Event Ledger は BTC-TS の 中心データ構造である。

すべての出来事はイベントとして記録される。

イベント種類

market_event
feature_event
strategy_event
execution_event
result_event
system_event

Event Ledger は

PostgreSQL

で管理される。

理由

transaction safety
time ordering
query reliability
4 Market Data Store

市場データ保存。

データ

trades
orderbook snapshots
tick data

保存形式

Parquet

保存場所

Market Data Lake

理由

large datasets
fast analytics
AI training
5 Feature Store

Feature Engine が生成した特徴量。

例

regime features
volatility
liquidity
orderbook imbalance
momentum

保存

Parquet

Feature Store は

AI training
strategy research

で使用される。

6 Strategy Store

Strategy System 用データ。

保存内容

strategy genomes
archetypes
parameters
strategy metadata

保存形式

YAML

保存場所

Strategy Repository
7 Replay Store

Replay System 用データ。

内容

event sequences
market states
strategy decisions
execution results

Replay Store により

deterministic market replay

が可能になる。

8 Arena Results Store

Arena の評価結果。

保存内容

strategy performance
ranking history
mutation lineage

このデータは

strategy evolution

に利用される。

9 Knowledge Store

Knowledge System 用ストア。

保存内容

market observations
AI discoveries
research notes
strategy insights

形式

Markdown
JSON metadata

Knowledge Store は

Human + AI research memory

として機能する。

10 Data Flow

BTC-TS のデータフロー

Collector
↓
Market Data Store
↓
Feature Engine
↓
Feature Store
↓
Strategy Engine
↓
Execution Engine
↓
Event Ledger
↓
Replay
↓
Arena
↓
Strategy Evolution
11 Data Retention

データ保持方針

Market Data

long-term storage

Feature Data

research datasets

Event Ledger

permanent trading history

Arena Results

strategy evolution history
12 Data Philosophy

BTC-TS のデータ哲学

Record Everything
Replay Anything
Learn Continuously