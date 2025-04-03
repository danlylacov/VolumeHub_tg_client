import os
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import pandas as pd
from PIL import Image, ImageDraw, ImageFont
import asyncio
import boto3
from matplotlib.dates import DateFormatter

# Настройка клиента S3 для LocalStack
s3_client = boto3.client(
    's3',
    endpoint_url='http://localhost:4566',
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
            volume_rub: str,
            today_growth: str,
            growth: str,
            buy: str,
            sell: str,
            candles: list
    ):
        self.action_name = action_name
        self.ticket = ticket
        self.price = price
        self.volume_lots = volume_lots
        self.volume_rub = volume_rub
        self.today_growth = today_growth
        self.growth = growth
        self.buy = buy
        self.sell = sell
        self.candles = candles
        self.output_path = f"make_image/result_{os.urandom(4).hex()}.png"

    async def generate_and_upload(self) -> str:
        await self._create_chart()
        await self._overlay_and_resize_images()
        bucket_name = "my-local-bucket"
        s3_key = f"photos/{os.path.basename(self.output_path)}"
        await self._upload_to_s3(bucket_name, s3_key)
        s3_url = f"http://localhost:4566/{bucket_name}/{s3_key}"
        os.remove("make_image/plot.png")
        os.remove(self.output_path)
        return s3_url

    async def _create_chart(self):
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

    def _plot_chart(self, stock_prices):
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
        plt.close()

    async def _overlay_and_resize_images(self):
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, self._overlay_images_sync)

    def _overlay_images_sync(self):
        background = Image.open('make_image/background.jpg')

        try:
            logo = Image.open(f'make_image/logos/{self.action_name}.png')
            logo = logo.convert("RGBA")
            logo = logo.resize((65, 65), Image.LANCZOS)
            background.paste(logo, (50, 50), logo)
            logo.close()
        except Exception as exc:
            print(f"Ошибка загрузки логотипа: {exc}")

        overlay = Image.open('make_image/plot.png')
        overlay = overlay.convert("RGBA")
        overlay = overlay.resize((480, 320), Image.LANCZOS)
        background.paste(overlay, (30, 350), overlay)
        overlay.close()

        draw = ImageDraw.Draw(background)
        font_path = "make_image/inter-bold-italic.ttf"

        def paste_text(text, position, color, size):
            font = ImageFont.truetype(font_path, size)
            draw.text(position, text, font=font, fill=color)

        paste_text(f"{self.action_name}", (130, 66), (255, 255, 255), 25)
        paste_text("Текущая цена:", (260, 120), (255, 255, 255), 17)
        paste_text(f"{self.price} ₽", (400, 115), (255, 255, 255), 25)
        paste_text(f'{self.volume_lots} лот', (50, 210), (255, 255, 255), 35)
        paste_text(f"{self.volume_rub} млн ₽", (200, 265), (255, 255, 255), 17)
        paste_text(f'{self.buy}%', (135, 292), (0, 255, 0), 17)
        paste_text(f'{self.sell}%', (135, 314), (255, 0, 0), 17)
        paste_text(f'{self.today_growth}%', (415, 210), (255, 255, 255), 17)
        paste_text(f'{self.growth}%', (415, 235), (255, 255, 255), 17)

        background.save(self.output_path)
        background.close()

    async def _upload_to_s3(self, bucket_name: str, s3_key: str):
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, lambda: s3_client.upload_file(self.output_path, bucket_name, s3_key))