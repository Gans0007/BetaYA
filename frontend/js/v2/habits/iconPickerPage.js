const HABIT_ICONS = [
    "✱", "🏃", "🥋", "🧘", "🚶", "🏊",
    "🏋️", "🚴", "⚽", "🎾", "🏀", "🏈",
    "⚾", "🥊", "🐾", "⚡", "➕", "🍴",
    "🥕", "💧", "☕", "🥛", "🍎", "💊",
    "🌳", "🌷", "🍃", "🚿", "🌙", "⏰",
    "🌅", "☀️", "❄️", "☁️", "🛏️", "🌍",
    "⏳", "💼", "💻", "📱", "🎓", "📖",
    "📥", "📁", "📦", "📄", "✍️", "🧠",
    "💰", "📊", "🎯", "🔥", "❤️", "⭐"
]

export function renderIconPickerPage(selectedIcon = "✱") {
    const root = document.getElementById("habits-v2-root")

    if (!root) {
        console.error("Icon Picker V2: не найден #habits-v2-root")
        return
    }

    const iconsMarkup = HABIT_ICONS.map((icon) => {
        const isSelected = icon === selectedIcon

        return `
            <button
                class="habit-icon-picker__item${isSelected ? " is-selected" : ""}"
                type="button"
                data-habit-icon="${icon}"
                aria-label="Выбрать значок ${icon}"
                aria-pressed="${isSelected}"
            >
                <span aria-hidden="true">${icon}</span>
            </button>
        `
    }).join("")

    root.innerHTML = `
        <section class="habit-icon-picker">

            <div
                class="habit-icon-picker__sheet"
                role="dialog"
                aria-modal="true"
                aria-label="Выбор значка привычки"
            >
                <div
                    class="habit-icon-picker__handle"
                    aria-hidden="true"
                ></div>

                <div class="habit-icon-picker__grid">
                    ${iconsMarkup}
                </div>

                <button
                    class="habit-icon-picker__confirm"
                    type="button"
                    data-action="confirm-habit-icon"
                >
                    Выбрать
                </button>
            </div>

        </section>
    `
}