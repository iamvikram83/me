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
def get_image_models(api_key):
    try:
        genai.configure(api_key=api_key)
        available_models = []
        for m in genai.list_models():
            if 'image' in m.description.lower() or 'generate_image' in m.supported_generation_methods:
                tier = " (Free Tier)" if "flash" in m.name.lower() else " (Paid Tier)"
                available_models.append(f"{m.display_name}{tier}")
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
            style_list = st.multiselect("Selected Styles", ["Bold black lines", "No shading", "White background"], default=["Bold black lines"])

        st.markdown("---")
        st.subheader("Image Generation Preferences")
        want_ai = st.radio("Would you like to generate images here using visual prompts?", options=["No", "Yes"], horizontal=True)

        if want_ai == "Yes":
            st.markdown("#### 🔗 Link Google AI Studio")
            if not st.session_state.connected:
                api_input = st.text_input("Enter API Key", type="password")
                if st.button("Connect & Load Models"):
                    if api_input:
                        st.session_state.api_key = api_input
                        st.session_state.connected = True
                        st.rerun()
            else:
                st.success("✅ API Connected!")
                model_options = get_image_models(st.session_state.api_key)
                st.session_state.gen_model = st.selectbox("Select Image Generation Model", options=model_options)
                if st.button("Disconnect API"):
                    st.session_state.connected = False
                    st.rerun()
        else:
            st.session_state.connected = False
            st.session_state.gen_model = "Manual Mode"

        if st.button("Next Step: Create Blueprint ➡️"):
            if topic:
                st.session_state.topic = topic
                st.session_state.page_count = page_count
                st.session_state.age_group = age_group
                st.session_state.style_tags = ", ".join(style_list)
                st.session_state.want_ai = want_ai
                
                # FIXED: Unique Initialization
                st.session_state.df = pd.DataFrame([
                    {"Page": i + 1, "Scene Description": f"Specific scene for {topic} - Part {i+1}", "Prompt": ""}
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
    
    # RENDER DATA EDITOR FIRST
    edited_df = st.data_editor(st.session_state.df, use_container_width=True, hide_index=True)
    
    # FIXED: Update Session State and generate unique prompts AFTER edit
    st.session_state.df = edited_df
    for index, row in st.session_state.df.iterrows():
        unique_prompt = (
            f"Coloring book page for {st.session_state.get('age_group')}. "
            f"Subject: {row['Scene Description']}. Style: {st.session_state.get('style_tags')}. "
            "Minimal details, high contrast."
        )
        st.session_state.df.at[index, 'Prompt'] = unique_prompt

    st.download_button("📥 Download All Page Prompts", 
                       data=st.session_state.df.to_csv(index=False).encode('utf-8'), 
                       file_name="blueprint.csv", mime="text/csv")

    st.markdown("---")
    st.subheader("Visual Prompt Summary")
    
    # Display unique prompts in expanders
    for index, row in st.session_state.df.iterrows():
        with st.expander(f"Page {row['Page']} - {row['Scene Description']}"):
            st.code(row['Prompt'], language="text")
            if st.session_state.get('want_ai') == "Yes" and st.session_state.connected:
                if st.button(f"Generate Image for Page {row['Page']}", key=f"btn_{index}"):
                    st.write(f"⏳ Generating unique image using: {st.session_state.get('gen_model')}")

    if st.button("Finish Project ✅"):
        st.session_state.step = 3
        st.rerun()

# --- 8. STEP 3: DONE ---
elif st.session_state.step == 3:
    st.balloons()
    st.success("🎉 Project Completed!")
    st.dataframe(st.session_state.df, use_container_width=True, hide_index=True)
    if st.button("🔄 Start New Project"):
        for key in ['step', 'connected', 'df', 'topic', 'gen_model', 'want_ai']:
            st.session_state.pop(key, None)
        st.rerun()
