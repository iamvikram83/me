import streamlit as st
import pandas as pd
import google.generativeai as genai

# --- 1. PAGE CONFIGURATION & STYLING ---
st.set_page_config(page_title="LearnAi Architect", layout="wide")

st.markdown("""
    <style>
    [data-testid="stAppViewContainer"] { background-color: #006994; }
    .stMarkdown, p, h1, h2, h3, span, label { color: white !important; }
    
    /* Stepper UI CSS */
    .stepper-wrapper { display: flex; justify-content: space-between; margin: 40px 0; position: relative; width: 100%; }
    .stepper-item { position: relative; display: flex; flex-direction: column; align-items: center; flex: 1; }
    .stepper-item::before { position: absolute; content: ""; border-bottom: 2px solid #ccc; width: 100%; top: 20px; left: -50%; z-index: 0; }
    .stepper-item:first-child::before { content: none; }
    .step-counter { position: relative; z-index: 1; display: flex; justify-content: center; align-items: center; width: 40px; height: 40px; border-radius: 50%; background: #ccc; margin-bottom: 6px; color: black; font-weight: bold; }
    .active .step-counter { background-color: #3f51b5; color: white; }
    .completed .step-counter { background-color: #4caf50; color: white; }
    .step-name { font-size: 14px; color: white; font-weight: 500; }

    /* Hide the eye icon (visibility toggle) on API key field */
    button[aria-label="Show password"], 
    button[aria-label="Hide password"] { 
        display: none !important; 
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. LOGIC HELPERS ---
if 'step' not in st.session_state: st.session_state.step = 1
if 'connected' not in st.session_state: st.session_state.connected = False

def render_stepper(current_step):
    """Renders the HTML stepper. Note: No 'return' used to avoid leakage."""
    steps = ["Setup & Connection", "Blueprint & Prompts", "Done"]
    html = '<div class="stepper-wrapper">'
    for i, name in enumerate(steps, 1):
        status = "active" if i == current_step else ("completed" if i < current_step else "")
        html += f'''
            <div class="stepper-item {status}">
                <div class="step-counter">{i}</div>
                <div class="step-name">{name}</div>
            </div>
        '''
    html += '</div>'
    st.markdown(html, unsafe_allow_html=True)

# --- 3. APP HEADER ---
st.markdown("<h1 style='text-align: center;'>🎨 The LearnAi: Coloring Book Architect</h1>", unsafe_allow_html=True)

# We call the function here. Because it returns None, nothing leaks to the screen.
render_stepper(st.session_state.step)

# --- 4. STEP 1: SETUP & API ---
if st.session_state.step == 1:
    with st.container():
        c1, c2 = st.columns(2)
        with c1:
            topic = st.text_input("Book Topic", placeholder="e.g. Manners and Kindness")
            page_count = st.number_input("Total Pages", min_value=1, value=1)
        with c2:
            age_group = st.selectbox("Age Group", options=["3-5 years", "6-9 years"], index=None)
            style_list = st.multiselect("Selected Styles", ["Bold black line art", "Pure white background", "No shading"])

        st.markdown("---")
        st.subheader("Link Google AI Studio")
        
        # type="password" is kept for safety, but CSS hides the eye icon toggle
        api_input = st.text_input("Enter API Key", type="password")
        
        if st.button("Connect"):
            if api_input:
                st.session_state.connected = True
                st.success("API Key Linked!")
            else:
                st.error("Please enter a key.")

        if st.session_state.connected:
            if st.button("Next Step: Create Blueprint ➡️"):
                if topic and age_group:
                    st.session_state.df = pd.DataFrame([{"Page": i+1} for i in range(page_count)])
                    st.session_state.topic = topic
                    st.session_state.step = 2
                    st.rerun()

# --- 5. STEP 2: BLUEPRINT & PROMPTS ---
elif st.session_state.step == 2:
    if st.button("⬅️ Back"):
        st.session_state.step = 1
        st.rerun()

    st.subheader("Finalize your Page Content")
    st.data_editor(st.session_state.df, use_container_width=True)
    
    if st.button("Finish Project"):
        st.session_state.step = 3
        st.rerun()

# --- 6. STEP 3: DONE ---
elif st.session_state.step == 3:
    st.balloons()
    st.success("Project Completed!")
    if st.button("Start New Project"):
        st.session_state.step = 1
        st.rerun()
