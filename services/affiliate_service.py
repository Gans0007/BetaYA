import logging
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
    # 🟢 Сделать реферала активным (ПЕРВАЯ АКТИВАЦИЯ)
    # -----------------------------------------
    async def activate_referral(self, user_id: int, bonus_amount: float = 0):
        affiliate_id = await repo.get_affiliate_for_user(user_id)

        if not affiliate_id:
            logging.warning(
                f"⚠️ [REF-ACTIVATE] Пользователь {user_id} активирован, "
                f"но affiliate не найден"
            )
            return False

        # 🔒 Защита от повторной активации
        if await repo.is_referral_active(user_id):
            logging.warning(
                f"⛔ [REF-ACTIVATE] Повторная активация реферала {user_id} "
                f"→ affiliate {affiliate_id} (пропуск)"
            )
            return False

        logging.info(
            f"🟢 [REF-ACTIVATE] Начало активации реферала {user_id} "
            f"→ affiliate {affiliate_id}"
        )

        # 1️⃣ Помечаем реферала активным
        await repo.mark_referral_active(user_id)

        logging.info(
            f"✅ [REF-ACTIVATE] Реферал {user_id} помечен активным в referrals"
        )

        if bonus_amount > 0:
            # 2️⃣ Записываем событие выплаты
            await repo.add_affiliate_payment(
                affiliate_id=affiliate_id,
                referral_user_id=user_id,
                amount=bonus_amount
            )

            logging.info(
                f"💰 [REF-PAYMENT] Создана запись выплаты: "
                f"affiliate={affiliate_id}, referral={user_id}, сумма={bonus_amount}"
            )

            # 3️⃣ Обновляем баланс партнёра
            await repo.add_payment_to_affiliate(
                affiliate_id,
                bonus_amount
            )

            logging.info(
                f"💳 [REF-PAYMENT] Баланс партнёра {affiliate_id} "
                f"увеличен на {bonus_amount}"
            )
        else:
            logging.info(
                f"ℹ️ [REF-ACTIVATE] Активация реферала {user_id} без бонуса"
            )

        logging.info(
            f"🏁 [REF-ACTIVATE] Завершена активация реферала {user_id} "
            f"→ affiliate {affiliate_id}"
        )

        return True

    # -----------------------------------------
    # 🔁 Продление подписки (ПОВТОРНЫЕ ВЫПЛАТЫ)
    # -----------------------------------------
    async def pay_for_subscription_renewal(
        self,
        referral_user_id: int,
        amount: float
    ):
        affiliate_id = await repo.get_affiliate_for_user(referral_user_id)

        if not affiliate_id:
            logging.warning(
                f"⚠️ [REF-RENEW] Продление подписки для пользователя "
                f"{referral_user_id}, но affiliate не найден"
            )
            return False

        # ❗ Продление подписки — БЕЗ проверки is_referral_active
        await repo.add_affiliate_payment(
            affiliate_id=affiliate_id,
            referral_user_id=referral_user_id,
            amount=amount
        )

        logging.info(
            f"💰 [REF-RENEW] Запись выплаты за продление создана: "
            f"affiliate={affiliate_id}, referral={referral_user_id}, сумма={amount}"
        )

        await repo.add_payment_to_affiliate(
            affiliate_id,
            amount
        )

        logging.info(
            f"💳 [REF-RENEW] Баланс партнёра {affiliate_id} "
            f"увеличен на {amount}"
        )

        logging.info(
            f"🔁 [REF-RENEW] Продление подписки завершено: "
            f"referral={referral_user_id}, affiliate={affiliate_id}"
        )

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
    # 📜 Рефералы с пагинацией
    # -----------------------------------------
    async def get_my_referrals_paginated(
        self,
        user_id: int,
        page: int = 1,
        per_page: int = 10
    ):
        if page < 1:
            page = 1

        offset = (page - 1) * per_page

        total = await repo.get_referrals_count(user_id)
        rows = await repo.get_referrals_list_paginated(
            user_id,
            limit=per_page,
            offset=offset
        )

        return {
            "total": total,
            "page": page,
            "per_page": per_page,
            "items": [dict(r) for r in rows]
        }


    # -----------------------------------------
    # 💰 Получить историю выплат (РЕАЛЬНУЮ)
    # -----------------------------------------
    async def get_affiliate_payments_list(self, user_id: int):
        rows = await repo.get_affiliate_payments_history(user_id)
        return [dict(row) for row in rows]



# =======================================
# Синглтон сервиса
# =======================================
affiliate_service = AffiliateService()
