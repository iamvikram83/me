import streamlit as st
import pandas as pd
from io import BytesIO
from docx import Document

# 1. UI Styling and Persistent Copy Button
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
    /* Persistent Copy Button */
    button[title="Copy to clipboard"] {
        opacity: 1 !important;
        visibility: visible !important;
    }
    /* Text Wrapping in Table */
    [data-testid="stDataEditor"] div[role="gridcell"] > div {
        white-space: normal !important;
        word-break: break-word !important;
    }
    .stDataEditor {
        background-color: white;
        border-radius: 8px;
    }
    </style>
    <div class="main-title">🎨 The LearnAi: Coloring Book Architect</div>
    """, unsafe_allow_html=True)

# 2. Sidebar for API Validation (The "Signed In" Logic)
with st.sidebar:
    st.header("Settings")
    api_key = st.text_input("Enter Google AI Studio API Key", type="password", 
                             help="The 'Generate in AI Studio' button will only appear if this is provided.")
    is_authenticated = len(api_key) > 10 # Basic check for key presence

def get_unique_header(page_num, topic, age_group):
    is_junior = "6-9" in age_group
    messages = [f"Explore {topic}!", f"The history of {topic} is grand.", f"Patterns in {topic}.", f"Future {topic}!", f"The story of {topic}."]
    if not is_junior:
        messages = [f"Happy {topic}!", f"Inside the lines of {topic}.", f"Your {topic} color.", f"Friend for {topic}.", f"Color the {topic}!"]
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
        age_group = st.selectbox("Age Group", options=["3-5 years (Explorer)", "6-9 years (Junior Creator)"], index=None)
    with r2_c2:
        style_list = st.multiselect("Styles", ["Bold black line art", "Pure white background", "No shading", "High-contrast outlines"])

    ref_image = st.file_uploader("Upload reference (Optional)", type=["png", "jpg", "jpeg"])

if 'df' not in st.session_state:
    st.session_state.df = None

if st.button("Generate Blueprint"):
    if not topic or not style_list or age_group is None:
        st.error("Please fill in all mandatory fields.")
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
    updated_df = st.data_editor(st.session_state.df, use_container_width=True, hide_index=True)
    st.markdown("---")

    if st.radio("Generate visual prompts based on blueprint?", ["No", "Yes"], horizontal=True) == "Yes":
        combined_styles = ", ".join(style_list)
        ref_context = " (Match reference style)" if ref_image else ""
        
        for _, row in updated_df.iterrows():
            prompt = (
                f"Page {row['Page Number']}:\n"
                f"Subject: {topic}. {row['Header Content']}\n"
                f"Orientation: {row['Orientation']}\n"
                f"Style: {combined_styles}{ref_context}"
            )
            
            st.markdown(f"### Page {row['Page Number']}")
            st.code(prompt, language="text")
            
            # --- IMAGE GENERATION OPTIONS ---
            c1, c2 = st.columns(2)
            
            with c1:
                # Conditional Logic: Only shows if API key is present
                if is_authenticated:
                    encoded_prompt = prompt.replace(" ", "%20")
                    st.link_button("🎨 Generate in Google AI Studio", 
                                   url=f"https://aistudio.google.com/app/prompts/new?prompt={encoded_prompt}")
                else:
                    st.caption("🔑 Link API Key in sidebar to enable AI Studio.")

            with c2:
                # Fixed Second Option: Clear interaction
                if st.button(f"Generate via Nano Banana", key=f"gen_{row['Page Number']}"):
                    st.warning("Please copy the prompt above and paste it into our chat to generate the image!")

            st.markdown("---")
