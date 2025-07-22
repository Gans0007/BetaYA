import logging
from datetime import datetime, timedelta
from aiogram import Bot

import pytz
from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from states.habit_states import ConfirmHabit
from services.confirmations.confirmation_service import (
    process_confirmation,
    send_to_public_chat
)
from repositories.habits.habit_repo import get_habits_by_user, get_habit_by_id

logger = logging.getLogger(__name__)
router = Router()

# 🔹 Обработка медиа без состояния
@router.message(F.photo | F.video | F.video_note)
async def handle_media_no_state(message: Message, state: FSMContext):
    if message.chat.type != "private":
        return

    user_id = message.from_user.id

    # Определяем тип медиа
    if message.photo:
        file_id = message.photo[-1].file_id
        file_type = "photo"
    elif message.video:
        file_id = message.video.file_id
        file_type = "video"
    elif message.video_note:
        file_id = message.video_note.file_id
        file_type = "video_note"
    else:
        logger.warning(f"[{user_id}] Получен неизвестный тип медиа")
        await message.answer("❌ Тип медиа не распознан.")
        return

    logger.info(f"[{user_id}] Отправил {file_type}, file_id={file_id}")
    await state.update_data(file_id=file_id, file_type=file_type)

    try:
        habits = await get_habits_by_user(user_id)
        media_habits = [(h.id, h.name) for h in habits if h.confirm_type in ("media", "wake_time")]

        if not media_habits:
            logger.info(f"[{user_id}] Нет подходящих привычек для подтверждения")
            await message.answer("😐 У тебя нет привычек, которые можно подтвердить через медиа.")
            return

        keyboard = types.InlineKeyboardMarkup(
            inline_keyboard=[
                [types.InlineKeyboardButton(text=name, callback_data=f"select_habit_{hid}")]
                for hid, name in media_habits
            ]
        )

        logger.info(f"[{user_id}] Показан выбор привычки для медиа-подтверждения")
        await message.answer("Выбери, для какой привычки это подтверждение:", reply_markup=keyboard)
        await state.set_state(ConfirmHabit.waiting_for_selection)

    except Exception as e:
        logger.exception(f"[{user_id}] Ошибка при обработке медиа-сообщения: {e}")
        await message.answer("Произошла ошибка при обработке медиа.")
        await state.clear()

# 🔹 Обработка выбора привычки
@router.callback_query(F.data.startswith("select_habit_"))
async def handle_habit_selection(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    try:
        data = await state.get_data()
        file_id = data.get("file_id")
        file_type = data.get("file_type")
        habit_id = int(callback.data.split("_")[-1])

        if not file_id or not file_type:
            logger.error(f"[{user_id}] Отсутствует file_id/file_type в состоянии")
            await callback.message.answer("❌ Ошибка: медиа не найдено. Попробуй отправить снова.")
            await state.clear()
            return

        habit = await get_habit_by_id(habit_id)

        # ⏰ Проверка времени wake_time
        if habit and habit.confirm_type == "wake_time":
            try:
                name = habit.name
                time_part = name.split("в")[1].strip()
                wake_time = datetime.strptime(time_part, "%H:%M").time()
                now = datetime.now(pytz.timezone("Europe/Kyiv")).time()
                latest_allowed = (datetime.combine(datetime.today(), wake_time) + timedelta(minutes=4)).time()

                if not (wake_time <= now <= latest_allowed):
                    logger.warning(f"[{user_id}] Позднее подтверждение: now={now}, допустимо до={latest_allowed}")
                    await callback.message.answer(
                        f"⏰ Подтверждение допускается только с {wake_time.strftime('%H:%M')} до {latest_allowed.strftime('%H:%M')}.\nСегодня уже поздно."
                    )
                    await state.clear()
                    return

            except Exception as e:
                logger.exception(f"[{user_id}] Ошибка парсинга времени habit_id={habit_id}: {e}")
                await callback.message.answer("❌ Невозможно определить время подъема.")
                await state.clear()
                return

        # ✅ Основная логика подтверждения
        progress_increased = await process_confirmation(
            user_id=user_id,
            habit_id=habit_id,
            file_id=file_id,
            file_type=file_type,
            bot=callback.bot
        )

        # 🔁 Отправка в общий чат
        await send_to_public_chat(
            user=callback.from_user,
            habit_id=habit_id,
            file_id=file_id,
            file_type=file_type,
            bot=callback.bot
        )

        # 🏁 Завершение челленджа, если нужно
        if progress_increased:
            habit = await get_habit_by_id(habit_id)
            if habit.is_challenge and int(habit.done_days) >= int(habit.days):
                from services.challenge_service.complete_challenge import complete_challenge
                await complete_challenge(habit_id, user_id, callback.bot)
                logger.info(f"[{user_id}] Завершил челлендж через медиа (habit_id={habit_id})")
                return

        # ✅ Ответ пользователю
        await callback.message.answer(
            "♻️ Видео/фото обновлено! Прогресс не изменён."
            if not progress_increased else
            "✅ Привычка успешно подтверждена! Прогресс обновлён."
        )

        logger.info(f"[{user_id}] Подтвердил {file_type} для habit_id={habit_id}")
        await callback.answer()

    except Exception as e:
        logger.exception(f"[{user_id}] Ошибка при обработке медиа-подтверждения habit_id={habit_id}: {e}")
        await callback.answer("❌ Произошла ошибка при подтверждении", show_alert=True)
    finally:
        await state.clear()
