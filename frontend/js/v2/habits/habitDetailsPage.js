/* =========================================================
   HABIT DETAILS PAGE

   Детальная страница одной привычки.
   ========================================================= */


/* =========================================================
   ЭКРАНИРОВАНИЕ ТЕКСТА
   ========================================================= */

function escapeHtml(value) {
    return String(value)
        .replaceAll("&", "&amp;")
        .replaceAll("<", "&lt;")
        .replaceAll(">", "&gt;")
        .replaceAll('"', "&quot;")
        .replaceAll("'", "&#039;")
}


/* =========================================================
   ФОРМАТИРОВАНИЕ ДНЕЙ
   ========================================================= */

function formatDays(value) {
    const days = Math.max(
        0,
        Math.floor(Number(value) || 0)
    )

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
   ========================================================= */

function getHabitDuration(createdAt) {
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

    return Math.max(1, difference + 1)
}


/* =========================================================
   РЕНДЕР СТРАНИЦЫ
   ========================================================= */

export function renderHabitDetailsPage(habit = {}) {
    const root = document.getElementById(
        "habits-v2-root"
    )

    if (!root) {
        return
    }

    const {
        id = "",
        name = "Без названия",
        icon = "✱",
        color = "green",
        completedToday = false,
        streak = 0,
        xpReward = 5,
        createdAt = null
    } = habit

    const safeId = escapeHtml(id)
    const safeName = escapeHtml(name)
    const safeIcon = escapeHtml(icon)

    const normalizedStreak = Math.max(
        0,
        Math.floor(Number(streak) || 0)
    )

    const normalizedXpReward = Math.max(
        0,
        Math.floor(Number(xpReward) || 0)
    )

    const duration = getHabitDuration(
        createdAt
    )

    const statusText = completedToday
        ? `Выполнено +${normalizedXpReward} XP`
        : "В процессе"

    root.innerHTML = `
        <section
            class="
                habit-details
                habit-details--${escapeHtml(color)}
            "
            data-habit-id="${safeId}"
        >

            <header class="habit-details__header">

                <button
                    class="habit-details__back-button"
                    type="button"
                    data-action="close-habit-details"
                    aria-label="Вернуться к привычкам"
                >
                    ‹
                </button>

                <button
                    class="habit-details__menu-button"
                    type="button"
                    data-action="open-habit-menu"
                    aria-label="Открыть меню привычки"
                >
                    ⋯
                </button>

            </header>


            <main class="habit-details__content">

                <div
                    class="habit-details__icon"
                    aria-hidden="true"
                >
                    ${safeIcon}
                </div>


                <h1 class="habit-details__title">
                    ${safeName}
                </h1>


                <div class="habit-details__status">
                    ${statusText}
                </div>


                <section
                    class="habit-details__stats"
                    aria-label="Статистика привычки"
                >

                    <article class="habit-details__stat">

                        <div class="habit-details__stat-main">
                            <span aria-hidden="true">
                                🔥
                            </span>

                            <span>
                                ${formatDays(normalizedStreak)}
                            </span>
                        </div>

                        <div class="habit-details__stat-label">
                            Текущая серия
                        </div>

                    </article>


                    <article class="habit-details__stat">

                        <div class="habit-details__stat-main">
                            <span aria-hidden="true">
                                ◷
                            </span>

                            <span>
                                ${formatDays(duration)}
                            </span>
                        </div>

                        <div class="habit-details__stat-label">
                            Длительность
                        </div>

                    </article>

                </section>


                <section class="habit-details__calendar-placeholder">

                    <h2 class="habit-details__section-title">
                        Календарь
                    </h2>

                    <div class="habit-details__calendar-empty">
                        Календарь добавим следующим шагом
                    </div>

                </section>

            </main>

        </section>
    `
}