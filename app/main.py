# main.py
from fastapi import FastAPI
from tests.connection.db_conntction_test import mongo_test
from tests.connection.openai_test import chat_with_gpt
app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Hello, Hackathon!"}

@app.get("/test-db")
def test_db_connection():
    result = mongo_test()
    return result

@app.get("/test-gpt")
def test_gpt(prompt: str = "맞히다와 맞추다의 차이 알려줘"):
    result = chat_with_gpt(prompt)
    return {"result": result}

