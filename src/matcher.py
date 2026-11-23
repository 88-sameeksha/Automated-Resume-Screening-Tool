"""Transparent resume-to-job relevance scoring using skills + TF-IDF."""
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from .processor import clean_text, find_skills

def score_resumes(job_description: str, required_skills: list[str],
                  candidates: list[dict]) -> list[dict]:
    job_clean = clean_text(job_description)
    resume_texts = [clean_text(item["text"]) for item in candidates]

    # Fit on the job description and all resumes so they share one vector space.
    vectorizer = TfidfVectorizer(ngram_range=(1, 2), stop_words="english")
    matrix = vectorizer.fit_transform([job_clean] + resume_texts)
    similarities = cosine_similarity(matrix[0:1], matrix[1:]).flatten()

    results = []
    for candidate, similarity in zip(candidates, similarities):
        matched = find_skills(candidate["text"], required_skills)
        missing = [s for s in required_skills if s not in matched]
        skill_coverage = len(matched) / len(required_skills) if required_skills else 0.0
        # Score is an explainable relevance indicator, not a hiring probability.
        final_score = (0.60 * skill_coverage + 0.40 * float(similarity)) * 100

        results.append({
            "filename": candidate["filename"],
            "matched_skills": ", ".join(matched),
            "missing_skills": ", ".join(missing),
            "matched_skill_count": len(matched),
            "required_skill_count": len(required_skills),
            "skill_coverage_pct": round(skill_coverage * 100, 2),
            "tfidf_similarity_pct": round(float(similarity) * 100, 2),
            "relevance_score_pct": round(final_score, 2),
            "review_priority": "Higher review priority" if final_score >= 50 else "Further review needed"
        })
    return sorted(results, key=lambda x: x["relevance_score_pct"], reverse=True)
