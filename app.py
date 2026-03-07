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
        df.columns = df.columns.str.strip()import streamlit as st
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

st.set_page_config(page_title="Universal Learning Pro", page_icon="🌎", layout="centered")

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

# --- 3. SESSION INITIALIZATION FUNCTION ---
def reset_game_state(words_data):
    st.session_state.word_pool = words_data
    st.session_state.current_set = random.sample(words_data, min(10, len(words_data)))
    st.session_state.game_round = 0
    st.session_state.score = 0
    st.session_state.wrong_list = []
    st.session_state.is_answered = False
    # Clear question-specific keys
    for k in ['current_options', 'correct_ans', 'display_word', 'sub_info']:
        if k in st.session_state: 
            del st.session_state[k]

# --- 4. SIDEBAR & DATA FETCH ---
with st.sidebar:
    st.header("⚙️ Settings")
    selected_lang_name = st.selectbox("භාෂාව තෝරන්න:", list(LANG_CONFIG.keys()))
    
conf = LANG_CONFIG[selected_lang_name]
words = load_data(conf["url"])

if not words:
    st.warning("දත්ත හමු නොවීය. කරුණාකර Link පරීක්ෂා කරන්න.")
    st.stop()

# Trigger reset if language changes or if session is empty
if 'last_lang' not in st.session_state or st.session_state.last_lang != selected_lang_name:
    st.session_state.last_lang = selected_lang_name
    reset_game_state(words)
    st.rerun()

# --- 5. GAME LOGIC ---
if st.session_state.game_round < len(st.session_state.current_set):
    curr_word = st.session_state.current_set[st.session_state.game_round]
    
    # Generate Question & Options if not already set for this round
    if 'correct_ans' not in st.session_state:
        if "Synonyms" in selected_lang_name:
            st.session_state.display_word = curr_word.get("ensyn", "N/A")
            st.session_state.correct_ans = str(curr_word.get("syno", "N/A")).strip()
            st.session_state.sub_info = curr_word.get("sinhala meaning", "Select the Synonym")
            ans_col = "syno"
        else:
            st.session_state.display_word = curr_word.get(conf["key"], "N/A")
            st.session_state.correct_ans = str(curr_word.get('si', "N/A")).strip()
            pr = curr_word.get('pr', "")
            st.session_state.sub_info = f"({pr})" if pr else ""
            ans_col = "si"

        # Generate Distractors
        correct = st.session_state.correct_ans
        wrong_candidates = list(set([str(w.get(ans_col, '')).strip() for w in st.session_state.word_pool if str(w.get(ans_col, '')).strip() != correct]))
        
        wrong_options = random.sample(wrong_candidates, min(3, len(wrong_candidates)))
        final_opts = list(set(wrong_options + [correct]))
        random.shuffle(final_opts)
        st.session_state.current_options = final_opts

    # UI Rendering
    st.title(f"{selected_lang_name}")
    st.progress((st.session_state.game_round) / len(st.session_state.current_set))
    st.subheader(f"ප්‍රශ්නය: {st.session_state.game_round + 1} / {len(st.session_state.current_set)}")
    
    color = "#007BFF" if "Synonyms" in selected_lang_name else "#008C45"
    st.markdown(f"""
        <div style="background-color: #f8f9fa; padding: 25px; border-radius: 15px; text-align: center; border-bottom: 10px solid {color}; margin-bottom: 20px; box-shadow: 2px 2px 10px rgba(0,0,0,0.1);">
            <h1 style="color: #333; margin:0; font-size: 50px;">{st.session_state.display_word}</h1>
            <p style="color: #666; font-size: 20px;">{st.session_state.sub_info}</p>
        </div>
    """, unsafe_allow_html=True)

    # Buttons
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
                    st.session_state.wrong_list.append({
                        "word": st.session_state.display_word,
                        "correct": st.session_state.correct_ans
                    })
                
                time.sleep(1.2)
                st.session_state.game_round += 1
                st.session_state.is_answered = False
                # Cleanup round data
                for k in ['current_options', 'correct_ans', 'display_word', 'sub_info']:
                    if k in st.session_state: del st.session_state[k]
                st.rerun()

# --- 6. ROUND END ---
else:
    st.balloons()
    st.header("🎉 වටය අවසන්!")
    
    # Score card
    col1, col2 = st.columns(2)
    col1.metric("ලකුණු", f"{st.session_state.score} / {len(st.session_state.current_set)}")
    accuracy = (st.session_state.score / len(st.session_state.current_set)) * 100
    col2.metric("නිවැරදි ප්‍රතිශතය", f"{accuracy}%")

    # Review Mistakes
    if st.session_state.wrong_list:
        with st.expander("⚠️ වැරදුණු වචන නැවත බලන්න"):
            for item in st.session_state.wrong_list:
                st.write(f"**{item['word']}** ➡️ {item['correct']}")

    if st.button("අලුත් වචන 10ක් පටන් ගන්න ➡️", type="primary"):
        reset_game_state(words)
        st.rerun()
        return df.fillna('').to_dict('records')
    except Exception as e:
        st.error(f"දත්ත ලබාගැනීමේ දෝෂයක්: {e}")
        return []

# --- 3. SIDEBAR ---
with st.sidebar:
    st.header("⚙️ Settings")
    selected_lang_name = st.selectbox("භාෂාව තෝරන්න:", list(LANG_CONFIG.keys()))
    
    # භාෂාව මාරු කරන විට session එක reset කිරීම
    if 'last_lang' not in st.session_state or st.session_state.last_lang != selected_lang_name:
        st.session_state.last_lang = selected_lang_name
        for key in ['word_pool', 'game_round', 'score', 'wrong_list', 'current_set', 'is_answered', 'current_options', 'correct_ans', 'display_word', 'sub_info']:
            if key in st.session_state: del st.session_state[key]
        st.rerun()

conf = LANG_CONFIG[selected_lang_name]
words = load_data(conf["url"])

if not words:
    st.warning("දත්ත හමු නොවීය. කරුණාකර Link පරීක්ෂා කරන්න.")
    st.stop()

# --- 4. SESSION INITIALIZE ---
if 'word_pool' not in st.session_state:
    st.session_state.word_pool = words
    st.session_state.current_set = random.sample(words, min(10, len(words)))
    st.session_state.game_round = 0
    st.session_state.score = 0
    st.session_state.wrong_list = []
    st.session_state.is_answered = False

# --- 5. GAME LOGIC ---
if st.session_state.game_round < len(st.session_state.current_set):
    curr_word = st.session_state.current_set[st.session_state.game_round]
    
    # 1. ප්‍රශ්නය සහ නිවැරදි පිළිතුර තීරණය කිරීම (එක් වරක් පමණක්)
    if 'correct_ans' not in st.session_state:
        if "Synonyms" in selected_lang_name:
            # උඹේ අලුත් CSV format එකට අනුව: ensyn, syno, sinhala meaning
            st.session_state.display_word = curr_word.get("ensyn", "N/A")
            st.session_state.correct_ans = str(curr_word.get("syno", "N/A")).strip()
            st.session_state.sub_info = curr_word.get("sinhala meaning", "Select the Synonym")
            ans_col = "syno" # වැරදි පිළිතුරු ගන්නා column එක
        else:
            # සාමාන්‍ය භාෂා සඳහා (Italian, Japanese, English)
            st.session_state.display_word = curr_word.get(conf["key"], "N/A")
            st.session_state.correct_ans = str(curr_word.get('si', "N/A")).strip()
            pr = curr_word.get('pr', "")
            st.session_state.sub_info = f"({pr})" if pr else ""
            ans_col = "si"

        # 2. MCQ Options සෑදීම (එක් වරක් පමණක්)
        wrong_candidates = set()
        correct = st.session_state.correct_ans
        
        for w in st.session_state.word_pool:
            val = str(w.get(ans_col if "Synonyms" in selected_lang_name else "si", '')).strip()
            if val and val != correct:
                wrong_candidates.add(val)

        # අහඹු ලෙස වැරදි පිළිතුරු 3ක් තෝරාගනී
        wrong_options = random.sample(list(wrong_candidates), min(3, len(wrong_candidates)))
        final_opts = list(set(wrong_options + [correct]))
        random.shuffle(final_opts)
        st.session_state.current_options = final_opts

    # UI දර්ශනය
    st.title(f"{selected_lang_name}")
    st.subheader(f"ප්‍රශ්නය: {st.session_state.game_round + 1} / {len(st.session_state.current_set)}")
    
    color = "#007BFF" if "Synonyms" in selected_lang_name else "#008C45"
    st.markdown(f"""
        <div style="background-color: #f8f9fa; padding: 25px; border-radius: 15px; text-align: center; border-bottom: 10px solid {color}; margin-bottom: 20px; box-shadow: 2px 2px 10px rgba(0,0,0,0.1);">
            <h1 style="color: #333; margin:0; font-size: 50px;">{st.session_state.display_word}</h1>
            <p style="color: #666; font-size: 20px;">{st.session_state.sub_info}</p>
        </div>
    """, unsafe_allow_html=True)

    # බටන්ස් පෙන්වීම
    cols = st.columns(2)
    for i, opt in enumerate(st.session_state.current_options):
        with cols[i % 2]:
            if st.button(opt, use_container_width=True, key=f"btn_{st.session_state.game_round}_{i}_{opt}", disabled=st.session_state.is_answered):
                st.session_state.is_answered = True
                if opt == st.session_state.correct_ans:
                    st.success("නිවැරදියි! ✅")
                    st.session_state.score += 1
                else:
                    st.error(f"වැරදියි! ❌ පිළිතුර: {st.session_state.correct_ans}")
                    st.session_state.wrong_list.append(curr_word)
                
                time.sleep(1.2)
                # ඊළඟ ප්‍රශ්නයට යාමට පෙර session variables මකා දැමීම
                st.session_state.game_round += 1
                st.session_state.is_answered = False
                for k in ['current_options', 'correct_ans', 'display_word', 'sub_info']:
                    if k in st.session_state: del st.session_state[k]
                st.rerun()

# --- 6. ROUND END ---
else:
    st.balloons()
    st.success(f"වටය අවසන්! ඔබේ ලකුණු: {st.session_state.score} / {len(st.session_state.current_set)}")
    
    if st.button("අලුත් වචන 10ක් පටන් ගන්න ➡️"):
        for k in ['game_round', 'score', 'wrong_list', 'current_set', 'current_options', 'correct_ans']:
            if k in st.session_state: del st.session_state[k]
        st.rerun()