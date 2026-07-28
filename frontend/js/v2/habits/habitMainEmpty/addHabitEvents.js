/* =========================================================
   HABITS EVENTS

   Главный контроллер раздела привычек.

   Отвечает за:
   - первоначальный запуск раздела;
   - рендер главной страницы;
   - открытие страницы создания привычки;
   - события карточек привычек;
   - подтверждение выполнения;
   - открытие деталей привычки;
   - восстановление прокрутки списка.

   Логика создания привычки находится отдельно:
   habitMainEmpty/addHabitEvents.js
   ========================================================= */

import {
    renderAddHabitPage
} from "./addHabitPage.js"

import {
    renderIconPickerPage
} from "./iconPickerPage.js"

import {
    initIconPickerEvents
} from "./iconPickerEvents.js"

import {
    getHabitDraft,
    getHabitDraftValue,
    setHabitDraftValue,
    updateHabitDraft,
    resetHabitDraft
} from "./habitsDraft.js"

import {
    addHabit
} from "../habitsStore.js"

import {
    createHabitId,
    addPressAnimation
} from "../habitsUtils.js"


/* =========================================================
   КОНТЕЙНЕР РАЗДЕЛА
   ========================================================= */

function getHabitsRoot() {
    return document.getElementById(
        "habits-v2-root"
    )
}


/* =========================================================
   СОХРАНИТЬ ДАННЫЕ ФОРМЫ В ЧЕРНОВИК

   Используется перед:
   - переходом к выбору эмодзи;
   - окончательным сохранением привычки.
   ========================================================= */

export function updateDraftFromAddHabitPage() {
    const root = getHabitsRoot()

    if (!root) {
        console.warn(
            "Add Habit Events: не найден #habits-v2-root"
        )

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

    const iconValue =
        selectedIcon?.textContent?.trim()

    updateHabitDraft({
        name: nameInput?.value ?? "",

        icon:
            iconValue ||
            getHabitDraftValue("icon"),

        color:
            selectedColor?.dataset.habitColor ||
            getHabitDraftValue("color"),

        size:
            selectedSize?.dataset.habitSize ||
            getHabitDraftValue("size")
    })
}


/* =========================================================
   ВОССТАНОВИТЬ ЧЕРНОВИК В ФОРМЕ

   Используется после возвращения со страницы выбора эмодзи.
   ========================================================= */

export function restoreDraftToAddHabitPage() {
    const root = getHabitsRoot()

    if (!root) {
        console.warn(
            "Add Habit Events: не найден #habits-v2-root"
        )

        return
    }

    const draft = getHabitDraft()

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


    /* ---------------------------------------------------------
       НАЗВАНИЕ
       --------------------------------------------------------- */

    if (nameInput) {
        nameInput.value = draft.name
    }


    /* ---------------------------------------------------------
       ИКОНКА
       --------------------------------------------------------- */

    if (selectedIcon) {
        selectedIcon.textContent = draft.icon
    }


    /* ---------------------------------------------------------
       ЦВЕТ
       --------------------------------------------------------- */

    colorButtons.forEach((button) => {
        const isSelected =
            button.dataset.habitColor ===
            draft.color

        button.classList.toggle(
            "is-selected",
            isSelected
        )

        button.setAttribute(
            "aria-checked",
            String(isSelected)
        )
    })


    /* ---------------------------------------------------------
       РАЗМЕР
       --------------------------------------------------------- */

    sizeButtons.forEach((button) => {
        const isSelected =
            button.dataset.habitSize ===
            draft.size

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
   СОЗДАТЬ ПРИВЫЧКУ ИЗ ЧЕРНОВИКА
   ========================================================= */

export function createHabitFromDraft() {
    const draft = getHabitDraft()

    const habitName = String(
        draft.name || ""
    ).trim()

    if (!habitName) {
        return null
    }

    const newHabit = {
        id: createHabitId(),

        name: habitName,
        icon: draft.icon || "✱",
        color: draft.color || "blue",
        size: draft.size || "large",

        completedToday: false,
        streak: 0,
        xpReward: 5,

        weekProgress: [
            false,
            false,
            false,
            false,
            false,
            false,
            false
        ],

        createdAt: new Date().toISOString(),
        completedAt: null
    }

    return addHabit(newHabit)
}


/* =========================================================
   ОТКРЫТЬ СТРАНИЦУ СОЗДАНИЯ ПРИВЫЧКИ

   resetDraft:
   true  — пользователь создаёт новую привычку;
   false — пользователь вернулся со страницы эмодзи.

   onOpenHabitsPage:
   функция возврата на главную страницу привычек.
   ========================================================= */

export function openAddHabitPage({
    resetDraft = false,
    onOpenHabitsPage = null
} = {}) {
    if (resetDraft) {
        resetHabitDraft()
    }

    renderAddHabitPage()
    restoreDraftToAddHabitPage()

    initAddHabitPageEvents({
        onOpenHabitsPage
    })
}


/* =========================================================
   ПОКАЗАТЬ ОШИБКУ ПУСТОГО НАЗВАНИЯ
   ========================================================= */

function showNameValidationError(nameInput) {
    if (!nameInput) {
        return
    }

    const nameField = nameInput.closest(
        ".add-habit-v2__name-field"
    )

    nameInput.focus()

    nameField?.classList.add(
        "has-error"
    )

    window.setTimeout(() => {
        nameField?.classList.remove(
            "has-error"
        )
    }, 450)
}


/* =========================================================
   ВЫБРАТЬ ЦВЕТ
   ========================================================= */

function selectHabitColor(
    selectedButton,
    colorButtons
) {
    const isLocked =
        selectedButton.dataset.locked === "true"

    if (isLocked) {
        console.log(
            "Этот цвет доступен только с Premium"
        )

        return
    }

    colorButtons.forEach((button) => {
        button.classList.remove(
            "is-selected"
        )

        button.setAttribute(
            "aria-checked",
            "false"
        )
    })

    selectedButton.classList.add(
        "is-selected"
    )

    selectedButton.setAttribute(
        "aria-checked",
        "true"
    )

    setHabitDraftValue(
        "color",
        selectedButton.dataset.habitColor ||
            "blue"
    )
}


/* =========================================================
   ВЫБРАТЬ РАЗМЕР
   ========================================================= */

function selectHabitSize(
    selectedButton,
    sizeButtons
) {
    sizeButtons.forEach((button) => {
        button.classList.remove(
            "is-selected"
        )

        button.setAttribute(
            "aria-pressed",
            "false"
        )
    })

    selectedButton.classList.add(
        "is-selected"
    )

    selectedButton.setAttribute(
        "aria-pressed",
        "true"
    )

    setHabitDraftValue(
        "size",
        selectedButton.dataset.habitSize ||
            "large"
    )
}


/* =========================================================
   СОБЫТИЯ СТРАНИЦЫ СОЗДАНИЯ
   ========================================================= */

export function initAddHabitPageEvents({
    onOpenHabitsPage = null
} = {}) {
    const root = getHabitsRoot()

    if (!root) {
        console.warn(
            "Add Habit Events: не найден #habits-v2-root"
        )

        return
    }


    /* =====================================================
       ЭЛЕМЕНТЫ
       ===================================================== */

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


    /* =====================================================
       АНИМАЦИИ НАЖАТИЯ
       ===================================================== */

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


    /* =====================================================
       ВВОД НАЗВАНИЯ
       ===================================================== */

    nameInput?.addEventListener(
        "input",
        () => {
            setHabitDraftValue(
                "name",
                nameInput.value
            )

            const nameField = nameInput.closest(
                ".add-habit-v2__name-field"
            )

            nameField?.classList.remove(
                "has-error"
            )
        }
    )


    /* =====================================================
       ВОЗВРАТ НА ГЛАВНУЮ

       При выходе со страницы создания черновик удаляется.
       ===================================================== */

    backButton?.addEventListener(
        "click",
        () => {
            resetHabitDraft()

            if (
                typeof onOpenHabitsPage ===
                "function"
            ) {
                onOpenHabitsPage()
                return
            }

            console.warn(
                "Add Habit Events: не передан onOpenHabitsPage"
            )
        }
    )


    /* =====================================================
       ОТКРЫТЬ ВЫБОР ЭМОДЗИ

       Сначала сохраняем заполненную форму в черновик.
       ===================================================== */

    iconButton?.addEventListener(
        "click",
        () => {
            updateDraftFromAddHabitPage()

            renderIconPickerPage(
                getHabitDraftValue("icon")
            )

            initIconPickerEvents({
                onBackToAddHabitPage: () => {
                    openAddHabitPage({
                        resetDraft: false,
                        onOpenHabitsPage
                    })
                }
            })
        }
    )


    /* =====================================================
       БЫСТРЫЕ ВАРИАНТЫ НАЗВАНИЯ
       ===================================================== */

    suggestionButtons.forEach((button) => {
        button.addEventListener(
            "click",
            () => {
                if (!nameInput) {
                    return
                }

                const suggestion =
                    button.dataset.habitSuggestion ||
                    ""

                nameInput.value = suggestion

                setHabitDraftValue(
                    "name",
                    suggestion
                )

                nameInput.focus()

                nameInput.dispatchEvent(
                    new Event(
                        "input",
                        {
                            bubbles: true
                        }
                    )
                )
            }
        )
    })


    /* =====================================================
       ВЫБОР ЦВЕТА
       ===================================================== */

    colorButtons.forEach((button) => {
        button.addEventListener(
            "click",
            () => {
                selectHabitColor(
                    button,
                    colorButtons
                )
            }
        )
    })


    /* =====================================================
       ВЫБОР РАЗМЕРА
       ===================================================== */

    sizeButtons.forEach((button) => {
        button.addEventListener(
            "click",
            () => {
                selectHabitSize(
                    button,
                    sizeButtons
                )
            }
        )
    })


    /* =====================================================
       СОХРАНЕНИЕ ПРИВЫЧКИ
       ===================================================== */

    saveButton?.addEventListener(
        "click",
        () => {
            updateDraftFromAddHabitPage()

            const habitName = String(
                getHabitDraftValue("name") ||
                ""
            ).trim()

            if (!habitName) {
                showNameValidationError(
                    nameInput
                )

                return
            }

            const newHabit =
                createHabitFromDraft()

            if (!newHabit) {
                console.error(
                    "Add Habit Events: не удалось создать привычку"
                )

                return
            }

            console.log(
                "Новая привычка:",
                newHabit
            )

            resetHabitDraft()

            if (
                typeof onOpenHabitsPage ===
                "function"
            ) {
                onOpenHabitsPage()
                return
            }

            console.warn(
                "Add Habit Events: привычка создана, но не передан onOpenHabitsPage"
            )
        }
    )
}