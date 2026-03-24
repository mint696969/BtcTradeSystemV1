# 監査（Audit）仕様差分メモ（2026-03-24 / Exploration Runtime 反映）

対象元文書:
- `docs/systems/collector/監査（Audit）＋派生サマリ 正式仕様書.md`

この差分メモは、元文書を全面書き換えずに **Exploration Runtime 主役化で変わった点だけ** を整理する。

---

## 1. 新しく重要になったイベント
Exploration Runtime 主役化により、以下の audit event が運用上の重要イベントになった。

### request completed / failed
- `collector_vnext.exploration.board_snapshot.completed`
- `collector_vnext.exploration.board_snapshot.failed`
- `collector_vnext.exploration.rest_trades.completed`
- `collector_vnext.exploration.rest_trades.failed`

### mode changed
- `collector_vnext.exploration.mode.changed`

payload の主項目:
- `from_mode`
- `to_mode`
- `exchange`
- `request_class`
- `status_code`
- `retry_after_sec`

---

## 2. mode.changed の扱い
従来の `rate_control.engaged / released` 中心の考え方に対し、Exploration Runtime では **mode.changed が一次的な運用判断材料** になる。

特に重要な topic:
- `crit`
- `recovery`
- `normal`

これらは Health の recent events / anomalies でも観測対象とする。

---

## 3. Health への接続
Health 側では `collector_vnext.exploration.mode.changed` を recent anomalies と continuity 判定に取り込む。

意味:
- `crit` は制限強化
- `recovery` は復帰開始
- `normal` は復帰完了

---

## 4. current audit 運用での注意
Exploration Runtime では completed/failed が高頻度で出るため、audit の読み方は以下を基本とする。
- completed が継続している → 生存と継続取得の証拠
- failed が連発している → request class 側異常の疑い
- mode.changed が `crit/recovery/normal` と流れる → 429 系制御が期待どおり働いている証拠

---

## 5. 今後の派生サマリ候補
派生サマリに追加価値がある候補:
- mode changed 回数（crit/recovery/normal）
- request class別 completed / failed / 429 集計
- active_target_ratio の日次要約
- utilization の max / avg / p95

---

## 6. 既知の Risk
1. completed/failed の高頻度出力により audit が肥大しやすい  
   - 派生サマリ側で集約が重要。
2. mode.changed は比較位置を誤ると取りこぼしやすい  
   - 現行実装では scheduler export_state ベースで補正済み。
3. audit 本体は exploration の current overlay に比べると時系列正本性が弱い箇所が残る  
   - 正本 state と併読する前提を維持する。
