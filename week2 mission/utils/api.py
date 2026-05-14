import os
from openai import OpenAI
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv(usecwd=True))
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
