import os
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import pandas as pd
from PIL import Image, ImageDraw, ImageFont
import asyncio
import boto3
from matplotlib.dates import DateFormatter
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

ENDPOINT_URL = os.getenv("AWS_ENDPOINT_URL", "http://localstack:4566")
PUBLIC_S3_URL = os.getenv("PUBLIC_S3_URL", ENDPOINT_URL)

s3_client = boto3.client(
    's3',
    endpoint_url=ENDPOINT_URL,
    aws_access_key_id='test',
    aws_secret_access_key='test',
    region_name='us-east-1'
)


class ImageMaker:
    def __init__(
            self,
            action_name: str,
            ticket: str,
            price: str,
            volume_lots: str,
            today_growth: str,
            growth: str,
            candles: list
    ):
        self.action_name = action_name
        self.ticket = ticket
        self.price = price
        self.volume_lots = volume_lots
        self.today_growth = today_growth
        self.growth = growth
        self.candles = candles
        self.output_path = f"make_image/result_{os.urandom(4).hex()}.png"

    async def generate_and_upload(self) -> str:
        logger.info("Starting generate_and_upload")
        await self._create_chart()
        logger.info("Chart created")
        await self._overlay_and_resize_images()
        logger.info("Image overlaid and resized")
        bucket_name = "my-local-bucket"
        s3_key = f"photos/{os.path.basename(self.output_path)}"
        await self._upload_to_s3(bucket_name, s3_key)
        logger.info(f"Uploaded to S3: {s3_key}")
        os.remove("make_image/plot.png")
        os.remove(self.output_path)
        logger.info("Temporary files removed")
        s3_url = f"{PUBLIC_S3_URL}/{bucket_name}/{s3_key}"
        logger.info(f"Generated S3 URL: {s3_url}")
        return s3_url

    async def _create_chart(self):
        logger.info("Creating chart")
        stocks = self.candles
        candle_count = len(stocks)
        if candle_count < 1:
            raise ValueError("Необходимо хотя бы одна свеча")

        time = datetime.fromisoformat(stocks[0][0]) + timedelta(hours=3)

        stock_prices = pd.DataFrame(
            {
                'open': [float(stocks[i][1]) for i in range(candle_count)],
                'close': [float(stocks[i][4]) for i in range(candle_count)],
                'high': [float(stocks[i][2]) for i in range(candle_count)],
                'low': [float(stocks[i][3]) for i in range(candle_count)]
            },
            index=pd.date_range(str(time).split('+')[0], periods=candle_count, freq="1min")
        )

        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, self._plot_chart, stock_prices)
        logger.info("Chart plotted")

    def _plot_chart(self, stock_prices):
        logger.info("Plotting chart")
        fig, ax = plt.subplots(figsize=(10, 6), facecolor=(0x1A / 255, 0x1B / 255, 0x26 / 255))
        ax.set_facecolor((0x1A / 255, 0x1B / 255, 0x26 / 255))

        up = stock_prices[stock_prices.close >= stock_prices.open]
        down = stock_prices[stock_prices.close < stock_prices.open]

        col2 = (1, 0, 0)  # Красный
        col1 = (0, 1, 0)  # Зеленый

        width = 0.0005
        width2 = 0.0001

        plt.bar(up.index, up.close - up.open, width, bottom=up.open, color=col1)
        plt.bar(up.index, up.high - up.close, width2, bottom=up.close, color=col1)
        plt.bar(up.index, up.low - up.open, width2, bottom=up.open, color=col1)

        plt.bar(down.index, down.close - down.open, width, bottom=down.open, color=col2)
        plt.bar(down.index, down.high - down.open, width2, bottom=down.open, color=col2)
        plt.bar(down.index, down.low - down.close, width2, bottom=down.close, color=col2)

        plt.gca().xaxis.set_major_formatter(DateFormatter('%H:%M'))
        plt.xticks(rotation=0, ha='center')
        plt.grid(True, linestyle='--', alpha=0.7)
        plt.tick_params(axis='both', colors='white')
        plt.gca().spines['bottom'].set_color('white')
        plt.gca().spines['top'].set_color('white')
        plt.gca().spines['right'].set_color('white')
        plt.gca().spines['left'].set_color('white')

        plt.savefig('make_image/plot.png', format='png', bbox_inches='tight')
        if not os.path.exists('make_image/plot.png'):
            logger.error("plot.png was not created")
            raise RuntimeError("Failed to create plot.png")
        plt.close()
        logger.info("Chart saved as plot.png")

    async def _overlay_and_resize_images(self):
        logger.info("Overlaying and resizing images")
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, self._overlay_images_sync)

    def _overlay_images_sync(self):
        logger.info("Starting overlay_images_sync")
        try:
            background = Image.open('make_image/background.jpg')
            logger.info("Background image opened")
        except Exception as e:
            logger.error(f"Failed to open background image: {e}")
            raise

        try:
            overlay = Image.open('make_image/plot.png')
            overlay = overlay.convert("RGBA")
            overlay = overlay.resize((500, 360), Image.LANCZOS)
            background.paste(overlay, (30, 320), overlay)
            overlay.close()
            logger.info("Overlay applied")
        except Exception as e:
            logger.error(f"Failed to apply overlay: {e}")
            raise

        draw = ImageDraw.Draw(background)
        font_path = "make_image/inter-bold-italic.ttf"

        try:
            font = ImageFont.truetype(font_path, 25)
            logger.info("Font loaded")
        except Exception as e:
            logger.error(f"Failed to load font: {e}")
            raise

        def paste_text(text, position, color, size):
            font = ImageFont.truetype(font_path, size)
            draw.text(position, text, font=font, fill=color)

        paste_text(f"{self.action_name}", (130, 66), (255, 255, 255), 25)
        paste_text("Текущая цена:", (260, 120), (255, 255, 255), 17)
        paste_text(f"{self.price} ₽", (400, 115), (255, 255, 255), 25)
        paste_text(f'{self.volume_lots} лот', (50, 217), (255, 255, 255), 35)
        paste_text(f'{self.today_growth}%', (435, 222), (255, 255, 255), 17)
        paste_text(f'{self.growth}%', (435, 250), (255, 255, 255), 17)
        logger.info("Text applied")

        try:
            background.save(self.output_path)
            logger.info(f"Image saved to {self.output_path}")
        except Exception as e:
            logger.error(f"Failed to save image: {e}")
            raise

        background.close()
        logger.info("Background image closed")

    async def _upload_to_s3(self, bucket_name: str, s3_key: str):
        logger.info(f"Uploading to S3: {bucket_name}/{s3_key}")
        loop = asyncio.get_event_loop()
        try:
            await loop.run_in_executor(None, lambda: s3_client.upload_file(self.output_path, bucket_name, s3_key))
            logger.info("Upload successful")
        except Exception as e:
            logger.error(f"Failed to upload to S3: {e}")
            raise
