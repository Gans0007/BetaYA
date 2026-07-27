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
   ДЛИТЕЛЬНОСТЬ ПРИВЫЧКИ

   День создания считается первым днём.
   ========================================================= */

export function getHabitDuration(createdAt) {
    const createdDate = new Date(createdAt)

    if (Number.isNaN(createdDate.getTime())) {
        return 1
    }

    const currentDate = new Date()

    const startOfCreatedDay = new Date(
        createdDate.getFullYear(),
        createdDate.getMonth(),
        createdDate.getDate()
    )

    const startOfCurrentDay = new Date(
        currentDate.getFullYear(),
        currentDate.getMonth(),
        currentDate.getDate()
    )

    const millisecondsPerDay =
        24 * 60 * 60 * 1000

    const difference = Math.floor(
        (
            startOfCurrentDay -
            startOfCreatedDay
        ) / millisecondsPerDay
    )

    return Math.max(
        1,
        difference + 1
    )
}