/* =========================================================
   HABITS STATS

   Отображает общую статистику раздела привычек:
   текущую серию и общее количество XP.
   ========================================================= */


/* =========================================================
   БЕЗОПАСНОЕ ЧИСЛО
   ========================================================= */

function normalizeStatValue(value) {
    const number = Number(value)

    if (!Number.isFinite(number) || number < 0) {
        return 0
    }

    return Math.floor(number)
}


/* =========================================================
   ФОРМА СЛОВА «ДЕНЬ»
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

                <div
                    class="habits-stats__icon"
                    aria-hidden="true"
                >
                    🔥
                </div>

                <div class="habits-stats__content">

                    <div class="habits-stats__label">
                        Текущая серия
                    </div>

                    <div class="habits-stats__value">
                        ${formatDays(currentStreak)}
                    </div>

                </div>

            </article>


            <article class="habits-stats__card">

                <div
                    class="habits-stats__icon"
                    aria-hidden="true"
                >
                    ⭐
                </div>

                <div class="habits-stats__content">

                    <div class="habits-stats__label">
                        Всего XP
                    </div>

                    <div class="habits-stats__value">
                        ${totalXp} XP
                    </div>

                </div>

            </article>

        </section>
    `
}