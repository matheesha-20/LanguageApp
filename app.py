import streamlit as st
import pandas as pd
import random
import time

# --- 1. CONFIGURATION & LINKS ---
# භාෂාව අනුව ලින්ක් සහ Column Names මෙතන Define කරමු
LANG_CONFIG = {
    "Italian 🇮🇹": {
        "url": "https://docs.google.com/spreadsheets/d/e/2PACX-1vQEYl7N7muoi3zY5fgFDBWo8gPrNKJvj8sJQQYmm-nAyF1qE6DMgl2a3cuNsbbrzPMIht-JervgZkMn/pub?gid=376702926&single=true&output=csv",
        "key": "it"
    },
    "Japanese 🇯🇵": {
        "url": "https://docs.google.com/spreadsheets/d/e/2PACX-1vQEYl7N7muoi3zY5fgFDBWo8gPrNKJvj8sJQQYmm-nAyF1qE6DMgl2a3cuNsbbrzPMIht-JervgZkMn/pub?gid=1635387400&single=true&output=csv",
        "key": "jp"
    }
}

st.set_page_config(page_title="Universal Learning Pro", page_icon="🌎")

conf = LANG_CONFIG[selected_lang_name]

# --- 2. DATA LOADING ---
@st.cache_data(ttl=600) 
def load_data(url):
    try:
        df = pd.read_csv(url)
        df.columns = df.columns.str.strip()
        return df.to_dict('records')
    except Exception as e:
        st.error(f"දත්ත ලබාගැනීමේ දෝෂයක්: {e}")
        return []

# --- 3. SIDEBAR: LANGUAGE SELECTOR ---
with st.sidebar:
    st.header("⚙️ Settings")
    selected_lang_name = st.selectbox("ඉගෙන ගන්නා භාෂාව තෝරන්න:", list(LANG_CONFIG.keys()))
    
    # භාෂාව මාරු කළොත් පරණ Data Reset කරනවා
    if 'last_lang' in st.session_state and st.session_state.last_lang != selected_lang_name:
        for key in ['word_pool', 'game_round', 'score', 'wrong_list', 'current_set', 'is_answered']:
            if key in st.session_state: del st.session_state[key]
            
    st.session_state.last_lang = selected_lang_name
    conf = LANG_CONFIG[selected_lang_name]

# ඩේටා ලෝඩ් කිරීම
words = load_data(conf["url"])

if not words:
    st.warning("දත්ත ලැබුණේ නැහැ.")
    st.stop()

# --- 4. SESSION STATES INITIALIZE ---
if 'word_pool' not in st.session_state or st.session_state.last_lang != selected_lang_name:
    st.session_state.word_pool = words
    # අලුත් භාෂාවට අදාළව ප්‍රශ්න 10කුත් අලුතින්ම ගන්නවා
    st.session_state.current_set = random.sample(st.session_state.word_pool, min(10, len(st.session_state.word_pool)))
    st.session_state.game_round = 0
    st.session_state.score = 0
    st.session_state.wrong_list = []
    st.session_state.is_answered = False
    st.session_state.is_retake_mode = False

if 'game_round' not in st.session_state:
    st.session_state.game_round = 0
    st.session_state.score = 0
    st.session_state.wrong_list = []
    st.session_state.is_retake_mode = False 
    st.session_state.current_set = random.sample(st.session_state.word_pool, min(10, len(st.session_state.word_pool)))
    st.session_state.is_answered = False

st.title(f"{selected_lang_name} Challenge")

# --- 5. GAME LOGIC ---
if st.session_state.game_round < len(st.session_state.current_set):
    curr_word = st.session_state.current_set[st.session_state.game_round]
    
    mode_text = "වැරදුණු වචන පුහුණුව" if st.session_state.is_retake_mode else "ප්‍රශ්න වටය"
    st.subheader(f"{mode_text}: {st.session_state.game_round + 1} / {len(st.session_state.current_set)}")
    
    # භාෂාව අනුව Column එක තෝරා ගැනීම (it හෝ jp)
    display_word = curr_word.get(conf["key"], 'N/A')
    pr_word = curr_word.get('pr', '')
    si_word = curr_word.get('si', 'N/A')

    # UI Design - භාෂාව අනුව වර්ණ වෙනස් කිරීම
    border_color = "#008C45" if "Italian" in selected_lang_name else "#BC002D"
    
    st.markdown(f"""
        <div style="background-color: #f8f9fa; padding: 25px; border-radius: 15px; text-align: center; border-bottom: 10px solid {border_color}; margin-bottom: 20px; box-shadow: 2px 2px 10px rgba(0,0,0,0.1);">
            <h1 style="color: #333; margin:0; font-size: 50px;">{display_word}</h1>
            <p style="color: #666; font-size: 20px;">({pr_word})</p>
        </div>
    """, unsafe_allow_html=True)

    if 'current_options' not in st.session_state:
        correct_ans = si_word
        wrong_candidates = [w.get('si', 'N/A') for w in st.session_state.word_pool if w.get('si') != correct_ans]
        wrong_options = random.sample(wrong_candidates, min(3, len(wrong_candidates)))
        all_opts = wrong_options + [correct_ans]
        random.shuffle(all_opts)
        st.session_state.current_options = all_opts

    # Buttons
    cols = st.columns(2)
    for i, opt in enumerate(st.session_state.current_options):
        with cols[i % 2]:
            if st.button(opt, use_container_width=True, key=f"btn_{st.session_state.game_round}_{opt}", disabled=st.session_state.is_answered):
                st.session_state.is_answered = True
                if opt == si_word:
                    st.success("නිවැරදියි! ✅")
                    if not st.session_state.is_retake_mode:
                        st.session_state.score += 1
                else:
                    st.error(f"වැරදියි! ❌ නිවැරදි පිළිතුර: {si_word}")
                    if curr_word not in st.session_state.wrong_list:
                        st.session_state.wrong_list.append(curr_word)
                
                time.sleep(1.2)
                st.session_state.game_round += 1
                st.session_state.is_answered = False
                if 'current_options' in st.session_state: del st.session_state.current_options
                st.rerun()

# End of Game
else:
    if st.session_state.wrong_list:
        st.warning(f"වටය අවසන්! ලකුණු: {st.session_state.score}/{len(st.session_state.current_set)}")
        if st.button("වැරදුණු වචන ටික ආයෙත් කරමු 🔄"):
            st.session_state.current_set = list(st.session_state.wrong_list)
            st.session_state.wrong_list = [] 
            st.session_state.game_round = 0
            st.session_state.is_retake_mode = True 
            st.rerun()
            
    else:
        st.balloons()
        st.success(f"නියමයි! ඔබ {selected_lang_name} සියලුම වචන නිවැරදිව ඉගෙන ගත්තා. 🏆")
        if st.button("ඊළඟ අලුත් වචන 10 පටන් ගන්න ➡️"):
            st.session_state.game_round = 0
            st.session_state.score = 0
            st.session_state.wrong_list = []
            st.session_state.is_retake_mode = False
            st.session_state.current_set = random.sample(st.session_state.word_pool, min(10, len(st.session_state.word_pool)))
            st.rerun()