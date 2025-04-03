from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup, LabeledPrice

from adminDB import UsersDataBase

start_keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
start_buttons = [
    KeyboardButton(text='ℹО ботеℹ'),
    KeyboardButton(text='📌Подписка📌')
]
start_keyboard.add(*start_buttons)
start_keyboard.add(KeyboardButton(text='👤Личный кабинет👤'))
start_keyboard.add(KeyboardButton(text='💌Промокод💌'))



payment_keyboard = InlineKeyboardMarkup(row_width=1)

db = UsersDataBase()
prices = db.get_prices()
db.db.close()

payment_buttons = [
    InlineKeyboardButton(text=f"7 дней  | пробный период", callback_data="test"),
    InlineKeyboardButton(text=f"30 дней  | {prices[0]} рублей", callback_data="30"),
    InlineKeyboardButton(text=f" 90 дней  | {prices[1]} рублей", callback_data="90"),
    InlineKeyboardButton(text=f"365 дней | {prices[2]} рублей", callback_data="365"),
]
payment_keyboard.add(*payment_buttons)

promo_pay_keyboard = InlineKeyboardMarkup(row_width=1)
promo_payment_buttons = [
    InlineKeyboardButton(text=f"30 дней  | 159 рублей", callback_data="promo30"),
    InlineKeyboardButton(text=f" 90 дней  | 450 рублей", callback_data="promo90")
]
promo_pay_keyboard.add(*promo_payment_buttons)



PRICES_FOR_PAYMENT = [
    LabeledPrice(label="Подписка на бота", amount=int(prices[0]) * 100),
    LabeledPrice(label="Подписка на бота", amount=int(prices[1]) * 100),
    LabeledPrice(label="Подписка на бота", amount=int(prices[2]) * 100),
    LabeledPrice(label="Подписка на бота", amount=15900),
    LabeledPrice(label="Подписка на бота", amount=45000)
]
