BTC Trade System (BTC-TS)
STRATEGY SYSTEM

1 Strategy System Overview

BTC-TS の Strategy System は

Strategy Evolution Framework

である。

戦略は静的なロジックではなく
進化する存在として扱う。

構造

Archetype
↓
Genome
↓
Strategy Instance
2 Strategy Archetype

Archetype は

戦略の種族

である。

市場構造ごとに分類される。

例

breakout
mean_reversion
liquidity_trap
momentum
arbitrage
market_making

Archetype は

戦略の進化系統

を形成する。

3 Strategy Genome

Genome は

戦略のDNA

である。

Genome は DSL (YAML) で定義される。

例

strategy: breakout_v1

archetype: breakout

regime:
  type: trend

signals:
  orderbook_imbalance: >0.65
  momentum: positive

entry:
  trigger: breakout
  confirmation: volume_spike

exit:
  take_profit: 1.5%
  stop_loss: 0.7%

risk:
  position_size: 0.02
  max_exposure: 0.1
4 Strategy Instance

Instance は

実際に実行された戦略

である。

記録される内容

entry_time
exit_time
position_size
pnl
execution_log

Instance は

Event Ledger

に保存される。

5 Strategy Arena

Arena は

戦略を競わせる環境

である。

フロー

Replay Market
↓
Strategy A
Strategy B
Strategy C
↓
Execution Simulation
↓
Performance Evaluation

評価指標

win_rate
profit_factor
max_drawdown
expectancy
6 Strategy Ranking

Arena結果はランキング化される。

例

1 liquidity_trap_v4
2 breakout_v6
3 momentum_v3

ランキングは

Strategy Inventory

に保存される。

7 Strategy Mutation

Mutation は

Genome parameter modification

である。

例

imbalance_threshold
0.65 → 0.72

Mutation は

AI
Human

どちらでも行える。

8 Strategy Lifecycle

戦略は次のライフサイクルを持つ。

Idea
↓
Genome
↓
Arena
↓
Shadow Trading
↓
Live Trading
↓
Evolution
9 Strategy Loadout

実戦で使う戦略セット

Active Strategy Set

例

breakout_v6
liquidity_trap_v4
mean_reversion_v5

Loadout は

War Room UI

で管理される。

10 Strategy Evolution Loop

BTC-TS の進化ループ

Market Data
↓
Feature Engine
↓
Strategy Genome
↓
Decision
↓
Execution
↓
Result
↓
Replay
↓
Arena
↓
Mutation
↓
Evolution
11 Strategy Inventory

システムは戦略ライブラリを持つ。

Strategy Inventory

例

Legendary breakout_v8
Rare liquidity_trap_v5
Experimental regime_switch_v1

これは

Strategy RPG System

として扱われる。

12 Human + AI Roles

Human

Strategy design
tactical judgement
AI evaluation

AI

mutation
analysis
strategy suggestion
13 Strategy System Philosophy

BTC-TS において戦略は

static algorithm

ではない。

戦略は

evolving organism

である。