# main.py
from fastapi import FastAPI
from app.core.db_conntction_test import mongo_test

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Hello, Hackathon!"}

@app.get("/test-db")
def test_db_connection():
    result = mongo_test()
    return result
