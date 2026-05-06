import streamlit as st
import pandas as pd
from io import BytesIO
from docx import Document
import random

# --- 1. UI Styling ---
st.set_page_config(page_title="Coloring Book Architect", layout="wide")

st.markdown("""
    <style>
    [data-testid="stAppViewContainer"] { background-color: #006994; }
    .stMarkdown, p, h1, h2, h3, span, label { color: white !important; }
    .main-title { text-align: center; font-size: 2.5rem; font-weight: bold; padding-bottom: 30px; }
    [data-testid="stDataEditor"] div[role="gridcell"] > div {
        white-space: normal !important;
        word-break: break-word !important;
        line-height: 1.4 !important;
    }
    .stDataEditor { background-color: white; border-radius: 8px; }
    </style>
    <div class="main-title">🎨 The LearnAi: Coloring Book Architect</div>
    """, unsafe_allow_html=True)

# --- 2. Fixed Unique Header Logic ---
def get_unique_header(page_num, topic, age_group):
    """Generates unique instructions by mixing components dynamically."""
    is_junior = "6-9" in age_group
    
    if is_junior:
        actions = ["Explore the science of", "Observe the history of", "Analyze the structure of", "Imagine a future with", "Study the details of"]
        details = ["intricate patterns", "historical significance", "unique geometric shapes", "neon-ready outlines", "complex storytelling"]
        contexts = ["Focus on precision.", "Use an authentic palette.", "How would this look in 100 years?", "Add artistic flair."]
    else:
        actions = ["Look at this happy", "Color the friendly", "Find the big", "Trace the lines of the", "Enjoy coloring this"]
        details = ["thick lines", "simple shapes", "smiling face", "bright spaces", "cheerful details"]
        contexts = ["Use bright colors!", "Stay inside the big lines.", "Draw a sun nearby!", "Add some polka dots!"]

    # Use page_num to ensure variety across pages
    # We use a simple combination logic to guarantee uniqueness without repetition for many pages
    act = actions[page_num % len(actions)]
    det = details[(page_num // len(actions)) % len(details)]
    ctx = contexts[(page_num // (len(actions) * len(details))) % len(contexts)]
    
    return f"{act} {topic}. It features {det}. {ctx}"

# --- 3. Input Section ---
with st.container():
    r1_c1, r1_c2 = st.columns(2)
    with r1_c1:
        topic = st.text_input("Book Topic", placeholder="e.g. Space Adventures")
    with r1_c2:
        page_count = st.number_input("Total Pages", min_value=1, value=5)
    
    r2_c1, r2_c2 = st.columns(2)
    with r2_c1:
        age_group = st.selectbox("Age Group", options=["3-5 years (Explorer)", "6-9 years (Junior Creator)"], index=0)
    with r2_c2:
        style_list = st.multiselect("Styles", 
            ["Bold black line art", "Pure white background", "No shading", "High-contrast outlines", "Whimsical details"],
            default=["Bold black line art"])

# --- 4. Logic & State Management ---
if 'df' not in st.session_state:
    st.session_state.df = None

if st.button("Generate Blueprint"):
    if not topic or not style_list:
        st.error("Please fill in all fields.")
    else:
        rows = []
        for i in range(1, page_count + 1):
            rows.append({
                "Page Number": i,
                "Header Content": f"{get_unique_header(i, topic, age_group)} [Designed by The LearnAi]",
                "Orientation": "Portrait" if i % 2 != 0 else "Landscape"
            })
        st.session_state.df = pd.DataFrame(rows)

# --- 5. Display Section ---
if st.session_state.df is not None:
    st.subheader("Interactive Blueprint Editor")
    
    # We store the edited dataframe back into session state
    updated_df = st.data_editor(
        st.session_state.df,
        column_config={
            "Orientation": st.column_config.SelectboxColumn("Orientation", options=["Portrait", "Landscape"]),
            "Page Number": st.column_config.NumberColumn(disabled=True),
            "Header Content": st.column_config.TextColumn("Header Content (Editable)", width="large")
        },
        use_container_width=True,
        hide_index=True,
        key="editor"
    )

    st.markdown("---")
    gen_p = st.radio("Generate visual prompts?", ["No", "Yes"], horizontal=True)

    if gen_p == "Yes":
        all_prompts = []
        combined_styles = ", ".join(style_list)
        
        for _, row in updated_df.iterrows():
            prompt = (
                f"Page {row['Page Number']}:\n"
                f"Coloring page in {row['Orientation']} orientation.\n"
                f"Subject: {topic}. {row['Header Content']}\n"
                f"Style: {combined_styles}\n"
                f"Footer: Designed by The LearnAi"
            )
            all_prompts.append(prompt)
            st.code(prompt, language="text")

        # Export Logic
        doc = Document()
        for p in all_prompts:
            doc.add_paragraph(p)
            doc.add_page_break()
        
        word_bio = BytesIO()
        doc.save(word_bio)
        st.download_button("Download Word (.docx)", data=word_bio.getvalue(), file_name="blueprint.docx")
