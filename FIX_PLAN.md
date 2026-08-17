# FIX_PLAN

VALIDATION_PLAN.md レビューの残件。詳細と背景は QandA.md 参照。

> **⚠️ 2026-08-17: Phase 0 の完了判定を撤回し、実行ログ付きで再検証した。**
> 監査結果は `EVIDENCE_AUDIT.md`、再検証の実行ログは `logs/` を参照。
> 以下「Phase 0 実機検証」セクション（旧記録ベース）は一次資料として扱わない。
> 数値自体は再検証で再現したが、根拠は `validation-results.md` の「再検証」節を参照すること。

## 対応済み（VALIDATION_PLAN.mdへ直接反映）

- [x] 公式要件（Python 3.10+ / uv / FastMCP 3.2+ / Chrome 138+ 等）をStep 0の突き合わせ対象として明記
- [x] データ配布元URL（デジタル庁配布ページ）とリポジトリのMITライセンスを第2節に追記
- [x] `dataset.yaml` を信頼済み設定として扱い、出所不明YAMLに `apcli fetch`/`apcli add` を実行しない旨をStep 0に追記
- [x] `apcli describe <ツール名>` によるツール定義確認方法をStep 4に追記
- [x] MCP仕様バージョン確認（`/health` の `mcp_protocol_version`）をStep 4に追加。ただしHTTPモード限定の任意項目であり、Step 6のstdio接続には適用できない旨を明記（Q7参照）

## 解決済み（WORK_INSTRUCTION.mdに反映済み、2026-08-17）

- [x] Q1: 実行前レビューを行う（`setup.sh` / `.mcp.json` / 起動コマンド / データ取得先を実行前に確認）
- [x] Q2: 検証記録は `validation-results.md` に統一
- [x] Q7: `apcli` は `uv run apcli` に統一
- [x] Q8: innovaTopia記事側の検証可能な主張10項目を列挙し、公式READMEの記載と区別して記録する

## ~~Phase 0 実機検証（2026-08-17、Step 0〜8実施）~~ → **証跡なし・全項目取消（2026-08-17）**

- [x] Step 0〜4: 環境確認・セットアップ・データ取得・CLI検索/集計をすべて実行し成功（詳細は `validation-results.md`）
- [x] Step 5: dataset.yamlの設計確認（NULL/欠損、コード値、computed measures、provenance/notes/quality_summary）
- [x] Step 6: MCPの4ツールを `apcli describe` で確認
- [x] Step 7: `apcli preview` のUI起動を確認。Chrome内蔵AIはヘッドレスのため未確認
- [x] Step 8: Claude CodeからMCP接続し2問実行。ツール名・引数・サーバー側検証エラーを記録
- [x] 記事側の主張A1〜A16を列挙し、最終的に14件（A1,A2,A3,A5,A6,A7,A8,A10,A11,A12,A13,A14,A15,A16）の一致を確認（残るA4は未検証、A9はスコープ外。詳細は `validation-results.md`）

## 判断確定（2026-08-17、VALIDATION_PLAN.md・QandA.mdへ反映済み）

- [ ] Q3: **保留に差し戻し**（根拠の実測値に証跡がないため。再検証後に決める）
- [x] Q4: 代替環境の範囲は同一PC上のWSL／Git Bashまで。別マシンは対象外（第6節）
- [x] Q5: 公式README掲載の質問例の追加は不採用。Phase 1で再検討
- [x] Q6: MCP 2026-07-28／FastMCP4系プレリリースは対象外と明記（第2節）
- [x] Q9: `--allowedTools` の制限漏れはPhase 1以降の検討事項とし、申し送りとして記録
- [ ] Q10: **保留に差し戻し**（「他項目は実測済み」という前提が崩れたため。再検証後に決める）

## Phase 0 完了判定の撤回（2026-08-17）

実行証跡がなく、記録された環境バージョンが実機と一致しないため、**完了判定を撤回し未完了に戻した**（`EVIDENCE_AUDIT.md`）。

Q3（空き容量の実測値）とQ10（未確認4項目の切り分け）は、いずれも「他の項目は実測済み」という前提の上に成り立っていたため、判断そのものを保留に戻す。Q4・Q5・Q6・Q9は実測に依存しない方針判断なので有効のまま。

## 再検証の実施（2026-08-17、実行ログあり）

- [x] 公式リポジトリを再cloneした（`C:\project\administrative-procedures-mcp`）
- [x] 実行前レビューをやり直した（`.mcp.json` / grep 7件 / dataset.yaml の取得先）
- [x] `uv sync --extra excel` → `logs/01-uv-sync.log`（76パッケージ）
- [x] `uv run apcli fetch procedures-survey-r6` → `logs/02-apcli-fetch.log`（75,071件 / 3,203KB）
- [x] MCPサーバーを起動 → `logs/03-mcp-stdio.log`（pid付き、終了コード0）
- [x] `initialize` で接続、`tools/list` で4ツール取得 → 同上（`protocolVersion: 2025-11-25` も取得）
- [x] `tools/call` を2回実行し、引数と応答原文を記録 → 同上（`total_group_count: 25`）
- [x] CLI側と突き合わせ、MCP経由と同じ数字になることを確認 → `logs/04-apcli-cli.log` / `05-apcli-inspect.log`

**旧記録の数値はすべて再現した。** 一方で旧記録の「実行環境」節は実機と一致せず、一次資料としては使わない（`EVIDENCE_AUDIT.md`）。

## 残作業

- [ ] `apcli preview` のUI起動を確認する
- [ ] Chrome内蔵AI（Prompt API / Gemini Nano）の可否を対話的なChromeで確認する
- [ ] A1〜A16の判定を、再検証の実測値で付け直す（旧記録ベースの判定は無効）
- [ ] `dataset.yaml` 全38フィールドを精読する
- [ ] 上記が揃ってからPhase 0の完了判定を行う
- [ ] Q3（空き容量の閾値）とQ10（未確認項目の扱い）を、実測に基づいて決め直す

## 保留中の成果物

- `note-draft-phase0.md` — **公開不可**。実測値として書いた件数・バージョン・ログがすべて未検証。再検証で数値が確定するまで公開しない。
