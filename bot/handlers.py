from aiogram import types
from aiogram.dispatcher import FSMContext

from states import UserStates
from utils import load_html_message
from keyboards import start_keyboard, payment_keyboard, PRICES_FOR_PAYMENT, promo_pay_keyboard
import os


def register_handlers(dp):
    @dp.message_handler(commands=['start'])
    async def start(message: types.Message):
        await dp.bot.send_message(
            message.chat.id,
            load_html_message("messages/start_message.html"),
            parse_mode='HTML',
            disable_web_page_preview=True,
            reply_markup=start_keyboard
        )


    @dp.message_handler(text='ℹО ботеℹ')
    async def about_bot(message: types.Message):
        await dp.bot.send_message(
            message.chat.id,
            load_html_message("messages/about.html"),
            parse_mode='HTML',
            disable_web_page_preview=True
        )

    @dp.message_handler(text='📌Подписка📌')
    async def subscription_info(message: types.Message):
        await dp.bot.send_message(
            message.chat.id,
            load_html_message("messages/subscription.html"),
            parse_mode='HTML',
            disable_web_page_preview=True,
            reply_markup=payment_keyboard
        )

    @dp.message_handler(text='👤Личный кабинет👤')
    async def account_info(message: types.Message):
        await dp.bot.send_message(
            message.chat.id,
            load_html_message("messages/account.html"),
            parse_mode='HTML',
            disable_web_page_preview=True
        )

    @dp.message_handler(text='💌Промокод💌')
    async def promo_start(message: types.Message):
        await dp.bot.send_message(message.from_user.id, 'Введите промокод:')
        await UserStates.get_promo_state.set()


    @dp.message_handler(content_types=['text'])
    async def unknown_command(message: types.Message):
        await message.reply("Неизвестная команда. Используйте кнопки меню!")


    @dp.message_handler(state=UserStates.get_promo_state, content_types=['text'])
    async def process_promo(message: types.Message, state: FSMContext):
        promo = message.text.strip()
        if promo == 'VOLUMEHUB2024':
            await message.reply(
                "Промокод активирован!\n\nВы можете приобрести подписку по сниженной цене:",
                reply_markup=promo_pay_keyboard
            )
        else:
            await message.reply("Неверный промокод!", reply_markup=start_keyboard)
        await state.finish()

    @dp.message_handler(state=UserStates.get_promo_state, content_types=types.ContentType.ANY)
    async def invalid_promo_input(message: types.Message, state: FSMContext):
        await message.reply("Пожалуйста, введите текст промокода!")


    @dp.callback_query_handler(lambda c: c.data)
    async def get_payment_link(callback_query: types.CallbackQuery):
        PAYMENT_TOKEN = os.environ['PAYMENT_TOKEN']
        if callback_query.data == '30':
            await dp.bot.send_invoice(
                callback_query.from_user.id,
                title="Подписка на бота",
                description='подписка на получение аномальных объемов на 30 дней',
                provider_token=PAYMENT_TOKEN,
                currency='rub',
                is_flexible=False,
                prices=[PRICES_FOR_PAYMENT[0]],
                start_parameter="one-month",
                payload='30_days'
            )
        elif callback_query.data == '90':
            await dp.bot.send_invoice(
                callback_query.from_user.id,
                title="Подписка на бота",
                description='подписка на получение аномальных объемов на 90 дней',
                provider_token=PAYMENT_TOKEN,
                currency='rub',
                is_flexible=False,
                prices=[PRICES_FOR_PAYMENT[1]],
                start_parameter="one-month",
                payload='90_days'
            )
        elif callback_query.data == '365':
            await dp.bot.send_invoice(
                callback_query.from_user.id,
                title="Подписка на бота",
                description='подписка на получение аномальных объемов на 365 дней',
                provider_token=PAYMENT_TOKEN,
                currency='rub',
                is_flexible=False,
                prices=[PRICES_FOR_PAYMENT[2]],
                start_parameter="one-month",
                payload='365_days'
            )
        elif callback_query.data == 'test':
            # TODO: запросы из базы
            subscription = '-'  # Заглушка, заменить на реальную проверку
            if subscription == '-':
                await dp.bot.send_message(callback_query.from_user.id, "Пробный период на 7 дней активирован!")
            else:
                await dp.bot.send_message(callback_query.from_user.id, "Вы уже активировали пробный период!")
        elif callback_query.data == 'promo30':
            await dp.bot.send_invoice(
                callback_query.from_user.id,
                title="Подписка на бота",
                description='подписка на получение аномальных объемов на 30 дней (по промокоду)',
                provider_token=PAYMENT_TOKEN,
                currency='rub',
                is_flexible=False,
                prices=[PRICES_FOR_PAYMENT[3]],
                start_parameter="one-month",
                payload='30_days'
            )
        elif callback_query.data == 'promo90':
            await dp.bot.send_invoice(
                callback_query.from_user.id,
                title="Подписка на бота",
                description='подписка на получение аномальных объемов на 90 дней (по промокоду)',
                provider_token=PAYMENT_TOKEN,
                currency='rub',
                is_flexible=False,
                prices=[PRICES_FOR_PAYMENT[4]],
                start_parameter="one-month",
                payload='90_days'
            )


    @dp.pre_checkout_query_handler(lambda query: True)
    async def pre_checkout_query(pre_checkout_q: types.PreCheckoutQuery):
        await dp.bot.send_message(pre_checkout_q.from_user.id, "Обрабатываем ваш платеж...")
        await dp.bot.answer_pre_checkout_query(pre_checkout_q.id, ok=True)


    @dp.message_handler(content_types=types.ContentType.SUCCESSFUL_PAYMENT)
    async def successful_payment(message: types.Message):
        await dp.bot.send_message(
            message.chat.id,
            'Платеж выполнен!\n\nНе забудьте подписаться на наш telegram-канал: <a href="https://t.me/volumeHub">https://t.me/volumeHub</a>',
            parse_mode='HTML'
        )