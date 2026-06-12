from fastapi import FastAPI

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

@app.get("/test/{day}")
async def read_message(day: int):
    return f"Test {day}"
