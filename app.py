import streamlit as st
import pandas as pd
import random
import time
import google.generativeai as genai

# --- 1. API & MODEL CONFIG ---
# [පරෙස්සමෙන්: උඹේ Gemini API Key එක මෙතනට දාපන්]
GEMINI_API_KEY = "AIzaSyCa2UGRHKcmOBhzlsUM8LxwEG2e3yqJKtA" 
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash-latest')

# ඇප් එකේ පෙනුම
st.set_page_config(page_title="Universal Language Master", page_icon="🌎", layout="centered")

# --- 2. DATA LOADING ---
# අපි පාවිච්චි කරන්නේ English-Sinhala පදනම් කරගත් වචන මාලාවක්
sheet_url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQEYl7N7muoi3zY5fgFDBWo8gPrNKJvj8sJQQYmm-nAyF1qE6DMgl2a3cuNsbbrzPMIht-JervgZkMn/pub?gid=1635387400&single=true&output=csv"

@st.cache_data(ttl=3600)
def load_data():
    try:
        df = pd.read_csv(sheet_url)
        df.columns = df.columns.str.strip()
        return df.to_dict('records')
    except:
        return []

# --- 3. AI TRANSLATION LOGIC ---
def get_target_word(english_word, target_lang):
    """ඉංග්‍රීසි වචනය AI එක හරහා අදාළ භාෂාවට සහ උච්චාරණයට හරවයි"""
    if target_lang == "English":
        return english_word, ""
    
    prompt = f"Translate the English word '{english_word}' to {target_lang}. Provide the translated word and its Sinhala pronunciation. Format: Word | Pronunciation"
    try:
        response = model.generate_content(prompt)
        res_parts = response.text.strip().split('|')
        return res_parts[0].strip(), res_parts[1].strip() if len(res_parts) > 1 else ""
    except:
        return english_word, "N/A"

# --- 4. SESSION STATE INITIALIZE ---
words = load_data()

if 'game_round' not in st.session_state:
    st.session_state.game_round = 0
    st.session_state.score = 0
    st.session_state.wrong_list = []
    st.session_state.current_set = random.sample(words, 10) if words else []
    st.session_state.is_answered = False

# --- 5. UI DESIGN ---
st.title("🌎 Universal Language Master")

# Sidebar එකේ භාෂාව තෝරන්න දෙමු
with st.sidebar:
    st.header("⚙️ Settings")
    selected_lang = st.selectbox(
        "ඔබට ඉගෙන ගැනීමට අවශ්‍ය භාෂාව:",
        ["English", "Italian", "Japanese", "French", "Korean", "German"]
    )
    st.divider()
    if st.button("🔄 අලුත් වටයක් පටන් ගන්න"):
        st.session_state.game_round = 0
        st.session_state.score = 0
        st.session_state.current_set = random.sample(words, 10)
        st.rerun()

# --- 6. GAME LOGIC ---
if st.session_state.game_round < len(st.session_state.current_set):
    curr_data = st.session_state.current_set[st.session_state.game_round]
    
    # English වචනය අරන් ඒක AI එකෙන් අදාළ භාෂාවට හරවනවා
    english_base = curr_data.get('it', 'Hello') # මෙතන 'it' කියන්නේ Sheet එකේ වචනය
    with st.spinner(f'{selected_lang} වලට පරිවර්තනය වෙමින්...'):
        display_word, pronunciation = get_target_word(english_base, selected_lang)
    
    si_meaning = curr_data.get('si', 'N/A')

    st.subheader(f"ප්‍රශ්නය: {st.session_state.game_round + 1} / 10")
    
    # ප්‍රශ්න පෙන්වන Card එක
    st.markdown(f"""
        <div style="background-color: #f0f2f6; padding: 30px; border-radius: 20px; text-align: center; border: 2px solid #007bff;">
            <p style="color: #555; font-size: 16px;">{selected_lang} වචනය:</p>
            <h1 style="margin: 0; color: #111;">{display_word}</h1>
            <p style="color: #007bff; font-weight: bold;">({pronunciation})</p>
        </div>
    """, unsafe_allow_html=True)

    # MCQ Options
    if 'opts' not in st.session_state or st.session_state.game_round != st.session_state.get('last_round', -1):
        correct = si_meaning
        others = [w['si'] for w in words if w['si'] != correct]
        wrong = random.sample(others, 3)
        all_opts = wrong + [correct]
        random.shuffle(all_opts)
        st.session_state.opts = all_opts
        st.session_state.last_round = st.session_state.game_round

    st.write("---")
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
                
                time.sleep(1.5)
                st.session_state.game_round += 1
                st.session_state.is_answered = False
                st.rerun()

else:
    st.balloons()
    st.success(f"වටය අවසන්! ඔබේ ලකුණු: {st.session_state.score} / 10")
    if st.button("ඊළඟ වටයට යන්න ➡️"):
        st.session_state.game_round = 0
        st.session_state.score = 0
        st.session_state.current_set = random.sample(words, 10)
        st.rerun()