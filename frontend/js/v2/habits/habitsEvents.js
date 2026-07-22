import { renderHabitsPage } from "./habitsPage.js"
import { renderAddHabitPage } from "./addHabitPage.js"
import { renderIconPickerPage } from "./iconPickerPage.js"


/* =========================================================
   ВРЕМЕННОЕ СОСТОЯНИЕ НОВОЙ ПРИВЫЧКИ
   Пока без API
   ========================================================= */

const habitDraft = {
    name: "",
    icon: "✱",
    color: "blue",
    size: "large"
}


/* =========================================================
   АНИМАЦИЯ НАЖАТИЯ
   Для телефона и компьютера
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
   СБРОС ЧЕРНОВИКА
   ========================================================= */

function resetHabitDraft() {
    habitDraft.name = ""
    habitDraft.icon = "✱"
    habitDraft.color = "blue"
    habitDraft.size = "large"
}


/* =========================================================
   СОХРАНЯЕМ ДАННЫЕ ИЗ ЭКРАНА СОЗДАНИЯ В ЧЕРНОВИК
   ========================================================= */

function updateDraftFromAddHabitPage() {
    const root = document.getElementById("habits-v2-root")

    if (!root) {
        return
    }

    const nameInput = root.querySelector(
        "#add-habit-name"
    )

    const selectedIcon = root.querySelector(
        ".add-habit-v2__selected-icon"
    )

    const selectedColor = root.querySelector(
        "[data-habit-color].is-selected"
    )

    const selectedSize = root.querySelector(
        "[data-habit-size].is-selected"
    )

    if (nameInput) {
        habitDraft.name = nameInput.value
    }

    const iconValue =
        selectedIcon?.textContent?.trim()

    if (iconValue) {
        habitDraft.icon = iconValue
    }

    if (selectedColor?.dataset.habitColor) {
        habitDraft.color =
            selectedColor.dataset.habitColor
    }

    if (selectedSize?.dataset.habitSize) {
        habitDraft.size =
            selectedSize.dataset.habitSize
    }
}


/* =========================================================
   ВОССТАНАВЛИВАЕМ ЧЕРНОВИК НА ЭКРАНЕ СОЗДАНИЯ
   ========================================================= */

function restoreDraftToAddHabitPage() {
    const root = document.getElementById("habits-v2-root")

    if (!root) {
        return
    }

    const nameInput = root.querySelector(
        "#add-habit-name"
    )

    const selectedIcon = root.querySelector(
        ".add-habit-v2__selected-icon"
    )

    const colorButtons = root.querySelectorAll(
        "[data-habit-color]"
    )

    const sizeButtons = root.querySelectorAll(
        "[data-habit-size]"
    )

    if (nameInput) {
        nameInput.value = habitDraft.name
    }

    if (selectedIcon) {
        selectedIcon.textContent = habitDraft.icon
    }

    colorButtons.forEach((button) => {
        const isSelected =
            button.dataset.habitColor === habitDraft.color

        button.classList.toggle(
            "is-selected",
            isSelected
        )

        button.setAttribute(
            "aria-checked",
            String(isSelected)
        )
    })

    sizeButtons.forEach((button) => {
        const isSelected =
            button.dataset.habitSize === habitDraft.size

        button.classList.toggle(
            "is-selected",
            isSelected
        )

        button.setAttribute(
            "aria-pressed",
            String(isSelected)
        )
    })
}


/* =========================================================
   ОТКРЫТИЕ ЭКРАНА СОЗДАНИЯ
   ========================================================= */

function openAddHabitPage() {
    renderAddHabitPage()
    restoreDraftToAddHabitPage()
    initAddHabitPageEvents()
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
        resetHabitDraft()
        openAddHabitPage()
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

    const iconButton = root.querySelector(
        '[data-action="open-icon-picker"]'
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
       АНИМАЦИИ
       --------------------------------------------------------- */

    addPressAnimation(backButton)
    addPressAnimation(saveButton)
    addPressAnimation(iconButton)

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
       НАЗВАНИЕ ПРИВЫЧКИ
       --------------------------------------------------------- */

    nameInput?.addEventListener("input", () => {
        habitDraft.name = nameInput.value
    })


    /* ---------------------------------------------------------
       НАЗАД НА ГЛАВНУЮ СТРАНИЦУ ПРИВЫЧЕК
       --------------------------------------------------------- */

    backButton?.addEventListener("click", () => {
        resetHabitDraft()

        renderHabitsPage()
        initHabitsPageEvents()
    })


    /* ---------------------------------------------------------
       ОТКРЫВАЕМ ВЫБОР ЭМОДЗИ
       --------------------------------------------------------- */

    iconButton?.addEventListener("click", () => {
        updateDraftFromAddHabitPage()

        renderIconPickerPage(habitDraft.icon)
        initIconPickerEvents()
    })


    /* ---------------------------------------------------------
       БЫСТРЫЕ НАЗВАНИЯ
       --------------------------------------------------------- */

    suggestionButtons.forEach((button) => {
        button.addEventListener("click", () => {
            if (!nameInput) {
                return
            }

            const suggestion =
                button.dataset.habitSuggestion || ""

            nameInput.value = suggestion
            habitDraft.name = suggestion

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
            const isLocked =
                button.dataset.locked === "true"

            if (isLocked) {
                console.log(
                    "Этот цвет доступен только с Premium"
                )

                return
            }

            colorButtons.forEach((colorButton) => {
                colorButton.classList.remove(
                    "is-selected"
                )

                colorButton.setAttribute(
                    "aria-checked",
                    "false"
                )
            })

            button.classList.add("is-selected")
            button.setAttribute("aria-checked", "true")

            habitDraft.color =
                button.dataset.habitColor || "blue"
        })
    })


    /* ---------------------------------------------------------
       ВЫБОР РАЗМЕРА
       --------------------------------------------------------- */

    sizeButtons.forEach((button) => {
        button.addEventListener("click", () => {
            sizeButtons.forEach((sizeButton) => {
                sizeButton.classList.remove(
                    "is-selected"
                )

                sizeButton.setAttribute(
                    "aria-pressed",
                    "false"
                )
            })

            button.classList.add("is-selected")
            button.setAttribute("aria-pressed", "true")

            habitDraft.size =
                button.dataset.habitSize || "large"
        })
    })


    /* ---------------------------------------------------------
       СОХРАНЕНИЕ
       Пока без API
       --------------------------------------------------------- */

    saveButton?.addEventListener("click", () => {
        updateDraftFromAddHabitPage()

        const habitName = habitDraft.name.trim()

        if (!habitName) {
            const nameField = nameInput?.closest(
                ".add-habit-v2__name-field"
            )

            nameInput?.focus()
            nameField?.classList.add("has-error")

            window.setTimeout(() => {
                nameField?.classList.remove("has-error")
            }, 450)

            return
        }

        console.log("Новая привычка:", {
            name: habitName,
            icon: habitDraft.icon,
            color: habitDraft.color,
            size: habitDraft.size
        })

        /*
         * Позднее здесь будет запрос:
         *
         * await createHabit({
         *     name: habitName,
         *     icon: habitDraft.icon,
         *     color: habitDraft.color,
         *     size: habitDraft.size
         * })
         */

        resetHabitDraft()

        renderHabitsPage()
        initHabitsPageEvents()
    })
}


/* =========================================================
   ЭКРАН ВЫБОРА ЭМОДЗИ
   ========================================================= */

function initIconPickerEvents() {
    const root = document.getElementById("habits-v2-root")

    if (!root) {
        return
    }

    const backButton = root.querySelector(
        '[data-action="close-icon-picker"]'
    )

    const confirmButton = root.querySelector(
        '[data-action="confirm-habit-icon"]'
    )

    const iconButtons = root.querySelectorAll(
        "[data-habit-icon]"
    )


    /* ---------------------------------------------------------
       АНИМАЦИИ
       --------------------------------------------------------- */

    addPressAnimation(backButton)
    addPressAnimation(confirmButton)

    iconButtons.forEach((button) => {
        addPressAnimation(button)
    })


    /* ---------------------------------------------------------
       СТРЕЛКА НАЗАД
       Выбранное значение сохраняется в черновике
       --------------------------------------------------------- */

    backButton?.addEventListener("click", () => {
        openAddHabitPage()
    })


    /* ---------------------------------------------------------
       ВЫБОР ЭМОДЗИ
       --------------------------------------------------------- */

    iconButtons.forEach((button) => {
        button.addEventListener("click", () => {
            iconButtons.forEach((iconButton) => {
                iconButton.classList.remove(
                    "is-selected"
                )

                iconButton.setAttribute(
                    "aria-pressed",
                    "false"
                )
            })

            button.classList.add("is-selected")
            button.setAttribute("aria-pressed", "true")

            habitDraft.icon =
                button.dataset.habitIcon || "✱"
        })
    })


    /* ---------------------------------------------------------
       ПОДТВЕРЖДАЕМ ВЫБОР
       --------------------------------------------------------- */

    confirmButton?.addEventListener("click", () => {
        openAddHabitPage()
    })
}


/* =========================================================
   ОБЩАЯ ИНИЦИАЛИЗАЦИЯ
   ========================================================= */

export function initHabitsEvents() {
    const iconPickerPage = document.querySelector(
        ".habit-icon-picker"
    )

    if (iconPickerPage) {
        initIconPickerEvents()
        return
    }

    const addHabitPage = document.querySelector(
        ".add-habit-v2"
    )

    if (addHabitPage) {
        restoreDraftToAddHabitPage()
        initAddHabitPageEvents()
        return
    }

    initHabitsPageEvents()
}