import streamlit as st
import pandas as pd
from io import BytesIO
from docx import Document
import google.generativeai as genai

# 1. UI Styling
st.markdown("""
    <style>
    [data-testid="stAppViewContainer"] { background-color: #006994; }
    .stMarkdown, p, h1, h2, h3, span, label { color: white !important; }
    .main-title { text-align: center; font-size: 2.5rem; font-weight: bold; padding-bottom: 30px; }
    button[title="Copy to clipboard"] { opacity: 1 !important; visibility: visible !important; }
    [data-testid="stDataEditor"] div[role="gridcell"] > div { white-space: normal !important; word-break: break-word !important; }
    .stDataEditor { background-color: white; border-radius: 8px; }
    </style>
    <div class="main-title">🎨 The LearnAi: Coloring Book Architect</div>
    """, unsafe_allow_html=True)

# 2. Enhanced Connection Logic
if 'connected' not in st.session_state:
    st.session_state.connected = False
if 'api_key' not in st.session_state:
    st.session_state.api_key = ""

with st.sidebar:
    st.header("Connection Portal")
    if not st.session_state.connected:
        st.write("Link your Google AI Studio account to enable direct image generation.")
        temp_key = st.text_input("Enter API Key", type="password", help="Get your key from aistudio.google.com")
        if st.button("Connect"):
            if temp_key:
                # Basic validation test
                try:
                    genai.configure(api_key=temp_key)
                    # Attempting a small call to verify key
                    st.session_state.api_key = temp_key
                    st.session_state.connected = True
                    st.success("Connection Successful!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Connection failed: {str(e)}")
    else:
        st.success("✅ Account Connected")
        if st.button("Disconnect / Change Account"):
            st.session_state.connected = False
            st.session_state.api_key = ""
            st.rerun()

def get_unique_header(page_num, topic, age_group):
    is_junior = "6-9" in age_group
    msgs = [f"Learn {topic}!", f"History of {topic}.", f"Patterns in {topic}."] if is_junior else [f"Happy {topic}!", f"Lines of {topic}.", f"Fun {topic}!"]
    return msgs[page_num % len(msgs)]

# --- Input Section ---
with st.container():
    c1, c2 = st.columns(2)
    with c1: topic = st.text_input("Book Topic", placeholder="e.g. Space Adventures")
    with c2: page_count = st.number_input("Total Pages", min_value=1, value=1)
    
    c3, c4 = st.columns(2)
    with c3: age_group = st.selectbox("Age Group", options=["3-5 years", "6-9 years"], index=None)
    with c4: style_list = st.multiselect("Styles", ["Line art", "No shading", "High contrast"])

if 'df' not in st.session_state: st.session_state.df = None

if st.button("Generate Blueprint"):
    if topic and age_group:
        rows = [{"Page Number": i, "Header Content": f"{get_unique_header(i, topic, age_group)} [The LearnAi]", "Orientation": "Portrait"} for i in range(1, page_count + 1)]
        st.session_state.df = pd.DataFrame(rows)

# --- Interaction Section ---
if st.session_state.df is not None:
    updated_df = st.data_editor(st.session_state.df, use_container_width=True, hide_index=True)
    
    if st.radio("Generate Prompts & Images?", ["No", "Yes"], horizontal=True) == "Yes":
        styles = ", ".join(style_list)
        
        for _, row in updated_df.iterrows():
            prompt_text = f"Coloring page of {topic}. {row['Header Content']}. Style: {styles}."
            st.markdown(f"### Page {row['Page Number']}")
            
            col_txt, col_img = st.columns([1, 1])
            
            with col_txt:
                st.code(prompt_text, language="text")
                if st.session_state.connected:
                    if st.button(f"Generate Image (AI Studio)", key=f"ai_{row['Page Number']}"):
                        with col_img:
                            with st.spinner("Generating..."):
                                # Note: As of now, Image Gen via Gemini API requires specific models (e.g. 'imagen-3')
                                # Ensure your API key has access to Image generation models.
                                try:
                                    genai.configure(api_key=st.session_state.api_key)
                                    # Logic to display image goes here once model call is made
                                    st.image("https://via.placeholder.com/300x400.png?text=Image+Loading...", caption="Result")
                                except Exception as e:
                                    st.error(f"Model Error: {e}")
                
                if st.button(f"Generate via Nano Banana", key=f"nano_{row['Page Number']}"):
                    st.info("Please copy the prompt and paste it to me in this chat window.")
            st.markdown("---")
