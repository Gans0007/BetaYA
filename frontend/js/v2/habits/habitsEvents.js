import { renderHabitsPage } from "./habitsPage.js"
import { renderAddHabitPage } from "./addHabitPage.js"
import { renderIconPickerPage } from "./iconPickerPage.js"
import { renderHabitDetailsPage } from "./habitDetailsPage.js"

import {
    getHabitDraft,
    getHabitDraftValue,
    setHabitDraftValue,
    updateHabitDraft,
    resetHabitDraft
} from "./habitsDraft.js"

import {
    getHabits,
    getHabitById,
    getHabitsStatistics,
    addHabit,
    updateHabit,
    selectHabit,
    setHabitsStatistics
} from "./habitsStore.js"

import {
    createHabitId,
    addPressAnimation
} from "./habitsUtils.js"

/* =========================================================
   СОХРАНЯЕМ ДАННЫЕ ФОРМЫ В ЧЕРНОВИК
   ========================================================= */

function updateDraftFromAddHabitPage() {
    const root = document.getElementById(
        "habits-v2-root"
    )

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
   ВОССТАНАВЛИВАЕМ ЧЕРНОВИК В ФОРМЕ
   ========================================================= */

function restoreDraftToAddHabitPage() {
    const root = document.getElementById(
        "habits-v2-root"
    )

    if (!root) {
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

    if (nameInput) {
        nameInput.value = draft.name
    }

    if (selectedIcon) {
        selectedIcon.textContent = draft.icon
    }

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
   РЕНДЕР ГЛАВНОЙ СТРАНИЦЫ

   preserveScroll:
   true  — сохраняет текущее положение прокрутки;
   false — открывает страницу с самого верха.
   ========================================================= */

function openHabitsPage({
    preserveScroll = false
} = {}) {
    const currentList = document.querySelector(
        ".habits-v2-list"
    )

    const savedScrollTop = preserveScroll
        ? currentList?.scrollTop || 0
        : 0

    renderHabitsPage(
        getHabits(),
        getHabitsStatistics()
    )

    initHabitsPageEvents()

    if (!preserveScroll) {
        return
    }

    const renderedList = document.querySelector(
        ".habits-v2-list"
    )

    if (!renderedList) {
        return
    }

    requestAnimationFrame(() => {
        renderedList.scrollTop = savedScrollTop
    })
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
    const draft = getHabitDraft()
    const habitName = draft.name.trim()

    if (!habitName) {
        return null
    }

const newHabit = {
    id: createHabitId(),
    name: habitName,
    icon: draft.icon,
    color: draft.color,
    size: draft.size,

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

    createdAt: new Date().toISOString()
}
    return addHabit(newHabit)
}


/* =========================================================
   СОБЫТИЯ ГЛАВНОЙ СТРАНИЦЫ
   ========================================================= */

function initHabitsPageEvents() {
    const root = document.getElementById(
        "habits-v2-root"
    )

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
   ИНДЕКС СЕГОДНЯШНЕГО ДНЯ В НЕДЕЛЕ

   Массив прогресса строится так:
   0 — понедельник
   1 — вторник
   2 — среда
   3 — четверг
   4 — пятница
   5 — суббота
   6 — воскресенье
   ========================================================= */

function getTodayWeekIndex() {
    const nativeDayIndex = new Date().getDay()

    return nativeDayIndex === 0
        ? 6
        : nativeDayIndex - 1
}

/* =========================================================
   ЛОКАЛЬНОЕ ПЕРЕКЛЮЧЕНИЕ ВЫПОЛНЕНИЯ ПРИВЫЧКИ

   Первое нажатие:
   - подтверждает привычку;
   - добавляет XP;
   - увеличивает серию;
   - отмечает сегодняшний день.

   Повторное нажатие:
   - снимает подтверждение;
   - возвращает XP;
   - уменьшает серию;
   - снимает отметку сегодняшнего дня.
   ========================================================= */

function toggleHabitConfirmationLocally(habitId) {
    const habit = getHabitById(habitId)

    if (!habit) {
        return null
    }

    const wasCompleted = Boolean(
        habit.completedToday
    )

    const xpReward = Math.max(
        0,
        Math.floor(Number(habit.xpReward) || 5)
    )

    const currentStreak = Math.max(
        0,
        Math.floor(Number(habit.streak) || 0)
    )

    const nextStreak = wasCompleted
        ? Math.max(0, currentStreak - 1)
        : currentStreak + 1

    const weekProgress = Array.from(
        {
            length: 7
        },
        (_, index) => Boolean(
            habit.weekProgress?.[index]
        )
    )

    weekProgress[getTodayWeekIndex()] =
        !wasCompleted

    const updatedHabit = updateHabit(
        habitId,
        {
            completedToday: !wasCompleted,
            streak: nextStreak,
            weekProgress,

            completedAt: wasCompleted
                ? null
                : new Date().toISOString()
        }
    )

    if (!updatedHabit) {
        return null
    }

    const statistics = getHabitsStatistics()

    const currentTotalXp = Math.max(
        0,
        Math.floor(
            Number(statistics.totalXp) || 0
        )
    )

    const nextTotalXp = wasCompleted
        ? Math.max(
            0,
            currentTotalXp - xpReward
        )
        : currentTotalXp + xpReward

    const highestHabitStreak = getHabits()
        .reduce((highestStreak, storedHabit) => {
            const storedStreak = Math.max(
                0,
                Math.floor(
                    Number(storedHabit.streak) || 0
                )
            )

            return Math.max(
                highestStreak,
                storedStreak
            )
        }, 0)

    setHabitsStatistics({
        totalXp: nextTotalXp,
        currentStreak: highestHabitStreak
    })

    return updatedHabit
}

/* =========================================================
   ПОЛОЖЕНИЕ СПИСКА ПЕРЕД ОТКРЫТИЕМ ПРИВЫЧКИ
   ========================================================= */

let habitsListScrollTop = 0

/* =========================================================
   СОБЫТИЯ КАРТОЧЕК
   ========================================================= */

function initHabitCardEvents() {
    const root = document.getElementById(
        "habits-v2-root"
    )

    if (!root) {
        return
    }

    const habitCards = root.querySelectorAll(
        ".habit-card[data-habit-id]"
    )

    habitCards.forEach((card) => {
        const habitId =
            card.dataset.habitId

        const confirmButton = card.querySelector(
            '[data-action="confirm-habit"]'
        )


        /* -----------------------------------------------------
           НЕ ДАЁМ НАЖАТИЮ НА ГАЛОЧКУ ДОЙТИ ДО КАРТОЧКИ
           ----------------------------------------------------- */

        const stopConfirmEvent = (event) => {
            event.stopPropagation()
        }

        confirmButton?.addEventListener(
            "pointerdown",
            stopConfirmEvent
        )

        confirmButton?.addEventListener(
            "pointerup",
            stopConfirmEvent
        )

        confirmButton?.addEventListener(
            "touchstart",
            stopConfirmEvent,
            {
                passive: true
            }
        )

        confirmButton?.addEventListener(
            "touchend",
            stopConfirmEvent,
            {
                passive: true
            }
        )


        /* -----------------------------------------------------
           АНИМАЦИИ
           ----------------------------------------------------- */

        addPressAnimation(card)
        addPressAnimation(confirmButton)


        /* -----------------------------------------------------
           ОТКРЫТИЕ ПРИВЫЧКИ
           ----------------------------------------------------- */

card.addEventListener(
    "click",
    (event) => {
        const clickedConfirmButton =
            event.target.closest(
                '[data-action="confirm-habit"]'
            )

        if (clickedConfirmButton) {
            return
        }

        const selectedHabit =
            selectHabit(habitId)

        if (!selectedHabit) {
            return
        }

        const currentList =
            document.querySelector(
                ".habits-v2-list"
            )

        habitsListScrollTop =
            currentList?.scrollTop || 0

        renderHabitDetailsPage(
            selectedHabit
        )

        initHabitDetailsEvents()
    }
)

        /* -----------------------------------------------------
           ПЕРЕКЛЮЧЕНИЕ ВЫПОЛНЕНИЯ
           ----------------------------------------------------- */

        confirmButton?.addEventListener(
            "click",
            (event) => {
                event.preventDefault()
                event.stopPropagation()

                const updatedHabit =
                    toggleHabitConfirmationLocally(
                        habitId
                    )

                if (!updatedHabit) {
                    return
                }

                openHabitsPage({
                    preserveScroll: true
                })
            }
        )
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
        setHabitDraftValue(
            "name",
            nameInput.value
        )

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

        renderIconPickerPage(
            getHabitDraftValue("icon")
        )
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
            setHabitDraftValue(
                "name",
                suggestion
            )

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

            setHabitDraftValue(
                "color",
                button.dataset.habitColor || "blue"
            )
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

            setHabitDraftValue(
                "size",
                button.dataset.habitSize || "large"
            )
        })
    })


    /* ---------------------------------------------------------
       СОХРАНЕНИЕ ПРИВЫЧКИ
       --------------------------------------------------------- */

    saveButton?.addEventListener("click", () => {
        updateDraftFromAddHabitPage()

        const habitName =
            getHabitDraftValue("name").trim()

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

        resetHabitDraft()
        openHabitsPage()
    })
}


function initIconPickerEvents() {
    const root = document.getElementById(
        "habits-v2-root"
    )

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
       ВРЕМЕННО ВЫБРАННАЯ ИКОНКА

       Она не записывается в черновик, пока пользователь
       не нажмёт кнопку «Выбрать».
       --------------------------------------------------------- */

    let pendingIcon =
        getHabitDraftValue("icon")


    /* ---------------------------------------------------------
       АНИМАЦИИ
       --------------------------------------------------------- */

    addPressAnimation(backButton)
    addPressAnimation(confirmButton)

    iconButtons.forEach((button) => {
        addPressAnimation(button)
    })


    /* ---------------------------------------------------------
       ВОЗВРАТ БЕЗ СОХРАНЕНИЯ
       --------------------------------------------------------- */

    backButton?.addEventListener("click", () => {
        openAddHabitPage()
    })


    /* ---------------------------------------------------------
       ВРЕМЕННЫЙ ВЫБОР ИКОНКИ
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

            pendingIcon =
                button.dataset.habitIcon || "✱"
        })
    })


    /* ---------------------------------------------------------
       ПОДТВЕРЖДЕНИЕ ИКОНКИ
       Только здесь записываем её в черновик.
       --------------------------------------------------------- */

    confirmButton?.addEventListener("click", () => {
        setHabitDraftValue(
            "icon",
            pendingIcon
        )

        openAddHabitPage()
    })
}

/* =========================================================
   СОБЫТИЯ ДЕТАЛЬНОЙ СТРАНИЦЫ
   ========================================================= */

function initHabitDetailsEvents() {
    const root = document.getElementById(
        "habits-v2-root"
    )

    if (!root) {
        return
    }

    const backButton = root.querySelector(
        '[data-action="close-habit-details"]'
    )

    const menuButton = root.querySelector(
        '[data-action="open-habit-menu"]'
    )

    addPressAnimation(backButton)
    addPressAnimation(menuButton)

    backButton?.addEventListener("click", () => {
        openHabitsPage()

        const renderedList = document.querySelector(
            ".habits-v2-list"
        )

        if (!renderedList) {
            return
        }

        requestAnimationFrame(() => {
            renderedList.scrollTop =
                habitsListScrollTop
        })
    })

    menuButton?.addEventListener("click", () => {
        console.log(
            "Открыть меню привычки"
        )
    })
}

/* =========================================================
   ОБЩАЯ ИНИЦИАЛИЗАЦИЯ
   ========================================================= */

export function initHabitsEvents() {
    const root = document.getElementById(
        "habits-v2-root"
    )

    if (!root) {
        return
    }

    const habitDetailsPage = root.querySelector(
        ".habit-details"
    )

    if (habitDetailsPage) {
        initHabitDetailsEvents()
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

    renderHabitsPage(
        getHabits(),
        getHabitsStatistics()
    )

    initHabitsPageEvents()
    }