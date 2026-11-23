"""Save ranking results as a CSV file."""
from pathlib import Path
import pandas as pd

def save_report(results: list[dict], output_path: str) -> str:
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    df = pd.DataFrame(results)
    df.insert(0, "rank", range(1, len(df) + 1))
    df.to_csv(path, index=False, encoding="utf-8-sig")
    return str(path)
