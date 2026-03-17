"""
app.py - AI Resume Analyzer
Main Streamlit UI with two-column layout, charts, and AI feedback
Run with: streamlit run app.py
"""

import io
import os
import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np

from utils import extract_text_from_pdf, clean_text, count_words, get_text_preview
from skills import SKILLS_DB
from logic import (
    detect_skills, detect_sections, calculate_ats_score,
    get_missing_skills, match_job_description,
    get_ats_color, get_ats_label
)
from ai_module import get_ai_feedback, generate_improve_section

# ─── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="AI Resume Analyzer",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─── Custom CSS ───────────────────────────────────────────────────────────────
st.markdown("""
<style>
  /* Global font */
  html, body, [class*="css"] { font-family: 'Segoe UI', sans-serif; }

  /* Header gradient */
  .hero-header {
    background: linear-gradient(135deg, #1e3a5f 0%, #0f6cbf 60%, #00c6ff 100%);
    padding: 2.5rem 2rem;
    border-radius: 14px;
    margin-bottom: 1.8rem;
    text-align: center;
    color: white;
  }
  .hero-header h1 { font-size: 2.4rem; font-weight: 800; margin: 0; letter-spacing: -0.5px; }
  .hero-header p  { font-size: 1.05rem; margin: 0.4rem 0 0; opacity: 0.88; }

  /* Score circle */
  .score-circle {
    display: flex; flex-direction: column;
    align-items: center; justify-content: center;
    width: 130px; height: 130px; border-radius: 50%;
    margin: 0 auto 0.8rem;
    font-weight: 900; font-size: 2.2rem; color: white;
  }
  .score-label { font-size: 0.8rem; font-weight: 600; letter-spacing: 1px; margin-top: -4px; }

  /* Metric cards */
  .metric-card {
    background: #f0f4fb; border-radius: 10px;
    padding: 1rem 1.2rem; margin-bottom: 0.6rem;
    border-left: 4px solid #0f6cbf;
  }
  .metric-card h4 { margin: 0 0 0.2rem; font-size: 0.85rem; color: #555; }
  .metric-card p  { margin: 0; font-size: 1.4rem; font-weight: 700; color: #1e3a5f; }

  /* Section headers */
  .section-title {
    font-size: 1.15rem; font-weight: 700; color: #1e3a5f;
    border-bottom: 2px solid #0f6cbf; padding-bottom: 0.3rem;
    margin: 1.2rem 0 0.8rem;
  }

  /* Skill pills */
  .skill-pill {
    display: inline-block; background: #e8f0fb; color: #1e3a5f;
    border-radius: 20px; padding: 2px 10px; font-size: 0.78rem;
    margin: 2px; font-weight: 500;
  }
  .skill-pill-missing {
    display: inline-block; background: #fff3cd; color: #856404;
    border-radius: 20px; padding: 2px 10px; font-size: 0.78rem;
    margin: 2px; font-weight: 500;
  }
  .skill-pill-matched {
    display: inline-block; background: #d4edda; color: #155724;
    border-radius: 20px; padding: 2px 10px; font-size: 0.78rem;
    margin: 2px; font-weight: 500;
  }

  /* AI feedback boxes */
  .fb-box {
    background: #f8faff; border: 1px solid #cdd9f0;
    border-radius: 10px; padding: 1rem 1.2rem; margin-bottom: 0.8rem;
  }
  .fb-box h4 { margin: 0 0 0.4rem; color: #0f6cbf; font-size: 0.92rem; }
  .fb-box p  { margin: 0; font-size: 0.9rem; line-height: 1.55; color: #333; }

  /* Section detection badges */
  .badge-found    { background: #d4edda; color: #155724; border-radius: 6px; padding: 2px 8px; font-size: 0.78rem; font-weight: 600; }
  .badge-missing  { background: #f8d7da; color: #721c24; border-radius: 6px; padding: 2px 8px; font-size: 0.78rem; font-weight: 600; }

  /* Divider */
  hr.thin { border: none; border-top: 1px solid #e0e8f5; margin: 1.2rem 0; }

  /* Download button */
  .stDownloadButton > button { width: 100%; }
</style>
""", unsafe_allow_html=True)

# ─── Hero Header ──────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero-header">
  <h1>📄 AI Resume Analyzer</h1>
  <p>Upload your resume · Get ATS score · Match jobs · Receive AI feedback</p>
</div>
""", unsafe_allow_html=True)

# ─── Sidebar ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## ⚙️ Controls")
    uploaded_file = st.file_uploader(
        "Upload Resume (PDF)",
        type=["pdf"],
        help="Upload your resume in PDF format"
    )

    st.markdown("---")
    st.markdown("### 📋 Job Description (Optional)")
    job_desc = st.text_area(
        "Paste the job description here",
        height=160,
        placeholder="Paste the job description to get a match score and alignment tips...",
        label_visibility="collapsed"
    )

    st.markdown("---")
    ai_disabled = uploaded_file is None
    run_ai = st.button(
        "✨ Generate AI Feedback",
        disabled=ai_disabled,
        use_container_width=True,
        help="Upload a resume first to enable AI feedback"
    )
    if ai_disabled:
        st.caption("Upload a resume to enable AI feedback.")

    st.markdown("---")
    st.markdown("### ℹ️ About")
    st.caption(
        "This tool uses PyPDF2 for extraction, "
        "keyword matching for ATS scoring, and "
        "google/flan-t5-base via Hugging Face for AI insights."
    )

# ─── Main Content ─────────────────────────────────────────────────────────────
if uploaded_file is None:
    # Landing / empty state
    st.markdown("---")
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown("### 📤 Upload")
        st.write("Upload your PDF resume using the sidebar to get started.")
    with c2:
        st.markdown("### 📊 Analyze")
        st.write("Get instant ATS score, skill detection, and section analysis.")
    with c3:
        st.markdown("### 🤖 AI Feedback")
        st.write("Receive AI-powered feedback on strengths, gaps, and improvements.")
    st.stop()

# ─── Extract & Process ────────────────────────────────────────────────────────
with st.spinner("Extracting text from PDF..."):
    raw_text = extract_text_from_pdf(uploaded_file)
    resume_text = clean_text(raw_text)

if not resume_text or count_words(resume_text) < 10:
    st.error(
        "Could not extract readable text from this PDF. "
        "This may be a scanned image PDF. Please use a text-based PDF."
    )
    st.stop()

# Run analysis
detected_skills = detect_skills(resume_text)
sections = detect_sections(resume_text)
ats_score, ats_breakdown = calculate_ats_score(resume_text, detected_skills, sections)
missing_skills = get_missing_skills(detected_skills)
word_count = count_words(resume_text)

# JD matching
jd_score, jd_matched, jd_missing = (0.0, [], [])
if job_desc.strip():
    jd_score, jd_matched, jd_missing = match_job_description(resume_text, job_desc)

# ─── Summary Row ──────────────────────────────────────────────────────────────
total_detected = sum(len(v) for v in detected_skills.values())
ats_color_hex = {"green": "#28a745", "orange": "#fd7e14", "red": "#dc3545"}[get_ats_color(ats_score)]
ats_label = get_ats_label(ats_score)

m1, m2, m3, m4 = st.columns(4)
with m1:
    st.markdown(f"""
    <div class="metric-card">
      <h4>ATS Score</h4>
      <p style="color:{ats_color_hex}">{ats_score}/100</p>
    </div>""", unsafe_allow_html=True)
with m2:
    st.markdown(f"""
    <div class="metric-card">
      <h4>Skills Detected</h4>
      <p>{total_detected}</p>
    </div>""", unsafe_allow_html=True)
with m3:
    st.markdown(f"""
    <div class="metric-card">
      <h4>Word Count</h4>
      <p>{word_count:,}</p>
    </div>""", unsafe_allow_html=True)
with m4:
    jd_display = f"{jd_score:.0f}%" if job_desc.strip() else "N/A"
    st.markdown(f"""
    <div class="metric-card">
      <h4>JD Match</h4>
      <p>{jd_display}</p>
    </div>""", unsafe_allow_html=True)

# ATS alert banners
if ats_score >= 70:
    st.success(f"✅ **{ats_label} Resume!** Your ATS score is {ats_score}/100 — great job!")
elif ats_score >= 40:
    st.warning(f"⚠️ **{ats_label} Resume.** Your ATS score is {ats_score}/100 — some improvements recommended.")
else:
    st.error(f"🚨 **{ats_label}.** Your ATS score is {ats_score}/100 — significant improvements needed.")

st.markdown("<hr class='thin'>", unsafe_allow_html=True)

# ─── Two-Column Layout ────────────────────────────────────────────────────────
col_left, col_right = st.columns([1.1, 1], gap="large")

# ══════════════════════════════════════════════
# LEFT COLUMN
# ══════════════════════════════════════════════
with col_left:

    # ── ATS Score Breakdown ──
    st.markdown('<div class="section-title">📊 ATS Score Breakdown</div>', unsafe_allow_html=True)

    fig_ats, ax_ats = plt.subplots(figsize=(5, 2.6))
    categories = list(ats_breakdown.keys())
    values = list(ats_breakdown.values())
    max_vals = [40, 25, 20, 15]
    bar_colors = []
    for v, m in zip(values, max_vals):
        ratio = v / m if m > 0 else 0
        if ratio >= 0.7:
            bar_colors.append("#28a745")
        elif ratio >= 0.4:
            bar_colors.append("#fd7e14")
        else:
            bar_colors.append("#dc3545")

    bars = ax_ats.barh(categories, values, color=bar_colors, height=0.5, edgecolor="none")
    ax_ats.barh(categories, max_vals, color="#e9ecef", height=0.5, edgecolor="none", zorder=0)
    ax_ats.barh(categories, values, color=bar_colors, height=0.5, edgecolor="none", zorder=1)

    for bar, val in zip(bars, values):
        ax_ats.text(bar.get_width() + 0.3, bar.get_y() + bar.get_height() / 2,
                    f"{val:.0f}", va="center", ha="left", fontsize=9, fontweight="bold", color="#333")

    ax_ats.set_xlim(0, 45)
    ax_ats.set_xlabel("Score", fontsize=8, color="#666")
    ax_ats.tick_params(axis="y", labelsize=9)
    ax_ats.tick_params(axis="x", labelsize=8)
    ax_ats.spines[["top", "right", "left"]].set_visible(False)
    ax_ats.set_facecolor("#fafcff")
    fig_ats.patch.set_facecolor("#fafcff")
    plt.tight_layout(pad=0.5)
    st.pyplot(fig_ats, use_container_width=True)
    plt.close(fig_ats)

    # ── Skill Distribution Bar Chart ──
    st.markdown('<div class="section-title">🛠️ Skill Distribution</div>', unsafe_allow_html=True)

    skill_cats = [c for c in SKILLS_DB.keys() if c != "Soft Skills"]
    detected_counts = [len(detected_skills.get(c, [])) for c in skill_cats]
    total_counts = [len(SKILLS_DB[c]) for c in skill_cats]

    fig_skills, ax_skills = plt.subplots(figsize=(5, 3))
    x = np.arange(len(skill_cats))
    width = 0.35
    short_labels = ["Programming", "Web Dev", "Data Science", "Core CS"]

    ax_skills.bar(x - width / 2, total_counts, width, label="Available", color="#cfe2ff", edgecolor="none")
    ax_skills.bar(x + width / 2, detected_counts, width, label="Detected", color="#0f6cbf", edgecolor="none")

    ax_skills.set_xticks(x)
    ax_skills.set_xticklabels(short_labels, fontsize=8.5)
    ax_skills.tick_params(axis="y", labelsize=8)
    ax_skills.legend(fontsize=8)
    ax_skills.spines[["top", "right"]].set_visible(False)
    ax_skills.set_facecolor("#fafcff")
    fig_skills.patch.set_facecolor("#fafcff")
    plt.tight_layout(pad=0.4)
    st.pyplot(fig_skills, use_container_width=True)
    plt.close(fig_skills)

    # ── Category Coverage Pie Chart ──
    st.markdown('<div class="section-title">🥧 Category Coverage</div>', unsafe_allow_html=True)

    pie_labels = short_labels
    pie_values = [max(c, 0.01) for c in detected_counts]
    pie_colors = ["#0f6cbf", "#198754", "#6f42c1", "#fd7e14"]

    fig_pie, ax_pie = plt.subplots(figsize=(4.5, 3))
    wedges, texts, autotexts = ax_pie.pie(
        pie_values, labels=pie_labels, autopct="%1.0f%%",
        colors=pie_colors, startangle=140,
        textprops={"fontsize": 8},
        wedgeprops={"edgecolor": "white", "linewidth": 1.5}
    )
    for at in autotexts:
        at.set_fontsize(7.5)
        at.set_color("white")
        at.set_fontweight("bold")
    ax_pie.set_facecolor("#fafcff")
    fig_pie.patch.set_facecolor("#fafcff")
    plt.tight_layout(pad=0.3)
    st.pyplot(fig_pie, use_container_width=True)
    plt.close(fig_pie)

    # ── Section Detection ──
    st.markdown('<div class="section-title">📑 Resume Section Detection</div>', unsafe_allow_html=True)
    section_labels = {
        "experience": "Work Experience",
        "education": "Education",
        "skills": "Skills Section",
        "projects": "Projects",
        "certifications": "Certifications",
        "summary": "Summary / Profile"
    }
    sec_cols = st.columns(2)
    for i, (key, label) in enumerate(section_labels.items()):
        found = sections.get(key, False)
        badge = f'<span class="badge-found">✔ Found</span>' if found else f'<span class="badge-missing">✘ Missing</span>'
        with sec_cols[i % 2]:
            st.markdown(f"**{label}** &nbsp; {badge}", unsafe_allow_html=True)

# ══════════════════════════════════════════════
# RIGHT COLUMN
# ══════════════════════════════════════════════
with col_right:

    # ── Detected Skills ──
    st.markdown('<div class="section-title">✅ Detected Skills</div>', unsafe_allow_html=True)

    category_icons = {
        "Programming Languages": "💻",
        "Web Development": "🌐",
        "Data Science & ML": "📈",
        "Core CS & DevOps": "⚙️",
        "Soft Skills": "🤝"
    }

    for category, skills in detected_skills.items():
        if skills:
            icon = category_icons.get(category, "•")
            with st.expander(f"{icon} {category} ({len(skills)} found)", expanded=(len(skills) > 0)):
                pills = " ".join(f'<span class="skill-pill">{s}</span>' for s in skills)
                st.markdown(pills, unsafe_allow_html=True)

    # ── Missing Skills ──
    st.markdown('<div class="section-title">❌ Missing Skills</div>', unsafe_allow_html=True)
    st.caption("Top skills from each category not found in your resume:")

    for category, skills in missing_skills.items():
        if skills and category != "Soft Skills":
            icon = category_icons.get(category, "•")
            with st.expander(f"{icon} {category} — {len(skills)} missing"):
                pills = " ".join(f'<span class="skill-pill-missing">{s}</span>' for s in skills)
                st.markdown(pills, unsafe_allow_html=True)

    # ── Job Description Matching ──
    if job_desc.strip():
        st.markdown('<div class="section-title">🎯 Job Description Match</div>', unsafe_allow_html=True)

        # JD match score meter
        jd_color = "#28a745" if jd_score >= 60 else ("#fd7e14" if jd_score >= 35 else "#dc3545")
        jd_label = "Strong Match" if jd_score >= 60 else ("Moderate Match" if jd_score >= 35 else "Low Match")

        fig_jd, ax_jd = plt.subplots(figsize=(4.5, 0.55))
        ax_jd.barh([0], [100], height=0.45, color="#e9ecef", edgecolor="none")
        ax_jd.barh([0], [jd_score], height=0.45, color=jd_color, edgecolor="none")
        ax_jd.set_xlim(0, 100)
        ax_jd.axis("off")
        fig_jd.patch.set_facecolor("#fafcff")
        plt.tight_layout(pad=0.1)
        st.pyplot(fig_jd, use_container_width=True)
        plt.close(fig_jd)

        st.markdown(f"**{jd_score:.1f}% Match** — {jd_label}")

        jd_c1, jd_c2 = st.columns(2)
        with jd_c1:
            st.markdown("**✅ Matched Keywords**")
            if jd_matched:
                matched_pills = " ".join(f'<span class="skill-pill-matched">{k}</span>' for k in jd_matched[:15])
                st.markdown(matched_pills, unsafe_allow_html=True)
            else:
                st.caption("No matches found.")
        with jd_c2:
            st.markdown("**⚠️ Missing from Resume**")
            if jd_missing:
                missing_pills = " ".join(f'<span class="skill-pill-missing">{k}</span>' for k in jd_missing[:15])
                st.markdown(missing_pills, unsafe_allow_html=True)
            else:
                st.caption("Great — no key terms missing!")
    else:
        st.markdown('<div class="section-title">🎯 Job Description Match</div>', unsafe_allow_html=True)
        st.info("Paste a job description in the sidebar to see how well your resume matches it.")

# ─── AI Feedback Section ──────────────────────────────────────────────────────
st.markdown("<hr class='thin'>", unsafe_allow_html=True)
st.markdown("## 🤖 AI-Powered Feedback")

if run_ai:
    with st.spinner("🤖 Generating AI feedback..."):
        feedback = get_ai_feedback(resume_text, job_desc)

        if feedback.get("error"):
            st.error(f"AI Error: {feedback['error']}")
        else:
            ai_c1, ai_c2 = st.columns(2)

            with ai_c1:
                st.markdown('<div class="section-title">💪 Strengths</div>', unsafe_allow_html=True)
                st.markdown(f'<div class="fb-box"><p>{feedback.get("strengths", "N/A")}</p></div>', unsafe_allow_html=True)

                st.markdown('<div class="section-title">📝 Resume Rewrite Tips</div>', unsafe_allow_html=True)
                st.markdown(f'<div class="fb-box"><p>{feedback.get("rewrite_tips", "N/A")}</p></div>', unsafe_allow_html=True)

                if feedback.get("job_alignment"):
                    st.markdown('<div class="section-title">🎯 Job Alignment</div>', unsafe_allow_html=True)
                    st.markdown(f'<div class="fb-box"><p>{feedback.get("job_alignment")}</p></div>', unsafe_allow_html=True)

            with ai_c2:
                st.markdown('<div class="section-title">⚠️ Weaknesses</div>', unsafe_allow_html=True)
                st.markdown(f'<div class="fb-box"><p>{feedback.get("weaknesses", "N/A")}</p></div>', unsafe_allow_html=True)

                st.markdown('<div class="section-title">🚀 Improvements</div>', unsafe_allow_html=True)
                st.markdown(f'<div class="fb-box"><p>{feedback.get("improvements", "N/A")}</p></div>', unsafe_allow_html=True)

            # ── Improve My Resume Section ──
            st.markdown("<hr class='thin'>", unsafe_allow_html=True)
            st.markdown("### ✍️ Improve My Resume")
            st.caption("AI-generated improved version of your resume introduction:")
            with st.spinner("Generating improved resume summary..."):
                improved = generate_improve_section(resume_text)
            if improved:
                st.markdown(f'<div class="fb-box"><p>{improved}</p></div>', unsafe_allow_html=True)

            # ── Download Report ──
            st.markdown("<hr class='thin'>", unsafe_allow_html=True)
            st.markdown("### 📥 Download Analysis Report")

            report_lines = [
                "=" * 60,
                "        AI RESUME ANALYSIS REPORT",
                "=" * 60,
                "",
                f"ATS Score: {ats_score}/100  ({ats_label})",
                f"Word Count: {word_count}",
                f"Skills Detected: {total_detected}",
                f"JD Match Score: {jd_score:.1f}%" if job_desc.strip() else "JD Match: Not provided",
                "",
                "── ATS SCORE BREAKDOWN ──",
            ]
            for k, v in ats_breakdown.items():
                report_lines.append(f"  {k}: {v:.1f}")
            report_lines += [
                "",
                "── DETECTED SKILLS ──",
            ]
            for cat, skills in detected_skills.items():
                if skills:
                    report_lines.append(f"  {cat}: {', '.join(skills)}")
            report_lines += [
                "",
                "── MISSING SKILLS (Top per Category) ──",
            ]
            for cat, skills in missing_skills.items():
                if skills and cat != "Soft Skills":
                    report_lines.append(f"  {cat}: {', '.join(skills[:5])}")
            report_lines += [
                "",
                "── AI FEEDBACK ──",
                "",
                "Strengths:",
                feedback.get("strengths", "N/A"),
                "",
                "Weaknesses:",
                feedback.get("weaknesses", "N/A"),
                "",
                "Improvements:",
                feedback.get("improvements", "N/A"),
                "",
                "Resume Rewrite Tips:",
                feedback.get("rewrite_tips", "N/A"),
            ]
            if feedback.get("job_alignment"):
                report_lines += ["", "Job Alignment:", feedback.get("job_alignment")]
            if improved:
                report_lines += ["", "Improved Resume Summary:", improved]
            report_lines += ["", "=" * 60, "Generated by AI Resume Analyzer", "=" * 60]

            report_text = "\n".join(report_lines)
            st.download_button(
                label="⬇️ Download Full Report (.txt)",
                data=report_text.encode("utf-8"),
                file_name="resume_analysis_report.txt",
                mime="text/plain",
                use_container_width=True
            )
else:
    st.info("Click **✨ Generate AI Feedback** in the sidebar to receive AI-powered resume analysis.")

# ─── Resume Text Preview ──────────────────────────────────────────────────────
st.markdown("<hr class='thin'>", unsafe_allow_html=True)
with st.expander("📄 View Extracted Resume Text"):
    st.text(get_text_preview(resume_text, max_chars=2000))
    if len(resume_text) > 2000:
        st.caption(f"Showing first 2000 characters. Total: {len(resume_text):,} characters.")
