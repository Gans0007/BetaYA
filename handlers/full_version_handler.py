from aiogram import Router, types, F
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from config import ADMIN_ID
from keyboards.monetization import get_main_monetization_menu

router = Router()

@router.message(F.text == "📥 Полная версия")
async def handle_full_version(message: types.Message):
    text = (
        "🔓 <b>Полная версия Your Ambitions</b> — это не просто бот, а <b>социальная сеть</b> для тех, кто:\n\n"
        "• Хочет выработать сильные привычки\n"
        "• Ищет единомышленников и полезные знакомства\n"
        "• Живёт в потоке саморазвития и движения вперёд\n\n"
        "🏆 <b>VIP-статус</b> (с 50+ XP) открывает доступ к эксклюзиву:\n\n"
        "• 🔥 <b>30% скидка</b> на полную версию\n"
        "• 🏅 Место на <b>Доске почёта</b> и в <b>Зале славы</b>\n"
        "• ♾️ <b>Безлимит</b> на привычки и челленджи\n"
        "• 🎯 <b>Сообщество VIP-участников</b>\n"
        "• 💸 <b>Ежемесячные выплаты</b> за рефералов\n"
        "• ✍️ Личный раздел <b>мечт, целей и планов</b> с напоминаниями\n"
        "•📊 Подробная <b>статистика</b> и прогресса\n"
        "•🎁 <b>Физические награды</b> от команды <b>Your Ambitions</b> \n\n"
        "🚀 Всё, что нужно — это прогресс. Ты в игре?"
    )

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔥 Приобрести полный доступ", callback_data="full_access_coming_soon")],
        [InlineKeyboardButton(text="◀️ Назад", callback_data="monetization_back")]
    ])

    await message.answer(text, reply_markup=keyboard, parse_mode="HTML")


@router.callback_query(F.data == "full_access_coming_soon")
async def handle_full_access_coming_soon(callback: CallbackQuery):
    await callback.answer("⏳ Скоро будет доступно!", show_alert=True)