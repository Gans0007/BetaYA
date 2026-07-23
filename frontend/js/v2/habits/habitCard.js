export function renderHabitCard(habit) {
    const {
        id,
        name,
        icon = "✱",
        color = "blue",
        size = "large"
    } = habit

    return `
        <article
            class="
                habit-card
                habit-card--${color}
                habit-card--${size}
            "
            data-habit-id="${id}"
        >
            <div class="habit-card__icon">
                ${icon}
            </div>

            <div class="habit-card__content">
                <h2 class="habit-card__name">
                    ${name}
                </h2>
            </div>
        </article>
    `
}