"""
GAVI - 英検準2級対策アプリ v2.0
Learn English, Enjoy the World

記憶定着エンジン（SRS間隔反復）搭載
- Part 1: 新規単語学習（予習→4択）
- Part 2: 記憶TEST（SRSで自動出題）
- ストリーク・カレンダーでゲーミフィケーション
"""

import streamlit as st
import random
from datetime import date, datetime
import srs_engine as srs
from data_manager import DataManager
from claude_api import evaluate_vocabulary_translation

APP_VERSION = "v2026-06-19.002-SRS"

st.set_page_config(
    page_title="GAVI - 英検準2級対策",
    page_icon="🌈",
    layout="centered",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
    .main { background: linear-gradient(180deg, #ffffff 0%, #f8f9fa 100%); }
    .stat-bar {
        display: flex; justify-content: space-around; background: white;
        border: 1px solid #e8e8e8; border-radius: 16px; padding: 16px; margin-bottom: 20px;
    }
    .stat-item { text-align: center; }
    .stat-value { font-size: 28px; font-weight: 700; line-height: 1; }
    .stat-label { font-size: 11px; color: #999; margin-top: 4px; }
    .word-card {
        background: linear-gradient(135deg, #4A90E2 0%, #357ABD 100%);
        border-radius: 20px; padding: 36px 28px; text-align: center;
        color: white; margin-bottom: 20px;
    }
    .word-en { font-size: 42px; font-weight: 700; margin-bottom: 8px; }
    .word-phonetic { font-size: 15px; opacity: 0.85; font-style: italic; margin-bottom: 16px; }
    .word-def { font-size: 17px; background: rgba(0,0,0,0.15); padding: 14px; border-radius: 12px; margin-bottom: 12px; }
    .word-ex { font-size: 13px; text-align: left; background: rgba(255,255,255,0.12); padding: 12px; border-radius: 10px; margin-top: 8px; line-height: 1.6; }
    .word-ex-ja { opacity: 0.8; font-size: 12px; }
    .mission-card { background: white; border: 1px solid #e8e8e8; border-radius: 16px; padding: 20px; margin-bottom: 12px; }
    .mission-row { display: flex; justify-content: space-between; align-items: center; padding: 8px 0; }
    .mission-label { font-size: 15px; font-weight: 600; }
    .mission-num { font-size: 20px; font-weight: 700; color: #4A90E2; }
</style>
""", unsafe_allow_html=True)


def init_session():
    defaults = {
        "page": "home", "selected_categories": [], "mission": None,
        "part1_queue": [], "part1_index": 0, "part1_phase": "preview", "part1_wrong": [],
        "part2_queue": [], "part2_index": 0, "part2_wrong": [],
        "show_ja": True, "answered": False, "last_correct": None,
        "cal_year": date.today().year, "cal_month": date.today().month,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

init_session()


def render_status_bar():
    s = srs.get_progress_summary()
    st.markdown(f"""
    <div class="stat-bar">
        <div class="stat-item"><div class="stat-value" style="color:#FF6B35;">🔥 {s['streak_current']}</div><div class="stat-label">連続日数</div></div>
        <div class="stat-item"><div class="stat-value" style="color:#28B448;">⭐ {s['mastered']}</div><div class="stat-label">マスター</div></div>
        <div class="stat-item"><div class="stat-value" style="color:#4A90E2;">📅 {s['days_until_exam']}</div><div class="stat-label">英検まで</div></div>
    </div>
    """, unsafe_allow_html=True)


def render_home():
    st.markdown('<div style="font-size:32px;font-weight:700;background:linear-gradient(135deg,#4A90E2,#28B448,#FF6B35);-webkit-background-clip:text;-webkit-text-fill-color:transparent;">🌈 GAVI</div>', unsafe_allow_html=True)
    st.caption("Learn English, Enjoy the World")
    render_status_bar()
    st.markdown("### 👋 Hello, Ria!")
    st.write("今日も一緒にがんばろう！")

    st.markdown("#### 📚 今日学ぶカテゴリーを選ぼう")
    cat_progress = DataManager.get_category_progress()
    selected = []
    cols = st.columns(2)
    for i, c in enumerate(cat_progress):
        with cols[i % 2]:
            label = f"{c['emoji']} {c['label']} ({c['mastered']}/{c['total']})"
            if st.checkbox(label, key=f"cat_check_{c['key']}", value=(c['key'] in ["verb","noun","adjective"])):
                selected.append(c['key'])
    st.session_state.selected_categories = selected
    st.divider()

    if selected:
        mission = srs.get_today_mission_by_categories(selected)
    else:
        mission = srs.get_today_mission_by_categories(["verb","noun","adjective","adverb","idiom","other"])

    st.markdown("#### 📅 Today's Mission")
    st.markdown(f"""
    <div class="mission-card">
        <div class="mission-row"><span class="mission-label">🆕 新規単語</span><span class="mission-num">{mission['new_count']}語</span></div>
        <div class="mission-row"><span class="mission-label">🔁 記憶テスト</span><span class="mission-num">{mission['review_count']}語</span></div>
    </div>
    """, unsafe_allow_html=True)
    if mission['review_overflow'] > 0:
        st.caption(f"（復習が多いため {mission['review_overflow']}語は明日に繰り越されます）")

    state = srs.load_state()
    today = srs.today_str()
    done_today = state["daily_log"].get(today, {}).get("completed", False)

    if done_today:
        st.success("🎉 今日のミッション完了！また明日ね！")
        if st.button("📅 カレンダーを見る", use_container_width=True):
            st.session_state.page = "calendar"; st.rerun()
    elif mission['new_count'] == 0 and mission['review_count'] == 0:
        st.info("今日学ぶ単語がありません。カテゴリーを選んでください。")
    else:
        if st.button("🚀 START", use_container_width=True, type="primary"):
            st.session_state.mission = mission
            st.session_state.part1_queue = list(mission['new_words'])
            st.session_state.part1_index = 0
            st.session_state.part1_phase = "preview"
            st.session_state.part1_wrong = []
            st.session_state.part2_queue = list(mission['review_words'])
            st.session_state.part2_index = 0
            st.session_state.part2_wrong = []
            st.session_state.answered = False
            if mission['new_count'] > 0:
                st.session_state.page = "part1"
            elif mission['review_count'] > 0:
                st.session_state.page = "part2"
            st.rerun()

    st.divider()
    if st.button("📅 カレンダー", use_container_width=True):
        st.session_state.page = "calendar"; st.rerun()


def make_choices(word, all_words):
    correct = word['definition'].split('、')[0]
    others = list({w['definition'].split('、')[0] for w in all_words if w['word_id'] != word['word_id']})
    others = [o for o in others if o != correct]
    random.shuffle(others)
    distractors = others[:3]
    filler = ["古い","新しい","大きい","小さい","速い","遅い","明るい","暗い"]
    while len(distractors) < 3:
        f = random.choice(filler)
        if f != correct and f not in distractors:
            distractors.append(f)
    choices = distractors + [correct]
    random.shuffle(choices)
    return choices, correct


def render_part1():
    queue = st.session_state.part1_queue
    idx = st.session_state.part1_index

    if idx >= len(queue):
        if st.session_state.part1_wrong:
            st.session_state.part1_queue = st.session_state.part1_wrong
            st.session_state.part1_index = 0
            st.session_state.part1_wrong = []
            st.session_state.part1_phase = "preview"
            st.rerun()
        else:
            if st.session_state.part2_queue:
                st.session_state.page = "part2"
            else:
                st.session_state.page = "complete"
            st.rerun()
        return

    word = queue[idx]
    phase = st.session_state.part1_phase
    total = len(queue)
    st.progress(idx / total if total > 0 else 0)
    st.caption(f"🆕 新規単語 {idx+1} / {total}")

    if phase == "preview":
        ex_html = ""
        for ex in word.get('examples', []):
            ja = f'<div class="word-ex-ja">{ex["ja"]}</div>' if st.session_state.show_ja else ""
            ex_html += f'<div class="word-ex">{ex["en"]}{ja}</div>'
        st.markdown(f"""
        <div class="word-card">
            <div class="word-en">{word['english']}</div>
            <div class="word-phonetic">{word['phonetic']}</div>
            <div class="word-def">{word['definition']}</div>
            {ex_html}
        </div>
        """, unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        with c1:
            st.session_state.show_ja = st.toggle("例文の訳", value=st.session_state.show_ja)
        with c2:
            if st.button("覚えた！4択へ →", use_container_width=True, type="primary"):
                st.session_state.part1_phase = "quiz"
                st.session_state.answered = False
                st.rerun()
    else:
        st.markdown(f"""<div class="word-card"><div class="word-en">{word['english']}</div><div class="word-phonetic">{word['phonetic']}</div></div>""", unsafe_allow_html=True)
        all_words = srs.load_words()
        ckey = f"p1_choices_{word['word_id']}"
        if ckey not in st.session_state:
            choices, correct = make_choices(word, all_words)
            st.session_state[ckey] = {"choices": choices, "correct": correct}
        choices = st.session_state[ckey]["choices"]
        correct = st.session_state[ckey]["correct"]
        st.markdown("**正しい意味は？**")
        if not st.session_state.answered:
            sel = st.radio("選択肢", choices, key=f"p1_radio_{word['word_id']}_{idx}", label_visibility="collapsed")
            if st.button("回答する", use_container_width=True, type="primary"):
                st.session_state.answered = True
                st.session_state.last_correct = (sel == correct)
                st.rerun()
        else:
            if st.session_state.last_correct:
                st.success(f"✅ 正解！ {word['definition']}")
                if st.button("次へ →", use_container_width=True, type="primary"):
                    srs.mark_new_learned(word['word_id'])
                    del st.session_state[ckey]
                    st.session_state.part1_index += 1
                    st.session_state.part1_phase = "preview"
                    st.session_state.answered = False
                    st.rerun()
            else:
                st.error(f"❌ 不正解。正解は「{correct}」")
                if st.button("もう一度", use_container_width=True):
                    if word not in st.session_state.part1_wrong:
                        st.session_state.part1_wrong.append(word)
                    del st.session_state[ckey]
                    st.session_state.part1_index += 1
                    st.session_state.part1_phase = "preview"
                    st.session_state.answered = False
                    st.rerun()


def render_part2():
    queue = st.session_state.part2_queue
    idx = st.session_state.part2_index
    if idx >= len(queue):
        if st.session_state.part2_wrong:
            st.session_state.part2_queue = st.session_state.part2_wrong
            st.session_state.part2_index = 0
            st.session_state.part2_wrong = []
            st.rerun()
        else:
            st.session_state.page = "complete"
            st.rerun()
        return

    word = queue[idx]
    total = len(queue)
    st.progress(idx / total if total > 0 else 0)
    st.caption(f"🔁 記憶テスト {idx+1} / {total}")
    st.markdown(f"""<div class="word-card"><div class="word-en">{word['english']}</div><div class="word-phonetic">{word['phonetic']}</div></div>""", unsafe_allow_html=True)

    all_words = srs.load_words()
    ckey = f"p2_choices_{word['word_id']}"
    if ckey not in st.session_state:
        choices, correct = make_choices(word, all_words)
        st.session_state[ckey] = {"choices": choices, "correct": correct}
    choices = st.session_state[ckey]["choices"]
    correct = st.session_state[ckey]["correct"]
    st.markdown("**正しい意味は？**")
    if not st.session_state.answered:
        sel = st.radio("選択肢", choices, key=f"p2_radio_{word['word_id']}_{idx}", label_visibility="collapsed")
        if st.button("回答する", use_container_width=True, type="primary"):
            st.session_state.answered = True
            st.session_state.last_correct = (sel == correct)
            st.rerun()
    else:
        if st.session_state.last_correct:
            st.success(f"✅ 正解！ {word['definition']}")
            if st.button("次へ →", use_container_width=True, type="primary"):
                srs.mark_review_result(word['word_id'], True)
                del st.session_state[ckey]
                st.session_state.part2_index += 1
                st.session_state.answered = False
                st.rerun()
        else:
            st.error(f"❌ 不正解。正解は「{correct}」")
            if st.button("もう一度 →", use_container_width=True):
                srs.mark_review_result(word['word_id'], False)
                if word not in st.session_state.part2_wrong:
                    st.session_state.part2_wrong.append(word)
                del st.session_state[ckey]
                st.session_state.part2_index += 1
                st.session_state.answered = False
                st.rerun()


def render_complete():
    srs.complete_today_mission()
    s = srs.get_progress_summary()
    st.balloons()
    st.markdown(f"""
    <div style="text-align:center; padding:40px 20px;">
        <div style="font-size:64px;">🎉</div>
        <div style="font-size:28px; font-weight:700; margin:16px 0;">Mission Complete!</div>
        <div style="font-size:18px; color:#FF6B35; font-weight:700;">🔥 連続 {s['streak_current']}日</div>
        <div style="font-size:16px; color:#28B448; margin-top:8px;">⭐ マスター {s['mastered']}語</div>
    </div>
    """, unsafe_allow_html=True)
    st.success("今日もよくがんばりました！また明日ね！")
    if st.button("📅 カレンダーを見る", use_container_width=True):
        st.session_state.page = "calendar"; st.rerun()
    if st.button("🏠 ホームに戻る", use_container_width=True):
        st.session_state.page = "home"; st.rerun()


def render_calendar():
    st.markdown("### 📅 GAVI Calendar")
    render_status_bar()
    y = st.session_state.cal_year
    m = st.session_state.cal_month
    c1, c2, c3 = st.columns([1, 2, 1])
    with c1:
        if st.button("← 前月"):
            if m == 1:
                st.session_state.cal_month = 12; st.session_state.cal_year -= 1
            else:
                st.session_state.cal_month -= 1
            st.rerun()
    with c2:
        st.markdown(f"<div style='text-align:center;font-size:18px;font-weight:700;'>{y}年 {m}月</div>", unsafe_allow_html=True)
    with c3:
        if st.button("次月 →"):
            if m == 12:
                st.session_state.cal_month = 1; st.session_state.cal_year += 1
            else:
                st.session_state.cal_month += 1
            st.rerun()

    caldata = srs.get_calendar(y, m)
    first_weekday = (date(y, m, 1).weekday() + 1) % 7
    html = '<div style="display:grid;grid-template-columns:repeat(7,1fr);gap:4px;text-align:center;">'
    for wd in ["日","月","火","水","木","金","土"]:
        html += f'<div style="font-size:11px;color:#999;padding:4px;">{wd}</div>'
    for _ in range(first_weekday):
        html += '<div></div>'
    for day in caldata["days"]:
        bg = "#f8f8f8"; emoji = ""
        if day["completed"]:
            bg = "rgba(255,107,53,0.15)"; emoji = "🔥"
        if day["is_exam"]:
            bg = "rgba(74,144,226,0.2)"; emoji = "🎯"
        elif day["is_australia"]:
            bg = "rgba(40,180,72,0.12)"; emoji = emoji or "🇦🇺"
        border = "2px solid #4A90E2" if day["is_today"] else "1px solid #eee"
        html += f'<div style="background:{bg};border:{border};border-radius:8px;padding:6px 2px;min-height:44px;"><div style="font-size:12px;font-weight:600;">{day["day"]}</div><div style="font-size:14px;">{emoji}</div></div>'
    html += '</div>'
    st.markdown(html, unsafe_allow_html=True)
    st.caption("🔥 達成日　🇦🇺 オーストラリア留学　🎯 英検一次")
    st.divider()
    if st.button("🏠 ホームに戻る", use_container_width=True):
        st.session_state.page = "home"; st.rerun()


def main():
    page = st.session_state.page
    if page == "home":
        render_home()
    elif page == "part1":
        render_part1()
    elif page == "part2":
        render_part2()
    elif page == "complete":
        render_complete()
    elif page == "calendar":
        render_calendar()
    else:
        render_home()
    st.caption(f"GAVI {APP_VERSION}")


if __name__ == "__main__":
    main()
