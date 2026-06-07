import os
from dotenv import load_dotenv
from groq import Groq

load_dotenv()


api_key = os.environ.get("GROQ_API_KEY")


system_prompt = """
    You are a code reviewer. Review this diff and give concise, actionable feedback. 
    Focus on: bugs, security issues, and code quality. 
    Be specific about line numbers if possible.
"""


with open("../text/diff.txt", "r", encoding="utf-8") as f:
    diff = f.read()

user_prompt = f"""
    Review this git diff:

    <diff>
    {diff}
    <diff>
"""

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
with open("../text/review.md", "w", encoding="utf-8") as f:
    f.write(review_text)

print(review_text)