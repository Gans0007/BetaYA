from aiogram import Router, types, F
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
import logging

from services.challenge_service import (
    get_level_info,
    is_level_unlocked,
    get_challenge_list,
    activate_challenge,
    get_difficulty,
    get_days_for_repeat
)

from data.challenges_data import LEVEL_QUOTES

from services.access_service import can_add_habit
from services.subscription_message_service import show_subscription_limit_message

router = Router()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(message)s",
)


# ============================================================
#              ВЫВОД СПИСКА УРОВНЕЙ ЧЕЛЛЕНДЖЕЙ
# ============================================================
@router.callback_query(F.data == "choose_from_list")
async def show_levels(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    logging.info(f"[CHALLENGE] Пользователь {user_id} открыл список уровней челленджей")

    stars, levels_dict = await get_level_info(user_id)

    keyboard = []
    for level_key, name in levels_dict.items():
        if not is_level_unlocked(level_key, stars) and level_key != "level_0":
            name = "🔒 " + name

        keyboard.append([
            InlineKeyboardButton(text=name, callback_data=level_key)
        ])

    keyboard.append([
        InlineKeyboardButton(text="⬅ Назад", callback_data="back_to_add_menu")
    ])

    await callback.message.edit_text(
        "💪 Выбери уровень челленджей:",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard)
    )
    await callback.answer()


# ============================================================
#                   СПИСОК ЧЕЛЛЕНДЖЕЙ УРОВНЯ
# ============================================================
@router.callback_query(F.data.startswith("level_"))
async def show_challenges(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    level_key = callback.data

    logging.info(f"[CHALLENGE] Пользователь {user_id} открыл уровень {level_key}")

    stars, levels_dict = await get_level_info(user_id)

    if not is_level_unlocked(level_key, stars):
        logging.info(f"[CHALLENGE] У пользователя {user_id} недостаточно звёзд для {level_key}")
        await callback.answer("Недостаточно ⭐ для доступа!", show_alert=True)
        return

    challenges, active_ids, active_diff, completed = \
        await get_challenge_list(user_id, level_key)

    level_name = levels_dict[level_key]
    quote = LEVEL_QUOTES[level_key]

    keyboard = []
    for index, (cid, title, desc_dict, ctype) in enumerate(challenges):

        if cid in active_ids:
            diff = active_diff.get(cid, 1)
            prefix = f"🔥 ⭐{diff}"

        elif cid in completed:
            stars_count = min(completed[cid], 3)
            prefix = "⭐" * stars_count + "☆" * (3 - stars_count)

        else:
            prefix = ""

        keyboard.append([
            InlineKeyboardButton(
                text=f"{prefix} {title}".strip(),
                callback_data=f"challenge|{level_key}|{index}"
            )
        ])

    keyboard.append([
        InlineKeyboardButton(text="⬅ Назад", callback_data="choose_from_list")
    ])

    await callback.message.edit_text(
        f"📋 *{level_name}*\n\n💬 {quote}\n\nВыбери челлендж:",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard)
    )

    await callback.answer()


# ============================================================
#                      ДЕТАЛИ ЧЕЛЛЕНДЖА
# ============================================================
@router.callback_query(F.data.startswith("challenge|"))
async def show_challenge_detail(callback: types.CallbackQuery):
    _, level_key, index_str = callback.data.split("|")
    index = int(index_str)
    user_id = callback.from_user.id

    logging.info(f"[CHALLENGE] Пользователь {user_id} смотрит детали челленджа index={index} в {level_key}")

    challenges, active_ids, active_diff, completed = \
        await get_challenge_list(user_id, level_key)

    cid, title, desc_dict, ctype = challenges[index]

    repeat = completed.get(cid, 0)
    difficulty = get_difficulty(repeat)
    days = get_days_for_repeat(repeat)
    desc_to_show = desc_dict[difficulty]

    stars_display = "⭐" * repeat + "☆" * (3 - repeat)

    text = (
        f"🏁 *{title}*\n\n"
        f"📖 {desc_to_show}\n\n"
        f"📅 Продолжительность: *{days} дней*\n"
        f"⭐ Прогресс: {stars_display}\n\n"
        f"Взять челлендж?"
    )

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Взять", callback_data=f"accept|{level_key}|{index}")],
        [InlineKeyboardButton(text="⬅ Назад", callback_data=level_key)]
    ])

    await callback.message.edit_text(text, parse_mode="Markdown", reply_markup=keyboard)
    await callback.answer()


# ============================================================
#                  ПРИНЯТЬ / АКТИВИРОВАТЬ ЧЕЛЛЕНДЖ
# ============================================================
@router.callback_query(F.data.startswith("accept|"))
async def accept_challenge_handler(callback: types.CallbackQuery):
    _, level_key, index_str = callback.data.split("|")
    index = int(index_str)
    user_id = callback.from_user.id

    logging.info(f"[CHALLENGE] Пользователь {user_id} пытается взять челлендж index={index} в {level_key}")

    # ✅ NEW: лимит проверяем именно при попытке взять (создать) челлендж
    allowed, active_count = await can_add_habit(user_id)
    if not allowed:
        await callback.answer()
        await show_subscription_limit_message(callback.message, active_count)
        return

    challenges, active_ids, active_diff, completed = \
        await get_challenge_list(user_id, level_key)

    cid, title, desc_dict, ctype = challenges[index]

    if cid in active_ids:
        logging.info(f"[CHALLENGE] Пользователь {user_id} уже имеет активный челлендж '{title}'")
        await callback.answer("Этот челлендж уже активен!", show_alert=True)
        return

    repeat = completed.get(cid, 0)
    difficulty, days = await activate_challenge(
        user_id, cid, title, desc_dict, repeat, ctype
    )

    logging.info(f"[CHALLENGE] Пользователь {user_id} начал челлендж '{title}', уровень={difficulty}, дней={days}")

    await callback.message.edit_text(
        f"🔥 Ты начал челлендж: *{title}*\n"
        f"⭐ Уровень: {difficulty} из 3\n"
        f"📅 Длительность: {days} дней\n\n"
        f"Теперь он в твоих Активных заданиях 💪🔥",
        parse_mode="Markdown"
    )
    await callback.answer()