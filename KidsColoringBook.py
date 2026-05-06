import streamlit as st
import pandas as pd
import google.generativeai as genai
import io

# --- 1. PAGE CONFIGURATION & STYLING ---
st.set_page_config(page_title="LearnAi Architect", layout="wide")

st.markdown("""
    <style>
    [data-testid="stAppViewContainer"] { background-color: #006994; }
    .stMarkdown, p, h1, h2, h3, span, label { color: white !important; }
    button[aria-label="Show password"], button[aria-label="Hide password"] { display: none !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. SESSION STATE DEFAULTS ---
if 'step' not in st.session_state: st.session_state.step = 1
if 'connected' not in st.session_state: st.session_state.connected = False
if 'df' not in st.session_state: st.session_state.df = pd.DataFrame()

# --- 3. STEPPER (Native Streamlit) ---
def render_stepper(current_step):
    steps = ["1 · Setup & Connection", "2 · Blueprint & Prompts", "3 · Done"]
    cols = st.columns(3)
    for i, (col, name) in enumerate(zip(cols, steps), 1):
        if i == current_step: col.success(f"🔵 **{name}**")
        elif i < current_step: col.success(f"✅ **{name}**")
        else: col.info(f"⬜ {name}")

# --- 4. APP HEADER ---
st.markdown("<h1 style='text-align: center;'>🎨 The LearnAi: Coloring Book Architect</h1>", unsafe_allow_html=True)
render_stepper(st.session_state.step)
st.markdown("---")

# --- 5. STEP 1: SETUP & API ---
if st.session_state.step == 1:
    with st.container():
        c1, c2 = st.columns(2)
        with c1:
            topic = st.text_input("Book Topic", value=st.session_state.get('topic', ''), placeholder="e.g. Manners and Kindness")
            page_count = st.number_input("Total Pages", min_value=1, value=st.session_state.get('page_count', 1))
        with c2:
            age_group = st.selectbox("Age Group", options=["3-5 years", "6-9 years"], index=0 if 'age_group' in st.session_state else None)
            gen_model = st.selectbox("Image Generation Model", options=["Imagen 3", "DALL-E 3", "Midjourney Style v6"])
            style_list = st.multiselect("Selected Styles", ["Bold black lines", "No shading", "White background"], default=["Bold black lines", "No shading", "White background"])

        st.markdown("---")
        st.subheader("Link Google AI Studio")

        if not st.session_state.connected:
            api_input = st.text_input("Enter API Key", type="password")
            if st.button("Connect"):
                if api_input:
                    st.session_state.api_key = api_input
                    st.session_state.connected = True
                    st.rerun()
        else:
            st.success("✅ API Connected!")
            if st.button("Disconnect API"):
                st.session_state.connected = False
                st.session_state.api_key = None
                st.rerun()

        if st.session_state.connected:
            if st.button("Next Step: Create Blueprint ➡️"):
                st.session_state.topic = topic
                st.session_state.age_group = age_group
                st.session_state.page_count = page_count
                st.session_state.styles = ", ".join(style_list)
                st.session_state.gen_model = gen_model
                
                # Initialize DataFrame if empty
                st.session_state.df = pd.DataFrame([
                    {"Page": i + 1, "Scene Description": f"Scene for {topic}", "Prompt": ""}
                    for i in range(page_count)
                ])
                st.session_state.step = 2
                st.rerun()

# --- 6. STEP 2: BLUEPRINT & PROMPTS ---
elif st.session_state.step == 2:
    if st.button("⬅️ Back"):
        st.session_state.step = 1
        st.rerun()

    st.subheader("Finalize your Page Content")
    st.info(f"**Target Model:** {st.session_state.gen_model} | **Topic:** {st.session_state.topic}")

    # The data_editor needs the key to keep sync
    edited_df = st.data_editor(st.session_state.df, use_container_width=True, hide_index=True)
    st.session_state.df = edited_df

    st.markdown("---")
    
    # Download logic
    csv = st.session_state.df.to_csv(index=False).encode('utf-8')
    st.download_button("📥 Download All Page Prompts (CSV)", data=csv, file_name="coloring_book_blueprint.csv", mime='text/csv')

    st.subheader("Visual Prompt Summary & Generation")
    
    for index, row in st.session_state.df.iterrows():
        # Update prompt logic
        full_prompt = (f"Coloring book page for {st.session_state.age_group} kids. "
                       f"Subject: {row['Scene Description']}. Style: {st.session_state.styles}. "
                       f"Optimized for {st.session_state.gen_model}.")
        st.session_state.df.at[index, 'Prompt'] = full_prompt
        
        with st.expander(f"Page {row['Page']} Tools"):
            st.code(full_prompt, language="text")
            if st.button(f"Generate Image for Page {row['Page']}", key=f"gen_{index}"):
                st.warning(f"Generating image for Page {row['Page']} using {st.session_state.gen_model}... (API Logic Placeholder)")
                # Here you would call genai or your image model API

    if st.button("Finish Project ✅"):
        st.session_state.step = 3
        st.rerun()

# --- 7. STEP 3: DONE ---
elif st.session_state.step == 3:
    st.balloons()
    st.success("🎉 Project Completed!")
    st.dataframe(st.session_state.df, use_container_width=True, hide_index=True)
    if st.button("🔄 Start New Project"):
        for key in ['step', 'connected', 'topic', 'df', 'api_key']: st.session_state.pop(key, None)
        st.rerun()
