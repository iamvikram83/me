import streamlit as st
import anthropic
import json
import csv
import io

# ── PAGE CONFIG ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="LearnAi Coloring Book Architect",
    page_icon="🎨",
    layout="wide",
)

# ── STYLES ─────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
[data-testid="stAppViewContainer"] { background-color: #0a0a0a; }
[data-testid="stHeader"] { background: transparent; }
section[data-testid="stSidebar"] { background: #111; }

h1, h2, h3, h4, p, label, span, div, li { color: #f0f0f0 !important; }
.stMarkdown p { color: #c8c8c8 !important; }

/* Cards */
.card {
    background: #1a1a1a;
    border: 1px solid #2a2a2a;
    border-radius: 12px;
    padding: 1.4rem 1.6rem;
    margin-bottom: 1rem;
}

/* Blueprint table */
.bp-table { width: 100%; border-collapse: collapse; font-size: 13px; }
.bp-table th {
    background: #1e1e1e;
    color: #888 !important;
    font-weight: 500;
    font-size: 11px;
    text-transform: uppercase;
    letter-spacing: .06em;
    padding: 10px 12px;
    border-bottom: 1px solid #2a2a2a;
    text-align: left;
}
.bp-table td {
    padding: 12px;
    border-bottom: 1px solid #1e1e1e;
    vertical-align: top;
    color: #d0d0d0 !important;
}
.bp-table tr:last-child td { border-bottom: none; }
.bp-table tr:hover td { background: #161616; }

/* Badges */
.badge-portrait {
    display:inline-block; padding:3px 10px;
    background:#0d2d4a; color:#60a5fa !important;
    border:1px solid #1e4976; border-radius:20px; font-size:11px; font-weight:500;
}
.badge-landscape {
    display:inline-block; padding:3px 10px;
    background:#0d3321; color:#4ade80 !important;
    border:1px solid #1a5c38; border-radius:20px; font-size:11px; font-weight:500;
}
.badge-cover {
    display:inline-block; padding:2px 8px;
    background:#3b2500; color:#fb923c !important;
    border-radius:10px; font-size:10px; font-weight:500; margin-left:6px;
}
.badge-gallery {
    display:inline-block; padding:2px 8px;
    background:#2d1b4e; color:#c084fc !important;
    border-radius:10px; font-size:10px; font-weight:500; margin-left:6px;
}
.page-num {
    display:inline-flex; align-items:center; justify-content:center;
    width:28px; height:28px; border-radius:50%;
    background:#222; color:#f0f0f0 !important;
    font-size:12px; font-weight:500;
}

/* Prompt code block */
.prompt-block {
    background:#0d0d0d; border:1px solid #2a2a2a; border-radius:8px;
    padding:10px 12px; font-family:monospace; font-size:11px;
    color:#a8d8a8 !important; line-height:1.7; white-space:pre-wrap;
    word-break:break-word;
}

/* Stat cards */
.stat-grid { display:grid; grid-template-columns:repeat(3,1fr); gap:12px; margin-bottom:1.2rem; }
.stat-card { background:#1a1a1a; border:1px solid #2a2a2a; border-radius:10px; padding:14px 18px; }
.stat-label { font-size:11px; color:#666 !important; margin-bottom:4px; }
.stat-val { font-size:22px; font-weight:500; color:#f0f0f0 !important; }

/* Progress */
.progress-label { font-size:13px; color:#888 !important; margin-bottom:6px; }
</style>
""", unsafe_allow_html=True)


# ── SESSION STATE ──────────────────────────────────────────────────────────────
for key, default in [
    ("step", 1),
    ("blueprint", []),
    ("topic", ""),
    ("age_group", "3-5"),
    ("page_count", 5),
    ("generating", False),
]:
    if key not in st.session_state:
        st.session_state[key] = default


# ── HELPERS ────────────────────────────────────────────────────────────────────
def age_style_name(age_group: str) -> str:
    return "Explorer" if age_group == "3-5" else "Junior Creator"


def build_system_prompt(age_group: str) -> str:
    if age_group == "3-5":
        style_guide = """
STYLE: Explorer (Ages 3-5)
- Simple, short sentences. Big encouragement. Repetition is good.
- Header example: "Meet Leo the Lion! Color his big mane bright orange. You are doing great!"
- Image prompts: single subject, large shapes, very thick outlines, minimal background detail.
- Orientation rule: almost always PORTRAIT unless the scene is truly wide (e.g., a train).
"""
    else:
        style_guide = """
STYLE: Junior Creator (Ages 6-9)
- Fun facts + creative freedom. Adventurous tone. Specific color suggestions.
- Header example: "Did you know lions roar so loud it's heard 5 miles away? Use golden fur and deep purple shadows!"
- Image prompts: richer scene, some background detail, medium-thick outlines, interesting composition.
- Orientation rule: use LANDSCAPE for panoramic/multi-character scenes, PORTRAIT otherwise.
"""
    return f"""You are an expert children's EdTech content creator specialising in branded kids' coloring books for "The LearnAi".

{style_guide}

ORIENTATION RULES (strictly follow):
- PORTRAIT (8.5×11 in): single character, vertical motion (rocket, giraffe), tall subjects (tree, skyscraper).
- LANDSCAPE (11×8.5 in): horizontal motion (train, car race), panoramic scenes (ocean, savanna), 2+ characters side by side.

BRANDING: Every page must include footer text: "Designed by The LearnAi"

OUTPUT FORMAT: Respond with a single valid JSON array. No markdown fences, no extra text.
Each element is an object with these exact keys:
  page        – integer (0 = cover, 999 = gallery, else sequential)
  type        – "cover" | "content" | "gallery"
  title       – 10-15 word page title / coloring instruction (for content pages)
  header      – 15-20 word engaging header matching the age style
  orientation – "PORTRAIT" or "LANDSCAPE"
  image_prompt – detailed image generation prompt (60-90 words) including: subject, background, style (clean black line art, coloring page, white background, bold outlines, no shading, no color), composition, and "Designed by The LearnAi" footer note
  branding    – always "Designed by The LearnAi"
"""


def build_user_prompt(topic: str, page_count: int, age_group: str) -> str:
    return f"""Create a complete coloring book blueprint.

Topic: {topic}
Age group: {age_group} years ({age_style_name(age_group)} style)
Total content pages: {page_count} (plus 1 cover page + 1 gallery page = {page_count + 2} entries total)

Page structure:
- Entry 0: Cover page (type="cover") — vibrant description for a full-colour cover, "The LearnAi Presents: [Book Title]", no coloring needed.
- Entries 1 to {page_count}: Content pages (type="content") — sequential coloring pages on the topic.
- Entry {page_count + 1}: Gallery page (type="gallery") — colorful "My Gallery" page, tile layout showing all {page_count} completed pages, include feedback email: learnaiwithvs@gmail.com.

Return JSON array with {page_count + 2} objects. Strictly follow orientation rules based on each scene's content."""


def orientation_badge(orient: str) -> str:
    cls = "badge-portrait" if orient == "PORTRAIT" else "badge-landscape"
    icon = "↕" if orient == "PORTRAIT" else "↔"
    return f'<span class="{cls}">{icon} {orient}</span>'


def page_label(row: dict) -> str:
    if row["type"] == "cover":
        return f'<span class="page-num">C</span><span class="badge-cover">COVER</span>'
    if row["type"] == "gallery":
        return f'<span class="page-num">G</span><span class="badge-gallery">GALLERY</span>'
    return f'<span class="page-num">{row["page"]}</span>'


def generate_blueprint(topic: str, page_count: int, age_group: str, api_key: str) -> list:
    client = anthropic.Anthropic(api_key=api_key)
    system = build_system_prompt(age_group)
    user = build_user_prompt(topic, page_count, age_group)

    message = client.messages.create(
        model="claude-opus-4-5",
        max_tokens=4096,
        system=system,
        messages=[{"role": "user", "content": user}],
    )

    raw = message.content[0].text.strip()
    # Strip accidental markdown fences
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    raw = raw.strip()
    return json.loads(raw)


def regenerate_prompt(row: dict, new_orientation: str, api_key: str) -> str:
    """Ask Claude to rewrite just the image_prompt for a new orientation."""
    client = anthropic.Anthropic(api_key=api_key)
    msg = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=300,
        messages=[{
            "role": "user",
            "content": (
                f"Rewrite this coloring-page image prompt for {new_orientation} orientation "
                f"({('8.5×11 in portrait' if new_orientation == 'PORTRAIT' else '11×8.5 in landscape')}).\n\n"
                f"Original prompt: {row['image_prompt']}\n\n"
                "Return ONLY the new prompt text, no extra commentary."
            )
        }]
    )
    return msg.content[0].text.strip()


def blueprint_to_csv(blueprint: list) -> str:
    output = io.StringIO()
    fields = ["page", "type", "title", "header", "orientation", "image_prompt", "branding"]
    writer = csv.DictWriter(output, fieldnames=fields, extrasaction="ignore")
    writer.writeheader()
    writer.writerows(blueprint)
    return output.getvalue()


# ── SIDEBAR ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 🎨 LearnAi Architect")
    st.markdown("---")
    api_key = st.text_input("Anthropic API Key", type="password", placeholder="sk-ant-...")
    st.markdown("---")
    st.markdown("**How it works**")
    st.markdown("""
1. Enter your book details  
2. AI generates full blueprint  
3. Edit orientations live  
4. Download as CSV
""")
    if st.session_state.blueprint:
        st.markdown("---")
        st.markdown("**Current book**")
        bp = st.session_state.blueprint
        content_pages = [r for r in bp if r["type"] == "content"]
        portraits = sum(1 for r in content_pages if r["orientation"] == "PORTRAIT")
        landscapes = len(content_pages) - portraits
        st.markdown(f"📖 **{st.session_state.topic}**")
        st.markdown(f"👶 Ages {st.session_state.age_group}")
        st.markdown(f"↕ Portrait: {portraits} &nbsp; ↔ Landscape: {landscapes}")


# ── MAIN ───────────────────────────────────────────────────────────────────────
st.markdown("<h1 style='text-align:center; margin-bottom:.25rem;'>🎨 LearnAi Coloring Book Architect</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center; color:#666;'>Generate a professional kids coloring book blueprint powered by AI</p>", unsafe_allow_html=True)
st.markdown("---")


# ═══════════════════════════════════════════════════════
# STEP 1 — SETUP FORM
# ═══════════════════════════════════════════════════════
if st.session_state.step == 1:
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown("#### Book details")

        topic = st.text_input("Book topic", placeholder="e.g. Wild Animals, Good Habits, Space Adventure...")

        c1, c2 = st.columns(2)
        with c1:
            page_count = st.number_input("Content pages", min_value=2, max_value=20, value=5,
                                          help="Cover + Gallery pages are added automatically")
        with c2:
            age_group = st.selectbox("Target age group", options=["3-5", "6-9"],
                                      format_func=lambda x: f"Ages {x} — {'Explorer' if x == '3-5' else 'Junior Creator'}")

        st.markdown("</div>", unsafe_allow_html=True)

        if not api_key:
            st.warning("⚠️ Enter your Anthropic API key in the sidebar to continue.")

        if st.button("✨ Generate Blueprint", type="primary", disabled=not (topic and api_key)):
            st.session_state.topic = topic
            st.session_state.page_count = page_count
            st.session_state.age_group = age_group

            with st.spinner(""):
                progress = st.progress(0, text="Connecting to AI…")
                try:
                    progress.progress(20, text="Analysing topic…")
                    blueprint = generate_blueprint(topic, page_count, age_group, api_key)
                    progress.progress(90, text="Building blueprint…")
                    st.session_state.blueprint = blueprint
                    progress.progress(100, text="Done!")
                    st.session_state.step = 2
                    st.rerun()
                except Exception as e:
                    st.error(f"Generation failed: {e}")


# ═══════════════════════════════════════════════════════
# STEP 2 — BLUEPRINT TABLE
# ═══════════════════════════════════════════════════════
elif st.session_state.step == 2:
    blueprint = st.session_state.blueprint

    # ── Stats row
    content_pages = [r for r in blueprint if r["type"] == "content"]
    portraits = sum(1 for r in content_pages if r["orientation"] == "PORTRAIT")
    landscapes = len(content_pages) - portraits
    total = len(blueprint)

    st.markdown(f"""
    <div class="stat-grid">
      <div class="stat-card"><div class="stat-label">Total entries</div><div class="stat-val">{total}</div></div>
      <div class="stat-card"><div class="stat-label">↕ Portrait</div><div class="stat-val">{portraits}</div></div>
      <div class="stat-card"><div class="stat-label">↔ Landscape</div><div class="stat-val">{landscapes}</div></div>
    </div>
    """, unsafe_allow_html=True)

    # ── Toolbar
    toolbar_l, toolbar_r = st.columns([1, 1])
    with toolbar_l:
        if st.button("⬅ New book"):
            st.session_state.step = 1
            st.session_state.blueprint = []
            st.rerun()
    with toolbar_r:
        csv_data = blueprint_to_csv(blueprint)
        st.download_button(
            "📥 Download CSV",
            data=csv_data.encode("utf-8"),
            file_name=f"learnai_{st.session_state.topic.lower().replace(' ', '_')}_blueprint.csv",
            mime="text/csv",
        )

    st.markdown("---")

    # ── Blueprint table — one expander per page
    for i, row in enumerate(blueprint):
        ptype = row.get("type", "content")
        icon = "🖼️" if ptype == "cover" else ("🖼️" if ptype == "gallery" else "📄")
        title_preview = row.get("title") or row.get("header", "")[:60]

        label = f"{icon} {'Cover' if ptype == 'cover' else ('Gallery' if ptype == 'gallery' else f'Page {row[\"page\"]}')} — {title_preview[:55]}..."

        with st.expander(label, expanded=(i == 0)):
            left, right = st.columns([1, 2])

            with left:
                st.markdown(f"**Page label:** {page_label(row)}", unsafe_allow_html=True)
                st.markdown(f"**Orientation:** {orientation_badge(row.get('orientation','PORTRAIT'))}", unsafe_allow_html=True)

                if ptype == "content":
                    new_orient = st.radio(
                        "Change orientation",
                        options=["PORTRAIT", "LANDSCAPE"],
                        index=0 if row.get("orientation") == "PORTRAIT" else 1,
                        key=f"orient_{i}",
                        horizontal=True,
                    )
                    if new_orient != row.get("orientation"):
                        if api_key:
                            with st.spinner("Rewriting prompt for new orientation…"):
                                new_prompt = regenerate_prompt(row, new_orient, api_key)
                                st.session_state.blueprint[i]["orientation"] = new_orient
                                st.session_state.blueprint[i]["image_prompt"] = new_prompt
                                st.rerun()
                        else:
                            st.session_state.blueprint[i]["orientation"] = new_orient
                            st.rerun()

                st.markdown("**Header content:**")
                new_header = st.text_area(
                    "header",
                    value=row.get("header", ""),
                    key=f"header_{i}",
                    label_visibility="collapsed",
                    height=100,
                )
                if new_header != row.get("header", ""):
                    st.session_state.blueprint[i]["header"] = new_header

            with right:
                st.markdown("**Image prompt:**")
                st.markdown(
                    f'<div class="prompt-block">{row.get("image_prompt","")}</div>',
                    unsafe_allow_html=True,
                )

                if ptype == "content":
                    st.markdown("**Page title / coloring instruction:**")
                    new_title = st.text_area(
                        "title",
                        value=row.get("title", ""),
                        key=f"title_{i}",
                        label_visibility="collapsed",
                        height=70,
                    )
                    if new_title != row.get("title", ""):
                        st.session_state.blueprint[i]["title"] = new_title

                st.markdown(f"🏷️ *{row.get('branding','')}*")
