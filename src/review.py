import os
import sys
from pathlib import Path
import time
from dotenv import load_dotenv
from groq import Groq, RateLimitError

load_dotenv()
api_key = os.environ.get("GROQ_API_KEY")

def get_system_prompt() -> str:
    with open("../text/system_prompt.md", "r", encoding="utf-8") as f:
        return f.read()

def get_diff() -> str:
    # 1. stdin (pipe)
    if not sys.stdin.isatty():
        diff = sys.stdin.read().strip()
        if diff:
            return diff

    # 2. file fallback
    diff_file = Path("../text/diff.txt")
    if diff_file.exists():
        return diff_file.read_text(encoding="utf-8")

    # 3. final fallback
    return ""


def get_user_prompt(diff: str) -> str:
    user_prompt = f"""
        Review this git diff:

        {diff}
    """
    return user_prompt

def save_review_text(review_text: str):
    with open("../text/review.md", "w", encoding="utf-8") as f:
        f.write(review_text)


def generate_review(diff: str) -> str:
    user_prompt = get_user_prompt(diff)
    system_prompt = get_system_prompt()

    client = Groq(api_key=api_key)
    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
    )
    review_text = response.choices[0].message.content
    return review_text


def get_ai_review() -> str:
    # Testcase 1: Empty diff
    diff = get_diff()
    if not diff.strip():
        return "No diff found"
    
    # Testcase 2 & 3: Rate limit & API error
    for i in range(3):
        try:
            return generate_review(diff)
        except RateLimitError:
            time.sleep(2 ** i)
            diff = diff[:8000] # should use another way to reduce the complexity

    raise Exception("Rate limit exceeded after retries")
    

def main():
    review_text = get_ai_review()
    save_review_text(review_text)

    print(review_text)

if __name__ == "__main__":
    main()