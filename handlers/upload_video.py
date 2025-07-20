from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from repositories.video.video_repo import save_pending_video, get_pending_videos, approve_video
from states.upload_video import UploadVideoFSM 
import logging
from datetime import datetime
from config import ADMIN_IDS
from utils.ui import safe_replace_message, try_edit_message
from repositories.video.video_repo import delete_video, approve_video, count_pending_videos_by_user


logger = logging.getLogger(__name__)
router = Router()

@router.callback_query(F.data == "review_pending_videos")
async def handle_review_videos(callback: types.CallbackQuery):
    if callback.from_user.id not in ADMIN_IDS:
        await callback.answer("⛔ Только для админов", show_alert=True)
        return

    videos = await get_pending_videos()
    if not videos:
        await callback.message.answer("📭 Нет видео на проверку.")
        return

    for video in videos:
        user_id = video["user_id"]                             # ✅
        video_link = video["video_link"]                       # ✅
        submitted_at = datetime.fromisoformat(video["submitted_at"]).strftime("%Y-%m-%d %H:%M")  # ✅
        approved = "✅ Да" if video["approved"] else "❌ Нет"   # ✅

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


# 🔹 Старт FSM — кнопка "Загрузить видео"
@router.callback_query(F.data == "upload_video")
async def start_video_upload(callback: types.CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    pending_count = await count_pending_videos_by_user(user_id)

    text = (
        "📹 Вставь ссылку на видео (YouTube, Google Drive, Telegram и т.д.)"
        f"\n\n🕵️ На проверке: {pending_count} видео"
    )

    keyboard = types.InlineKeyboardMarkup(inline_keyboard=[
        [types.InlineKeyboardButton(text="❌ Отмена", callback_data="cancel_upload")]
    ])

    await callback.message.answer(text, reply_markup=keyboard)
    await state.set_state(UploadVideoFSM.waiting_for_video_link)
    await callback.answer()

# 🔹 Обработка ссылки
@router.message(UploadVideoFSM.waiting_for_video_link, F.text)
async def handle_video_link(message: types.Message, state: FSMContext):
    video_url = message.text.strip()

    if not video_url.startswith("http"):
        await message.answer("❌ Это не похоже на ссылку. Попробуй снова.")
        return

    await save_pending_video(user_id=message.from_user.id, video_link=video_url)
    await message.answer("✅ Твое видео отправлено на проверку. Жди одобрения от Админа.")
    await state.clear()

@router.callback_query(F.data == "cancel_upload")
async def cancel_upload(callback: types.CallbackQuery, state: FSMContext):
    await state.clear()
    await safe_replace_message(callback.message, "🚫 Загрузка отменена.")
    await callback.answer()


@router.callback_query(F.data.startswith("reject_video:"))
async def handle_reject_video(callback: types.CallbackQuery):
    if callback.from_user.id not in ADMIN_IDS:
        await callback.answer("⛔ Только для админов", show_alert=True)
        return

    video_id = int(callback.data.split(":")[1])
    await delete_video(video_id)  # удаляем видео из базы
    await try_edit_message(callback, text="❌ Видео отклонено.")
    await callback.answer("Видео удалено")

@router.callback_query(F.data.startswith("approve_video:"))
async def handle_approve_video(callback: types.CallbackQuery):
    if callback.from_user.id not in ADMIN_IDS:
        await callback.answer("⛔ Только для админов", show_alert=True)
        return

    video_id = int(callback.data.split(":")[1])
    await approve_video(video_id)
    await try_edit_message(callback, text="✅ Видео одобрено.")
    await callback.answer("Одобрено")