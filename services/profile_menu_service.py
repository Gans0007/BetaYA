from repositories.profile_repository import get_is_affiliate


class ProfileService:

    async def user_is_affiliate(self, user_id: int) -> bool:
        """
        Возвращает True если пользователь имеет статус партнёра
        """
        return await get_is_affiliate(user_id)


profile_service = ProfileService()
