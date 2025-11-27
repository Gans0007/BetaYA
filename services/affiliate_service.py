from repositories import affiliate_repository as repo


class AffiliateService:

    # -----------------------------------------
    # 📌 Назначить реферального партнёра
    # -----------------------------------------
    async def assign_referral(self, user_id: int, referral_code: str) -> bool:
        """
        Возвращает:
        True — реферал успешно присвоен
        False — не присваиваем (код не найден, или уже есть реферал)
        """

        # найти владельца реф-кода
        affiliate_id = await repo.get_affiliate_by_code(referral_code)
        if not affiliate_id:
            return False

        # нельзя быть рефералом самого себя
        if affiliate_id == user_id:
            return False

        # проверяем — уже являешься чьим-то рефералом?
        if await repo.user_already_has_affiliate(user_id):
            return False

        # записываем
        await repo.create_referral(affiliate_id, user_id)
        return True


    # -----------------------------------------
    # 🟢 Сделать реферала активным
    # -----------------------------------------
    async def activate_referral(self, user_id: int, bonus_amount: float = 0):
        """
        Активирует реферала.
        По желанию начисляет бонус партнёру.
        """

        affiliate_id = await repo.get_affiliate_for_user(user_id)
        if not affiliate_id:
            return False

        # обновляем статус
        await repo.mark_referral_active(user_id)

        # начисление денег партнёру
        if bonus_amount > 0:
            await repo.add_payment_to_affiliate(affiliate_id, bonus_amount)

        return True


    # -----------------------------------------
    # 🔴 Сделать реферала неактивным
    # -----------------------------------------
    async def deactivate_referral(self, user_id: int):
        """
        Убирает активный статус у реферала.
        """

        await repo.mark_referral_inactive(user_id)
        return True


    # -----------------------------------------
    # 📊 Получить отображаемую инфу для меню
    # -----------------------------------------
    async def get_affiliate_dashboard(self, user_id: int):
        """
        Возвращает словарь с данными для UI.
        """

        stats = await repo.get_affiliate_stats(user_id)
        code = await repo.get_referral_code(user_id)
        payments = await repo.get_payments(user_id)

        return {
            "code": code,
            "invited": stats["invited"],
            "active": stats["active"],
            "payments": payments,
        }


    # -----------------------------------------
    # 📜 Получить список рефералов (для UI)
    # -----------------------------------------
    async def get_my_referrals(self, user_id: int):
        """
        Возвращает список словарей:
        {
            "user_id":,
            "registered_at":,
            "is_active":,
            "active_at":,
            "username":
        }
        """

        rows = await repo.get_referrals_list(user_id)
        return [dict(row) for row in rows]


    # -----------------------------------------
    # 💰 Получить историю выплат (для UI)
    # -----------------------------------------
    async def get_affiliate_payments_list(self, user_id: int):
        """
        Возвращает историю выплат.
        """

        rows = await repo.get_payments_list(user_id)
        return [dict(row) for row in rows]


# =======================================
# Синглтон сервиса
# =======================================
affiliate_service = AffiliateService()
