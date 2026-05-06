import streamlit as st
import pandas as pd
import google.generativeai as genai

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

# --- 3. STEPPER (Native Streamlit) ---
def render_stepper(current_step):
    steps = ["1 · Setup & Connection", "2 · Blueprint & Prompts", "3 · Done"]
    cols = st.columns(3)
    for i, (col, name) in enumerate(zip(cols, steps), 1):
        if i == current_step: col.success(f"🔵 **{name}**")
        elif i < current_step: col.success(f"✅ **{name}**")
        else: col.info(f"⬜ {name}")

# --- 4. DATA HELPER: LOAD MODELS ---
def get_image_models():
    """Fetches available image models from the API and maps their cost tier."""
    if not st.session_state.connected:
        return ["Connect API to view models"]
    
    try:
        genai.configure(api_key=st.session_state.api_key)
        # Note: In the current API, 'imagen-3' or similar names are standard
        available_models = []
        for m in genai.list_models():
            if 'image' in m.description.lower() or 'generate_image' in m.supported_generation_methods:
                # Basic logic for Free vs Paid mapping
                tier = " (Free Tier)" if "flash" in m.name.lower() else " (Paid Tier)"
                available_models.append(f"{m.display_name}{tier}")
        
        # Fallback if no specific image models are found/returned by the list
        if not available_models:
            return ["Imagen 3 (Paid Tier)", "Imagen 3 Fast (Free Tier)"]
        return available_models
    except Exception:
        return ["Error loading models - Check API Key"]

# --- 5. APP HEADER ---
st.markdown("<h1 style='text-align: center;'>🎨 The LearnAi: Coloring Book Architect</h1>", unsafe_allow_html=True)
render_stepper(st.session_state.step)
st.markdown("---")

# --- 6. STEP 1: SETUP & API ---
if st.session_state.step == 1:
    with st.container():
        c1, c2 = st.columns(2)
        with c1:
            topic = st.text_input("Book Topic", value=st.session_state.get('topic', ''), placeholder="e.g. Manners and Kindness")
            page_count = st.number_input("Total Pages", min_value=1, value=st.session_state.get('page_count', 1))
        with c2:
            age_group = st.selectbox("Age Group", options=["3-5 years", "6-9 years"], index=0)
            
            # DYNAMIC MODEL LOADING
            model_options = get_image_models()
            gen_model = st.selectbox("Image Generation Model", options=model_options)
            
            style_list = st.multiselect("Selected Styles", ["Bold black lines", "No shading", "White background"], default=["Bold black lines"])

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
                st.rerun()

        if st.session_state.connected:
            if st.button("Next Step: Create Blueprint ➡️"):
                if topic:
                    st.session_state.topic = topic
                    st.session_state.page_count = page_count
                    st.session_state.age_group = age_group
                    st.session_state.gen_model = gen_model
                    st.session_state.style_tags = ", ".join(style_list)
                    
                    st.session_state.df = pd.DataFrame([
                        {"Page": i + 1, "Scene Description": f"Scene for {topic}", "Prompt": ""}
                        for i in range(page_count)
                    ])
                    st.session_state.step = 2
                    st.rerun()
                else:
                    st.warning("Please enter a Book Topic.")

# --- 7. STEP 2: BLUEPRINT & PROMPTS ---
elif st.session_state.step == 2:
    if st.button("⬅️ Back"):
        st.session_state.step = 1
        st.rerun()

    st.subheader("Finalize your Page Content")
    current_model = st.session_state.get('gen_model', 'Not Selected')
    st.info(f"**Target Model:** {current_model} | **Topic:** {st.session_state.get('topic', 'Not Set')}")

    edited_df = st.data_editor(st.session_state.df, use_container_width=True, hide_index=True)
    st.session_state.df = edited_df

    csv = st.session_state.df.to_csv(index=False).encode('utf-8')
    st.download_button("📥 Download All Page Prompts", data=csv, file_name="blueprint.csv", mime="text/csv")

    st.markdown("---")
    st.subheader("Visual Prompt Summary & Generation")
    
    for index, row in st.session_state.df.iterrows():
        full_prompt = (f"Coloring book page for {st.session_state.get('age_group')}. "
                       f"Subject: {row['Scene Description']}. Style: {st.session_state.get('style_tags')}. "
                       f"Optimized for {current_model}.")
        st.session_state.df.at[index, 'Prompt'] = full_prompt
        
        with st.expander(f"Page {row['Page']} - Image Generator"):
            st.code(full_prompt, language="text")
            if st.button(f"Generate Image for Page {row['Page']}", key=f"btn_{index}"):
                st.write(f"⏳ Calling {current_model} API for Page {row['Page']}...")

    if st.button("Finish Project ✅"):
        st.session_state.step = 3
        st.rerun()

# --- 8. STEP 3: DONE ---
elif st.session_state.step == 3:
    st.balloons()
    st.success("🎉 Project Completed!")
    st.dataframe(st.session_state.df, use_container_width=True, hide_index=True)
    if st.button("🔄 Start New Project"):
        for key in ['step', 'connected', 'df', 'topic', 'gen_model']:
            st.session_state.pop(key, None)
        st.rerun()
