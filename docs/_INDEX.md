# path: ./docs/_INDEX.md
# desc: docs配下の索引（リンク集）。仕様書一式など主要ドキュメントへの導線。

この `docs/_INDEX.md` が **docs の正準入口**です。

> 仕様書は増減します。ファイル一覧に依存せず、導線はここで管理します。

## 1. 正準（まずここを見る）
- 仕様書一式の入口: `docs/仕様書一式/README.md`
- 仕様書（完成版）: `docs/仕様書一式/`
- Phase2: 監査（Audit）＋派生サマリ: `docs/仕様書一式/監査（Audit）＋派生サマリ 正式仕様書.md`

## 2. 補助（ツール手順・サンプル）
- `docs/tools/`（各テスト・運用スクリプト仕様）
- `docs/placeholders/`（サンプル）

## 3. 参考（原則 repo には置かない）
- 作業メモ・引継ぎ・途中経過は `tmp/gpt_room/` に置く

## 4. 非正準（原則参照しない）
- `docs/working/**`（ドラフト置き場は作らない。必要なら `tmp/gpt_room/_cold/` に退避して明示参照）

## 5. 最新一覧（補助）
- tmp: `tmp/gpt_room/_generated/DOCS_INDEX.md`（Utilities生成）

> `DOCS_INDEX.md` は正準ではないが、増減するファイルの「最新一覧」を見る用途で便利。
