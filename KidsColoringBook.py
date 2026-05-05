import streamlit as st
import pandas as pd
from io import BytesIO
from docx import Document

# 1. Custom CSS for UI Refinement
st.markdown("""
    <style>
    [data-testid="stAppViewContainer"] {
        background-color: #006994;
    }
    .stMarkdown, p, h1, h2, h3, span, label {
        color: white !important;
    }
    /* Title without underline and centered */
    .main-title {
        text-align: center;
        font-size: 2.5rem;
        font-weight: bold;
        white-space: nowrap;
        padding-bottom: 30px;
    }
    /* Make table headers visible and clean */
    thead tr th {
        background-color: #f0f2f6 !important;
        color: black !important;
        font-weight: bold !important;
    }
    .stDataEditor {
        background-color: white;
        border-radius: 8px;
    }
    </style>
    <div class="main-title">🎨 The LearnAi: Coloring Book Architect</div>
    """, unsafe_allow_html=True)

def get_unique_header(page_num, topic, age_group):
    """Dynamic content generation based on page number."""
    is_junior = "6-9" in age_group
    if is_junior:
        messages = [
            f"Explore the fascinating world of {topic}! What details can you add?",
            f"The history of {topic} is waiting for your colors. Make it vibrant!",
            f"Did you know {topic} has unique patterns? Study them as you color.",
            f"Imagine {topic} in a futuristic setting. Use neon shades!",
            f"Every {topic} has a story. Tell yours through your art."
        ]
    else:
        messages = [
            f"Here is a happy {topic}! Can you color it with bright crayons?",
            f"Stay inside the thick lines of the {topic}. You're doing great!",
            f"What color should a {topic} be? You decide the best look!",
            f"Color the {topic} first, then draw a sun in the background.",
            f"How many {topic} objects can you find? Give each a different color!"
        ]
    return messages[page_num % len(messages)]

# --- Input Section (2 per row) ---
with st.container():
    row1_col1, row1_col2 = st.columns(2)
    with row1_col1:
        topic = st.text_input("Book Topic", placeholder="e.g. Space Adventures", 
                              help="Enter the main theme of your coloring book.")
    with row1_col2:
        page_count = st.number_input("Total Pages", min_value=1, value=1, 
                                     help="How many unique coloring pages do you need?")
    
    row2_col1, row2_col2 = st.columns(2)
    with row2_col1:
        age_group = st.selectbox("Age Group", ["3-5 years (Explorer)", "6-9 years (Junior Creator)"],
                                 help="Selecting an age group changes the difficulty and tone of instructions.")
    with row2_col2:
        style_list = st.multiselect("Styles", 
            ["Bold black line art", "Pure white background", "No shading", "High-contrast outlines", "Whimsical details"],
            placeholder="Choose styles...", help="Select one or more styles for the image generation prompts.")

if 'df' not in st.session_state:
    st.session_state.df = None

if st.button("Generate Blueprint", help="Click to create the page-by-page table."):
    if not topic or not style_list:
        st.error("Please enter a topic and select at least one style.")
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

# --- Display Section ---
if st.session_state.df is not None:
    st.subheader("Interactive Blueprint Editor")
    
    # hide_index=True removes the index column from display
    updated_df = st.data_editor(
        st.session_state.df,
        column_config={
            "Orientation": st.column_config.SelectboxColumn("Orientation", options=["Portrait", "Landscape"]),
            "Page Number": st.column_config.NumberColumn(disabled=True),
            "Branding": st.column_config.TextColumn(disabled=True)
        },
        use_container_width=True,
        hide_index=True
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
            st.text_area(f"Page {row['Page Number']}", prompt, height=180)

        # --- Consolidated Download Section ---
        st.markdown("### 📥 Export Section")
        
        # Popover acting as a single button with options
        with st.popover("Download Visual Prompts as..."):
            # Excel
            xl_bio = BytesIO()
            with pd.ExcelWriter(xl_bio, engine='openpyxl') as writer:
                pd.DataFrame({"Visual Prompts": all_prompts}).to_excel(writer, index=False)
            st.download_button("Excel (.xlsx)", data=xl_bio.getvalue(), file_name="blueprint.xlsx", use_container_width=True)
            
            # CSV
            st.download_button("CSV (.csv)", data="\n\n".join(all_prompts), file_name="blueprint.csv", use_container_width=True)
            
            # Text
            st.download_button("Text (.txt)", data="\n\n".join(all_prompts), file_name="blueprint.txt", use_container_width=True)
            
            # Word
            doc = Document()
            doc.add_heading(f"Blueprint: {topic}", 0)
            for p in all_prompts:
                doc.add_paragraph(p)
                doc.add_page_break()
            word_bio = BytesIO()
            doc.save(word_bio)
            st.download_button("Word (.docx)", data=word_bio.getvalue(), file_name="blueprint.docx", use_container_width=True)
