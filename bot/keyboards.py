from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup, LabeledPrice



start_keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
start_buttons = [
    KeyboardButton(text='ℹО ботеℹ'),
    KeyboardButton(text='📌Подписка📌')
]
start_keyboard.add(*start_buttons)
start_keyboard.add(KeyboardButton(text='👤Личный кабинет👤'))
start_keyboard.add(KeyboardButton(text='💌Промокод💌'))



payment_keyboard = InlineKeyboardMarkup(row_width=1)



payment_buttons = [
    InlineKeyboardButton(text=f"7 дней  | пробный период", callback_data="test"),
    InlineKeyboardButton(text=f"30 дней  | 100 рублей", callback_data="30"),
    InlineKeyboardButton(text=f" 90 дней  | 200 рублей", callback_data="90"),
    InlineKeyboardButton(text=f"365 дней | 300 рублей", callback_data="365"),
]
payment_keyboard.add(*payment_buttons)

promo_pay_keyboard = InlineKeyboardMarkup(row_width=1)
promo_payment_buttons = [
    InlineKeyboardButton(text=f"30 дней  | 159 рублей", callback_data="promo30"),
    InlineKeyboardButton(text=f" 90 дней  | 450 рублей", callback_data="promo90")
]
promo_pay_keyboard.add(*promo_payment_buttons)



PRICES_FOR_PAYMENT = [
    LabeledPrice(label="Подписка на бота", amount=int(100) * 100),
    LabeledPrice(label="Подписка на бота", amount=int(200) * 100),
    LabeledPrice(label="Подписка на бота", amount=int(300) * 100),
    LabeledPrice(label="Подписка на бота", amount=15900),
    LabeledPrice(label="Подписка на бота", amount=45000)
]
