"""Text normalization and simple skill extraction."""
import re

def clean_text(text: str) -> str:
    text = text.lower()
    text = text.replace("&", " and ")
    text = re.sub(r"[^a-z0-9+#.\s-]", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()

def find_skills(text: str, skills: list[str]) -> list[str]:
    cleaned = clean_text(text)
    found = []
    for skill in skills:
        # Match whole phrases/terms rather than partial words.
        pattern = r"(?<![a-z0-9])" + re.escape(skill.lower()) + r"(?![a-z0-9])"
        if re.search(pattern, cleaned):
            found.append(skill)
    return found
