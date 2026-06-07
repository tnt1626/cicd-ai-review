import os
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

api_key = os.environ.get("GROQ_API_KEY")

client = Groq(api_key=api_key)
response = client.chat.completions.create(
    model="llama-3.1-8b-instant",
    messages=[{"role": "user", "content": "Review this code: print('hello')"}]
)
print(response.choices[0].message.content)