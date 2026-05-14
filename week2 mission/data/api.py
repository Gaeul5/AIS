import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def chat(messages, temperature=0.7):
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
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
