import os
import pathlib
from openai import OpenAI
from dotenv import load_dotenv

# api.py 위치에서 상위로 올라가며 .env 탐색 (실행 위치와 무관하게 동작)
for _parent in pathlib.Path(__file__).resolve().parents:
    if (_parent / '.env').exists():
        load_dotenv(_parent / '.env')
        break
client = OpenAI(
    api_key=os.getenv("GROQ_API_KEY"),
    base_url="https://api.groq.com/openai/v1",
)


def chat(messages, temperature=0.7):
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=messages,
        temperature=temperature,
    )
    return response.choices[0].message.content


def print_result(label, question, response):
    print(f"\n{'='*60}")
    print(f"[{label}]")
    print(f"Q: {question}")
    print(f"{'-'*60}")
    print(response)
