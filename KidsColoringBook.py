import streamlit as st
import pandas as pd
from io import BytesIO
from docx import Document

# 1. UI Styling: Background, Wrapped Table Text, and Title
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
        padding-bottom: 30px;
    }
    /* Force text wrapping in data editor cells */
    [data-testid="stTable"] td, .stDataEditor div[role="gridcell"] {
        white-space: normal !important;
        word-wrap: break-word !important;
    }
    .stDataEditor {
        background-color: white;
        border-radius: 8px;
    }
    </style>
    <div class="main-title">🎨 The LearnAi: Coloring Book Architect</div>
    """, unsafe_allow_html=True)

def get_unique_header(page_num, topic, age_group):
    """Dynamic header logic for unique educational content."""
    is_junior = "6-9" in age_group
    if is_junior:
        messages = [
            f"The science of {topic} is full of mystery! Can you color the details accurately?",
            f"History tells us that {topic} changed our world. Use colors that feel historic.",
            f"Did you know {topic} has a unique structure? Focus on the bold lines here.",
            f"Imagine {topic} in a futuristic city. Use neon and bright shades!",
            f"Every {topic} has a story. Use your art to tell what happens next."
        ]
    else:
        messages = [
            f"Look at this friendly {topic}! Use your favorite colors to fill it in.",
            f"Stay inside the thick lines of the {topic}. You are doing a great job!",
            f"What color makes a {topic} happy? You decide the best look!",
            f"Color the {topic} first, then draw a smiley face next to it.",
            f"How many {topic} shapes can you see? Color each one differently!"
        ]
    return messages[page_num % len(messages)]

# --- Input Section (2 columns per row) ---
with st.container():
    r1_c1, r1_c2 = st.columns(2)
    with r1_c1:
        topic = st.text_input("Book Topic", placeholder="e.g. Space Adventures", 
                              help="Enter the main theme of your coloring book.")
    with r1_c2:
        page_count = st.number_input("Total Pages", min_value=1, value=1, 
                                     help="How many unique coloring pages do you need?")
    
    r2_c1, r2_c2 = st.columns(2)
    with r2_c1:
        age_group = st.selectbox("Age Group", ["3-5 years (Explorer)", "6-9 years (Junior Creator)"],
                                 help="This changes the tone and difficulty of the instructions.")
    with r2_c2:
        style_list = st.multiselect("Styles", 
            ["Bold black line art", "Pure white background", "No shading", "High-contrast outlines", "Whimsical details"],
            placeholder="Select artistic styles...", help="These styles will be added to the image prompts.")

if 'df' not in st.session_state:
    st.session_state.df = None

if st.button("Generate Blueprint", help="Click to create the blueprint table."):
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
    
    # Text wrapping is handled via CSS; index is hidden
    updated_df = st.data_editor(
        st.session_state.df,
        column_config={
            "Orientation": st.column_config.SelectboxColumn("Orientation", options=["Portrait", "Landscape"]),
            "Page Number": st.column_config.NumberColumn(disabled=True),
            "Branding": st.column_config.TextColumn(disabled=True),
            "Header Content": st.column_config.TextColumn(width="large")
        },
        use_container_width=True,
        hide_index=True
    )

    st.markdown("---")
    # Updated label as requested
    gen_p = st.radio("Would you like to generate visual prompts based upon your book blue print?", ["No", "Yes"], horizontal=True)

    if gen_p == "Yes":
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
            # Use st.text_area for built-in copy functionality
            st.text_area(f"Page {row['Page Number']} (Click icon in top right to copy)", prompt, height=200)

        # --- Updated Export Section ---
        st.markdown("### 📥 Export Section")
        
        with st.popover("Export Visual Prompts as"):
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
