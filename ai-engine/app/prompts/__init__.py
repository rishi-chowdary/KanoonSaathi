from pathlib import Path

PROMPTS_DIR = Path(__file__).resolve().parent


def load_prompt(template_name: str, version: str = "v1") -> str:
    file_path = PROMPTS_DIR / version / f"{template_name}.txt"
    if not file_path.exists():
        raise FileNotFoundError(f"Prompt template '{template_name}' not found at {file_path}")
    return file_path.read_text(encoding="utf-8")
