import streamlit as st
import pandas as pd

# 1. Custom CSS for Sea Blue Background and White Text
st.markdown("""
    <style>
    [data-testid="stAppViewContainer"] {
        background-color: #006994;
    }
    [data-testid="stHeader"] {
        background-color: rgba(0,0,0,0);
    }
    .stMarkdown, p, h1, h2, h3, span {
        color: white !important;
    }
    /* Make the editor readable against blue */
    .stDataEditor {
        background-color: white;
        border-radius: 5px;
    }
    </style>
    """, unsafe_allow_html=True)

def generate_visual_prompt(row, style, topic):
    """Constructs the specific prompt format requested."""
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

st.title("🎨 The LearnAi: Coloring Book Architect")

# Sidebar/Inputs
with st.container():
    col1, col2 = st.columns(2)
    with col1:
        topic = st.text_input("Book Topic", "Kindness and Sharing")
        page_count = st.number_input("Total Pages", min_value=1, value=5)
    with col2:
        age_group = st.selectbox("Age Group", ["3-5 years (Explorer)", "6-9 years (Junior Creator)"])
        style_preset = st.selectbox("Style", [
            "Bold black line art, pure white background, no shading, and high-contrast outlines for a professional coloring book look",
            "Fine line detail, whimsical patterns, white background, high-contrast outlines",
            "Thick bold lines, simple shapes, white background, no shading"
        ])

# Initialize Blueprint
if 'blueprint_df' not in st.session_state:
    st.session_state.blueprint_df = None

if st.button("Generate Book Blueprint"):
    data = []
    is_junior = "6-9" in age_group
    
    for i in range(1, page_count + 1):
        orientation = "Portrait" if i % 2 != 0 else "Landscape"
        # Logic for header content based on your example
        header = (f"Did you know saying 'Please' and 'Thank You' acts like a 'social glue'? "
                  if is_junior else f"Let's share fruit with friends! ")
        
        data.append({
            "Page Number": i,
            "Header Content": f"{header} [Designed by The LearnAi]",
            "Orientation": orientation,
            "Branding": "Designed by The LearnAi"
        })
    st.session_state.blueprint_df = pd.DataFrame(data)

# Editable Section
if st.session_state.blueprint_df is not None:
    st.subheader("Edit Your Blueprint (Orientation is Clickable)")
    
    # Use the returned dataframe from the editor to ensure changes are captured
    final_df = st.data_editor(
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
        use_container_width=True,
        key="editor"
    )
    
    st.markdown("---")
    gen_prompts = st.radio("Would you like to generate visual/image prompts?", ("No", "Yes"))

    if gen_prompts == "Yes":
        st.subheader("🚀 Final Visual Prompts")
        for _, row in final_df.iterrows():
            prompt_text = generate_visual_prompt(row, style_preset, topic)
            st.text_area(f"Page {row['Page Number']}", prompt_text, height=300)
