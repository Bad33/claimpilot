from pathlib import Path


def load_prompt(prompt_filename: str) -> str:
    prompt_path = Path("prompts") / prompt_filename
    return prompt_path.read_text(encoding="utf-8")