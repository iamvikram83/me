import streamlit as st
import pandas as pd
import google.generativeai as genai

# 1. Custom CSS for the Horizontal Stepper
st.markdown("""
    <style>
    [data-testid="stAppViewContainer"] { background-color: #006994; }
    .stMarkdown, p, h1, h2, h3, span, label { color: white !important; }
    
    /* Stepper Container */
    .stepper-wrapper { display: flex; justify-content: space-between; margin-bottom: 40px; position: relative; }
    .stepper-item { position: relative; display: flex; flex-direction: column; align-items: center; flex: 1; }
    .stepper-item::before { position: absolute; content: ""; border-bottom: 2px solid #ccc; width: 100%; top: 20px; left: -50%; z-index: 0; }
    .stepper-item:first-child::before { content: none; }
    .step-counter { position: relative; z-index: 1; display: flex; justify-content: center; align-items: center; width: 40px; height: 40px; border-radius: 50%; background: #ccc; margin-bottom: 6px; color: black; font-weight: bold; }
    .active .step-counter { background-color: #3f51b5; color: white; }
    .completed .step-counter { background-color: #4caf50; color: white; }
    .step-name { font-size: 14px; color: white; }
    </style>
    """, unsafe_allow_html=True)

# 2. Session State Management
if 'step' not in st.session_state: st.session_state.step = 1
if 'connected' not in st.session_state: st.session_state.connected = False
if 'img_models' not in st.session_state: st.session_state.img_models = ["Nano Banana (free)"]

def render_stepper(current_step):
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

# --- APP LAYOUT ---
st.markdown("<h1 style='text-align: center;'>🎨 The LearnAi Architect</h1>", unsafe_allow_html=True)
render_stepper(st.session_state.step)

# --- STEP 1: SETUP & CONNECTION ---
if st.session_state.step == 1:
    with st.container():
        c1, c2 = st.columns(2)
        with c1:
            topic = st.text_input("Book Topic", placeholder="e.g. Health & Manners")
            page_count = st.number_input("Total Pages", min_value=1, value=1)
        with c2:
            age_group = st.selectbox("Age Group", options=["3-5 years", "6-9 years"], index=None)
            style_list = st.multiselect("Styles", ["Bold black line art", "Pure white background", "No shading", "High-contrast"])

        st.markdown("---")
        api_key = st.text_input("Google AI Studio API Key", type="password")
        
        if st.button("Connect & Load Models"):
            if api_key:
                try:
                    genai.configure(api_key=api_key)
                    models = []
                    for m in genai.list_models():
                        if 'generateContent' in m.supported_generation_methods:
                            # Filter and label models
                            name = m.name.replace('models/', '')
                            if "vision" in name.lower() or "flash" in name.lower() or "imagen" in name.lower():
                                label = f"{name} (free)" if "flash" in name.lower() else name
                                models.append(label)
                    
                    st.session_state.img_models = ["Nano Banana (free)"] + models
                    st.session_state.api_key = api_key
                    st.session_state.connected = True
                    st.success("Connected!")
                except Exception as e:
                    st.error(f"Error: {e}")

        if st.session_state.connected:
            st.session_state.selected_model = st.selectbox("Choose Model", st.session_state.img_models)
            if st.button("Next Step ➡️"):
                if topic and age_group:
                    rows = [{"Page Number": i, "Header": "Default Header", "Orientation": "Portrait (8.5 x 11 inches)"} for i in range(1, page_count + 1)]
                    st.session_state.df = pd.DataFrame(rows)
                    st.session_state.topic = topic
                    st.session_state.styles = ", ".join(style_list)
                    st.session_state.step = 2
                    st.rerun()

# --- STEP 2: BLUEPRINT & GENERATION ---
elif st.session_state.step == 2:
    if st.button("⬅️ Back"):
        st.session_state.step = 1
        st.rerun()

    updated_df = st.data_editor(st.session_state.df, use_container_width=True, hide_index=True)
    
    st.markdown("---")
    for index, row in updated_df.iterrows():
        # Formatting the Final Visual Prompt
        prompt_block = (
            f"The Content for Page {row['Page Number']} :\n\n"
            f"Create a high-resolution, printable children's coloring page in {row['Orientation']}. "
            f"Ensure high-quality line art and correct text placement for printing.\n\n"
            f"Subject: {st.session_state.topic}. Wide, clear lines, no shading.\n\n"
            f"Top Header: {row['Header']}\n\n"
            f"Footer Branding: 'Designed by The LearnAi'.\n\n"
            f"Page Number: {row['Page Number']}\n\n"
            f"Style: {st.session_state.styles}"
        )
        
        col_txt, col_img = st.columns([1, 1])
        with col_txt:
            st.code(prompt_block, language="text")
            if st.button(f"Generate Page {row['Page Number']}", key=f"g_{index}"):
                with col_img:
                    if "Nano Banana" in st.session_state.selected_model:
                        st.warning("Please copy the prompt and paste it into our chat window!")
                    else:
                        with st.spinner("Generating..."):
                            # Placeholder for actual Imagen API call
                            st.image("https://via.placeholder.com/400x500.png?text=Coloring+Book+Page", caption=f"Page {row['Page Number']}")
