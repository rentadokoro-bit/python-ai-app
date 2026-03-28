import streamlit as st
import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()

# ページ設定
st.set_page_config(
    page_title="AI ライティングツール",
    page_icon="✍️",
    layout="wide",
)

# Gemini API設定
def get_api_key():
    return st.session_state.get("api_key") or os.getenv("GEMINI_API_KEY", "")

def get_gemini_model():
    api_key = get_api_key()
    if not api_key:
        return None
    genai.configure(api_key=api_key)
    return genai.GenerativeModel("gemini-2.5-flash")

def generate(prompt: str) -> str:
    model = get_gemini_model()
    if model is None:
        st.error("APIキーが設定されていません。サイドバーからGemini APIキーを入力してください。")
        return ""
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        st.error(f"エラーが発生しました: {e}")
        return ""

# ---- サイドバー ----
with st.sidebar:
    st.title("✍️ AI ライティングツール")
    st.markdown("---")

    # APIキー入力
    api_key_input = st.text_input(
        "Gemini APIキー",
        type="password",
        value=st.session_state.get("api_key", ""),
        placeholder="AIza...",
        help="Google AI StudioでAPIキーを取得してください",
    )
    if api_key_input:
        st.session_state["api_key"] = api_key_input

    st.markdown("---")

    # ツール選択
    tool = st.selectbox(
        "ツールを選択",
        [
            "📝 ブログ記事執筆",
            "📧 メール返信文作成",
            "📋 文章要約",
            "✏️ 文章校正・改善",
            "📱 SNS投稿文作成",
            "💡 タイトル・見出し生成",
        ],
    )

    st.markdown("---")
    st.markdown(
        """
        **使い方**
        1. APIキーを入力
        2. ツールを選択
        3. 必要情報を入力
        4. 生成ボタンをクリック
        """
    )

# ---- メインコンテンツ ----

if tool == "📝 ブログ記事執筆":
    st.header("📝 ブログ記事執筆")
    st.markdown("テーマや要件を入力すると、ブログ記事を自動生成します。")

    col1, col2 = st.columns(2)
    with col1:
        topic = st.text_input("テーマ・タイトル *", placeholder="例: 初心者向けPythonプログラミング入門")
        tone = st.selectbox("文体・トーン", ["です・ます調（丁寧）", "だ・である調（論説）", "カジュアル・友好的", "プロフェッショナル"])
    with col2:
        target = st.text_input("ターゲット読者", placeholder="例: プログラミング未経験の20代社会人")
        length = st.selectbox("記事の長さ", ["短め（500字程度）", "標準（1000〜1500字）", "長め（2000字以上）"])

    keywords = st.text_input("キーワード（カンマ区切り）", placeholder="例: Python, 初心者, プログラミング")
    extra = st.text_area("その他の指示・補足", placeholder="例: SEOを意識して書いてください。見出しを使って構造化してください。", height=80)

    if st.button("記事を生成する", type="primary", use_container_width=True):
        if not topic:
            st.warning("テーマを入力してください。")
        else:
            with st.spinner("記事を生成中..."):
                prompt = f"""あなたはSEOに精通したプロのブログライターです。以下の条件で、検索上位を狙えるブログ記事を日本語で書いてください。

## 記事の基本情報
- テーマ: {topic}
- ターゲット読者: {target or "一般読者"}
- 文体: {tone}
- 記事の長さ: {length}
{"- メインキーワード: " + keywords if keywords else ""}
{"- 追加指示: " + extra if extra else ""}

## SEOの要件
- 記事の冒頭100〜150字以内にメインキーワードを自然に含める
- H2見出しにキーワードまたは関連語句を含める
- 検索意図（知りたい・やりたい・行きたいなど）に応えた構成にする
- 読者が検索で求めている疑問に対して、冒頭で結論を先に伝える（PREP法）
- 各段落は4〜5行以内に収め、スキャンしやすくする
- 箇条書きや表を活用して情報を整理する
- 記事の末尾にまとめと次のアクション（CTA）を入れる

## 出力形式
マークダウン形式で以下の構成で出力してください：
1. メタディスクリプション（120字前後、キーワードを含む）
2. 本文（# タイトル → ## 見出し → 本文 の階層構造）
3. まとめ"""
                result = generate(prompt)
                if result:
                    st.markdown("---")
                    st.subheader("生成された記事")
                    st.markdown(result)
                    st.download_button("テキストでダウンロード", result, file_name="blog_article.md", mime="text/markdown")

elif tool == "📧 メール返信文作成":
    st.header("📧 メール返信文作成")
    st.markdown("受信したメールの内容を貼り付けると、返信文を生成します。")

    received_mail = st.text_area("受信メールの内容 *", placeholder="ここに受信したメールの本文を貼り付けてください...", height=200)

    col1, col2 = st.columns(2)
    with col1:
        reply_tone = st.selectbox("返信のトーン", ["丁寧・フォーマル", "友好的・カジュアル", "簡潔・ビジネスライク", "お詫び・謝罪"])
        sender_name = st.text_input("送信者名（自分の名前）", placeholder="例: 山田 太郎")
    with col2:
        reply_intent = st.selectbox("返信の意図", ["承諾・了解", "断り・辞退", "質問・確認", "お礼・感謝", "情報提供", "その他"])
        recipient_name = st.text_input("宛先の名前", placeholder="例: 鈴木 花子")

    extra_notes = st.text_area("補足・追加したい内容", placeholder="例: 来週火曜日以降なら都合が良い旨も加えてください。", height=80)

    if st.button("返信文を生成する", type="primary", use_container_width=True):
        if not received_mail:
            st.warning("受信メールの内容を入力してください。")
        else:
            with st.spinner("返信文を生成中..."):
                prompt = f"""以下の受信メールに対する返信文を日本語で作成してください。

【受信メール】
{received_mail}

【返信の条件】
- トーン: {reply_tone}
- 返信の意図: {reply_intent}
{"- 送信者名: " + sender_name if sender_name else ""}
{"- 宛先名: " + recipient_name if recipient_name else ""}
{"- 補足・追加内容: " + extra_notes if extra_notes else ""}

件名（Re:）から始めて、宛先・本文・署名の形式で返信メールを書いてください。"""
                result = generate(prompt)
                if result:
                    st.markdown("---")
                    st.subheader("生成された返信文")
                    st.text_area("返信文", result, height=300)
                    st.download_button("テキストでダウンロード", result, file_name="email_reply.txt", mime="text/plain")

elif tool == "📋 文章要約":
    st.header("📋 文章要約")
    st.markdown("長い文章を貼り付けると、要点をまとめて要約します。")

    original_text = st.text_area("要約したい文章 *", placeholder="ここに要約したい文章を貼り付けてください...", height=250)

    col1, col2 = st.columns(2)
    with col1:
        summary_style = st.selectbox(
            "要約スタイル",
            ["箇条書き（ポイントを列挙）", "短文要約（1〜3文）", "詳細要約（構造を保持）", "ELI5（わかりやすく説明）"],
        )
    with col2:
        summary_length = st.selectbox("要約の長さ", ["極短（100字以内）", "短め（200字程度）", "標準（400字程度）", "長め（600字以上）"])

    focus = st.text_input("重点的にまとめたい観点（任意）", placeholder="例: コスト・費用に関する部分を重点的に")

    if st.button("要約する", type="primary", use_container_width=True):
        if not original_text:
            st.warning("要約したい文章を入力してください。")
        else:
            with st.spinner("要約中..."):
                prompt = f"""以下の文章を日本語で要約してください。

【文章】
{original_text}

【要約の条件】
- スタイル: {summary_style}
- 長さ: {summary_length}
{"- 重点観点: " + focus if focus else ""}

重要なポイントを漏らさず、わかりやすく要約してください。"""
                result = generate(prompt)
                if result:
                    st.markdown("---")
                    col_orig, col_sum = st.columns(2)
                    with col_orig:
                        st.subheader("元の文章")
                        st.caption(f"{len(original_text)}文字")
                        st.text_area("元文", original_text, height=200, disabled=True)
                    with col_sum:
                        st.subheader("要約")
                        st.caption(f"{len(result)}文字")
                        st.markdown(result)
                    st.download_button("要約をダウンロード", result, file_name="summary.txt", mime="text/plain")

elif tool == "✏️ 文章校正・改善":
    st.header("✏️ 文章校正・改善")
    st.markdown("文章を貼り付けると、誤字脱字の修正や表現の改善を行います。")

    original_text = st.text_area("校正・改善したい文章 *", placeholder="ここに校正・改善したい文章を入力してください...", height=250)

    col1, col2 = st.columns(2)
    with col1:
        fix_type = st.multiselect(
            "改善の種類",
            ["誤字脱字の修正", "文法・語法の修正", "表現の自然化", "読みやすさの向上", "敬語の統一"],
            default=["誤字脱字の修正", "表現の自然化"],
        )
    with col2:
        target_tone = st.selectbox("目標とする文体", ["現状を維持", "より丁寧に", "よりカジュアルに", "よりプロフェッショナルに", "より簡潔に"])

    explain = st.checkbox("修正箇所と理由も説明する", value=True)

    if st.button("校正・改善する", type="primary", use_container_width=True):
        if not original_text:
            st.warning("校正したい文章を入力してください。")
        else:
            with st.spinner("校正・改善中..."):
                fix_list = "、".join(fix_type) if fix_type else "総合的な改善"
                prompt = f"""以下の文章を校正・改善してください。

【元の文章】
{original_text}

【改善の条件】
- 改善種類: {fix_list}
- 目標文体: {target_tone}
{"- 修正箇所と理由も合わせて説明してください。" if explain else "- 改善後の文章のみを出力してください。"}

{"【出力形式】まず改善後の全文を出力し、その後に「【修正・改善のポイント】」として箇条書きで説明してください。" if explain else ""}"""
                result = generate(prompt)
                if result:
                    st.markdown("---")
                    st.subheader("校正・改善結果")
                    st.markdown(result)
                    st.download_button("結果をダウンロード", result, file_name="corrected_text.txt", mime="text/plain")

elif tool == "📱 SNS投稿文作成":
    st.header("📱 SNS投稿文作成")
    st.markdown("伝えたい内容を入力すると、各SNSに最適化した投稿文を生成します。")

    content = st.text_area("投稿したい内容・伝えたいこと *", placeholder="例: 新しいカフェに行って美味しいラテアートのコーヒーを飲んだ体験を投稿したい", height=120)

    col1, col2 = st.columns(2)
    with col1:
        platform = st.multiselect(
            "投稿するSNS",
            ["X（Twitter）", "Instagram", "Facebook", "LinkedIn", "Threads", "Note"],
            default=["X（Twitter）", "Instagram"],
        )
    with col2:
        sns_tone = st.selectbox("投稿のトーン", ["カジュアル・親しみやすい", "プロフェッショナル", "エンタメ・おもしろい", "感情的・共感を呼ぶ"])

    use_hashtag = st.checkbox("ハッシュタグを含める", value=True)
    use_emoji = st.checkbox("絵文字を含める", value=True)

    if st.button("投稿文を生成する", type="primary", use_container_width=True):
        if not content:
            st.warning("投稿したい内容を入力してください。")
        elif not platform:
            st.warning("投稿するSNSを選択してください。")
        else:
            with st.spinner("投稿文を生成中..."):
                platform_list = "、".join(platform)
                prompt = f"""以下の内容をもとに、各SNS向けの投稿文を日本語で作成してください。

【投稿内容】
{content}

【条件】
- 対象SNS: {platform_list}
- トーン: {sns_tone}
{"- ハッシュタグを適切に含めてください。" if use_hashtag else "- ハッシュタグは不要です。"}
{"- 絵文字を効果的に使ってください。" if use_emoji else "- 絵文字は不要です。"}

各SNSの特性（文字数制限、ユーザー層、文化）に合わせた投稿文を、SNSごとに分けて出力してください。"""
                result = generate(prompt)
                if result:
                    st.markdown("---")
                    st.subheader("生成された投稿文")
                    st.markdown(result)
                    st.download_button("投稿文をダウンロード", result, file_name="sns_posts.txt", mime="text/plain")

elif tool == "💡 タイトル・見出し生成":
    st.header("💡 タイトル・見出し生成")
    st.markdown("テーマや文章を入力すると、魅力的なタイトルや見出しを複数提案します。")

    input_type = st.radio("入力タイプ", ["テーマ・キーワードを入力", "文章を貼り付けてタイトルを生成"], horizontal=True)

    if input_type == "テーマ・キーワードを入力":
        theme_input = st.text_input("テーマ・キーワード *", placeholder="例: 在宅ワーク, 生産性向上, ライフハック")
    else:
        theme_input = st.text_area("文章 *", placeholder="タイトルを生成したい文章を貼り付けてください...", height=200)

    col1, col2 = st.columns(2)
    with col1:
        title_type = st.selectbox(
            "タイトルの種類",
            ["ブログ記事タイトル", "メールの件名", "SNS投稿のタイトル", "プレゼンのタイトル", "商品・サービス名"],
        )
        num_titles = st.slider("生成する数", min_value=3, max_value=10, value=5)
    with col2:
        title_style = st.multiselect(
            "タイトルのスタイル",
            ["数字を使ったもの（例: 5つの方法）", "疑問形", "インパクト重視", "SEO最適化", "感情に訴えるもの"],
            default=["数字を使ったもの（例: 5つの方法）", "インパクト重視"],
        )

    if st.button("タイトル・見出しを生成する", type="primary", use_container_width=True):
        if not theme_input:
            st.warning("テーマまたは文章を入力してください。")
        else:
            with st.spinner("生成中..."):
                style_list = "、".join(title_style) if title_style else "バリエーション豊富に"
                if input_type == "テーマ・キーワードを入力":
                    input_desc = f"テーマ・キーワード: {theme_input}"
                else:
                    input_desc = f"以下の文章のタイトルを生成してください:\n{theme_input}"

                prompt = f"""以下の条件で{title_type}のタイトル・見出しを{num_titles}個、日本語で生成してください。

【入力】
{input_desc}

【条件】
- 種類: {title_type}
- スタイル: {style_list}

各タイトルに番号をつけて列挙し、それぞれ簡単な採用理由（1行）も添えてください。"""
                result = generate(prompt)
                if result:
                    st.markdown("---")
                    st.subheader("生成されたタイトル・見出し")
                    st.markdown(result)
                    st.download_button("タイトル一覧をダウンロード", result, file_name="titles.txt", mime="text/plain")
