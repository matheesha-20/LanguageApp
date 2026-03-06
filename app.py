import streamlit as st
import pandas as pd
import random
import time

# --- 1. CONFIGURATION ---
LANG_CONFIG = {
    "Italian 🇮🇹": {"url": "https://docs.google.com/spreadsheets/d/e/2PACX-1vQEYl7N7muoi3zY5fgFDBWo8gPrNKJvj8sJQQYmm-nAyF1qE6DMgl2a3cuNsbbrzPMIht-JervgZkMn/pub?gid=376702926&single=true&output=csv", "key": "it"},
    "English 🇺🇸": {"url": "https://docs.google.com/spreadsheets/d/e/2PACX-1vQEYl7N7muoi3zY5fgFDBWo8gPrNKJvj8sJQQYmm-nAyF1qE6DMgl2a3cuNsbbrzPMIht-JervgZkMn/pub?gid=1228520353&single=true&output=csv", "key": "en"},
    "English Synonyms 🇺🇸": {"url": "https://docs.google.com/spreadsheets/d/e/2PACX-1vQEYl7N7muoi3zY5fgFDBWo8gPrNKJvj8sJQQYmm-nAyF1qE6DMgl2a3cuNsbbrzPMIht-JervgZkMn/pub?gid=703983749&single=true&output=csv", "key": "ensyn"},
    "Japanese 🇯🇵": {"url": "https://docs.google.com/spreadsheets/d/e/2PACX-1vQEYl7N7muoi3zY5fgFDBWo8gPrNKJvj8sJQQYmm-nAyF1qE6DMgl2a3cuNsbbrzPMIht-JervgZkMn/pub?gid=1635387400&single=true&output=csv", "key": "jp"}
}

st.set_page_config(page_title="Universal Learning Pro", page_icon="🌎")

# --- 2. DATA LOADING ---
@st.cache_data(ttl=600)
def load_data(url):
    try:
        df = pd.read_csv(url)
        df.columns = df.columns.str.strip()
        return df.fillna('').to_dict('records')
    except Exception as e:
        st.error(f"දත්ත ලබාගැනීමේ දෝෂයක්: {e}")
        return []

# --- 3. HELPER FUNCTIONS ---
def get_display_logic(selected_lang, curr_word, conf):
    if "Synonyms" in selected_lang:
        display = curr_word.get(conf["key"], "N/A")
        
        # අහඹු ලෙස Advanced1 හෝ Advanced2 තෝරාගනී
        adv_keys = [k for k in ["Advanced1", "Advanced2"] if curr_word.get(k)]
        ans_key = random.choice(adv_keys) if adv_keys else conf["key"]
        
        correct = str(curr_word.get(ans_key, "N/A")).strip()
        sub_text = curr_word.get("Sinhala Meaning", "Select the Advanced Synonym")
        mode = "SynonymMode"
    else:
        display = curr_word.get(conf["key"], "N/A")
        correct = str(curr_word.get("si", "N/A")).strip()
        pr = curr_word.get("pr", "")
        sub_text = f"({pr})" if pr else ""
        mode = "TranslationMode"
        
    return display, correct, sub_text, mode

# --- 4. SIDEBAR ---
with st.sidebar:
    st.header("⚙️ Settings")
    selected_lang_name = st.selectbox("භාෂාව තෝරන්න:", list(LANG_CONFIG.keys()))
    
    if 'last_lang' not in st.session_state or st.session_state.last_lang != selected_lang_name:
        st.session_state.last_lang = selected_lang_name
        for key in ['word_pool', 'game_round', 'score', 'wrong_list', 'current_set', 'is_answered', 'current_options']:
            if key in st.session_state: del st.session_state[key]
        st.rerun()

conf = LANG_CONFIG[selected_lang_name]
words = load_data(conf["url"])

if not words: st.stop()

# --- 5. SESSION INITIALIZE ---
if 'word_pool' not in st.session_state:
    st.session_state.word_pool = words
    st.session_state.current_set = random.sample(words, min(10, len(words)))
    st.session_state.game_round = 0
    st.session_state.score = 0
    st.session_state.wrong_list = []
    st.session_state.is_answered = False
    st.session_state.is_retake_mode = False

# --- 6. GAME UI & LOGIC ---
if st.session_state.game_round < len(st.session_state.current_set):
    curr_word = st.session_state.current_set[st.session_state.game_round]
    display_word, correct_ans, sub_info, mode = get_display_logic(selected_lang_name, curr_word, conf)

    st.title(f"{selected_lang_name}")
    st.subheader(f"ප්‍රශ්නය: {st.session_state.game_round + 1} / {len(st.session_state.current_set)}")
    
    # UI Card
    border_color = "#007BFF" if mode == "SynonymMode" else "#008C45"
    st.markdown(f"""
        <div style="background-color: #f8f9fa; padding: 25px; border-radius: 15px; text-align: center; border-bottom: 10px solid {border_color}; margin-bottom: 20px; box-shadow: 2px 2px 10px rgba(0,0,0,0.1);">
            <h1 style="color: #333; margin:0; font-size: 50px;">{display_word}</h1>
            <p style="color: #666; font-size: 20px;">{sub_info}</p>
        </div>
    """, unsafe_allow_html=True)

    # --- MCQ GENERATOR (RE-FIXED) ---
    if 'current_options' not in st.session_state:
        wrong_candidates = set()
        
        if mode == "SynonymMode":
            for w in st.session_state.word_pool:
                for k in ["Advanced1", "Advanced2", "ensyn"]:
                    val = str(w.get(k, '')).strip()
                    # නිවැරදි පිළිතුරට සමාන කිසිම දෙයක් pool එකට ගන්නේ නැත
                    if val and val != correct_ans:
                        wrong_candidates.add(val)
        else:
            for w in st.session_state.word_pool:
                val = str(w.get('si', '')).strip()
                if val and val != correct_ans:
                    wrong_candidates.add(val)

        # අහඹු ලෙස වැරදි පිළිතුරු 3ක් තෝරාගනී
        wrong_options = random.sample(list(wrong_candidates), min(3, len(wrong_candidates)))
        
        # නිවැරදි පිළිතුර අනිවාර්යයෙන්ම ඇතුළත් කර shuffle කරයි
        final_opts = wrong_options + [correct_ans]
        random.shuffle(final_opts)
        st.session_state.current_options = final_opts

    # Display Buttons
    cols = st.columns(2)
    for i, opt in enumerate(st.session_state.current_options):
        with cols[i % 2]:
            if st.button(opt, use_container_width=True, key=f"btn_{st.session_state.game_round}_{i}_{opt}", disabled=st.session_state.is_answered):
                st.session_state.is_answered = True
                if opt == correct_ans:
                    st.success("නිවැරදියි! ✅")
                    if not st.session_state.is_retake_mode: st.session_state.score += 1
                else:
                    st.error(f"වැරදියි! ❌ පිළිතුර: {correct_ans}")
                    if curr_word not in st.session_state.wrong_list:
                        st.session_state.wrong_list.append(curr_word)
                
                time.sleep(1.2)
                st.session_state.game_round += 1
                st.session_state.is_answered = False
                if 'current_options' in st.session_state: del st.session_state.current_options
                st.rerun()
else:
    st.balloons()
    st.success(f"වටය අවසන්! ලකුණු: {st.session_state.score}/{len(st.session_state.current_set)}")
    if st.button("නැවත ආරම්භ කරන්න 🔄"):
        st.session_state.game_round = 0
        st.session_state.score = 0
        st.session_state.wrong_list = []
        st.session_state.current_set = random.sample(st.session_state.word_pool, min(10, len(st.session_state.word_pool)))
        st.rerun()