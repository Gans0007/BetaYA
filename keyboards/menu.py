import logging
import config
from aiogram import Bot, types
from aiogram import Router
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram import F
from aiogram.types import CallbackQuery

from services.confirmations.confirmation_service import was_confirmed_today
from repositories.habits.habit_repo import get_habits_by_user
from services.challenge_service.complete_challenge import complete_challenge
from repositories.habits.habit_repo import should_show_delete_button
from repositories.habits.habit_repo import count_user_habits
from keyboards.monetization import get_main_monetization_menu
from config import ADMIN_ID
from handlers.rules_text import rules_text

logger = logging.getLogger(__name__)

router = Router()


def get_main_menu() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="➕ Добавить привычку / челлендж"),
                KeyboardButton(text="📋 Активные задания")
            ],
            [
                KeyboardButton(text="💰 Монетизация"),
                KeyboardButton(text="📥 Полная версия")
            ]
        ],
        resize_keyboard=True,
        one_time_keyboard=False,
        input_field_placeholder="Выбери действие..."
    )

# Обработка кнопки "➕ Добавить привычку / челлендж"
@router.message(lambda msg: msg.text == "➕ Добавить привычку / челлендж")
async def handle_add_habit(message: types.Message):
    user_id = message.from_user.id
    total = await count_user_habits(user_id)

    text = (
        "📌 В привычке ты можешь сам добавить свою привычку.\n"
        "🔥 А в Challenge — выбрать одно из заданий от команды <b>Your Ambitions</b>.\n\n"
        f"{total}/5"
    )

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="➕ Добавить привычку", callback_data="add_habit_custom")],
        [InlineKeyboardButton(text="🔥 Взять Challenge", callback_data="take_challenge")]
    ])
    await message.answer(text, reply_markup=keyboard, parse_mode="HTML")

# Обработка активных заданий
@router.message(lambda msg: msg.text == "📋 Активные задания")
async def show_active_tasks(message: types.Message, bot: Bot):
    habits = await get_habits_by_user(message.from_user.id)
    if not habits:
        await message.answer("😐 У тебя пока нет активных привычек.")
        return

    for habit in habits:
        habit_id = habit.id
        name = habit.name
        days = habit.days
        description = habit.description
        done_days = habit.done_days
        is_challenge = habit.is_challenge
        confirm_type = habit.confirm_type

        # 🔁 Автоудаление завершённых челленджей
        if is_challenge and done_days >= days:
            await complete_challenge(habit_id, message.from_user.id, bot)
            continue

        title = "🔥<b>Активный челлендж:</b>" if is_challenge else "⚡️<b>Активная привычка:</b>"
        percent = round((done_days / days) * 100) if days > 0 else 0

        text = (
            f"{title}\n\n"
            f"<b>Название:</b> {name}\n"
            f"<b>Описание:</b> {description}\n"
            f"<b>Прогресс:</b> {done_days} из {days} дней  <b>( {percent}% ) </b>"
        )

        buttons = []

        # 🏁 Привычка завершена — предложить завершить или продлить
        if not is_challenge and done_days == days:
            buttons = [
                InlineKeyboardButton(
                    text="🫠 Завершить",
                    callback_data=f"complete_habit_{habit_id}"
                ),
                InlineKeyboardButton(
                    text="🫡 Продлить",
                    callback_data=f"extend_habit_{habit_id}"
                )
            ]
        else:
            # Кнопка подтверждения
            btn_text = (
                "⏰ Подтвердить (до +4 мин)"
                if confirm_type == "wake_time"
                else "♻️ Переподтвердить" if await was_confirmed_today(message.from_user.id, habit_id)
                else "✅ Подтвердить"
            )
            buttons.append(
                InlineKeyboardButton(
                    text=btn_text,
                    callback_data=f"confirm_done_{habit_id}"
                )
            )

            if await should_show_delete_button(message.from_user.id, habit_id):
                buttons.append(
                    InlineKeyboardButton(
                        text="🗑 Удалить",
                        callback_data=f"delete_habit_{habit_id}"
                    )
                )

        await message.answer(
            text,
            parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[buttons])
        )

#обработка кнопки МОНЕТИЗАЦИЯ
# Универсальная функция показа меню монетизации
async def send_monetization_menu(bot: Bot, chat_id: int, is_admin: bool):
    text = (
        "💸 <b>Монетизация</b>\n\n"
        "Твой путь к заработку с <b>Your Ambitions</b> 💼\n\n"
        "Выбери, с чего начать:"
    )

    keyboard = [
        [
            InlineKeyboardButton(text="💰 Баланс", callback_data="balance"),
            InlineKeyboardButton(text="👥 Реферальная ссылка", callback_data="monetization_referral")
        ],
        [
            InlineKeyboardButton(text="📤 Загрузить видео", callback_data="upload_video"),
            InlineKeyboardButton(text="📚 Правила", callback_data="monetization_rules")
        ]
    ]

    if is_admin:
        keyboard.append([InlineKeyboardButton(text="✅ Одобрение", callback_data="review_pending_videos")])

    markup = InlineKeyboardMarkup(inline_keyboard=keyboard)
    await bot.send_message(chat_id, text, reply_markup=markup, parse_mode="HTML")


# Обработка команды "💰 Монетизация"
@router.message(lambda msg: msg.text == "💰 Монетизация")
async def handle_monetization(message: types.Message, bot: Bot):
    user_id = message.from_user.id
    logger.info(f"[{user_id}] Открыл меню монетизации")

    keyboard = get_main_monetization_menu(is_admin=(user_id == config.ADMIN_ID))
    await bot.send_message(
        chat_id=message.chat.id,
        text="💸 <b>Монетизация</b>\n\nТвой путь к заработку с <b>Your Ambitions</b> 💼\n\nВыбери, с чего начать:",
        reply_markup=keyboard,
        parse_mode="HTML"
    )

@router.callback_query(F.data == "monetization_back")
async def handle_monetization_back(callback: types.CallbackQuery, bot: Bot):
    user_id = callback.from_user.id
    is_admin = (user_id == config.ADMIN_ID)
    keyboard = get_main_monetization_menu(is_admin=is_admin)

    await callback.answer()
    await bot.send_message(
        chat_id=callback.message.chat.id,
        text="💸 <b>Монетизация</b>\n\nТвой путь к заработку с <b>Your Ambitions</b> 💼\n\nВыбери, с чего начать:",
        reply_markup=keyboard,
        parse_mode="HTML"
    )

@router.callback_query(F.data == "monetization_rules")
async def handle_monetization_rules(callback: CallbackQuery):
    await callback.answer()

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📌 Примеры медиа", callback_data="rules_examples")],
        [InlineKeyboardButton(text="◀️ Назад", callback_data="monetization_back")]
    ])

    await callback.message.answer(rules_text, reply_markup=keyboard, parse_mode="HTML")

