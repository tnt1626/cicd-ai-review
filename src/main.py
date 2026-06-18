from fastapi import FastAPI
from src.helper import mlflow_reviews_stats

app = FastAPI()

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.get("/message/{day}")
async def read_message(day: int):
    return {
        "message": "Test Workflow",
        "day": day
    }

@app.get("reviews/stats")
async def get_reviews_stats():
    response = await mlflow_reviews_stats()
    return response

