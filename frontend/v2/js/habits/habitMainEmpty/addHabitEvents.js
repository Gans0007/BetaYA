/* =========================================================
   ADD HABIT EVENTS

   Логика страницы создания и редактирования привычки.

   Отвечает за:
   - создание новой привычки;
   - редактирование существующей привычки;
   - работу с черновиком;
   - выбор названия;
   - выбор цвета;
   - выбор размера;
   - переход к выбору эмодзи;
   - сохранение изменений;
   - возврат с формы.
   ========================================================= */


/* =========================================================
   РЕНДЕР СТРАНИЦ
   ========================================================= */

import {
    renderAddHabitPage
} from "./addHabitPage.js"

import {
    renderIconPickerPage
} from "./iconPickerPage.js"


/* =========================================================
   СОБЫТИЯ ВЫБОРА ЭМОДЗИ
   ========================================================= */

import {
    initIconPickerEvents
} from "./iconPickerEvents.js"


/* =========================================================
   ЧЕРНОВИК ПРИВЫЧКИ
   ========================================================= */

import {
    getHabitDraft,
    getHabitDraftValue,
    setHabitDraftValue,
    updateHabitDraft,
    resetHabitDraft,
    startNewHabitDraft,
    getEditingHabitId,
    isHabitDraftEditing
} from "./habitsDraft.js"


/* =========================================================
   STORE
   ========================================================= */

import {
    addHabit,
    updateHabit
} from "../habitsStore.js"


/* =========================================================
   ОБЩИЕ УТИЛИТЫ
   ========================================================= */

import {
    createHabitId,
    addPressAnimation
} from "../habitsUtils.js"


/* =========================================================
   КОРНЕВОЙ КОНТЕЙНЕР
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
        name:
            nameInput?.value ?? "",

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

   Используется:
   - после открытия страницы;
   - после возвращения со страницы выбора эмодзи;
   - при редактировании существующей привычки.
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
        nameInput.value =
            draft.name
    }


    /* ---------------------------------------------------------
       ИКОНКА
       --------------------------------------------------------- */

    if (selectedIcon) {
        selectedIcon.textContent =
            draft.icon
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
   ПОЛУЧИТЬ ПРОВЕРЕННОЕ НАЗВАНИЕ
   ========================================================= */

function getNormalizedHabitName() {
    return String(
        getHabitDraftValue("name") || ""
    ).trim()
}


/* =========================================================
   СОЗДАТЬ НОВУЮ ПРИВЫЧКУ ИЗ ЧЕРНОВИКА
   ========================================================= */

export function createHabitFromDraft() {
    const draft = getHabitDraft()

    const habitName =
        getNormalizedHabitName()

    if (!habitName) {
        return null
    }

    const newHabit = {
        id:
            createHabitId(),

        name:
            habitName,

        icon:
            draft.icon || "✱",

        color:
            draft.color || "blue",

        size:
            draft.size || "large",

        completedToday:
            false,

        streak:
            0,

        xpReward:
            5,

        weekProgress: [
            false,
            false,
            false,
            false,
            false,
            false,
            false
        ],

        completedDates: [],

        createdAt:
            new Date().toISOString(),

        completedAt:
            null
    }

    return addHabit(
        newHabit
    )
}


/* =========================================================
   ОБНОВИТЬ СУЩЕСТВУЮЩУЮ ПРИВЫЧКУ ИЗ ЧЕРНОВИКА

   Изменяются только:
   - название;
   - иконка;
   - цвет;
   - размер.

   Остальные данные привычки Store сохраняет:
   - серию;
   - XP;
   - календарь;
   - историю подтверждений;
   - дату создания;
   - сегодняшний статус.
   ========================================================= */

export function updateHabitFromDraft() {
    const editingHabitId =
        getEditingHabitId()

    if (!editingHabitId) {
        console.warn(
            "Add Habit Events: отсутствует ID редактируемой привычки"
        )

        return null
    }

    const draft = getHabitDraft()

    const habitName =
        getNormalizedHabitName()

    if (!habitName) {
        return null
    }

    return updateHabit(
        editingHabitId,
        {
            name:
                habitName,

            icon:
                draft.icon || "✱",

            color:
                draft.color || "blue",

            size:
                draft.size || "large"
        }
    )
}


/* =========================================================
   СОХРАНИТЬ ЧЕРНОВИК

   Автоматически определяет режим:

   создание:
   addHabit()

   редактирование:
   updateHabit()
   ========================================================= */

export function saveHabitFromDraft() {
    if (isHabitDraftEditing()) {
        return updateHabitFromDraft()
    }

    return createHabitFromDraft()
}


/* =========================================================
   ОТКРЫТЬ СТРАНИЦУ СОЗДАНИЯ ИЛИ РЕДАКТИРОВАНИЯ

   resetDraft:
   true — начать создание новой привычки;
   false — сохранить текущий черновик.

   onOpenHabitsPage:
   резервный возврат на главную страницу.

   onHabitSaved:
   вызывается после успешного сохранения.

   onCancel:
   вызывается при нажатии стрелки назад.
   ========================================================= */

export function openAddHabitPage({
    resetDraft = false,
    onOpenHabitsPage = null,
    onHabitSaved = null,
    onCancel = null
} = {}) {
    if (resetDraft) {
        startNewHabitDraft()
    }

    renderAddHabitPage()

    restoreDraftToAddHabitPage()

    initAddHabitPageEvents({
        onOpenHabitsPage,
        onHabitSaved,
        onCancel
    })
}


/* =========================================================
   ПОКАЗАТЬ ОШИБКУ ПУСТОГО НАЗВАНИЯ
   ========================================================= */

function showNameValidationError(
    nameInput
) {
    if (!nameInput) {
        return
    }

    const nameField =
        nameInput.closest(
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
        selectedButton.dataset.locked ===
        "true"

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
   ВЕРНУТЬСЯ СО СТРАНИЦЫ ФОРМЫ
   ========================================================= */

function handleAddHabitBack({
    onOpenHabitsPage = null,
    onCancel = null
} = {}) {
    resetHabitDraft()

    if (typeof onCancel === "function") {
        onCancel()
        return
    }

    if (
        typeof onOpenHabitsPage ===
        "function"
    ) {
        onOpenHabitsPage()
        return
    }

    console.warn(
        "Add Habit Events: не передан обработчик возврата"
    )
}


/* =========================================================
   ОБРАБОТАТЬ УСПЕШНОЕ СОХРАНЕНИЕ
   ========================================================= */

function handleHabitSaved(
    savedHabit,
    {
        wasEditing = false,
        onHabitSaved = null,
        onOpenHabitsPage = null
    } = {}
) {
    resetHabitDraft()

    if (
        typeof onHabitSaved ===
        "function"
    ) {
        onHabitSaved(
            savedHabit,
            {
                wasEditing
            }
        )

        return
    }

    if (
        typeof onOpenHabitsPage ===
        "function"
    ) {
        onOpenHabitsPage()
        return
    }

    console.warn(
        "Add Habit Events: привычка сохранена, но не передан обработчик перехода"
    )
}


/* =========================================================
   СОБЫТИЯ СТРАНИЦЫ СОЗДАНИЯ / РЕДАКТИРОВАНИЯ
   ========================================================= */

export function initAddHabitPageEvents({
    onOpenHabitsPage = null,
    onHabitSaved = null,
    onCancel = null
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

    const suggestionButtons =
        root.querySelectorAll(
            "[data-habit-suggestion]"
        )

    const colorButtons =
        root.querySelectorAll(
            "[data-habit-color]"
        )

    const sizeButtons =
        root.querySelectorAll(
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

            const nameField =
                nameInput.closest(
                    ".add-habit-v2__name-field"
                )

            nameField?.classList.remove(
                "has-error"
            )
        }
    )


    /* =====================================================
       ВОЗВРАТ НАЗАД

       При создании:
       возвращаемся на главную страницу.

       При редактировании:
       позже вернёмся в детали привычки через onCancel.
       ===================================================== */

    backButton?.addEventListener(
        "click",
        () => {
            handleAddHabitBack({
                onOpenHabitsPage,
                onCancel
            })
        }
    )


    /* =====================================================
       ОТКРЫТЬ ВЫБОР ЭМОДЗИ

       Сначала сохраняем заполненную форму в черновик.
       Режим редактирования при этом не сбрасывается.
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
                        onOpenHabitsPage,
                        onHabitSaved,
                        onCancel
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
                    button.dataset
                        .habitSuggestion || ""

                nameInput.value =
                    suggestion

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

       Перед сохранением запоминаем режим,
       потому что resetHabitDraft() позже его сбросит.
       ===================================================== */

    saveButton?.addEventListener(
        "click",
        () => {
            updateDraftFromAddHabitPage()

            const habitName =
                getNormalizedHabitName()

            if (!habitName) {
                showNameValidationError(
                    nameInput
                )

                return
            }

            const wasEditing =
                isHabitDraftEditing()

            const savedHabit =
                saveHabitFromDraft()

            if (!savedHabit) {
                console.error(
                    wasEditing
                        ? "Add Habit Events: не удалось обновить привычку"
                        : "Add Habit Events: не удалось создать привычку"
                )

                return
            }

            console.log(
                wasEditing
                    ? "Привычка обновлена:"
                    : "Новая привычка:",
                savedHabit
            )

            handleHabitSaved(
                savedHabit,
                {
                    wasEditing,
                    onHabitSaved,
                    onOpenHabitsPage
                }
            )
        }
    )
}