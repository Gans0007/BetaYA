from calendar import monthrange
from datetime import date, datetime
from zoneinfo import ZoneInfo


KYIV_TIMEZONE = ZoneInfo("Europe/Kyiv")


def get_current_season_info(current_date: date | None = None) -> dict:

    if current_date is None:
        current_date = datetime.now(KYIV_TIMEZONE).date()

    year = current_date.year
    month = current_date.month

    # -----------------------------
    # Сезон I
    # 1 июня - 31 августа
    # -----------------------------
    if 6 <= month <= 8:
        season_number = 1
        start_year = year
        end_year = year
        start_month = 6
        end_month = 8

    # -----------------------------
    # Сезон II
    # 1 сентября - 30 ноября
    # -----------------------------
    elif 9 <= month <= 11:
        season_number = 2
        start_year = year
        end_year = year
        start_month = 9
        end_month = 11

    # -----------------------------
    # Сезон III
    # 1 декабря - конец февраля
    # -----------------------------
    elif month == 12:
        season_number = 3
        start_year = year
        end_year = year + 1
        start_month = 12
        end_month = 2

    else:
        season_number = 3
        start_year = year - 1
        end_year = year
        start_month = 12
        end_month = 2

    # -----------------------------
    # Сезон IV
    # 1 марта - 31 мая
    # -----------------------------
    if 3 <= month <= 5:
        season_number = 4
        start_year = year
        end_year = year
        start_month = 3
        end_month = 5

    season_start = date(
        start_year,
        start_month,
        1
    )

    season_end = date(
        end_year,
        end_month,
        monthrange(end_year, end_month)[1]
    )

    days_left = max(
        0,
        (season_end - current_date).days
    )

    return {
        "key": f"{start_year}-S{season_number}",
        "number": season_number,
        "name": f"Сезон {season_number}",
        "year": start_year,
        "start": season_start,
        "end": season_end,
        "days_left": days_left,
    }


def get_current_season_key(current_date: date | None = None) -> str:
    return get_current_season_info(current_date)["key"]