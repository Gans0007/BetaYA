import { renderHabitCard } from "./habitCard.js"
import { renderHabitsStats } from "./habitsStats.js"
import { formatCurrentDate } from "../habitsUtils.js"


export function renderHabitsList(
    habits,
    statistics = {}
) {
    return `
        <section class="habits-v2-list">

            <header class="habits-v2-list__header">

                <div class="habits-v2-list__top">

                    <div class="habits-v2-list__heading">

                        <div class="habits-v2-list__date">
                            ${formatCurrentDate()}
                        </div>

                        <h1 class="habits-v2-list__title">
                            Главная
                        </h1>

                    </div>

                    <div class="habits-v2-list__actions">

                        <button
                            class="habits-v2-list__add-button"
                            type="button"
                            data-action="open-add-habit"
                            aria-label="Создать привычку"
                        >
                            +
                        </button>

                    </div>

                </div>

            </header>


            ${renderHabitsStats(statistics)}


            <div class="habits-v2-list__cards">
                ${habits.map(renderHabitCard).join("")}
            </div>

        </section>
    `
}