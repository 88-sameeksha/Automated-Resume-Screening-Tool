"""Optional Streamlit dashboard. Run with: streamlit run app.py"""
from pathlib import Path
import json
import tempfile
import streamlit as st
from src.extractor import extract_text
from src.matcher import score_resumes

BASE_DIR = Path(__file__).resolve().parent
st.set_page_config(page_title="Resume Relevance Analyzer", page_icon="📄", layout="wide")
st.title("Automated Resume Screening Tool")
st.caption("Educational resume-to-job relevance analysis. Human review is required.")

job_default = (BASE_DIR / "data" / "job_description.txt").read_text(encoding="utf-8")
skills_default = json.loads((BASE_DIR / "data" / "required_skills.json").read_text(encoding="utf-8"))

job = st.text_area("Job description", value=job_default, height=180)
skills_text = st.text_input("Required skills (comma-separated)", value=", ".join(skills_default))
uploads = st.file_uploader("Upload resumes (PDF, DOCX, TXT)", type=["pdf", "docx", "txt"], accept_multiple_files=True)

if st.button("Analyze resumes", type="primary"):
    skills = [s.strip() for s in skills_text.split(",") if s.strip()]
    candidates = []
    if not uploads:
        st.warning("Upload at least one resume.")
    elif not skills:
        st.warning("Enter at least one required skill.")
    else:
        for upload in uploads:
            suffix = Path(upload.name).suffix
            with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as temp:
                temp.write(upload.getvalue())
                temp_path = temp.name
            try:
                extracted = extract_text(temp_path)
                if extracted.strip():
                    candidates.append({"filename": upload.name, "text": extracted})
            finally:
                Path(temp_path).unlink(missing_ok=True)

        if candidates:
            results = score_resumes(job, skills, candidates)
            st.subheader("Resume relevance ranking")
            st.dataframe(results, use_container_width=True)
            import pandas as pd
            csv = pd.DataFrame(results).to_csv(index=False).encode("utf-8")
            st.download_button("Download CSV report", csv, "resume_ranking.csv", "text/csv")
            st.info("Use these transparent relevance signals only to organize human review. Do not use them as automatic hiring or rejection decisions.")
        else:
            st.error("No readable text was found. Scanned PDFs may require OCR, which is not included in this starter version.")
