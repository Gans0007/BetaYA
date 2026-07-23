/* =========================================================
   ICON PICKER PAGE V2
   Светлый полноэкранный выбор эмодзи
   6 элементов в строке
   ========================================================= */


/* =========================================================
   СПИСОК ЭМОДЗИ

   Порядок приближен к референсу:
   спорт → здоровье → питание → режим →
   работа → обучение
   ========================================================= */

const HABIT_ICONS = [
    // Спорт и физическая активность
    "✱", "🏃", "🥋", "🏋️", "🚶", "🧘",
    "🏊", "🧗", "🚴", "👣", "👤", "👥",
    "🙂", "🏋️‍♂️", "⚽", "🎾", "🏈", "🏀",
    "⚾", "🫁", "🐾", "⚡", "➕", "🍴",

    // Питание и вода
    "🥕", "💧", "☕", "🥤", "🍼", "🍷",
    "🍎", "🍌", "🥑", "🥗", "🥚", "🍚",
    "🥛", "🫖", "🍵", "🥣", "🥦", "🍋",

    // Здоровье и уход
    "💊", "⏱️", "🌳", "🌷", "🍃", "🚿",
    "🩺", "🧴", "🪥", "🧼", "🛁", "🧖",
    "❤️", "🧠", "🫀", "🦷", "👁️", "🩹",

    // Сон, режим и погода
    "🌙", "🕒", "🌅", "☀️", "❄️", "☁️",
    "🛏️", "⏰", "🌇", "🌄", "🌧️", "🌈",
    "📅", "⌛", "⏳", "🕯️", "🌌", "⭐",

    // Работа и продуктивность
    "🌍", "⏳", "💼", "💻", "📱", "⌨️",
    "📝", "✅", "📌", "📊", "📈", "🗂️",
    "🧾", "📋", "🖥️", "🖊️", "📎", "🧮",

    // Обучение и развитие
    "🎓", "📖", "📥", "📁", "📦", "📄",
    "📚", "✏️", "🧑‍💻", "🧩", "💡", "🔬",
    "🎯", "🗣️", "🎧", "🧪", "🌐", "🏆",

    // Деньги и статус
    "💰", "💵", "💳", "🪙", "🏦", "📉",
    "💎", "👑", "🚀", "🔥", "⭐", "🥇",

    // Отдых и личная жизнь
    "🎵", "🎮", "🎨", "📷", "🎬", "🎸",
    "🐕", "🐈", "🌿", "🏠", "🚗", "✈️"
]


/* =========================================================
   ЭКРАНИРОВАНИЕ ЗНАЧЕНИЙ

   Сейчас значения состоят из эмодзи, однако функция
   оставлена для безопасного формирования HTML.
   ========================================================= */

function escapeAttribute(value) {
    return String(value)
        .replaceAll("&", "&amp;")
        .replaceAll('"', "&quot;")
        .replaceAll("<", "&lt;")
        .replaceAll(">", "&gt;")
}


/* =========================================================
   СОЗДАНИЕ ОДНОГО ЭЛЕМЕНТА
   ========================================================= */

function createIconMarkup(icon, selectedIcon) {
    const isSelected = icon === selectedIcon

    return `
        <button
            class="habit-icon-picker__item${
                isSelected ? " is-selected" : ""
            }"
            type="button"
            data-habit-icon="${escapeAttribute(icon)}"
            aria-label="Выбрать значок ${escapeAttribute(icon)}"
            aria-pressed="${String(isSelected)}"
        >
            <span
                class="habit-icon-picker__emoji"
                aria-hidden="true"
            >
                ${icon}
            </span>
        </button>
    `
}


/* =========================================================
   РЕНДЕР СТРАНИЦЫ
   ========================================================= */

export function renderIconPickerPage(
    selectedIcon = "✱"
) {
    const root = document.getElementById(
        "habits-v2-root"
    )

    if (!root) {
        console.error(
            "Icon Picker V2: не найден контейнер #habits-v2-root"
        )

        return
    }

    const iconsMarkup = HABIT_ICONS
        .map((icon) => {
            return createIconMarkup(
                icon,
                selectedIcon
            )
        })
        .join("")

    root.innerHTML = `
        <section class="habit-icon-picker">

            <div
                class="habit-icon-picker__sheet"
                role="dialog"
                aria-modal="true"
                aria-label="Выбор значка привычки"
            >

                <!-- Верхняя панель -->

                <header class="habit-icon-picker__header">

                    <button
                        class="habit-icon-picker__back-button"
                        type="button"
                        data-action="close-icon-picker"
                        aria-label="Вернуться к созданию привычки"
                    >
                        <span
                            class="habit-icon-picker__back-icon"
                            aria-hidden="true"
                        >
                            ‹
                        </span>
                    </button>

                </header>


                <!-- Прокручиваемая сетка эмодзи -->

                <div class="habit-icon-picker__body">

                    <div
                        class="habit-icon-picker__grid"
                        role="list"
                        aria-label="Доступные значки привычки"
                    >
                        ${iconsMarkup}
                    </div>

                </div>


                <!-- Фиксированная нижняя кнопка -->

                <footer class="habit-icon-picker__footer">

                    <button
                        class="habit-icon-picker__confirm"
                        type="button"
                        data-action="confirm-habit-icon"
                    >
                        Выбрать
                    </button>

                </footer>

            </div>

        </section>
    `
}