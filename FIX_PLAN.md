# FIX_PLAN

VALIDATION_PLAN.md レビューの残件。詳細と背景は QandA.md 参照。

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

## Phase 0 実機検証（2026-08-17、Step 0〜8実施）

- [x] Step 0〜4: 環境確認・セットアップ・データ取得・CLI検索/集計をすべて実行し成功（詳細は `validation-results.md`）
- [x] Step 5: dataset.yamlの設計確認（NULL/欠損、コード値、computed measures、provenance/notes/quality_summary）
- [x] Step 6: MCPの4ツールを `apcli describe` で確認
- [x] Step 7: `apcli preview` のUI起動を確認。Chrome内蔵AIはヘッドレスのため未確認
- [x] Step 8: Claude CodeからMCP接続し2問実行。ツール名・引数・サーバー側検証エラーを記録
- [x] 記事側の主張A1〜A16を列挙し、11件（A1,A2,A3,A6,A7,A8,A10,A11,A14,A15,A16）の一致を確認

## 要判断（QandA.md参照、回答待ち）

- [ ] Q3: 「十分な空き容量」の具体的な閾値を決める（実測値は得たが正式な数値を明記するか）（重大度: 低）
- [ ] Q4: 停止条件の「代替環境」の範囲を定義する（重大度: 低）
- [ ] Q5: Step 6の質問例に公式README掲載の例を追加するか（重大度: 低・任意）
- [ ] Q6: MCP 2026-07-28／FastMCP4系プレリリースを検証対象に含めるか対象外とするか（重大度: 低）
- [ ] Q9: `claude -p --allowedTools` がBashを遮断できなかった件への対応方針（重大度: 中）
- [ ] Q10: 未確認のまま残る4項目（MCP Apps UI描画／フェーズ1・2基準日／Chrome内蔵AI実操作／MCP仕様バージョン`/health`）をPhase 0完了の必須条件にするか（重大度: 低〜中）
