import os
import time
import logging
from dotenv.main import load_dotenv
from aiogram import Bot, Dispatcher, executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage

from handlers import register_handlers


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()
API_TOKEN = os.environ['BOT_TOKEN']
PAYMENT_TOKEN = os.environ['PAYMENT_TOKEN']

bot = Bot(token=API_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

register_handlers(dp)

if __name__ == "__main__":
    while True:
        try:
            executor.start_polling(dp, skip_updates=False)
        except Exception as e:
            logger.error(f"Bot crashed: {e}", exc_info=True)
            time.sleep(5)