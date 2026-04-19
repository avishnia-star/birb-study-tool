import streamlit as st
import os
import random

# --- PAGE CONFIG & WOODSY THEME ---
st.set_page_config(page_title="Birb Study Tool", page_icon="🌲", layout="centered")

st.markdown("""
    <style>
    /* Earthy background */
    .stApp { background-color: #f4f1e1; } 
    
    /* Dark wood text */
    h1, h2, h3, p, label { color: #3e2723 !important; } 
    
    /* Woodsy Buttons */
    .stButton>button {
        background-color: #6d4c41; 
        color: white;
        border-radius: 8px;
        border: none;
        transition: 0.3s;
        width: 100%;
        font-weight: bold;
    }
    .stButton>button:hover { background-color: #4e342e; color: white; }
    
    /* Answer Boxes */
    .answer-box {
        background-color: #ffffff;
        padding: 20px;
        border-radius: 10px;
        border-left: 8px solid #2e7d32; 
        margin-top: 20px;
        text-align: center;
        box-shadow: 2px 2px 10px rgba(0,0,0,0.1);
    }
    .correct { border-left: 8px solid #2e7d32; }
    .incorrect { border-left: 8px solid #c62828; }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] { gap: 20px; }
    .stTabs [data-baseweb="tab"] { height: 50px; white-space: pre-wrap; background-color: transparent; border-radius: 5px 5px 0 0; gap: 1px; padding-top: 10px; padding-bottom: 10px; }
    .stTabs [aria-selected="true"] { background-color: #e8e6d9; border-bottom: 3px solid #2e7d32; }
    </style>
""", unsafe_allow_html=True)

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

# --- STATE MANAGEMENT & FILTERING ---
if 'starred' not in st.session_state:
    st.session_state.starred = set()

# Sidebar Filter
with st.sidebar:
    st.header("⚙️ Study Settings")
    use_filter = st.checkbox("⭐ Study Starred Birds Only", value=False)
    
    if use_filter and len(st.session_state.starred) == 0:
        st.warning("You haven't starred any birds yet! Showing all birds for now.")
        
    st.write("---")
    st.write(f"**Starred Birds:** {len(st.session_state.starred)} / {len(st.session_state.birds)}")

# Determine Active Pool of Birds
if use_filter and len(st.session_state.starred) > 0:
    active_birds = [b for b in st.session_state.birds if b["name"] in st.session_state.starred]
else:
    active_birds = st.session_state.birds

# Detect if the pool changed (e.g., filter toggled) to safely rebuild the decks
current_pool_names = set([b["name"] for b in active_birds])
if 'last_pool_names' not in st.session_state or st.session_state.last_pool_names != current_pool_names:
    st.session_state.fc_order = list(range(len(active_birds)))
    random.shuffle(st.session_state.fc_order)
    st.session_state.fc_pos = 0
    st.session_state.fc_show_answer = False
    
    st.session_state.test_birds = random.sample(active_birds, len(active_birds))
    st.session_state.test_submitted = False
    for key in list(st.session_state.keys()):
        if key.startswith("test_ans_"):
            del st.session_state[key]
            
    st.session_state.last_pool_names = current_pool_names

# --- NAVIGATION FUNCTIONS ---
def next_flashcard():
    st.session_state.fc_pos = (st.session_state.fc_pos + 1) % len(active_birds)
    st.session_state.fc_show_answer = False

def prev_flashcard():
    st.session_state.fc_pos = (st.session_state.fc_pos - 1) % len(active_birds)
    st.session_state.fc_show_answer = False

def shuffle_flashcards():
    random.shuffle(st.session_state.fc_order)
    st.session_state.fc_pos = 0
    st.session_state.fc_show_answer = False

def retake_test():
    st.session_state.test_birds = random.sample(active_birds, len(active_birds))
    st.session_state.test_submitted = False
    for key in list(st.session_state.keys()):
        if key.startswith("test_ans_"):
            del st.session_state[key]


# --- UI LAYOUT ---
st.title("🌲 Birb Study Tool 🦉")

tab1, tab2 = st.tabs(["🃏 Flashcards", "📝 Test"])

# --- TAB 1: FLASHCARDS ---
with tab1:
    st.subheader("Study Mode")
    
    col_a, col_b = st.columns(2)
    show_pic = col_a.checkbox("Show Picture", value=True, key="fc_pic")
    show_aud = col_b.checkbox("Play Audio", value=True, key="fc_aud")
    
    st.write("---")
    
    # Grab current bird safely
    if st.session_state.fc_pos >= len(active_birds): 
        st.session_state.fc_pos = 0
        
    current_bird_idx = st.session_state.fc_order[st.session_state.fc_pos]
    current_bird = active_birds[current_bird_idx]
    is_starred = current_bird["name"] in st.session_state.starred
    
    # Header with Progress and Star Button
    c_prog, c_star = st.columns([3, 1])
    with c_prog:
        st.caption(f"Card {st.session_state.fc_pos + 1} of {len(active_birds)}")
    with c_star:
        star_btn = st.button("⭐ Unstar" if is_starred else "☆ Star", key="star_toggle")
        if star_btn:
            if is_starred:
                st.session_state.starred.remove(current_bird["name"])
            else:
                st.session_state.starred.add(current_bird["name"])
            st.rerun()
    
    # Media Display
    if show_pic:
        st.image(current_bird["image"], use_container_width=True)
    if show_aud:
        st.audio(current_bird["audio"])
    
    if not show_pic and not show_aud:
        st.warning("Select at least one option above to study!")

    st.write("---")
    
    # Navigation Buttons
    c1, c2, c3 = st.columns(3)
    with c1:
        if st.button("⬅️ Previous"):
            prev_flashcard()
            st.rerun()
    with c2:
        if st.button("Reveal Answer 🔍"):
            st.session_state.fc_show_answer = True
    with c3:
        if st.button("Next Bird ➡️"):
            next_flashcard()
            st.rerun()

    if st.session_state.fc_show_answer:
        st.markdown(f"<div class='answer-box'><h2>{current_bird['name']}</h2></div>", unsafe_allow_html=True)
        
    st.write("---")
    if st.button("🔀 Shuffle Deck", use_container_width=True):
        shuffle_flashcards()
        st.rerun()


# --- TAB 2: TEST ---
with tab2:
    st.subheader("Test")
    
    if not st.session_state.test_submitted:
        st.write(f"Test yourself on {len(active_birds)} birds.")
        
        c_pic, c_aud = st.columns(2)
        c_pic.checkbox("Show Pictures", value=True, key="t_pic")
        c_aud.checkbox("Play Audio", value=True, key="t_aud")
        
        st.write("---")
        
        with st.form("quiz_form"):
            for i, bird in enumerate(st.session_state.test_birds):
                st.markdown(f"**{i+1}.**")
                
                if st.session_state.t_pic: st.image(bird["image"], use_container_width=True)
                if st.session_state.t_aud: st.audio(bird["audio"])
                
                st.text_input("Name this bird:", key=f"test_ans_{i}")
                st.write("---")
                
            submit_test = st.form_submit_button("Submit & Grade Test")
            
            if submit_test:
                st.session_state.test_submitted = True
                st.rerun()

    else:
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
                
                if st.session_state.get("t_pic", True): st.image(bird["image"], use_container_width=True)
                if st.session_state.get("t_aud", True): st.audio(bird["audio"])
        
        st.write("---")
        st.subheader(f"Final Score: {score} / {len(active_birds)}")
        
        if st.button("Retake Test 🔄"):
            retake_test()
            st.rerun()