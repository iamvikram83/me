import streamlit as st
import pandas as pd

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
if 'step' not in st.session_state:
    st.session_state.step = 1

# --- 3. MASTER PROMPT LOGIC ---
def get_visual_prompt(row, style_tags):
    """Generates the prompt based on the Master Template logic."""
    # Mapping Orientation to specific print dimensions
    if row['Orientation'] == "Portrait":
        dims = "Portrait orientation (8.5 x 11 inches)"
    else:
        dims = "Landscape orientation (11 x 8.5 inches)"
        
    prompt = (
        f"The Content for Page {row['Page']}:\n\n"
        f"Create a high-resolution, printable children's coloring page in {dims}. "
        f"Ensure high-quality line art and correct text placement for printing.\n\n"
        f"Subject: {row['Scene Description']}\n\n"
        f"Top Header: {row['Header']}\n\n"
        f"Footer Branding: 'Designed by The LearnAi'.\n\n"
        f"Page Number: {row['Page']}\n\n"
        f"Style: {style_tags}"
    )
    return prompt

# --- 4. APP HEADER ---
st.markdown("<h1 style='text-align: center;'>🎨 The LearnAi: Coloring Book Architect</h1>", unsafe_allow_html=True)
st.markdown("---")

# --- 5. STEP 1: SETUP ---
if st.session_state.step == 1:
    c1, c2 = st.columns(2)
    with c1:
        topic = st.text_input("Book Topic", placeholder="e.g. Good Habits")
        page_count = st.number_input("Total Pages", min_value=1, value=5)
    with c2:
        age_group = st.selectbox("Age Group", options=["3-5 years", "6-9 years"])
        style_list = st.multiselect("Selected Styles", 
                                    options=["Bold black lines", "No shading", "White background", "High-contrast outlines"],
                                    default=[],
                                    placeholder="Select styles...")

    if st.button("Generate Visual Prompts ➡️"):
        if topic and style_list:
            st.session_state.topic = topic
            st.session_state.style_tags = ", ".join(style_list)
            
            # Initialize unique data structure
            data = []
            for i in range(page_count):
                data.append({
                    "Page": i + 1,
                    "Header": f"Did you know about {topic}? Instruction: Use bright colors for the smiles!",
                    "Orientation": "Portrait",
                    "Scene Description": f"Clean line art of {topic} related scene."
                })
            st.session_state.df = pd.DataFrame(data)
            st.session_state.step = 2
            st.rerun()
        else:
            st.warning("Please enter a Topic and select at least one Style.")

# --- 6. STEP 2: INTERACTIVE VISUAL PROMPTS ---
elif st.session_state.step == 2:
    col_back, col_toggle = st.columns([1, 1])
    with col_back:
        if st.button("⬅️ Back to Setup"):
            st.session_state.step = 1
            st.rerun()
    with col_toggle:
        show_table = st.checkbox("🔍 View/Edit Blueprint Table", value=False)

    if show_table:
        st.subheader("Blueprint Table")
        # Direct editing in table syncs with prompts
        edited_df = st.data_editor(
            st.session_state.df, 
            use_container_width=True, 
            hide_index=True,
            column_config={
                "Orientation": st.column_config.SelectboxColumn(options=["Portrait", "Landscape"])
            }
        )
        st.session_state.df = edited_df

    st.markdown("---")
    st.subheader("Visual Prompt Summary")
    
    # Render individual page controls and prompts
    for index, row in st.session_state.df.iterrows():
        with st.expander(f"Page {row['Page']} - {row['Orientation']}"):
            ui_col, prompt_col = st.columns([1, 2])
            
            with ui_col:
                # Orientation selector that triggers dynamic prompt update
                new_orient = st.selectbox(
                    f"Change Orientation", 
                    options=["Portrait", "Landscape"],
                    index=0 if row['Orientation'] == "Portrait" else 1,
                    key=f"opt_{index}"
                )
                if new_orient != row['Orientation']:
                    st.session_state.df.at[index, 'Orientation'] = new_orient
                    st.rerun()
                
                # Editable header for unique page facts
                new_head = st.text_area(f"Edit Header Content", value=row['Header'], key=f"head_{index}")
                if new_head != row['Header']:
                    st.session_state.df.at[index, 'Header'] = new_head
                    st.rerun()

            with prompt_col:
                # Calculate prompt using the Master Template logic
                final_prompt = get_visual_prompt(st.session_state.df.iloc[index], st.session_state.style_tags)
                st.code(final_prompt, language="text")

    st.markdown("---")
    st.download_button("📥 Download All Prompts (CSV)", 
                       st.session_state.df.to_csv(index=False).encode('utf-8'), 
                       "blueprint.csv", "text/csv")
