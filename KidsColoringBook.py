import streamlit as st
import pandas as pd
import google.generativeai as genai

# --- 1. PAGE CONFIGURATION ---
st.set_page_config(page_title="LearnAi Architect", layout="wide")

st.markdown("""
    <style>
    [data-testid="stAppViewContainer"] { background-color: #006994; }
    .stMarkdown, p, h1, h2, h3, span, label { color: white !important; }
    button[aria-label="Show password"], button[aria-label="Hide password"] { display: none !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. SESSION STATE ---
if 'step' not in st.session_state: st.session_state.step = 1
if 'connected' not in st.session_state: st.session_state.connected = False

# --- 3. STEPPER ---
def render_stepper(current_step):
    steps = ["1 · Setup", "2 · Blueprint", "3 · Done"]
    cols = st.columns(3)
    for i, (col, name) in enumerate(zip(cols, steps), 1):
        if i == current_step: col.success(f"🔵 **{name}**")
        elif i < current_step: col.success(f"✅ **{name}**")
        else: col.info(f"⬜ {name}")

# --- 4. MASTER PROMPT GENERATOR ---
def generate_master_prompt(row, style_tags):
    """Applies the specific Master Template logic provided by the user."""
    orientation_str = "Portrait orientation (8.5 x 11 inches)" if row['Orientation'] == "Portrait" else "Landscape orientation (11 x 8.5 inches)"
    
    prompt = (
        f"The Content for Page {row['Page']}:\n\n"
        f"Create a high-resolution, printable children's coloring page in {orientation_str}. "
        f"Ensure high-quality line art and correct text placement for printing.\n\n"
        f"Subject: {row['Scene Description']}\n\n"
        f"Top Header: {row['Header']}\n\n"
        f"Footer Branding: 'Designed by The LearnAi'.\n\n"
        f"Page Number: {row['Page']}\n\n"
        f"Style: {style_tags}"
    )
    return prompt

# --- 5. APP HEADER ---
st.markdown("<h1 style='text-align: center;'>🎨 The LearnAi: Coloring Book Architect</h1>", unsafe_allow_html=True)
render_stepper(st.session_state.step)

# --- 6. STEP 1: SETUP ---
if st.session_state.step == 1:
    with st.container():
        c1, c2 = st.columns(2)
        with c1:
            topic = st.text_input("Book Topic", value=st.session_state.get('topic', ''), placeholder="e.g. Good Habits")
            page_count = st.number_input("Total Pages", min_value=1, value=st.session_state.get('page_count', 5))
        with c2:
            age_group = st.selectbox("Age Group", options=["3-5 years", "6-9 years"])
            # Style is blank/placeholder by default
            style_list = st.multiselect("Selected Styles", 
                                        options=["Bold black lines", "No shading", "White background", "High-contrast outlines"],
                                        default=[],
                                        placeholder="Please select styles...")

        if st.button("Next Step: Create Blueprint ➡️"):
            if topic and style_list:
                st.session_state.topic = topic
                st.session_state.style_tags = ", ".join(style_list)
                st.session_state.page_count = page_count
                st.session_state.age_group = age_group
                
                # Initialize with unique headers and scene descriptions
                data = []
                for i in range(page_count):
                    data.append({
                        "Page": i + 1,
                        "Header": f"Did you know about {topic}? Instruction: Color the scene using bright tones.",
                        "Orientation": "Portrait",
                        "Scene Description": f"Clean line art of {topic} related scene.",
                        "Full Prompt": ""
                    })
                st.session_state.df = pd.DataFrame(data)
                st.session_state.step = 2
                st.rerun()
            else:
                st.warning("Please provide a Topic and select at least one Style.")

# --- 7. STEP 2: BLUEPRINT ---
elif st.session_state.step == 2:
    if st.button("⬅️ Back"):
        st.session_state.step = 1
        st.rerun()

    st.subheader("Edit Page Details & Orientation")

    # Table with horizontal scroll enabled via column_config widths
    edited_df = st.data_editor(
        st.session_state.df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Page": st.column_config.NumberColumn(width="small", disabled=True),
            "Header": st.column_config.TextColumn("Header (Story/Fact)", width="large"),
            "Orientation": st.column_config.SelectboxColumn("Orientation", options=["Portrait", "Landscape"], width="medium"),
            "Scene Description": st.column_config.TextColumn("Scene Description", width="large"),
            "Full Prompt": st.column_config.TextColumn("Final Prompt", width="large", disabled=True)
        }
    )

    # Sync prompts with the Master Template logic
    for index, row in edited_df.iterrows():
        edited_df.at[index, 'Full Prompt'] = generate_master_prompt(row, st.session_state.style_tags)
    
    st.session_state.df = edited_df

    st.markdown("---")
    st.subheader("Visual Prompt Summary")
    for index, row in st.session_state.df.iterrows():
        with st.expander(f"Page {row['Page']} - {row['Header'][:50]}..."):
            st.code(row['Full Prompt'], language="text")

    if st.button("Finish Project ✅"):
        st.session_state.step = 3
        st.rerun()

# --- 8. STEP 3: DONE ---
elif st.session_state.step == 3:
    st.balloons()
    st.success("🎉 Project Blueprint Ready!")
    st.dataframe(st.session_state.df[["Page", "Header", "Orientation", "Full Prompt"]], use_container_width=True)
    st.download_button("📥 Download CSV", st.session_state.df.to_csv(index=False), "blueprint.csv")
    if st.button("Restart"):
        st.session_state.clear()
        st.rerun()
