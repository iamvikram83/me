import streamlit as st
import pandas as pd

# 1. Custom CSS for Sea Blue Background
st.markdown("""
    <style>
    .stApp {
        background-color: #006994;
        color: white;
    }
    .stMarkdown, .stTable, .stDataFrame {
        background-color: rgba(255, 255, 255, 0.1);
        border-radius: 10px;
        padding: 10px;
    }
    </style>
    """, unsafe_allow_get_template=True)

def generate_visual_prompt(row, style, topic):
    """Formats the final visual prompt according to specific blueprint requirements."""
    return (
        f"Page {row['Page Number']}:\n"
        f"Create a high-resolution, printable children's coloring page in {row['Orientation'].capitalize()} "
        f"orientation (8.5 x 11 inches). Ensure high-quality line art and correct text placement for printing.\n\n"
        f"The Content for Page {row['Page Number']}:\n"
        f"Subject: {topic} - {row['Orientation']} composition. Wide, clear lines, no shading. Minimalist background.\n\n"
        f"Top Header: {row['Header Content']}\n\n"
        f"Footer Branding: {row['Branding']}\n\n"
        f"Page Number: {row['Page Number']}\n\n"
        f"Style: {style}"
    )

# --- UI Setup ---
st.title("🎨 The LearnAi: Coloring Book Architect")

# Sidebar/Form Inputs
with st.container():
    col1, col2 = st.columns(2)
    with col1:
        topic = st.text_input("Book Topic", "Kindness and Sharing")
        page_count = st.number_input("Total Pages", min_value=1, value=5)
    with col2:
        age_group = st.selectbox("Age Group", ["3-5 years (Explorer)", "6-9 years (Junior Creator)"])
        style_preset = st.selectbox("Artistic Style", [
            "Bold black line art, pure white background, no shading, and high-contrast outlines",
            "Fine line detail, whimsical patterns, white background, professional grade",
            "Thick outlines, geometric shapes, minimalist background for toddlers"
        ])

# Initialize session state for the blueprint
if 'blueprint_df' not in st.session_state:
    st.session_state.blueprint_df = None

if st.button("Generate Book Blueprint"):
    data = []
    is_junior = "6-9" in age_group
    
    for i in range(1, page_count + 1):
        orientation = "Portrait" if i % 2 != 0 else "Landscape"
        header = (f"Did you know saying 'Please' and 'Thank You' acts like a 'social glue'? "
                  if is_junior else f"Let's share fruit with friends! ")
        
        data.append({
            "Page Number": i,
            "Header Content": f"{header} [Designed by The LearnAi]",
            "Orientation": orientation,
            "Branding": "Designed by The LearnAi"
        })
    st.session_state.blueprint_df = pd.DataFrame(data)

# 3. Editable Table (Orientation as inline editable)
if st.session_state.blueprint_df is not None:
    st.subheader("Edit Your Blueprint")
    edited_df = st.data_editor(
        st.session_state.blueprint_df,
        column_config={
            "Orientation": st.column_config.SelectboxColumn(
                "Orientation",
                options=["Portrait", "Landscape"],
                required=True,
            )
        },
        disabled=["Page Number", "Branding"],
        num_rows="fixed",
        use_container_width=True
    )
    
    # 2. Ask User if they want to generate prompts
    st.markdown("---")
    gen_prompts = st.radio("Would you like to generate visual/image prompts?", ("No", "Yes"))

    if gen_prompts == "Yes":
        st.subheader("🚀 Final Visual Prompts for Image Generators")
        for index, row in edited_df.iterrows():
            final_prompt = generate_visual_prompt(row, style_preset, topic)
            st.text_area(f"Page {row['Page Number']} Prompt", final_prompt, height=250)
            st.markdown("---")
