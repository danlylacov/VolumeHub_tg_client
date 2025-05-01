from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()

@app.post("/items/")
@app.get("/items/")
async def create_item(item: str):
    print(item)
    return {"received_item": item}



if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=7000)
