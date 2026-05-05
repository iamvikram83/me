import streamlit as st
import pandas as pd
from io import BytesIO
from docx import Document

# 1. CSS for Sea Blue Background and Horizontal Title Layout
st.markdown("""
    <style>
    [data-testid="stAppViewContainer"] {
        background-color: #006994;
    }
    .stMarkdown, p, h1, h2, h3, span, label {
        color: white !important;
    }
    .main-title {
        font-size: 2.5rem;
        font-weight: bold;
        text-align: center;
        white-space: nowrap;
        margin-bottom: 20px;
    }
    .stDataEditor {
        background-color: white;
        border-radius: 5px;
    }
    </style>
    <div class="main-title">🎨 The LearnAi: Kids' Coloring Book Architect</div>
    """, unsafe_allow_html=True)

def generate_header(i, topic, is_junior):
    """Generates unique educational/fun headers for each page."""
    if is_junior:
        facts = [
            f"Did you know {topic} can be seen from great distances?",
            f"The history of {topic} dates back hundreds of years!",
            f"Scientists study {topic} to understand our world better.",
            f"Every {topic} has a unique pattern, just like a fingerprint.",
            f"Imagine you are exploring {topic} for the first time today!"
        ]
        return f"{facts[i % len(facts)]} [Designed by The LearnAi]"
    else:
        actions = [
            f"Look at this big {topic}! Can you color it brightly?",
            f"Trace the lines of the {topic} slowly and carefully.",
            f"Use your favorite colors to make this {topic} beautiful!",
            f"How many {topic} shapes can you count on this page?",
            f"Stay inside the lines to make the {topic} pop!"
        ]
        return f"{actions[i % len(actions)]} [Designed by The LearnAi]"

def generate_visual_prompt(row, style_list, topic):
    styles = ", ".join(style_list)
    return (
        f"Page {row['Page Number']}:\n"
        f"Create a high-resolution, printable children's coloring page in {row['Orientation']} "
        f"orientation (8.5 x 11 inches).\n\n"
        f"Subject: {topic} - {row['Orientation']} composition. {row['Header Content']}\n\n"
        f"Style: {styles}\n\n"
        f"Footer Branding: {row['Branding']}"
    )

# --- UI Implementation ---
with st.container():
    col1, col2, col3 = st.columns([2, 1, 2])
    with col1:
        topic = st.text_input("Book Topic", placeholder="e.g., Space Adventures or Jungle Animals")
        page_count = st.number_input("Total Pages", min_value=1, value=1)
    with col2:
        age_group = st.selectbox("Age Group", ["3-5 years (Explorer)", "6-9 years (Junior Creator)"])
    with col3:
        style_presets = st.multiselect("Select Styles", [
            "Bold black line art", "Pure white background", "No shading", 
            "High-contrast outlines", "Whimsical patterns", "Minimalist background"
        ], placeholder="Choose one or more styles")

if 'blueprint_df' not in st.session_state:
    st.session_state.blueprint_df = None

if st.button("Generate Book Blueprint"):
    if not topic or not style_presets:
        st.error("Please enter a topic and select at least one style.")
    else:
        data = []
        is_junior = "6-9" in age_group
        for i in range(1, page_count + 1):
            orientation = "Portrait" if i % 2 != 0 else "Landscape"
            data.append({
                "Page Number": i,
                "Header Content": generate_header(i, topic, is_junior),
                "Orientation": orientation,
                "Branding": "Designed by The LearnAi"
            })
        st.session_state.blueprint_df = pd.DataFrame(data)

if st.session_state.blueprint_df is not None:
    final_df = st.data_editor(
        st.session_state.blueprint_df,
        column_config={"Orientation": st.column_config.SelectboxColumn("Orientation", options=["Portrait", "Landscape"])},
        use_container_width=True,
        key="editor"
    )
    
    st.markdown("---")
    gen_prompts = st.radio("Generate visual/image prompts?", ("No", "Yes"))

    if gen_prompts == "Yes":
        all_prompts = []
        for _, row in final_df.iterrows():
            p_text = generate_visual_prompt(row, style_presets, topic)
            all_prompts.append(p_text)
            st.text_area(f"Page {row['Page Number']}", p_text, height=200)

        # --- Export Options ---
        st.subheader("📥 Export All Prompts")
        export_col1, export_col2, export_col3 = st.columns(3)
        
        # 1. CSV
        csv = "\n\n".join(all_prompts).encode('utf-8')
        export_col1.download_button("Download CSV", data=csv, file_name="prompts.csv")
        
        # 2. Word (.docx)
        doc = Document()
        doc.add_heading(f"Coloring Book Prompts: {topic}", 0)
        for p in all_prompts:
            doc.add_paragraph(p)
            doc.add_page_break()
        bio = BytesIO()
        doc.save(bio)
        export_col2.download_button("Download Word", data=bio.getvalue(), file_name="prompts.docx")
        
        # 3. Excel
        df_prompts = pd.DataFrame({"Prompts": all_prompts})
        buffer = BytesIO()
        with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
            df_prompts.to_excel(writer, index=False)
        export_col3.download_button("Download Excel", data=buffer.getvalue(), file_name="prompts.xlsx")
