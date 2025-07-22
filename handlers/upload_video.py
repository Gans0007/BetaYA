from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from repositories.video.video_repo import save_pending_video, get_pending_videos, approve_video
from states.upload_video import UploadVideoFSM 
import logging
from aiogram import Bot
from datetime import datetime
from config import ADMIN_IDS
from utils.ui import safe_replace_message, try_edit_message
from repositories.video.video_repo import get_pending_video_by_id
from repositories.video.video_repo import delete_video, approve_video, count_pending_videos_by_user
from services.monetization.reward_service import add_reward

logger = logging.getLogger(__name__)
router = Router()

@router.callback_query(F.data == "review_pending_videos")
async def handle_review_videos(callback: types.CallbackQuery):
    if callback.from_user.id not in ADMIN_IDS:
        await callback.answer("⛔ Только для админов", show_alert=True)
        return

    logger.info(f"[ADMIN] 🔍 Админ {callback.from_user.id} просматривает видео на проверку")
    videos = await get_pending_videos()
    if not videos:
        await callback.message.answer("📭 Нет видео на проверку.")
        logger.info(f"[ADMIN] 📭 Админ {callback.from_user.id}: нет видео на проверку")
        return

    for video in videos:
        user_id = video["user_id"]
        video_link = video["video_link"]
        submitted_at = video["submitted_at"].strftime("%Y-%m-%d %H:%M")
        approved = "✅ Да" if video["approved"] else "❌ Нет"

        text = (
            f"👤 Пользователь: <code>{user_id}</code>\n"
            f"🔗 Ссылка: {video_link}\n"
            f"📅 Отправлено: {submitted_at}\n"
            f"⚙️ Одобрено: {approved}"
        )

        keyboard = types.InlineKeyboardMarkup(inline_keyboard=[
            [
                types.InlineKeyboardButton(text="✅ Одобрить", callback_data=f"approve_video:{video['id']}"),
                types.InlineKeyboardButton(text="❌ Отклонить", callback_data=f"reject_video:{video['id']}")
            ]
        ])

        await callback.message.answer(text, reply_markup=keyboard)

    await callback.answer()


@router.callback_query(F.data == "upload_video")
async def start_video_upload(callback: types.CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    pending_count = await count_pending_videos_by_user(user_id)

    logger.info(f"[VIDEO] 🟡 Пользователь {user_id} начал загрузку видео. На проверке: {pending_count}")
    
    text = (
        "📹 Вставь ссылку на видео с отметкой бота или канала(TikTok, Instagram, Telegram и т.д.)"
        f"\n\n🕵️ На проверке: {pending_count} видео"
    )

    keyboard = types.InlineKeyboardMarkup(inline_keyboard=[
        [types.InlineKeyboardButton(text="❌ Отмена", callback_data="cancel_upload")]
    ])

    await callback.message.answer(text, reply_markup=keyboard)
    await state.set_state(UploadVideoFSM.waiting_for_video_link)
    await callback.answer()


@router.message(UploadVideoFSM.waiting_for_video_link, F.text)
async def handle_video_link(message: types.Message, state: FSMContext):
    video_url = message.text.strip()

    if not video_url.startswith("http"):
        await message.answer("❌ Это не похоже на ссылку. Попробуй снова.")
        logger.warning(f"[VIDEO] 🚫 Неверная ссылка от {message.from_user.id}: {video_url}")
        return

    await save_pending_video(user_id=message.from_user.id, video_link=video_url)
    await message.answer("✅ Твое видео отправлено на проверку. Жди одобрения от Админа.")
    logger.info(f"[VIDEO] ✅ Пользователь {message.from_user.id} загрузил видео: {video_url}")
    await state.clear()


@router.callback_query(F.data == "cancel_upload")
async def cancel_upload(callback: types.CallbackQuery, state: FSMContext):
    await state.clear()
    await safe_replace_message(callback.message, "🚫 Загрузка отменена.")
    logger.info(f"[VIDEO] 🚫 Пользователь {callback.from_user.id} отменил загрузку видео")
    await callback.answer()


@router.callback_query(F.data.startswith("reject_video:"))
async def handle_reject_video(callback: types.CallbackQuery, bot: Bot):
    if callback.from_user.id not in ADMIN_IDS:
        await callback.answer("⛔ Только для админов", show_alert=True)
        return

    video_id = int(callback.data.split(":")[1])
    logger.info(f"[ADMIN] ❌ Админ {callback.from_user.id} отклоняет видео {video_id}")

    video = await get_pending_video_by_id(video_id)
    if video:
        try:
            await bot.send_message(
                video["user_id"],
                "❌ Ваше видео было отклонено администратором. Попробуйте загрузить другой вариант."
            )
            logger.info(f"[VIDEO] ❌ Отклонение отправлено пользователю {video['user_id']}")
        except Exception as e:
            logger.error(f"[VIDEO] ❌ Ошибка при отправке отклонения пользователю {video['user_id']}: {e}")

    await delete_video(video_id)
    await try_edit_message(callback, text="❌ Видео отклонено.")
    await callback.answer("Видео удалено")


@router.callback_query(F.data.startswith("approve_video:"))
async def handle_approve_video(callback: types.CallbackQuery, bot: Bot):
    if callback.from_user.id not in ADMIN_IDS:
        await callback.answer("⛔ Только для админов", show_alert=True)
        return

    video_id = int(callback.data.split(":")[1])
    await approve_video(video_id)

    video = await get_pending_video_by_id(video_id)
    if video:
        user_id = video["user_id"]
        logger.info(f"[ADMIN] ✅ Админ {callback.from_user.id} одобрил видео {video_id} пользователя {user_id}")

        await add_reward(user_id=user_id, amount=0.10, reason="Видео одобрено", reward_type="usdt")

        try:
            await bot.send_message(user_id, "✅ Ваше видео было одобрено администратором!")
            await bot.send_message(
                user_id,
                "Тебе благодарность от YA \n\n⭐ <b>+3 XP</b> за старание\n\n💸 <b>+0.10 USDT</b> за вклад в комьюнити!",
                parse_mode="HTML"
            )
            logger.info(f"[VIDEO] ✅ Отправлены 2 сообщения о наградах пользователю {user_id}")
        except Exception as e:
            logger.error(f"[VIDEO] ❌ Не удалось отправить уведомления пользователю {user_id}: {e}")

    await try_edit_message(callback, text="✅ Видео одобрено.")
    await callback.answer("Одобрено")
