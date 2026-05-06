import streamlit as st
import pandas as pd
from io import BytesIO
from docx import Document

# 1. UI Styling: Background, Text Wrapping, and Persistent Copy Button
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
        padding-bottom: 30px;
    }
    /* Force text wrapping in Data Editor cells */
    [data-testid="stDataEditor"] div[role="gridcell"] > div {
        white-space: normal !important;
        word-break: break-word !important;
        line-height: 1.4 !important;
    }
    /* Make the Copy to Clipboard button always visible */
    button[title="Copy to clipboard"] {
        opacity: 1 !important;
        visibility: visible !important;
    }
    .stDataEditor {
        background-color: white;
        border-radius: 8px;
    }
    </style>
    <div class="main-title">🎨 The LearnAi: Coloring Book Architect</div>
    """, unsafe_allow_html=True)

def get_unique_header(page_num, topic, age_group):
    """Dynamic content generation logic."""
    is_junior = "6-9" in age_group
    if is_junior:
        messages = [
            f"The science of {topic} is fascinating! Can you color the details accurately?",
            f"History tells us {topic} changed our world. Use colors that feel historic.",
            f"Did you know {topic} has a unique structure? Focus on the lines.",
            f"Imagine {topic} in a futuristic city. Use neon and bright shades!",
            f"Every {topic} has a story. Use art to tell what happens next."
        ]
    else:
        messages = [
            f"Look at this friendly {topic}! Use your favorite colors to fill it in.",
            f"Stay inside the thick lines of the {topic}. Great job!",
            f"What color makes a {topic} happy? You decide the best look!",
            f"Color the {topic} first, then draw a smiley face next to it.",
            f"How many {topic} shapes can you see? Color each one differently!"
        ]
    return messages[page_num % len(messages)]

# --- Input Section ---
with st.container():
    r1_c1, r1_c2 = st.columns(2)
    with r1_c1:
        topic = st.text_input("Book Topic", placeholder="e.g. Space Adventures", help="Main theme of the book.")
    with r1_c2:
        page_count = st.number_input("Total Pages", min_value=1, value=1, help="Number of pages to generate.")
    
    r2_c1, r2_c2 = st.columns(2)
    with r2_c1:
        age_group = st.selectbox("Age Group", options=["3-5 years (Explorer)", "6-9 years (Junior Creator)"], 
                                 index=None, placeholder="Please select an age group...",
                                 help="Required: Determines the tone of instructions.")
    with r2_c2:
        style_list = st.multiselect("Styles", 
            ["Bold black line art", "Pure white background", "No shading", "High-contrast outlines", "Whimsical details"],
            placeholder="Select artistic styles...", help="Select styles for the AI prompt.")

    ref_image = st.file_uploader("Upload reference to review (Optional)", type=["png", "jpg", "jpeg"], 
                                 help="Optional: Upload an image for style and placement review.")

if 'df' not in st.session_state:
    st.session_state.df = None

if st.button("Generate Blueprint"):
    if not topic or not style_list or age_group is None:
        st.error("Please fill in the Topic, select Styles, and choose an Age Group.")
    else:
        rows = []
        for i in range(1, page_count + 1):
            rows.append({
                "Page Number": i,
                "Header Content": f"{get_unique_header(i, topic, age_group)} [Designed by The LearnAi]",
                "Orientation": "Portrait" if i % 2 != 0 else "Landscape"
            })
        st.session_state.df = pd.DataFrame(rows)

# --- Display Section ---
if st.session_state.df is not None:
    st.subheader("Interactive Blueprint Editor")
    
    updated_df = st.data_editor(
        st.session_state.df,
        column_config={
            "Orientation": st.column_config.SelectboxColumn("Orientation", options=["Portrait", "Landscape"]),
            "Page Number": st.column_config.NumberColumn(disabled=True),
            "Header Content": st.column_config.TextColumn("Header Content (Editable)", width="large")
        },
        use_container_width=True,
        hide_index=True
    )

    st.markdown("---")
    gen_p = st.radio("Would you like to generate visual prompts based upon your book blue print?", ["No", "Yes"], horizontal=True)

    if gen_p == "Yes":
        all_prompts = []
        combined_styles = ", ".join(style_list)
        ref_context = " (Match the uploaded reference style and placement)" if ref_image else ""
        
        for _, row in updated_df.iterrows():
            prompt = (
                f"Page {row['Page Number']}:\n"
                f"Create a high-resolution, printable children's coloring page in {row['Orientation']} "
                f"orientation (8.5 x 11 inches).\n\n"
                f"Subject: {topic}. {row['Header Content']}\n\n"
                f"Style: {combined_styles}{ref_context}\n\n"
                f"Footer Branding: Designed by The LearnAi"
            )
            all_prompts.append(prompt)
            
            # Simplified Label: Page X
            st.markdown(f"### Page {row['Page Number']}")
            # Persistent copy button via CSS above
            st.code(prompt, language="text")
            st.markdown("---")

        # --- Export Section ---
        st.markdown("### 📥 Export Section")
        with st.popover("Export Visual Prompts as"):
            xl_bio = BytesIO()
            with pd.ExcelWriter(xl_bio, engine='openpyxl') as writer:
                pd.DataFrame({"Visual Prompts": all_prompts}).to_excel(writer, index=False)
            st.download_button("Excel (.xlsx)", data=xl_bio.getvalue(), file_name="blueprint.xlsx", use_container_width=True)
            st.download_button("CSV (.csv)", data="\n\n".join(all_prompts), file_name="blueprint.csv", use_container_width=True)
            st.download_button("Text (.txt)", data="\n\n".join(all_prompts), file_name="blueprint.txt", use_container_width=True)
            
            doc = Document()
            doc.add_heading(f"Blueprint: {topic}", 0)
            for p in all_prompts:
                doc.add_paragraph(p)
                doc.add_page_break()
            word_bio = BytesIO()
            doc.save(word_bio)
            st.download_button("Word (.docx)", data=word_bio.getvalue(), file_name="blueprint.docx", use_container_width=True)
