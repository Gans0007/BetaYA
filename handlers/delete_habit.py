import logging
from aiogram import Router, F, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery

from repositories.habits.habit_repo import delete_habit_by_id, get_habit_by_id, should_show_delete_button
from services.confirmations.confirmation_service import was_confirmed_today

logger = logging.getLogger(__name__)
router = Router()

# 🔹 Запрос подтверждения удаления
@router.callback_query(F.data.startswith("delete_habit_"))
async def confirm_delete(callback: CallbackQuery):
    user_id = callback.from_user.id
    try:
        habit_id = int(callback.data.split("_")[-1])
        logger.info(f"[{user_id}] Запросил подтверждение удаления привычки habit_id={habit_id}")

        keyboard = InlineKeyboardMarkup(inline_keyboard=[[
            InlineKeyboardButton(text="✅ Подтвердить удаление", callback_data=f"confirm_delete_{habit_id}"),
            InlineKeyboardButton(text="❌ Отмена", callback_data="cancel_delete")
        ]])

        await callback.message.edit_text("⚠️ Ты точно хочешь удалить эту привычку?", reply_markup=keyboard)
        await callback.answer()

    except Exception as e:
        logger.exception(f"[{user_id}] Ошибка при показе подтверждения удаления привычки: {e}")
        await callback.answer("Произошла ошибка при попытке удалить привычку", show_alert=True)

# 🔹 Удаление привычки
@router.callback_query(F.data.startswith("confirm_delete_"))
async def delete_habit(callback: CallbackQuery):
    user_id = callback.from_user.id
    try:
        habit_id = int(callback.data.split("_")[-1])
        await delete_habit_by_id(habit_id)
        logger.info(f"[{user_id}] Удалил привычку habit_id={habit_id}")
        await callback.message.edit_text("✅ Привычка удалена.")
        await callback.answer()
    except Exception as e:
        logger.exception(f"[{user_id}] Ошибка при удалении привычки habit_id={habit_id}: {e}")
        await callback.answer("Не удалось удалить привычку", show_alert=True)

# 🔹 Отмена удаления и возврат к карточке
@router.callback_query(F.data == "cancel_delete")
async def cancel_delete(callback: CallbackQuery):
    user_id = callback.from_user.id
    try:
        habit_id = int(callback.message.reply_markup.inline_keyboard[0][0].callback_data.split("_")[-1])
        logger.info(f"[{user_id}] Отменил удаление привычки habit_id={habit_id}")

        habit = await get_habit_by_id(habit_id)
        if not habit:
            logger.warning(f"[{user_id}] Привычка habit_id={habit_id} не найдена при отмене удаления")
            await callback.message.edit_text("❌ Привычка не найдена.")
            await callback.answer()
            return

        habit_id, name, days, description, done_days, is_challenge, confirm_type = habit
        title = "🔥<b>Активный челлендж:</b>" if is_challenge else "⚡️<b>Активная привычка:</b>"
        percent = round((done_days / days) * 100) if days > 0 else 0

        text = (
            f"{title}\n\n"
            f"<b>Название:</b> {name}\n"
            f"<b>Описание:</b> {description}\n"
            f"<b>Прогресс:</b> {done_days} из {days} дней  <b>( {percent}% ) </b>"
        )

        # Кнопки
        buttons = [
            InlineKeyboardButton(
                text="♻️ Переподтвердить" if await was_confirmed_today(user_id, habit_id) else "✅ Подтвердить",
                callback_data=f"confirm_done_{habit_id}"
            )
        ]

        if await should_show_delete_button(user_id, habit_id):
            buttons.append(
                InlineKeyboardButton(
                    text="🗑 Удалить",
                    callback_data=f"delete_habit_{habit_id}"
                )
            )

        reply_markup = InlineKeyboardMarkup(inline_keyboard=[buttons])
        await callback.message.edit_text(text, reply_markup=reply_markup, parse_mode="HTML")
        await callback.answer()

    except Exception as e:
        logger.exception(f"[{user_id}] Ошибка при возврате к карточке habit_id={habit_id} после отмены удаления: {e}")
        await callback.answer("Произошла ошибка при отмене", show_alert=True)
