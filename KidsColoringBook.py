import streamlit as st
import pandas as pd
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

# 2. Session State Initialization
if 'connected' not in st.session_state: st.session_state.connected = False
if 'api_key' not in st.session_state: st.session_state.api_key = ""
if 'available_models' not in st.session_state: st.session_state.available_models = []

# 3. Sidebar: Google AI Studio Connection
with st.sidebar:
    st.header("Settings")
    if not st.session_state.connected:
        st.subheader("Link Google AI Studio")
        temp_key = st.text_input("Enter API Key", type="password")
        if st.button("Connect"):
            if temp_key:
                try:
                    genai.configure(api_key=temp_key)
                    # Fetch models that support image generation or vision
                    models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
                    st.session_state.available_models = models
                    st.session_state.api_key = temp_key
                    st.session_state.connected = True
                    st.success("Connected!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Connection failed: {e}")
    else:
        st.success("Connected to AI Studio")
        st.session_state.selected_model = st.selectbox("Select Image Model", st.session_state.available_models)
        if st.button("Disconnect"):
            st.session_state.connected = False
            st.rerun()

# --- Core Logic Functions ---
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

# --- Sequential Gated Logic ---
if st.session_state.df is not None:
    updated_df = st.data_editor(st.session_state.df, use_container_width=True, hide_index=True)
    
    st.markdown("---")
    # Gate 1: Visual Prompts
    gen_prompts = st.radio("Would you like to generate visual prompts?", ["No", "Yes"], horizontal=True)
    
    if gen_prompts == "Yes":
        # Gate 2: AI Studio Choice
        use_ai_studio = st.radio("Would you like to generate image on Google AI Studio?", ["No", "Yes"], horizontal=True)
        
        if use_ai_studio == "Yes" and not st.session_state.connected:
            st.warning("Please link your Google AI Studio API in the sidebar to continue.")
        
        styles = ", ".join(style_list)
        for index, row in updated_df.iterrows():
            st.markdown(f"### Page {row['Page Number']}")
            prompt_text = f"Coloring page: {topic}. {row['Header Content']}. Style: {styles}."
            
            col_txt, col_img = st.columns([1.2, 1])
            with col_txt:
                st.code(prompt_text, language="text")
                
                # Logic for AI Studio
                if use_ai_studio == "Yes" and st.session_state.connected:
                    if st.button(f"Generate via {st.session_state.selected_model}", key=f"ai_{index}"):
                        with col_img:
                            with st.spinner("Generating..."):
                                try:
                                    genai.configure(api_key=st.session_state.api_key)
                                    # Note: Specific image models (like Imagen) may require different API calls
                                    # This shows a placeholder image next to the text
                                    st.image("https://via.placeholder.com/300x400.png?text=Generated+Image", caption=f"Result Page {row['Page Number']}")
                                except Exception as e:
                                    st.error(f"Generation Error: {e}")
                
                # Nano Banana remains as a peer-to-peer instruction
                if st.button(f"Generate via Nano Banana", key=f"nano_{index}"):
                    st.info("Please copy the prompt and paste it to me here in this chat window!")
            st.markdown("---")
