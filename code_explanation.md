# PythonとGemini APIで作るAIライティングツール — コード解説

## 全体構成

このアプリは **1ファイル（`app.py`）** だけで動いています。構成は大きく3つのブロックに分かれています。

```
app.py
├── ① 初期設定・Gemini API接続（1〜36行目）
├── ② サイドバーUI（38〜78行目）
└── ③ 各ツールのUI・処理（80〜347行目）
```

---

## ① 初期設定・Gemini API接続

```python
import streamlit as st
import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()
```

最初にライブラリを読み込みます。`load_dotenv()` は `.env` ファイルを読んで `GEMINI_API_KEY` などの環境変数を使えるようにします。

```python
def get_api_key():
    return st.session_state.get("api_key") or os.getenv("GEMINI_API_KEY", "")
```

APIキーの取得は「UIで入力したもの」と「`.env` ファイルのもの」の2経路に対応しています。UIが優先されます。

```python
def get_gemini_model():
    api_key = get_api_key()
    if not api_key:
        return None
    genai.configure(api_key=api_key)
    return genai.GenerativeModel("gemini-2.5-flash")
```

Geminiのモデルオブジェクトを返す関数です。APIキーがなければ `None` を返して処理を止めます。

```python
def generate(prompt: str) -> str:
    model = get_gemini_model()
    if model is None:
        st.error("APIキーが設定されていません。")
        return ""
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        st.error(f"エラーが発生しました: {e}")
        return ""
```

アプリ全体で唯一の「AI呼び出し口」です。どのツールもこの `generate()` にプロンプト文字列を渡すだけで使えます。失敗時は空文字 `""` を返します。

---

## ② サイドバーUI

```python
with st.sidebar:
    # APIキー入力フォーム
    api_key_input = st.text_input("Gemini APIキー", type="password", ...)
    if api_key_input:
        st.session_state["api_key"] = api_key_input

    # ツール選択ドロップダウン
    tool = st.selectbox("ツールを選択", ["📝 ブログ記事執筆", "📧 メール返信文作成", ...])
```

サイドバーには2つの役割があります。

- **APIキーの受け取り** → `st.session_state` に保存してページをまたいで保持
- **ツールの切り替え** → 選ばれた値が `tool` 変数に入る

---

## ③ ツールの切り替えと処理

```python
if tool == "📝 ブログ記事執筆":
    ...
elif tool == "📧 メール返信文作成":
    ...
elif tool == "📋 文章要約":
    ...
```

`tool` の値で `if/elif` 分岐するシンプルな構造です。各ブロックの中身はすべて同じパターンで書かれています。

**各ツールの共通パターン：**

```
1. st.text_input / st.text_area でユーザーの入力を受け取る
2. st.button でボタンを表示
3. ボタンが押されたら prompt 文字列を組み立てる
4. generate(prompt) でGeminiに投げる
5. 結果を st.markdown で表示
6. st.download_button でダウンロードボタンを表示
```

例として「ブログ記事執筆」ツールを見てみます。

```python
# ユーザーの入力を受け取る
topic = st.text_input("テーマ・タイトル *")
tone = st.selectbox("文体・トーン", ["です・ます調", ...])

# ボタンが押されたらプロンプトを組み立てて送信
if st.button("記事を生成する"):
    prompt = f"""テーマ: {topic}
文体: {tone}
マークダウン形式で記事を書いてください。"""
    result = generate(prompt)
    st.markdown(result)
    st.download_button("ダウンロード", result, file_name="blog_article.md")
```

ユーザーが選んだ設定（文体・長さ・ターゲットなど）をそのままプロンプト文字列に埋め込んでいるのがポイントです。**UIの選択肢 = プロンプトの指示** という直感的な設計になっています。

---

## データの流れまとめ

```
ユーザーが入力
    ↓
st.text_input / st.selectbox などで値を取得
    ↓
f-string でプロンプト文字列を組み立てる
    ↓
generate(prompt) → Gemini API に送信
    ↓
response.text を受け取る
    ↓
st.markdown() で画面に表示
st.download_button() でダウンロード可能にする
```

---

## このコードの特徴

| 特徴 | 説明 |
|---|---|
| シングルファイル | `app.py` 1本で完結。分割不要なシンプルさ |
| AIの差し替えが容易 | `get_gemini_model()` の1箇所だけ変えればモデル変更できる |
| ツールの追加が簡単 | selectboxにリスト追加 + `elif` ブロックを1つ足すだけ |
| Streamlitの再実行モデル | ボタンを押すたびにスクリプトが上から再実行される。状態保持が必要なものだけ `st.session_state` を使う |
