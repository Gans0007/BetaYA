from aiogram import Router
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.exceptions import TelegramBadRequest


from services.habits.habit_service import save_habit
from repositories.habits.habit_repo import get_habits_by_user, habit_exists
from repositories.habits.habit_repo import count_user_habits

import logging
logger = logging.getLogger(__name__)

router = Router()

# Уровни челленджей
LEVELS = {
    "level_1": "🔰 Новичок",
    "level_2": "🚶 Основы контроля",
    "level_3": "🧠 Фокус и энергия",
    "level_4": "🔒 Самодисциплина",
    "level_5": "🧱 Преодоление",
    "level_6": "⏰ Ранний подъём",
}

# 2) Челленджи: (название, описание, длительность, тип подтверждения)
CHALLENGES = {
    "level_1": [
        ("Без телефона утром", "Не использовать телефон первые 30 минут", 7, "media"),
        ("Зарядка 5 минут", "Сделать лёгкую зарядку 5 минут утром", 14, "media"),
        ("Прогулка 10 минут", "Выйти на улицу минимум на 10 минут", 7, "media"),
        ("Сон до 23:00", "Лечь спать до 23:00", 21, "media"),
        ("Утренняя вода", "Пить стакан воды после пробуждения", 30, "media"),
    ],
    "level_2": [
        ("30 мин глубокого чтения", "Чтение без отвлечения", 14, "media"),
        ("5000 шагов", "Пройти минимум 5000 шагов за день", 30, "media"),
        ("Аффирмации", "Повторять свою формулу силы", 21, "media"),
        ("Визуализация цели", "5 минут представлять свой результат", 21, "media"),
        ("Дневник дисциплины", "Пиши итоги и ошибки дня", 30, "media"),
        ("Кружок каждый день", "Записывать голос/видео", 14, "media"),
        ("Планирование дня", "Записать 3 приоритетные задачи на день", 7, "media"),
        ("Тренировка 10 мин", "Минимальная физнагрузка каждый день", 14, "media"),
        ("Учёт расходов", "Записать все траты за день", 30, "media"),
        ("Чтение 10 минут", "Читать каждый день хотя бы 10 минут", 21, "media"),
    ],
    "level_3": [
        ("Без мата", "Следить за речью, исключить мат", 30, "media"),
        ("Без сахара", "Не употреблять сахар в течение дня", 21, "media"),
        ("Без фастфуда", "Ни одной вредной еды", 21, "media"),
        ("Комплимент незнакомцу", "Сделай искренний комплимент", 7, "media"),
        ("Медитация", "Медитировать минимум 5 минут в день", 14, "media"),
        ("Наблюдение за мыслями", "5 мин без реакции на мысли", 14, "media"),
        ("Пост в Telegram", "Писать короткий отчёт или мотивацию", 30, "media"),
        ("Учёба", "30 минут обучения или чтения курса", 21, "media"),
        ("Ходьба босиком", "15 минут босиком", 14, "media"),
        ("Холодный душ", "Принять холодный душ или обливание", 7, "media"),
        ("Час молчания", "Полное молчание в течение часа", 7, "media"),
    ],
    "level_4": [
        ("10 000 шагов", "Пройти 10 000 шагов за день", 30, "media"),
        ("10 подтягиваний", "Сделать 10 подтягиваний подряд", 14, "media"),
        ("50 отжиманий", "Сделать 50 отжиманий без остановки", 14, "media"),
        ("Бег 3 км", "Пробежать минимум 3 км", 21, "media"),
        ("Без зеркал", "Не смотреть в зеркало", 30, "media"),
        ("Отдых на коленях", "Отдыхать сидя на коленях", 14, "media"),
        ("Просить скидку", "Иди и попроси скидку", 7, "media"),
        ("Тишина", "Никакой музыки весь день", 7, "media"),
        ("Холодный душ", "Холодный душ и кружок-реакция", 14, "media"),
        ("Цифровой детокс", "Не заходить в соцсети в течение дня", 21, "media"),
    ],
    "level_5": [
        ("1 приём пищи в день", "Есть один раз в день", 7, "media"),
        ("2 тренировки в день", "Две тренировки ежедневно", 14, "media"),
        ("NoFap", "Полный контроль сексуальных импульсов", 30, "media"),
        ("Без порно", "Никакого порноконтента", 30, "media"),
        ("Планка", "Делай планку минимум 30 секунд", 14, "media"),
        ("Подъём в 4:30", "Просыпаться ровно в 4:30 утра", 21, "media"),
        ("Сенсорная изоляция", "Никаких звуков, видео, соцсетей", 7, "media"),
        ("Телефон в коробке", "Убирай телефон в ящик/коробку на 2+ часа в день", 14, "media"),
        ("Только лестница", "Не пользоваться лифтом — только лестница", 7, "media"),
        ("Фокус 2 часа", "2 часа работы без отвлечений", 21, "media"),
    ],
    "level_6": [
        ("Подъем в 7:00", "Подтверждение между 7:00 и 7:04, иначе сброс прогресса", 30, "wake_time"),
        ("Подъем в 6:30", "Подтверждение между 6:30 и 6:34, иначе сброс прогресса", 30, "wake_time"),
        ("Подъем в 6:00", "Подтверждение между 6:00 и 6:04, иначе сброс прогресса", 30, "wake_time"),
        ("Подъем в 5:30", "Подтверждение между 5:30 и 5:34, иначе сброс прогресса", 30, "wake_time"),
        ("Подъем в 5:00", "Подтверждение между 5:00 и 5:04, иначе сброс прогресса", 30, "wake_time"),
    ],
}

# --- Клавиатуры ---
def build_levels_keyboard():
    kb = InlineKeyboardMarkup(inline_keyboard=[], row_width=1)
    for key, label in LEVELS.items():
        btn = InlineKeyboardButton(text=label, callback_data=f"select_level:{key}")
        kb.inline_keyboard.append([btn])

    # ✅ Добавим кнопку назад в главное меню
    kb.inline_keyboard.append([
        InlineKeyboardButton(text="⬅️ Назад в меню привычек", callback_data="back_to_habit_menu")
    ])
    return kb


def build_challenges_keyboard(level_key: str):
    items = CHALLENGES.get(level_key, [])
    kb = InlineKeyboardMarkup(inline_keyboard=[], row_width=1)
    for idx, (title, desc, days, ctype) in enumerate(items):
        btn = InlineKeyboardButton(
            text=f"{title} ({days} дн.)",
            callback_data=f"select_challenge:{level_key}:{idx}"
        )
        kb.inline_keyboard.append([btn])
    kb.inline_keyboard.append([InlineKeyboardButton(text="⬅️ Назад", callback_data="take_challenge")])
    return kb

# --- Обработчики ---

@router.callback_query(lambda c: c.data == "take_challenge")
async def show_levels_menu(callback: CallbackQuery):
    user_id = callback.from_user.id
    logger.info(f"[{user_id}] Открывает меню уровней челленджей")

    try:
        if callback.message.text != "Выбирай Брат":
            await callback.message.edit_text("Выбирай Брат", reply_markup=build_levels_keyboard())
        else:
            await callback.message.edit_reply_markup(reply_markup=build_levels_keyboard())
        await callback.answer()

    except TelegramBadRequest as e:
        if "message is not modified" in str(e):
            await callback.answer()
            return
        logger.exception(f"[{user_id}] TelegramBadRequest при открытии меню уровней: {e}")
        await callback.answer("⚠️ Telegram выдал ошибку (BadRequest)", show_alert=True)

    except Exception as e:
        logger.exception(f"[{user_id}] Ошибка при открытии меню уровней: {e}")
        try:
            await callback.answer("Произошла ошибка при загрузке меню уровней", show_alert=True)
        except TelegramBadRequest:
            pass

@router.callback_query(lambda c: c.data.startswith("select_level:"))
async def show_challenges(callback: CallbackQuery):
    user_id = callback.from_user.id
    await callback.answer()

    try:
        _, level_key = callback.data.split(":", 1)
        logger.info(f"[{user_id}] Выбрал уровень: {level_key} ({LEVELS.get(level_key)})")

        await callback.message.edit_text(
            f"🏅 Челленджи уровня {LEVELS[level_key]}",
            reply_markup=build_challenges_keyboard(level_key)
        )
    except Exception as e:
        logger.exception(f"[{user_id}] Ошибка при отображении челленджей уровня {level_key}: {e}")
        try:
            await callback.message.answer("❌ Не удалось загрузить список челленджей.")
        except Exception:
            pass

@router.callback_query(lambda c: c.data.startswith("select_challenge:"))
async def confirm_challenge(callback: CallbackQuery):
    user_id = callback.from_user.id

    try:
        _, level_key, idx_str = callback.data.split(":", 2)
        idx = int(idx_str)
        title, desc, days, ctype = CHALLENGES[level_key][idx]

        logger.info(f"[{user_id}] Открыл описание челленджа: '{title}' (дни={days}, тип={ctype})")

        text = (
            f"🔥<b>Активный челлендж:</b>\n\n"
            f"<b>Название:</b> {title}\n"
            f"<b>Длительность:</b> {days} дней\n"
            f"<b>Описание:</b> {desc}\n\n"
            f"Добавить в активные привычки?"
        )

        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="✅ Взять челлендж", callback_data=f"add_challenge:{level_key}:{idx}")],
            [InlineKeyboardButton(text="⬅️ Назад", callback_data=f"select_level:{level_key}")]
        ])

        await callback.message.edit_text(text, parse_mode="HTML", reply_markup=kb)
        await callback.answer()

    except Exception as e:
        logger.exception(f"[{user_id}] Ошибка при отображении описания челленджа уровня {level_key}: {e}")
        await callback.answer("Не удалось отобразить детали челленджа", show_alert=True)

@router.callback_query(lambda c: c.data.startswith("add_challenge:"))
async def add_challenge(callback: CallbackQuery):
    user_id = callback.from_user.id
    await callback.answer()

    from repositories.habits.habit_repo import count_user_habits  # (если ещё не импортирован)
    total_habits = await count_user_habits(user_id)
    if total_habits >= 5:
        await callback.message.answer("❌ У тебя уже 5 активных привычек или челленджей. Удали одну, чтобы добавить новую.")
        return

    try:
        _, level_key, idx_str = callback.data.split(":", 2)
        idx = int(idx_str)
        title, desc, days, ctype = CHALLENGES[level_key][idx]

        if await habit_exists(user_id, title):
            logger.warning(f"[{user_id}] Попытка повторного добавления челленджа '{title}' — уже есть")
            await callback.message.answer("❌ Этот челлендж уже активен!")
            return

        logger.info(f"[{user_id}] Добавляет челлендж '{title}' (дни={days}, тип={ctype})")

        await save_habit(
            user_id=user_id,
            name=title,
            days=days,
            description=desc,
            is_challenge=True,
            confirm_type=ctype
        )

        habits = await get_habits_by_user(user_id)
        habit_id = habits[-1][0] if habits else None

        logger.info(f"[{user_id}] Челлендж '{title}' успешно добавлен, habit_id={habit_id}")
        await callback.message.edit_text("✅ Челлендж добавлен в активные привычки!")

    except Exception as e:
        logger.exception(f"[{user_id}] Ошибка при добавлении челленджа: {e}")
        try:
            await callback.message.answer("❌ Не удалось добавить челлендж")
        except Exception:
            pass


@router.callback_query(lambda c: c.data == "back_to_habit_menu")
async def back_to_habit_menu(callback: CallbackQuery):
    from repositories.habits.habit_repo import count_user_habits
    total = await count_user_habits(callback.from_user.id)

    text = (
        "📌 В привычке ты можешь сам добавить свою привычку.\n"
        "🔥 А в Challenge — выбрать одно из заданий от команды <b>Your Ambitions</b>.\n\n"
        f"{total}/5"
    )

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="➕ Добавить привычку", callback_data="add_habit_custom")],
        [InlineKeyboardButton(text="🔥 Взять Challenge", callback_data="take_challenge")]
    ])

    await callback.message.edit_text(text, reply_markup=keyboard, parse_mode="HTML")
    await callback.answer()
