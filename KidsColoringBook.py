import streamlit as st
import pandas as pd
from io import BytesIO
from docx import Document

# Custom CSS for the Sea Blue background and one-line title
st.markdown("""
    <style>
    [data-testid="stAppViewContainer"] {
        background-color: #006994;
    }
    .stMarkdown, p, h1, h2, h3, span, label {
        color: white !important;
    }
    .main-title {
        text-align: center;
        font-size: 2.5rem;
        font-weight: bold;
        white-space: nowrap;
        padding-bottom: 20px;
        border-bottom: 1px solid white;
    }
    .stDataEditor {
        background-color: white;
        border-radius: 5px;
    }
    </style>
    <div class="main-title">🎨 The LearnAi: Coloring Book Architect</div>
    """, unsafe_allow_html=True)

def get_unique_header(page_num, topic, age_group):
    """Generates unique educational content for each page."""
    is_junior = "6-9" in age_group
    if is_junior:
        messages = [
            f"Did you know {topic} can be seen from miles away? It is truly a wonder of nature!",
            f"History tells us that {topic} changed the way we see the world. What colors represent history?",
            f"Scientists study {topic} to learn about patterns. Can you color these patterns carefully?",
            f"Imagine {topic} is part of a magical kingdom. Use your most royal colors here!",
            f"Every {topic} has a secret. Your colors will help reveal the beauty of this scene."
        ]
    else:
        messages = [
            f"Look at this big {topic}! Can you use your favorite bright colors to fill it in?",
            f"Stay inside the lines of the {topic}. You are doing a wonderful job!",
            f"What color is a happy {topic}? Use that color to make this page smile!",
            f"Trace the edges of the {topic} first, then fill the middle with color.",
            f"How many {topic} shapes can you see? Color them all differently!"
        ]
    return messages[page_num % len(messages)]

# Input Section
with st.container():
    col1, col2, col3 = st.columns([2, 1, 2])
    with col1:
        topic = st.text_input("Book Topic", placeholder="e.g. Ocean Life")
        page_count = st.number_input("Total Pages", min_value=1, value=1)
    with col2:
        age_group = st.selectbox("Age Group", ["3-5 years (Explorer)", "6-9 years (Junior Creator)"])
    with col3:
        style_list = st.multiselect("Styles", 
            ["Bold black line art", "Pure white background", "No shading", "High-contrast outlines", "Whimsical details"],
            placeholder="Choose styles...")

if 'df' not in st.session_state:
    st.session_state.df = None

if st.button("Generate Blueprint"):
    if not topic or not style_list:
        st.error("Please provide a topic and select at least one style.")
    else:
        rows = []
        for i in range(1, page_count + 1):
            rows.append({
                "Page Number": i,
                "Header Content": f"{get_unique_header(i, topic, age_group)} [Designed by The LearnAi]",
                "Orientation": "Portrait" if i % 2 != 0 else "Landscape",
                "Branding": "Designed by The LearnAi"
            })
        st.session_state.df = pd.DataFrame(rows)

if st.session_state.df is not None:
    # Editable Table
    updated_df = st.data_editor(
        st.session_state.df,
        column_config={"Orientation": st.column_config.SelectboxColumn("Orientation", options=["Portrait", "Landscape"])},
        use_container_width=True
    )

    st.markdown("---")
    if st.radio("Generate final visual prompts?", ["No", "Yes"], horizontal=True) == "Yes":
        all_prompts = []
        combined_styles = ", ".join(style_list)
        
        for _, row in updated_df.iterrows():
            prompt = (
                f"Page {row['Page Number']}:\n"
                f"Create a high-resolution, printable children's coloring page in {row['Orientation']} "
                f"orientation (8.5 x 11 inches).\n\n"
                f"Subject: {topic}. {row['Header Content']}\n\n"
                f"Style: {combined_styles}\n\n"
                f"Footer Branding: {row['Branding']}"
            )
            all_prompts.append(prompt)
            st.text_area(f"Page {row['Page Number']}", prompt, height=200)

        # Download Buttons
        st.subheader("📥 Export Prompts")
        d_col1, d_col2, d_col3 = st.columns(3)

        # Word Export
        doc = Document()
        doc.add_heading(f"Blueprint for {topic}", 0)
        for p in all_prompts:
            doc.add_paragraph(p)
            doc.add_page_break()
        bio = BytesIO()
        doc.save(bio)
        d_col1.download_button("Download Word", data=bio.getvalue(), file_name="blueprint.docx")

        # CSV Export
        d_col2.download_button("Download CSV", data="\n\n".join(all_prompts), file_name="blueprint.csv")

        # Excel Export
        xl_bio = BytesIO()
        with pd.ExcelWriter(xl_bio, engine='openpyxl') as writer:
            pd.DataFrame({"Visual Prompts": all_prompts}).to_excel(writer, index=False)
        d_col3.download_button("Download Excel", data=xl_bio.getvalue(), file_name="blueprint.xlsx")
