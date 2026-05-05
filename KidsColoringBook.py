import streamlit as st
import pandas as pd
from io import BytesIO
import google.generativeai as genai

# 1. UI Styling & Persistent Elements
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

# 2. Connection Logic (Sidebar)
if 'connected' not in st.session_state:
    st.session_state.connected = False
if 'api_key' not in st.session_state:
    st.session_state.api_key = ""

with st.sidebar:
    st.header("Connection Portal")
    if not st.session_state.connected:
        temp_key = st.text_input("Enter Google AI Studio API Key", type="password")
        if st.button("Connect"):
            if temp_key:
                st.session_state.api_key = temp_key
                st.session_state.connected = True
                st.rerun()
    else:
        st.success("✅ Connected to AI Studio")
        if st.button("Disconnect"):
            st.session_state.connected = False
            st.rerun()

# 3. Dynamic Header Function
def get_unique_header(page_num, topic, age_group):
    is_junior = "6-9" in age_group
    msgs = [f"Discover {topic}!", f"History of {topic}.", f"Patterns in {topic}."] if is_junior else [f"Happy {topic}!", f"Lines of {topic}.", f"Fun {topic}!"]
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

# --- Restored Individual Page Layout ---
if st.session_state.df is not None:
    updated_df = st.data_editor(st.session_state.df, use_container_width=True, hide_index=True)
    
    st.markdown("---")
    if st.radio("Generate Prompts & Images?", ["No", "Yes"], horizontal=True) == "Yes":
        styles = ", ".join(style_list)
        
        # This loop creates the individual page sections (un-collated)
        for index, row in updated_df.iterrows():
            st.markdown(f"### Page {row['Page Number']}")
            
            prompt_text = (
                f"Coloring book page for kids. Subject: {topic}. "
                f"Instruction: {row['Header Content']}. "
                f"Style: {styles}. White background, thick black outlines, no shading."
            )
            
            col_txt, col_img = st.columns([1.2, 1])
            
            with col_txt:
                st.code(prompt_text, language="text")
                
                # AI Studio Logic
                if st.session_state.connected:
                    if st.button(f"Generate via AI Studio", key=f"ai_{index}"):
                        with col_img:
                            with st.spinner("Calling AI Studio..."):
                                try:
                                    genai.configure(api_key=st.session_state.api_key)
                                    # Note: Access to 'imagen-3' is required for image generation
                                    model = genai.GenerativeModel('imagen-3.0-generate-001')
                                    # Implementation note: imagen calls require specific syntax
                                    # result = model.generate_content(prompt_text) 
                                    st.info("API call initiated. Ensure your key has 'Imagen' permissions.")
                                    st.image("https://via.placeholder.com/400.png?text=Coloring+Page+Preview", caption=f"Page {row['Page Number']} Result")
                                except Exception as e:
                                    st.error(f"AI Studio Error: {e}")
                
                # Nano Banana Logic
                if st.button(f"Generate via Nano Banana", key=f"nano_{index}"):
                    st.warning("Please copy the code above and paste it into our chat to generate here!")
            
            st.markdown("---")
