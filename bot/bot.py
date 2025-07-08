import io
import json
import os
import logging
import asyncio
from datetime import datetime

from aiogram.types import InputFile
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from fastapi import FastAPI, Request, HTTPException
import uvicorn
import requests

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()
API_TOKEN = os.environ['BOT_TOKEN']
PAYMENT_TOKEN = os.environ['PAYMENT_TOKEN']
CHAT_ID = '691902762'
MAKING_PHOTO_SERVICE_URL = 'http://photo_service:8003/generate-image'  # Изменил на 127.0.0.1

app = FastAPI()

bot = Bot(token=API_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

try:
    from handlers import register_handlers

    register_handlers(dp)
except ImportError:
    logger.warning("Handlers not found, skipping registration")


@app.post("/log-anomaly")
async def log_anomaly(request: Request):
    try:
        data = await request.json()
        logger.info("Received data: %s", data)

        service_data = {
            "name": data['name'],
            "priceCurrent": data['priceCurrent'],
            "volume": data['volume'],
            "priceDailyChangeAsPercentage": data['priceDailyChangeAsPercentage'],
            "priceMinuteChangeAsPercentage": data['priceMinuteChangeAsPercentage'],
            "time": int(datetime.strptime(data['time'], "%Y-%m-%dT%H:%M:%S.%fZ").timestamp()),
            "candlesLastHour": [
                {
                    "open": candle['open'],
                    "high": candle['high'],
                    "low": candle['low'],
                    "close": candle['close'],
                    "volume": candle['volume'],
                    "time": int(datetime.strptime(candle['timestamp'], "%Y-%m-%dT%H:%M:%S.%fZ").timestamp())
                }
                for candle in data['candlesLastHour']
            ]
        }

        logger.info(f"Sending to photo service: {service_data}")

        response = requests.post(
            MAKING_PHOTO_SERVICE_URL,
            headers={"Content-Type": "application/json"},
            json=service_data
        )

        response.raise_for_status()
        photo_data = response.json()
        logger.info(f"Photo service response: {photo_data}")

        if 'image_url' not in photo_data:
            raise ValueError("Invalid response from photo service: missing image_url")

        image_url = photo_data['image_url']
        image_response = requests.get(image_url)
        image_response.raise_for_status()

        photo_bytes = io.BytesIO(image_response.content)
        photo_bytes.name = "anomaly_photo.png"

        action_name = str(data['name'])
        price_change = str(data['priceMinuteChangeAsPercentage'])
        day_price_change = str(data['priceDailyChangeAsPercentage'])
        price = str(data['priceCurrent'])
        volume = str(data['volume'])
        time = str(data['time'])
        emoji = '🟢🟢🟢' if float(price_change) >= 0 else '🔴🔴🔴'

        message = (
            f"{emoji}\n\n"
            f"<b>{action_name.upper()} ({volume} ЛОТОВ)</b>\n\n"
            f"<i>Изменение цены: </i> <b>{price_change}%</b>\n"
            f"<i>Изменение за день: </i> <b>{day_price_change}%</b>\n"
            f"<i>Текущая цена: </i> <b>{price} р</b>\n"
            f"<i>Объём: </i> <b>{str(round((int(volume) * float(price)) / 1000))} млн р</b>\n\n"
            f"Время: {time}\n\n"
            "Замечено ботом @volumeHub_bot"
        )

        await bot.send_photo(
            chat_id=CHAT_ID,
            photo=InputFile(photo_bytes),
            caption=message,
            parse_mode="HTML"
        )

        return {"status": "success"}

    except requests.exceptions.RequestException as e:
        logger.error(f"Request error: {str(e)}")
        raise HTTPException(status_code=502, detail={"status": "error", "message": "Photo service unavailable"})
    except ValueError as e:
        logger.error(f"Value error: {str(e)}")
        raise HTTPException(status_code=500, detail={"status": "error", "message": str(e)})
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail={"status": "error", "message": "Internal server error"})


async def start_telegram_bot():
    try:
        await dp.start_polling()
    except Exception as e:
        logger.error(f"Bot crashed: {e}", exc_info=True)
        await asyncio.sleep(5)
        await start_telegram_bot()


async def start_fastapi():
    config = uvicorn.Config(app, host="0.0.0.0", port=5000)
    server = uvicorn.Server(config)
    await server.serve()


async def main():
    await asyncio.gather(
        start_telegram_bot(),
        start_fastapi()
    )


if __name__ == "__main__":
    asyncio.run(main())
