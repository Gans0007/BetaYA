import {
    escapeHabitDetailsHtml,
    normalizeHabitDetailsNumber,
    formatHabitDetailsDays,
    getHabitDuration,
    createHabitDetailsCalendar
} from "./habitDetailsUtils.js"


/* =========================================================
   ДНИ НЕДЕЛИ
   ========================================================= */

const HABIT_DETAILS_WEEK_DAYS = [
    "Пн",
    "Вт",
    "Ср",
    "Чт",
    "Пт",
    "Сб",
    "Вс"
]


/* =========================================================
   РЕНДЕР ДНЕЙ НЕДЕЛИ
   ========================================================= */

function renderHabitCalendarWeekDays() {
    return HABIT_DETAILS_WEEK_DAYS
        .map(
            (dayName) => `
                <div
                    class="habit-calendar__weekday"
                    aria-hidden="true"
                >
                    ${dayName}
                </div>
            `
        )
        .join("")
}


/* =========================================================
   РЕНДЕР ЯЧЕЙКИ КАЛЕНДАРЯ
   ========================================================= */

function renderHabitCalendarCell(cell) {
    if (cell.type === "empty") {
        return `
            <div
                class="
                    habit-calendar__day
                    habit-calendar__day--empty
                "
                aria-hidden="true"
            ></div>
        `
    }

    const classNames = [
        "habit-calendar__day"
    ]

    if (cell.isCompleted) {
        classNames.push(
            "habit-calendar__day--completed"
        )
    }

    if (cell.isToday) {
        classNames.push(
            "habit-calendar__day--today"
        )
    }

    if (cell.isBeforeCreated) {
        classNames.push(
            "habit-calendar__day--before-created"
        )
    }

    if (cell.isFuture) {
        classNames.push(
            "habit-calendar__day--future"
        )
    }

    const stateLabel = []

    if (cell.isCompleted) {
        stateLabel.push("выполнено")
    }

    if (cell.isToday) {
        stateLabel.push("сегодня")
    }

    if (cell.isBeforeCreated) {
        stateLabel.push(
            "до создания привычки"
        )
    }

    if (cell.isFuture) {
        stateLabel.push("будущий день")
    }

    const ariaLabel = stateLabel.length
        ? `${cell.day}, ${stateLabel.join(", ")}`
        : String(cell.day)

    return `
        <div
            class="${classNames.join(" ")}"
            data-date="${cell.dateKey}"
            aria-label="${ariaLabel}"
        >
            <span class="habit-calendar__day-number">
                ${cell.day}
            </span>

            ${
                cell.isToday
                    ? `
                        <span
                            class="habit-calendar__today-dot"
                            aria-hidden="true"
                        ></span>
                    `
                    : ""
            }
        </div>
    `
}


/* =========================================================
   РЕНДЕР КАЛЕНДАРЯ
   ========================================================= */

function renderHabitCalendar({
    completedDates,
    createdAt
}) {
    const calendar =
        createHabitDetailsCalendar({
            completedDates,
            createdAt
        })

    const cellsHtml =
        calendar.cells
            .map(renderHabitCalendarCell)
            .join("")

    return `
        <section
            class="habit-details__calendar"
            aria-label="Календарь привычки"
        >

            <h2 class="habit-calendar__month">
                ${calendar.monthName}
            </h2>

            <div class="habit-calendar__weekdays">
                ${renderHabitCalendarWeekDays()}
            </div>

            <div class="habit-calendar__grid">
                ${cellsHtml}
            </div>

        </section>
    `
}


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
        createdAt = null,

        /*
           Пока API нет.

           completedDates временно приходит
           из локального объекта привычки / Store.
        */

        completedDates = []
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

/*
   Пока API нет.

   Если привычка подтверждена сегодня,
   временно добавляем сегодняшнюю дату
   в локальный календарь.
*/

const calendarCompletedDates = [
    ...completedDates
]

if (completedToday) {
    calendarCompletedDates.push(
        new Date()
    )
}

const calendarHtml =
    renderHabitCalendar({
        completedDates:
            calendarCompletedDates,
        createdAt
    })

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
    class="habit-details__back-button back-button"
    type="button"
    data-action="close-habit-details"
    aria-label="Вернуться к привычкам"
>
    <span
        class="material-symbols-rounded back-icon"
        aria-hidden="true"
    >
        arrow_back_ios_new
    </span>
</button>

<div class="habit-details__menu-wrapper">

    <button
        class="habit-details__menu-button"
        type="button"
        data-action="toggle-habit-menu"
        aria-label="Открыть меню привычки"
        aria-expanded="false"
        aria-controls="habit-details-menu"
    >
        ⋯
    </button>

    <div
        id="habit-details-menu"
        class="habit-details__menu"
        role="menu"
        aria-hidden="true"
    >

        <button
            class="habit-details__menu-item"
            type="button"
            data-action="confirm-habit"
            role="menuitem"
        >
            <span
                class="material-symbols-rounded habit-details__menu-icon"
                aria-hidden="true"
            >
                check_circle
            </span>

            <span>
                Подтвердить
            </span>
        </button>

        <button
            class="habit-details__menu-item"
            type="button"
            data-action="edit-habit"
            role="menuitem"
        >
            <span
                class="material-symbols-rounded habit-details__menu-icon"
                aria-hidden="true"
            >
                edit
            </span>

            <span>
                Редактировать
            </span>
        </button>

        <button
            class="
                habit-details__menu-item
                habit-details__menu-item--danger
            "
            type="button"
            data-action="delete-habit"
            role="menuitem"
        >
            <span
                class="material-symbols-rounded habit-details__menu-icon"
                aria-hidden="true"
            >
                delete
            </span>

            <span>
                Удалить
            </span>
        </button>

    </div>

</div>

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


                ${calendarHtml}

            </main>

        </section>
    `
}