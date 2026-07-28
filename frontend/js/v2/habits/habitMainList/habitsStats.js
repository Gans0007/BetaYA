/* =========================================================
   HABITS STATS

   Общая статистика привычек:
   текущая серия и суммарный XP.
   ========================================================= */


/* =========================================================
   НОРМАЛИЗАЦИЯ ЧИСЛА
   ========================================================= */

function normalizeStatValue(value) {
    const number = Number(value)

    if (!Number.isFinite(number) || number < 0) {
        return 0
    }

    return Math.floor(number)
}


/* =========================================================
   ФОРМАТИРОВАНИЕ ДНЕЙ
   ========================================================= */

function formatDays(value) {
    const days = normalizeStatValue(value)

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
   РЕНДЕР СТАТИСТИКИ
   ========================================================= */

export function renderHabitsStats(statistics = {}) {
    const currentStreak = normalizeStatValue(
        statistics.currentStreak
    )

    const totalXp = normalizeStatValue(
        statistics.totalXp
    )

    return `
        <section
            class="habits-stats"
            aria-label="Статистика привычек"
        >

            <article class="habits-stats__card">

                <div class="habits-stats__main">

                    <span
                        class="
                            habits-stats__icon
                            habits-stats__icon--streak
                        "
                        aria-hidden="true"
                    >
                        🔥
                    </span>

                    <span class="habits-stats__value">
                        ${formatDays(currentStreak)}
                    </span>

                </div>

                <div class="habits-stats__label">
                    Текущая серия
                </div>

            </article>


            <article class="habits-stats__card">

                <div class="habits-stats__main">

                    <span
                        class="
                            habits-stats__icon
                            habits-stats__icon--xp
                        "
                        aria-hidden="true"
                    >
                        ⭐
                    </span>

                    <span class="habits-stats__value">
                        ${totalXp}
                    </span>

                </div>

                <div class="habits-stats__label">
                    Всего XP
                </div>

            </article>

        </section>
    `
}