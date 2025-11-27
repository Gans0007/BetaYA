# services/profile_settings_service.py
from repositories.profile_settings_repository import (
    get_user_settings,
    update_notification_tone,
    update_language,
    toggle_share_media
)


NOTIFICATION_TONES = {
    "friend": "Друг🤝",
    "gamer": "Игровой🎮",
    "spartan": "Спартанец⚔️",
}

LANGUAGES = {
    "ru": "Рус",
    "uk": "🇺🇦 Українська",
    "en": "🇬🇧 English",
}


class ProfileSettingsService:

    async def get_settings_for_user(self, user_id: int):
        user = await get_user_settings(user_id)

        tone_code = user["notification_tone"] or "friend"
        share_on = user["share_confirmation_media"] if user["share_confirmation_media"] is not None else True
        lang_code = user["language"] or "ru"

        return {
            "tone_code": tone_code,
            "tone_label": NOTIFICATION_TONES.get(tone_code),
            "share_on": share_on,
            "lang_code": lang_code,
            "lang_label": LANGUAGES.get(lang_code),
        }

    async def set_tone(self, user_id: int, tone_code: str):
        if tone_code not in NOTIFICATION_TONES:
            return False
        await update_notification_tone(user_id, tone_code)
        return True

    async def set_language(self, user_id: int, lang_code: str):
        if lang_code not in LANGUAGES:
            return False
        await update_language(user_id, lang_code)
        return True

    async def toggle_share_media_option(self, user_id: int):
        return await toggle_share_media(user_id)


profile_settings_service = ProfileSettingsService()
