# achievements/definitions.py

ACHIEVEMENTS = {

# ==================================================
# 🔥 ДИСЦИПЛИНА (10) — XP ONLY
# ==================================================

"discipline_first_confirm": {
    "category": "discipline",
    "event": "habit_confirmed",
    "metric": "total_confirmed",
    "operator": "gte",
    "target": 1,
    "xp": 3,
    "money": 0,
    "secret": False,
},

"discipline_10_confirms": {
    "category": "discipline",
    "event": "habit_confirmed",
    "metric": "total_confirmed",
    "operator": "gte",
    "target": 10,
    "xp": 4,
    "money": 0,
    "secret": False,
},

"discipline_30_confirms": {
    "category": "discipline",
    "event": "habit_confirmed",
    "metric": "total_confirmed",
    "operator": "gte",
    "target": 30,
    "xp": 6,
    "money": 0,
    "secret": False,
},

"discipline_100_confirms": {
    "category": "discipline",
    "event": "habit_confirmed",
    "metric": "total_confirmed",
    "operator": "gte",
    "target": 100,
    "xp": 8,
    "money": 0,
    "secret": False,
},

"discipline_300_confirms": {
    "category": "discipline",
    "event": "habit_confirmed",
    "metric": "total_confirmed",
    "operator": "gte",
    "target": 300,
    "xp": 12,
    "money": 0,
    "secret": False,
},

"discipline_streak_7": {
    "category": "discipline",
    "event": "streak_updated",
    "metric": "streak",
    "operator": "gte",
    "target": 7,
    "xp": 5,
    "money": 0,
    "secret": False,
},

"discipline_streak_14": {
    "category": "discipline",
    "event": "streak_updated",
    "metric": "streak",
    "operator": "gte",
    "target": 14,
    "xp": 6,
    "money": 0,
    "secret": False,
},

"discipline_streak_30": {
    "category": "discipline",
    "event": "streak_updated",
    "metric": "streak",
    "operator": "gte",
    "target": 30,
    "xp": 8,
    "money": 0,
    "secret": False,
},

"discipline_streak_60": {
    "category": "discipline",
    "event": "streak_updated",
    "metric": "streak",
    "operator": "gte",
    "target": 60,
    "xp": 10,
    "money": 0,
    "secret": False,
},

"discipline_streak_365": {
    "category": "discipline",
    "event": "streak_updated",
    "metric": "streak",
    "operator": "gte",
    "target": 365,
    "xp": 15,
    "money": 0,
    "secret": True,
},

# ==================================================
# 🥊 ТЕЛО (10) — XP ONLY
# ==================================================

"body_first": {
    "category": "body",
    "event": "body_challenge_completed",
    "metric": "body_total",
    "operator": "gte",
    "target": 1,
    "xp": 3,
    "money": 0,
    "secret": False,
},

"body_5": {
    "category": "body",
    "event": "body_challenge_completed",
    "metric": "body_total",
    "operator": "gte",
    "target": 5,
    "xp": 4,
    "money": 0,
    "secret": False,
},

"body_10": {
    "category": "body",
    "event": "body_challenge_completed",
    "metric": "body_total",
    "operator": "gte",
    "target": 10,
    "xp": 6,
    "money": 0,
    "secret": False,
},

"body_25": {
    "category": "body",
    "event": "body_challenge_completed",
    "metric": "body_total",
    "operator": "gte",
    "target": 25,
    "xp": 8,
    "money": 0,
    "secret": False,
},

"body_50": {
    "category": "body",
    "event": "body_challenge_completed",
    "metric": "body_total",
    "operator": "gte",
    "target": 50,
    "xp": 10,
    "money": 0,
    "secret": False,
},

"body_streak_7": {
    "category": "body",
    "event": "body_streak_updated",
    "metric": "body_streak",
    "operator": "gte",
    "target": 7,
    "xp": 6,
    "money": 0,
    "secret": False,
},

"body_streak_14": {
    "category": "body",
    "event": "body_streak_updated",
    "metric": "body_streak",
    "operator": "gte",
    "target": 14,
    "xp": 8,
    "money": 0,
    "secret": False,
},

"body_streak_30": {
    "category": "body",
    "event": "body_streak_updated",
    "metric": "body_streak",
    "operator": "gte",
    "target": 30,
    "xp": 12,
    "money": 0,
    "secret": False,
},

"body_100": {
    "category": "body",
    "event": "body_challenge_completed",
    "metric": "body_total",
    "operator": "gte",
    "target": 100,
    "xp": 14,
    "money": 0,
    "secret": False,
},

"body_200_secret": {
    "category": "body",
    "event": "body_challenge_completed",
    "metric": "body_total",
    "operator": "gte",
    "target": 200,
    "xp": 15,
    "money": 0,
    "secret": True,
},

# ==================================================
# 🧠 УМ (10) — XP ONLY
# ==================================================

"mind_first": {
    "category": "mind",
    "event": "mind_challenge_completed",
    "metric": "mind_total",
    "operator": "gte",
    "target": 1,
    "xp": 3,
    "money": 0,
    "secret": False,
},

"mind_5": {
    "category": "mind",
    "event": "mind_challenge_completed",
    "metric": "mind_total",
    "operator": "gte",
    "target": 5,
    "xp": 4,
    "money": 0,
    "secret": False,
},

"mind_10": {
    "category": "mind",
    "event": "mind_challenge_completed",
    "metric": "mind_total",
    "operator": "gte",
    "target": 10,
    "xp": 6,
    "money": 0,
    "secret": False,
},

"mind_25": {
    "category": "mind",
    "event": "mind_challenge_completed",
    "metric": "mind_total",
    "operator": "gte",
    "target": 25,
    "xp": 8,
    "money": 0,
    "secret": False,
},

"mind_50": {
    "category": "mind",
    "event": "mind_challenge_completed",
    "metric": "mind_total",
    "operator": "gte",
    "target": 50,
    "xp": 10,
    "money": 0,
    "secret": False,
},

"mind_streak_7": {
    "category": "mind",
    "event": "mind_streak_updated",
    "metric": "mind_streak",
    "operator": "gte",
    "target": 7,
    "xp": 6,
    "money": 0,
    "secret": False,
},

"mind_streak_14": {
    "category": "mind",
    "event": "mind_streak_updated",
    "metric": "mind_streak",
    "operator": "gte",
    "target": 14,
    "xp": 8,
    "money": 0,
    "secret": False,
},

"mind_streak_30": {
    "category": "mind",
    "event": "mind_streak_updated",
    "metric": "mind_streak",
    "operator": "gte",
    "target": 30,
    "xp": 12,
    "money": 0,
    "secret": False,
},

"mind_100": {
    "category": "mind",
    "event": "mind_challenge_completed",
    "metric": "mind_total",
    "operator": "gte",
    "target": 100,
    "xp": 14,
    "money": 0,
    "secret": False,
},

"mind_master": {
    "category": "mind",
    "event": "mind_challenge_completed",
    "metric": "mind_total",
    "operator": "gte",
    "target": 200,
    "xp": 15,
    "money": 0,
    "secret": True,
},

# ==================================================
# 👑 СТАТУС (10) — XP + $
# ==================================================

"status_top_100": {
    "category": "status",
    "event": "rank_updated",
    "metric": "rank",
    "operator": "lte",
    "target": 100,
    "xp": 6,
    "money": 0,
    "secret": False,
},

"status_top_50": {
    "category": "status",
    "event": "rank_updated",
    "metric": "rank",
    "operator": "lte",
    "target": 50,
    "xp": 7,
    "money": 0,
    "secret": False,
},

"status_top_25": {
    "category": "status",
    "event": "rank_updated",
    "metric": "rank",
    "operator": "lte",
    "target": 25,
    "xp": 8,
    "money": 0,
    "secret": False,
},

"status_top_10": {
    "category": "status",
    "event": "rank_updated",
    "metric": "rank",
    "operator": "lte",
    "target": 10,
    "xp": 10,
    "money": 2,
    "secret": False,
},

"status_top_5": {
    "category": "status",
    "event": "rank_updated",
    "metric": "rank",
    "operator": "lte",
    "target": 5,
    "xp": 12,
    "money": 4,
    "secret": False,
},

"status_top_3": {
    "category": "status",
    "event": "rank_updated",
    "metric": "rank",
    "operator": "lte",
    "target": 3,
    "xp": 13,
    "money": 6,
    "secret": False,
},

"status_top_1": {
    "category": "status",
    "event": "rank_updated",
    "metric": "rank",
    "operator": "eq",
    "target": 1,
    "xp": 15,
    "money": 10,
    "secret": False,
},

"status_top_7_days": {
    "category": "status",
    "event": "rank_streak_updated",
    "metric": "top_streak",
    "operator": "gte",
    "target": 7,
    "xp": 10,
    "money": 0,
    "secret": False,
},

"status_top_30_days": {
    "category": "status",
    "event": "rank_streak_updated",
    "metric": "top_streak",
    "operator": "gte",
    "target": 30,
    "xp": 15,
    "money": 5,
    "secret": False,
},

"status_legend": {
    "category": "status",
    "event": "rank_streak_updated",
    "metric": "top1_streak",
    "operator": "gte",
    "target": 30,
    "xp": 15,
    "money": 10,
    "secret": True,
},

# ==================================================
# 💰 ДЕНЬГИ (10) — XP + $
# ==================================================

"money_first_ref": {
    "category": "money",
    "event": "referral_added",
    "metric": "referrals_total",
    "operator": "gte",
    "target": 1,
    "xp": 6,
    "money": 0,
    "secret": False,
},

"money_active_1": {
    "category": "money",
    "event": "referral_active",
    "metric": "active_referrals",
    "operator": "gte",
    "target": 1,
    "xp": 7,
    "money": 0,
    "secret": False,
},

"money_active_3": {
    "category": "money",
    "event": "referral_active",
    "metric": "active_referrals",
    "operator": "gte",
    "target": 3,
    "xp": 8,
    "money": 0,
    "secret": False,
},

"money_active_5": {
    "category": "money",
    "event": "referral_active",
    "metric": "active_referrals",
    "operator": "gte",
    "target": 5,
    "xp": 10,
    "money": 0,
    "secret": False,
},

"money_first_income": {
    "category": "money",
    "event": "affiliate_payment",
    "metric": "total_earnings",
    "operator": "gte",
    "target": 1,
    "xp": 8,
    "money": 2,
    "secret": False,
},

"money_10": {
    "category": "money",
    "event": "affiliate_payment",
    "metric": "total_earnings",
    "operator": "gte",
    "target": 10,
    "xp": 10,
    "money": 3,
    "secret": False,
},

"money_50": {
    "category": "money",
    "event": "affiliate_payment",
    "metric": "total_earnings",
    "operator": "gte",
    "target": 50,
    "xp": 12,
    "money": 5,
    "secret": False,
},

"money_100": {
    "category": "money",
    "event": "affiliate_payment",
    "metric": "total_earnings",
    "operator": "gte",
    "target": 100,
    "xp": 13,
    "money": 7,
    "secret": False,
},

"money_250": {
    "category": "money",
    "event": "affiliate_payment",
    "metric": "total_earnings",
    "operator": "gte",
    "target": 250,
    "xp": 15,
    "money": 10,
    "secret": False,
},

"money_system": {
    "category": "money",
    "event": "affiliate_payment",
    "metric": "total_earnings",
    "operator": "gte",
    "target": 500,
    "xp": 15,
    "money": 10,
    "secret": True,
},

}
