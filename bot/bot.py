import os
import time
import logging
import asyncio
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from fastapi import FastAPI
from pydantic import BaseModel
import uvicorn


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()
API_TOKEN = os.environ['BOT_TOKEN']
PAYMENT_TOKEN = os.environ['PAYMENT_TOKEN']
CHAT_ID = '691902762'  # Telegram chat ID

app = FastAPI()

bot = Bot(token=API_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)


class CandleAnomalyDto(BaseModel):
    name: str
    priceCurrent: float
    volume: int
    priceDailyChangeAsPercentage: float
    priceMinuteChangeAsPercentage: float
    time: str  # Предполагаем, что time передаётся как строка в формате ISO


# Заглушка для handlers, если register_handlers не определён
try:
    from handlers import register_handlers
    register_handlers(dp)
except ImportError:
    logger.warning("Handlers not found, skipping registration")


@app.post("/items/")
async def create_item(item: CandleAnomalyDto):
    message = f"Received anomaly: {item.dict()}"
    logger.info(message)
    try:
        await bot.send_message(chat_id=CHAT_ID, text=message)
    except Exception as e:
        logger.error(f"Failed to send message to Telegram: {e}")
    return item  # Возвращаем тот же объект для согласованности с клиентом


@app.get("/items/")
async def get_item(item: str):
    message = f"Received GET item: {item}"
    logger.info(message)
    try:
        await bot.send_message(chat_id=CHAT_ID, text=message)
    except Exception as e:
        logger.error(f"Failed to send message to Telegram: {e}")
    return {"received_item": item}


async def start_telegram_bot():
    try:
        await dp.start_polling()
    except Exception as e:
        logger.error(f"Bot crashed: {e}", exc_info=True)
        await asyncio.sleep(5)
        await start_telegram_bot()


async def start_fastapi():
    config = uvicorn.Config(app, host="0.0.0.0", port=7000)
    server = uvicorn.Server(config)
    await server.serve()


async def main():
    await asyncio.gather(
        start_telegram_bot(),
        start_fastapi()
    )


if __name__ == "__main__":
    asyncio.run(main())