import random
import logging
from aiogram import Router, types

router = Router()
logger = logging.getLogger(__name__)

CHANNEL_USERNAME = "@yourambitions"

# Список рабочих file_id мотивационных изображений
MOTIVATION_CONTENT = [
    ("photo", "AgACAgIAAxkBAAKfaWiKcT8Zvpa0gyVy09kKXjOQFxFEAAIt7zEbhhxYSFGk0REQ3niXAQADAgADeQADNgQ"),
    ("photo", "AgACAgIAAxkBAAKfbWiKcVNUMky63XUKNmn0O1Au-3FsAAIv7zEbhhxYSFrT5QNUGw2fAQADAgADeQADNgQ"),
    ("photo", "AgACAgIAAxkBAAKfb2iKcVPAiYW-fhc24-J29u0d4WMPAAIx7zEbhhxYSDyv2L-DzHS7AQADAgADeQADNgQ"),
    ("photo", "AgACAgIAAxkBAAKfa2iKcVOODSiuBODV9DqhooOk4g2RAAIu7zEbhhxYSD8fzQkkV3B-AQADAgADeQADNgQ"),
    ("photo", "AgACAgIAAxkBAAKfdWiKcV6_n1AhquLxDOLe33lq5TbVAAIz7zEbhhxYSJH_AYzw7dhaAQADAgADeQADNgQ"),
    ("photo", "AgACAgIAAxkBAAKfd2iKcV4_ixeqH6ZZjznI6Uqa5bRbAAI17zEbhhxYSCQYoA94T0QjAQADAgADeQADNgQ"),
    ("photo", "AgACAgIAAxkBAAKfdmiKcV42Dl8xdiPKxAK27lyycT3hAAI07zEbhhxYSMoMHfY_sT25AQADAgADeQADNgQ"),
    ("photo", "AgACAgIAAxkBAAKfeGiKcV7XMGBARe0rnAJKPdcDWuL3AAKr-jEbgd5RSLOMhYnvLGYZAQADAgADeQADNgQ"),
    ("photo", "AgACAgIAAxkBAAKfeWiKcV7oixmXlGnXeLIbD8QKx7JfAAJ-9zEbqDpYSOture27i5O1AQADAgADeQADNgQ"),
    ("photo", "AgACAgIAAxkBAAKffWiKcV7m5wu014R2cLO1gcnmnwsTAAI57zEbhhxYSL3D1Cjjyx_wAQADAgADeQADNgQ"),
    ("photo", "AgACAgIAAxkBAAKfemiKcV6Dd-qtdooyAYrBSIVfxDACAAI47zEbhhxYSHIU1NO_cB5MAQADAgADeQADNgQ"),
    ("photo", "AgACAgIAAxkBAAKffmiKcV4vOO1TYpLoS2ITDLKeu6wUAAKs-jEbgd5RSINoSTzBIzpkAQADAgADeQADNgQ"),
    ("photo", "AgACAgIAAxkBAAKffGiKcV7Iwg5KEGUkURkeuLSKEO-4AAI27zEbhhxYSHZ7BLNCE888AQADAgADeQADNgQ"),
    ("photo", "AgACAgIAAxkBAAKfe2iKcV5KyfU5zeI5exkiJzb3_3VQAAI37zEbhhxYSCJ-Bs3Dj8aMAQADAgADeQADNgQ"),
    ("photo", "AgACAgIAAxkBAAKfimiKcV_XQLfuoBN3LiXNHke7ztjsAAI77zEbhhxYSGt6rJYLBTiMAQADAgADeQADNgQ"),
    ("photo", "AgACAgIAAxkBAAKfiWiKcV-NOxTxFIbwOfGJzTzdKbwlAAI67zEbhhxYSEPpumGdvut2AQADAgADeQADNgQ"),
    ("photo", "AgACAgIAAxkBAAKfjGiKcV9L925tPxB3v1DGm0puK1teAAI-7zEbhhxYSDTGwB2iBnGoAQADAgADeQADNgQ"),
    ("photo", "AgACAgIAAxkBAAKfjWiKcV-vbs8HB1C9yHUjpCc_VfddAAI_7zEbhhxYSJkRhm0msj-dAQADAgADeQADNgQ"),
    ("photo", "AgACAgIAAxkBAAKfj2iKcV_QGpnQEtVeCOjh8ukiLwjhAAI97zEbhhxYSLJ5eUrNCWJ9AQADAgADeQADNgQ"),
    ("photo", "AgACAgIAAxkBAAKfjmiKcV9z-Z_kgb40h88Ho2HW_xdXAAJA7zEbhhxYSAn_M-M9QNeMAQADAgADeQADNgQ"),
    ("photo", "AgACAgIAAxkBAAKfkGiKcV-CNW3JrywefIlS_74Q77HlAAJC7zEbhhxYSD-lWG46DWWfAQADAgADeQADNgQ"),
    ("photo", "AgACAgIAAxkBAAKfi2iKcV-LRVrJnvLbwLf_MDG3r47aAAI87zEbhhxYSKimGubZh-LcAQADAgADeQADNgQ"),

    # Посты канала (пересылка)
    ("post", 579),
    ("post", 578),
    ("post", 576),
    ("post", 570),
]

@router.message(lambda msg: msg.text == "⚡️ Мотивация")
async def show_motivation(message: types.Message):
    choice = random.choice(MOTIVATION_CONTENT)
    content_type, value = choice
    logger.info(f"[MOTIVATION] Выбран контент: {content_type} | {value}")

    if content_type == "photo":
        await message.answer_photo(value, caption="💪 Держи мотивацию!")
    else:  # post
        try:
            await message.bot.forward_message(
                chat_id=message.chat.id,
                from_chat_id=CHANNEL_USERNAME,
                message_id=value
            )
        except Exception as e:
            logger.error(f"[MOTIVATION] Ошибка при пересылке поста {value}: {e}")
            await message.answer("❌ Ошибка при пересылке поста. Убедись, что бот админ в канале.")