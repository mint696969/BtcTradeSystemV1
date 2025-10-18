# BtcTradeSystem 運転モードと監査（使い方・仕様・調べ方）

運転モードと監査（使い方・仕様・調べ方）


## モードの目的と出力差分
PROD（本番）
監査: 最小限（*.start, dashboard.poll, 重大イベントのみ）
性能優先。UIは通常表示。
想定用途: 24/7 運用監視。

DEBUG（開発・検証）
監査: 主要関数入口/例外を追加記録（I/O詳細は抑制）。
想定用途: UI/ロジックのふるまい確認・軽い不具合切り分け。

DIAG（詳細診断）
監査: ファイルI/O（file.write 等）、ヘルス遷移（collector.health）を詳細記録。
想定用途: 原因特定（どのプロセス/モジュール/行がいつ何をしたか）。
監査ファイル: logs/audit.jsonl（JSON Lines）


## 変更・永続化の方針（実装予定）
**UI（設定パネル）**でモードを切替 → config/settings.yaml の runtime.mode に保存（分散禁止）。
切替直後は 即時反映（obs.setup を再初期化）、再起動後も同じ設定で起動。


## 監査イベントの読み方
各行は JSON。主なキー:
ts … ISO時刻（UTC）
actor … 常に "system"（将来、ユーザー操作も識別予定）
component … dashboard / collector / app 等（＝どのコンポーネント）
source … module/file/line/func（＝どのファイルのどの行）
action … イベント種別（例: dashboard.start, dashboard.poll, collector.health, file.write）
target … 対象（例: apps.dashboard, collector.bitflyer, 書き込んだファイルパス）
detail … 補足（例: {"level":"CRIT"}, {"append":true}）
mode … PROD / DEBUG / DIAG


## 何が分かるか（モード別の“見える化”）
PROD
起動/再実行周期、重大なヘルス遷移（OK→WARN/CRIT）だけを素早く把握。

DEBUG
UIタブ切替や主要処理の“入口”が見える → どの操作で何が動いたか分かる。

DIAG
どのファイルが書いたか（file.writeのtarget）、
どの行が判定を出したか（source.file/source.line）、
どの取引所の状態が変わったか（collector.healthのdetail.level）まで追跡可能。


## 問題点の洗い出し手順（PowerShell 例）
すべて repo 直下 で実行

最新50件を監視
Get-Content .\logs\audit.jsonl -Tail 50 -Wait

特定コンポーネントだけ（例: collector）
Get-Content .\logs\audit.jsonl | Select-String '"component":\s*"collector"'

CRIT だけ抽出
Get-Content .\logs\audit.jsonl | Select-String '"collector.health".*"CRIT"'

どのファイルが書いた？（file.write 一覧）
Get-Content .\logs\audit.jsonl | Select-String '"action":\s*"file.write"'

bitflyer の状態遷移の時系列
Get-Content .\logs\audit.jsonl | Select-String '"collector.health".*"bitflyer"'

ダッシュボードの再実行周期確認（dashboard.poll）
Get-Content .\logs\audit.jsonl | Select-String '"action":\s*"dashboard.poll"'

さらに深掘りしたい場合は VSCode の “検索（正規表現）” で \"action\":\s*\"collector\.health\".*\"CRIT\" を使うと速い。


## 典型的な調査ストーリー
ヘルスの赤/黄をUIで確認 → 同時刻の collector.health を検索
直前の file.write で当該取引所のファイル更新が滞っていないか確認
source.file/line で 判断を出したコード位置を特定 → 実装へジャンプ
必要に応じて DEBUG→DIAG に切替、再現して詳細ログを追加収集
修正後、PROD に戻して監査出力量を絞る


## 運用の注意
監査ファイルはローテーション前提（将来 max_bytes / backup_count を設定UIから変更可）。
本番（PROD）では最小記録が原則。問題発生時だけ DIAG に上げて短時間で原因採取 → 速やかに PROD へ戻す。


## 今後の拡張（計画）
actor にユーザー操作を反映（ボタン押下・設定変更）。
trace_id による一連処理のひも付け。
監査ビューア（UIタブ）でのフィルタ/検索/可視化。
