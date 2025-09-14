# Put this at the very top of your file (before other imports / code)
from __future__ import annotations

import base64
import csv
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional

import streamlit as st
from PIL import Image

# === GLOBAL CONFIG ===
LINKEDIN = "https://www.linkedin.com/in/abhisekhbajracharya"
GITHUB = "https://github.com/abhisekhbajracharya"
RESUME_URL = None  # or "https://..." if hosted online
FORM_SUBMIT_EMAIL = None  # or your email if using FormSubmit

def resume_bytes():
    f = asset("Abhisekh_Resume.pdf")
    return load_bytes(f) if f.exists() else None

def pill(text: str):
    st.markdown(f"<span style='background:#eee;padding:3px 8px;border-radius:12px;margin-right:4px'>{text}</span>", unsafe_allow_html=True)
# ======================
# CONFIG & LIGHT STYLING, THIS MUST BE FIRST LINE OF CODE!!
# ======================
st.set_page_config(
    page_title="Abhisekh Bajracharya",
    page_icon="🌐",
    layout="centered",
    initial_sidebar_state="expanded",
)

# changing website background image
def add_bg_from_local(image_file):
    with open(image_file, "rb") as f:
        encoded = base64.b64encode(f.read()).decode()
    st.markdown(
        f"""
        <style>
        .stApp {{
            background-image: url("data:image/jpg;base64,{encoded}");
            background-attachment: fixed;
            background-size: cover;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

add_bg_from_local("background.jpg")
# Combining images cause there is gap in between casuing spacing issues.
def combine_images(files_and_widths, bg=(255,255,255)):
    imgs = []
    for fname, target_w in files_and_widths:
        img = Image.open(fname).convert("RGBA")
        w0,h0 = img.size
        new_h = int(h0 * (target_w / w0))
        img = img.resize((target_w, new_h), Image.LANCZOS)
        imgs.append(img)
    max_h = max(im.size[1] for im in imgs)
    padded = []
    for im in imgs:
        w,h = im.size
        if h < max_h:
            new = Image.new("RGBA", (w, max_h), (255,255,255,0))
            new.paste(im, (0, (max_h - h)//2), im)
            padded.append(new)
        else:
            padded.append(im)
    total_w = sum(im.size[0] for im in padded)
    out = Image.new("RGBA", (total_w, max_h), bg + (255,))
    x = 0
    for im in padded:
        out.paste(im, (x, 0), im)
        x += im.size[0]
    return out.convert("RGB")

def skill_bar(label: str, pct: int):
    pct = max(0, min(int(pct), 100))
    st.markdown(
        f"""
<div class='skill'>
  <div class='label'>{label}</div>
  <div class='bar'><div class='fill' style='width:{pct}%;'></div></div>
</div>
""",
        unsafe_allow_html=True,
    )


# Minimal CSS polish
st.markdown("""
<style>
.block-container {max-width: 980px;}
h1, h2, h3 { letter-spacing: .2px; }
.st-emotion-cache-1v0mbdj { margin-bottom: .35rem; }
.card {
  border: 1px solid rgba(0,0,0,.08);
  padding: .9rem 1rem;
  border-radius: 14px;
  box-shadow: 0 2px 10px rgba(0,0,0,.06);
  background: rgba(250,250,250,.7);
  margin-bottom: .6rem;
}
.small { opacity: .75; font-size: .9rem; }
</style>
""", unsafe_allow_html=True)

# ======================
# HELPERS
# ======================
def asset(path: str) -> Path:
    return Path("assets") / path

def load_bytes(p: Path):
    return p.read_bytes() if p.exists() else None

def skill_row(name: str, level: int, out_of: int = 5) -> str:
    level = max(0, min(level, out_of))
    filled = "🟩" * level
    empty = "⬜" * (out_of - level)
    return f"**{name}** {filled}{empty}"

def save_contact_message(name: str, email: str, message: str):
    Path("data").mkdir(exist_ok=True)
    file = Path("data/messages.csv")
    new = not file.exists()
    with file.open("a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if new:
            writer.writerow(["timestamp", "name", "email", "message"])
        writer.writerow([datetime.utcnow().isoformat(), name, email, message])


# =====================
# SIDEBAR — QUICK ACCESS + CONTACT
# =====================
st.sidebar.title("🔗 Quick Access")
st.sidebar.link_button("💼 LinkedIn", LINKEDIN)
st.sidebar.link_button("🧠 GitHub", GITHUB)
rb = resume_bytes()
if rb:
    st.sidebar.download_button("⬇️ Resume (PDF)", data=rb, file_name="Abhisekh_Resume.pdf", mime="application/pdf")
elif RESUME_URL:
    st.sidebar.link_button("📄 View Resume (PDF)", RESUME_URL)
else:
    st.sidebar.info("Add assets/Abhisekh_Resume.pdf or set RESUME_URL.")

st.sidebar.markdown("---")

with st.sidebar.form("contact_form", clear_on_submit=True):
    st.write("📬 Contact Me")
    name = st.text_input("Your Name")
    email = st.text_input("Your Email")
    msg = st.text_area("Message")
    ok = st.form_submit_button("Send")
    if ok:
        if not (name and email and msg):
            st.sidebar.error("Please fill out all fields.")
        else:
            # Always persist locally
            data_dir = Path("data"); data_dir.mkdir(exist_ok=True)
            fpath = data_dir / "messages.csv"
            new = not fpath.exists()
            with fpath.open("a", newline="", encoding="utf-8") as f:
                w = csv.writer(f)
                if new:
                    w.writerow(["timestamp", "name", "email", "message"])
                w.writerow([datetime.utcnow().isoformat(), name, email, msg])

            sent_remote = False
            if FORM_SUBMIT_EMAIL:
                try:
                    import requests  # lightweight; only used if email is set
                    endpoint = f"https://formsubmit.co/ajax/{FORM_SUBMIT_EMAIL}"
                    r = requests.post(endpoint, data={"name": name, "email": email, "message": msg}, timeout=8)
                    sent_remote = r.ok
                except Exception:
                    sent_remote = False

            if sent_remote:
                st.sidebar.success("Thanks! Your message was delivered.")
            else:
                # Provide a reliable fallback the user can click
                mailto = (
                    "mailto:" + (FORM_SUBMIT_EMAIL or "") +
                    f"?subject=Website%20Message%20from%20{name}&body=" +
                    (msg.replace("\n", "%0A"))
                )
                st.sidebar.success("Saved! Use the mail link below if needed.")
                st.sidebar.markdown(f"[📧 If email delivery failed, click to send](" + mailto + ")")
# ======================
# MAIN
# ======================
st.title("🌐 Abhisekh's Website")
st.caption("Run using `streamlit run dashboard.py`")

tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8 = st.tabs(
    ["About Me", "Resume", "Projects", "Hobbies", "Tech Stack", "Testimonials","Organizations", "More",]
)

# === TAB 1: ABOUT ME ===
with tab1:
    combined = combine_images([("UTA.jpg", 300), ("pho1.jpg", 300), ("JPM.jpg", 300)])
    st.image(combined, use_container_width=False)

    st.markdown("## 👋 Who am I?")
    st.markdown("""
    Hello, and welcome to my website. My name is **Abhisekh**.  
    I created this space to give you a clear and personal view of who I am—beyond what a résumé alone can show.  

    In today’s fast-paced hiring environment, where thousands of applications often compete for a job or internship, I believe this is the most effective way to present my background, interests, and strengths.
    """)

    st.markdown("## 💡 What do I (as a person) have to offer?")
    st.info("I recently graduated with a bachelors degree in computer science in December 2024, and am actively developing my skills in **data engineering, cloud platforms (Snowflake, Azure), and applied AI.** My current employment is at JP Morgan Chase as a Data Entry Specalist at the Lewisville, Texas.")
    st.markdown("""
    My goal is to contribute to building scalable solutions that deliver meaningful results.  
    While I am still growing my expertise, I am eager to learn quickly, apply myself to real-world projects, and contribute as a dedicated member of your team.
    """)
    with st.expander("📊 JPMorgan – Current Role"):
        st.image("JPM.jpg", width=300)
        st.markdown("""
        I’m currently working at JPMorgan in a datahouse environment, where I handle large volumes of information to ensure accuracy and consistency.  

        My responsibilities include:  
        - Processing and validating data  
        - Resolving discrepancies  
        - Maintaining clean records that support decision-making across teams  

        This experience has strengthened my interest in data-focused work and motivated me to deepen my technical skills.
        """)

    with st.expander("📦 Amazon (Irving, TX | June 2023 – June 2025)"):
        st.image("amazon.png", width=300)
        st.markdown("""
        At the same time, I worked as an Supply chain associate at an Amazon warehouse. Balancing this with my studies—like taking a Data Mining exam and then going straight to a shift—pushed me to become disciplined and reliable.  
        Amazon offered to pay for my tuition which greatly helped me continue on my studies.
        **Key takeaways:**  
        - Hands-on experience in inventory management & workflow coordination  
        - Meeting strict performance goals  
        - Reinforced the importance of efficiency and responsibility in large-scale operations
        """)

    with st.expander("🚀 NASA L’SPACE Academy (Remote | May – Aug 2024)"):
        st.image("lspace.png", width=200)
        st.markdown("""
                    In 2024, I joined **NASA’s L’SPACE Academy**, where I contributed to **mission planning and systems design** for a lunar rover project.  
                    This experience challenged me to bridge technical analysis with team collaboration, working alongside students from diverse disciplines to solve complex design problems.  
                    
                    As part of the **NASA Lunar Design – Data Analysis track**, I:  
                    - Queried **historical mission datasets in BigQuery** to uncover trends in payload efficiency and failure rates.  
                    - Built **data flow pipelines with DBT**, supporting structured testing and automated reporting.  
                    - Modeled **component performance with SQL-driven metrics**, achieving a **20% improvement in throughput analysis**.  
                    
                    Through this project, I gained hands-on exposure to **data-driven decision-making in aerospace contexts** while strengthening my skills in teamwork, communication, and systems thinking.  

                    Here is the link to the program: https://www.lspace.asu.edu/
                    """)


    with st.expander("🛍️ Retail Store Supervisor – Burkes Outlet (Irving, TX | June – August 2022)"):
        st.image("burkes.jpg", width=300)
        st.markdown("""
                    In 2022, while searching for additional opportunities across Irving, I joined **Burkes Outlet** as a **Retail Store Supervisor**. The team was impressed by my initiative and drive, and I was quickly trusted with leadership responsibilities.  
                    **Key Contributions:**  
                    - Supervised **daily retail operations**, ensuring smooth workflow and compliance with company standards.  
                    - Managed **confidential personnel matters**, including timecard approvals and employee dispute resolution.  
                    - **Trained new hires** in customer service protocols, safety procedures, and workplace expectations.  
                    - Utilized **Excel for staffing logs and inventory reporting**, and managed scheduling through Word and Outlook.  
                    """)


    with st.expander("🎓 Academic Projects"):
        st.markdown("""
        That interest grew during my academic projects, where I built predictive models, designed dashboards, and developed AI-powered business insights.  

        These projects showed me how technical skills can be applied to solve practical problems, and they gave me a foundation for working with data in a meaningful way.
        """)

    st.markdown("## 🎯 Career Goals & Vision")
    st.markdown("""
    Looking ahead, I want to bring these experiences together and focus on **AI, automation, and cloud platforms like Snowflake and Azure.**  
    My goal is to keep growing my skills and contribute to projects that use data to create impactful, scalable solutions.  

    Over the next **3–5 years**, I aim to:  
    - Gain hands-on experience through IT internships and entry-level roles  
    - Strengthen my foundation in data, cloud platforms, and automation  
    - Contribute to real projects where I can learn from experienced teams  
    - Grow into roles that allow me to apply problem-solving and technical skills to make a real impact  
    """)
# === TAB 2: RESUME ===
with tab2:
    st.header("📄 Resume & Experience")

    # --- Education ---
    st.subheader("🎓 Education")
    st.markdown(
        "🏫 **University of Texas at Arlington** — Bachelor of Science in Computer Science | December 2024"
    )
    st.markdown(
        "📚 **Courses Taken:** Algorithms & Data Structures | Probabilities & Statistics | Operating Systems | Computer Networks | Software Testing & Maintenance | Database Systems | Linux Systems | Cloud Computing | Information Security II | Microsoft Power Platforms | Azure Fundamentals | Datamining"
    )
    st.markdown("---")

    # --- Side-by-side Experience & Projects ---
    exp_col, proj_col = st.columns(2)

    # --- Professional Experience (Highlight JPMorgan) ---
    with exp_col:
        st.markdown("### 💼 Experience")
        st.markdown(
            "<div style= padding:12px; border-radius:10px'>"
            "⭐ <b>Data Entry | JPMorgan Chase (Contract by Adecco) — Lewisville, TX | June 2025 – Present</b>"
            "</div>", unsafe_allow_html=True
        )
        jpm_bullets = [
            "📌 Maintained accuracy and confidentiality while processing high volumes of financial data.",
            "📊 Prepared Excel templates and reports for analysis.",
            "⚡ Improved internal ETL workflows and documentation.",
            "⏱️ Supported fast-paced data handling workflows ensuring document accuracy."
        ]
        for b in jpm_bullets:
            st.markdown(f"- {b}")
        st.markdown("---")

        other_experience = {
            "Supply Chain Associate | Amazon — Irving, TX | June 2023 – June 2025": [
                "📦 Loaded packages and pallets correctly for safe transport.",
                "📱 Tracked package destinations using handheld scanners.",
                "🚀 Maintained workflow efficiency while meeting productivity & safety targets."
            ],
            "Intern | NASA L’Space Program | May 2024 – Aug 2024": [
                "🛰️ Tested drone payload subsystem performance.",
                "📝 Created system requirement checklists & validated integration.",
                "⚠️ Participated in risk analysis and suggested mitigations."
            ],
        }
        for title, bullets in other_experience.items():
            st.markdown(f"**{title}**")
            for b in bullets:
                st.markdown(f"- {b}")
            st.markdown("---")

    # --- Projects ---
    with proj_col:
        st.markdown("### 💻 Projects")
        projects = {
            "AI-Powered Business Risk Intelligence Dashboard – 2025": [
                "📊 Interactive fraud detection dashboard with Streamlit & scikit-learn.",
                "🤖 ML models flagged high-risk transactions; SHAP explainability.",
                "🔍 SQL-style filtering for business users."
            ],
            "Python-Based Data Insights & Automation Toolkit – 2025": [
                "🐍 Data cleaning, transformation, and exploratory analysis toolkit.",
                "📈 Automated Excel report generation with charts & summaries.",
                "💻 Command-line interface for batch processing."
            ],
            "DevOps-Enabled SaaS Task Management Platform – 2024": [
                "☁️ Cloud task app using React.js & MySQL; improved query performance ~30%.",
                "⚙️ CI/CD pipeline with GitHub Actions for testing & deployment.",
                "🔗 Ensured seamless frontend-backend integration."
            ],
            "CI/CD Pipeline for Flask Web App – 2023": [
                "🌐 Lightweight Flask app deployment.",
                "🐳 CI/CD workflow with GitHub Actions & Docker.",
                "🤝 Collaborated on pipeline improvements & peer reviews."
            ]
        }
        for proj, bullets in projects.items():
            st.markdown(f"**{proj}**")
            for b in bullets:
                st.markdown(f"- {b}")
            st.markdown("---")

    # --- Organizations ---
    st.subheader("🏛️ Organizations")
    st.markdown(
        "- 🚀 NASA L’Space Mission Concept Academy\n"
        "- 💻 UTA ACM (Association for Computing Machinery)\n"
        "- 🏆 UTA Hackathon Participant"
    )

    # --- Download Resume ---
    resume_file = asset("Abhisekh_Resume.pdf")
    pdf_bytes = load_bytes(resume_file)
    if pdf_bytes:
        st.download_button(
            label="⬇️ Download Full Resume (PDF)",
            data=pdf_bytes,
            file_name="Abhisekh_Resume.pdf",
            mime="application/pdf"
        )
    else:
        st.warning("Resume not found. Add it at `assets/Abhisekh_Resume.pdf` to enable download.")


# === TAB 3: PROJECTS ===
with tab3:
    st.header("Featured Projects (Top 3)")

    projects: List[Dict] = [
        {
            "title": "AI-Powered Business Risk Intelligence Dashboard",
            "when": "2025",
            "desc": [
                "Streamlit dashboard for anomaly detection in transactions.",
                "scikit-learn models + SHAP for explainability.",
                "SQL-style filtering and exportable reports.",
            ],
            "image": asset("proj_risk_dashboard.png"),
            "repo": f"{GITHUB}",  # update to specific repo when ready
            "demo": None,
            "stack": ["Python", "Streamlit", "scikit-learn", "pandas"],
        },
        {
            "title": "DevOps CI/CD for Flask App",
            "when": "2024",
            "desc": [
                "GitHub Actions pipeline for test/build/deploy.",
                "Dockerized app; simplified releases and rollbacks.",
                "Reduced manual errors; faster iterations.",
            ],
            "image": asset("proj_cicd.png"),
            "repo": f"{GITHUB}",
            "demo": None,
            "stack": ["GitHub Actions", "Docker", "Flask"],
        },
        {
            "title": "NASA L’SPACE — Lunar Rover Systems Concept (Data Track)",
            "when": "2024",
            "desc": [
                "Queried historical mission data (BigQuery) for component performance.",
                "Modeled throughput metrics; organized data flow with dbt.",
                "Worked in a cross-disciplinary student team.",
            ],
            "image": asset("proj_lspace.png"),
            "repo": None,
            "demo": None,
            "stack": ["SQL", "BigQuery", "dbt", "Excel"],
        },
    ]

    for p in projects:
        with st.container():
            c1, c2 = st.columns([1.2, 2])
            with c1:
                img_bytes = load_bytes(p["image"]) if p["image"] else None
                if img_bytes:
                    st.image(img_bytes, use_container_width=True, caption=p["title"], output_format="PNG")
                else:
                    st.markdown("<div class='card'>Add an image at " + str(p["image"]) + "</div>", unsafe_allow_html=True)
            with c2:
                st.markdown(f"#### {p['title']}  ")
                st.caption(p["when"])
                for d in p["desc"]:
                    st.write("- ", d)
                st.markdown(" ")
                # stack pills
                for s in p["stack"]:
                    pill(s)
                st.markdown(" ")
                bcol1, bcol2 = st.columns(2)
                if p["repo"]:
                    bcol1.link_button("🔗 View on GitHub", p["repo"])  # update per-project later
                if p["demo"]:
                    bcol2.link_button("▶️ Live Demo", p["demo"])  
        st.markdown("---")

# === TAB 4: HOBBIES ===
with tab4:
    st.header("🎯 Hobbies")
    st.markdown("""
Outside of work, I enjoy:
- 🎮 Video games: Crusader Kings 3, Project Zomboid, Red Dead Redemption 2, GTA V, Skyrim
- 🌿 Nature walks & photography: Used AllTrails in Angler MT trail, Colorado, Mt. Rainier Trail, Washington
- ✍️ Writing & 📖 Reading...
""")
    
    st.subheader("Travel Timeline")
    st.markdown("""
- **2022 Summer:** ✈️ Cozumel, Mexico – Relaxed on white-sand beaches, explored cenotes, and practiced slow travel.  
- **2022 Fall:** 🌲 Broken Bow, Oklahoma – Cabin retreat with friends, hiking and kayaking sparked my interest in nature photography.  
- **2023 Summer:** 🏙️ Manhattan, New York – Solo trip exploring tech culture, museums, and reflecting on personal goals.  
- **2023 Fall:** 🌧️ Cancun, Mexico – Mixed city and nature experiences, from local parks to cultural landmarks.  
- **2024 Summer:** ☀️ Rockwall, Texas – Discovered local scenery, enjoyed lake views, and short day hikes.  
- **2024 Fall:** 🌧️ Seattle, Washington – Explored the city’s tech scene and natural landscapes, from Pike Place to nearby trails.  
- **2025 Summer:** 🕉️ Kathmandu, Nepal – Reconnected with family and heritage, visited temples and historic sites.  
- **2025 Fall:** 🏔️ Vail, Colorado – Mountain retreat with hiking, fresh air, and a focus on relaxation.  
""")

# === TAB 5: TECH STACK ===
with tab5:
    st.header("Tech Stack")

    left, right = st.columns(2)
    with left:
        st.subheader("Core")
        skill_bar("Python", 90)
        skill_bar("SQL", 80)
        skill_bar("Streamlit", 90)
        skill_bar("scikit-learn", 75)
        skill_bar("GitHub Actions", 75)
        skill_bar("Docker", 60)
    with right:
        st.subheader("Cloud / Tools")
        skill_bar("Azure", 60)
        skill_bar("AWS", 55)
        skill_bar("Power BI", 55)
        skill_bar("Jupyter", 90)
        skill_bar("Linux", 65)

    st.caption("*Levels are honest self-assessments for quick scanning; details on request.*")
    st.markdown("### 🛠️ Skills (Levels)")

    # Skill details dictionary
    skill_details = {
        "Python": "Daily use in AI dashboards, data pipelines, and automation scripts; strong command of pandas, numpy, scikit-learn, matplotlib; end-to-end pipeline experience.",
        "SQL": "Regularly writing queries for analytics and reporting; confident in data extraction, filtering, aggregation, and joins.",
        "HTML/CSS": "Built dashboards and web interfaces; solid understanding of structuring pages and styling for clear, functional design.",
        "scikit-learn": "Applied in multiple ML projects for predictive modeling, anomaly detection, feature engineering, and pipelines.",
        "TensorFlow": "Developed neural network models; practical experience building, training, and evaluating deep learning models.",
        "GitHub Actions": "Created CI/CD pipelines for automated testing, building, and deploying apps; strong workflow experience.",
        "Docker": "Containerized applications for consistent development, testing, and deployment; experienced with images and commands.",
        "Heroku": "Deployed apps quickly; practiced in managing apps, updates, and integrations with CI/CD pipelines.",
        "AWS": "Hands-on with S3, Lambda, EC2; experienced in practical deployment and integration into projects.",
        "Azure": "Used core services for cloud-based project deployments; confident in managing storage, functions, and ML workloads.",
        "Streamlit": "Built multiple dashboards and interactive apps; highly comfortable creating polished, user-friendly interfaces.",
        "Jupyter": "Daily environment for notebooks, experimentation, and sharing data projects; central to workflow.",
        "Power BI": "Created interactive reports and dashboards; skilled in visualizing data and generating actionable insights."
    }

    # Layout: 3 columns for skills + descriptions
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown(f"**Python** 🟩🟩🟩🟩🟩  - {skill_details['Python']}")
        st.markdown(f"**SQL** 🟩🟩🟩🟩⬜  - {skill_details['SQL']}")
        st.markdown(f"**HTML/CSS** 🟩🟩🟩⬜⬜  - {skill_details['HTML/CSS']}")
    with col2:
        st.markdown(f"**scikit-learn** 🟩🟩🟩🟩⬜  - {skill_details['scikit-learn']}")
        st.markdown(f"**TensorFlow** 🟩🟩🟩⬜⬜  - {skill_details['TensorFlow']}")
    with col3:
        st.markdown(f"**GitHub Actions** 🟩🟩🟩🟩⬜  - {skill_details['GitHub Actions']}")
        st.markdown(f"**Docker** 🟩🟩🟩⬜⬜  - {skill_details['Docker']}")
        st.markdown(f"**Heroku** 🟩🟩🟩⬜⬜  - {skill_details['Heroku']}")

    st.markdown("### ☁️ Cloud")
    cloud1, cloud2 = st.columns(2)
    with cloud1:
        st.markdown(f"**AWS** 🟩🟩🟩⬜⬜  - {skill_details['AWS']}")
    with cloud2:
        st.markdown(f"**Azure** 🟩🟩🟩⬜⬜  - {skill_details['Azure']}")

    st.markdown("### 🧰 Tools")
    t1, t2, t3 = st.columns(3)
    with t1:
        st.markdown(f"**Streamlit** 🟩🟩🟩🟩🟩  - {skill_details['Streamlit']}")
    with t2:
        st.markdown(f"**Jupyter** 🟩🟩🟩🟩🟩  - {skill_details['Jupyter']}")
    with t3:
        st.markdown(f"**Power BI** 🟩🟩🟩⬜⬜  - {skill_details['Power BI']}")

    st.markdown("### 📜 Certifications")
    st.write("- Google Data Analytics Certificate – Coursera")
    st.write("- Microsoft Azure Fundamentals – AZ-900")
    st.write("- NASA L'SPACE Mission Concept Academy")


# === TAB 6: TESTIMONIALS ===
# Add CSS once (outside your tab6 block)
st.markdown(
    """
    <style>
    .card {
        background-color: #0a2540; /* dark blue */
        color: white; /* text color */
        padding: 20px;
        margin: 10px 0;
        border-radius: 10px;
        font-size: 16px;
        line-height: 1.5;
    }
    .card .small {
        font-size: 14px;
        color: #d0e0ff; /* lighter blue for author text */
        display: block;
        margin-top: 8px;
    }
    </style>
    """,
    unsafe_allow_html=True
)

with tab6:
    st.header("💬 Testimonials")
    st.markdown('<div class="card">“Abhisekh demonstrated leadership and clarity under pressure. Highly recommended.”<br><span class="small">— L\'SPACE Mentor</span></div>', unsafe_allow_html=True)
    st.markdown('<div class="card">“Consistent, focused, and collaborative — a valuable team member.”<br><span class="small">— Amazon Supervisor</span></div>', unsafe_allow_html=True)
    st.markdown('<div class="card">“He showed strong initiative during his capstone project, translating ideas into solutions.”<br><span class="small">— UTA Professor</span></div>', unsafe_allow_html=True)

# === TAB 7: MORE ===
with tab7:
    st.header("🏛️ Clubs and Organizations")

    st.markdown("### 🚀 NASA L’SPACE Mission Concept Academy")
    st.markdown(
        "- Took part in a national NASA program focused on mission design.\n"
        "- Gained experience working with a student team on a **lunar rover concept**.\n"
        "- Learned how big projects are broken down into systems like power, thermal, and payload."
    )

    st.markdown("### 💻 UTA ACM (Association for Computing Machinery)")
    st.markdown(
        "- Attended coding workshops and tech talks to learn from peers and guest speakers.\n"
        "- Joined group projects and practice sessions to get better at problem solving.\n"
        "- Used the club as a way to meet other students interested in programming and AI."
    )

    st.markdown("### 🏆 UTA Hackathon Participant")
    st.markdown(
        "- Entered hackathons with classmates to try out quick coding ideas.\n"
        "- Focused on building simple prototypes and learning under time pressure.\n"
        "- Gained practice presenting rough solutions to judges, even when unfinished."
    )

    st.markdown("### 🌸 United Newa Community")
    st.markdown(
        "- Joined events that celebrated **Newa culture and traditions**.\n"
        "- Helped out with small tasks during community gatherings and festivals.\n"
        "- Mostly participated to stay connected with heritage and meet other Nepali families."
    )

    st.markdown("### 👔 Nepali Young Professionals (NYP)")
    st.markdown(
        "- Attended meetups and networking events with other young Nepali professionals.\n"
        "- Listened to guest speakers talk about careers and opportunities.\n"
        "- Used the group as a way to stay in touch with the broader Nepali community in the U.S."
    )

    st.markdown("### 🦁 Dallas Lions Club")
    st.markdown(
        "- Volunteered at a few local service events hosted by the Lions Club.\n"
        "- Helped with small roles like setting up, organizing materials, or assisting participants.\n"
        "- Exposure to community service projects made me more aware of local needs."
    )


# === TAB 8: MORE ===
with tab8:
    st.header("🌟 More")
    st.markdown("### 🤝 Open Source & Community")
    st.write("- Contributed to **Awesome-Data-Science** repo (docs & examples)")
    st.write("- Participated in hackathons (e.g., **HackTX**) & local meetups")
    st.write("- Volunteer mentor for Python & data analysis beginners")

    st.markdown("### 🧠 Soft Skills & Work Style")
    st.write("- Communication, teamwork, adaptability")
    st.write("- Managed deadlines in fast-paced environments")
    st.write("- Continuous learning & open feedback")

    st.markdown("### 📓 Blog & Insights")
    st.write("[How I Built My First Streamlit Dashboard](#)")
    st.write("[Trends in AI and Ethics](#)")
    st.write("[Balancing Productivity and Wellness](#)")

    st.markdown("### 📓 Poems and Short Stories")
    st.link_button("Laurel Crown of Florence", "https://docs.google.com/document/d/15pfmXz-BYTDSDe-V5B9CbuCWdeTqrRJCI1CoCDOGaDY/edit?usp=sharing")
    st.link_button("Castella", "https://docs.google.com/document/d/12HoqldBM9bv2NIVOw_jRA0y0VAnge6_-TXn_laL6o70/edit?usp=sharing")
    st.link_button("Seaheart", "")
    st.link_button("Value of Life", "https://docs.google.com/document/d/1Gh0EPCR3JYS2o9NR2GwQyYXgnwSFOuEJvMwgQN-6mWU/edit?usp=sharing")
    st.image("Seaheart_cover.png", caption="Seaheart cover", width=300)

