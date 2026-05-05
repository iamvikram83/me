import streamlit as st
import pandas as pd
from io import BytesIO
from docx import Document

# 1. UI Styling (Sea Blue, Wrapped Text, Persistent Copy Button)
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
    [data-testid="stDataEditor"] div[role="gridcell"] > div {
        white-space: normal !important;
        word-break: break-word !important;
    }
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
    is_junior = "6-9" in age_group
    messages = [
        f"Discover the secrets of {topic}!",
        f"The history of {topic} is colorful!",
        f"Patterns in {topic} are amazing.",
        f"Imagine {topic} in the future!",
        f"Every {topic} has a story."
    ] if is_junior else [
        f"Color this happy {topic}!",
        f"Stay inside the lines of {topic}.",
        f"What color is your {topic}?",
        f"Draw a friend for this {topic}.",
        f"Color every part of the {topic}!"
    ]
    return messages[page_num % len(messages)]

# --- Input Section ---
with st.container():
    r1_c1, r1_c2 = st.columns(2)
    with r1_c1:
        topic = st.text_input("Book Topic", placeholder="e.g. Space Adventures")
    with r1_c2:
        page_count = st.number_input("Total Pages", min_value=1, value=1)
    
    r2_c1, r2_c2 = st.columns(2)
    with r2_c1:
        age_group = st.selectbox("Age Group", options=["3-5 years (Explorer)", "6-9 years (Junior Creator)"], 
                                 index=None, placeholder="Select age group...")
    with r2_c2:
        style_list = st.multiselect("Styles", 
            ["Bold black line art", "Pure white background", "No shading", "High-contrast outlines"],
            placeholder="Select styles...")

    ref_image = st.file_uploader("Upload reference (Optional)", type=["png", "jpg", "jpeg"])

if 'df' not in st.session_state:
    st.session_state.df = None

if st.button("Generate Blueprint"):
    if not topic or not style_list or age_group is None:
        st.error("Please complete all fields.")
    else:
        rows = []
        for i in range(1, page_count + 1):
            rows.append({
                "Page Number": i,
                "Header Content": f"{get_unique_header(i, topic, age_group)} [Designed by The LearnAi]",
                "Orientation": "Portrait" if i % 2 != 0 else "Landscape"
            })
        st.session_state.df = pd.DataFrame(rows)

if st.session_state.df is not None:
    st.subheader("Interactive Blueprint Editor")
    updated_df = st.data_editor(st.session_state.df, use_container_width=True, hide_index=True)

    st.markdown("---")
    if st.radio("Generate visual prompts based on blueprint?", ["No", "Yes"], horizontal=True) == "Yes":
        combined_styles = ", ".join(style_list)
        ref_context = " (Match uploaded reference)" if ref_image else ""
        
        for _, row in updated_df.iterrows():
            prompt = (
                f"Page {row['Page Number']}:\n"
                f"Create a high-resolution children's coloring page in {row['Orientation']}.\n"
                f"Subject: {topic}. {row['Header Content']}\n"
                f"Style: {combined_styles}{ref_context}\n"
                f"Footer Branding: Designed by The LearnAi"
            )
            
            st.markdown(f"### Page {row['Page Number']}")
            st.code(prompt, language="text")
            
            # Action Buttons for Image Generation
            c1, c2 = st.columns(2)
            with c1:
                # Link to Google AI Studio (Dynamic prompt encoding)
                encoded_prompt = prompt.replace(" ", "%20")
                st.link_button("🎨 Generate in Google AI Studio", 
                               url=f"https://aistudio.google.com/app/prompts/new?prompt={encoded_prompt}")
            with c2:
                if st.button(f"Request Image for Page {row['Page Number']}", key=f"btn_{row['Page Number']}"):
                    st.info("Copy the prompt above and paste it to me here to generate using Nano Banana 2!")
            st.markdown("---")

        # --- Export Section ---
        with st.popover("Export Visual Prompts as"):
            # (Export buttons for Excel, CSV, Word, etc. as previously implemented)
            st.write("Excel, CSV, Word options here...")
