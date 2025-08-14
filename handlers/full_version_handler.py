from aiogram import Router, types, F
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from config import ADMIN_ID
from keyboards.monetization import get_main_monetization_menu
from db.db import database  # добавлено для запроса к БД
import logging


router = Router()


@router.message(F.text == "📥 Полная версия")
async def handle_full_version(message: types.Message):
    logging.getLogger(__name__).info(
        f"[DEBUG] Кнопка 'Полная версия' нажата. text={repr(message.text)}, user_id={message.from_user.id}"
    )

    # Получаем XP пользователя
    query = "SELECT xp_balance FROM users WHERE user_id = :user_id"
    row = await database.fetch_one(query, {"user_id": message.from_user.id})
    xp = row[0] if row else 0

    # Новый текст
    text = (
        "🔓 <b>YOUR AMBITIONS — больше, чем бот</b>\n"
        "Это <b>твоя социальная сеть</b>, если ты:\n"
        "• Хочешь изменить жизнь, но не знаешь, с чего начать\n"
        "• Ищешь сильное окружение и единомышленников\n"
        "• Видишь цель, но чувствуешь, что для рывка чего-то не хватает\n\n"
        "<b>В ПОЛНОЙ ВЕРСИИ ТЕБЯ ЖДЁТ:</b>\n"
        "✅ Безлимит на привычки и челленджи\n"
        "🌍 Бот на 3 языках (uk, ru, en) — выбирай свой\n"
        "🔔 3 режима уведомлений: мягкий, средний, жёсткий\n"
        "📵 Возможность отключать отправку медиа в общий чат\n"
        "📈 Подробная статистика прогресса\n"
        "💸 Ежемесячные выплаты за рефералов — зови друзей и зарабатывай\n"
        "🥇 Лиги, уровни, достижения — делай процесс увлекательным\n"
        "🏆 Топ-10 в мире и в своей лиге\n"
        "👤 Профили участников — находи людей с твоими ценностями\n"
        "📅 Личные заметки, мечты, цели, планы с напоминаниями\n"
        "🎁 Физические награды от команды Your Ambitions\n\n"
        "⚡️ <b>СЕЙЧАС ТВОЙ ШАНС</b>\n"
        "🎯 С 60 хр — скидка 30% на полную версию!\n"
        f"У тебя сейчас — <b>{xp} хр</b>.\n\n"
        "Тебе не нужны чудеса.\n"
        "Тебе нужен прогресс.\n\n"
        "🔥 Ты в игре?"
    )

    # Логика выбора ссылки
    if xp >= 60:
        buy_url = "https://t.me/tribute/app?startapp=ssYz"
    else:
        buy_url = "https://t.me/yourambitionsbot"

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔥 Приобрести полный доступ", url=buy_url)],
        [InlineKeyboardButton(text="◀️ Назад", callback_data="monetization_back")]
    ])

    await message.answer(text, reply_markup=keyboard, parse_mode="HTML")


@router.message(F.photo)
async def handle_photo(message: types.Message):
    # Берем самое большое по качеству фото
    photo = message.photo[-1]
    file_id = photo.file_id

    logging.getLogger(__name__).info(f"[PHOTO] file_id={file_id} from user_id={message.from_user.id}")
    print(f"[PHOTO] file_id={file_id} from user_id={message.from_user.id}")  # для вывода прямо в консоль

    await message.answer(f"ID этой фотографии:\n<code>{file_id}</code>", parse_mode="HTML")