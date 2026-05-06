import streamlit as st
import pandas as pd
import google.generativeai as genai

# --- 1. PAGE CONFIGURATION & STYLING ---
st.set_page_config(page_title="LearnAi Architect", layout="wide")

st.markdown("""
    <style>
    [data-testid="stAppViewContainer"] { background-color: #006994; }
    .stMarkdown, p, h1, h2, h3, span, label { color: white !important; }
    
    /* Stepper UI CSS */
    .stepper-wrapper { display: flex; justify-content: space-between; margin: 40px 0; position: relative; }
    .stepper-item { position: relative; display: flex; flex-direction: column; align-items: center; flex: 1; }
    .stepper-item::before { position: absolute; content: ""; border-bottom: 2px solid #ccc; width: 100%; top: 20px; left: -50%; z-index: 0; }
    .stepper-item:first-child::before { content: none; }
    .step-counter { position: relative; z-index: 1; display: flex; justify-content: center; align-items: center; width: 40px; height: 40px; border-radius: 50%; background: #ccc; margin-bottom: 6px; color: black; font-weight: bold; }
    .active .step-counter { background-color: #3f51b5; color: white; }
    .completed .step-counter { background-color: #4caf50; color: white; }
    .step-name { font-size: 14px; color: white; font-weight: 500; }
    
    /* Remove the visibility icon padding if possible via CSS */
    .stTextInput input[type="password"]::-ms-reveal,
    .stTextInput input[type="password"]::-ms-clear { display: none; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. LOGIC & DATA HELPERS ---
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
    # Use st.write("") followed by markdown to ensure clean clearing of the buffer
    st.markdown(html, unsafe_allow_html=True)

# --- 3. APP HEADER ---
st.markdown("<h1 style='text-align: center;'>🎨 The LearnAi: Coloring Book Architect</h1>", unsafe_allow_html=True)
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
            style_list = st.multiselect("Selected Styles", ["Bold black line art", "Pure white background", "No shading", "High-contrast outlines"])

        st.markdown("---")
        st.subheader("Link Google AI Studio")
        
        # To remove the eye icon, we use a standard text input with a custom label 
        # but warn the user it is not masked. Alternatively, type="default" removes it.
        api_input = st.text_input("Enter API Key", type="default", help="The eye icon is removed; please ensure your screen is private.")
        
        if st.button("Connect & Load Image Models"):
            if api_input:
                try:
                    genai.configure(api_key=api_input)
                    models = []
                    for m in genai.list_models():
                        if 'generateContent' in m.supported_generation_methods:
                            name = m.name.replace('models/', '')
                            label = f"{name} (free)" if "flash" in name.lower() else name
                            models.append(label)
                    
                    st.session_state.img_models = ["Nano Banana (free)"] + models
                    st.session_state.api_key = api_input
                    st.session_state.connected = True
                    st.success("Successfully Connected!")
                except Exception as e:
                    st.error(f"Connection Failed: {e}")

        if st.session_state.connected:
            st.session_state.selected_model = st.selectbox("Select Model to Use", st.session_state.img_models)
            if st.button("Next Step: Create Blueprint ➡️"):
                if topic and age_group:
                    rows = [{"Page Number": i, "Header": f"Did you know {topic} is fun?", "Orientation": "Portrait (8.5 x 11 inches)"} for i in range(1, page_count + 1)]
                    st.session_state.df = pd.DataFrame(rows)
                    st.session_state.topic = topic
                    st.session_state.styles = ", ".join(style_list)
                    st.session_state.step = 2
                    st.rerun()

# --- 5. STEP 2: BLUEPRINT & PROMPTS ---
elif st.session_state.step == 2:
    if st.button("⬅️ Back to Step 1"):
        st.session_state.step = 1
        st.rerun()

    st.subheader("Finalize your Page Content")
    updated_df = st.data_editor(st.session_state.df, use_container_width=True, hide_index=True)
    
    st.markdown("---")
    for index, row in updated_df.iterrows():
        final_visual_prompt = (
            f"The Content for Page {row['Page Number']} :\n\n"
            f"Create a high-resolution, printable children's coloring page in {row['Orientation']}. "
            f"Ensure high-quality line art and correct text placement for printing.\n\n"
            f"Subject: Clean black and white line art of {st.session_state.topic}. Wide, clear lines, no shading.\n\n"
            f"Top Header: {row['Header']}\n\n"
            f"Footer Branding: 'Designed by The LearnAi'.\n\n"
            f"Page Number: {row['Page Number']}\n\n"
            f"Style: {st.session_state.styles}"
        )
        
        col_txt, col_img = st.columns([1.2, 1])
        with col_txt:
            st.code(final_visual_prompt, language="text")
            if st.button(f"Generate Page {row['Page Number']}", key=f"btn_{index}"):
                with col_img:
                    if "Nano Banana" in st.session_state.selected_model:
                        st.info("Paste the prompt above into our chat window!")
                    else:
                        st.image("https://via.placeholder.com/400x500.png?text=Coloring+Page", caption=f"Page {row['Page Number']}")

    if st.button("Finish Project"):
        st.session_state.step = 3
        st.rerun()

# --- 6. STEP 3: DONE ---
elif st.session_state.step == 3:
    st.balloons()
    st.success("Project Completed!")
    if st.button("Start New Project"):
        st.session_state.step = 1
        st.rerun()
