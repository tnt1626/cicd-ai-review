import os
import sys
import time
import argparse
import requests
from pathlib import Path
from dotenv import load_dotenv
from groq import APIError, Groq, RateLimitError

# load_dotenv()
api_key = os.environ.get("GROQ_API_KEY")
if not api_key:
    raise EnvironmentError("GROQ_API_KEY is not set. Add it to your .env file or GitHub Secrets.")
client = Groq(api_key=api_key)

github_token = os.environ.get("GITHUB_TOKEN")
github_repository = os.environ.get("GITHUB_REPOSITORY")

def truncate_diff(diff: str, max_chars: int = 15000) -> str:
    if len(diff) <= max_chars:
        return diff
    lines, result, count = diff.splitlines(), [], 0
    for line in lines:
        if count + len(line) > max_chars:
            break
        result.append(line)
        count += len(line)
    return "\n".join(result) + "\n\n[diff truncated — too large]"


def get_system_prompt() -> str:
    file_path = Path(__file__).parent.parent / "text" / "system_prompt.md"
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()

def get_diff() -> str:
    # 1. stdin (pipe)
    if not sys.stdin.isatty():
        diff = sys.stdin.read().strip()
        if diff:
            return diff

    # 2. file fallback
    diff_file = Path(__file__).parent.parent / "text" / "diff.txt"
    if diff_file.exists():
        return diff_file.read_text(encoding="utf-8")

    # 3. final fallback
    return ""


def get_user_prompt(diff: str) -> str:
    return f"Review this git diff:\n\n{diff}"

def save_review_text(review_text: str):
    file_path = Path(__file__).parent.parent / "text" / "review.md"
    with open(file_path, "w", encoding="utf-8") as f:
            f.write(review_text)


def generate_review(diff: str) -> str:
    user_prompt = get_user_prompt(diff)
    system_prompt = get_system_prompt()

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        max_tokens=1024,
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
    
    diff = truncate_diff(diff)
    
    # Testcase 2 & 3: Rate limit & API error
    for i in range(3):
        try:
            return generate_review(diff)
        
        except (RateLimitError, APIError) as e:
            if i == 2:
                raise
            print(f"[retry {i+1}/3] {type(e).__name__}: {e}", file=sys.stderr)
            time.sleep(2 ** i)

    raise Exception("Rate limit exceeded after retries")

def post_review_comment(review_text: str, pr_num: str, repo: str) -> None:
    if not github_token:
        print("[skip] GITHUB_TOKEN not set — skipping PR comment", file=sys.stderr)
        return
    if not pr_num or not repo:
        print("[skip] pr_number or repo not provided — skipping PR comment", file=sys.stderr)
        return

    url = f"https://api.github.com/repos/{repo}/issues/{pr_num}/comments"
    headers = {
        "Authorization": f"Bearer {github_token}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28"
    }
    
    response = requests.post(url=url, headers=headers, json={"body": review_text})

    if response.status_code == 201:
        print(f"[ok] Review posted to PR #{pr_num}")
    else:
        print(f"[error] GitHub API {response.status_code}: {response.text}", file=sys.stderr)


def main():
    parser = argparse.ArgumentParser(description="AI Code Review Bot")
    parser.add_argument("--pr-number", type=int, help="Pull request number")
    parser.add_argument("--repo", default=github_repository, help="owner/repo format")
    args = parser.parse_args()

    review_text = get_ai_review()
    save_review_text(review_text)
    post_review_comment(review_text, str(args.pr_number), args.repo)
    print(review_text)

if __name__ == "__main__":
    main()