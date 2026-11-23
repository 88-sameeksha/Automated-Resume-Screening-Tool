"""Command-line entry point for the Automated Resume Screening Tool."""
from pathlib import Path
import json
from src.extractor import extract_text
from src.matcher import score_resumes
from src.reporter import save_report

BASE_DIR = Path(__file__).resolve().parent

def main():
    resume_dir = BASE_DIR / "resumes"
    job_path = BASE_DIR / "data" / "job_description.txt"
    skills_path = BASE_DIR / "data" / "required_skills.json"
    output_path = BASE_DIR / "outputs" / "resume_ranking.csv"

    job_description = job_path.read_text(encoding="utf-8")
    required_skills = json.loads(skills_path.read_text(encoding="utf-8"))

    candidates = []
    for path in sorted(resume_dir.iterdir()):
        if path.is_file() and path.suffix.lower() in {".pdf", ".docx", ".txt"}:
            try:
                text = extract_text(str(path))
                if text.strip():
                    candidates.append({"filename": path.name, "text": text})
                else:
                    print(f"WARNING: No selectable text found in {path.name}")
            except Exception as exc:
                print(f"WARNING: Could not read {path.name}: {exc}")

    if not candidates:
        print("No readable resumes found. Add PDF, DOCX or TXT files to the resumes folder.")
        return

    results = score_resumes(job_description, required_skills, candidates)
    report = save_report(results, str(output_path))

    print("\\nAUTOMATED RESUME SCREENING – RELEVANCE REPORT")
    print("=" * 58)
    print(f"Resumes processed: {len(results)}")
    print(f"Required skills: {', '.join(required_skills)}")
    print("-" * 58)
    for rank, item in enumerate(results, start=1):
        print(f"{rank}. {item['filename']} | Relevance: {item['relevance_score_pct']}%")
        print(f"   Matched: {item['matched_skills'] or 'None detected'}")
        print(f"   Missing: {item['missing_skills'] or 'None'}")
        print(f"   Review signal: {item['review_priority']}")
    print("-" * 58)
    print(f"CSV report saved to: {report}")
    print("Reminder: scores support human review; they are not hiring decisions.")

if __name__ == "__main__":
    main()
