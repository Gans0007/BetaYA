from datetime import datetime
import pytz
import random

from core.database import get_pool
from data.challenges_data import FINAL_MESSAGES
from services.user_service import recalculate_total_confirmed_days
from services.xp_service import add_xp_for_confirmation

from repositories.confirm_habit_repository import (
    get_user_timezone,
    get_habit_for_start,
    get_last_confirmation_for_habit,
    habit_exists,
    update_last_confirmation_media,
    insert_confirmation,
    increment_done_days,
    get_confirmations_count_today,
    get_user_notification_data,
    get_habit_progress,
    get_challenge_habit,
    get_completed_challenge,
    update_completed_challenge,
    insert_completed_challenge,
)

from services.user_stats_service import (
    increment_finished_challenges,
    increment_total_stars,
)


from handlers.tone.confirm_habit_service_tone import HABIT_CONFIRM_TONE
from handlers.tone.confirm_caption_tone import HABIT_CAPTION_TONE

from services.achievements.achievements_service import check_and_grant_achievements


class HabitService:

    # ================================
    # START CONFIRMATION (обёртка)
    # ================================
    async def start_confirmation(self, user_id: int, habit_id: int):
        pool = await get_pool()
        async with pool.acquire() as conn:
            async with conn.transaction():
                return await self._start_confirmation_logic(conn, user_id, habit_id)

    async def _start_confirmation_logic(self, conn, user_id, habit_id):
        user_row = await get_user_timezone(conn, user_id)
        user_tz = user_row["timezone"] if user_row else "Europe/Kyiv"
        tz = pytz.timezone(user_tz)
        now = datetime.now(tz)

        habit = await get_habit_for_start(conn, habit_id)
        if not habit:
            return {"error": "HABIT_NOT_FOUND"}

        habit_name = habit["name"]
        is_challenge = habit["is_challenge"]
        title = f"челленджа *{habit_name}*" if is_challenge else f"привычки *{habit_name}*"

        last = await get_last_confirmation_for_habit(conn, user_id, habit_id)

        if last:
            last_dt = last["datetime"].astimezone(tz)
            if last_dt.date() == now.date():
                return {
                    "error": None,
                    "reverify": True,
                    "text": f"♻️ Уже есть подтверждение сегодня.\nПришли новое медиа, чтобы *переподтвердить* {title}.",
                    "parse_mode": "Markdown",
                }

        return {
            "error": None,
            "reverify": False,
            "text": f"📸 Пришли фото, видео или кружочек для подтверждения {title} 💪",
            "parse_mode": "Markdown",
            "allow_no_media": True,
        }

    # ================================
    # PROCESS MEDIA (обёртка)
    # ================================
    async def process_confirmation_media(
        self,
        user_id: int,
        habit_id: int,
        file_id: str | None,
        file_type: str | None,
        reverify: bool,
    ):
        pool = await get_pool()
        async with pool.acquire() as conn:
            async with conn.transaction():
                return await self._process_confirmation_logic(
                    conn,
                    user_id,
                    habit_id,
                    file_id,
                    file_type,
                    reverify,
                )

    async def _process_confirmation_logic(
        self,
        conn,
        user_id,
        habit_id,
        file_id,
        file_type,
        reverify,
    ):

        exists = await habit_exists(conn, habit_id)
        if not exists:
            return {"error": "HABIT_NOT_FOUND"}

        # 🏆 Список новых достижений
        new_achievements = []

        # === дальше оставляешь весь свой старый код ===
        # НИЧЕГО ВНУТРИ ЛОГИКИ МЕНЯТЬ НЕ НУЖНО


        # =============================
        # ♻️ REVERIFY
        # =============================
        if reverify:
            if file_id and file_type:
                await update_last_confirmation_media(
                    conn,
                    file_id,
                    file_type,
                    user_id,
                    habit_id
                )

            await recalculate_total_confirmed_days(conn, user_id)
            self_message = "♻️ Переподтверждение обновлено 💪"

        else:
            # новое подтверждение
            await insert_confirmation(conn, user_id, habit_id, file_id, file_type)

            from services.user_stats_service import update_user_streak

            await update_user_streak(conn, user_id)

            # сброс streak для челленджа
            habit_row = await get_challenge_habit(conn, habit_id)
            if habit_row and habit_row["is_challenge"]:
                await conn.execute("""
                    UPDATE habits
                    SET reset_streak = 0
                    WHERE id = $1
                """, habit_id)

            xp_gain = await add_xp_for_confirmation(conn, user_id, habit_id)

            await increment_done_days(conn, habit_id)
            await recalculate_total_confirmed_days(conn, user_id)

            # =============================
            # 🏆 ПРОВЕРКА ДОСТИЖЕНИЙ
            # =============================
            new_achievements = await check_and_grant_achievements(conn, user_id)

            count_today = await get_confirmations_count_today(conn, user_id)

            # выбираем тон сообщения
            tone = await conn.fetchval("SELECT notification_tone FROM users WHERE user_id=$1", user_id)
            if tone not in HABIT_CONFIRM_TONE:
                tone = "friend"

            if xp_gain > 0 and count_today <= 3:
                self_message = random.choice(HABIT_CONFIRM_TONE[tone]["with_xp"]).format(xp=xp_gain)

            elif count_today == 4:
                self_message = (
                    "⚠️ Максимум 3 уникальных подтверждения в сутки!\n"
                    "Подтверждение засчитано, но XP не начислено."
                )

            else:
                self_message = random.choice(HABIT_CONFIRM_TONE[tone]["no_xp"])

        # =============================
        # 📌 ПОДГОТОВКА ТЕКСТА ДЛЯ ЧАТА
        # =============================
        user_row = await get_user_notification_data(conn, user_id)
        share_allowed = user_row["share_confirmation_media"]
        nickname = user_row["nickname"]

        habit_info = await get_habit_progress(conn, habit_id)
        habit_name = habit_info["name"]
        total_days = habit_info["days"] or 1
        current_day = habit_info["done_days"]

        percent = round((current_day / total_days) * 100)

        action_text = "♻️ переподтвердил" if reverify else "💪 подтвердил"

        tone = user_row.get("notification_tone") or "friend"
        if tone not in HABIT_CAPTION_TONE:
            tone = "friend"

        caption_raw = random.choice(HABIT_CAPTION_TONE[tone])

        try:
            caption_text = caption_raw.format(
                action=action_text,
                nickname=nickname,
                habit_name=habit_name,
                current_day=current_day,
                total_days=total_days,
                percent=percent,
            )
        except:
            caption_text = (
                f"{action_text} *{nickname}* привычку *“{habit_name}”*\n"
                f"📅 День {current_day} из {total_days} ({percent}%)"
            )

        # =============================
        # 🔥 АВТОЗАВЕРШЕНИЕ ЧЕЛЛЕНДЖА
        # =============================
        challenge_message = None

        habit_row = await get_challenge_habit(conn, habit_id)
        if habit_row and habit_row["is_challenge"] and habit_row["done_days"] >= habit_row["days"]:

            existing = await get_completed_challenge(conn, habit_row["user_id"], habit_row["challenge_id"])

            if existing:
                new_count = min(existing["repeat_count"] + 1, 3)
                await update_completed_challenge(conn, new_count, habit_row["user_id"], habit_row["challenge_id"])
                stars = new_count
            else:
                await insert_completed_challenge(conn, habit_row["user_id"], habit_row["name"], habit_row["challenge_id"])
                stars = 1

            stars_delta = 1 if not existing else stars - existing["repeat_count"]

            # 🔹 +1 к завершённым челленджам
            await increment_finished_challenges(conn, habit_row["user_id"])

            # 🔹 начисляем звёзды только если они есть
            if stars_delta > 0:
                await increment_total_stars(conn, habit_row["user_id"], stars_delta)


            cid = habit_row["challenge_id"]
            stars_display = "⭐" * stars + "☆" * (3 - stars)
            final_msg = FINAL_MESSAGES.get(cid, {}).get(stars, "")

            text = (
                f"🔥 Челлендж *{habit_row['name']}* завершён!\n"
                f"🏆 Результат: {stars_display}\n\n"
            )

            if final_msg:
                text += final_msg + "\n\n"

            text += "Продолжаем доминировать 💪"
            challenge_message = text

            # ❌ УДАЛЯЕМ ЧЕЛЛЕНДЖ НАВСЕГДА
            await conn.execute("""
                DELETE FROM habits
                WHERE id = $1
            """, habit_id)

        return {
            "error": None,
            "self_message": self_message,
            "share_allowed": share_allowed,
            "caption_text": caption_text,
            "file_type": file_type,
            "file_id": file_id,
            "challenge_message": challenge_message,
            "new_achievements": new_achievements,
        }


habit_service = HabitService()
