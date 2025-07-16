from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from states.habit_states import ConfirmHabit
from config import PUBLIC_CHAT_ID
from datetime import datetime, timedelta
import pytz
import logging

from repositories.habits.habit_repo import get_habit_by_id
from services.confirmations.confirmation_service import (
    process_confirmation,
    send_to_public_chat,
    log_confirmation
)

logger = logging.getLogger(__name__)
router = Router()

cancel_keyboard = types.InlineKeyboardMarkup(
    inline_keyboard=[
        [types.InlineKeyboardButton(text="❌ Отмена", callback_data="cancel_fsm_confirmation")]
    ]
)

# 🔹 Обработка кнопки "✅ Подтвердить"
@router.callback_query(F.data.startswith("confirm_done_"))
async def handle_confirm_callback(callback: types.CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    try:
        habit_id = int(callback.data.split("_")[-1])
        habit = await get_habit_by_id(habit_id)

        if not habit:
            logger.error(f"[{user_id}] Попытка подтвердить несуществующую привычку habit_id={habit_id}")
            await callback.message.answer("❌ Привычка не найдена.")
            return

        confirm_type = habit.confirm_type
        name = habit.name
        logger.info(f"[{user_id}] Подтверждает привычку '{name}' (id={habit_id}, тип={confirm_type})")

        if confirm_type == "wake_time":
            try:
                time_part = name.split("в")[1].strip()
                wake_time = datetime.strptime(time_part, "%H:%M").time()
                now = datetime.now(pytz.timezone("Europe/Kyiv")).time()
                latest_allowed = (datetime.combine(datetime.today(), wake_time) + timedelta(minutes=4)).time()

                if not (wake_time <= now <= latest_allowed):
                    logger.info(f"[{user_id}] Пропущено окно подтверждения wake_time для habit_id={habit_id}")
                    await callback.message.answer(
                        f"⏰ Подтверждение допускается только с {wake_time.strftime('%H:%M')} до {latest_allowed.strftime('%H:%M')}.\nСегодня уже поздно."
                    )
                    await callback.answer()
                    return
            except Exception:
                logger.exception(f"[{user_id}] Ошибка при проверке времени habit_id={habit_id}")
                await callback.message.answer("❌ Невозможно определить время подъема.")
                await callback.answer()
                return

        await state.update_data(habit_id=habit_id, confirm_type=confirm_type)
        await callback.message.answer(
            f"📹 Пришли кружок или видео для подтверждения привычки: {name}",
            reply_markup=cancel_keyboard
        )
        logger.info(f"[{user_id}] Запущено ожидание медиа для habit_id={habit_id}")
        await state.set_state(ConfirmHabit.waiting_for_media)
        await callback.answer()

    except Exception:
        logger.exception(f"[{user_id}] Ошибка при обработке подтверждения привычки")
        await callback.answer("Произошла ошибка при подтверждении", show_alert=True)

# 🔹 Обработка видео/кружка
@router.message(ConfirmHabit.waiting_for_media, F.video | F.video_note | F.photo)
async def handle_habit_video(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    try:
        data = await state.get_data()
        habit_id = data.get("habit_id")
        confirm_type = data.get("confirm_type")

        if habit_id is None:
            logger.critical(f"[{user_id}] FSM-состояние повреждено: habit_id отсутствует")
            await message.answer("❌ Произошла критическая ошибка. Попробуй снова.")
            return

        # Тип файла
        if message.video:
            file_id = message.video.file_id
            file_type = "video"
        elif message.video_note:
            file_id = message.video_note.file_id
            file_type = "video_note"
        elif message.photo:
            file_id = message.photo[-1].file_id
            file_type = "photo"
        else:
            logger.error(f"[{user_id}] Неверный тип медиа при подтверждении habit_id={habit_id}")
            await message.answer("❌ Пожалуйста, пришли видео, кружок или фото.")
            return

        logger.info(f"[{user_id}] Отправил {file_type} для habit_id={habit_id}")

        if confirm_type == "wake_time":
            habit = await get_habit_by_id(habit_id)
            name = habit.name
            try:
                time_part = name.split("в")[1].strip()
                wake_time = datetime.strptime(time_part, "%H:%M").time()
            except Exception:
                logger.exception(f"[{user_id}] Не удалось распарсить время привычки '{name}'")
                await message.answer("❌ Невозможно определить время подъема.")
                return

            now = datetime.now(pytz.timezone("Europe/Kyiv")).time()
            latest_allowed = (datetime.combine(datetime.today(), wake_time) + timedelta(minutes=4)).time()
            if not (wake_time <= now <= latest_allowed):
                logger.info(f"[{user_id}] Медиа отправлено вне допустимого времени для habit_id={habit_id}")
                await message.answer(
                    f"⏰ Подтверждение допускается только с {wake_time.strftime('%H:%M')} до {(latest_allowed).strftime('%H:%M')}.\nСегодня уже поздно."
                )
                return

        progress_increased = await process_confirmation(
            user_id=user_id,
            habit_id=habit_id,
            file_id=file_id,
            file_type=file_type,
            bot=message.bot
        )

        await send_to_public_chat(
            user=message.from_user,
            habit_id=habit_id,
            file_id=file_id,
            file_type=file_type,
            bot=message.bot
        )

        if progress_increased:
            habit = await get_habit_by_id(habit_id)
            if habit.is_challenge and int(habit.done_days) >= int(habit.days):
                from services.challenge_service.complete_challenge import complete_challenge
                logger.info(f"[{user_id}] Завершил челлендж habit_id={habit_id}")
                await complete_challenge(habit_id, user_id, message.bot)
                return

        logger.info(f"[{user_id}] {file_type} успешно подтверждено для habit_id={habit_id}")
        await message.answer(
            "♻️ Медиа обновлено! Прогресс не изменён."
            if not progress_increased else
            "✅ Привычка успешно подтверждена! Прогресс обновлён."
        )

    except Exception:
        logger.exception(f"[{user_id}] Ошибка при загрузке медиа для habit_id={habit_id}")
        await message.answer("❌ Произошла ошибка при подтверждении.")
    finally:
        await state.clear()

@router.callback_query(F.data == "cancel_fsm_confirmation")
async def cancel_fsm_confirmation(callback: types.CallbackQuery, state: FSMContext):
    await state.clear()
    logger.info(f"[{callback.from_user.id}] Отменил подтверждение привычки через FSM")
    await callback.message.edit_text("🚫 Подтверждение привычки отменено.")
    await callback.answer()
