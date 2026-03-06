import streamlit as st
import pandas as pd
import random
import time

# Google Sheet Link (CSV)
sheet_url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQEYl7N7muoi3zY5fgFDBWo8gPrNKJvj8sJQQYmm-nAyF1qE6DMgl2a3cuNsbbrzPMIht-JervgZkMn/pub?output=csv"

@st.cache_data(ttl=600) 
def load_data():
    try:
        df = pd.read_csv(sheet_url)
        df.columns = df.columns.str.strip()
        return df.to_dict('records')
    except Exception as e:
        st.error(f"දත්ත ලබාගැනීමේ දෝෂයක්: {e}")
        return []

words = load_data()

st.set_page_config(page_title="Italy Learning Pro", page_icon="🇮🇹")

if not words:
    st.warning("දත්ත ලැබුණේ නැහැ. කරුණාකර Link එක පරීක්ෂා කරන්න.")
    st.stop()

# --- Session States Initialize ---
if 'word_pool' not in st.session_state:
    st.session_state.word_pool = words

if 'game_round' not in st.session_state:
    st.session_state.game_round = 0
    st.session_state.score = 0
    st.session_state.wrong_list = []
    st.session_state.is_retake_mode = False # වැරදුණු ටික විතරක් කරන වටයද?
    st.session_state.current_set = random.sample(st.session_state.word_pool, 10)
    st.session_state.is_answered = False

st.title("🇮🇹 Italy Master Challenge")

# Game Logic
if st.session_state.game_round < len(st.session_state.current_set):
    curr_word = st.session_state.current_set[st.session_state.game_round]
    
    # Header එක වෙනස් වෙනවා වටය අනුව
    mode_text = "වැරදුණු වචන පුහුණුව" if st.session_state.is_retake_mode else "ප්‍රශ්න වටය"
    st.subheader(f"{mode_text}: {st.session_state.game_round + 1} / {len(st.session_state.current_set)}")
    
    it_word = curr_word.get('it', 'N/A')
    pr_word = curr_word.get('pr', '')
    si_word = curr_word.get('si', 'N/A')

    st.markdown(f"""
        <div style="background-color: #f8f9fa; padding: 25px; border-radius: 15px; text-align: center; border-left: 10px solid #008C45; border-right: 10px solid #CD212A; margin-bottom: 20px;">
            <h1 style="color: #333; margin:0;">{it_word}</h1>
            <p style="color: #666;">({pr_word})</p>
        </div>
    """, unsafe_allow_html=True)

    if 'current_options' not in st.session_state:
        correct_ans = si_word
        wrong_candidates = [w.get('si', 'N/A') for w in st.session_state.word_pool if w.get('si') != correct_ans]
        wrong_options = random.sample(wrong_candidates, 3)
        all_opts = wrong_options + [correct_ans]
        random.shuffle(all_opts)
        st.session_state.current_options = all_opts

    # බටන්ස්
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
                    # වැරදුණු වචනය wrong_list එකට දාගන්නවා
                    if curr_word not in st.session_state.wrong_list:
                        st.session_state.wrong_list.append(curr_word)
                
                time.sleep(1.5)
                st.session_state.game_round += 1
                st.session_state.is_answered = False
                if 'current_options' in st.session_state: del st.session_state.current_options
                st.rerun()

# වටය අවසානය
else:
    # වැරදුණු වචන තිබේ නම් ඒවා නැවත කරවීම
    if st.session_state.wrong_list:
        st.warning(f"වටය අවසන්! ඔබේ ලකුණු: {st.session_state.score}/10. දැන් වැරදුණු වචන {len(st.session_state.wrong_list)} නැවත පුහුණු වෙමු.")
        
        if st.button("වැරදුණු වචන ටික ආයෙත් කරමු 🔄"):
            st.session_state.current_set = list(st.session_state.wrong_list)
            st.session_state.wrong_list = [] # List එක reset කරනවා ආයේ වැරදුණොත් දාගන්න
            st.session_state.game_round = 0
            st.session_state.is_retake_mode = True # දැන් පුහුණු වටය
            st.rerun()
            
    # ඔක්කොම හරි නම් අලුත් වටයකට යෑම
    else:
        st.balloons()
        st.success("නියමයි! ඔබ සියලුම වචන නිවැරදිව ඉගෙන ගත්තා. 🏆")
        if st.button("ඊළඟ අලුත් වචන 10 පටන් ගන්න ➡️"):
            st.session_state.game_round = 0
            st.session_state.score = 0
            st.session_state.wrong_list = []
            st.session_state.is_retake_mode = False
            st.session_state.current_set = random.sample(st.session_state.word_pool, 10)
            st.rerun()