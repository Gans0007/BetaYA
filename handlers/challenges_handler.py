from aiogram import Router, types, F
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from database import get_pool

router = Router()


# -------------------------------
# 🌟 Требования по звёздам для разблокировки уровней
# -------------------------------
LEVEL_UNLOCKS = {
    "level_0": 0,   # Новичок — всегда доступен
    "level_1": 4,   # Активность — 3 звезды
    "level_2": 8,   # Фокус и энергия — 6 звёзд
    "level_3": 13,  # Самодисциплина — 13 звёзд
    "level_4": 20,  # Преодоление — 21 звезда
    "level_5": 22   # Предприниматели — 30 звёзд
}



# -------------------------------
# 🔹 Уровни челленджей
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
# 🔹 Цитаты для каждого уровня
# -------------------------------
LEVEL_QUOTES = {
    "level_0": "«Начинаем с самого малого. Любое действие по 1 минуте вдень что бы не перегружать себя! Смысл выработать привычку.\n Выбери из списка ниже, или создай свою привычку в 'добавить привычку':» 💫",
    "level_1": "«Движение — это жизнь. Даже маленькие шаги ведут к большим переменам.» 🏃‍♂️",
    "level_2": "«Энергия течёт туда, куда направлено внимание.» ⚡️",
    "level_3": "«Самодисциплина — мост между целями и достижениями.» 💪",
    "level_4": "«Преодоление трудностей формирует твой характер.» 🧱",
    "level_5": "«Предприниматель — это тот, кто видит возможности там, где другие видят проблемы.» 🚀",
}

# -------------------------------
# 🔹 Список челленджей (id, title, desc, days, type)
#     id — уникальный тег для блокировки дублей
# -------------------------------
CHALLENGES = {
    "level_0": [
        ("0_reading", "Книга", "Читать 1 страницу каждый день на протяжении 7 дней. Не думай что это просто!", 7, "media"),
        ("0_walking", "Поймать мысль", "Записывать 1 мысль в свой дневник каждый день. Для отслеживания своих мыслей.", 7, "media"),
        ("0_warmup", "Зарядка", "Выделяй 1 минуту для зарядки в своем загруженом графике в течении 7 дней", 7, "media"),
        ("0_pushups", "Отжимания", "Делай 1 отжимание ежедневно в течении 7 дней, и не забывай подтверждать фото или видео!", 7, "media"),
        ("0_learnings", "Изучение", "Каждый день учить по 1 новому слову (на любом языке)", 7, "media"),
        ("0_squats", "Благодарность", "Каждый день благодарить за что-то одно вселенную", 7, "media"),
        ("0_plank", "Подкаст/Аудиокнига", "Прослушивать каждый день по 1 минуте подкаста или аудиокниги", 7, "media"),
        ("0_jumps", "Уединение", "Сидеть в тишине 1 минуту каждый день", 7, "media"),
        ("0_splits", "Шпагат", "Тянись 1 минту в шпагате каждый день. Гибкость для твоего тела очень важно!", 7, "media"),
        ("0_lay_bad", "Кровать", "Первым делом я заправляю свою кровать после того как проснулся!", 7, "media"),
        ("0_not_touch", "Телефон", "Не открывать соц. сети в течении 1минуты после пробуждения", 7, "media"),
        ("0_money", ".Фин. Грамотность", "Каждый день откладывать по 1 монете/ 1 гривне /1 доллару", 7, "media"),
    ],
    "level_1": [
        ("1_no_phone_morning", "Без телефона утром", "Начни или закончи день с лёгкой пробежки на свежем воздухе", 7, "media"),
        ("1_warmup_5", "Зарядка 5 минут", "Сделать лёгкую зарядку 5 минут утром", 14, "media"),
        ("1_walk_10", "Прогулка 10 минут", "Выйти на улицу минимум на 10 минут", 7, "media"),
        ("1_sleep_23", "Сон до 23:00", "Лечь спать до 23:00", 21, "media"),
        ("1_water_morning", "Утренняя вода", "Пить стакан воды после пробуждения", 30, "media"),
    ],
    "level_2": [
        ("2_deep_reading_30", "30 мин глубокого чтения", "Чтение без отвлечения", 14, "media"),
        ("2_steps_5000", "5000 шагов", "Пройти минимум 5000 шагов за день", 30, "media"),
        ("2_affirmations", "Аффирмации", "Повторять свою формулу силы", 21, "media"),
        ("2_visualization", "Визуализация цели", "5 минут представлять свой результат", 21, "media"),
        ("2_discipline_journal", "Дневник дисциплины", "Пиши итоги и ошибки дня", 30, "media"),
        ("2_daily_circle", "Кружок каждый день", "Записывать голос/видео", 14, "media"),
        ("2_day_plan", "Планирование дня", "Записать 3 приоритетные задачи на день", 7, "media"),
        ("2_training_10", "Тренировка 10 мин", "Минимальная физнагрузка каждый день", 14, "media"),
        ("2_expense_log", "Учёт расходов", "Записать все траты за день", 30, "media"),
        ("2_reading_10", "Чтение 10 минут", "Читать каждый день хотя бы 10 минут", 21, "media"),
    ],
    "level_3": [
        ("3_no_swear", "Без мата", "Следить за речью, исключить мат", 30, "media"),
        ("3_no_sugar", "Без сахара", "Не употреблять сахар в течение дня", 21, "media"),
        ("3_no_fastfood", "Без фастфуда", "Ни одной вредной еды", 21, "media"),
        ("3_compliment", "Комплимент незнакомцу", "Сделай искренний комплимент", 7, "media"),
        ("3_meditation", "Медитация", "Медитировать минимум 5 минут в день", 14, "media"),
        ("3_thought_watch", "Наблюдение за мыслями", "5 мин без реакции на мысли", 14, "media"),
        ("3_tg_post", "Пост в Telegram", "Писать короткий отчёт или мотивацию", 30, "media"),
        ("3_study", "Учёба", "30 минут обучения или чтения курса", 21, "media"),
        ("3_barefoot", "Ходьба босиком", "15 минут босиком", 14, "media"),
        ("3_cold_shower", "Холодный душ", "Принять холодный душ или обливание", 7, "media"),
        ("3_silence_hour", "Час молчания", "Полное молчание в течение часа", 7, "media"),
    ],
    "level_4": [
        ("4_steps_10000", "10 000 шагов", "Пройти 10 000 шагов за день", 30, "media"),
        ("4_pullups_10", "10 подтягиваний", "Сделать 10 подтягиваний подряд", 14, "media"),
        ("4_pushups_50", "50 отжиманий", "Сделать 50 отжиманий без остановки", 14, "media"),
        ("4_run_3k", "Бег 3 км", "Пробежать минимум 3 км", 21, "media"),
        ("4_no_mirrors", "Без зеркал", "Не смотреть в зеркало", 30, "media"),
        ("4_kneel_rest", "Отдых на коленях", "Отдыхать сидя на коленях", 14, "media"),
        ("4_ask_discount", "Просить скидку", "Иди и попроси скидку", 7, "media"),
        ("4_silence", "Тишина", "Никакой музыки весь день", 7, "media"),
        ("4_cold_shower_circle", "Холодный душ", "Холодный душ и кружок-реакция", 14, "media"),
        ("4_digital_detox", "Цифровой детокс", "Не заходить в соцсети в течение дня", 21, "media"),
    ],
    "level_5": [
        ("5_omad", "1 приём пищи в день", "Есть один раз в день", 7, "media"),
        ("5_two_workouts", "2 тренировки в день", "Две тренировки ежедневно", 14, "media"),
        ("5_nofap", "NoFap", "Полный контроль сексуальных импульсов", 30, "media"),
        ("5_no_porn", "Без порно", "Никакого порноконтента", 30, "media"),
        ("5_plank_30s", "Планка", "Делай планку минимум 30 секунд", 14, "media"),
        ("5_wakeup_430", "Подъём в 4:30", "Просыпаться ровно в 4:30 утра", 21, "media"),
        ("5_sensory_isolation", "Сенсорная изоляция", "Никаких звуков, видео, соцсетей", 7, "media"),
        ("5_phone_box", "Телефон в коробке", "Убирай телефон в ящик/коробку на 2+ часа в день", 14, "media"),
        ("5_stairs_only", "Только лестница", "Не пользоваться лифтом — только лестница", 7, "media"),
        ("5_focus_2h", "Фокус 2 часа", "2 часа работы без отвлечений", 21, "media"),
    ],
}

# -------------------------------
# 🔹 Выбор уровня
# -------------------------------
@router.callback_query(F.data == "choose_from_list")
async def show_levels(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    pool = await get_pool()

    async with pool.acquire() as conn:
        stars = await conn.fetchval("""
            SELECT total_stars FROM users WHERE user_id = $1
        """, user_id)

    lang = "ru"
    levels = CHALLENGE_LEVELS[lang]

    keyboard = []
    for level_key, level_name in levels.items():
        required = LEVEL_UNLOCKS.get(level_key, 0)

        # Если звёзд меньше — добавляем замочек ПЕРЕД текстом
        if stars < required and level_key != "level_0":
            level_name = f"🔒 {level_name}"
        else:
            level_name = f"{level_name}"

        keyboard.append([
            InlineKeyboardButton(text=level_name, callback_data=level_key)
        ])

    await callback.message.edit_text(
        "💪 Выбери уровень челленджей:",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard)
    )
    await callback.answer()


# -------------------------------
# 🔹 Список челленджей с отображением ⭐
# -------------------------------
@router.callback_query(F.data.startswith("level_"))
async def show_challenges(callback: types.CallbackQuery):
    level_key = callback.data
    user_id = callback.from_user.id

    pool = await get_pool()
    async with pool.acquire() as conn:

        total_stars = await conn.fetchval("""
            SELECT total_stars FROM users WHERE user_id = $1
        """, user_id)

        required_stars = LEVEL_UNLOCKS.get(level_key, 0)

        if total_stars < required_stars:
            await callback.message.answer(
                f"🔒 Раздел пока недоступен!\n"
                f"🌟 Нужно: *{required_stars}* звёзд\n"
                f"⭐ У тебя: *{total_stars}*",
                parse_mode="Markdown"
            )
            await callback.answer()
            return

        level_name = CHALLENGE_LEVELS["ru"][level_key]
        challenges = CHALLENGES[level_key]
        quote = LEVEL_QUOTES[level_key]

        active_rows = await conn.fetch("""
            SELECT challenge_id, difficulty FROM habits
            WHERE user_id = $1 AND is_challenge = TRUE
        """, user_id)

        completed_rows = await conn.fetch("""
            SELECT challenge_id, repeat_count FROM completed_challenges
            WHERE user_id = $1
        """, user_id)

    # ВНИМАНИЕ: дальше conn НЕ используется ❗

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
        reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard),
        parse_mode="Markdown"
    )
    await callback.answer()



# -------------------------------
# 🔹 Детали челленджа
# -------------------------------
@router.callback_query(F.data.startswith("challenge_"))
async def show_challenge_detail(callback: types.CallbackQuery):
    parts = callback.data.split("_")
    level_key = f"{parts[1]}_{parts[2]}"
    index = int(parts[3])
    challenge = CHALLENGES.get(level_key, [])[index]
    cid, title, desc, days, ctype = challenge

    pool = await get_pool()
    async with pool.acquire() as conn:
        # Проверяем, сколько раз челлендж уже завершён
        row = await conn.fetchrow("""
            SELECT repeat_count FROM completed_challenges
            WHERE user_id = $1 AND challenge_id = $2
        """, callback.from_user.id, cid)

    stars = 0
    if row and row["repeat_count"]:
        stars = min(row["repeat_count"], 3)  # максимум 3 звезды

    stars_display = "⭐" * stars + "☆" * (3 - stars)

    text = (
        f"🏁 *{title}*\n\n"
        f"📖 {desc}\n\n"
        f"📅 Продолжительность: *{days} дней*\n"
        f"🎯 Тип подтверждения: {ctype}\n\n"
        f"⭐ Прогресс: {stars_display}\n\n"
        f"Хочешь взять этот челлендж?"
    )

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="✅ Взять челлендж", callback_data=f"accept_{level_key}_{index}")],
            [InlineKeyboardButton(text="⬅ Назад", callback_data=level_key)],
        ]
    )

    await callback.message.edit_text(text, parse_mode="Markdown", reply_markup=keyboard)
    await callback.answer()


# -------------------------------
# 🔹 Взять челлендж
# -------------------------------
@router.callback_query(F.data.startswith("accept_"))
async def accept_challenge(callback: types.CallbackQuery):
    parts = callback.data.split("_")
    level_key = f"{parts[1]}_{parts[2]}"
    index = int(parts[3])
    cid, title, desc, days, ctype = CHALLENGES.get(level_key, [])[index]

    pool = await get_pool()
    user_id = callback.from_user.id

    async with pool.acquire() as conn:
        # Проверяем, активен ли сейчас
        active_exists = await conn.fetchval("""
            SELECT 1 FROM habits
            WHERE user_id = $1 AND is_challenge = TRUE AND challenge_id = $2
        """, user_id, cid)

        if active_exists:
            await callback.answer("Этот челлендж уже активен! 🚫", show_alert=True)
            return

        # Проверяем, сколько раз завершён до этого
        row = await conn.fetchrow("""
            SELECT repeat_count FROM completed_challenges
            WHERE user_id = $1 AND challenge_id = $2
        """, user_id, cid)

        repeat_count = row["repeat_count"] if row else 0
        difficulty = min(repeat_count + 1, 3)

        # Добавляем новый челлендж с учётом сложности
        await conn.execute("""
            INSERT INTO habits (user_id, name, description, days, confirm_type, is_challenge, challenge_id, difficulty)
            VALUES ($1, $2, $3, $4, $5, TRUE, $6, $7)
        """, user_id, title, desc, days, ctype, cid, difficulty)

    await callback.message.edit_text(
        f"🔥 Ты начал челлендж: *{title}*!\n"
        f"⭐ Текущая сложность: {difficulty} из 3\n\n"
        f"Он добавлен в твои активные задания 💪",
        parse_mode="Markdown"
    )
    await callback.answer()


# -------------------------------
# 🔹 Завершить челлендж (⭐ до 5)
# -------------------------------
@router.callback_query(F.data.startswith("complete_"))
async def complete_challenge(callback: types.CallbackQuery):
    parts = callback.data.split("_")
    level_key = f"{parts[1]}_{parts[2]}"
    index = int(parts[3])
    cid, title, *_ = CHALLENGES.get(level_key, [])[index]

    pool = await get_pool()
    async with pool.acquire() as conn:
        existing = await conn.fetchrow("""
            SELECT repeat_count FROM completed_challenges
            WHERE user_id = $1 AND challenge_id = $2
        """, callback.from_user.id, cid)

        if existing:
            new_count = min(existing["repeat_count"] + 1, 3)
            await conn.execute("""
                UPDATE completed_challenges
                SET repeat_count = $1, completed_at = NOW()
                WHERE user_id = $2 AND challenge_id = $3
            """, new_count, callback.from_user.id, cid)
        else:
            await conn.execute("""
                INSERT INTO completed_challenges (user_id, challenge_name, level_key, challenge_id, repeat_count)
                VALUES ($1, $2, $3, $4, 1)
            """, callback.from_user.id, title, level_key, cid)

        await conn.execute("""
            DELETE FROM habits
            WHERE user_id = $1 AND challenge_id = $2 AND is_challenge = TRUE
        """, callback.from_user.id, cid)

    await callback.message.edit_text(
        f"✅ Челлендж *{title}* завершён!\n"
        f"⭐ Ты заработал новую звезду!\n"
        f"Максимум можно получить 3 ⭐ за этот челлендж 💪",
        parse_mode="Markdown"
    )
    await callback.answer()
