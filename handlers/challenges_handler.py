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
    "level_0": "«Начинаем с малого...» 💫",
    "level_1": "«Движение — жизнь» 🏃‍♂️",
    "level_2": "«Внимание = энергия» ⚡️",
    "level_3": "«Самодисциплина = мост» 💪",
    "level_4": "«Преодоление формирует характер» 🧱",
    "level_5": "«Предприниматель видит возможности» 🚀",
}

# -------------------------------
# 🔹 Структура челленджей
# -------------------------------
# cid, title, desc, confirm_type
# -------------------------------
# 🔹 Список челленджей (id, title, desc, type)
#     id — уникальный тег для блокировки дублей
# -------------------------------
CHALLENGES = {
    "level_0": [
        ("0_reading", "Книга", "Читать 1 страницу каждый день на протяжении 7 дней. Не думай что это просто!", "media"),
        ("0_walking", "Поймать мысль", "Записывать 1 мысль в свой дневник каждый день. Для отслеживания своих мыслей.", "media"),
        ("0_warmup", "Зарядка", "Выделяй 1 минуту для зарядки в своем загруженом графике в течении 7 дней", "media"),
        ("0_pushups", "Отжимания", "Делай 1 отжимание ежедневно в течении 7 дней, и не забывай подтверждать фото или видео!", "media"),
        ("0_learnings", "Изучение", "Каждый день учить по 1 новому слову (на любом языке)", "media"),
        ("0_squats", "Благодарность", "Каждый день благодарить за что-то одно вселенную", "media"),
        ("0_plank", "Подкаст/Аудиокнига", "Прослушивать каждый день по 1 минуте подкаста или аудиокниги", "media"),
        ("0_jumps", "Уединение", "Сидеть в тишине 1 минуту каждый день", "media"),
        ("0_splits", "Шпагат", "Тянись 1 минту в шпагате каждый день. Гибкость для твоего тела очень важно!", "media"),
        ("0_lay_bad", "Кровать", "Первым делом я заправляю свою кровать после того как проснулся!", "media"),
        ("0_not_touch", "Телефон", "Не открывать соц. сети в течении 1минуты после пробуждения", "media"),
        ("0_money", ".Фин. Грамотность", "Каждый день откладывать по 1 монете/ 1 гривне /1 доллару", "media"),
    ],
    "level_1": [
        ("1_no_phone_morning", "Без телефона утром", "Начни или закончи день с лёгкой пробежки на свежем воздухе", "media"),
        ("1_warmup_5", "Зарядка 5 минут", "Сделать лёгкую зарядку 5 минут утром", "media"),
        ("1_walk_10", "Прогулка 10 минут", "Выйти на улицу минимум на 10 минут", "media"),
        ("1_sleep_23", "Сон до 23:00", "Лечь спать до 23:00", "media"),
        ("1_water_morning", "Утренняя вода", "Пить стакан воды после пробуждения", "media"),
    ],
    "level_2": [
        ("2_deep_reading_30", "30 мин глубокого чтения", "Чтение без отвлечения", "media"),
        ("2_steps_5000", "5000 шагов", "Пройти минимум 5000 шагов за день", "media"),
        ("2_affirmations", "Аффирмации", "Повторять свою формулу силы", "media"),
        ("2_visualization", "Визуализация цели", "5 минут представлять свой результат", "media"),
        ("2_discipline_journal", "Дневник дисциплины", "Пиши итоги и ошибки дня", "media"),
        ("2_daily_circle", "Кружок каждый день", "Записывать голос/видео", "media"),
        ("2_day_plan", "Планирование дня", "Записать 3 приоритетные задачи на день", "media"),
        ("2_training_10", "Тренировка 10 мин", "Минимальная физнагрузка каждый день", "media"),
        ("2_expense_log", "Учёт расходов", "Записать все траты за день", "media"),
        ("2_reading_10", "Чтение 10 минут", "Читать каждый день хотя бы 10 минут", "media"),
    ],
    "level_3": [
        ("3_no_swear", "Без мата", "Следить за речью, исключить мат", "media"),
        ("3_no_sugar", "Без сахара", "Не употреблять сахар в течение дня", "media"),
        ("3_no_fastfood", "Без фастфуда", "Ни одной вредной еды", "media"),
        ("3_compliment", "Комплимент незнакомцу", "Сделай искренний комплимент", "media"),
        ("3_meditation", "Медитация", "Медитировать минимум 5 минут в день", "media"),
        ("3_thought_watch", "Наблюдение за мыслями", "5 мин без реакции на мысли", "media"),
        ("3_tg_post", "Пост в Telegram", "Писать короткий отчёт или мотивацию", "media"),
        ("3_study", "Учёба", "30 минут обучения или чтения курса", "media"),
        ("3_barefoot", "Ходьба босиком", "15 минут босиком", "media"),
        ("3_cold_shower", "Холодный душ", "Принять холодный душ или обливание", "media"),
        ("3_silence_hour", "Час молчания", "Полное молчание в течение часа", "media"),
    ],
    "level_4": [
        ("4_steps_10000", "10 000 шагов", "Пройти 10 000 шагов за день", "media"),
        ("4_pullups_10", "10 подтягиваний", "Сделать 10 подтягиваний подряд", "media"),
        ("4_pushups_50", "50 отжиманий", "Сделать 50 отжиманий без остановки", "media"),
        ("4_run_3k", "Бег 3 км", "Пробежать минимум 3 км", "media"),
        ("4_no_mirrors", "Без зеркал", "Не смотреть в зеркало", "media"),
        ("4_kneel_rest", "Отдых на коленях", "Отдыхать сидя на коленях", "media"),
        ("4_ask_discount", "Просить скидку", "Иди и попроси скидку", "media"),
        ("4_silence", "Тишина", "Никакой музыки весь день", "media"),
        ("4_cold_shower_circle", "Холодный душ", "Холодный душ и кружок-реакция", "media"),
        ("4_digital_detox", "Цифровой детокс", "Не заходить в соцсети в течение дня", "media"),
    ],
    "level_5": [
        ("5_omad", "1 приём пищи в день", "Есть один раз в день", "media"),
        ("5_two_workouts", "2 тренировки в день", "Две тренировки ежедневно", "media"),
        ("5_nofap", "NoFap", "Полный контроль сексуальных импульсов", "media"),
        ("5_no_porn", "Без порно", "Никакого порноконтента", "media"),
        ("5_plank_30s", "Планка", "Делай планку минимум 30 секунд", "media"),
        ("5_wakeup_430", "Подъём в 4:30", "Просыпаться ровно в 4:30 утра", "media"),
        ("5_sensory_isolation", "Сенсорная изоляция", "Никаких звуков, видео, соцсетей", "media"),
        ("5_phone_box", "Телефон в коробке", "Убирай телефон в ящик/коробку на 2+ часа в день", "media"),
        ("5_stairs_only", "Только лестница", "Не пользоваться лифтом — только лестница", "media"),
        ("5_focus_2h", "Фокус 2 часа", "2 часа работы без отвлечений", "media"),
    ],
}


# -------------------------------
# 🔹 ВЫБОР УРОВНЯ
# -------------------------------
@router.callback_query(F.data == "choose_from_list")
async def show_levels(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    pool = await get_pool()
    async with pool.acquire() as conn:
        stars = await conn.fetchval("SELECT total_stars FROM users WHERE user_id = $1", user_id)

    levels = CHALLENGE_LEVELS["ru"]
    keyboard = []
    for level_key, name in levels.items():
        required = LEVEL_UNLOCKS[level_key]
        if stars < required and level_key != "level_0":
            name = "🔒 " + name
        keyboard.append([InlineKeyboardButton(text=name, callback_data=level_key)])

    await callback.message.edit_text(
        "💪 Выбери уровень челленджей:",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard)
    )
    await callback.answer()

# -------------------------------
# 🔹 СПИСОК ЧЕЛЛЕНДЖЕЙ
# -------------------------------
@router.callback_query(F.data.startswith("level_"))
async def show_challenges(callback: types.CallbackQuery):
    level_key = callback.data
    user_id = callback.from_user.id
    pool = await get_pool()

    async with pool.acquire() as conn:
        stars = await conn.fetchval("SELECT total_stars FROM users WHERE user_id=$1", user_id)

    if stars < LEVEL_UNLOCKS[level_key]:
        await callback.answer("Недостаточно ⭐ для этого уровня!", show_alert=True)
        return

    level_name = CHALLENGE_LEVELS["ru"][level_key]
    challenges = CHALLENGES[level_key]

    pool = await get_pool()
    async with pool.acquire() as conn:
        active = await conn.fetch("SELECT challenge_id FROM habits WHERE user_id=$1 AND is_challenge=TRUE", user_id)
        completed = await conn.fetch("SELECT challenge_id, repeat_count FROM completed_challenges WHERE user_id=$1", user_id)

    active_ids = {r["challenge_id"] for r in active}
    completed_map = {r["challenge_id"]: r["repeat_count"] for r in completed}

    kb = []
    for i, (cid, title, *_rest) in enumerate(challenges):
        prefix = ""
        if cid in active_ids:
            prefix = "🔥"
        elif cid in completed_map:
            stars = min(completed_map[cid], 3)
            prefix = "⭐" * stars + "☆" * (3 - stars)
        kb.append([InlineKeyboardButton(text=f"{prefix} {title}", callback_data=f"challenge_{level_key}_{i}")])

    kb.append([InlineKeyboardButton(text="⬅ Назад", callback_data="choose_from_list")])

    await callback.message.edit_text(
        f"📋 Уровень *{level_name}*\n\nВыбери челлендж:",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=kb)
    )
    await callback.answer()

# -------------------------------
# 🔹 ДЕТАЛИ ЧЕЛЛЕНДЖА
# -------------------------------
@router.callback_query(F.data.startswith("challenge_"))
async def show_challenge_detail(callback: types.CallbackQuery):
    parts = callback.data.split("_")
    level_key = f"{parts[1]}_{parts[2]}"
    index = int(parts[3])
    cid, title, desc, ctype = CHALLENGES[level_key][index]

    user_id = callback.from_user.id
    pool = await get_pool()

    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            "SELECT repeat_count FROM completed_challenges WHERE user_id=$1 AND challenge_id=$2",
            user_id, cid)

    repeat = row["repeat_count"] if row else 0
    stars_display = "⭐" * repeat + "☆" * (3 - repeat)

    # дни зависят от repeat_count (награды)
    if repeat == 0:
        days = 7
    elif repeat == 1:
        days = 10
    else:
        days = 14

    text = (
        f"🏁 *{title}*\n\n"
        f"📖 {desc}\n"
        f"📅 Продолжительность: *{days} дней*\n"
        f"⭐ Прогресс: {stars_display}\n\n"
        f"Взять челлендж?"
    )

    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="✅ Взять", callback_data=f"accept_{level_key}_{index}")],
            [InlineKeyboardButton(text="⬅ Назад", callback_data=level_key)],
        ]
    )

    await callback.message.edit_text(text, parse_mode="Markdown", reply_markup=kb)
    await callback.answer()

# -------------------------------
# 🔹 ВЗЯТЬ ЧЕЛЛЕНДЖ (difficulty + days)
# -------------------------------
@router.callback_query(F.data.startswith("accept_"))
async def accept_challenge(callback: types.CallbackQuery):
    parts = callback.data.split("_")
    level_key = f"{parts[1]}_{parts[2]}"
    index = int(parts[3])
    cid, title, desc, ctype = CHALLENGES[level_key][index]

    user_id = callback.from_user.id
    pool = await get_pool()

    async with pool.acquire() as conn:
        row = await conn.fetchrow("""
            SELECT repeat_count
            FROM completed_challenges 
            WHERE user_id=$1 AND challenge_id=$2
        """, user_id, cid)

        repeat = row["repeat_count"] if row else 0

        # сложность теперь НЕ зависит от repeat_count
        # сложность = награда + 1 (но максимум 3)
        if repeat == 0:
            difficulty = 1
        elif repeat == 1:
            difficulty = 2
        else:
            difficulty = 3

        # дни оставляем по наградам
        days = 7 if repeat == 0 else 10 if repeat == 1 else 14

        active = await conn.fetchval("""
            SELECT 1 FROM habits 
            WHERE user_id=$1 AND is_challenge=TRUE AND challenge_id=$2
        """, user_id, cid)

        if active:
            await callback.answer("Этот челлендж уже активен!", show_alert=True)
            return

        await conn.execute("""
            INSERT INTO habits (user_id, name, description, days, confirm_type, is_challenge, challenge_id, difficulty)
            VALUES ($1,$2,$3,$4,$5,TRUE,$6,$7)
        """, user_id, title, desc, days, ctype, cid, difficulty)

    await callback.message.edit_text(
        f"🔥 Ты начал челлендж: *{title}*!\n\nОн добавлен в твои активные задания 💪",
        parse_mode="Markdown"
    )
    await callback.answer()


# -------------------------------
# 🔹 ЗАВЕРШЕНИЕ ЧЕЛЛЕНДЖА (только звёзды)
# -------------------------------
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
                INSERT INTO completed_challenges (user_id, challenge_name, level_key, challenge_id, repeat_count)
                VALUES ($1,$2,$3,$4,$5)
            """, user_id, title, level_key, cid, new_repeat)

        if gained_star:
            await conn.execute("UPDATE users SET total_stars = total_stars + 1 WHERE user_id=$1", user_id)

        await conn.execute("DELETE FROM habits WHERE user_id=$1 AND challenge_id=$2", user_id, cid)

    text = (
        f"🔥 Челлендж *{title}* завершён!\n"
        f"⭐ Получено: {gained_star} звезда(ы)\n"
        f"Всего: {new_repeat}/3"
    )

    await callback.message.edit_text(text, parse_mode="Markdown")
    await callback.answer()
