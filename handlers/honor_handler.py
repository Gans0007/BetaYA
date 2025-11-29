import logging
from aiogram import Router, types, F
from aiogram.types import CallbackQuery, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from database import get_pool
from services.xp_service import LEAGUES
from handlers.tone.honor_board_tone import HONOR_TONE
import random

router = Router()
logger = logging.getLogger(__name__)

DIVIDER = "-" * 34


def get_rank_message(rank: int, tone: str) -> str:
    if tone not in HONOR_TONE:
        tone = "friend"

    if rank == 1:
        group = HONOR_TONE[tone]["1"]
    elif rank <= 3:
        group = HONOR_TONE[tone]["3"]
    elif rank <= 5:
        group = HONOR_TONE[tone]["5"]
    elif rank <= 10:
        group = HONOR_TONE[tone]["10"]
    elif rank <= 30:
        group = HONOR_TONE[tone]["30"]
    elif rank <= 50:
        group = HONOR_TONE[tone]["50"]
    elif rank <= 100:
        group = HONOR_TONE[tone]["100"]
    else:
        group = HONOR_TONE[tone]["else"]

    return random.choice(group)


async def safe_replace_message(msg: types.Message, text: str, kb=None):
    try:
        await msg.edit_text(text, reply_markup=kb, parse_mode="HTML")
    except:
        await msg.answer(text, reply_markup=kb, parse_mode="HTML")


def rating_keyboard(current: str):
    kb = InlineKeyboardBuilder()

    row1 = []

    if current != "world":
        row1.append(InlineKeyboardButton(text="🌍 По миру", callback_data="honor_world"))
    if current != "league":
        row1.append(InlineKeyboardButton(text="🏅 По лиге", callback_data="honor_league"))
    if current != "stars":
        row1.append(InlineKeyboardButton(text="⭐ По звёздам", callback_data="honor_stars"))

    kb.row(*row1)

    return kb.as_markup()


async def get_display_name(nickname: str):
    if nickname:
        return nickname[:8]
    return "anon"


def get_league_by_xp(xp: float):
    last = 0
    for i, lg in enumerate(LEAGUES):
        if xp >= lg["xp"]:
            last = i
    return last


# 🌍 ТОП ПО МИРУ
async def show_top10_world(msg):
    user_id = msg.from_user.id

    pool = await get_pool()
    async with pool.acquire() as conn:

        total = await conn.fetchval("SELECT COUNT(*) FROM users")

        rows = await conn.fetch("""
            SELECT user_id, nickname, xp, total_confirmed_days, current_streak, total_stars
            FROM users
            ORDER BY xp DESC
            LIMIT 10
        """)

        medals = ["👑", "🥈", "🥉"] + [f"{i}." for i in range(4, 11)]

        header = (
            "🏆 <b>Рейтинг (По миру)</b>\n"
            f"Всего участников: <b>{total}</b>\n\n"
        )

        table = [
            "<pre>\n"
            f"{'№':<3}{'Ник':<8}{'XP':>5}{'Дн':>5}{'🔥':>5}{'⭐':>3}\n"
            f"{DIVIDER}\n"
        ]

        for i, row in enumerate(rows):
            xp = round(float(row["xp"]), 1)
            days = row["total_confirmed_days"] or 0
            streak = row["current_streak"] or 0
            stars = row["total_stars"] or 0

            nick = await get_display_name(row["nickname"])
            medal = medals[i].ljust(4)

            table.append(
                f"{medal}{nick:<8} {xp:>4} {days:>4} {streak:>4} {stars:>4}\n"
            )

        # ВСЕГДА показываем позицию пользователя ниже
        pos = await conn.fetchrow("""
            SELECT r, nickname, xp, total_confirmed_days, current_streak, total_stars
            FROM (
                SELECT user_id, nickname, xp, total_confirmed_days, current_streak, total_stars,
                       ROW_NUMBER() OVER (ORDER BY xp DESC) AS r
                FROM users
            ) t WHERE user_id=$1
        """, user_id)

        if pos:
            nick = await get_display_name(pos["nickname"])

            rank = pos["r"]
            tone = await conn.fetchval(
                "SELECT notification_tone FROM users WHERE user_id=$1",
                user_id
            )
            msg_mot = get_rank_message(rank, tone)

            table.append(DIVIDER + "\n")
            table.append("🔽 Твоя позиция:\n")
            table.append(
                f"{rank}. {nick:<8}  "
                f"{round(float(pos['xp']), 1):>6} {pos['total_confirmed_days']:>6} "
                f"{pos['current_streak']:>6} {pos['total_stars']:>6}\n"
            )
            table.append(f"{msg_mot}\n")

        table.append("</pre>")
        text = header + "".join(table)

    await safe_replace_message(
        msg.message if isinstance(msg, CallbackQuery) else msg,
        text,
        kb=rating_keyboard("world")
    )

    if isinstance(msg, CallbackQuery):
        await msg.answer()


# 🏅 ТОП ПО ЛИГЕ
@router.callback_query(F.data == "honor_league")
async def honor_league(callback: CallbackQuery):
    user_id = callback.from_user.id

    pool = await get_pool()
    async with pool.acquire() as conn:

        xp_user = await conn.fetchval("SELECT xp FROM users WHERE user_id=$1", user_id)
        league_index = get_league_by_xp(xp_user)
        league = LEAGUES[league_index]

        users = await conn.fetch("""
            SELECT user_id, nickname, xp, total_confirmed_days, current_streak, total_stars
            FROM users ORDER BY xp DESC
        """)

        same = [u for u in users if get_league_by_xp(float(u["xp"])) == league_index]

        top10 = same[:10]
        medals = ["👑", "🥈", "🥉"] + [f"{i}." for i in range(4, 11)]

        header = (
            f"🏅 <b>Топ твоей лиги:</b> {league['name']} {league['emoji']}\n"
            f"Всего в лиге: <b>{len(same)}</b>\n\n"
        )

        table = [
            "<pre>\n"
            f"{'№':<3}{'Ник':<9}{'XP':>5}{'Дн':>5}{'🔥':>5}{'⭐':>4}\n"
            f"{DIVIDER}\n"
        ]

        for i, row in enumerate(top10):
            xp = round(float(row["xp"]), 1)
            days = row["total_confirmed_days"] or 0
            streak = row["current_streak"] or 0
            stars = row["total_stars"] or 0

            nick = await get_display_name(row["nickname"])
            medal = medals[i].ljust(4)

            table.append(
                f"{medal}{nick:<8} {xp:>4} {days:>4} {streak:>4} {stars:>4}\n"
            )

        # ВСЕГДА показываем позицию пользователя ниже (относительно своей лиги)
        rank = None
        pos_row = None
        for idx, row in enumerate(same, start=1):
            if row["user_id"] == user_id:
                rank = idx
                pos_row = row
                break

        if rank is not None and pos_row is not None:
            nick = await get_display_name(pos_row["nickname"])
            xp = round(float(pos_row["xp"]), 1)
            days = pos_row["total_confirmed_days"] or 0
            streak = pos_row["current_streak"] or 0
            stars = pos_row["total_stars"] or 0

            tone = await conn.fetchval(
                "SELECT notification_tone FROM users WHERE user_id=$1",
                user_id
            )
            msg_mot = get_rank_message(rank, tone)

            table.append(DIVIDER + "\n")
            table.append("🔽 Твоя позиция:\n")
            table.append(
                f"{rank}. {nick:<8}  {xp:>6} {days:>6} {streak:>6} {stars:>6}\n"
            )
            table.append(f"{msg_mot}\n")

        table.append("</pre>")
        text = header + "".join(table)

    await safe_replace_message(callback.message, text, rating_keyboard("league"))
    await callback.answer()


# ⭐ ТОП ПО ЗВЁЗДАМ
@router.callback_query(F.data == "honor_stars")
async def honor_stars(callback: CallbackQuery):
    user_id = callback.from_user.id

    pool = await get_pool()
    async with pool.acquire() as conn:

        total = await conn.fetchval("SELECT COUNT(*) FROM users")

        rows = await conn.fetch("""
            SELECT user_id, nickname, total_stars, xp, total_confirmed_days, current_streak
            FROM users ORDER BY total_stars DESC LIMIT 10
        """)

        medals = ["👑", "🥈", "🥉"] + [f"{i}." for i in range(4, 11)]

        header = (
            "⭐ <b>Рейтинг по звёздам</b>\n"
            f"Всего участников: <b>{total}</b>\n\n"
        )

        table = [
            "<pre>\n"
            f"{'№':<3}{'Ник':<9}{'⭐':>5}{'XP':>5}{'Дн':>5}{'🔥':>4}\n"
            f"{DIVIDER}\n"
        ]

        for i, row in enumerate(rows):
            stars = row["total_stars"]
            xp = round(float(row["xp"]), 1)
            days = row["total_confirmed_days"]
            streak = row["current_streak"]

            nick = await get_display_name(row["nickname"])
            medal = medals[i].ljust(4)

            table.append(
                f"{medal}{nick:<8} {stars:>4} {xp:>4} {days:>4} {streak:>4}\n"
            )

        userpos = await conn.fetchrow("""
            SELECT r, nickname, total_stars, xp, total_confirmed_days, current_streak FROM (
                SELECT user_id, nickname, total_stars, xp, total_confirmed_days, current_streak,
                       ROW_NUMBER() OVER (ORDER BY total_stars DESC) AS r
                FROM users
            ) tt WHERE user_id=$1
        """, user_id)

        if userpos:
            rank = userpos["r"]
            nick = await get_display_name(userpos["nickname"])
            tone = await conn.fetchval(
                "SELECT notification_tone FROM users WHERE user_id=$1",
                user_id
            )
            msg_mot = get_rank_message(rank, tone)

            table.append(DIVIDER + "\n")
            table.append("🔽 Твоя позиция:\n")
            table.append(
                f"{rank}. {nick:<8}  "
                f"{userpos['total_stars']:>6} {round(float(userpos['xp']), 1):>6} "
                f"{userpos['total_confirmed_days']:>6} {userpos['current_streak']:>6}\n"
            )
            table.append(f"{msg_mot}\n")

        table.append("</pre>")
        text = header + "".join(table)

    await safe_replace_message(callback.message, text, rating_keyboard("stars"))
    await callback.answer()


@router.callback_query(F.data == "honor_world")
async def honor_world(callback: CallbackQuery):
    await show_top10_world(callback)


@router.message(F.text == "🏆 Рейтинг")
async def open_rating(message: types.Message):
    await show_top10_world(message)
