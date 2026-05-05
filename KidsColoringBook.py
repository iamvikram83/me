import streamlit as st
import pandas as pd

# Set professional page layout
st.set_page_config(page_title="The LearnAi - Coloring Book Architect", layout="wide")

def generate_content(topic, num_pages, age_group):
    """
    Logic engine to generate page-by-page blueprints based on branding rules.
    """
    data = []
    is_junior = "6-9" in age_group

    for i in range(1, num_pages + 1):
        # Decisions on orientation based on page number for variety
        orientation = "PORTRAIT" if i % 2 != 0 else "LANDSCAPE"
        
        # Age-specific copywriting logic
        if is_junior:
            header = f"Did you know {topic} has amazing details? Imagine this scene and use deep colors for shadows. [Designed by The LearnAi]"
        else:
            header = f"Here is a {topic}! Use your favorite bright colors and stay inside the lines. [Designed by The LearnAi]"
        
        # Visual prompt engineering
        prompt = f"Kids coloring book style, black and white line art, {topic}, {orientation.lower()} view, bold outlines, no shading."

        data.append({
            "Page": i,
            "Header Content": header,
            "Orientation": orientation,
            "Branding": "Designed by The LearnAi",
            "Visual Prompt": prompt
        })
    return data

# --- UI IMPLEMENTATION ---
st.title("🎨 Kids' Coloring Book Blueprint Generator")
st.markdown("### Expert EdTech Content Creator Tool | Powered by The LearnAi")

# Step 1: Gather User Inputs
with st.container():
    st.info("Please enter the book details below to generate your blueprint.")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        topic = st.text_input("Topic", placeholder="e.g., Space Exploration")
    with col2:
        pages = st.number_input("Total Pages", min_value=1, max_value=100, value=10)
    with col3:
        age_range = st.selectbox("Target Age Group", ["3-5 years (Explorer)", "6-9 years (Junior Creator)"])

# Step 2: Trigger Generation
if st.button("Generate Full Blueprint"):
    if not topic:
        st.warning("Please provide a topic to generate the content.")
    else:
        results = generate_content(topic, pages, age_range)
        df = pd.DataFrame(results)

        # Step 3: Show Overview & Cover
        st.success(f"Blueprint Generated for '{topic}'")
        st.subheader("Book Layout Overview")
        
        # Cover Page Description
        st.markdown(f"**📘 Cover Page:** High-energy, full-color illustration of {topic}. Featuring 'Designed by The LearnAi'.")

        # Display Table
        st.dataframe(df, use_container_width=True)

        # Last Page Description
        st.markdown("---")
        st.markdown(f"**🖼️ Last Page:** Colorful Gallery Page showing all {pages} images. Email: learnaiwithvs@gmail.com. [Designed by The LearnAi]")

        # Export Functionality
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="Download Blueprint as CSV",
            data=csv,
            file_name=f"{topic.replace(' ', '_')}_blueprint.csv",
            mime='text/csv',
        )
