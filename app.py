import streamlit as st
import pandas as pd
import random
import time

# --- 1. CONFIGURATION & LINKS ---
LANG_CONFIG = {
    "Italian 🇮🇹": {
        "url": "https://docs.google.com/spreadsheets/d/e/2PACX-1vQEYl7N7muoi3zY5fgFDBWo8gPrNKJvj8sJQQYmm-nAyF1qE6DMgl2a3cuNsbbrzPMIht-JervgZkMn/pub?gid=376702926&single=true&output=csv",
        "key": "it"
    },
    "English 🇺🇸": {
        "url": "https://docs.google.com/spreadsheets/d/e/2PACX-1vQEYl7N7muoi3zY5fgFDBWo8gPrNKJvj8sJQQYmm-nAyF1qE6DMgl2a3cuNsbbrzPMIht-JervgZkMn/pub?gid=1228520353&single=true&output=csv",
        "key": "en"
    },
    "English Synonyms 🇺🇸": {
        "url": "https://docs.google.com/spreadsheets/d/e/2PACX-1vQEYl7N7muoi3zY5fgFDBWo8gPrNKJvj8sJQQYmm-nAyF1qE6DMgl2a3cuNsbbrzPMIht-JervgZkMn/pub?gid=703983749&single=true&output=csv",
        "key": "en" # We use 'en' as the question base
    },
    "Japanese 🇯🇵": {
        "url": "https://docs.google.com/spreadsheets/d/e/2PACX-1vQEYl7N7muoi3zY5fgFDBWo8gPrNKJvj8sJQQYmm-nAyF1qE6DMgl2a3cuNsbbrzPMIht-JervgZkMn/pub?gid=1635387400&single=true&output=csv",
        "key": "jp"
    }
}

st.set_page_config(page_title="Universal Learning Pro", page_icon="🌎")

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

# --- 3. HELPER FUNCTIONS ---
def get_display_logic(selected_lang, curr_word, conf):
    """Handles logic for switching between translation and synonym modes."""
    if "Synonyms" in selected_lang:
        # Check for 'Basic Word' first, then 'en' as fallback
        display = curr_word.get("ensyn", curr_word.get("en", "N/A"))
        # Check for 'Advanced Word 1' first, then 'ensyn' as fallback
        correct = curr_word.get("Advanced Word 1", curr_word.get("ensyn", "N/A"))
        sub_text = curr_word.get("Sinhala Meaning", curr_word.get("ensyn", "N/A"))
        ans_key = "Advanced Word 1" if "Advanced Word 1" in curr_word else "ensyn"
    else:
        display = curr_word.get(conf["key"], "N/A")
        correct = curr_word.get("si", "N/A")
        pr = curr_word.get("pr", "")
        sub_text = f"({pr})" if pr else ""
        ans_key = "si"
    return display, correct, sub_text, ans_key

# --- 4. SIDEBAR: LANGUAGE SELECTOR ---
with st.sidebar:
    st.header("⚙️ Settings")
    selected_lang_name = st.selectbox("ඉගෙන ගන්නා භාෂාව තෝරන්න:", list(LANG_CONFIG.keys()))
    
    if 'last_lang' not in st.session_state or st.session_state.last_lang != selected_lang_name:
        st.session_state.last_lang = selected_lang_name
        keys_to_reset = ['word_pool', 'game_round', 'score', 'wrong_list', 'current_set', 'is_answered', 'current_options']
        for key in keys_to_reset:
            if key in st.session_state: del st.session_state[key]
        st.rerun()

conf = LANG_CONFIG[selected_lang_name]
words = load_data(conf["url"])

if not words:
    st.warning("දත්ත ලැබුණේ නැහැ. කරුණාකර Link පරීක්ෂා කරන්න.")
    st.stop()

# --- 5. SESSION STATES INITIALIZE ---
if 'word_pool' not in st.session_state:
    st.session_state.word_pool = words
    st.session_state.current_set = random.sample(words, min(10, len(words)))
    st.session_state.game_round = 0
    st.session_state.score = 0
    st.session_state.wrong_list = []
    st.session_state.is_answered = False
    st.session_state.is_retake_mode = False

st.title(f"{selected_lang_name} Challenge")

# --- 6. GAME LOGIC ---
if st.session_state.game_round < len(st.session_state.current_set):
    curr_word = st.session_state.current_set[st.session_state.game_round]
    
    # Get Dynamic Content
    display_word, correct_ans, sub_info, ans_col = get_display_logic(selected_lang_name, curr_word, conf)

    mode_text = "වැරදුණු වචන පුහුණුව" if st.session_state.is_retake_mode else "ප්‍රශ්න වටය"
    st.subheader(f"{mode_text}: {st.session_state.game_round + 1} / {len(st.session_state.current_set)}")
    
    # UI Design
    if "Italian" in selected_lang_name: border_color = "#008C45"
    elif "Synonyms" in selected_lang_name: border_color = "#007BFF"
    else: border_color = "#BC002D"
    
    st.markdown(f"""
        <div style="background-color: #f8f9fa; padding: 25px; border-radius: 15px; text-align: center; border-bottom: 10px solid {border_color}; margin-bottom: 20px; box-shadow: 2px 2px 10px rgba(0,0,0,0.1);">
            <h1 style="color: #333; margin:0; font-size: 50px;">{display_word}</h1>
            <p style="color: #666; font-size: 20px;">{sub_info}</p>
        </div>
    """, unsafe_allow_html=True)

    # Options (MCQ) Generator
    if 'current_options' not in st.session_state:
        # Pull wrong candidates from the correct answer column (ensyn or si)
        wrong_candidates = [w.get(ans_col, 'N/A') for w in st.session_state.word_pool if w.get(ans_col) != correct_ans]
        wrong_options = random.sample(wrong_candidates, min(3, len(wrong_candidates)))
        all_opts = wrong_options + [correct_ans]
        random.shuffle(all_opts)
        st.session_state.current_options = all_opts

    # Display Buttons
    cols = st.columns(2)
    for i, opt in enumerate(st.session_state.current_options):
        with cols[i % 2]:
            if st.button(opt, use_container_width=True, key=f"btn_{st.session_state.game_round}_{opt}", disabled=st.session_state.is_answered):
                st.session_state.is_answered = True
                if opt == correct_ans:
                    st.success("නිවැරදියි! ✅")
                    if not st.session_state.is_retake_mode:
                        st.session_state.score += 1
                else:
                    st.error(f"වැරදියි! ❌ නිවැරදි පිළිතුර: {correct_ans}")
                    if curr_word not in st.session_state.wrong_list:
                        st.session_state.wrong_list.append(curr_word)
                
                time.sleep(1.2)
                st.session_state.game_round += 1
                st.session_state.is_answered = False
                if 'current_options' in st.session_state: del st.session_state.current_options
                st.rerun()

# End of Round Logic
else:
    if st.session_state.wrong_list:
        st.warning(f"වටය අවසන්! ලකුණු: {st.session_state.score}/{len(st.session_state.current_set)}")
        if st.button("වැරදුණු වචන ටික ආයෙත් කරමු 🔄"):
            st.session_state.current_set = list(st.session_state.wrong_list)
            st.session_state.wrong_list = [] 
            st.session_state.game_round = 0
            st.session_state.is_retake_mode = True 
            if 'current_options' in st.session_state: del st.session_state.current_options
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
            if 'current_options' in st.session_state: del st.session_state.current_options
            st.rerun()