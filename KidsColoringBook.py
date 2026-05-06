import streamlit as st
import pandas as pd
from io import BytesIO
from docx import Document

# ... (Keep your UI Styling CSS here) ...

def get_unique_header(page_num, topic, age_group):
    """
    Generates a unique string for every page by incorporating 
    the page number directly into the text.
    """
    is_junior = "6-9" in age_group
    
    # 1. Create a pool of varied sentence starters
    if is_junior:
        starters = [
            f"On this page {page_num}, explore the scientific details of {topic}.",
            f"This is scene number {page_num}: focus on the historical side of {topic}.",
            f"For page {page_num}, visualize a technical blueprint of {topic}.",
            f"In this {page_num}th illustration, imagine {topic} in a new world.",
            f"Detail number {page_num} involves looking closely at {topic}'s structure."
        ]
    else:
        starters = [
            f"Here is a big {topic} for page {page_num}! Color it bright.",
            f"Page {page_num} shows a friendly {topic}. Use your favorite color.",
            f"Can you find the hidden shapes in this {topic} on page {page_num}?",
            f"Let's color this {topic} together for page {page_num}!",
            f"Look at how happy this {topic} is on page {page_num}!"
        ]
    
    # 2. Add a unique secondary instruction based on page number to ensure 100% uniqueness
    # Even if the starter repeats, the 'Bonus Task' will be unique because it uses the number
    bonus_tasks = [
        f"Draw {page_num} small stars in the background.",
        f"Use at least {page_num + 1} different colors here.",
        f"Circle the biggest part of the {topic} on this page.",
        f"Add a unique pattern to the corner of page {page_num}.",
        f"Sign your name at the bottom of this {page_num}th page."
    ]
    
    main_msg = starters[page_num % len(starters)]
    extra_task = bonus_tasks[page_num % len(bonus_tasks)]
    
    return f"{main_msg} {extra_task}"

# --- Logic for the Generate Button ---
if st.button("Generate Blueprint"):
    if not topic or not style_list or age_group is None:
        st.error("Please fill in all fields.")
    else:
        rows = []
        for i in range(1, page_count + 1):
            # i is the page number passed to the function
            unique_text = get_unique_header(i, topic, age_group)
            rows.append({
                "Page Number": i,
                "Header Content": f"{unique_text} [Designed by The LearnAi]",
                "Orientation": "Portrait" if i % 2 != 0 else "Landscape"
            })
        st.session_state.df = pd.DataFrame(rows)

# ... (Keep the rest of your Display and Export Section) ...
