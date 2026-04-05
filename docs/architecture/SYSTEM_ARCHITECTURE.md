# path: ./docs/architecture/SYSTEM_ARCHITECTURE.md
# desc: High-level architecture overview and gateway to current canonical specs.
BTC Trade System (BTC-TS)
System Architecture

## Current Canonical Specs

> [!IMPORTANT]
> この文書は BTC-TS 全体像の高位アーキテクチャ説明です。
> 現行 repository のレイヤ責務・分離検証・L4 / UI hub 設計の正本は、以下の architecture 文書群を参照してください。

- docs/architecture/LAYER_RESPONSIBILITY_RUNTIME_SPEC_2026-04-04.md
- docs/architecture/L2_L3_SEPARATION_LIGHTWEIGHT_VERIFICATION_SPEC_2026-04-04.md
- docs/architecture/L2_L3_SEPARATION_LIGHTWEIGHT_VERIFICATION_CHECKLIST_2026-04-04.md
- docs/architecture/L4_SHARED_FIRST_DESIGN_SPEC_2026-04-04.md
- docs/architecture/L4_SHARED_FIRST_MIGRATION_CHECKLIST_2026-04-04.md
- docs/architecture/UI_HUB_WIDGET_ARCHITECTURE_SPEC_2026-04-04.md
- docs/architecture/L4_MARKET_SUMMARY_FIELD_SPEC_2026-04-04.md
- docs/architecture/L4_MARKET_SUMMARY_BUILDER_SKELETON_SPEC_2026-04-04.md
- docs/architecture/L4_OPERATOR_UI_ADAPTER_SPEC_2026-04-05.md

BTC-TSは Layered Modular Architecture を採用する。

理由

拡張性
分散構造
AI連携
研究システムとの統合
全体構造

BTC-TSは7つのレイヤーで構成される。

Market Data Layer
Feature Layer
Strategy Layer
Execution Layer
Replay Layer
Evolution Layer
UI Layer

これをまとめて

BTC-TS Core Architecture

と呼ぶ。

Layer 1
Market Data Layer

役割

市場データ収集

コンポーネント

Collector
Exchange adapters
Data normalizer

入力

trade
orderbook
ticker

出力

normalized market events

実装

btcts_next (現在)
Layer 2
Feature Layer

役割

市場特徴量生成

フロー

Market Data
↓
Feature Engine
↓
Feature Dataset

特徴量カテゴリ

Market Regime
Microstructure
Trader Behaviour
Volatility
Liquidity
Momentum

出力

feature vectors
Layer 3
Strategy Layer

役割

戦略定義
戦略評価
意思決定

構造

Archetype
Genome
Strategy Instance

例

breakout
mean_reversion
liquidity_trap
momentum
Layer 4
Execution Layer

役割

注文発行
ポジション管理

コンポーネント

Order engine
Position manager
Risk control
Exchange connector

出力

execution events
Layer 5
Replay Layer

役割

市場再現
意思決定再現

構造

Event Ledger
Replay Engine
Scenario Loader

用途

研究
戦略検証
AI学習
Layer 6
Evolution Layer

役割

戦略進化

コンポーネント

Strategy Arena
Mutation Engine
Strategy Ranking

Arenaフロー

Replay Market
↓
Strategy Competition
↓
Performance Evaluation
↓
Ranking
Layer 7
UI Layer

役割

Human-AI interaction

UI構造

Operator UI
Research Lab
War Room
Operator UI

役割

システム管理

機能

collector status
exchange config
system health
logs
Research Lab

役割

研究環境

機能

dataset browser
feature analysis
AI research
knowledge base
strategy experiments
War Room

役割

戦術司令室

機能

market regime display
strategy loadout
risk monitor
AI console
live metrics
Data Backbone

BTC-TSは Event Driven System である。

イベントタイプ

market_event
feature_event
strategy_event
execution_event
result_event

すべて

Event Ledger

に記録される。

AI Integration Layer

AIはシステムの複数レイヤーに関与する。

役割

market analysis
strategy generation
risk evaluation
research assistance

将来構造

Human
↓
Central AI
↓
AI Agent Network

Agent例

Analyst AI
Strategy AI
Risk AI
Execution AI
Research AI
Modular Repository Philosophy

BTC-TSは 機能ごとにリポジトリ分離を採用する。

例

btcts_next        (collector)
btcts_trade       (execution)
btcts_inference   (AI)
btcts_audit       (audit)
btcts_ui          (UI hub)

中央ハブ

BTC Trade System
System Flow

BTC-TSの基本ループ

Market Data
↓
Feature Engine
↓
Strategy Decision
↓
Execution
↓
Result
↓
Replay
↓
Arena
↓
Evolution
Architecture Philosophy

BTC-TSの設計原則

Modular
Event-Driven
AI-Integrated
Research-First
Evolution-Based
Architecture Summary

BTC-TSは

Human + AI cooperative research system

として設計された

Strategy Evolution Platform

である。