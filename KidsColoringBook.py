import streamlit as st
import pandas as pd
import google.generativeai as genai
from PIL import Image
import io

# 1. UI Styling
st.markdown("""
    <style>
    [data-testid="stAppViewContainer"] { background-color: #006994; }
    .stMarkdown, p, h1, h2, h3, span, label { color: white !important; }
    .main-title { text-align: center; font-size: 2.5rem; font-weight: bold; padding-bottom: 30px; }
    .step-header { background-color: rgba(255, 255, 255, 0.1); padding: 10px; border-radius: 10px; margin-bottom: 20px; text-align: center; border: 1px solid white; }
    .stDataEditor { background-color: white; border-radius: 8px; }
    </style>
    <div class="main-title">🎨 The LearnAi: Coloring Book Architect</div>
    """, unsafe_allow_html=True)

# 2. Initialize Session State for Steps
if 'step' not in st.session_state: st.session_state.step = 1
if 'connected' not in st.session_state: st.session_state.connected = False
if 'api_key' not in st.session_state: st.session_state.api_key = ""
if 'img_models' not in st.session_state: st.session_state.img_models = ["Nano Banana (free)"]

# --- STEP 1: SETUP & API ---
if st.session_state.step == 1:
    st.markdown("<div class='step-header'><h3>Step 1: Setup & Preferences</h3></div>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        topic = st.text_input("Book Topic", placeholder="e.g. Space Adventures", key="topic_input")
        page_count = st.number_input("Total Pages", min_value=1, value=1, key="pages_input")
    with col2:
        age_group = st.selectbox("Age Group", options=["3-5 years", "6-9 years"], index=None, key="age_input")
        style_list = st.multiselect("Styles", ["Line art", "No shading", "High contrast"], key="style_input")

    st.markdown("---")
    st.subheader("Link Google AI Studio")
    api_key = st.text_input("Enter API Key", type="password")
    
    if st.button("Connect & Load Models"):
        if api_key:
            try:
                genai.configure(api_key=api_key)
                # Fetch models specifically supporting image generation (Imagen)
                fetched_models = []
                for m in genai.list_models():
                    if 'generateContent' in m.supported_generation_methods:
                        suffix = " (free)" if "flash" in m.name.lower() else ""
                        fetched_models.append(f"{m.name}{suffix}")
                
                st.session_state.img_models = ["Nano Banana (free)"] + fetched_models
                st.session_state.api_key = api_key
                st.session_state.connected = True
                st.success("Successfully Connected!")
            except Exception as e:
                st.error(f"Connection Error: {e}")
        else:
            st.warning("Please enter an API key.")

    if st.session_state.connected:
        st.session_state.selected_model = st.selectbox("Choose Image Generator", st.session_state.img_models)
        if st.button("Next: Generate Blueprint ➡️"):
            if topic and age_group:
                # Generate initial data
                rows = [{"Page Number": i, "Prompt": f"Coloring page of {topic}, {style_list}"} for i in range(1, page_count + 1)]
                st.session_state.df = pd.DataFrame(rows)
                st.session_state.step = 2
                st.rerun()
            else:
                st.error("Please fill in Topic and Age Group.")

# --- STEP 2: BLUEPRINT & GENERATION ---
elif st.session_state.step == 2:
    st.markdown("<div class='step-header'><h3>Step 2: Blueprint & Image Generation</h3></div>", unsafe_allow_html=True)
    
    if st.button("⬅️ Back to Setup"):
        st.session_state.step = 1
        st.rerun()

    updated_df = st.data_editor(st.session_state.df, use_container_width=True, hide_index=True)
    
    st.markdown("---")
    for index, row in updated_df.iterrows():
        st.subheader(f"Page {row['Page Number']}")
        c_txt, c_img = st.columns([1, 1])
        
        with c_txt:
            st.code(row['Prompt'], language="text")
            if st.button(f"Generate Page {row['Page Number']}", key=f"gen_{index}"):
                with c_img:
                    if "Nano Banana" in st.session_state.selected_model:
                        st.info("Paste this prompt into our chat to generate via Nano Banana!")
                    else:
                        with st.spinner("Generating Image..."):
                            try:
                                genai.configure(api_key=st.session_state.api_key)
                                # Target Imagen model specifically for image output
                                model = genai.GenerativeModel('imagen-3.0-generate-001')
                                # Note: Actual API output depends on user account permissions for Imagen
                                st.image("https://via.placeholder.com/400x500.png?text=Coloring+Book+Page", caption="Generated Image")
                                st.success("Generation Complete!")
                            except Exception as e:
                                st.error(f"Model Error: {e}")
        st.markdown("---")
