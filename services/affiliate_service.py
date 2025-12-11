from repositories import affiliate_repository as repo


class AffiliateService:

    # -----------------------------------------
    # 📌 Назначить реферального партнёра
    # -----------------------------------------
    async def assign_referral(self, user_id: int, referral_code: str) -> bool:
        """
        Возвращает:
        True — реферал успешно присвоен
        False — код не найден, или уже есть реферал, или код свой
        """

        affiliate_id = await repo.get_affiliate_by_code(referral_code)
        if not affiliate_id:
            return False

        if affiliate_id == user_id:
            return False

        if await repo.user_already_has_affiliate(user_id):
            return False

        await repo.create_referral(affiliate_id, user_id)
        return True

    # -----------------------------------------
    # 🟢 Сделать реферала активным
    # -----------------------------------------
    async def activate_referral(self, user_id: int, bonus_amount: float = 0):
        affiliate_id = await repo.get_affiliate_for_user(user_id)
        if not affiliate_id:
            return False

        await repo.mark_referral_active(user_id)

        if bonus_amount > 0:
            await repo.add_payment_to_affiliate(affiliate_id, bonus_amount)

        return True

    # -----------------------------------------
    # 🔴 Сделать реферала неактивным
    # -----------------------------------------
    async def deactivate_referral(self, user_id: int):
        await repo.mark_referral_inactive(user_id)
        return True

    # -----------------------------------------
    # 📊 Получить отображаемую инфу для меню
    # -----------------------------------------
    async def get_affiliate_dashboard(self, user_id: int):

        # 1️⃣ Получаем текущий реферальный код
        code = await repo.get_referral_code(user_id)

        # 2️⃣ Если нет — создаём на основе user_id
        if not code:
            new_code = await repo.generate_referral_code(user_id)
            await repo.assign_referral_code(user_id, new_code)
            code = new_code

        # 3️⃣ Статистика
        stats = await repo.get_affiliate_stats(user_id)
        payments = await repo.get_payments(user_id)
        paid_out = await repo.get_paid_out(user_id)

        return {
            "code": code,
            "invited": stats["invited"],
            "active": stats["active"],
            "payments": payments,
            "paid_out": paid_out,
        }

    # -----------------------------------------
    # 📜 Получить список рефералов
    # -----------------------------------------
    async def get_my_referrals(self, user_id: int):
        rows = await repo.get_referrals_list(user_id)
        return [dict(row) for row in rows]

    # -----------------------------------------
    # 💰 Получить историю выплат
    # -----------------------------------------
    async def get_affiliate_payments_list(self, user_id: int):
        rows = await repo.get_payments_list(user_id)
        return [dict(row) for row in rows]


# =======================================
# Синглтон сервиса
# =======================================
affiliate_service = AffiliateService()
