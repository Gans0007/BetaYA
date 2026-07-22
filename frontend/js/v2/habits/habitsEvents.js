import { renderHabitsPage } from "./habitsPage.js"
import { renderAddHabitPage } from "./addHabitPage.js"


/* =========================================================
   ОБЩАЯ АНИМАЦИЯ НАЖАТИЯ
   ========================================================= */

function addPressAnimation(element) {
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

    element.addEventListener("pointerdown", press)
    element.addEventListener("pointerup", release)
    element.addEventListener("pointercancel", release)
    element.addEventListener("pointerleave", release)

    element.addEventListener("touchstart", press, {
        passive: true
    })

    element.addEventListener("touchend", release, {
        passive: true
    })

    element.addEventListener("touchcancel", release, {
        passive: true
    })
}


/* =========================================================
   ГЛАВНАЯ СТРАНИЦА ПРИВЫЧЕК
   ========================================================= */

function initHabitsPageEvents() {
    const addButton = document.querySelector(
        ".habits-v2-empty__add-button"
    )

    if (!addButton) {
        return
    }

    addPressAnimation(addButton)

    addButton.addEventListener("click", () => {
        renderAddHabitPage()
        initAddHabitPageEvents()
    })
}


/* =========================================================
   ЭКРАН СОЗДАНИЯ ПРИВЫЧКИ
   ========================================================= */

function initAddHabitPageEvents() {
    const root = document.getElementById("habits-v2-root")

    if (!root) {
        return
    }

    const backButton = root.querySelector(
        '[data-action="close-add-habit"]'
    )

    const saveButton = root.querySelector(
        '[data-action="save-habit"]'
    )

    const nameInput = root.querySelector(
        "#add-habit-name"
    )

    const suggestionButtons = root.querySelectorAll(
        "[data-habit-suggestion]"
    )

    const colorButtons = root.querySelectorAll(
        "[data-habit-color]"
    )

    const sizeButtons = root.querySelectorAll(
        "[data-habit-size]"
    )


    /* ---------------------------------------------------------
       АНИМАЦИИ НАЖАТИЙ
       --------------------------------------------------------- */

    addPressAnimation(backButton)
    addPressAnimation(saveButton)

    suggestionButtons.forEach((button) => {
        addPressAnimation(button)
    })

    colorButtons.forEach((button) => {
        addPressAnimation(button)
    })

    sizeButtons.forEach((button) => {
        addPressAnimation(button)
    })


    /* ---------------------------------------------------------
       КНОПКА НАЗАД
       --------------------------------------------------------- */

    backButton?.addEventListener("click", () => {
        renderHabitsPage()
        initHabitsPageEvents()
    })


    /* ---------------------------------------------------------
       БЫСТРЫЕ НАЗВАНИЯ
       --------------------------------------------------------- */

    suggestionButtons.forEach((button) => {
        button.addEventListener("click", () => {
            if (!nameInput) {
                return
            }

            nameInput.value = button.dataset.habitSuggestion || ""
            nameInput.focus()

            nameInput.dispatchEvent(
                new Event("input", {
                    bubbles: true
                })
            )
        })
    })


    /* ---------------------------------------------------------
       ВЫБОР ЦВЕТА
       --------------------------------------------------------- */

    colorButtons.forEach((button) => {
        button.addEventListener("click", () => {
            const isLocked = button.dataset.locked === "true"

            if (isLocked) {
                console.log("Этот цвет доступен только с Premium")
                return
            }

            colorButtons.forEach((colorButton) => {
                colorButton.classList.remove("is-selected")
                colorButton.setAttribute("aria-checked", "false")
            })

            button.classList.add("is-selected")
            button.setAttribute("aria-checked", "true")
        })
    })


    /* ---------------------------------------------------------
       ВЫБОР РАЗМЕРА КАРТОЧКИ
       --------------------------------------------------------- */

    sizeButtons.forEach((button) => {
        button.addEventListener("click", () => {
            sizeButtons.forEach((sizeButton) => {
                sizeButton.classList.remove("is-selected")
                sizeButton.setAttribute("aria-pressed", "false")
            })

            button.classList.add("is-selected")
            button.setAttribute("aria-pressed", "true")
        })
    })


    /* ---------------------------------------------------------
       КНОПКА СОХРАНЕНИЯ
       Пока без API
       --------------------------------------------------------- */

    saveButton?.addEventListener("click", () => {
        const habitName = nameInput?.value.trim() || ""

        const selectedColor = root.querySelector(
            "[data-habit-color].is-selected"
        )?.dataset.habitColor || "blue"

        const selectedSize = root.querySelector(
            "[data-habit-size].is-selected"
        )?.dataset.habitSize || "large"

        if (!habitName) {
            nameInput?.focus()
            nameInput?.closest(
                ".add-habit-v2__name-field"
            )?.classList.add("has-error")

            window.setTimeout(() => {
                nameInput?.closest(
                    ".add-habit-v2__name-field"
                )?.classList.remove("has-error")
            }, 450)

            return
        }

        console.log("Новая привычка:", {
            name: habitName,
            color: selectedColor,
            size: selectedSize
        })

        /*
         * Пока API не подключён.
         * После нажатия возвращаемся на главную страницу.
         */

        renderHabitsPage()
        initHabitsPageEvents()
    })
}


/* =========================================================
   ОБЩАЯ ИНИЦИАЛИЗАЦИЯ
   ========================================================= */

export function initHabitsEvents() {
    const addHabitPage = document.querySelector(".add-habit-v2")

    if (addHabitPage) {
        initAddHabitPageEvents()
        return
    }

    initHabitsPageEvents()
}