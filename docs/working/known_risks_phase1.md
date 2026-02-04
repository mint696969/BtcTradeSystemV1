util解除側（clear窓）が実装されていない可能性

no_data判定が単純すぎる設計

endpoint / topic の概念混在

## 1. rate_state の監査スパム化リスク
対象ファイル: ./btcts_next/src/btcts/collector/scheduler.py
箇所: rate_state_every_sec 間隔で write_rate_state(..., emit_audit=True) を継続
理由: Phase2でログ肥大・ディスク圧迫の火種になりやすい（Phase1では許容だが、後で必ず整理が要る）



対象ファイル: ./btcts_next/src/btcts/collector/scheduler.py
EndpointState に last_try_ts があるが status/items 出力に未反映
対象ファイル: scheduler.py
理由: 「試行しているが成功していない」可視化が将来欲しくなる可能性（Phase1では不要）