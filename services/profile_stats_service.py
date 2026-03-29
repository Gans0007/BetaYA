# services/profile_stats_service.py
from repositories.profile_stats_repository import (
    get_user_stats,
    update_league,
    get_last_confirmations_for_week
)


from services.xp_service import LEAGUES, check_next_league
from services.achievements.achievements_service import (
    get_total_achievement_progress,
    build_progress_bar
)
from core.database import get_pool

from services.xp_service import get_league_by_name

class ProfileStatsService:

    async def build_stats_text(self, user_id: int):
        user = await get_user_stats(user_id)
        if not user:
            return None

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
        usdt = user["usdt_payments"] or 0
        joined_at = user["joined_at"].strftime("%d.%m.%Y") if user["joined_at"] else "—"

        league_name = user["league"]
        league_emoji = user["league_emoji"]

        league_data = get_league_by_name(league_name)
        league_quote = league_data["quote"] if league_data else "—"

        current_index = next((i for i, l in enumerate(LEAGUES) if l["name"] == league_name), 0)

        if current_index < len(LEAGUES) - 1:
            next_league = LEAGUES[current_index + 1]
            stars_needed = max(0, next_league["stars"] - stars)
            xp_needed = int(round(max(0, next_league["xp"] - xp)))
            next_req_text = f"(до следующей — {stars_needed}⭐ и {xp_needed} XP)"
        else:
            next_req_text = "(максимальная лига)"

        table = (
            "<pre>"
            f"🪪 Nickname:            {nickname}\n"
            f"📅 Дата вступления:     {joined_at}\n"
            "--------------------------------------\n"
            f"🏆 Лига: {league_emoji} {league_name} {next_req_text}\n"
            "--------------------------------------\n"
            f"🌟 Звёзды   | XP      | $\n"
            f"{stars:<10} {xp:<8}  {usdt}\n"
            "--------------------------------------\n"
            f"🔥 Текущий стрик:          {current}\n"
            f"⚡️ Максимальный стрик:      {maximum}\n"
            f"💪 Завершённых привычек:    {habits}\n"
            f"🦾 Завершённых челленджей:  {challenges}\n"
            f"📅 Подтверждённых дней:     {confirmed_days}\n"

        )

        # --- ОБЩИЙ ПРОГРЕСС ДОСТИЖЕНИЙ ---
        pool = await get_pool()
        async with pool.acquire() as conn:
            progress = await get_total_achievement_progress(conn, user_id)

        bar = build_progress_bar(progress["percent"])

        achievements_block = (
            "🔥 Достижений: "
            f"{progress['completed']} / {progress['total']}\n"
            f"📊 {bar}\n"
            "</pre>"
        )


        final_text = (
            f"📊 <b>Твоя статистика</b>\n\n"
            f"{table}\n"
            f"{achievements_block}\n"
            f"💬 <i>{league_quote}</i>\n\n"
        )

        return final_text

    async def process_level_up_request(self, user_id: int):
        """Вся бизнес-логика перехода на следующую лигу"""
        result = await check_next_league(user_id)

        return result

    #-----------------------------------------
    #переход на следующую лигу
    #-----------------------------------------
    async def auto_level_up(self, bot, user_id: int):
        """
        Автоматически повышает лигу, если выполнены условия.
        Поддерживает несколько апов подряд.
        """

        from services.xp_service import check_next_league
        from core.database import get_pool
        import json

        upgrades = []

        pool = await get_pool()

        while True:
            result = await check_next_league(user_id)

            # нет следующей лиги
            if not result.get("next_league"):
                break

            # условия не выполнены
            if not result.get("can_level_up"):
                break

            next_l = result["next_league"]
  
            # применяем ап
            async with pool.acquire() as conn:
                async with conn.transaction():

                    # обновляем лигу
                    await conn.execute("""
                        INSERT INTO user_stats (user_id, league, league_emoji)
                        VALUES ($1, $2, $3)
                        ON CONFLICT (user_id) DO UPDATE
                        SET league = EXCLUDED.league,
                            league_emoji = EXCLUDED.league_emoji
                    """, user_id, next_l["name"], next_l["emoji"])


                    await conn.execute("""
                        INSERT INTO user_events (user_id, type, value, meta)
                        VALUES ($1, 'league_up', $2, $3)
                    """, user_id, next_l["name"], json.dumps({
                        "emoji": next_l["emoji"]
                    }))

            upgrades.append(next_l)


        # 🔔 уведомление (если был хотя бы 1 ап)
        if upgrades:
            text = "🏆 <b>Повышение!</b>\n\n"

            for u in upgrades:
                text += f"{u['emoji']} {u['name']}\n"

            text += "\nТы растёшь. Продолжай."

            try:
                await bot.send_message(user_id, text, parse_mode="HTML")
                print("[LEVEL UP] message sent")
            except Exception as e:
                print(f"[LEVEL UP ERROR] {e}")

    async def apply_level_up(self, user_id: int, league_name: str, emoji: str):
        await update_league(user_id, league_name, emoji)

    async def get_weekly_confirmation_rate(self, user_id: int):
        return await get_last_confirmations_for_week(user_id)


profile_stats_service = ProfileStatsService()