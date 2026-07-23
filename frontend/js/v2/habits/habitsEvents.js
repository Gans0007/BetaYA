import { renderHabitsPage } from "./habitsPage.js"
import { renderAddHabitPage } from "./addHabitPage.js"
import { renderIconPickerPage } from "./iconPickerPage.js"


/* =========================================================
   ВРЕМЕННОЕ ХРАНИЛИЩЕ ПРИВЫЧЕК
   Позже будет заменено запросами к API
   ========================================================= */

const habits = []


/* =========================================================
   ЧЕРНОВИК НОВОЙ ПРИВЫЧКИ
   ========================================================= */

const habitDraft = {
    name: "",
    icon: "✱",
    color: "blue",
    size: "large"
}


/* =========================================================
   СОЗДАНИЕ ID
   ========================================================= */

function createHabitId() {
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
   СОХРАНЯЕМ ДАННЫЕ ФОРМЫ В ЧЕРНОВИК
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
   ВОССТАНАВЛИВАЕМ ЧЕРНОВИК В ФОРМЕ
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
            button.dataset.habitColor ===
            habitDraft.color

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
            button.dataset.habitSize ===
            habitDraft.size

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
   РЕНДЕР ГЛАВНОЙ СТРАНИЦЫ
   ========================================================= */

function openHabitsPage() {
    renderHabitsPage(habits)
    initHabitsPageEvents()
}


/* =========================================================
   ОТКРЫТИЕ СТРАНИЦЫ СОЗДАНИЯ
   ========================================================= */

function openAddHabitPage({
    resetDraft = false
} = {}) {
    if (resetDraft) {
        resetHabitDraft()
    }

    renderAddHabitPage()
    restoreDraftToAddHabitPage()
    initAddHabitPageEvents()
}


/* =========================================================
   СОЗДАНИЕ ПРИВЫЧКИ
   ========================================================= */

function createHabitFromDraft() {
    const habitName = habitDraft.name.trim()

    if (!habitName) {
        return null
    }

    const newHabit = {
        id: createHabitId(),
        name: habitName,
        icon: habitDraft.icon,
        color: habitDraft.color,
        size: habitDraft.size,
        createdAt: new Date().toISOString()
    }

    habits.push(newHabit)

    return newHabit
}


/* =========================================================
   СОБЫТИЯ ГЛАВНОЙ СТРАНИЦЫ
   ========================================================= */

function initHabitsPageEvents() {
    const root = document.getElementById("habits-v2-root")

    if (!root) {
        return
    }

    const addButtons = root.querySelectorAll(
        '[data-action="open-add-habit"], .habits-v2-empty__add-button'
    )

    addButtons.forEach((button) => {
        addPressAnimation(button)

        button.addEventListener("click", () => {
            openAddHabitPage({
                resetDraft: true
            })
        })
    })

    initHabitCardEvents()
}


/* =========================================================
   СОБЫТИЯ КАРТОЧЕК
   Пока только базовая заготовка
   ========================================================= */

function initHabitCardEvents() {
    const root = document.getElementById("habits-v2-root")

    if (!root) {
        return
    }

    const habitCards = root.querySelectorAll(
        "[data-habit-id]"
    )

    habitCards.forEach((card) => {
        addPressAnimation(card)

        card.addEventListener("click", () => {
            const habitId =
                card.dataset.habitId

            const selectedHabit = habits.find(
                (habit) => habit.id === habitId
            )

            if (!selectedHabit) {
                return
            }

            console.log(
                "Выбрана привычка:",
                selectedHabit
            )

            /*
             * Позже здесь будет открываться:
             * страница привычки,
             * меню привычки
             * или подтверждение выполнения.
             */
        })
    })
}


/* =========================================================
   СОБЫТИЯ СТРАНИЦЫ СОЗДАНИЯ
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

        const nameField = nameInput.closest(
            ".add-habit-v2__name-field"
        )

        nameField?.classList.remove("has-error")
    })


    /* ---------------------------------------------------------
       ВОЗВРАТ НА ГЛАВНУЮ
       --------------------------------------------------------- */

    backButton?.addEventListener("click", () => {
        resetHabitDraft()
        openHabitsPage()
    })


    /* ---------------------------------------------------------
       ОТКРЫТИЕ ВЫБОРА ИКОНКИ
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

            button.setAttribute(
                "aria-checked",
                "true"
            )

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

            button.setAttribute(
                "aria-pressed",
                "true"
            )

            habitDraft.size =
                button.dataset.habitSize || "large"
        })
    })


    /* ---------------------------------------------------------
       СОХРАНЕНИЕ ПРИВЫЧКИ
       --------------------------------------------------------- */

    saveButton?.addEventListener("click", () => {
        updateDraftFromAddHabitPage()

        const habitName =
            habitDraft.name.trim()

        if (!habitName) {
            const nameField = nameInput?.closest(
                ".add-habit-v2__name-field"
            )

            nameInput?.focus()
            nameField?.classList.add("has-error")

            window.setTimeout(() => {
                nameField?.classList.remove(
                    "has-error"
                )
            }, 450)

            return
        }

        const newHabit =
            createHabitFromDraft()

        if (!newHabit) {
            return
        }

        console.log(
            "Новая привычка:",
            newHabit
        )

        /*
         * Позже этот участок заменим на:
         *
         * const newHabit = await createHabit({
         *     name: habitName,
         *     icon: habitDraft.icon,
         *     color: habitDraft.color,
         *     size: habitDraft.size
         * })
         */

        resetHabitDraft()
        openHabitsPage()
    })
}


/* =========================================================
   СОБЫТИЯ ВЫБОРА ИКОНКИ
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
       ВОЗВРАТ В ФОРМУ
       --------------------------------------------------------- */

    backButton?.addEventListener("click", () => {
        openAddHabitPage()
    })


    /* ---------------------------------------------------------
       ВЫБОР ИКОНКИ
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

            button.setAttribute(
                "aria-pressed",
                "true"
            )

            habitDraft.icon =
                button.dataset.habitIcon || "✱"
        })
    })


    /* ---------------------------------------------------------
       ПОДТВЕРЖДЕНИЕ ИКОНКИ
       --------------------------------------------------------- */

    confirmButton?.addEventListener("click", () => {
        openAddHabitPage()
    })
}


/* =========================================================
   ОБЩАЯ ИНИЦИАЛИЗАЦИЯ
   ========================================================= */

export function initHabitsEvents() {
    const root = document.getElementById("habits-v2-root")

    if (!root) {
        return
    }

    const iconPickerPage = root.querySelector(
        ".habit-icon-picker"
    )

    if (iconPickerPage) {
        initIconPickerEvents()
        return
    }

    const addHabitPage = root.querySelector(
        ".add-habit-v2"
    )

    if (addHabitPage) {
        restoreDraftToAddHabitPage()
        initAddHabitPageEvents()
        return
    }

    /*
     * При первом открытии страницы передаём
     * текущий массив привычек.
     */

    renderHabitsPage(habits)
    initHabitsPageEvents()
}