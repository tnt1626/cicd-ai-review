from fastapi import FastAPI

app = FastAPI()

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.get("/message/{day}")
async def read_message(day: int):
    return {
        "message": "Day 1 of my project",
        "day": day
    }
