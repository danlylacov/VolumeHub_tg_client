from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class CandleAnomalyDto(BaseModel):
    symbol: str
    volume: float

@app.post("/items/")
async def create_item(item: CandleAnomalyDto):
    print(item)
    return item


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=7000)
