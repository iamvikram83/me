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
if 'step' not in st.session_state: st.session_state.step = 1

# --- 3. MASTER PROMPT LOGIC ---
def get_visual_prompt(row, style_tags):
    """Generates prompt based on the Master Template."""
    # Orientation logic
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
        style_list = st.multiselect("Styles", ["Bold black lines", "No shading", "White background"], default=["Bold black lines"])

    if st.button("Generate Visual Prompts ➡️"):
        if topic and style_list:
            st.session_state.topic = topic
            st.session_state.style_tags = ", ".join(style_list)
            
            # Initialize hidden data
            data = []
            for i in range(page_count):
                data.append({
                    "Page": i + 1,
                    "Header": f"Did you know about {topic}? Use bright colors for the smiles!",
                    "Orientation": "Portrait",
                    "Scene Description": f"Clean line art of {topic} related scene."
                })
            st.session_state.df = pd.DataFrame(data)
            st.session_state.step = 2
            st.rerun()

# --- 6. STEP 2: VISUAL PROMPTS (NO TABLE DISPLAYED) ---
elif st.session_state.step == 2:
    if st.button("⬅️ Back to Setup"):
        st.session_state.step = 1
        st.rerun()

    st.subheader("Visual Prompt Summary")
    st.info(f"Topic: {st.session_state.topic} | Use the options below to adjust individual pages.")

    # Iterate through the rows to display expanders
    for index, row in st.session_state.df.iterrows():
        with st.expander(f"Page {row['Page']} - {row['Orientation']} Mode"):
            
            col_ui, col_code = st.columns([1, 3])
            
            with col_ui:
                # Editable Orientation for this specific page
                new_orientation = st.selectbox(
                    f"Orientation (Page {row['Page']})",
                    options=["Portrait", "Landscape"],
                    index=0 if row['Orientation'] == "Portrait" else 1,
                    key=f"orient_{index}"
                )
                
                # Update logic if changed
                if new_orientation != row['Orientation']:
                    st.session_state.df.at[index, 'Orientation'] = new_orientation
                    st.rerun()

                st.text_input(f"Edit Header (Page {row['Page']})", value=row['Header'], key=f"head_{index}")
                # Update description if edited
                new_desc = st.text_area(f"Edit Scene (Page {row['Page']})", value=row['Scene Description'], key=f"desc_{index}")
                if new_desc != row['Scene Description']:
                    st.session_state.df.at[index, 'Scene Description'] = new_desc
                    st.rerun()

            with col_code:
                # Generate and display the final prompt based on current row state
                final_prompt = get_visual_prompt(st.session_state.df.iloc[index], st.session_state.style_tags)
                st.markdown(f"**Current Orientation:** {new_orientation}")
                st.code(final_prompt, language="text")

    st.markdown("---")
    if st.button("Finish Project ✅"):
        st.balloons()
        st.success("Project Finalized!")
