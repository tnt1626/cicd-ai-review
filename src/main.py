from fastapi import FastAPI
from src.helper import mlflow_reviews_stats

app = FastAPI()

@app.get("/health")
async def health_check():
    """
    Liveness check used by deployment/monitoring tools
    """
    return {"status": "healthy"}


@app.get("/reviews/stats")
async def get_reviews_stats():
    """
    Aggregated AI review statistics sourced from MLflow
    """
    response = await mlflow_reviews_stats()
    return response

