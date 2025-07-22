import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()  # .env 파일에서 환경변수 읽어오기

def chat_with_gpt(prompt: str):
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise Exception("API Key not found in environment variable!")
    client = OpenAI(api_key=api_key)

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",  # or "gpt-4" if 계정 허용시
        messages=[
            {"role": "system", "content": "너는 초등학생 돌봄선생님이야."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=100
    )
    return response.choices[0].message.content
