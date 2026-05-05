import streamlit as st
import pandas as pd
from io import BytesIO
from docx import Document

# 1. UI Styling: Sea Blue Background and Horizontal Title
st.markdown("""
    <style>
    [data-testid="stAppViewContainer"] {
        background-color: #006994;
    }
    .stMarkdown, p, h1, h2, h3, span, label {
        color: white !important;
    }
    .full-width-title {
        width: 100%;
        text-align: center;
        font-size: 2.2rem;
        font-weight: bold;
        padding: 10px 0px;
        white-space: nowrap;
        border-bottom: 2px solid rgba(255,255,255,0.2);
        margin-bottom: 20px;
    }
    .stDataEditor {
        background-color: white;
        border-radius: 8px;
    }
    </style>
    <div class="full-width-title">🎨 The LearnAi: Kids' Coloring Book Architect</div>
    """, unsafe_allow_html=True)

def get_dynamic_header(index, topic, age_group):
    """Generates unique instructions/facts for every page."""
    is_junior = "6-9" in age_group
    if is_junior:
        facts = [
            f"Did you know {topic} can be seen from space? Look at the amazing details!",
            f"The history of {topic} is full of surprises. What colors represent its past?",
            f"Scientists study {topic} to learn about our future. Use your imagination here!",
            f"Every {topic} tells a story. What story will your colors tell today?",
            f"Imagine {topic} in a world made of candy. What colors would you use then?"
        ]
        return facts[index % len(facts)]
    else:
        instructions = [
            f"Can you find the hidden shapes in this {topic}? Color them first!",
            f"Use your brightest crayons for this {topic}! You're doing great.",
            f"Stay inside the thick lines of the {topic}. It looks wonderful!",
            f"What is your favorite color for {topic}? Fill the whole page!",
            f"Trace the edges of the {topic} before you start coloring the middle."
        ]
        return instructions[index % len(instructions)]

# --- Input Section ---
with st.container():
    c1, c2, c3 = st.columns([2, 1, 2])
    with c1:
        topic = st.text_input("Book Topic", value="", placeholder="e.g. Space Adventures")
        page_count = st.number_input("Total Pages", min_value=1, value=1)
    with c2:
        age_group = st.selectbox("Age Group", ["3-5 years (Explorer)", "6-9 years (Junior Creator)"])
    with c3:
        styles = st.multiselect("Visual Styles", 
            ["Bold black line art", "Pure white background", "No shading", "High-contrast outlines", "Whimsical details"],
            placeholder="Select styles to apply...")

# --- Logic & Processing ---
if 'blueprint' not in st.session_state:
    st.session_state.blueprint = None

if st.button("Generate Book Blueprint"):
    if not topic or not styles:
        st.warning("Please provide a Topic and at least one Style.")
    else:
        rows = []
        for i in range(1, page_count + 1):
            rows.append({
                "Page Number": i,
                "Header Content": f"{get_dynamic_header(i, topic, age_group)} [Designed by The LearnAi]",
                "Orientation": "Portrait" if i % 2 != 0 else "Landscape",
                "Branding": "Designed by The LearnAi"
            })
        st.session_state.blueprint = pd.DataFrame(rows)

if st.session_state.blueprint is not None:
    st.subheader("Interactive Blueprint Editor")
    # Editable table for orientation
    final_df = st.data_editor(
        st.session_state.blueprint,
        column_config={
            "Orientation": st.column_config.SelectboxColumn("Orientation", options=["Portrait", "Landscape"])
        },
        use_container_width=True
    )

    st.markdown("---")
    show_prompts = st.radio("Would you like to generate visual/image prompts?", ["No", "Yes"], horizontal=True)

    if show_prompts == "Yes":
        all_prompts = []
        style_str = ", ".join(styles)
        
        for _, row in final_df.iterrows():
            prompt = (
                f"Page {row['Page Number']}:\n"
                f"Create a high-resolution, printable children's coloring page in {row['Orientation']} "
                f"orientation (8.5 x 11 inches).\n\n"
                f"Subject: {topic} - {row['Orientation']} composition. {row['Header Content']}\n\n"
                f"Style: {style_str}\n\n"
                f"Footer Branding: {row['Branding']}"
            )
            all_prompts.append(prompt)
            st.text_area(f"Visual Prompt for Page {row['Page Number']}", prompt, height=200)

        # --- Export Features ---
        st.markdown("### 📥 Download Prompts")
        ec1, ec2, ec3 = st.columns(3)

        # Word Export
        doc = Document()
        doc.add_heading(f"Coloring Book Blueprint: {topic}", 0)
        for p in all_prompts:
            doc.add_paragraph(p)
            doc.add_page_break()
        word_io = BytesIO()
        doc.save(word_io)
        ec1.download_button("Download Word (.docx)", data=word_io.getvalue(), file_name="prompts.docx")

        # CSV Export
        csv_data = "\n\n---\n\n".join(all_prompts)
        ec2.download_button("Download CSV", data=csv_data, file_name="prompts.csv")

        # Excel Export
        xl_io = BytesIO()
        with pd.ExcelWriter(xl_io, engine='openpyxl') as writer:
            pd.DataFrame({"Prompts": all_prompts}).to_excel(writer, index=False)
        ec3.download_button("Download Excel (.xlsx)", data=xl_io.getvalue(), file_name="prompts.xlsx")
