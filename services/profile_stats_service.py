# services/profile_stats_service.py
from repositories.profile_stats_repository import (
    get_user_stats,
    update_league,
    get_last_confirmations_for_week
)
from services.xp_service import LEAGUES, check_next_league


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
        joined_at = user["joined_at"].strftime("%d.%m.%Y") if user["joined_at"] else "—"

        league_name = user["league"]
        league_emoji = user["league_emoji"]

        league_data = next((l for l in LEAGUES if l["name"] == league_name), None)
        league_quote = league_data["quote"] if league_data else "—"

        current_index = next((i for i, l in enumerate(LEAGUES) if l["name"] == league_name), 0)

        if current_index < len(LEAGUES) - 1:
            next_league = LEAGUES[current_index + 1]
            stars_needed = max(0, next_league["stars"] - stars)
            xp_needed = max(0, next_league["xp"] - xp)
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
            f"{stars:<10} {xp:<8}  {0}\n"
            "--------------------------------------\n"
            f"🔥 Текущий стрик:          {current}\n"
            f"🏆 Максимальный стрик:      {maximum}\n"
            f"💪 Завершённых привычек:    {habits}\n"
            f"🏆 Завершённых челленджей:  {challenges}\n"
            f"📅 Подтверждённых дней:     {confirmed_days}\n"
            "</pre>"
        )

        final_text = (
            f"📊 <b>Твоя статистика</b>\n\n"
            f"{table}\n"
            f"💬 <i>{league_quote}</i>\n\n"
            f"Продолжай в том же духе! 💥"
        )

        return final_text

    async def process_level_up_request(self, user_id: int):
        """Вся бизнес-логика перехода на следующую лигу"""
        result = await check_next_league(user_id)

        return result

    async def apply_level_up(self, user_id: int, league_name: str, emoji: str):
        await update_league(user_id, league_name, emoji)

    async def get_weekly_confirmation_rate(self, user_id: int):
        return await get_last_confirmations_for_week(user_id)


profile_stats_service = ProfileStatsService()
