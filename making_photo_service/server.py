from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from image_generator import ImageMaker

app = FastAPI()


class ImageRequest(BaseModel):
    action_name: str
    ticket: str
    price: str
    volume_lots: str
    volume_rub: str
    today_growth: str
    growth: str
    buy: str
    sell: str
    candles: list


@app.post("/generate-image/")
async def generate_image_endpoint(request: ImageRequest):
    try:
        maker = ImageMaker(
            action_name=request.action_name,
            ticket=request.ticket,
            price=request.price,
            volume_lots=request.volume_lots,
            volume_rub=request.volume_rub,
            today_growth=request.today_growth,
            growth=request.growth,
            buy=request.buy,
            sell=request.sell,
            candles=request.candles
        )
        image_url = await maker.generate_and_upload()
        return {"image_url": image_url}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)