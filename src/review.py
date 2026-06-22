import os
import sys
import time
import argparse
import requests
import mlflow
from pathlib import Path
from dotenv import load_dotenv
from groq import APIError, Groq, RateLimitError
from prometheus_client import Counter, Gauge, Histogram


load_dotenv()
api_key = os.environ.get("GROQ_API_KEY")
if not api_key:
    raise EnvironmentError("GROQ_API_KEY is not set. Add it to your .env file or GitHub Secrets.")
client = Groq(api_key=api_key)

github_token = os.environ.get("GITHUB_TOKEN")
github_repository = os.environ.get("GITHUB_REPOSITORY")
env = os.environ.get("ENV", "dev")

MAX_CHARS = 15000

review_counter = Counter("ai_reviews_total", "Total AI reviews run")
review_latency = Histogram("ai_review_latency_seconds", "Review latency")
review_errors = Counter("ai_review_errors_total", "Total review errors", ["error_type"])
active_reviews = Gauge("ai_reviews_in_progress", "Reviews currently running")

def prepare_mlflow_run():
    """
    Prepare tracking URI and setup experiment name for both environment
    """
    mlflow.set_tracking_uri(os.environ.get("MLFLOW_TRACKING_URI", "http://localhost:5001"))
    mlflow.set_experiment(f"pr-reviews-{env}")

def truncate_diff(diff: str, max_chars: int = MAX_CHARS) -> str:
    """
    Preprocessing `diff` text by truncation method before feeding LLM
    """
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
    """
    Get system prompt with `production` alias on MLflow server
    """
    loaded = mlflow.genai.load_prompt("prompts:/ai-review-prompt@production")
    system_prompt = loaded.template
    return system_prompt

def get_diff() -> str:
    """
    Prepare `diff` text with 3 different methods
        - Using pipeline with command
        - Getting diff text saved in file
        - Fallback to an empty string if two above methods not availabel
    """
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
    """
    Define a user prompt as an input for LLM model with `diff` text
    """
    return f"Review this git diff:\n\n{diff}"

def save_review_text(review_text: str):
    """
    Save LLM's output as a review for code source of recent commit
    """
    file_path = Path(__file__).parent.parent / "text" / "review.md"
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(review_text)


def generate_review(diff: str) -> str:
    """
    Define main logic for generting review using LLM
    and monitor with Mlflow
    """
    active_reviews.inc()
    review_counter.inc()
    prepare_mlflow_run()
    with mlflow.start_run():
        try:
            user_prompt = get_user_prompt(diff)
            system_prompt = get_system_prompt()
            prompt = mlflow.genai.register_prompt(
                name="ai-review-prompt",
                template=system_prompt,
                commit_message="Auditor persona",
            )
            mlflow.log_param('prompt_version', prompt.version)
            mlflow.log_param('model_name', 'llama-3.3-70b-versatile')
            mlflow.log_param('truncated', len(diff) >= MAX_CHARS)
            mlflow.log_metric('diff_size_chars', len(diff))
            mlflow.log_text(diff, "input_diff.txt")

            start_time = time.perf_counter()
            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                max_tokens=1024,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ]
            )    
            end_time = time.perf_counter()
            response_latency_seconds = end_time - start_time

            review_latency.observe(response_latency_seconds)

            mlflow.log_metric('token_count_input', response.usage.prompt_tokens)
            mlflow.log_metric('token_count_output', response.usage.completion_tokens)
            mlflow.log_metric('latency_seconds', round(response_latency_seconds, 2))
            mlflow.log_metric('token_per_second', round(response.usage.completion_tokens / response_latency_seconds, 1))

            review_text = response.choices[0].message.content
            mlflow.log_text(review_text, "review_output.md")

            mlflow.set_tag('status', 'success')
        except Exception as e:
            review_errors.labels(error_type=type(e).__name__).inc()
            active_reviews.dec()
            mlflow.set_tag('status', 'failed')
            mlflow.set_tag('error', str(e))
            raise
    
    active_reviews.dec()
    return review_text


def get_ai_review() -> str:
    """
    Define main pipeline to get AI review text
    """
    diff = get_diff()
    if not diff.strip():
        return "No diff found"
    
    diff = truncate_diff(diff)
    
    for i in range(3):
        try:
            return generate_review(diff)
        
        except (RateLimitError, APIError) as e:
            if i == 2:
                raise
            print(f"[retry {i+1}/3] {type(e).__name__}: {e}", file=sys.stderr)
            time.sleep(2 ** i)
    
    raise RuntimeError("Unreachable: retry loop exited without returning or raising")


def post_review_comment(review_text: str, pr_num: str, repo: str) -> None:
    """
    Post AI review text with Public GitHub API
        - review_text: text generated by LLM after reviewing `diff` on PR
        - pr_num: the number of PR that we get diff text
        - repo: name of repository
    """
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

    try:
        review_text = get_ai_review()
    except Exception as e:
        print(f"[fatal] {e}", file=sys.stderr)
        sys.exit(1)

    save_review_text(review_text)
    post_review_comment(review_text, str(args.pr_number), args.repo)
    print(review_text)

if __name__ == "__main__":
    main()