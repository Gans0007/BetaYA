from aiogram import Router, types
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from database import get_pool
from services.xp_service import LEAGUES
from services.xp_service import check_next_league

router = Router()

# -------------------------------
# 📊 Статистика
# -------------------------------
@router.callback_query(lambda c: c.data == "profile_stats")
async def show_stats(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    await callback.answer()

    pool = await get_pool()
    async with pool.acquire() as conn:
        user = await conn.fetchrow("""
            SELECT username, nickname, finished_habits, finished_challenges,
                   total_stars, total_confirmed_days, joined_at,
                   current_streak, max_streak, xp,
                   league, league_emoji
            FROM users
            WHERE user_id = $1
        """, user_id)

    if not user:
        await callback.message.edit_text("❌ Пользователь не найден.")
        return

    # ----------------------------
    # Извлекаем данные пользователя
    # ----------------------------
    nickname = user["nickname"] or "—"
    if nickname.startswith("@"):
        nickname = nickname[1:]

    current = user["current_streak"] or 0
    maximum = user["max_streak"] or 0
    habits = user["finished_habits"] or 0
    challenges = user["finished_challenges"] or 0
    stars = user["total_stars"] or 0
    confirmed_days = user["total_confirmed_days"] or 0
    xp = round(user["xp"] or 0, 1)
    joined_at = user["joined_at"].strftime("%d.%m.%Y") if user["joined_at"] else "—"

    league_name = user["league"]
    league_emoji = user["league_emoji"]

    # Получаем структуру текущей лиги
    league_data = next((l for l in LEAGUES if l["name"] == league_name), None)
    league_quote = league_data["quote"] if league_data else "—"

    # ----------------------------
    # Расчёт следующей лиги
    # ----------------------------
    current_index = next((i for i, l in enumerate(LEAGUES) if l["name"] == league_name), 0)

    if current_index < len(LEAGUES) - 1:
        next_league = LEAGUES[current_index + 1]
        stars_needed = max(0, next_league["stars"] - stars)
        xp_needed = max(0, next_league["xp"] - xp)
        next_req_text = f"(до следующей — {stars_needed}⭐ и {xp_needed} XP)"
    else:
        stars_needed = xp_needed = 0
        next_league = None
        next_req_text = "(максимальная лига)"

    # ----------------------------
    # 📊 Таблица статистики
    # ----------------------------
    table = (
        "<pre>"
        f"🪪 Nickname:            {nickname}\n"
        f"📅 Дата вступления:     {joined_at}\n"
        "--------------------------------------\n"
        f"🏆 Лига: {league_emoji} {league_name} {next_req_text}\n"
        "--------------------------------------\n"
        f"🌟 Звёзды   | XP      | $\n"
        f"{stars:<10} {xp:<8}  {0}\n"
        "--------------------------------------\n"
        f"🔥 Текущий стрик:          {current}\n"
        f"🏆 Максимальный стрик:      {maximum}\n"
        f"💪 Завершённых привычек:    {habits}\n"
        f"🏆 Завершённых челленджей:  {challenges}\n"
        f"📅 Подтверждённых дней:     {confirmed_days}\n"
        "</pre>"
    )

    # ----------------------------
    # Финальный текст
    # ----------------------------
    text = (
        f"📊 <b>Твоя статистика</b>\n\n"
        f"{table}\n"
        f"💬 <i>{league_quote}</i>\n\n"
        f"Продолжай в том же духе! 💥"
    )

    # ----------------------------
    # Кнопки
    # ----------------------------
    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🚀 Level Up", callback_data="next_league")],
            [InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_profile_menu")]
        ]
    )

    await callback.message.edit_text(text, parse_mode="HTML", reply_markup=kb)


# -------------------------------
# 🚀 ОБРАБОТЧИК LEVEL UP
# -------------------------------
@router.callback_query(lambda c: c.data == "next_league")
async def process_level_up(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    await callback.answer()

    pool = await get_pool()

    # проверяем возможность
    result = await check_next_league(user_id)

    # максимальная лига
    if not result["next_league"]:
        await callback.message.edit_text(
            "🔥 Ты уже достиг максимальной лиги!",
            reply_markup=InlineKeyboardMarkup(
                inline_keyboard=[[InlineKeyboardButton(text="⬅️ Назад", callback_data="profile_stats")]]
            )
        )
        return

    # условия НЕ выполнены → вернуть расчёт времени
    if not result["can_level_up"]:

        need_stars = result["need_stars"]
        need_xp = result["need_xp"]

        async with pool.acquire() as conn:
            conf_count = await conn.fetchval("""
                SELECT COUNT(*) FROM confirmations
                WHERE user_id = $1 AND datetime > NOW() - INTERVAL '7 days'
            """, user_id)

        if not conf_count:
            estimate = "Сделай хотя бы одно подтверждение, чтобы я рассчитал темп 💪"
        else:
            # Средний XP за неделю
            avg_xp = float((conf_count * 1.4) / 7)
            days = float(need_xp) / avg_xp if avg_xp > 0 else 999

            low = max(1, int(days * 0.85))
            high = max(1, int(days * 1.15))

            estimate = f"~ {low}–{high} дней при твоём текущем темпе 🔥"

        await callback.message.answer(
            f"⏳ <b>Примерно до новой лиги:</b>\n"
            f"{estimate}\n\n"
            f"⭐ Осталось: <b>{need_stars}⭐</b>\n"
            f"✨ Осталось: <b>{need_xp} XP</b>",
            parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup(
                inline_keyboard=[[InlineKeyboardButton(text="⬅️ Назад", callback_data="profile_stats")]]
            )
        )
        return

    # условия выполнены → повышаем
    next_l = result["next_league"]

    async with pool.acquire() as conn:
        await conn.execute("""
            UPDATE users
            SET league = $1,
                league_emoji = $2
            WHERE user_id = $3
        """, next_l["name"], next_l["emoji"], user_id)

    await callback.message.answer(
        f"🏆 Новая лига!\n"
        f"Ты поднялся до уровня: {next_l['emoji']} {next_l['name']}\n\n"
        f"«{next_l['quote']}»\n"
        f"Продолжай в том же духе 🚀"
    )
