"""
GAVI - 英検準2級対策アプリ v2.1
Learn English, Enjoy the World

記憶定着エンジン（SRS）＋ eiloカラー＆カードデザイン
- カテゴリーボタン → 品詞別ページ（全単語カード一覧）
- Part 1: 25語まとめて予習 → 25問4択
- Part 2: 記憶TEST（SRS、全カテゴリー混在）
"""

import streamlit as st
import random
from datetime import date
import srs_engine as srs
from data_manager import DataManager

APP_VERSION = "v2026-06-19.003-eilo"

st.set_page_config(page_title="GAVI", page_icon="🌈", layout="centered", initial_sidebar_state="collapsed")

st.markdown("""
<style>
    .main { background: linear-gradient(180deg,#ffffff 0%,#f8f9fa 100%); }
    .stat-bar { display:flex; justify-content:space-around; background:white; border:1px solid #e8e8e8; border-radius:16px; padding:16px; margin-bottom:20px; }
    .stat-item { text-align:center; }
    .stat-value { font-size:28px; font-weight:700; line-height:1; }
    .stat-label { font-size:11px; color:#999; margin-top:4px; }
    /* eiloカード */
    .eilo-grid { display:grid; grid-template-columns:repeat(auto-fill,minmax(140px,1fr)); gap:10px; margin:16px 0; }
    .eilo-card { background:white; border-radius:12px; border-top:4px solid #ccc; padding:14px 8px; text-align:center; box-shadow:0 1px 3px rgba(0,0,0,0.08); position:relative; }
    .eilo-kana { font-size:11px; color:#aaa; margin-bottom:2px; }
    .eilo-en { font-size:20px; font-weight:700; color:#1a1a1a; }
    .eilo-ja { font-size:12px; color:#888; margin-top:2px; }
    .eilo-mark { position:absolute; top:6px; right:8px; font-size:14px; }
    /* 学習カード（大） */
    .word-card { border-radius:20px; padding:36px 28px; text-align:center; color:white; margin-bottom:20px; }
    .word-kana { font-size:14px; opacity:0.8; margin-bottom:4px; }
    .word-en { font-size:42px; font-weight:700; margin-bottom:8px; }
    .word-phonetic { font-size:15px; opacity:0.85; font-style:italic; margin-bottom:16px; }
    .word-def { font-size:17px; background:rgba(0,0,0,0.15); padding:14px; border-radius:12px; margin-bottom:12px; }
    .word-ex { font-size:13px; text-align:left; background:rgba(255,255,255,0.15); padding:12px; border-radius:10px; margin-top:8px; line-height:1.6; }
    .word-ex-ja { opacity:0.8; font-size:12px; }
    .mission-card { background:white; border:1px solid #e8e8e8; border-radius:16px; padding:20px; margin-bottom:12px; }
    .mission-row { display:flex; justify-content:space-between; align-items:center; padding:8px 0; }
    .mission-label { font-size:15px; font-weight:600; }
    .mission-num { font-size:20px; font-weight:700; color:#4A90E2; }
    .cat-badge { display:inline-block; width:12px; height:12px; border-radius:3px; margin-right:6px; vertical-align:middle; }
    /* primary buttonをGAVI青に統一 */
    .stButton > button[kind="primary"] { background:#4A90E2; border:none; }
    .stButton > button[kind="primary"]:hover { background:#357ABD; }
</style>
""", unsafe_allow_html=True)


def init_session():
    d = {
        "page":"home", "active_category":None,
        "part1_queue":[], "part1_index":0, "part1_stage":"preview", "part1_wrong":[],
        "part2_queue":[], "part2_index":0, "part2_wrong":[],
        "show_ja":True, "answered":False, "last_correct":None,
        "cal_year":date.today().year, "cal_month":date.today().month,
    }
    for k,v in d.items():
        if k not in st.session_state: st.session_state[k]=v
init_session()


def status_bar():
    s = srs.get_progress_summary()
    st.markdown(f"""<div class="stat-bar">
        <div class="stat-item"><div class="stat-value" style="color:#FF6B35;">🔥 {s['streak_current']}</div><div class="stat-label">連続日数</div></div>
        <div class="stat-item"><div class="stat-value" style="color:#28B448;">⭐ {s['mastered']}</div><div class="stat-label">マスター</div></div>
        <div class="stat-item"><div class="stat-value" style="color:#4A90E2;">📅 {s['days_until_exam']}</div><div class="stat-label">英検まで</div></div>
    </div>""", unsafe_allow_html=True)


def color_for(cat_key):
    return DataManager.get_category_color(cat_key)


def make_choices(word, all_words):
    correct = word['definition'].split('、')[0]
    others = list({w['definition'].split('、')[0] for w in all_words if w['word_id']!=word['word_id']})
    others = [o for o in others if o!=correct]
    random.shuffle(others)
    d = others[:3]
    filler = ["古い","新しい","大きい","小さい","速い","遅い","明るい","暗い"]
    while len(d)<3:
        f=random.choice(filler)
        if f!=correct and f not in d: d.append(f)
    ch = d+[correct]; random.shuffle(ch)
    return ch, correct


# ============================================================
# ホーム（カテゴリーボタン）
# ============================================================
def render_home():
    st.markdown('<div style="font-size:32px;font-weight:700;background:linear-gradient(135deg,#4A90E2,#28B448,#FF6B35);-webkit-background-clip:text;-webkit-text-fill-color:transparent;">🌈 GAVI</div>', unsafe_allow_html=True)
    st.caption("Learn English, Enjoy the World")
    status_bar()
    st.markdown("### 👋 Hello, Ria!")

    today = srs.today_str()
    state = srs.load_state()
    done = state["daily_log"].get(today,{}).get("completed",False)
    if done:
        st.success("🎉 Mission Complete! See you tomorrow!")

    # 記憶テスト（全カテゴリー混在）
    mission = srs.get_today_mission_by_categories(["verb","noun","adjective","adverb","idiom","other"])
    if mission['review_count']>0:
        st.markdown(f"""<div class="mission-card"><div class="mission-row">
            <span class="mission-label">🔁 Memory Test</span>
            <span class="mission-num">{mission['review_count']} words</span></div></div>""", unsafe_allow_html=True)
        if st.button("🔁 Start Memory Test", use_container_width=True, type="primary"):
            st.session_state.part2_queue=list(mission['review_words'])
            st.session_state.part2_index=0; st.session_state.part2_wrong=[]
            st.session_state.answered=False; st.session_state.page="part2"; st.rerun()
        st.divider()

    st.markdown("#### 📚 Choose a category to learn")

    # カテゴリーごとにボタン色を変えるCSS
    cats = DataManager.get_category_progress()
    css = "<style>"
    for c in cats:
        css += f'div[data-cat="{c["key"]}"] + div button {{ background:{c["color"]} !important; color:white !important; border:none !important; }}'
    css += "</style>"
    st.markdown(css, unsafe_allow_html=True)

    cols = st.columns(2)
    for i,c in enumerate(cats):
        with cols[i%2]:
            col = c['color']
            st.markdown(f"""<div data-cat="{c['key']}" style="border-left:5px solid {col};background:white;border:1px solid #eee;border-radius:10px;padding:10px 14px;margin-bottom:4px;">
                <span style="font-weight:600;">{c['emoji']} {c['en']} <span style="font-size:12px;color:#999;">{c['label']}</span></span>
                <span style="float:right;color:{col};font-weight:700;">{c['mastered']}/{c['total']}</span></div>""", unsafe_allow_html=True)
            if st.button(f"Learn {c['en']} →", key=f"catbtn_{c['key']}", use_container_width=True):
                st.session_state.active_category=c['key']; st.session_state.page="category"; st.rerun()

    st.divider()
    if st.button("📅 Calendar", use_container_width=True):
        st.session_state.page="calendar"; st.rerun()


# ============================================================
# 品詞別ページ（eiloカード一覧 ＋ START）
# ============================================================
def render_category():
    cat_key = st.session_state.active_category
    cat = next(c for c in DataManager.CATEGORIES if c["key"]==cat_key)
    col = cat["color"]

    if st.button("← Back to Home"):
        st.session_state.page="home"; st.rerun()

    st.markdown(f"""<h3><span class="cat-badge" style="background:{col};"></span>{cat['emoji']} {cat['en']} <span style="font-size:15px;color:#999;">{cat['label']}</span></h3>""", unsafe_allow_html=True)

    words = DataManager.get_words_by_category(cat_key)
    mastered = len([w for w in words if w.get("status")=="mastered"])
    st.caption(f"{mastered} / {len(words)} mastered")

    # 新規単語START（上部に配置）
    new_words = [w for w in words if w.get("srs_level",0)==0 and w.get("learned_date") is None]
    per_day = srs.load_state()["settings"]["new_words_per_day"]
    todays = new_words[:per_day]

    if todays:
        st.markdown(f"**🆕 New words today: {len(todays)}**")
        if st.button("🚀 START", use_container_width=True, type="primary"):
            st.session_state.part1_queue=list(todays)
            st.session_state.part1_index=0
            st.session_state.part1_stage="preview"
            st.session_state.part1_wrong=[]
            st.session_state.answered=False
            st.session_state.page="part1"; st.rerun()
    else:
        st.info("All new words in this category are done! 🎉")

    st.divider()
    st.caption("📋 Word list")

    # eiloカード一覧（進捗マーク付き）
    html = '<div class="eilo-grid">'
    for w in words:
        mark = srs.get_word_mark(w)
        bg = "white"
        if w.get("status")=="mastered":
            bg = f"{col}1a"
        html += f"""<div class="eilo-card" style="border-top-color:{col};background:{bg};">
            <div class="eilo-mark">{mark}</div>
            <div class="eilo-kana">{w.get('katakana','')}</div>
            <div class="eilo-en">{w['english']}</div>
            <div class="eilo-ja">{w['definition'].split('、')[0]}</div>
        </div>"""
    html += '</div>'
    st.markdown(html, unsafe_allow_html=True)


# ============================================================
# Part 1: 予習（全部）→ 4択（全部）
# ============================================================
def render_part1():
    queue = st.session_state.part1_queue
    idx = st.session_state.part1_index
    stage = st.session_state.part1_stage
    total = len(queue)
    cat_key = st.session_state.active_category
    col = color_for(cat_key)

    # ===== 予習ステージ：1語ずつ見ていく =====
    if stage=="preview":
        if idx>=total:
            # 予習完了 → 4択へ
            st.session_state.part1_stage="quiz"
            st.session_state.part1_index=0
            st.session_state.answered=False
            st.rerun()
            return
        word = queue[idx]
        st.progress(idx/total if total else 0)
        st.caption(f"📖 Preview {idx+1} / {total}")
        ex_html=""
        for ex in word.get('examples',[]):
            ja = f'<div class="word-ex-ja">{ex["ja"]}</div>' if st.session_state.show_ja else ""
            ex_html+=f'<div class="word-ex">{ex["en"]}{ja}</div>'
        st.markdown(f"""<div class="word-card" style="background:linear-gradient(135deg,{col},{col}cc);">
            <div class="word-kana">{word.get('katakana','')}</div>
            <div class="word-en">{word['english']}</div>
            <div class="word-phonetic">{word['phonetic']}</div>
            <div class="word-def">{word['definition']}</div>
            {ex_html}
        </div>""", unsafe_allow_html=True)
        c1,c2 = st.columns(2)
        with c1:
            st.session_state.show_ja = st.toggle("Show translation", value=st.session_state.show_ja)
        with c2:
            label = "Next →" if idx<total-1 else "Quiz →"
            if st.button(label, use_container_width=True, type="primary"):
                st.session_state.part1_index+=1; st.rerun()
        return

    # ===== 4択クイズステージ =====
    if idx>=total:
        if st.session_state.part1_wrong:
            st.session_state.part1_queue=st.session_state.part1_wrong
            st.session_state.part1_wrong=[]
            st.session_state.part1_index=0
            st.info("Let's retry the wrong words!")
            st.rerun()
        else:
            # Part1完了
            st.session_state.page="complete"; st.rerun()
        return

    word = queue[idx]
    st.progress(idx/total if total else 0)
    st.caption(f"❓ Quiz {idx+1} / {total}")
    st.markdown(f"""<div class="word-card" style="background:linear-gradient(135deg,{col},{col}cc);">
        <div class="word-kana">{word.get('katakana','')}</div>
        <div class="word-en">{word['english']}</div>
        <div class="word-phonetic">{word['phonetic']}</div></div>""", unsafe_allow_html=True)

    all_words=srs.load_words()
    ck=f"p1c_{word['word_id']}"
    if ck not in st.session_state:
        ch,co=make_choices(word,all_words); st.session_state[ck]={"ch":ch,"co":co}
    ch=st.session_state[ck]["ch"]; co=st.session_state[ck]["co"]
    st.markdown("**What does it mean?**")
    if not st.session_state.answered:
        sel=st.radio("c",ch,key=f"p1r_{word['word_id']}_{idx}",label_visibility="collapsed")
        if st.button("Answer",use_container_width=True,type="primary"):
            st.session_state.answered=True; st.session_state.last_correct=(sel==co); st.rerun()
    else:
        if st.session_state.last_correct:
            st.success(f"✅ Correct! {word['definition']}")
            if st.button("Next →",use_container_width=True,type="primary"):
                srs.mark_new_learned(word['word_id'])
                del st.session_state[ck]; st.session_state.part1_index+=1
                st.session_state.answered=False; st.rerun()
        else:
            st.error(f"❌ Wrong. Answer: {co}")
            if st.button("Retry",use_container_width=True):
                if word not in st.session_state.part1_wrong: st.session_state.part1_wrong.append(word)
                del st.session_state[ck]; st.session_state.part1_index+=1
                st.session_state.answered=False; st.rerun()


# ============================================================
# Part 2: 記憶TEST
# ============================================================
def render_part2():
    queue=st.session_state.part2_queue; idx=st.session_state.part2_index
    if idx>=len(queue):
        if st.session_state.part2_wrong:
            st.session_state.part2_queue=st.session_state.part2_wrong
            st.session_state.part2_wrong=[]; st.session_state.part2_index=0; st.rerun()
        else:
            st.session_state.page="complete"; st.rerun()
        return
    word=queue[idx]; total=len(queue)
    col=color_for(word.get('category','other'))
    st.progress(idx/total if total else 0)
    st.caption(f"🔁 Memory Test {idx+1} / {total}")
    st.markdown(f"""<div class="word-card" style="background:linear-gradient(135deg,{col},{col}cc);">
        <div class="word-kana">{word.get('katakana','')}</div>
        <div class="word-en">{word['english']}</div>
        <div class="word-phonetic">{word['phonetic']}</div></div>""", unsafe_allow_html=True)
    all_words=srs.load_words()
    ck=f"p2c_{word['word_id']}"
    if ck not in st.session_state:
        ch,co=make_choices(word,all_words); st.session_state[ck]={"ch":ch,"co":co}
    ch=st.session_state[ck]["ch"]; co=st.session_state[ck]["co"]
    st.markdown("**What does it mean?**")
    if not st.session_state.answered:
        sel=st.radio("c",ch,key=f"p2r_{word['word_id']}_{idx}",label_visibility="collapsed")
        if st.button("Answer",use_container_width=True,type="primary"):
            st.session_state.answered=True; st.session_state.last_correct=(sel==co); st.rerun()
    else:
        if st.session_state.last_correct:
            st.success(f"✅ Correct! {word['definition']}")
            if st.button("Next →",use_container_width=True,type="primary"):
                srs.mark_review_result(word['word_id'],True)
                del st.session_state[ck]; st.session_state.part2_index+=1
                st.session_state.answered=False; st.rerun()
        else:
            st.error(f"❌ Wrong. Answer: {co}")
            if st.button("Retry →",use_container_width=True):
                srs.mark_review_result(word['word_id'],False)
                if word not in st.session_state.part2_wrong: st.session_state.part2_wrong.append(word)
                del st.session_state[ck]; st.session_state.part2_index+=1
                st.session_state.answered=False; st.rerun()


# ============================================================
# 完了
# ============================================================
def render_complete():
    srs.complete_today_mission()
    s=srs.get_progress_summary()
    st.balloons()
    st.markdown(f"""<div style="text-align:center;padding:40px 20px;">
        <div style="font-size:64px;">🎉</div>
        <div style="font-size:28px;font-weight:700;margin:16px 0;">Mission Complete!</div>
        <div style="font-size:18px;color:#FF6B35;font-weight:700;">🔥 連続 {s['streak_current']}日</div>
        <div style="font-size:16px;color:#28B448;margin-top:8px;">⭐ マスター {s['mastered']}語</div>
    </div>""", unsafe_allow_html=True)
    st.success("Great job today!")
    if st.button("📅 Calendar",use_container_width=True):
        st.session_state.page="calendar"; st.rerun()
    if st.button("🏠 Back to Home",use_container_width=True):
        st.session_state.page="home"; st.rerun()


# ============================================================
# カレンダー
# ============================================================
def render_calendar():
    st.markdown("### 📅 Calendar")
    status_bar()
    y=st.session_state.cal_year; m=st.session_state.cal_month
    c1,c2,c3=st.columns([1,2,1])
    with c1:
        if st.button("← Prev"):
            if m==1: st.session_state.cal_month=12; st.session_state.cal_year-=1
            else: st.session_state.cal_month-=1
            st.rerun()
    with c2:
        st.markdown(f"<div style='text-align:center;font-size:18px;font-weight:700;'>{y}/{m}</div>",unsafe_allow_html=True)
    with c3:
        if st.button("Next →"):
            if m==12: st.session_state.cal_month=1; st.session_state.cal_year+=1
            else: st.session_state.cal_month+=1
            st.rerun()
    cd=srs.get_calendar(y,m)
    fw=(date(y,m,1).weekday()+1)%7
    html='<div style="display:grid;grid-template-columns:repeat(7,1fr);gap:4px;text-align:center;">'
    for wd in ["Sun","Mon","Tue","Wed","Thu","Fri","Sat"]:
        html+=f'<div style="font-size:11px;color:#999;padding:4px;">{wd}</div>'
    for _ in range(fw): html+='<div></div>'
    for d in cd["days"]:
        bg="#f8f8f8"; em=""
        if d["completed"]: bg="rgba(255,107,53,0.15)"; em="🔥"
        if d["is_exam"]: bg="rgba(74,144,226,0.2)"; em="🎯"
        elif d["is_australia"]: bg="rgba(40,180,72,0.12)"; em=em or "🇦🇺"
        bd="2px solid #4A90E2" if d["is_today"] else "1px solid #eee"
        html+=f'<div style="background:{bg};border:{bd};border-radius:8px;padding:6px 2px;min-height:44px;"><div style="font-size:12px;font-weight:600;">{d["day"]}</div><div style="font-size:14px;">{em}</div></div>'
    html+='</div>'
    st.markdown(html,unsafe_allow_html=True)
    st.caption("🔥 Done　🇦🇺 Australia　🎯 Eiken")
    st.divider()
    if st.button("🏠 Back to Home",use_container_width=True):
        st.session_state.page="home"; st.rerun()


def main():
    p=st.session_state.page
    if p=="home": render_home()
    elif p=="category": render_category()
    elif p=="part1": render_part1()
    elif p=="part2": render_part2()
    elif p=="complete": render_complete()
    elif p=="calendar": render_calendar()
    else: render_home()
    st.caption(f"GAVI {APP_VERSION}")

if __name__=="__main__":
    main()
