import streamlit as st
import os
import random

# --- PAGE CONFIG & COSTA RICA THEME ---
st.set_page_config(page_title="Bird Study Tool", page_icon="🦜", layout="centered")

st.markdown("""
    <style>
    .stApp { background-color: #eaf1e3; }
    h1, h2, h3, p, label { color: #1b4332 !important; }
    
    /* Buttons */
    .stButton>button {
        background-color: #bc6c25; 
        color: white;
        border-radius: 8px;
        border: none;
        transition: 0.3s;
        width: 100%;
        font-weight: bold;
    }
    .stButton>button:hover { background-color: #dda15e; color: #1b4332; }
    
    /* Answer Boxes */
    .answer-box {
        background-color: #ffffff;
        padding: 20px;
        border-radius: 10px;
        border-left: 8px solid #2d6a4f;
        margin-top: 20px;
        text-align: center;
        box-shadow: 2px 2px 10px rgba(0,0,0,0.1);
    }
    .correct { border-left: 8px solid #4CAF50; }
    .incorrect { border-left: 8px solid #F44336; }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] { gap: 20px; }
    .stTabs [data-baseweb="tab"] { height: 50px; white-space: pre-wrap; background-color: transparent; border-radius: 5px 5px 0 0; gap: 1px; padding-top: 10px; padding-bottom: 10px; }
    .stTabs [aria-selected="true"] { background-color: #d8e2dc; }
    </style>
""", unsafe_allow_html=True)

st.title("🌿 Rainforest Bird Study 🦜")

# --- DATA LOADING ---
@st.cache_data
def load_birds(media_folder="media"):
    birds = []
    if not os.path.exists(media_folder):
        return birds
    
    for filename in os.listdir(media_folder):
        if filename.endswith((".jpg", ".png", ".jpeg")):
            bird_name = os.path.splitext(filename)[0]
            
            audio_path = None
            for ext in ['.mp3', '.m4a', '.wav']:
                temp = os.path.join(media_folder, f"{bird_name}{ext}")
                if os.path.exists(temp):
                    audio_path = temp
                    break
            
            if audio_path:
                birds.append({
                    "name": bird_name.replace("_", " ").title(),
                    "image": os.path.join(media_folder, filename),
                    "audio": audio_path
                })
    return birds

if 'birds' not in st.session_state:
    st.session_state.birds = load_birds()

if not st.session_state.birds:
    st.error("No birds found in the 'media' folder. Check your files.")
    st.stop()

# --- STATE MANAGEMENT ---
if 'fc_index' not in st.session_state:
    st.session_state.fc_index = 0
if 'fc_show_answer' not in st.session_state:
    st.session_state.fc_show_answer = False

# Setup for the test tab
if 'test_birds' not in st.session_state:
    st.session_state.test_birds = random.sample(st.session_state.birds, len(st.session_state.birds))
if 'test_submitted' not in st.session_state:
    st.session_state.test_submitted = False

def next_flashcard():
    st.session_state.fc_index = random.randint(0, len(st.session_state.birds) - 1)
    st.session_state.fc_show_answer = False

def retake_test():
    st.session_state.test_birds = random.sample(st.session_state.birds, len(st.session_state.birds))
    st.session_state.test_submitted = False
    for key in list(st.session_state.keys()):
        if key.startswith("test_ans_"):
            del st.session_state[key]

# --- UI LAYOUT ---
tab1, tab2 = st.tabs(["🃏 Flashcards", "📝 Practice Test"])

# --- TAB 1: FLASHCARDS ---
with tab1:
    st.subheader("Study Mode")
    
    col_a, col_b = st.columns(2)
    show_pic = col_a.checkbox("Show Picture", value=True, key="fc_pic")
    show_aud = col_b.checkbox("Play Audio", value=True, key="fc_aud")
    
    st.write("---")
    
    current_bird = st.session_state.birds[st.session_state.fc_index]
    
    if show_pic:
        st.image(current_bird["image"], use_container_width=True)
    if show_aud:
        st.audio(current_bird["audio"])
    
    if not show_pic and not show_aud:
        st.warning("Select at least one option above to study!")

    st.write("---")
    
    c1, c2 = st.columns(2)
    with c1:
        if st.button("Reveal Answer 🔍"):
            st.session_state.fc_show_answer = True
    with c2:
        if st.button("Next Bird ➡️"):
            next_flashcard()
            st.rerun()

    if st.session_state.fc_show_answer:
        st.markdown(f"<div class='answer-box'><h2>{current_bird['name']}</h2></div>", unsafe_allow_html=True)


# --- TAB 2: PRACTICE TEST ---
with tab2:
    st.subheader("Quizlet Mode")
    
    if not st.session_state.test_submitted:
        st.write(f"Test yourself on all {len(st.session_state.birds)} birds.")
        
        c_pic, c_aud = st.columns(2)
        test_pic = c_pic.checkbox("Show Pictures", value=True, key="t_pic")
        test_aud = c_aud.checkbox("Play Audio", value=True, key="t_aud")
        
        st.write("---")
        
        with st.form("quiz_form"):
            for i, bird in enumerate(st.session_state.test_birds):
                st.markdown(f"**{i+1}.**")
                if test_pic: st.image(bird["image"], width=300)
                if test_aud: st.audio(bird["audio"])
                
                st.text_input("Name this bird:", key=f"test_ans_{i}")
                st.write("---")
                
            submit_test = st.form_submit_button("Submit & Grade Test")
            
            if submit_test:
                st.session_state.test_submitted = True
                st.rerun()

    else:
        # Grading Logic
        score = 0
        st.header("Test Results")
        
        for i, bird in enumerate(st.session_state.test_birds):
            user_answer = st.session_state.get(f"test_ans_{i}", "").strip().lower()
            correct_answer = bird['name'].lower()
            
            if user_answer == correct_answer:
                score += 1
                st.markdown(f"<div class='answer-box correct'><b>{i+1}. Correct!</b><br>It is a {bird['name']}</div>", unsafe_allow_html=True)
            else:
                st.markdown(f"<div class='answer-box incorrect'><b>{i+1}. Incorrect</b><br>You wrote: <i>{user_answer}</i><br>Correct answer: <b>{bird['name']}</b></div>", unsafe_allow_html=True)
                if test_pic: st.image(bird["image"], width=200)
                if test_aud: st.audio(bird["audio"])
        
        st.write("---")
        st.subheader(f"Final Score: {score} / {len(st.session_state.birds)}")
        
        if st.button("Retake Test 🔄"):
            retake_test()
            st.rerun()