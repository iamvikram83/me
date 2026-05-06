import streamlit as st
import pandas as pd
from io import BytesIO
from docx import Document

# --- 1. UI Styling ---
st.set_page_config(page_title="Coloring Book Architect", layout="wide")

st.markdown("""
    <style>
    [data-testid="stAppViewContainer"] { background-color: #006994; }
    .stMarkdown, p, h1, h2, h3, span, label { color: white !important; }
    .main-title { text-align: center; font-size: 2.5rem; font-weight: bold; padding-bottom: 30px; }
    .stDataEditor { background-color: white; border-radius: 8px; }
    </style>
    <div class="main-title">🎨 The LearnAi: Coloring Book Architect</div>
    """, unsafe_allow_html=True)

# --- 2. THE FIX: Guaranteed Unique Content Generator ---
def get_unique_header(page_num, topic, age_group):
    # Determine the vibe based on age
    is_junior = "6-9" in str(age_group)
    
    # We use dynamic descriptors to ensure Page 1 and Page 100 are different
    if is_junior:
        instruction = f"Detailed Activity {page_num}: Study and color the complex patterns of {topic}."
        tip = f"Tip: Use professional shading for this {topic} scene."
    else:
        instruction = f"Fun Page {page_num}: Color the big, happy {topic}!"
        tip = f"Challenge: Can you add {page_num} tiny dots inside the {topic}?"

    return f"{instruction} {tip}"

# --- 3. Input Section ---
with st.container():
    col1, col2 = st.columns(2)
    with col1:
        topic = st.text_input("Book Topic", value="Space Adventures")
    with col2:
        page_count = st.number_input("Total Pages", min_value=1, value=10)
    
    col3, col4 = st.columns(2)
    with col3:
        age_group = st.selectbox("Age Group", options=["3-5 years (Explorer)", "6-9 years (Junior Creator)"], index=0)
    with col4:
        style_list = st.multiselect("Styles", 
            ["Bold black line art", "Pure white background", "No shading"],
            default=["Bold black line art"])

# Initialize session state
if 'df' not in st.session_state:
    st.session_state.df = None

# --- 4. Generation Logic ---
if st.button("Generate Blueprint"):
    if not topic:
        st.error("Please enter a topic.")
    else:
        try:
            rows = []
            for i in range(1, page_count + 1):
                # We pass 'i' to the function to ensure the text contains the actual page number
                unique_text = get_unique_header(i, topic, age_group)
                
                rows.append({
                    "Page Number": i,
                    "Header Content": f"{unique_text} [Designed by The LearnAi]",
                    "Orientation": "Portrait" if i % 2 != 0 else "Landscape"
                })
            st.session_state.df = pd.DataFrame(rows)
            st.rerun() # Forces the UI to show the new data immediately
        except Exception as e:
            st.error(f"Logic Error: {e}")

# --- 5. Display & Export ---
if st.session_state.df is not None:
    st.subheader("Interactive Blueprint Editor")
    
    updated_df = st.data_editor(
        st.session_state.df,
        column_config={
            "Page Number": st.column_config.NumberColumn(disabled=True),
            "Header Content": st.column_config.TextColumn("Header Content", width="large")
        },
        use_container_width=True,
        hide_index=True
    )

    if st.button("Download as Word"):
        doc = Document()
        doc.add_heading(f"Coloring Book: {topic}", 0)
        for _, row in updated_df.iterrows():
            doc.add_paragraph(f"PAGE {row['Page Number']}")
            doc.add_paragraph(row['Header Content'])
            doc.add_page_break()
        
        bio = BytesIO()
        doc.save(bio)
        st.download_button("Click to Download", data=bio.getvalue(), file_name="book.docx")
