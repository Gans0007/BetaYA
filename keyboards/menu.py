import logging
import config
from aiogram import Bot, types
from aiogram import Router
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import InlineKeyboardMarkup, InlineKeyboardButton


from services.confirmations.confirmation_service import was_confirmed_today
from repositories.habits.habit_repo import get_habits_by_user
from services.challenge_service.complete_challenge import complete_challenge
from repositories.habits.habit_repo import should_show_delete_button
from config import ADMIN_ID

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
                KeyboardButton(text="💰 Монетизация")
            ]
        ],
        resize_keyboard=True,
        one_time_keyboard=False,
        input_field_placeholder="Выбери действие..."
    )

# Обработка кнопки "➕ Добавить привычку / челлендж"
@router.message(lambda msg: msg.text == "➕ Добавить привычку / челлендж")
async def handle_add_habit(message: types.Message):
    text = (
        "📌 В привычке ты можешь сам добавить свою привычку.\n"
        "🔥 А в Challenge — выбрать одно из заданий от команды <b>Your Ambitions</b>."
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

    for habit_id, name, days, description, done_days, is_challenge, confirm_type in habits:
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
@router.message(lambda msg: msg.text == "💰 Монетизация")
async def handle_monetization(message: types.Message):
    user_id = message.from_user.id
    logger.info(f"[{user_id}] Открыл меню монетизации")

    text = (
        "💸 <b>Монетизация</b>\n\n"
        "Твой путь к заработку с <b>Your Ambitions</b> 💼\n\n"
        "Выбери, с чего начать:"
    )

    # Основные кнопки
    keyboard = [
        [
            InlineKeyboardButton(text="💰 Баланс", callback_data="monetization_balance"),
            InlineKeyboardButton(text="👥 Реферальная ссылка", callback_data="monetization_referral")
        ],
        [
            InlineKeyboardButton(text="📤 Загрузить видео", callback_data="monetization_upload"),
            InlineKeyboardButton(text="📚 Правила", callback_data="monetization_rules")
        ]
    ]

    # Если пользователь — админ, добавляем кнопку "Одобрение"
    if user_id == config.ADMIN_ID:
        logger.info(f"[{user_id}] Является админом — добавлена кнопка 'Одобрение'")
        keyboard.append(
            [InlineKeyboardButton(text="✅ Одобрение", callback_data="monetization_approval")]
        )

    markup = InlineKeyboardMarkup(inline_keyboard=keyboard)

    await message.answer(text, reply_markup=markup, parse_mode="HTML")