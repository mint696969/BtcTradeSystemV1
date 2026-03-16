BTC-TS Operator UI 完全設計書 v1

BTC-TS Operator UI Complete Specification

Version: 1.0
System: BTC-TS (BTC Trade System)
Scope: Operator Interface / War Room / AI Interaction Layer

1. UI Philosophy（思想）

BTC-TS Operator UI は単なるダッシュボードではない。

これは

Human + AI Trading War Room

である。

目的は以下。

目的	内容
市場理解	板・フロー・マイクロ構造の可視化
AI分析	市場状態をAIが解釈
戦略判断	AI + Human の協働判断
リスク管理	市場リスクのリアルタイム監視
研究	Research Lab
検証	Replay Lab

Operator UI は

AI + Human
共同意思決定システム

として設計されている。

2. System Architecture

Operator UI は BTC-TS の オペレーションレイヤ。

Collector
    ↓
Data Storage
    ↓
Replay / Research
    ↓
Operator UI
    ↓
Human + AI Decision

構造。

3. Application Structure

エントリーポイント

btcts_next/src/btcts/apps/operator_ui/app.py

UIページ構成

Operator UI
│
├ War Room
├ Collector
├ Health
├ Logs
├ Config
├ Research
└ Replay
4. Sidebar Control

左サイドバーは UI制御センター。

設定項目

設定	内容
Language	ja / en
UI Scale	50 / 75 / 100
Auto Refresh	ON / OFF
Refresh Interval	秒

UI更新は

Streamlit rerun

で実装。

5. War Room（最重要）

War Room は

Trading Command Center

である。

市場・AI・戦略・リスクを一画面で統合。

構造

War Room
│
├ Market Monitor
├ AI Operator
├ AI Reasoning
├ Alert Engine
├ Risk Monitor
├ Decision Log
├ Watch List
├ Timeline
└ AI Conversation
6. Market Monitor

市場のリアルタイム状態。

表示項目

指標	内容
spread	bid / ask 差
imbalance	板偏り
trade_delta	約定フロー
wall_ratio	板の壁

データソース

Collector
Replay artifact
Research artifact
7. AI Operator System

AI Operator は

市場判断AI

である。

役割

市場状態 → 推奨行動

出力

項目	内容
Suggested Action	long / short / wait
Risk Posture	low / medium / high

判断ロジック例

trend_up
+
imbalance > 0.2
+
delta > 0.2

↓

long_watch
8. AI Reasoning System

AI Operator の判断理由を説明。

構造

Reasoning
├ headline
├ metrics
├ reason list
└ conclusion

表示例

spread: tight
imbalance: bid bias
delta: buy flow

↓

Long watch is reasonable
9. Decision Log System

AI判断履歴を保存。

保存先

E:\btc_ts\data\operator_ui\ai_operator_decisions.jsonl

保存内容

timestamp
regime
spread_state
imbalance_state
delta_state
wall_state
action
risk
runtime_source
10. Watch System

重要局面を保存。

保存先

watch_list.jsonl

用途

あとでReplay分析

保存項目

timestamp
regime
action
risk
11. Timeline / Event Feed

Collectorイベント表示。

データ

audit.jsonl

表示項目

項目	内容
timestamp	イベント時間
event	collector event
exchange	取引所
topic	データ種類
latency	ms
12. Risk Monitor

市場リスクを表示。

リスク要因

要因	内容
spread	市場流動性
latency	API遅延
flow_conflict	フロー衝突
wall_ratio	板圧力

リスク出力

LOW
MEDIUM
HIGH
13. AI Conversation System

Human ↔ AI 対話。

コンポーネント

ai_conversation_panel.py

質問例

現在の市場を要約して
ショート優勢？
壁はどちら？

パラメータ

項目	内容
intent	explain / decide / risk
style	concise / normal / deep
14. AI Runtime

AI実行制御

ai_runtime.py

モード

mode	内容
local	ローカルロジック
external	外部AI
fallback	local fallback

外部AI

http://127.0.0.1:18080/ai/respond
15. Market Memory

AI短期記憶。

保存

ai_market_memory.jsonl

保存内容

spread
imbalance
delta
wall_ratio
timestamp

用途

AIコンテキスト
16. Research Lab

研究UI

views/research_page.py

用途

市場研究
AI実験
指標分析
17. Replay Lab

市場再生。

views/replay_page.py

目的

過去市場再現
AI判断検証
戦略検証
18. Data Sources

UIが読むデータ

Collector
E:\btc_ts\data\collector\
Audit Log
E:\btc_ts\logs\audit.jsonl
Replay
E:\btc_ts\replay
Research
E:\btc_ts\research
19. Persistence Layer

保存データ

operator_ui/
├ ai_market_memory.jsonl
├ watch_list.jsonl
└ ai_operator_decisions.jsonl
20. Auto Refresh Mechanism

UI更新

Streamlit rerun

対象ページ

Collector
War Room
Health
Logs

更新間隔

3〜10秒
21. Current Design Limitation

現状の War Room は

Replay / Research snapshot

を多く参照している。

そのため

リアルタイム性が弱い

場合がある。

22. Future Architecture

将来設計

WarRoom Live Bridge

新構造

LIVE DATA
↓
Collector State
↓
War Room

これにより

真のリアルタイム分析

が可能になる。

23. UI Structure Summary
Operator UI
│
├ War Room
│   ├ Market Monitor
│   ├ AI Operator
│   ├ AI Reasoning
│   ├ Alert Engine
│   ├ Risk Monitor
│   ├ Decision Log
│   ├ Watch List
│   ├ Timeline
│   └ AI Conversation
│
├ Collector
├ Health
├ Logs
├ Config
├ Research
└ Replay
24. Long Term Vision

BTC-TS Operator UI は

AI Trading War Room

として進化する。

最終構造

Human
+
AI Agents
+
Live Market

の 共同意思決定システム。