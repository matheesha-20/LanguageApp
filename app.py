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

@st.cache_data(ttl=600)
def load_data(url):
    try:
        df = pd.read_csv(url)
        df.columns = df.columns.str.strip()
        return df.fillna('').to_dict('records')
    except Exception as e:
        st.error(f"දත්ත ලබාගැනීමේ දෝෂයක්: {e}")
        return []

# --- 2. SIDEBAR ---
with st.sidebar:
    st.header("⚙️ Settings")
    selected_lang_name = st.selectbox("භාෂාව තෝරන්න:", list(LANG_CONFIG.keys()))
    if 'last_lang' not in st.session_state or st.session_state.last_lang != selected_lang_name:
        st.session_state.last_lang = selected_lang_name
        for key in ['word_pool', 'game_round', 'score', 'wrong_list', 'current_set', 'is_answered', 'current_options', 'correct_ans']:
            if key in st.session_state: del st.session_state[key]
        st.rerun()

conf = LANG_CONFIG[selected_lang_name]
words = load_data(conf["url"])
if not words: st.stop()

# --- 3. SESSION INITIALIZE ---
if 'word_pool' not in st.session_state:
    st.session_state.word_pool = words
    st.session_state.current_set = random.sample(words, min(10, len(words)))
    st.session_state.game_round = 0
    st.session_state.score = 0
    st.session_state.wrong_list = []
    st.session_state.is_answered = False

# --- 4. GAME LOGIC ---
if st.session_state.game_round < len(st.session_state.current_set):
    curr_word = st.session_state.current_set[st.session_state.game_round]
    
    # පෙන්වන වචනය සහ නිවැරදි පිළිතුර Session එකේ එක පාරක් පමණක් save කරගනී
    if 'correct_ans' not in st.session_state:
        if "Synonyms" in selected_lang_name:
            st.session_state.display_word = curr_word.get(conf["key"], "N/A")
            adv_keys = [k for k in ["Advanced1", "Advanced2"] if curr_word.get(k)]
            ans_key = random.choice(adv_keys) if adv_keys else conf["key"]
            st.session_state.correct_ans = str(curr_word.get(ans_key, "N/A")).strip()
            st.session_state.sub_info = curr_word.get("Sinhala Meaning", "Select the Synonym")
        else:
            st.session_state.display_word = curr_word.get(conf["key"], "N/A")
            st.session_state.correct_ans = str(curr_word.get('si', "N/A")).strip()
            pr = curr_word.get('pr', "")
            st.session_state.sub_info = f"({pr})" if pr else ""

    # MCQ Options එක පාරක් පමණක් සාදා ගනී
    if 'current_options' not in st.session_state:
        wrong_candidates = set()
        correct = st.session_state.correct_ans
        
        if "Synonyms" in selected_lang_name:
            for w in st.session_state.word_pool:
                for k in ["Advanced1", "Advanced2", "ensyn"]:
                    val = str(w.get(k, '')).strip()
                    if val and val != correct: wrong_candidates.add(val)
        else:
            for w in st.session_state.word_pool:
                val = str(w.get('si', '')).strip()
                if val and val != correct: wrong_candidates.add(val)

        wrong_options = random.sample(list(wrong_candidates), min(3, len(wrong_candidates)))
        final_opts = list(set(wrong_options + [correct]))
        random.shuffle(final_opts)
        st.session_state.current_options = final_opts

    # UI
    st.title(f"{selected_lang_name}")
    st.subheader(f"ප්‍රශ්නය: {st.session_state.game_round + 1} / {len(st.session_state.current_set)}")
    
    color = "#007BFF" if "Synonyms" in selected_lang_name else "#008C45"
    st.markdown(f"""
        <div style="background-color: #f8f9fa; padding: 25px; border-radius: 15px; text-align: center; border-bottom: 10px solid {color}; margin-bottom: 20px;">
            <h1 style="color: #333; margin:0; font-size: 50px;">{st.session_state.display_word}</h1>
            <p style="color: #666; font-size: 20px;">{st.session_state.sub_info}</p>
        </div>
    """, unsafe_allow_html=True)

    cols = st.columns(2)
    for i, opt in enumerate(st.session_state.current_options):
        with cols[i % 2]:
            if st.button(opt, use_container_width=True, key=f"btn_{st.session_state.game_round}_{i}", disabled=st.session_state.is_answered):
                st.session_state.is_answered = True
                if opt == st.session_state.correct_ans:
                    st.success("නිවැරදියි! ✅")
                    st.session_state.score += 1
                else:
                    st.error(f"වැරදියි! ❌ පිළිතුර: {st.session_state.correct_ans}")
                    st.session_state.wrong_list.append(curr_word)
                
                time.sleep(1.2)
                # ඊළඟ ප්‍රශ්නයට යන්න කලින් session variables අයින් කරයි
                st.session_state.game_round += 1
                st.session_state.is_answered = False
                for k in ['current_options', 'correct_ans', 'display_word', 'sub_info']:
                    if k in st.session_state: del st.session_state[k]
                st.rerun()
else:
    st.success(f"වටය අවසන්! ලකුණු: {st.session_state.score}/{len(st.session_state.current_set)}")
    if st.button("නැවත ආරම්භ කරන්න 🔄"):
        for k in ['game_round', 'score', 'wrong_list', 'current_set']:
            if k in st.session_state: del st.session_state[k]
        st.rerun()