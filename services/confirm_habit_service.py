import random
from datetime import datetime
import pytz

from data.challenges_data import FINAL_MESSAGES
from services.user_service import recalculate_total_confirmed_days, update_user_streak
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
    choose_target_chat,
    get_habit_progress,
    get_challenge_habit,
    get_completed_challenge,
    update_completed_challenge,
    insert_completed_challenge,
    update_user_challenge_counters,
)



class HabitService:
    """
    Полная логика подтверждения привычки.
    Поведение 1-в-1 как в исходном confirm_habit_handler.
    """

    # ================================
    #  Старт подтверждения (callback confirm_)
    # ================================
    async def start_confirmation(self, conn, user_id: int, habit_id: int):
        """
        Возвращает:
        - error: None / "HABIT_NOT_FOUND"
        - reverify: bool
        - text: текст для сообщения
        - parse_mode: "Markdown" или None
        """

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
                # REVERIFY
                text = (
                    "♻️ Уже есть подтверждение сегодня.\n"
                    f"Пришли новое медиа, чтобы *переподтвердить* {title}."
                )
                return {
                    "error": None,
                    "reverify": True,
                    "text": text,
                    "parse_mode": "Markdown",
                }

        # обычное подтверждение
        text = (
            f"📸 Пришли фото, видео или кружочек для подтверждения {title} 💪"
        )
        return {
            "error": None,
            "reverify": False,
            "text": text,
            "parse_mode": "Markdown",
        }

    # ================================
    #  Обработка медиа (message в FSM)
    # ================================
    async def process_confirmation_media(
        self,
        conn,
        user_id: int,
        habit_id: int,
        file_id: str,
        file_type: str,
        reverify: bool,
    ):
        """
        Полностью повторяет поведение оригинального receive_media.
        Возвращает словарь:
        - error
        - self_message
        - target_chat
        - share_allowed
        - caption_text
        - file_type
        - file_id
        - challenge_message (или None)
        """

        exists = await habit_exists(conn, habit_id)
        if not exists:
            return {"error": "HABIT_NOT_FOUND"}

        # =============================
        # ♻️ REVERIFY
        # =============================
        if reverify:
            await update_last_confirmation_media(
                conn, file_id, file_type, user_id, habit_id
            )

            await recalculate_total_confirmed_days(user_id)
            self_message = "♻️ Переподтверждение обновлено 💪"

        # =============================
        # ✔ Новое подтверждение
        # =============================
        else:
            await insert_confirmation(conn, user_id, habit_id, file_id, file_type)

            await update_user_streak(user_id)
            xp_gain = await add_xp_for_confirmation(user_id, habit_id)

            await increment_done_days(conn, habit_id)
            await recalculate_total_confirmed_days(user_id)

            # АНТИ-ФАРМ XP — 1-в-1 как в исходнике
            count_today = await get_confirmations_count_today(conn, user_id)

            if count_today <= 3 and xp_gain > 0:
                variants = [
                    f"✨ +{xp_gain} XP\n🔥 Мощно! Следующий шаг — ещё сильнее.",
                    f"✨ +{xp_gain} XP\n💪 Вот это дисциплина. Продолжаем!",
                    f"✨ +{xp_gain} XP\n⚡ Каждый день приносит результат!",
                    f"✨ +{xp_gain} XP\n🏆 Ты укрепляешь свои амбиции."
                ]
                self_message = random.choice(variants)

            elif count_today == 4 and xp_gain == 0:
                self_message = (
                    "⚠️ Максимум 3 уникальных подтверждения в сутки!\n"
                    "Подтверждение засчитано, но XP не начислено."
                )
            else:
                variants_no_xp = [
                    "✅ Подтверждено. Двигаемся дальше!",
                    "🔥 День закрыт. Ты на пути к цели.",
                    "⚡ Дисциплина соблюдена!",
                    "🏆 Отлично. Поставил галочку — идём выше."
                ]
                self_message = random.choice(variants_no_xp)

        # =============================
        # 🔥 ОТПРАВКА В ЧАТ (данные)
        # =============================
        user_row = await get_user_notification_data(conn, user_id)
        target_chat = choose_target_chat(user_row)
        share_allowed = user_row["share_confirmation_media"]
        nickname = user_row["nickname"]

        habit_info = await get_habit_progress(conn, habit_id)
        habit_name = habit_info["name"]
        total_days = habit_info["days"]
        current_day = habit_info["done_days"]
        percent = round((current_day / total_days) * 100)

        if reverify:
            action_text = "♻️ переподтвердил"
        else:
            action_text = "💪 подтвердил"

        caption_text = (
            f"{action_text} *{nickname}* привычку *“{habit_name}”*\n"
            f"📅 День {current_day} из {total_days} ({percent}%)"
        )

        # ===========================================================
        # 🔥 Шаг 4: автозавершение челленджа (1-в-1 как в исходнике)
        # ===========================================================
        challenge_message = None

        habit_row = await get_challenge_habit(conn, habit_id)
        if habit_row and habit_row["is_challenge"] and habit_row["done_days"] >= habit_row["days"]:
            existing = await get_completed_challenge(
                conn, habit_row["user_id"], habit_row["challenge_id"]
            )

            if existing:
                new_count = min(existing["repeat_count"] + 1, 3)
                await update_completed_challenge(
                    conn, new_count, habit_row["user_id"], habit_row["challenge_id"]
                )
                stars = new_count
            else:
                await insert_completed_challenge(
                    conn, habit_row["user_id"], habit_row["name"], habit_row["challenge_id"]
                )
                stars = 1

            stars_delta = 1 if not existing else stars - existing["repeat_count"]
            await update_user_challenge_counters(
                conn, stars_delta, habit_row["user_id"]
            )

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

        return {
            "error": None,
            "self_message": self_message,
            "target_chat": target_chat,
            "share_allowed": share_allowed,
            "caption_text": caption_text,
            "file_type": file_type,
            "file_id": file_id,
            "challenge_message": challenge_message,
        }


# Глобальный экземпляр, как у тебя subscription_service и т.п.
habit_service = HabitService()
