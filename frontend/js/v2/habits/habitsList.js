import { renderHabitCard } from "./habitCard.js"


export function renderHabitsList(habits) {
    return `
        <section class="habits-v2-list">

            <header class="habits-v2-list__header">
                <div class="habits-v2-list__date">
                    Вт, 21 июля
                </div>

                <h1 class="habits-v2-list__title">
                    Мои привычки
                </h1>
            </header>

            <div class="habits-v2-list__cards">
                ${habits.map(renderHabitCard).join("")}
            </div>

        </section>
    `
}