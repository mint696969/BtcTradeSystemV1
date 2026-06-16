BTC Trade System (BTC-TS)
UI ARCHITECTURE

1 UI Philosophy

BTC-TS UI は

AI-First Interface

として設計される。

通常のトレードUI

chart
order
position

BTC-TS UI

Human
+
AI
+
Strategy
+
Research
2 UI Space Model

BTC-TS UI は4つの空間で構成される。

Operator Room
Research Lab
War Room
Replay Lab
3 Operator Room

役割

system operation

用途

collector control
exchange configuration
system health
logs
alerts

特徴

simple
stable
low latency

Operator UI は Streamlitでも可。

4 Research Lab

役割

research environment

機能

dataset explorer
feature analysis
AI experiments
knowledge base
strategy experiments

表示

charts
feature graphs
dataset tables
AI insights

Research Lab は

data science workspace

として設計する。

5 War Room

War Room は

AI Trading Command Center

である。

UI構造

AI Conversation Panel
Strategy Status
Market Radar
Risk Monitor
Execution Feed
6 AI Conversation Panel

War Room の中心。

表示

Analyst AI
Strategy AI
Risk AI
Central AI
Human

例

Analyst AI:
Range regime detected.

Strategy AI:
Mean reversion preferred.

Risk AI:
Volatility increasing.

Human は

AI tactical discussion

に参加できる。

7 AI Agent Panels

Conversation Panel の横に

AIエージェント状態が表示される。

例

Analyst AI
Regime: Range
Volatility: Medium
Confidence: 0.68
Strategy AI
Active Archetype:
Liquidity Trap
Breakout
Risk AI
Exposure: 14%
Max DD: 3.1%
8 Strategy Panel

現在の戦略状態。

表示

active strategies
archetype distribution
strategy performance

例

breakout_v6
liquidity_trap_v4
mean_reversion_v5
9 Market Radar

市場状況。

表示

trend strength
volatility
liquidity
regime detection

Market Radar は

AI summarized market state

として表示される。

10 Risk Monitor

リアルタイムリスク。

表示

exposure
drawdown
position concentration
risk alerts
11 Execution Feed

リアルタイムイベント。

表示

orders
fills
strategy decisions
12 Replay Lab

Replay Lab は

market replay environment

である。

機能

market replay
decision replay
strategy comparison

用途

research
strategy validation
post-mortem analysis
13 UI Technology

UIは 用途ごとに分離する。

Operator UI

Streamlit

Research / War Room

Web UI (React / Next.js)

理由

high visualization flexibility
custom layout
interactive dashboards
14 UI Philosophy Summary

BTC-TS UI は

AI-first
research-centric
strategy-aware

な

Human + AI Cooperative Interface

である。