/* =========================================================
   HABITS UTILS

   Вспомогательные функции раздела привычек.
   Здесь нет состояния, HTML и запросов к API.
   ========================================================= */


/* =========================================================
   СОЗДАНИЕ УНИКАЛЬНОГО ID
   ========================================================= */

export function createHabitId() {
    if (
        typeof crypto !== "undefined" &&
        typeof crypto.randomUUID === "function"
    ) {
        return crypto.randomUUID()
    }

    return `habit-${Date.now()}-${Math.random()
        .toString(16)
        .slice(2)}`
}


/* =========================================================
   АНИМАЦИЯ НАЖАТИЯ
   Добавляет класс is-pressed на время нажатия.
   ========================================================= */

export function addPressAnimation(element) {
    if (!element) {
        return
    }

    let releaseTimer = null

    const press = () => {
        if (releaseTimer) {
            window.clearTimeout(releaseTimer)
        }

        element.classList.add("is-pressed")
    }

    const release = () => {
        releaseTimer = window.setTimeout(() => {
            element.classList.remove("is-pressed")
        }, 90)
    }

    element.addEventListener(
        "pointerdown",
        press
    )

    element.addEventListener(
        "pointerup",
        release
    )

    element.addEventListener(
        "pointercancel",
        release
    )

    element.addEventListener(
        "pointerleave",
        release
    )

    element.addEventListener(
        "touchstart",
        press,
        {
            passive: true
        }
    )

    element.addEventListener(
        "touchend",
        release,
        {
            passive: true
        }
    )

    element.addEventListener(
        "touchcancel",
        release,
        {
            passive: true
        }
    )
}

/* =========================================================
   ТЕКУЩАЯ ДАТА

   Возвращает строку:
   Пн, 27 июля
   ========================================================= */

export function formatCurrentDate() {
    const date = new Date()

    const weekdays = [
        "Вс",
        "Пн",
        "Вт",
        "Ср",
        "Чт",
        "Пт",
        "Сб"
    ]

    const months = [
        "января",
        "февраля",
        "марта",
        "апреля",
        "мая",
        "июня",
        "июля",
        "августа",
        "сентября",
        "октября",
        "ноября",
        "декабря"
    ]

    return `${weekdays[date.getDay()]}, ${date.getDate()} ${months[date.getMonth()]}`
}