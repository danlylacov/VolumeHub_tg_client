from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from image_generator import ImageMaker
import logging
from datetime import datetime


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()


class Candle(BaseModel):
    open: float
    close: float
    high: float
    low: float
    volume: int
    time: int


class ImageRequest(BaseModel):
    name: str
    priceCurrent: float
    volume: int
    priceDailyChangeAsPercentage: float
    priceMinuteChangeAsPercentage: float
    time: int
    candlesLastHour: list[Candle]

    def to_image_maker_params(self):
        candles = [
            [
                datetime.fromtimestamp(candle.time / 1000).isoformat(),
                str(candle.open),
                str(candle.high),
                str(candle.low),
                str(candle.close)
            ]
            for candle in self.candlesLastHour
        ]
        return {
            "action_name": self.name,
            "ticket": "N/A",
            "price": str(self.priceCurrent),
            "volume_lots": str(self.volume),
            #"volume_rub": "N/A",
            "today_growth": str(self.priceDailyChangeAsPercentage),
            "growth": str(self.priceMinuteChangeAsPercentage),
            "candles": candles
        }


@app.post("/generate-image/")
async def generate_image_endpoint(request: ImageRequest):
    logger.info("Received request to generate image")
    try:
        params = request.to_image_maker_params()
        maker = ImageMaker(**params)
        image_url = await maker.generate_and_upload()
        logger.info(f"Image generated and uploaded: {image_url}")
        return {"image_url": image_url}
    except Exception as e:
        logger.error(f"Error in generate_image_endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Ошибка: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8003)