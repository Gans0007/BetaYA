/* =========================================================
   HABIT DETAILS UTILS

   Вспомогательные функции детальной страницы привычки.
   Здесь нет DOM, событий и рендера страницы.
   ========================================================= */


/* =========================================================
   ЭКРАНИРОВАНИЕ HTML
   ========================================================= */

export function escapeHabitDetailsHtml(value) {
    return String(value)
        .replaceAll("&", "&amp;")
        .replaceAll("<", "&lt;")
        .replaceAll(">", "&gt;")
        .replaceAll('"', "&quot;")
        .replaceAll("'", "&#039;")
}


/* =========================================================
   НОРМАЛИЗАЦИЯ ЧИСЛА
   ========================================================= */

export function normalizeHabitDetailsNumber(value) {
    const number = Number(value)

    if (!Number.isFinite(number) || number < 0) {
        return 0
    }

    return Math.floor(number)
}


/* =========================================================
   ФОРМАТИРОВАНИЕ ДНЕЙ
   ========================================================= */

export function formatHabitDetailsDays(value) {
    const days =
        normalizeHabitDetailsNumber(value)

    const lastTwoDigits = days % 100
    const lastDigit = days % 10

    if (
        lastTwoDigits >= 11 &&
        lastTwoDigits <= 14
    ) {
        return `${days} дней`
    }

    if (lastDigit === 1) {
        return `${days} день`
    }

    if (
        lastDigit >= 2 &&
        lastDigit <= 4
    ) {
        return `${days} дня`
    }

    return `${days} дней`
}


/* =========================================================
   ПОЛУЧЕНИЕ ЛОКАЛЬНОЙ ДАТЫ

   Не используем new Date("2026-07-24"),
   потому что браузер может воспринять такую дату как UTC.
   ========================================================= */

export function parseHabitDetailsDate(value) {
    if (value instanceof Date) {
        const copiedDate = new Date(value)

        if (!Number.isNaN(copiedDate.getTime())) {
            return copiedDate
        }

        return null
    }

    if (typeof value !== "string") {
        return null
    }

    const normalizedValue =
        value.trim().slice(0, 10)

    const match = normalizedValue.match(
        /^(\d{4})-(\d{2})-(\d{2})$/
    )

    if (!match) {
        const fallbackDate = new Date(value)

        if (Number.isNaN(fallbackDate.getTime())) {
            return null
        }

        return fallbackDate
    }

    const year = Number(match[1])
    const monthIndex = Number(match[2]) - 1
    const day = Number(match[3])

    const date = new Date(
        year,
        monthIndex,
        day
    )

    if (
        date.getFullYear() !== year ||
        date.getMonth() !== monthIndex ||
        date.getDate() !== day
    ) {
        return null
    }

    return date
}


/* =========================================================
   КЛЮЧ ДАТЫ YYYY-MM-DD
   ========================================================= */

export function getHabitDetailsDateKey(value) {
    const date =
        parseHabitDetailsDate(value)

    if (!date) {
        return ""
    }

    const year =
        date.getFullYear()

    const month =
        String(date.getMonth() + 1)
            .padStart(2, "0")

    const day =
        String(date.getDate())
            .padStart(2, "0")

    return `${year}-${month}-${day}`
}


/* =========================================================
   СРАВНЕНИЕ ДАТ БЕЗ ВРЕМЕНИ
   ========================================================= */

export function compareHabitDetailsDates(
    firstValue,
    secondValue
) {
    const firstDate =
        parseHabitDetailsDate(firstValue)

    const secondDate =
        parseHabitDetailsDate(secondValue)

    if (!firstDate || !secondDate) {
        return 0
    }

    const firstTime = new Date(
        firstDate.getFullYear(),
        firstDate.getMonth(),
        firstDate.getDate()
    ).getTime()

    const secondTime = new Date(
        secondDate.getFullYear(),
        secondDate.getMonth(),
        secondDate.getDate()
    ).getTime()

    if (firstTime < secondTime) {
        return -1
    }

    if (firstTime > secondTime) {
        return 1
    }

    return 0
}


/* =========================================================
   ДЛИТЕЛЬНОСТЬ ПРИВЫЧКИ

   День создания считается первым днём.
   Используем UTC, чтобы переход летнего времени
   не влиял на количество календарных дней.
   ========================================================= */

export function getHabitDuration(createdAt) {
    const createdDate =
        parseHabitDetailsDate(createdAt)

    if (!createdDate) {
        return 1
    }

    const currentDate = new Date()

    const createdDayUtc = Date.UTC(
        createdDate.getFullYear(),
        createdDate.getMonth(),
        createdDate.getDate()
    )

    const currentDayUtc = Date.UTC(
        currentDate.getFullYear(),
        currentDate.getMonth(),
        currentDate.getDate()
    )

    const millisecondsPerDay =
        24 * 60 * 60 * 1000

    const difference = Math.floor(
        (
            currentDayUtc -
            createdDayUtc
        ) / millisecondsPerDay
    )

    return Math.max(
        1,
        difference + 1
    )
}
/* =========================================================
   НАЗВАНИЯ МЕСЯЦЕВ
   ========================================================= */

const HABIT_DETAILS_MONTH_NAMES = [
    "Январь",
    "Февраль",
    "Март",
    "Апрель",
    "Май",
    "Июнь",
    "Июль",
    "Август",
    "Сентябрь",
    "Октябрь",
    "Ноябрь",
    "Декабрь"
]


/* =========================================================
   НАЗВАНИЕ МЕСЯЦА
   ========================================================= */

export function getHabitDetailsMonthName(
    monthIndex
) {
    return (
        HABIT_DETAILS_MONTH_NAMES[
            monthIndex
        ] ?? ""
    )
}


/* =========================================================
   НОРМАЛИЗАЦИЯ ВЫПОЛНЕННЫХ ДАТ
   ========================================================= */

export function normalizeHabitCompletedDates(
    completedDates
) {
    if (!Array.isArray(completedDates)) {
        return new Set()
    }

    const normalizedDates =
        completedDates
            .map(getHabitDetailsDateKey)
            .filter(Boolean)

    return new Set(normalizedDates)
}


/* =========================================================
   ПОСТРОЕНИЕ КАЛЕНДАРЯ

   Возвращает данные текущего месяца.
   Неделя начинается с понедельника.
   ========================================================= */

export function createHabitDetailsCalendar({
    completedDates = [],
    createdAt = null,
    currentDate = new Date()
} = {}) {
    const safeCurrentDate =
        parseHabitDetailsDate(currentDate) ??
        new Date()

    const year =
        safeCurrentDate.getFullYear()

    const monthIndex =
        safeCurrentDate.getMonth()

    const todayKey =
        getHabitDetailsDateKey(
            safeCurrentDate
        )

    const createdDate =
        parseHabitDetailsDate(createdAt)

    const createdDateKey =
        getHabitDetailsDateKey(
            createdDate
        )

    const normalizedCompletedDates =
        normalizeHabitCompletedDates(
            completedDates
        )

    const firstDayOfMonth =
        new Date(
            year,
            monthIndex,
            1
        )

    const daysInMonth =
        new Date(
            year,
            monthIndex + 1,
            0
        ).getDate()

    /*
       JavaScript:
       Вс = 0
       Пн = 1
       ...
       Сб = 6

       Нам нужно:
       Пн = 0
       ...
       Вс = 6
    */

    const emptyCellsBeforeMonth =
        (
            firstDayOfMonth.getDay() + 6
        ) % 7

    const cells = []

    for (
        let index = 0;
        index < emptyCellsBeforeMonth;
        index += 1
    ) {
        cells.push({
            type: "empty",
            key: `empty-${index}`
        })
    }

    for (
        let day = 1;
        day <= daysInMonth;
        day += 1
    ) {
        const date = new Date(
            year,
            monthIndex,
            day
        )

        const dateKey =
            getHabitDetailsDateKey(date)

        const isToday =
            dateKey === todayKey

        const isCompleted =
            normalizedCompletedDates.has(
                dateKey
            )

        const isBeforeCreated =
            Boolean(createdDateKey) &&
            compareHabitDetailsDates(
                date,
                createdDate
            ) < 0

        const isFuture =
            compareHabitDetailsDates(
                date,
                safeCurrentDate
            ) > 0

        cells.push({
            type: "day",
            key: dateKey,
            day,
            dateKey,
            isToday,
            isCompleted,
            isBeforeCreated,
            isFuture
        })
    }

    return {
        year,
        monthIndex,
        monthName:
            getHabitDetailsMonthName(
                monthIndex
            ),
        todayKey,
        cells
    }
}