import streamlit as st
import pandas as pd
import google.generativeai as genai

# 1. UI Styling & Theme
st.markdown("""
    <style>
    [data-testid="stAppViewContainer"] { background-color: #006994; }
    .stMarkdown, p, h1, h2, h3, span, label { color: white !important; }
    .main-title { text-align: center; font-size: 2.5rem; font-weight: bold; padding-bottom: 30px; }
    .step-box { background-color: rgba(255, 255, 255, 0.1); padding: 15px; border-radius: 10px; border: 1px solid white; margin-bottom: 20px; }
    .stDataEditor { background-color: white; border-radius: 8px; }
    </style>
    <div class="main-title">🎨 The LearnAi: Coloring Book Architect</div>
    """, unsafe_allow_html=True)

# 2. Initialize State
if 'step' not in st.session_state: st.session_state.step = 1
if 'connected' not in st.session_state: st.session_state.connected = False
if 'api_key' not in st.session_state: st.session_state.api_key = ""
if 'img_models' not in st.session_state: st.session_state.img_models = ["Nano Banana (free)"]

# --- STEP 1: SETUP ---
if st.session_state.step == 1:
    st.markdown("<div class='step-box'><h3>Step 1: Setup & Configuration</h3></div>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        topic = st.text_input("Book Topic", placeholder="e.g. Space Adventures")
        page_count = st.number_input("Total Pages", min_value=1, value=1)
    with col2:
        age_group = st.selectbox("Age Group", options=["3-5 years (Explorer)", "6-9 years (Junior Creator)"], index=None)
        style_choice = st.multiselect("Selected Styles", ["Bold black line art", "Pure white background", "No shading", "High-contrast outlines"])

    st.markdown("---")
    st.subheader("Google AI Studio Connection")
    api_input = st.text_input("Enter Google AI Studio API Key", type="password")
    
    if st.button("Connect & Load Image Models"):
        if api_input:
            try:
                genai.configure(api_key=api_input)
                # Filtering for image generation/multimodal capabilities
                fetched_models = []
                for m in genai.list_models():
                    if 'generateContent' in m.supported_generation_methods:
                        # Append (free) to specific models known for free tier access
                        name = m.name.replace('models/', '')
                        label = f"{name} (free)" if "flash" in name.lower() else name
                        fetched_models.append(label)
                
                st.session_state.img_models = ["Nano Banana (free)"] + fetched_models
                st.session_state.api_key = api_input
                st.session_state.connected = True
                st.success("Connected successfully!")
            except Exception as e:
                st.error(f"Failed to load models: {e}")
        else:
            st.warning("Please enter an API key.")

    if st.session_state.connected:
        st.session_state.selected_model = st.selectbox("Select Generator", st.session_state.img_models)
        if st.button("Proceed to Step 2 ➡️"):
            if topic and age_group and style_choice:
                # Prepare data for Step 2
                rows = []
                for i in range(1, page_count + 1):
                    rows.append({
                        "Page Number": i,
                        "Header Content": f"Amazing facts about {topic}!",
                        "Orientation": "Portrait (8.5 x 11 inches)"
                    })
                st.session_state.df = pd.DataFrame(rows)
                st.session_state.topic = topic
                st.session_state.style_str = ", ".join(style_choice)
                st.session_state.step = 2
                st.rerun()
            else:
                st.error("Please complete all setup fields.")

# --- STEP 2: GENERATION ---
elif st.session_state.step == 2:
    st.markdown("<div class='step-box'><h3>Step 2: Blueprint & Final Prompts</h3></div>", unsafe_allow_html=True)
    
    if st.button("⬅️ Back to Step 1"):
        st.session_state.step = 1
        st.rerun()

    # Allow user to edit headers/orientation
    updated_df = st.data_editor(st.session_state.df, use_container_width=True, hide_index=True)
    
    st.markdown("---")
    for index, row in updated_df.iterrows():
        st.markdown(f"#### Configuration for Page {row['Page Number']}")
        
        # Formatting the final prompt as requested
        final_visual_prompt = (
            f"The Content for Page {row['Page Number']} :\n\n"
            f"Create a high-resolution, printable children's coloring page in {row['Orientation']}. "
            f"Ensure high-quality line art and correct text placement for printing.\n\n"
            f"Subject: Clean black and white line art of {st.session_state.topic}. Wide, clear lines, no shading.\n\n"
            f"Top Header: {row['Header Content']}\n\n"
            f"Footer Branding: 'Designed by The LearnAi'.\n\n"
            f"Page Number: {row['Page Number']}\n\n"
            f"Style: {st.session_state.style_str}"
        )
        
        col_txt, col_img = st.columns([1, 1])
        
        with col_txt:
            st.code(final_visual_prompt, language="text")
            
            if st.button(f"Generate Page {row['Page Number']}", key=f"btn_{index}"):
                with col_img:
                    if "Nano Banana" in st.session_state.selected_model:
                        st.info("Paste the prompt above into our chat. I will generate it for you!")
                    else:
                        with st.spinner("Generating via AI Studio..."):
                            # This is where the direct API call to the selected model would happen
                            # Note: Actual image generation depends on key permissions for 'imagen'
                            st.image("https://via.placeholder.com/400x500.png?text=Image+Generated", caption=f"Page {row['Page Number']}")
        st.markdown("---")
