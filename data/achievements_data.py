# ==========================================
# 🏆 ACHIEVEMENTS DATA
# Code-driven система достижений
# ==========================================


# -------------------------------
# 🔥 Discipline Achievements
# -------------------------------

DISCIPLINE_ACHIEVEMENTS = [

    {
        "code": "discipline_streak_3",
        "category": "discipline",
        "title": "3 дня дисциплины",
        "description": "Начало системы. Ты сделал первый шаг.",
        "icon": "🔥",
        "condition_type": "streak",
        "condition_value": 3,
        "xp_reward": 10,
        "usdt_reward": 0,
    },

    {
        "code": "discipline_streak_7",
        "category": "discipline",
        "title": "7 дней дисциплины",
        "description": "Настоящая стабильность. Ты уже отличаешься от большинства.",
        "icon": "🔥",
        "condition_type": "streak",
        "condition_value": 7,
        "xp_reward": 25,
        "usdt_reward": 0.5,
    },

]


# -------------------------------
# 📦 Универсальный список всех достижений
# -------------------------------
ALL_ACHIEVEMENTS = {
    "discipline": DISCIPLINE_ACHIEVEMENTS,
    # "body": BODY_ACHIEVEMENTS,
    # "mind": MIND_ACHIEVEMENTS,
    # "status": STATUS_ACHIEVEMENTS,
    # "money": MONEY_ACHIEVEMENTS,
}