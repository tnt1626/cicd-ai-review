import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from groq import Groq

load_dotenv()
api_key = os.environ.get("GROQ_API_KEY")

def get_system_prompt() -> str:
    with open("../text/system_prompt.md", "r", encoding="utf-8") as f:
        system_prompt = f.read()
    return system_prompt


def get_diff() -> str:
    # 1. stdin (pipe)
    if not sys.stdin.isatty():
        diff = sys.stdin.read().strip()
        if diff:
            return diff

    # 2. file fallback
    diff_file = Path("../text/diff.txt")
    return diff_file.read_text(encoding="utf-8")


def get_user_prompt(diff: str) -> str:
    user_prompt = f"""
        Review this git diff:

        <diff>
        {diff}
        <diff>
    """
    return user_prompt

def save_review_text(review_text: str):
    with open("../text/review.md", "w", encoding="utf-8") as f:
        f.write(review_text)

# TODO: handle errors
def get_ai_review(user_prompt: str, system_prompt: str) -> str:
    client = Groq(api_key=api_key)
    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{
            "role": "system",
            "content": system_prompt,
            "role": "user", 
            "content": user_prompt
        }]
    )
    review_text = response.choices[0].message.content
    return review_text

def main():
    system_prompt = get_system_prompt()
    diff = get_diff()
    user_prompt = get_user_prompt(diff)

    review_text = get_ai_review(user_prompt, system_prompt)
    save_review_text(review_text)

    print(review_text)

if __name__ == "__main__":
    main()