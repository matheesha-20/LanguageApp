import streamlit as st
import pandas as pd
import random
import time

# --- 1. CONFIGURATION ---
st.set_page_config(page_title="Universal Language Master", page_icon="🌎", layout="centered")

# භාෂාව අනුව Google Sheet ලින්ක් ටික මෙතන තියෙනවා
SHEET_LINKS = {
    "Italian": "https://docs.google.com/spreadsheets/d/e/2PACX-1vQEYl7N7muoi3zY5fgFDBWo8gPrNKJvj8sJQQYmm-nAyF1qE6DMgl2a3cuNsbbrzPMIht-JervgZkMn/pub?gid=1635387400&single=true&output=csv",
    "Japanese": "https://docs.google.com/spreadsheets/d/e/2PACX-1vQEYl7N7muoi3zY5fgFDBWo8gPrNKJvj8sJQQYmm-nAyF1qE6DMgl2a3cuNsbbrzPMIht-JervgZkMn/pub?gid=376702926&single=true&output=csv"
}

# --- 2. DATA LOADING FUNCTION ---
def load_data(url):
    try:
        # මචං මෙතන ttl=0 දැම්මේ භාෂාව මාරු කරපු ගමන් අලුත් ඩේටා ගන්න ඕන නිසා
        df = pd.read_csv(url)
        df.columns = df.columns.str.strip() # Column names වල තියෙන හිස්තැන් අයින් කරනවා
        return df.to_dict('records')
    except Exception as e:
        st.error(f"දත්ත ලබාගැනීමේ දෝෂයක්: {e}")
        return []

# --- 3. SIDEBAR: LANGUAGE SELECTION ---
with st.sidebar:
    st.header("⚙️ Settings")
    selected_lang = st.selectbox(
        "ඔබ ඉගෙන ගැනීමට අවශ්‍ය භාෂාව:",
        list(SHEET_LINKS.keys())
    )
    
    # භාෂාව මාරු කළොත් සෙෂන් එක රීසෙට් කරන්න බටන් එකක්
    if st.button("🔄 අලුත් වටයක් පටන් ගන්න"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()

# --- 4. SESSION STATE INITIALIZE ---
# තෝරගත් භාෂාවට අදාළ ලින්ක් එකෙන් ඩේටා ලෝඩ් කරනවා
current_url = SHEET_LINKS[selected_lang]
words = load_data(current_url)

if not words:
    st.warning(f"{selected_lang} සඳහා දත්ත පූරණය කළ නොහැකි විය.")
    st.stop()

if 'current_set' not in st.session_state or st.session_state.get('last_lang') != selected_lang:
    st.session_state.last_lang = selected_lang
    st.session_state.game_round = 0
    st.session_state.score = 0
    st.session_state.wrong_list = []
    # වචන 100 ම තියෙනවා නම් ඒ අතරින් 10ක් ගන්නවා
    st.session_state.current_set = random.sample(words, min(10, len(words)))
    st.session_state.is_answered = False

# --- 5. GAME UI ---
st.title(f"🌎 {selected_lang} Master Challenge")

if st.session_state.game_round < len(st.session_state.current_set):
    curr_data = st.session_state.current_set[st.session_state.game_round]
    
    # ෂීට් එකේ තියෙන Column names වලට අනුව (it හෝ jp)
    # අපි පොදුවේ ඉස්සරහ කෑල්ලට 'word' කියමු
    display_word = curr_data.get('it') if selected_lang == "Italian" else curr_data.get('jp')
    pronunciation = curr_data.get('pr', '')
    si_meaning = curr_data.get('si', 'N/A')

    st.subheader(f"ප්‍රශ්නය: {st.session_state.game_round + 1} / {len(st.session_state.current_set)}")
    
    # ප්‍රශ්න Card එක
    st.markdown(f"""
        <div style="background-color: #f8f9fa; padding: 30px; border-radius: 20px; text-align: center; border-left: 10px solid #007bff; box-shadow: 2px 2px 10px rgba(0,0,0,0.1);">
            <h1 style="margin: 0; color: #111; font-size: 50px;">{display_word}</h1>
            <p style="color: #007bff; font-weight: bold; font-size: 20px;">({pronunciation})</p>
        </div>
    """, unsafe_allow_html=True)

    # MCQ Options හදන හැටි
    if 'opts' not in st.session_state or st.session_state.game_round != st.session_state.get('opt_round', -1):
        correct = si_meaning
        # අනිත් වැරදි පිළිතුරු ටික ෂීට් එකෙන්ම ගන්නවා
        others = [w['si'] for w in words if w['si'] != correct]
        wrong = random.sample(others, min(3, len(others)))
        all_opts = wrong + [correct]
        random.shuffle(all_opts)
        st.session_state.opts = all_opts
        st.session_state.opt_round = st.session_state.game_round

    st.write("<br>", unsafe_allow_html=True)
    cols = st.columns(2)
    for i, opt in enumerate(st.session_state.opts):
        with cols[i % 2]:
            if st.button(opt, key=f"opt_{i}", use_container_width=True, disabled=st.session_state.is_answered):
                st.session_state.is_answered = True
                if opt == si_meaning:
                    st.success("නිවැරදියි! ✅")
                    st.session_state.score += 1
                else:
                    st.error(f"වැරදියි! ❌ නිවැරදි තේරුම: {si_meaning}")
                
                time.sleep(1.2)
                st.session_state.game_round += 1
                st.session_state.is_answered = False
                st.rerun()

else:
    st.balloons()
    st.success(f"වටය අවසන්! ඔබේ ලකුණු: {st.session_state.score} / {len(st.session_state.current_set)}")
    if st.button("ඊළඟ අලුත් වචන 10 පටන් ගන්න ➡️"):
        st.session_state.game_round = 0
        st.session_state.score = 0
        st.session_state.current_set = random.sample(words, min(10, len(words)))
        st.rerun()