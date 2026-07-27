import {
    escapeHabitDetailsHtml,
    normalizeHabitDetailsNumber,
    formatHabitDetailsDays,
    getHabitDuration
} from "./habitDetailsUtils.js"


/* =========================================================
   HABIT DETAILS PAGE

   Отвечает только за разметку детальной страницы.
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

    const safeId =
        escapeHabitDetailsHtml(id)

    const safeName =
        escapeHabitDetailsHtml(name)

    const safeIcon =
        escapeHabitDetailsHtml(icon)

    const safeColor =
        escapeHabitDetailsHtml(color)

    const normalizedStreak =
        normalizeHabitDetailsNumber(streak)

    const normalizedXpReward =
        normalizeHabitDetailsNumber(xpReward)

    const duration =
        getHabitDuration(createdAt)

    const statusText = completedToday
        ? `Выполнено +${normalizedXpReward} XP`
        : "В процессе"

    root.innerHTML = `
        <section
            class="
                habit-details
                habit-details--${safeColor}
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
                                ${formatHabitDetailsDays(
                                    normalizedStreak
                                )}
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
                                ${formatHabitDetailsDays(
                                    duration
                                )}
                            </span>

                        </div>

                        <div class="habit-details__stat-label">
                            Длительность
                        </div>

                    </article>

                </section>


                <section
                    class="habit-details__calendar-placeholder"
                >

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