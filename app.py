"""
GAVI - 英検準2級対策アプリケーション
Learn English, Enjoy the World

MVP Version 1.0
"""

import streamlit as st
import json
import random
from datetime import datetime, timedelta
from data_manager import DataManager
from claude_api import (
    score_writing_free, 
    evaluate_vocabulary_translation,
    free_talk,
    interview_simulation
)

# ============================================================
# ページ設定
# ============================================================

st.set_page_config(
    page_title="GAVI - 英検準2級対策",
    page_icon="🌈",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# CSS カスタマイズ
st.markdown("""
<style>
    * {
        margin: 0;
        padding: 0;
    }
    
    body {
        background: linear-gradient(180deg, #ffffff 0%, #f8f9fa 100%);
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    }
    
    .main {
        background-color: transparent;
    }
    
    /* ヘッダー */
    .header-title {
        font-size: 32px;
        font-weight: 700;
        background: linear-gradient(135deg, #4A90E2 0%, #28B448 50%, #FF6B35 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin-bottom: 10px;
    }
    
    .header-subtitle {
        font-size: 13px;
        color: #666;
        font-weight: 500;
    }
    
    /* カウントダウン */
    .countdown {
        background: linear-gradient(135deg, #FF6B35 0%, #FF8C42 100%);
        padding: 12px 16px;
        border-radius: 12px;
        color: white;
        text-align: right;
    }
    
    .countdown-number {
        font-size: 28px;
        font-weight: 700;
        line-height: 1;
    }
    
    .countdown-label {
        font-size: 11px;
        opacity: 0.9;
    }
    
    /* メニューボタン */
    .menu-button {
        background: white;
        border-radius: 12px;
        padding: 20px 16px;
        text-align: center;
        cursor: pointer;
        transition: all 0.3s ease;
        border: 1px solid #e8e8e8;
        text-decoration: none;
        color: #1a1a1a;
    }
    
    .menu-button:hover {
        transform: translateY(-4px);
        box-shadow: 0 12px 24px rgba(0, 0, 0, 0.12);
    }
    
    .menu-icon {
        font-size: 32px;
        margin-bottom: 8px;
    }
    
    .menu-label {
        font-size: 12px;
        font-weight: 600;
    }
    
    /* Progress Card */
    .phase-card {
        background: white;
        border-radius: 12px;
        padding: 16px;
        border: 1px solid #e8e8e8;
        border-left: 4px solid #4A90E2;
        transition: all 0.3s ease;
    }
    
    .phase-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.08);
    }
    
    .phase-name {
        font-size: 14px;
        font-weight: 600;
        color: #1a1a1a;
        margin-bottom: 8px;
    }
    
    .phase-date {
        font-size: 12px;
        color: #999;
        margin-bottom: 12px;
    }
    
    /* Status Card */
    .status-card {
        background: linear-gradient(135deg, #4A90E2 0%, #357ABD 100%);
        border-radius: 12px;
        padding: 24px;
        text-align: center;
        color: white;
    }
    
    .status-value {
        font-size: 36px;
        font-weight: 700;
        margin-bottom: 4px;
    }
    
    .status-subtitle {
        font-size: 13px;
        opacity: 0.9;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================
# セッション状態の初期化
# ============================================================

if "user_id" not in st.session_state:
    st.session_state.user_id = "user01"

if "current_page" not in st.session_state:
    st.session_state.current_page = "home"

if "word_index" not in st.session_state:
    st.session_state.word_index = 0

if "selected_category" not in st.session_state:
    st.session_state.selected_category = "verb"

# ============================================================
# ホーム画面
# ============================================================

def render_home():
    """ホーム画面のレンダリング"""
    
    # ヘッダー
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.markdown('<div class="header-title">🌈 GAVI</div>', unsafe_allow_html=True)
        st.markdown('<div class="header-subtitle">Learn English, Enjoy the World</div>', unsafe_allow_html=True)
    
    with col2:
        progress = DataManager.load_progress()
        days_left = progress.get("days_until_exam", 71)
        st.markdown(f"""
        <div class="countdown">
            <div class="countdown-number">{days_left}</div>
            <div class="countdown-label">Days Left</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.divider()
    
    # GAVI メッセージ
    col1, col2 = st.columns([1, 4])
    with col1:
        st.markdown("### 🌈")
    with col2:
        st.markdown("### Hello, Ria! 👋")
        st.markdown(
            "Today we're learning together. Let's explore the world through English!"
        )
    
    st.divider()
    
    # ステータスカード
    progress = DataManager.load_progress()
    exam_readiness = progress.get("exam_readiness", {})
    
    st.markdown("""
    <div class="status-card">
        <div style="font-size: 12px; opacity: 0.9; margin-bottom: 8px;">YOUR CURRENT LEVEL</div>
        <div class="status-value">+5 pts</div>
        <div class="status-subtitle">5 points to pass! You can do it!</div>
    </div>
    """, unsafe_allow_html=True)
    
    st.divider()
    
    # フェーズ進捗
    st.markdown("### 📊 Your Progress")
    
    phase_cards = [
        {
            "phase": 1,
            "name": "📚 Phase 1: Build Foundations",
            "badge": "ACTIVE",
            "date": "Jun 18 – Aug 12 (56 days)",
            "progress": 65,
            "color": "#4A90E2"
        },
        {
            "phase": 2,
            "name": "🇦🇺 Phase 2: Immersion in Australia",
            "badge": "COMING",
            "date": "Aug 13 – Aug 27 (14 days)",
            "progress": 0,
            "color": "#28B448"
        },
        {
            "phase": 3,
            "name": "🎯 Phase 3: Final Push",
            "badge": "LOCKED",
            "date": "Aug 28 – Sep 27 (31 days)",
            "progress": 0,
            "color": "#FF6B35"
        }
    ]
    
    for card in phase_cards:
        col1, col2, col3 = st.columns([3, 1, 1])
        
        with col1:
            st.markdown(f"""
            <div class="phase-card" style="border-left-color: {card['color']};">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                    <div class="phase-name">{card['name']}</div>
                    <span style="
                        background: rgba({int(card['color'][1:3], 16)}, {int(card['color'][3:5], 16)}, {int(card['color'][5:7], 16)}, 0.1);
                        color: {card['color']};
                        padding: 4px 8px;
                        border-radius: 6px;
                        font-size: 11px;
                        font-weight: 600;
                    ">{card['badge']}</span>
                </div>
                <div class="phase-date">{card['date']}</div>
                <div style="height: 6px; background: #f0f0f0; border-radius: 3px; overflow: hidden;">
                    <div style="height: 100%; background: {card['color']}; width: {card['progress']}%; border-radius: 3px;"></div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"<div style='text-align: right; font-size: 12px; font-weight: 600; color: {card['color']};'>{card['progress']}%</div>", unsafe_allow_html=True)
    
    st.divider()
    
    # メニュー
    st.markdown("### 📚 Start Learning")
    
    cols = st.columns(4)
    menu_items = [
        ("📖", "Vocabulary", "vocabulary"),
        ("🔲", "Fill in", "fill_in"),
        ("🔀", "Order", "order"),
        ("📄", "Reading", "reading"),
        ("✍️", "Writing", "writing"),
        ("🎤", "Interview", "interview"),
        ("💬", "Free Talk", "freetalk"),
        ("📊", "Analytics", "analytics")
    ]
    
    for idx, (icon, label, page_id) in enumerate(menu_items):
        col = st.columns(4)[idx % 4]
        with col:
            if st.button(f"{icon}\n\n{label}", key=f"menu_{page_id}", use_container_width=True):
                st.session_state.current_page = page_id
                st.rerun()

# ============================================================
# 単語学習：カテゴリー選択画面
# ============================================================

def render_vocabulary_categories():
    """単語学習のカテゴリー（品詞）選択画面"""

    st.markdown("## 📖 Vocabulary")
    st.markdown("カテゴリーを選んで学習しましょう")

    # 全体進捗
    overall = DataManager.get_overall_progress()
    st.markdown(f"""
    <div style="
        background: linear-gradient(135deg, #4A90E2 0%, #357ABD 100%);
        border-radius: 12px;
        padding: 20px;
        text-align: center;
        color: white;
        margin-bottom: 24px;
    ">
        <div style="font-size: 12px; opacity: 0.9; margin-bottom: 6px;">🏆 全体の進捗</div>
        <div style="font-size: 32px; font-weight: 700;">{overall['mastered']} / {overall['total']} 語</div>
        <div style="font-size: 14px; opacity: 0.9;">マスター率 {overall['percentage']}%</div>
    </div>
    """, unsafe_allow_html=True)

    # 全体プログレスバー
    st.progress(overall['percentage'] / 100 if overall['total'] > 0 else 0)
    st.markdown("---")

    # カテゴリーごとのカード（2列）
    categories = DataManager.get_category_progress()
    cols = st.columns(2)
    for i, cat in enumerate(categories):
        with cols[i % 2]:
            pct = round((cat['mastered'] / cat['total']) * 100) if cat['total'] > 0 else 0
            # カード表示
            st.markdown(f"""
            <div style="
                background: white;
                border: 1px solid #e8e8e8;
                border-radius: 12px;
                padding: 16px;
                margin-bottom: 8px;
            ">
                <div style="font-size: 16px; font-weight: 600; margin-bottom: 6px;">
                    {cat['emoji']} {cat['label']}
                </div>
                <div style="font-size: 13px; color: #4A90E2; font-weight: 600; margin-bottom: 8px;">
                    {cat['mastered']} / {cat['total']} 語 ({pct}%)
                </div>
                <div style="height: 6px; background: #f0f0f0; border-radius: 3px; overflow: hidden;">
                    <div style="height: 100%; background: #4A90E2; width: {pct}%; border-radius: 3px;"></div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            # 学習開始ボタン
            disabled = cat['total'] == 0
            btn_label = f"{cat['label']}を学習" if not disabled else "単語なし"
            if st.button(btn_label, key=f"cat_{cat['key']}", use_container_width=True, disabled=disabled):
                st.session_state.selected_category = cat['key']
                st.session_state.word_index = 0
                st.session_state.current_page = "vocabulary_step1"
                st.rerun()

    st.markdown("---")
    if st.button("ホームに戻る", use_container_width=True, key="cat_home"):
        st.session_state.current_page = "home"
        st.rerun()


# ============================================================
# 単語学習画面（Step 1）
# ============================================================

def render_vocabulary_step1():
    """単語学習 Step 1：意味・発音"""
    
    # カテゴリー名を取得
    cat_key = st.session_state.get("selected_category", "verb")
    cat_label = next((c["label"] for c in DataManager.CATEGORIES if c["key"] == cat_key), "")

    st.markdown(f"## 📖 Vocabulary - Step 1 ({cat_label})")
    st.markdown("意味と発音を覚えましょう")
    
    # 選択カテゴリーの未学習単語を取得
    words = [w for w in DataManager.get_words_by_category(cat_key) if w["status"] == "new"]
    if not words:
        st.success(f"🎉 {cat_label}の未学習単語はすべて完了しました！")
        if st.button("カテゴリー選択に戻る"):
            st.session_state.current_page = "vocabulary"
            st.rerun()
        return
    
    word = words[st.session_state.word_index % len(words)]
    
    # 単語カード
    st.markdown(f"""
    <div style="
        background: linear-gradient(135deg, #4A90E2 0%, #357ABD 100%);
        border-radius: 16px;
        padding: 40px 30px;
        text-align: center;
        color: white;
        margin-bottom: 24px;
    ">
        <div style="font-size: 40px; font-weight: 700; margin-bottom: 12px;">
            {word['english']}
        </div>
        <div style="font-size: 14px; opacity: 0.9; margin-bottom: 16px; font-style: italic;">
            {word['phonetic']}
        </div>
        <div style="
            font-size: 15px;
            line-height: 1.6;
            opacity: 0.95;
            background: rgba(0, 0, 0, 0.15);
            padding: 16px;
            border-radius: 10px;
        ">
            {word['definition']}
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # ボタン
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔊 音声を聞く", use_container_width=True, key="play_audio"):
            st.info("音声再生機能は Phase 2 で実装予定")
    
    with col2:
        if st.button("この単語を理解した →", use_container_width=True, key="understood_word"):
            # ステータスを quiz_pending に更新
            DataManager.update_word_status(word['word_id'], "quiz_pending")
            st.success("次のステップに進みます！")
            st.session_state.current_page = "vocabulary_step2"
            st.rerun()
    
    # ナビゲーション
    st.divider()
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("← 前の単語", use_container_width=True):
            st.session_state.word_index = max(0, st.session_state.word_index - 1)
            st.rerun()
    
    with col2:
        if st.button("カテゴリー選択に戻る", use_container_width=True, key="step1_back"):
            st.session_state.current_page = "vocabulary"
            st.rerun()
    
    with col3:
        if st.button("次の単語 →", use_container_width=True):
            st.session_state.word_index += 1
            st.rerun()

# ============================================================
# 単語学習画面（Step 2）
# ============================================================

def render_vocabulary_step2():
    """単語学習 Step 2：4択クイズ"""

    cat_key = st.session_state.get("selected_category", "verb")
    cat_label = next((c["label"] for c in DataManager.CATEGORIES if c["key"] == cat_key), "")

    st.markdown(f"## ❓ Vocabulary - Step 2 ({cat_label})")
    st.markdown("正しい和訳を選びましょう")

    # 選択カテゴリーの quiz_pending 単語を取得
    cat_words = DataManager.get_words_by_category(cat_key)
    words = [w for w in cat_words if w["status"] == "quiz_pending"]
    if not words:
        words = [w for w in cat_words if w["status"] == "new"]
        if not words:
            st.success(f"🎉 {cat_label}のクイズ対象単語はありません！")
            if st.button("カテゴリー選択に戻る"):
                st.session_state.current_page = "vocabulary"
                st.rerun()
            return

    word = words[st.session_state.word_index % len(words)]
    correct = word['definition'].split('、')[0]

    st.markdown(f"""
    <div style="
        background: linear-gradient(135deg, #4A90E2 0%, #357ABD 100%);
        border-radius: 16px;
        padding: 40px 30px;
        text-align: center;
        color: white;
        margin-bottom: 24px;
    ">
        <div style="font-size: 32px; font-weight: 700;">
            {word['english']}
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("### 正しい和訳を選んでください")

    # 4択選択肢を「同カテゴリーの他の単語」からランダム生成
    # （選択肢は単語ごとに固定するため session_state にキャッシュ）
    choice_key = f"choices_{word['word_id']}"
    if choice_key not in st.session_state:
        # 他の単語の意味（先頭の訳）を集める
        others = [
            w['definition'].split('、')[0]
            for w in DataManager.load_words()
            if w['word_id'] != word['word_id']
        ]
        # 正答と重複しないものだけ
        others = list({o for o in others if o != correct})
        random.shuffle(others)
        distractors = others[:3]
        # もし他カテゴリー含めても3つ足りない場合の予備
        filler = ["古い", "新しい", "大きい", "小さい", "速い", "遅い"]
        while len(distractors) < 3:
            f = random.choice(filler)
            if f != correct and f not in distractors:
                distractors.append(f)
        choices = distractors + [correct]
        random.shuffle(choices)
        st.session_state[choice_key] = choices

    choices = st.session_state[choice_key]

    selected = st.radio(
        "選択肢：",
        choices,
        key=f"quiz_radio_{word['word_id']}"
    )

    if st.button("回答する", use_container_width=True, key="submit_quiz"):
        if selected == correct:
            st.success("✅ 正解！")
            st.markdown(f"**フィードバック:** {word['definition']}")

            if st.button("次へ進む", use_container_width=True, key="next_step2"):
                DataManager.update_word_status(
                    word['word_id'],
                    "translation_pending",
                    {"quiz_attempts": 1}
                )
                # 選択肢キャッシュをクリア
                if choice_key in st.session_state:
                    del st.session_state[choice_key]
                st.session_state.current_page = "vocabulary_step3"
                st.rerun()
        else:
            st.error("❌ 不正解。もう一度チャレンジしてください。")
    
    # ナビゲーション
    st.divider()
    if st.button("カテゴリー選択に戻る", use_container_width=True, key="step2_back"):
        st.session_state.current_page = "vocabulary"
        st.rerun()

# ============================================================
# 単語学習画面（Step 3）
# ============================================================

def render_vocabulary_step3():
    """単語学習 Step 3：英→日訳"""

    cat_key = st.session_state.get("selected_category", "verb")
    cat_label = next((c["label"] for c in DataManager.CATEGORIES if c["key"] == cat_key), "")

    st.markdown(f"## 📝 Vocabulary - Step 3 ({cat_label})")
    st.markdown("英語を日本語に訳してください")

    # 選択カテゴリーの translation_pending 単語を取得
    cat_words = DataManager.get_words_by_category(cat_key)
    words = [w for w in cat_words if w["status"] == "translation_pending"]
    if not words:
        st.success(f"🎉 {cat_label}の訳問題はありません！")
        if st.button("カテゴリー選択に戻る"):
            st.session_state.current_page = "vocabulary"
            st.rerun()
        return

    word = words[st.session_state.word_index % len(words)]
    
    st.markdown(f"""
    <div style="
        background: linear-gradient(135deg, #4A90E2 0%, #357ABD 100%);
        border-radius: 16px;
        padding: 40px 30px;
        text-align: center;
        color: white;
        margin-bottom: 24px;
    ">
        <div style="font-size: 40px; font-weight: 700;">
            {word['english']}
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("### 和訳を入力してください")
    
    user_answer = st.text_input(
        "和訳：",
        placeholder="例：本物の",
        key=f"translation_{word['word_id']}"
    )
    
    if st.button("回答する", use_container_width=True, key="submit_translation"):
        # Claude API で採点
        eval_result = evaluate_vocabulary_translation(
            user_answer,
            word['definition'],
            word['english']
        )
        
        if eval_result.get("is_correct"):
            st.success("✅ 正解！")
            st.markdown(f"**スコア:** {eval_result.get('score', 0)}/100")
            st.markdown(f"**フィードバック:** {eval_result.get('feedback', '')}")
            
            if st.button("マスター完了！次の単語へ", use_container_width=True, key="mastered"):
                DataManager.update_word_status(
                    word['word_id'],
                    "mastered",
                    {"translation_attempts": 1}
                )
                # 次の単語のため index リセット、カテゴリー選択画面で進捗確認
                st.session_state.word_index = 0
                st.session_state.current_page = "vocabulary"
                st.rerun()
        else:
            st.error("❌ 不正解。もう一度チャレンジしてください。")
            st.markdown(f"**フィードバック:** {eval_result.get('feedback', '')}")
    
    # ナビゲーション
    st.divider()
    if st.button("カテゴリー選択に戻る", use_container_width=True, key="step3_back"):
        st.session_state.current_page = "vocabulary"
        st.rerun()

# ============================================================
# ページルーティング
# ============================================================

def main():
    """メインアプリケーション"""
    
    if st.session_state.current_page == "home":
        render_home()
    elif st.session_state.current_page == "vocabulary":
        render_vocabulary_categories()
    elif st.session_state.current_page == "vocabulary_step1":
        render_vocabulary_step1()
    elif st.session_state.current_page == "vocabulary_step2":
        render_vocabulary_step2()
    elif st.session_state.current_page == "vocabulary_step3":
        render_vocabulary_step3()
    else:
        st.markdown("### 🚧 Coming Soon...")
        st.info("この機能は Phase 2 で実装予定です。")
        if st.button("ホームに戻る"):
            st.session_state.current_page = "home"
            st.rerun()

if __name__ == "__main__":
    main()
