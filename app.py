import streamlit as st
from pdf_parser import parse_pdf, generate_grouped_content_string, check_education_match
from skills_extractor import extract_skills_from_text, load_ner_model
from faiss_handler import compute_skill_score
import spacy
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import numpy as np 

st.title("The Skill Matcher App")
st.write(
    "This app matches the skills from your CV with a job description to help you identify matching and missing skills!"
)
nlp = spacy.load("en_core_web_lg")
ner_model = load_ner_model()

# Section 1: Upload your CV

st.subheader("Upload Your CV")
cv_uploaded = st.file_uploader("", type="pdf", key="cv_upload")

cv_content = None
if cv_uploaded:
    with st.spinner("Parsing CV PDF..."):
        parsed_sections = parse_pdf(cv_uploaded)
        cv_content = generate_grouped_content_string(parsed_sections)
    #st.success("CV uploaded and parsed successfully!")

# Section 2: Paste the Job Description
st.subheader("Job Description")
job_description = st.text_area("Paste the Job Description", placeholder="Enter the job description here...", height=100)

if st.button("Analyze Skills"):
    if not cv_uploaded:
        st.warning("Please upload your CV.")
    elif not job_description.strip():
        st.warning("Please paste the job description.")
    else:
        st.success("Inputs confirmed! Scroll down to see the results.")

# Section 3: Process Skills and Compute Match
if cv_content and job_description:


    with st.spinner("Extracting Skills from CV and Job Description..."):
        cv_skills = extract_skills_from_text(cv_content, 'cv', nlp)
        job_skills = extract_skills_from_text(job_description, 'job_description', nlp)

    st.subheader("Extracted Skills")

    # CV Skills Word Cloud
    cv_wordcloud = WordCloud(background_color="white").generate(" ".join(cv_skills))
    job_wordcloud = WordCloud(background_color="white").generate(" ".join(job_skills))
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("CV Skills")
        fig, ax = plt.subplots()
        ax.imshow(cv_wordcloud, interpolation='bilinear')
        ax.axis("off")
        st.pyplot(fig)

    with col2:
        st.subheader("Job Skills")
        fig, ax = plt.subplots()
        ax.imshow(job_wordcloud, interpolation='bilinear')
        ax.axis("off")
        st.pyplot(fig)

    with st.spinner("Checking Education Match..."):
        education_match = check_education_match(cv_content, job_description)
    st.subheader("Education Match")
    st.write(education_match)

    with st.spinner("Computing Skill Match..."):
        score, missing_skills, overlapping_skills = compute_skill_score(
            cv_skills, job_skills, nlp
        )
    st.subheader("Skill Matching Result")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("#### Matching skills ✅")
        for skill in overlapping_skills:
            st.write(f"- {skill}")

    with col2:
        st.markdown("#### Skills you can consider learning and adding to your CV 📚")
        for skill in missing_skills:
            st.write(f"- {skill}")

