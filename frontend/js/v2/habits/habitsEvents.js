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


/* =========================================================
   РЕНДЕР ГЛАВНОЙ СТРАНИЦЫ
   ========================================================= */

import {
    renderHabitsPage
} from "./habitsPage.js"


/* =========================================================
   СТРАНИЦА СОЗДАНИЯ ПРИВЫЧКИ
   ========================================================= */

import {
    openAddHabitPage,
    restoreDraftToAddHabitPage,
    initAddHabitPageEvents
} from "./habitMainEmpty/addHabitEvents.js"


/* =========================================================
   ПРОСМОТР ДЕТАЛЕЙ ПРИВЫЧКИ
   ========================================================= */

import {
    renderHabitDetailsPage
} from "./viewHabitDetails/habitDetailsPage.js"

import {
    initHabitDetailsEvents
} from "./viewHabitDetails/habitDetailsEvents.js"


/* =========================================================
   STORE
   ========================================================= */

import {
    getHabits,
    getHabitById,
    getHabitsStatistics,
    updateHabit,
    selectHabit,
    setHabitsStatistics
} from "./habitsStore.js"


/* =========================================================
   ОБЩИЕ ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ
   ========================================================= */

import {
    addPressAnimation
} from "./habitsUtils.js"


/* =========================================================
   ПОЛОЖЕНИЕ СПИСКА

   Запоминаем прокрутку перед открытием деталей привычки,
   чтобы после возврата пользователь оказался на прежнем месте.
   ========================================================= */

let habitsListScrollTop = 0


/* =========================================================
   ПОЛУЧИТЬ КОРНЕВОЙ КОНТЕЙНЕР
   ========================================================= */

function getHabitsRoot() {
    return document.getElementById(
        "habits-v2-root"
    )
}


/* =========================================================
   РЕНДЕР ГЛАВНОЙ СТРАНИЦЫ

   preserveScroll:
   true  — сохраняет текущую прокрутку списка;
   false — открывает страницу с начала.
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
        renderedList.scrollTop =
            savedScrollTop
    })
}


/* =========================================================
   ОТКРЫТИЕ СТРАНИЦЫ СОЗДАНИЯ

   Передаём openHabitsPage в addHabitEvents.js,
   чтобы форма могла:

   - вернуться назад;
   - открыть список после сохранения привычки.
   ========================================================= */

function openNewHabitPage() {
    openAddHabitPage({
        resetDraft: true,
        onOpenHabitsPage: openHabitsPage
    })
}


/* =========================================================
   СОБЫТИЯ ГЛАВНОЙ СТРАНИЦЫ
   ========================================================= */

function initHabitsPageEvents() {
    const root = getHabitsRoot()

    if (!root) {
        console.warn(
            "Habits Events: не найден #habits-v2-root"
        )

        return
    }


    /* ---------------------------------------------------------
       КНОПКИ ДОБАВЛЕНИЯ ПРИВЫЧКИ

       Работает и для:
       - пустой страницы;
       - страницы со списком привычек.
       --------------------------------------------------------- */

    const addButtons = root.querySelectorAll(
        '[data-action="open-add-habit"]'
    )

    addButtons.forEach((button) => {
        addPressAnimation(button)

        button.addEventListener(
            "click",
            openNewHabitPage
        )
    })


    /* ---------------------------------------------------------
       СОБЫТИЯ КАРТОЧЕК
       --------------------------------------------------------- */

    initHabitCardEvents()
}


/* =========================================================
   ИНДЕКС СЕГОДНЯШНЕГО ДНЯ

   Индексы массива weekProgress:

   0 — понедельник
   1 — вторник
   2 — среда
   3 — четверг
   4 — пятница
   5 — суббота
   6 — воскресенье
   ========================================================= */

function getTodayWeekIndex() {
    const nativeDayIndex =
        new Date().getDay()

    return nativeDayIndex === 0
        ? 6
        : nativeDayIndex - 1
}


/* =========================================================
   ПЕРЕКЛЮЧЕНИЕ ВЫПОЛНЕНИЯ ПРИВЫЧКИ

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

function toggleHabitConfirmationLocally(
    habitId
) {
    const habit = getHabitById(
        habitId
    )

    if (!habit) {
        return null
    }

    const wasCompleted = Boolean(
        habit.completedToday
    )

    const xpReward = Math.max(
        0,
        Math.floor(
            Number(habit.xpReward) || 5
        )
    )

    const currentStreak = Math.max(
        0,
        Math.floor(
            Number(habit.streak) || 0
        )
    )

    const nextStreak = wasCompleted
        ? Math.max(
            0,
            currentStreak - 1
        )
        : currentStreak + 1


    /* ---------------------------------------------------------
       ВСЕГДА ФОРМИРУЕМ РОВНО 7 ДНЕЙ
       --------------------------------------------------------- */

    const weekProgress = Array.from(
        {
            length: 7
        },
        (_, index) => {
            return Boolean(
                habit.weekProgress?.[index]
            )
        }
    )

    weekProgress[getTodayWeekIndex()] =
        !wasCompleted


    /* ---------------------------------------------------------
       ОБНОВЛЯЕМ ПРИВЫЧКУ
       --------------------------------------------------------- */

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


    /* ---------------------------------------------------------
       ОБНОВЛЯЕМ ОБЩИЙ XP
       --------------------------------------------------------- */

    const statistics =
        getHabitsStatistics()

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


    /* ---------------------------------------------------------
       ОПРЕДЕЛЯЕМ САМУЮ ВЫСОКУЮ ТЕКУЩУЮ СЕРИЮ
       --------------------------------------------------------- */

    const highestHabitStreak = getHabits()
        .reduce(
            (
                highestStreak,
                storedHabit
            ) => {
                const storedStreak =
                    Math.max(
                        0,
                        Math.floor(
                            Number(
                                storedHabit.streak
                            ) || 0
                        )
                    )

                return Math.max(
                    highestStreak,
                    storedStreak
                )
            },
            0
        )


    /* ---------------------------------------------------------
       СОХРАНЯЕМ СТАТИСТИКУ
       --------------------------------------------------------- */

    setHabitsStatistics({
        totalXp: nextTotalXp,
        currentStreak: highestHabitStreak
    })

    return updatedHabit
}


/* =========================================================
   ВОССТАНОВИТЬ ПОЗИЦИЮ СПИСКА
   ========================================================= */

function restoreHabitsListScroll() {
    const renderedList =
        document.querySelector(
            ".habits-v2-list"
        )

    if (!renderedList) {
        return
    }

    requestAnimationFrame(() => {
        renderedList.scrollTop =
            habitsListScrollTop
    })
}


/* =========================================================
   ВОЗВРАТ ИЗ ДЕТАЛЕЙ ПРИВЫЧКИ
   ========================================================= */

function handleHabitDetailsBack() {
    openHabitsPage()

    restoreHabitsListScroll()
}


/* =========================================================
   ОТКРЫТИЕ ДЕТАЛЕЙ ПРИВЫЧКИ
   ========================================================= */

function openHabitDetails(habitId) {
    const selectedHabit = selectHabit(
        habitId
    )

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

    initHabitDetailsEvents({
        onBack: handleHabitDetailsBack
    })
}


/* =========================================================
   СОБЫТИЯ КАРТОЧЕК ПРИВЫЧЕК
   ========================================================= */

function initHabitCardEvents() {
    const root = getHabitsRoot()

    if (!root) {
        return
    }

    const habitCards = root.querySelectorAll(
        ".habit-card[data-habit-id]"
    )

    habitCards.forEach((card) => {
        const habitId =
            card.dataset.habitId

        if (!habitId) {
            return
        }

        const confirmButton = card.querySelector(
            '[data-action="confirm-habit"]'
        )


        /* -----------------------------------------------------
           АНИМАЦИИ НАЖАТИЯ
           ----------------------------------------------------- */

        addPressAnimation(card)
        addPressAnimation(confirmButton)


        /* -----------------------------------------------------
           НЕ ДАЁМ СОБЫТИЮ ГАЛОЧКИ ДОЙТИ ДО КАРТОЧКИ
           ----------------------------------------------------- */

        const stopConfirmEvent = (
            event
        ) => {
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
           ОТКРЫТИЕ ДЕТАЛЕЙ
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

                openHabitDetails(
                    habitId
                )
            }
        )


        /* -----------------------------------------------------
           ПОДТВЕРЖДЕНИЕ ПРИВЫЧКИ
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
   ОБЩАЯ ИНИЦИАЛИЗАЦИЯ РАЗДЕЛА
   ========================================================= */

export function initHabitsEvents() {
    const root = getHabitsRoot()

    if (!root) {
        console.warn(
            "Habits Events: не найден #habits-v2-root"
        )

        return
    }


    /* ---------------------------------------------------------
       ЕСЛИ УЖЕ ОТКРЫТА СТРАНИЦА ДЕТАЛЕЙ
       --------------------------------------------------------- */

    const habitDetailsPage = root.querySelector(
        ".habit-details"
    )

    if (habitDetailsPage) {
        initHabitDetailsEvents({
            onBack: handleHabitDetailsBack
        })

        return
    }


    /* ---------------------------------------------------------
       ЕСЛИ УЖЕ ОТКРЫТА СТРАНИЦА СОЗДАНИЯ

       Например, initHabitsEvents вызвали повторно после
       повторной инициализации приложения.
       --------------------------------------------------------- */

    const addHabitPage = root.querySelector(
        ".add-habit-v2"
    )

    if (addHabitPage) {
        restoreDraftToAddHabitPage()

        initAddHabitPageEvents({
            onOpenHabitsPage:
                openHabitsPage
        })

        return
    }


    /* ---------------------------------------------------------
       ГЛАВНАЯ СТРАНИЦА

       При первом запуске рендерим:
       - пустой экран, если привычек нет;
       - список, если привычки существуют.
       --------------------------------------------------------- */

    openHabitsPage()
}