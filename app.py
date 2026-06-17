import streamlit as st
from matcher import match_resume_to_jd, extract_text_from_file
import plotly.graph_objects as go

st.set_page_config(
    page_title="Resume-JD Matcher",
    page_icon="📄",
    layout="centered"
)

st.title("📄 Resume ↔ Job Description Matcher")
st.write("Paste a job description and upload your CV (or paste it) to see your match score and missing keywords.")

col1, col2 = st.columns(2)

with col1:
    st.write("**Job Description**")
    jd_method = st.radio("How would you like to provide the job description?",
                          ["Paste text", "Upload file (PDF/DOCX)"],
                          horizontal=True, key="jd_method")

    jd_input = ""

    if jd_method == "Upload file (PDF/DOCX)":
        jd_file = st.file_uploader("Upload job description", type=['pdf', 'docx'], key="jd_uploader")
        if jd_file is not None:
            extracted_jd = extract_text_from_file(jd_file)
            if extracted_jd:
                jd_input = extracted_jd
                st.success(f"Extracted {len(extracted_jd.split())} words from {jd_file.name}")
            else:
                st.error("Could not read this file type.")
    else:
        jd_input = st.text_area("Paste the job description here", height=200, placeholder="Paste the job description here...")

with col2:
    st.write("**Your CV / Resume**")
    upload_method = st.radio("How would you like to provide your CV?",
                              ["Upload file (PDF/DOCX)", "Paste text"],
                              horizontal=True)

    cv_input = ""

    if upload_method == "Upload file (PDF/DOCX)":
        uploaded_file = st.file_uploader("Upload your CV", type=['pdf', 'docx'])
        if uploaded_file is not None:
            extracted = extract_text_from_file(uploaded_file)
            if extracted:
                cv_input = extracted
                st.success(f"Extracted {len(extracted.split())} words from {uploaded_file.name}")
            else:
                st.error("Could not read this file type.")
    else:
        cv_input = st.text_area("Paste your CV text", height=200, placeholder="Paste your CV text here...")

if st.button("Check Match", type="primary"):
    if not jd_input.strip() or not cv_input.strip():
        st.warning("Please provide both the job description and your CV.")
    else:
        result = match_resume_to_jd(jd_input, cv_input)

        st.divider()
        st.subheader("Results")

        score = result['final_score']
        st.metric("Overall Match Score", f"{score}%")

        if score >= 70:
            st.success("Strong match! Your CV aligns well with this job description.")
        elif score >= 40:
            st.info("Moderate match. Consider adding some of the missing keywords below.")
        else:
            st.warning("Low match. This CV may need significant tailoring for this role.")

        col_a, col_b = st.columns(2)
        with col_a:
            st.metric("Text Similarity", f"{result['tfidf_similarity']}%")
        with col_b:
            st.metric("Skill Coverage", f"{result['skill_coverage']}%")

        st.divider()

        matched_count = len(result['matched_skills'])
        missing_count = len(result['missing_skills'])

        fig = go.Figure(data=[go.Pie(
            labels=['Matched Skills', 'Missing Skills'],
            values=[matched_count, missing_count],
            hole=0.6,
            marker=dict(colors=['#2ecc71', '#e74c3c']),
            textinfo='label+percent',
            textfont=dict(size=14)
        )])

        fig.update_layout(
            showlegend=False,
            height=320,
            margin=dict(t=20, b=20, l=20, r=20),
            annotations=[dict(
                text=f"{result['skill_coverage']}%<br>Coverage",
                x=0.5, y=0.5,
                font_size=20,
                showarrow=False
            )]
        )

        st.plotly_chart(fig, use_container_width=True)

        st.divider()

        col_c, col_d = st.columns(2)
        with col_c:
            st.write("**✅ Matched Skills**")
            if result['matched_skills']:
                for skill in result['matched_skills']:
                    st.write(f"- {skill}")
            else:
                st.write("None found")

        with col_d:
            st.write("**❌ Missing Skills**")
            if result['missing_skills']:
                for skill in result['missing_skills']:
                    st.write(f"- {skill}")
            else:
                st.write("None — great coverage!")