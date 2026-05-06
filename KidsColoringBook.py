import streamlit as st
import pandas as pd
import google.generativeai as genai

# --- 1. PAGE CONFIGURATION & STYLING ---
st.set_page_config(page_title="LearnAi Architect", layout="wide")

st.markdown("""
    <style>
    [data-testid="stAppViewContainer"] { background-color: #006994; }
    .stMarkdown, p, h1, h2, h3, span, label { color: white !important; }
    
    /* Stepper UI Design */
    .stepper-wrapper { display: flex; justify-content: space-between; margin: 40px 0; position: relative; width: 100%; }
    .stepper-item { position: relative; display: flex; flex-direction: column; align-items: center; flex: 1; }
    .stepper-item::before { position: absolute; content: ""; border-bottom: 2px solid #ccc; width: 100%; top: 20px; left: -50%; z-index: 0; }
    .stepper-item:first-child::before { content: none; }
    .completed::before { border-bottom-color: #4caf50 !important; }
    .step-counter { position: relative; z-index: 1; display: flex; justify-content: center; align-items: center; width: 40px; height: 40px; border-radius: 50%; background: #ccc; margin-bottom: 6px; color: black; font-weight: bold; }
    .active .step-counter { background-color: #3f51b5; color: white; }
    .completed .step-counter { background-color: #4caf50; color: white; }
    .step-name { font-size: 14px; color: white; font-weight: 500; }

    /* Remove the visibility toggle (eye icon) from the API Key field */
    button[aria-label="Show password"], 
    button[aria-label="Hide password"] { 
        display: none !important; 
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. LOGIC & DATA HELPERS ---
if 'step' not in st.session_state: st.session_state.step = 1
if 'connected' not in st.session_state: st.session_state.connected = False

def render_stepper(current_step):
    """Renders the step progress bar. Always returns None to prevent HTML leakage."""
    steps = ["Setup & Connection", "Blueprint & Prompts", "Done"]
    html_parts = []
    html_parts.append('<div class="stepper-wrapper">')
    for i, name in enumerate(steps, 1):
        if i == current_step:
            status = "active"
        elif i < current_step:
            status = "completed"
        else:
            status = ""
        html_parts.append(f'''
            <div class="stepper-item {status}">
                <div class="step-counter">{i}</div>
                <div class="step-name">{name}</div>
            </div>
        ''')
    html_parts.append('</div>')
    html = "".join(html_parts)
    st.markdown(html, unsafe_allow_html=True)
    return None  # Explicit None prevents Streamlit capturing any return value

# --- 3. APP HEADER ---
st.markdown("<h1 style='text-align: center;'>🎨 The LearnAi: Coloring Book Architect</h1>", unsafe_allow_html=True)

# Call the function directly — never assign to a variable
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
            style_list = st.multiselect("Selected Styles", ["Bold black lines", "No shading", "White background"])

        st.markdown("---")
        st.subheader("Link Google AI Studio")

        # 'type="password"' masks input, CSS hides the eye icon
        api_input = st.text_input("Enter API Key", type="password")

        if st.button("Connect"):
            if api_input:
                st.session_state.api_key = api_input
                st.session_state.connected = True
                st.success("API Connected!")
            else:
                st.error("Please enter your API Key.")

        if st.session_state.connected:
            if st.button("Next Step: Create Blueprint ➡️"):
                if topic and age_group:
                    st.session_state.topic = topic
                    st.session_state.age_group = age_group
                    st.session_state.style_list = style_list
                    st.session_state.df = pd.DataFrame([{"Page": i + 1, "Scene Description": "", "Prompt": ""} for i in range(page_count)])
                    st.session_state.step = 2
                    st.rerun()
                else:
                    st.warning("Please fill in Book Topic and Age Group before continuing.")

# --- 5. STEP 2: BLUEPRINT & PROMPTS ---
elif st.session_state.step == 2:
    if st.button("⬅️ Back"):
        st.session_state.step = 1
        st.rerun()

    st.subheader("Finalize your Page Content")
    st.markdown(f"**Topic:** {st.session_state.get('topic', '')} &nbsp;|&nbsp; **Age Group:** {st.session_state.get('age_group', '')}")

    edited_df = st.data_editor(
        st.session_state.df,
        use_container_width=True,
        hide_index=True,
        num_rows="fixed"
    )
    st.session_state.df = edited_df

    if st.button("Finish Project ✅"):
        st.session_state.step = 3
        st.rerun()

# --- 6. STEP 3: DONE ---
elif st.session_state.step == 3:
    st.balloons()
    st.success("🎉 Project Completed! Your coloring book blueprint is ready.")

    st.subheader("Your Blueprint Summary")
    st.dataframe(st.session_state.df, use_container_width=True, hide_index=True)

    if st.button("🔄 Start New Project"):
        for key in ['step', 'connected', 'topic', 'age_group', 'style_list', 'df', 'api_key']:
            if key in st.session_state:
                del st.session_state[key]
        st.rerun()
