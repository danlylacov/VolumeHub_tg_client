import os
import time
from datetime import datetime

import pandas as pd
from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.types import ParseMode, ContentType, InputFile
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from dotenv.main import load_dotenv
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup

from adminDB import UsersDataBase
from apsched import send_message_interval, subscription_reminder
from keyboards import start_keyboard, payment_keyboard, PRICES_FOR_PAYMENT, promo_pay_keyboard

load_dotenv()
API_TOKEN = os.environ['BOT_TOKEN']
PAYMENT_TOKEN = os.environ['PAYMENT_TOKEN']

bot = Bot(token=API_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)



class UserStates(StatesGroup):
    get_promo_state = State()


@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    db = UsersDataBase()
    db.add_user(userid=message.from_user.id,  username=message.from_user.username)
    db.db.close()
    await bot.send_message(message.chat.id, "🙋 ‍Привет! Это бот VolumeHub!\n\n"
                                            "📍 Что делает бот?\n\n"
                                            "✅ Считывает данные минутных свечей по 146 акциям мосбиржи(первый и второй эшелоны просматривает на 100%).\n\n"
                                            "✅ Если объём (изменение цены) за минуту превышает 97.5% минутного объёма (изменения цены) за последнюю неделю, присылает пользователю развернутое уведомление.\n\n"
                                            "👇👇👇"
                                            "Наш официальный telegram-канал: https://t.me/volumeHub",
                           reply_markup=start_keyboard)






@dp.message_handler(commands=['admin_4_zDvrPlEG_getusers'])
async def get_users(message: types.Message):
    db = UsersDataBase()
    users = db.get_all_users()
    db.db.close()
    result = ''
    users_with_sub = 0
    users_without_sub = 0

    data = []
    columns = ['id', 'userId', 'Username', 'Subscription']

    for user in users:
        result += str(user) + '\n'

        if user[3] == '-':
            users_without_sub += 1
        else:
            date_str = str(user[3]).split('.')[0]
            date_format = "%Y-%m-%d %H:%M:%S"
            subscription_datetime = datetime.strptime(date_str, date_format)

            if subscription_datetime > datetime.now():
                users_with_sub += 1

        data.append(user)

    df = pd.DataFrame(data, columns=columns)

    excel_filename = 'users_data.xlsx'
    df.to_excel(excel_filename, index=False)

    users_document = InputFile(excel_filename)
    await bot.send_document(message.chat.id, users_document,
                            caption='Количество пользователей всего: ' + str(len(users)) +
                                    '\nКоличество пользователей с подпиской: ' + str(users_with_sub) +
                                    '\nКоличество пользователей без подписки: ' + str(users_without_sub))


@dp.message_handler(commands=['admin_4_zDvrPlEG_getpayments'])
async def get_payments(message: types.Message):
    db = UsersDataBase()
    payments = db.get_all_payments()
    db.db.close()

    df = pd.DataFrame(payments, columns=['id', 'paymentId', 'fromId', 'firstName', 'username', 'lngCode', 'currencu',
                                         'totalAmount', 'date'])  # Замените названия колонок

    df.to_excel('payments.xlsx', index=False)

    payments_document = InputFile('payments.xlsx')
    await bot.send_document(message.chat.id, payments_document)


@dp.message_handler(content_types=['text'])
async def menu(message: types.Message):
    if message.text == 'ℹО ботеℹ':
        await bot.send_message(message.chat.id,
                               '🤝 <a href="https://telegra.ph/Polzovatelskoe-soglashenie-01-03-2">Пользовательское соглашение</a>\n\n'
                               '📌 <a href="https://telegra.ph/O-proekte-VolumeHub-01-13">Инструкция по использованию</a>\n\n\n'
                               'Наш официальный telegram-канал: https://t.me/volumeHub', parse_mode='HTML',
                               disable_web_page_preview=True
                               )

    if message.text == '📌Подписка📌':
        db = UsersDataBase()
        await bot.send_message(message.chat.id, str(db.get_subscription_text()), reply_markup=payment_keyboard)
        db.db.close()

    if message.text == '👤Личный кабинет👤':
        db = UsersDataBase()
        date = db.get_subscription(message.from_user.id).split()[0]
        db.db.close()
        text = f'🙋Привет, {message.from_user.username}!\n\n📍Твоя подписка активна до: {date}'
        await bot.send_message(message.from_user.id, text)


    if message.text == '💌Промокод💌':
        await bot.send_message(message.from_user.id, 'Введите промокод:')
        await UserStates.get_promo_state.set()


@dp.message_handler(state=UserStates.get_promo_state)
async def process_answer(message: types.Message, state: FSMContext):
    promo = message.text

    if promo == 'VOLUMEHUB2024':
        await message.reply(
            text="Промокод активирован!\n\n\nВы можете приобрести подписку по очень сочным ценам, нажав кнопку ниже:",
            reply_markup=promo_pay_keyboard
        )
    else:
        await message.reply(f"Неверный промокод!")

    await state.finish()


@dp.callback_query_handler(lambda c: c.data)
async def get_payment_link(callback_query: types.CallbackQuery, state: FSMContext):
    if callback_query.data == '30':
        await bot.send_invoice(callback_query.from_user.id,
                               title="Подписка на бота",
                               description='подписка на получение аномальных объемов на 30 дней',
                               provider_token=PAYMENT_TOKEN,
                               currency='rub',
                               is_flexible=False,
                               prices=[PRICES_FOR_PAYMENT[0]],
                               start_parameter="one-month",
                               payload='30_days')
    elif callback_query.data == '90':
        await bot.send_invoice(callback_query.from_user.id,
                               title="Подписка на бота",
                               description='подписка на получение аномальных объемов на 90 дней',
                               provider_token=PAYMENT_TOKEN,
                               currency='rub',
                               is_flexible=False,
                               prices=[PRICES_FOR_PAYMENT[1]],
                               start_parameter="one-month",
                               payload='90_days')
    elif callback_query.data == '365':
        await bot.send_invoice(callback_query.from_user.id,
                               title="Подписка на бота",
                               description='подписка на получение аномальных объемов на 365 дней',
                               provider_token=PAYMENT_TOKEN,
                               currency='rub',
                               is_flexible=False,
                               prices=[PRICES_FOR_PAYMENT[2]],
                               start_parameter="one-month",
                               payload='365_days')
    elif callback_query.data == 'test':
        db = UsersDataBase()
        subscription = db.get_subscription(callback_query.from_user.id)
        if subscription == '-':
            db.give_subscription_to_user(7, callback_query.from_user.id)
            await bot.send_message(callback_query.from_user.id, "Пробный период на 7 дней активирован!")
        else:
            await bot.send_message(callback_query.from_user.id, "Вы уже активировали пробный период!")
        db.db.close()
    elif callback_query.data == 'promo30':
        await bot.send_invoice(callback_query.from_user.id,
                               title="Подписка на бота",
                               description='подписка на получение аномальных объемов на 30 дней',
                               provider_token=PAYMENT_TOKEN,
                               currency='rub',
                               is_flexible=False,
                               prices=[PRICES_FOR_PAYMENT[3]],
                               start_parameter="one-month",
                               payload='30_days')

    elif callback_query.data == 'promo90':
        await bot.send_invoice(callback_query.from_user.id,
                               title="Подписка на бота",
                               description='подписка на получение аномальных объемов на 90 дней',
                               provider_token=PAYMENT_TOKEN,
                               currency='rub',
                               is_flexible=False,
                               prices=[PRICES_FOR_PAYMENT[4]],
                               start_parameter="one-month",
                               payload='90_days')


@dp.pre_checkout_query_handler(lambda query: True)
async def pre_checkout_query(pre_checkout_q: types.PreCheckoutQuery):
    print(pre_checkout_q)
    db = UsersDataBase()
    prices = db.get_prices()
    db.add_payment(int(pre_checkout_q.id), int(pre_checkout_q.from_user.id), pre_checkout_q.from_user.first_name,
                   pre_checkout_q.from_user.username,
                   pre_checkout_q.from_user.language_code, pre_checkout_q.currency,
                   int(pre_checkout_q.total_amount) // 100)
    if str(pre_checkout_q.total_amount // 100) == prices[0]:
        db.give_subscription_to_user(30, int(pre_checkout_q.from_user.id))
    if str(pre_checkout_q.total_amount // 100) == prices[1]:
        db.give_subscription_to_user(90, int(pre_checkout_q.from_user.id))
    if str(pre_checkout_q.total_amount // 100) == prices[2]:
        db.give_subscription_to_user(365, int(pre_checkout_q.from_user.id))
    db.db.close()
    await bot.answer_pre_checkout_query(pre_checkout_q.id, ok=True)


@dp.message_handler(content_types=ContentType.SUCCESSFUL_PAYMENT)
async def succsessful_payment(message: types.Message):
    await bot.send_message(message.chat.id,
                           'Платеж выполнен!\n\nНе забудьте подписаться на наш telegram-канал, чтобы не пропустить важные обновления: https://t.me/volumeHub')


# Функция для отправки сообщения через бота
async def send_message_to_user(chat_id, text, photo_path=None):
    if photo_path:
        with open(photo_path, 'rb') as photo:
            await bot.send_photo(chat_id, photo, caption=text, parse_mode=ParseMode.MARKDOWN)
    else:
        await bot.send_message(chat_id, text, parse_mode=ParseMode.MARKDOWN)


async def on_startup(dp):
    scheduler = AsyncIOScheduler(timezone='Europe/Moscow')

    first_run_time = datetime.now().replace(second=20)



    scheduler.add_job(send_message_interval, trigger='cron', second='20', kwargs={'bot_old': bot})
    scheduler.add_job(subscription_reminder, trigger='cron', hour='19', minute='0', kwargs={'bot_old': bot})

    scheduler.start()
    print('Планировщик запущен!')


if __name__ == "__main__":
    while True:
        try:
            executor.start_polling(dp, on_startup=on_startup, skip_updates=False)
        except:
            print('rebooting bot_old...')
            time.sleep(1)

