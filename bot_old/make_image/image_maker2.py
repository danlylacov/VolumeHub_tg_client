import os
from datetime import datetime, timedelta

import matplotlib.pyplot as plt
import pandas as pd
import requests
from PIL import Image, ImageDraw, ImageFont
from dotenv import load_dotenv
from matplotlib.dates import DateFormatter


class ImageMaker():

    def __init__(self, figi: str, action_name: str, ticket: str, price: str, volume_lots: str, volume_rub: str,
                 today_growth: str,
                 growth: str, buy: str, sell: str, name_of_logo_photo: str = ''):
        self._create_chart(figi)
        plt.close()
        self._overlay_and_resize_images('make_image/background.jpg', 'make_image/plot.png',
                                        f'make_image/logos/{figi}.png', 'result.png',
                                        action_name, ticket, price, volume_lots, volume_rub, today_growth, growth, buy,
                                        sell)

    def _create_chart(self, figi: str):
        load_dotenv()
        API_URL = os.environ['API_URL']  # API_URL
        stocks = list(requests.get(f'{API_URL}/get_hour_data/{figi}').json())

        time = datetime.fromisoformat(stocks[0][-1]) + timedelta(hours=3)

        stock_prices = pd.DataFrame(
            {
                'open': [float(stocks[i][1]) for i in range(60)],
                'close': [float(stocks[i][4]) for i in range(60)],
                'high': [float(stocks[i][2]) for i in range(60)],
                'low': [float(stocks[i][3]) for i in range(60)]
            },
            index=pd.date_range(str(time).split('+')[0], periods=60, freq="1min")
        )

        # Создание фигуры и оси
        fig, ax = plt.subplots(figsize=(10, 6), facecolor=(0x1A / 255, 0x1B / 255, 0x26 / 255))

        # Установка цвета фона графика (под свечами)
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

        # Добавление сетки
        plt.grid(True, linestyle='--', alpha=0.7)

        # Установка цвета меток на черный
        plt.tick_params(axis='both', colors='white')

        # Установка цвета осей на черный
        plt.gca().spines['bottom'].set_color('white')
        plt.gca().spines['top'].set_color('white')
        plt.gca().spines['right'].set_color('white')
        plt.gca().spines['left'].set_color('white')

        plt.savefig('make_image/plot.png', format='png', bbox_inches='tight')

        plt.close()

    def _overlay_and_resize_images(
            self, background_path, overlay_path, logo_overlay_path, output_path,
            action_name: str, ticket: str, price: str, volume_lots: str, volume_rub: str,
            today_growth: str,
            growth: str, buy: str, sell: str
    ):

        def paste_text(text, position, color, size): # Вынести
            draw = ImageDraw.Draw(background)
            text_position = position
            text_color = color
            font_path = "make_image/inter-bold-italic.ttf"
            font = ImageFont.truetype(font_path, size)

            try:
                draw.text(text_position, text, font=font, fill=text_color)
            except Exception as e:
                print(f"Error drawing text: {e}")

        background = Image.open(background_path)
        try:
            # логотип
            logo = Image.open(logo_overlay_path)
            logo = logo.convert("RGBA")
            logo = logo.resize((65, 65), Image.LANCZOS)
            background.paste(logo, (50, 50), logo)
            logo.close()
        except Exception as exc:
            print(exc)

        # график
        overlay = Image.open(overlay_path)
        overlay = overlay.convert("RGBA")
        overlay = overlay.resize((480, 320), Image.LANCZOS)
        background.paste(overlay, (30, 350), overlay)
        overlay.close()

        paste_text(f"{action_name}", (130, 66), (255, 255, 255), 25)
        paste_text("Текущая цена:", (260, 120), (255, 255, 255), 17)
        paste_text(f"{price} ₽", (400, 115), (255, 255, 255), 25)
        paste_text(f'{volume_lots} лот', (50, 210), (255, 255, 255), 35)
        paste_text(f"{volume_rub} млн ₽", (200, 265), (255, 255, 255), 17)
        paste_text(f'{buy}%', (135, 292), (0, 255, 0), 17)
        paste_text(f'{sell}%', (135, 314), (255, 0, 0), 17)
        paste_text(f'{today_growth}%', (415, 210), (255, 255, 255), 17)
        paste_text(f'{growth}%', (415, 235), (255, 255, 255), 17)

        background.save(output_path)

        background.close()


mk_image = ImageMaker('BBG004730RP0', 'Газпром ', 'BANEP', '1000', '13453', '4.6', '1.2', '0.5', '40', '60')
