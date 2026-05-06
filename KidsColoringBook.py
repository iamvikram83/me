import streamlit as st
import pandas as pd
import google.generativeai as genai

# --- 1. PAGE CONFIGURATION & STYLING ---
st.set_page_config(page_title="LearnAi Architect", layout="wide")

st.markdown("""
    <style>
    [data-testid="stAppViewContainer"] { background-color: #006994; }
    .stMarkdown, p, h1, h2, h3, span, label { color: white !important; }

    /* Remove the visibility toggle (eye icon) from the API Key field */
    button[aria-label="Show password"],
    button[aria-label="Hide password"] {
        display: none !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. SESSION STATE DEFAULTS ---
if 'step' not in st.session_state:
    st.session_state.step = 1
if 'connected' not in st.session_state:
    st.session_state.connected = False

# --- 3. STEPPER (Native Streamlit — no HTML, no leakage) ---
def render_stepper(current_step):
    steps = ["1 · Setup & Connection", "2 · Blueprint & Prompts", "3 · Done"]
    cols = st.columns(3)
    for i, (col, name) in enumerate(zip(cols, steps), 1):
        if i == current_step:
            col.success(f"🔵 **{name}**")
        elif i < current_step:
            col.success(f"✅ **{name}**")
        else:
            col.info(f"⬜ {name}")

# --- 4. APP HEADER ---
st.markdown("<h1 style='text-align: center;'>🎨 The LearnAi: Coloring Book Architect</h1>", unsafe_allow_html=True)

render_stepper(st.session_state.step)
st.markdown("---")

# --- 5. STEP 1: SETUP & API ---
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

        api_input = st.text_input("Enter API Key", type="password")

        if st.button("Connect"):
            if api_input:
                st.session_state.api_key = api_input
                st.session_state.connected = True
                st.success("✅ API Connected!")
            else:
                st.error("Please enter your API Key.")

        if st.session_state.connected:
            if st.button("Next Step: Create Blueprint ➡️"):
                if topic and age_group:
                    st.session_state.topic = topic
                    st.session_state.age_group = age_group
                    st.session_state.style_list = style_list
                    st.session_state.df = pd.DataFrame([
                        {"Page": i + 1, "Scene Description": "", "Prompt": ""}
                        for i in range(page_count)
                    ])
                    st.session_state.step = 2
                    st.rerun()
                else:
                    st.warning("⚠️ Please fill in Book Topic and Age Group before continuing.")

# --- 6. STEP 2: BLUEPRINT & PROMPTS ---
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

# --- 7. STEP 3: DONE ---
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
