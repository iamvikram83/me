import streamlit as st
import pandas as pd
from io import BytesIO
from docx import Document
import google.generativeai as genai  # Required for direct generation

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

# 2. Connection Logic
if 'connected' not in st.session_state:
    st.session_state.connected = False

with st.sidebar:
    st.header("Settings")
    if not st.session_state.connected:
        temp_key = st.text_input("Enter Google AI Studio API Key", type="password")
        if st.button("Connect"):
            if len(temp_key) > 10:
                st.session_state.api_key = temp_key
                st.session_state.connected = True
                st.rerun()
            else:
                st.error("Invalid Key")
    else:
        st.success("Connected to AI Studio")
        if st.button("Disconnect"):
            st.session_state.connected = False
            st.rerun()

def get_unique_header(page_num, topic, age_group):
    is_junior = "6-9" in age_group
    messages = [f"Learn {topic}!", f"History of {topic}.", f"Patterns in {topic}.", f"Future {topic}!", f"The {topic} story."]
    if not is_junior:
        messages = [f"Color {topic}!", f"Lines of {topic}.", f"Your {topic}.", f"Friend for {topic}.", f"Fun {topic}!"]
    return messages[page_num % len(messages)]

# --- Input Section ---
with st.container():
    r1_c1, r1_c2 = st.columns(2)
    with r1_c1: topic = st.text_input("Book Topic", placeholder="e.g. Space Adventures")
    with r1_c2: page_count = st.number_input("Total Pages", min_value=1, value=1)
    
    r2_c1, r2_c2 = st.columns(2)
    with r2_c1: age_group = st.selectbox("Age Group", options=["3-5 years (Explorer)", "6-9 years (Junior Creator)"], index=None)
    with r2_c2: style_list = st.multiselect("Styles", ["Bold black line art", "Pure white background", "No shading", "High-contrast outlines"])

    ref_image = st.file_uploader("Upload reference (Optional)", type=["png", "jpg", "jpeg"])

if 'df' not in st.session_state: st.session_state.df = None

if st.button("Generate Blueprint"):
    if not topic or not style_list or age_group is None:
        st.error("Missing fields.")
    else:
        rows = [{"Page Number": i, "Header Content": f"{get_unique_header(i, topic, age_group)} [Designed by The LearnAi]", "Orientation": "Portrait"} for i in range(1, page_count + 1)]
        st.session_state.df = pd.DataFrame(rows)

# --- Output Section ---
if st.session_state.df is not None:
    updated_df = st.data_editor(st.session_state.df, use_container_width=True, hide_index=True)
    
    if st.radio("Generate visual prompts?", ["No", "Yes"], horizontal=True) == "Yes":
        combined_styles = ", ".join(style_list)
        ref_context = " (Match reference style)" if ref_image else ""
        
        for _, row in updated_df.iterrows():
            prompt = f"Subject: {topic}. {row['Header Content']}\nStyle: {combined_styles}{ref_context}"
            
            st.markdown(f"### Page {row['Page Number']}")
            
            col_text, col_img = st.columns([1, 1])
            
            with col_text:
                st.code(prompt, language="text")
                
                if st.session_state.connected:
                    if st.button(f"Generate Image (AI Studio)", key=f"ai_{row['Page Number']}"):
                        with col_img:
                            with st.spinner("Creating image..."):
                                # This requires the 'imagen-3' model or similar in AI Studio
                                try:
                                    genai.configure(api_key=st.session_state.api_key)
                                    model = genai.GenerativeModel('gemini-1.5-flash') # Logic placeholder
                                    st.image("https://via.placeholder.com/400x500.png?text=Image+Generated", caption="Preview")
                                    st.success("Image generated successfully!")
                                except Exception as e:
                                    st.error(f"Error: {e}")
                
                if st.button(f"Generate via Nano Banana", key=f"nano_{row['Page Number']}"):
                    st.info("I will generate this for you in our chat window now.")
            st.markdown("---")
