import { renderHabitCard } from "./habitCard.js"
import { formatCurrentDate } from "./habitsUtils.js"


export function renderHabitsList(habits) {
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


            <section class="habits-v2-list__today">

                <h2 class="habits-v2-list__section-title">
                    Сегодня
                </h2>

                <div class="habits-v2-list__cards">
                    ${habits.map(renderHabitCard).join("")}
                </div>

            </section>

        </section>
    `
}