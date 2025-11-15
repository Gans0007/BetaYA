from aiogram import Router, types, F
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from database import get_pool

router = Router()

# -------------------------------
# 🌟 Требования по звёздам для уровней
# -------------------------------
LEVEL_UNLOCKS = {
    "level_0": 0,
    "level_1": 4,
    "level_2": 8,
    "level_3": 13,
    "level_4": 20,
    "level_5": 22,
}

# -------------------------------
# 🔹 Названия уровней
# -------------------------------
CHALLENGE_LEVELS = {
    "ru": {
        "level_0": "🔰 Новичок",
        "level_1": "Активность",
        "level_2": "Фокус и энергия",
        "level_3": "Самодисциплина",
        "level_4": "Преодоление",
        "level_5": "Для будущих предпринимателей",
    }
}

# -------------------------------
# 🔹 Цитаты к уровням
# -------------------------------
LEVEL_QUOTES = {
    "level_0": "«Начинаем с малого…» 💫",
    "level_1": "«Движение — жизнь» 🏃‍♂️",
    "level_2": "«Внимание = энергия» ⚡️",
    "level_3": "«Самодисциплина = мост» 💪",
    "level_4": "«Преодоление формирует характер» 🧱",
    "level_5": "«Предприниматель видит возможности» 🚀",
}

# -------------------------------
# 🔹 Структура челленджей
# -------------------------------
CHALLENGES = {
    "level_0": [
        (
            "0_reading",
            "Книга",
            {
                1: "Читай 1 страницу каждый день. Это создаёт привычку фокусироваться хотя бы минимально.",
                2: "Теперь читай 3 страницы. Это уже лёгкое погружение без перегрузки.",
                3: "Читай 5 страниц. Это формирует дисциплину и глубину мышления."
            },
            "media"
        ),
        (
            "0_walking",
            "Поймать мысль",
            {
                1: "Запиши одну мысль в день — это развивает наблюдательность.",
                2: "Записывай 2 мысли — начинаешь понимать свои внутренние процессы.",
                3: "Записывай 3 мысли — это уже осознанность на новом уровне."
            },
            "media"
        ),
        (
            "0_warmup",
            "Зарядка",
            {
                1: "Сделай 1 минуту зарядки — просто включи тело.",
                2: "Делай 2 минуты — мягкая, но стойкая дисциплина.",
                3: "Делай 3 минуты — формируешь сильный утренний ритуал."
            },
            "media"
        ),
        (
            "0_pushups",
            "Отжимания",
            {
                1: "Выполни 1 отжимание — лёгкий вход в спорт.",
                2: "Сделай 3 отжимания — стабильная активация тела.",
                3: "Сделай 5 отжиманий — формируешь базовый уровень силы."
            },
            "media"
        ),
        (
            "0_learnings",
            "Изучение",
            {
                1: "Учись 1 новому слову в день — лёгкая активация мозга.",
                2: "Учись 2 словам — формируешь устойчивую память.",
                3: "Учись 3 словам — ускоряешь развитие словарного запаса."
            },
            "media"
        ),
        (
            "0_squats",
            "Благодарность",
            {
                1: "Запиши 1 благодарность — это развивает позитивное мышление.",
                2: "Запиши 2 благодарности — начинаешь видеть хорошее чаще.",
                3: "Запиши 3 благодарности — полностью меняешь внутренний настрой."
            },
            "media"
        ),
        (
            "0_plank",
            "Подкаст / Аудиокнига",
            {
                1: "Слушай 1 минуту — лёгкое включение ума.",
                2: "Слушай 3 минуты — тренируешь фокус.",
                3: "Слушай 5 минут — формируешь привычку обучаться."
            },
            "media"
        ),
        (
            "0_jumps",
            "Уединение",
            {
                1: "Сиди в тишине 1 минуту — знакомство с собой.",
                2: "Сиди 3 минуты — успокаивается ум.",
                3: "Сиди 5 минут — мини-медитация, дающая контроль над мыслями."
            },
            "media"
        ),
        (
            "0_splits",
            "Шпагат",
            {
                1: "Тянись 1 минуту — даёшь телу гибкость.",
                2: "Тянись 2 минуты — мышцы начинают раскрываться.",
                3: "Тянись 3 минуты — формируется упругость и здоровье тела."
            },
            "media"
        ),
        (
            "0_lay_bad",
            "Кровать",
            {
                1: "Заправь кровать — создаёшь порядок с самого утра.",
                2: "Сделай это аккуратно — формируешь уважение к себе.",
                3: "Заправляй идеально — это фундамент дисциплины."
            },
            "media"
        ),
        (
            "0_not_touch",
            "Телефон",
            {
                1: "Не трогай телефон 1 минуту после пробуждения.",
                2: "Теперь 3 минуты — даёшь мозгу спокойный запуск.",
                3: "5 минут — ты контролируешь утро, а не соцсети."
            },
            "media"
        ),
        (
            "0_money",
            "Фин. Грамотность",
            {
                1: "Откладывай по 1 монете / гривне / доллару ежедневно.",
                2: "Откладывай по 2 — формируешь финансовую дисциплину.",
                3: "Откладывай по 3 — прокачиваешь мышление инвестора."
            },
            "media"
        ),
    ],

    "level_1": [
        ("1_no_phone_morning", "Без телефона утром", "Начни день без телефона.", "media"),
        ("1_warmup_5", "Зарядка 5 минут", "Лёгкая зарядка 5 минут.", "media"),
        ("1_walk_10", "Прогулка 10 минут", "Гулять 10 минут.", "media"),
        ("1_sleep_23", "Сон до 23:00", "Лечь спать до 23:00.", "media"),
        ("1_water_morning", "Утренняя вода", "Пить воду после пробуждения.", "media"),
    ],
    "level_2": [
        ("2_deep_reading_30", "Чтение 30 мин", "Чтение без отвлечений.", "media"),
        ("2_steps_5000", "5000 шагов", "Пройти минимум 5000 шагов.", "media"),
        ("2_affirmations", "Аффирмации", "Повторять свою формулу силы.", "media"),
        ("2_visualization", "Визуализация", "Представлять результат 5 минут.", "media"),
        ("2_discipline_journal", "Дневник дисциплины", "Писать итоги дня.", "media"),
        ("2_daily_circle", "Кружок", "Записывать голос/видео.", "media"),
        ("2_day_plan", "Планирование", "Писать 3 задачи на день.", "media"),
        ("2_training_10", "Тренировка 10 мин", "Лёгкая тренировка.", "media"),
        ("2_expense_log", "Учёт расходов", "Записывать траты.", "media"),
        ("2_reading_10", "Чтение 10 минут", "Читать 10 минут.", "media"),
    ],
    "level_3": [
        ("3_no_swear", "Без мата", "Следить за речью.", "media"),
        ("3_no_sugar", "Без сахара", "Не употреблять сахар.", "media"),
        ("3_no_fastfood", "Без фастфуда", "Без вредной еды.", "media"),
        ("3_compliment", "Комплимент", "Сделать комплимент.", "media"),
        ("3_meditation", "Медитация", "Медитировать 5 минут.", "media"),
        ("3_thought_watch", "Наблюдать мысли", "5 минут без реакции.", "media"),
        ("3_tg_post", "Пост в Telegram", "Писать отчёт.", "media"),
        ("3_study", "Учёба", "30 минут учиться.", "media"),
        ("3_barefoot", "Ходьба босиком", "15 минут босиком.", "media"),
        ("3_cold_shower", "Холодный душ", "Принять холодный душ.", "media"),
        ("3_silence_hour", "Час молчания", "Полное молчание 1 час.", "media"),
    ],
    "level_4": [
        ("4_steps_10000", "10 000 шагов", "Пройти 10 000 шагов.", "media"),
        ("4_pullups_10", "10 подтягиваний", "10 подтягиваний подряд.", "media"),
        ("4_pushups_50", "50 отжиманий", "50 отжиманий подряд.", "media"),
        ("4_run_3k", "Бег 3 км", "Пробежать 3 км.", "media"),
        ("4_no_mirrors", "Без зеркал", "Не смотреть в зеркала.", "media"),
        ("4_kneel_rest", "Отдых на коленях", "Отдых сидя на коленях.", "media"),
        ("4_ask_discount", "Попросить скидку", "Попросить скидку.", "media"),
        ("4_silence", "Тишина", "Без музыки весь день.", "media"),
        ("4_cold_shower_circle", "Душ + кружок", "Холодный душ и видео.", "media"),
        ("4_digital_detox", "Диджитал детокс", "Не заходить в соцсети.", "media"),
    ],
    "level_5": [
        ("5_omad", "1 приём пищи", "Есть 1 раз в день.", "media"),
        ("5_two_workouts", "2 тренировки", "2 тренировки в день.", "media"),
        ("5_nofap", "NoFap", "Контроль сексуальной энергии.", "media"),
        ("5_no_porn", "Без порно", "Никакого порноконтента.", "media"),
        ("5_plank_30s", "Планка 30 сек", "Планка 30 секунд.", "media"),
        ("5_wakeup_430", "Подъём 4:30", "Просыпаться в 4:30.", "media"),
        ("5_sensory_isolation", "Изоляция", "Никаких звуков/видео.", "media"),
        ("5_phone_box", "Телефон в коробку", "Убрать телефон на 2 часа.", "media"),
        ("5_stairs_only", "Только лестница", "Не пользоваться лифтом.", "media"),
        ("5_focus_2h", "Фокус 2 часа", "Работать 2 часа без отвлечений.", "media"),
    ],
}



# ============================================================
#                     ВЫБОР УРОВНЯ
# ============================================================

@router.callback_query(F.data == "choose_from_list")
async def show_levels(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    pool = await get_pool()
    async with pool.acquire() as conn:
        stars = await conn.fetchval("SELECT total_stars FROM users WHERE user_id=$1", user_id)

    keyboard = []
    for level_key, name in CHALLENGE_LEVELS["ru"].items():
        required = LEVEL_UNLOCKS[level_key]
        if stars < required and level_key != "level_0":
            name = "🔒 " + name
        keyboard.append([InlineKeyboardButton(text=name, callback_data=level_key)])

    await callback.message.edit_text(
        "💪 Выбери уровень:",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard)
    )
    await callback.answer()



# ============================================================
#                     СПИСОК ЧЕЛЛЕНДЖЕЙ
# ============================================================

@router.callback_query(F.data.startswith("level_"))
async def show_challenges(callback: types.CallbackQuery):
    level_key = callback.data
    user_id = callback.from_user.id

    pool = await get_pool()
    async with pool.acquire() as conn:
        total_stars = await conn.fetchval("SELECT total_stars FROM users WHERE user_id=$1", user_id)

        if total_stars < LEVEL_UNLOCKS.get(level_key, 0):
            await callback.answer("Недостаточно ⭐ для доступа!", show_alert=True)
            return

        challenges = CHALLENGES[level_key]
        level_name = CHALLENGE_LEVELS["ru"][level_key]
        quote = LEVEL_QUOTES[level_key]

        active_rows = await conn.fetch("""
            SELECT challenge_id, difficulty FROM habits
            WHERE user_id=$1 AND is_challenge=TRUE
        """, user_id)

        completed_rows = await conn.fetch("""
            SELECT challenge_id, repeat_count FROM completed_challenges
            WHERE user_id=$1
        """, user_id)

    active_ids = {row["challenge_id"] for row in active_rows}
    diff_dict = {row["challenge_id"]: row["difficulty"] for row in active_rows}
    completed_dict = {row["challenge_id"]: row["repeat_count"] for row in completed_rows}

    keyboard = []
    for i, (cid, title, *_rest) in enumerate(challenges):
        if cid in active_ids:
            diff = diff_dict.get(cid, 1)
            prefix = f"🔥 ⭐{diff}"
        elif cid in completed_dict:
            stars = min(completed_dict[cid], 3)
            prefix = "⭐" * stars + "☆" * (3 - stars)
        else:
            prefix = ""

        keyboard.append([
            InlineKeyboardButton(
                text=f"{prefix} {title}".strip(),
                callback_data=f"challenge_{level_key}_{i}"
            )
        ])

    keyboard.append([InlineKeyboardButton(text="⬅ Назад", callback_data="choose_from_list")])

    await callback.message.edit_text(
        f"📋 Уровень *{level_name}*\n\n💬 {quote}\n\nВыбери челлендж:",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard)
    )
    await callback.answer()



# ============================================================
#                  ДЕТАЛИ ЧЕЛЛЕНДЖА
# ============================================================
@router.callback_query(F.data.startswith("challenge_"))
async def show_challenge_detail(callback: types.CallbackQuery):
    parts = callback.data.split("_")
    level_key = f"{parts[1]}_{parts[2]}"
    index = int(parts[3])
    cid, title, desc_dict, ctype = CHALLENGES[level_key][index]

    user_id = callback.from_user.id
    pool = await get_pool()

    async with pool.acquire() as conn:
        row = await conn.fetchrow("""
            SELECT repeat_count FROM completed_challenges
            WHERE user_id=$1 AND challenge_id=$2
        """, user_id, cid)

    repeat = row["repeat_count"] if row else 0
    difficulty = min(repeat + 1, 3)

    # Выбираем описание
    desc_to_show = desc_dict[difficulty]

    stars_display = "⭐" * repeat + "☆" * (3 - repeat)

    # Длительность
    days = 7 if repeat == 0 else 10 if repeat == 1 else 14

    text = (
        f"🏁 *{title}*\n\n"
        f"📖 {desc_to_show}\n\n"
        f"📅 Продолжительность: *{days} дней*\n"
        f"⭐ Прогресс: {stars_display}\n\n"
        f"Взять челлендж?"
    )

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Взять", callback_data=f"accept_{level_key}_{index}")],
        [InlineKeyboardButton(text="⬅ Назад", callback_data=level_key)],
    ])

    await callback.message.edit_text(text, parse_mode="Markdown", reply_markup=kb)
    await callback.answer()


# ============================================================
#                  ВЗЯТЬ ЧЕЛЛЕНДЖ
# ============================================================

@router.callback_query(F.data.startswith("accept_"))
async def accept_challenge(callback: types.CallbackQuery):
    parts = callback.data.split("_")
    level_key = f"{parts[1]}_{parts[2]}"
    index = int(parts[3])
    cid, title, desc_dict, ctype = CHALLENGES[level_key][index]

    user_id = callback.from_user.id
    pool = await get_pool()

    async with pool.acquire() as conn:

        active_exists = await conn.fetchval("""
            SELECT 1 FROM habits
            WHERE user_id=$1 AND is_challenge=TRUE AND challenge_id=$2
        """, user_id, cid)

        if active_exists:
            await callback.answer("Этот челлендж уже активен!", show_alert=True)
            return

        row = await conn.fetchrow("""
            SELECT repeat_count FROM completed_challenges
            WHERE user_id=$1 AND challenge_id=$2
        """, user_id, cid)

        repeat = row["repeat_count"] if row else 0
        difficulty = min(repeat + 1, 3)
        days = 7 if repeat == 0 else 10 if repeat == 1 else 14

        # Берём нужное описание
        desc_to_save = desc_dict[difficulty]

        await conn.execute("""
            INSERT INTO habits (user_id, name, description, days, confirm_type,
                                is_challenge, challenge_id, difficulty)
            VALUES ($1,$2,$3,$4,$5,TRUE,$6,$7)
        """, user_id, title, desc_to_save, days, ctype, cid, difficulty)

    await callback.message.edit_text(
        f"🔥 Ты начал челлендж: *{title}*\n"
        f"⭐ Сложность: {difficulty} из 3\n"
        f"📅 Длительность: {days} дней\n\n"
        f"Теперь он находится в Активных заданиях💪🔥",
        parse_mode="Markdown"
    )
    await callback.answer()


# ============================================================
#                ЗАВЕРШЕНИЕ ЧЕЛЛЕНДЖА
# ============================================================

@router.callback_query(F.data.startswith("complete_"))
async def complete_challenge(callback: types.CallbackQuery):
    parts = callback.data.split("_")
    level_key = f"{parts[1]}_{parts[2]}"
    index = int(parts[3])
    cid, title, *_ = CHALLENGES[level_key][index]

    user_id = callback.from_user.id
    pool = await get_pool()

    async with pool.acquire() as conn:
        row = await conn.fetchrow("""
            SELECT repeat_count
            FROM completed_challenges
            WHERE user_id=$1 AND challenge_id=$2
        """, user_id, cid)

        repeat = row["repeat_count"] if row else 0

        if repeat < 3:
            new_repeat = repeat + 1
            gained_star = 1
        else:
            new_repeat = repeat
            gained_star = 0

        if row:
            await conn.execute("""
                UPDATE completed_challenges
                SET repeat_count=$1, completed_at=NOW()
                WHERE user_id=$2 AND challenge_id=$3
            """, new_repeat, user_id, cid)
        else:
            await conn.execute("""
                INSERT INTO completed_challenges (user_id, challenge_name,
                    level_key, challenge_id, repeat_count)
                VALUES ($1,$2,$3,$4,$5)
            """, user_id, title, level_key, cid, new_repeat)

        if gained_star:
            await conn.execute("""
                UPDATE users SET total_stars = total_stars + 1
                WHERE user_id=$1
            """, user_id)

        await conn.execute("""
            DELETE FROM habits
            WHERE user_id=$1 AND challenge_id=$2
        """, user_id, cid)

    await callback.message.edit_text(
        f"🔥 Челлендж *{title}* завершён!\n"
        f"⭐ Получено: {gained_star} звёзд\n"
        f"Всего прогресс: {new_repeat}/3 ⭐",
        parse_mode="Markdown"
    )
    await callback.answer()
