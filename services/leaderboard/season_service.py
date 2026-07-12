from calendar import monthrange
from datetime import date, datetime
from zoneinfo import ZoneInfo


KYIV_TIMEZONE = ZoneInfo("Europe/Kyiv")


def get_current_season_info(current_date: date | None = None) -> dict:
    """
    Возвращает текущий трёхмесячный сезон.

    S1: январь — март
    S2: апрель — июнь
    S3: июль — сентябрь
    S4: октябрь — декабрь
    """

    if current_date is None:
        current_date = datetime.now(KYIV_TIMEZONE).date()

    year = current_date.year
    month = current_date.month

    season_number = ((month - 1) // 3) + 1

    start_month = ((season_number - 1) * 3) + 1
    end_month = start_month + 2

    season_start = date(year, start_month, 1)
    season_end = date(
        year,
        end_month,
        monthrange(year, end_month)[1]
    )

    days_left = max(
        0,
        (season_end - current_date).days
    )

    return {
        "key": f"{year}-S{season_number}",
        "number": season_number,
        "name": f"Сезон {season_number}",
        "year": year,
        "start": season_start,
        "end": season_end,
        "days_left": days_left,
    }


def get_current_season_key(current_date: date | None = None) -> str:
    return get_current_season_info(current_date)["key"]