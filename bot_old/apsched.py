import os
import sys
from datetime import datetime

import requests
from aiogram import Bot, types
from dotenv import load_dotenv

from adminDB import UsersDataBase
from make_image.image_maker2 import ImageMaker

load_dotenv()
API_URL = os.environ['API_URL']


async def send_message_interval(bot: Bot):
    print('Sched func works!')
    print(datetime.utcnow())
    anomal_volume_notes = dict(requests.get(f'{API_URL}/get_anomal_volumes').json())
    print('anomal_volume_notes takes: ', sys.getsizeof(anomal_volume_notes))
    users_db = UsersDataBase()

    for id in anomal_volume_notes.keys():
        note = anomal_volume_notes[id]
        action_name = str(note['action_name'])
        price_change = str(note['price_change'])
        day_price_change = str(note['day_price_change'])
        price = str(note['price'])
        volume = str(note['volume'])
        time = str(note['time'])
        amoj = '🟢🟢🟢' if float(price_change) >= 0 else '🔴🔴🔴'
        print('request figi', datetime.now())
        print('act name:', action_name)
        figi = requests.get(f'{API_URL}/get_figi_by_action_name/{action_name[:-1]}').json()
        print('figi takes: ', sys.getsizeof(figi))

        print('request book', datetime.now())

        print('Figi', figi)
        try:
            book = requests.get(f'{API_URL}/get_order_book_percent/{figi}').json()

            print(book)

            ask, bid = book['ask'], book['bid']
        except:
            ask, bid = None, None



        ImageMaker(figi, action_name, '', price, volume, str(round((int(volume) * float(price)) / 1000)),
                   day_price_change,
                   price_change, ask, bid)
        print('Image maker end work', datetime.now())

        for chat_id in users_db.get_subscriptors_ids():
            photo_path = 'result.png'
            message = amoj + "\n\n" + \
                      f"<b>{action_name.upper()} ({volume} ЛОТОВ)</b>\n\n" + \
                      f"<i>Изменение цены: </i> <b>{price_change}%</b>\n" + \
                      f"<i>Изменение за день: </i> <b>{day_price_change}%</b>\n" + \
                      f"<i>Текущая цена: </i> <b>{price} р</b>\n" + \
                      f"<i>Объём: </i> <b>{str(round((int(volume) * float(price)) / 1000))} млн р</b>\n\n" + \
                      f"🟩<i>Покупка: </i> <b>{ask}%</b>\n" + \
                      f"🟥<i>Продажа: </i> <b>{bid}%</b>\n\n" + \
                      f"Время: {time}\n\n" + \
                      "Замечено ботом @volumeHub_bot"

            with open(photo_path, 'rb') as photo:
                try:
                    await bot.send_photo(
                        chat_id=chat_id,
                        caption=message,
                        photo=types.InputFile(photo),
                        parse_mode='HTML'
                    )
                    photo.close()
                except:
                    pass
            print('mes sent!', datetime.now())



        requests.get(f'{API_URL}/delete_anomal_volume/{id}')

        print('Sched func end work', datetime.now())
    users_db.db.close()


async def subscription_reminder(bot: Bot):
    print('subscription_reminder works!', datetime.now())
    users_db = UsersDataBase()
    for users_id in users_db.get_subscriptors_ids():
        if users_id == '-':
            continue

        date_str = users_db.get_subscription(users_id).split('.')[0]
        print(date_str)
        date_format = "%Y-%m-%d %H:%M:%S"
        subscription_datetime = datetime.strptime(date_str, date_format)
        remaining_subscription_in_days = int(str(subscription_datetime - datetime.now()).split(' ')[0])
        print(remaining_subscription_in_days)
        if remaining_subscription_in_days < 3:
            await bot.send_message(
                users_id,
                (f'❗️❗️❗\nВнимание!\nВаша подписка истекает {subscription_datetime.date()}.'
                 f'\nПродлите её сейчас, чтобы и дальше получать уведомления об аномальных объемах!')
            )
    users_db.db.close()
    print('subscription_reminder end work!', datetime.now())
