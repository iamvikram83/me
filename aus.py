import streamlit as st

# Page configuration
st.set_page_config(page_title="Vikramjit Singh | Complete Portfolio", layout="wide")

# --- HEADER SECTION ---
st.title("Vikramjit Singh")
st.subheader("Software Delivery Leader | EdTech & SaaS Platforms | Agile Programs")
st.markdown("📍 Hyderabad, India (Open to Relocation: Australia) | 📞 (+91) 9781381213")
st.markdown("✉️ kuwar.vikram@gmail.com | [LinkedIn Profile](https://www.linkedin.com/in/vsasr)")
st.write("---")

# --- PROFESSIONAL SUMMARY ---
st.header("Professional Summary")
st.write("""
Delivery-focused technology leader with 18+ years of experience managing software programs across Agile environments, with strong exposure to Australian clients and business expectations.

Experienced in delivering end-to-end SaaS and digital platforms, working closely with product teams, stakeholders, and engineering functions to ensure practical, outcome-driven delivery. Known for improving delivery reliability, strengthening team accountability, and maintaining clear communication across distributed teams.

Brings a strong understanding of working with Australian organisations, including stakeholder engagement, transparency in reporting, and accountability for delivery outcomes.
""")

# --- WHY I'M A STRONG FIT FOR AUSTRALIAN EMPLOYERS ---
st.header("Why I'm a Strong Fit for Australian Employers")
col1, col2 = st.columns(2)
with col1:
    st.subheader("Australian Domain & Workplace")
    st.write("**Domain Experience**")
    st.write("Delivered RTO/VET software for clients including Truly Imagine, Sydney School of Business and Technology, Total Synergy Concepts and Dream Net Software covering AVETMISS, CRICOS, VFH/VSL compliance frameworks.")
    st.write("**Workplace Alignment**") 
    st.write("Worked directly with Australian-based product teams (Truly Imagine Pty Ltd, Sydney School of Business & Technology), demonstrating collaboration, accountability, and clear communication.")
with col2:
    st.subheader("Delivery & Improvement")
    st.write("**Agile Excellence**") 
    st.write("18+ years managing Agile/Scrum teams with 95%+ on-time delivery, 30% reduction in sprint carry-over, and 35% faster client onboarding.")
    st.write("**Mindset**") 
    st.write("Certified Lean Six Sigma practitioner with a track record of driving process improvement and reducing defect rates.")

# --- CORE COMPETENCIES ---
st.header("Core Competencies")
c1, c2, c3 = st.columns(3)
with c1:
    st.write("**Methodologies:** Agile, Scrum, Kanban, Lean Six Sigma, Waterfall, SDLC")
    st.write("**Project Tools:** Jira, Confluence, Asana, Trello, Monday.com, Teamwork, Zendesk")
    st.write("**Agile Practices:** Sprint planning, backlog grooming, daily stand-ups, retrospectives, velocity tracking, Definition of Done, user stories, OKRs / KPIs")
with c2:
    st.write("**QA & Testing:** UI, functional, integration, regression, usability testing; TestRail, Postman / Newman")
    st.write("**Dev & CI/CD:** GitHub, GitLab, release management, GitHub Actions (awareness), deployment tracking")
    st.write("**Data & Reporting:** MS SQL, PostgreSQL, Power BI (awareness), Tableau (awareness), Excel (advanced), Google Analytics")
with c3:
    st.write("**Collaboration:** MS Teams, Slack, Zoom, Google Meet, Miro, Google Workspace, SharePoint, OneDrive, Dropbox")
    st.write("**Leadership:** Stakeholder management, risk mitigation, cross-functional leadership, client onboarding, technical documentation, budget management")
    st.write("**AU Domain:** AVETMISS, CRICOS, VFH/VSL, RTO software, Student Management Systems, USI Integration")

# --- WORK EXPERIENCE ---
st.header("Work Experience")

st.subheader("Software Project Manager | Truly Imagine Pty Ltd")
st.caption("Remote - Australian-based company | Jan 2023 - May 2025")
st.write("""
Led delivery of SaaS-based platforms for Australian stakeholders, managing distributed teams and ensuring alignment between business expectations and technical execution.
""")
st.write("""- Led cross-functional team of 6 using Scrum, managing sprint planning and delivery across 3 active sprint cycles per month with 95%+ on-time delivery.
- Facilitated daily stand-ups and retrospectives via Jira/Confluence, reducing sprint carry-over by 30%.
- Owned end-to-end product roadmap and release calendar, aligning milestones to business OKRs.
- Designed and executed QA strategy reducing post-release defect rate by 25%.
- Collaborated via GitHub/GitLab and Postman to streamline API integration and CI/CD visibility.
- Maintained sprint artifacts and risk logs in Google Workspace/Confluence for full transparency.
""")

st.subheader("Freelance Project Management Consulting | Independent")
st.caption("Career development period | Apr 2022 - Dec 2022")
st.write("""- Completed Atlassian Jira Foundation and Lean Six Sigma (White, Yellow, Advanced Yellow Belt) certifications.
- Undertook freelance advisory work in project process documentation and team workflow optimisation.
"")


st.subheader("Database Administrator & Product Manager | Total Synergy Concepts Pvt Ltd")
st.caption("Amritsar - client: Australian RTO software provider | Nov 2019 - Jun 2021")
st.write("- Managed product improvement sprints using Teamwork and Zendesk to align delivery with client KPIs.")
st.write("- Analysed product and compliance data using MS SQL and Excel to support AVETMISS reporting accuracy.")
st.write("- Maintained live risk register, ensuring zero compliance-impacting defects at release.")

st.subheader("Senior Product Support Manager | Dream Net Software Pvt Ltd")
st.caption("Amritsar - Australian-focused RTO/VET software | Nov 2010 - Oct 2019")
st.write("- Translated Australian client requirements into detailed user stories and sprint tasks via Teamwork, Asana, GitHub, and Postman.")
st.write("- Managed compliance-critical delivery meeting Australian VET standards: CRICOS, AVETMISS, VFH/VSL.")
st.write("- Led client onboarding/data migration projects using MS SQL and PostgreSQL, reducing onboarding time by 35%.")
st.write("- Coordinated directly with Australian users and compliance officers to meet regulatory obligations.")

st.subheader("Support Team Lead | Dream Net Software Pvt Ltd")
st.caption("Amritsar - Australian RTO client base | Nov 2008 - Oct 2010")
st.write("- Managed escalated client issues via Zendesk, performing root cause analysis and usability testing.")
st.write("- Maintained MS SQL database backups and shared performance insights in team retrospectives.")
st.write("- Mentored junior staff and established documentation, reducing first-response resolution time by 20%.")

st.subheader("WFM Executive / Subject Matter Expert / Technical Support | Kochar InfoTech Pvt Ltd")
st.caption("Oct 2005 - Oct 2008")
st.write("- Managed workforce scheduling and employee data for major telecom clients: Airtel, Aircel, Idea.")
st.write("- Designed business performance improvement plans, increasing operational efficiency.")
st.write("- Handled complex technical escalations and implemented systemic solutions to reduce repeat incidents.")

# --- KEY CONTRIBUTIONS ---
st.header("Key Contributions")
# st.markdown("### EduRP SMS - Finance Module, Timetabling & WhatsApp Integration (Mar 2024 - Present)")

st.write("""- Improved delivery reliability through structured Agile practices.
- Strengthened stakeholder communication and reporting.
- Enhanced coordination across cross-functional teams.
- Reduced delivery issues through better planning and quality checks.
- Built consistent and accountable delivery processes.
""")
# --- AI TOOLS & ADOPTION ---
st.header("AI Tools & Adoption")
st.write("- **ChatGPT & Claude:** Prompt engineering for sprint documentation, retrospective summaries, user story drafting, and stakeholder reports.")
st.write("- **Notion AI / Confluence AI:** AI-assisted knowledge management and meeting summarisation.")
st.write("- **AI-powered Analytics:** Exploring Power BI Copilot for delivery reporting and real-time sprint insight generation.")

# --- CERTIFICATIONS ---
st.header("Certifications")
st.table({
    "Certification": ["Beginner's Guide to Agile in Jira", "Jira Foundation Badge", "Lean Six Sigma Yellow Belt", "Advanced LSS Yellow Belt", "Lean Six Sigma White Belt", "PMP (In Progress)", "Certified Scrum Master (Planned)"],
    "Issuing Body": ["Atlassian", "Atlassian", "Daniel Holzer", "Sparen & Gewinn Consulting", "Opex Learning", "PMI", "Scrum Alliance"],
    "Date/ID": ["215343779 | Jul 2022", "213760790 | Jun 2022", "8769Q54C | Jul 2022", "SG0722YB000277 | Jul 2022", "2022993422 | Jun 2022", "Target: 2025-26", "Target: 2025-26"]
})

# --- EDUCATION ---
st.header("Education")
st.write("- **Bachelor of Computer Applications (BCA):** Hindu College - Computer Application (2003-2006)")
st.write("- **Senior Secondary (+2):** Non-Medical, Punjab School Education Board (2001-2003)")
st.write("- **High School / Matriculation (10th):** Cedar Spring High School (1999-2001)")

# --- REFEREES ---
st.write("---")
st.write("**Professional referees available on request. Australian-based references can be provided.**")
