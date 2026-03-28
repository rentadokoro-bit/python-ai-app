# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## セットアップ・起動

```bash
# 依存パッケージのインストール
pip install -r requirements.txt

# APIキーの設定（ファイルで管理する場合）
cp .env.example .env
# .env を編集して GEMINI_API_KEY を設定

# アプリ起動
streamlit run app.py
```

APIキーはUIのサイドバーからも入力可能（`st.session_state["api_key"]` に保存される）。

## アーキテクチャ

シングルファイル構成（`app.py`）。すべてのツールが1ファイルに実装されている。

**ツール選択の仕組み**：サイドバーの `st.selectbox` で選んだ `tool` 変数の値で `if/elif` 分岐し、各ツールのUIと処理を描画する。新しいツールを追加するには、selectboxのリストに追加し、対応する `elif` ブロックを末尾に追加するだけ。

**Gemini API呼び出しの流れ**：
- `get_api_key()` → セッション or 環境変数からAPIキー取得
- `get_gemini_model()` → `genai.configure()` してモデルを返す（毎回 configure を呼ぶ設計）
- `generate(prompt)` → 実際の生成。エラーはそのまま `st.error()` で表示し空文字を返す

使用モデル: `gemini-2.5-flash`

## 実装済みツール

| ツール名（selectbox値） | 機能 |
|---|---|
| `📝 ブログ記事執筆` | テーマ・文体・長さ指定でMarkdown記事を生成 |
| `📧 メール返信文作成` | 受信メール貼り付けで返信文を生成 |
| `📋 文章要約` | 複数スタイル（箇条書き/短文/詳細/ELI5）で要約 |
| `✏️ 文章校正・改善` | 誤字修正・表現改善・修正理由の説明付き |
| `📱 SNS投稿文作成` | X/Instagram/Facebook/LinkedIn等、SNS別に最適化 |
| `💡 タイトル・見出し生成` | テーマまたは文章からタイトル案を複数生成 |

各ツールは生成結果を `st.download_button` でダウンロードできる。

## 新しいツールを追加する手順

1. `app.py` のサイドバー `st.selectbox` リストに `"🆕 ツール名"` を追記
2. ファイル末尾に `elif tool == "🆕 ツール名":` ブロックを追加
3. ブロック内で `generate(prompt)` を呼び出し、結果を `st.markdown()` で表示
4. `st.download_button` でダウンロード対応

## 設計上の注意点

- `generate()` は失敗時に空文字 `""` を返す（`None` ではない）。結果の有無は `if result:` で判定する
- `get_gemini_model()` は呼び出しのたびに `genai.configure()` を実行する設計。APIキーが動的に変わることを想定している
- モデル名 `gemini-2.0-flash` はアプリ全体で共通。変更する場合は `get_gemini_model()` の1箇所のみ修正する
- Streamlit はスクリプトを上から再実行する仕組みのため、状態の保持が必要な場合は `st.session_state` を使う

## Gemini API の制約

- 無料枠: 1分あたり15リクエスト、1日1500リクエスト（2025年時点）
- 長文入力（文章要約など）はトークン上限に注意。`gemini-2.5-flash` の入力上限は100万トークン
- APIキーは `.env` ファイルか環境変数 `GEMINI_API_KEY` で管理し、コードにハードコードしない

## 環境変数

| 変数名 | 必須 | 説明 |
|---|---|---|
| `GEMINI_API_KEY` | 任意 | UIからも入力可能。両方設定時はUIが優先 |
