/* =========================================================
   HABITS LIST EVENTS

   Логика страницы со списком привычек.

   Отвечает за:
   - события карточек;
   - открытие деталей привычки;
   - подтверждение выполнения;
   - снятие подтверждения;
   - изменение XP;
   - изменение текущей серии;
   - обновление недельного прогресса;
   - обновление календаря детальной страницы;
   - сохранение позиции прокрутки;
   - возврат из деталей к списку.
   ========================================================= */


/* =========================================================
   СТРАНИЦА ДЕТАЛЕЙ
   ========================================================= */

import {
    renderHabitDetailsPage
} from "../viewHabitDetails/habitDetailsPage.js"

import {
    initHabitDetailsEvents
} from "../viewHabitDetails/habitDetailsEvents.js"

import {
    openHabitDetailsMenu
} from "../viewHabitDetails/habitDetailsMenu.js"

import {
    openHabitDeleteConfirm
} from "../viewHabitDetails/habitDeleteConfirm.js"


/* =========================================================
   СТРАНИЦА РЕДАКТИРОВАНИЯ
   ========================================================= */

import {
    openAddHabitPage
} from "../habitMainEmpty/addHabitEvents.js"

import {
    startHabitEditDraft
} from "../habitMainEmpty/habitsDraft.js"

/* =========================================================
   STORE
   ========================================================= */

import {
    getHabits,
    getHabitById,
    getHabitsStatistics,
    updateHabit,
    removeHabit,
    selectHabit,
    getSelectedHabit,
    setHabitsStatistics
} from "../habitsStore.js"

/* =========================================================
   ОБЩИЕ УТИЛИТЫ
   ========================================================= */

import {
    addPressAnimation
} from "../habitsUtils.js"


/* =========================================================
   СОХРАНЁННАЯ ПОЗИЦИЯ СПИСКА

   Перед открытием подробной страницы запоминаем,
   где находился пользователь.
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
   ПОЛУЧИТЬ СПИСОК ПРИВЫЧЕК
   ========================================================= */

function getHabitsListElement() {
    return document.querySelector(
        ".habits-v2-list"
    )
}


/* =========================================================
   ИНДЕКС СЕГОДНЯШНЕГО ДНЯ

   weekProgress:

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
   НОРМАЛИЗАЦИЯ ПОЛОЖИТЕЛЬНОГО ЦЕЛОГО ЧИСЛА
   ========================================================= */

function normalizePositiveInteger(
    value,
    fallback = 0
) {
    const numericValue = Number(value)

    if (!Number.isFinite(numericValue)) {
        return fallback
    }

    return Math.max(
        0,
        Math.floor(numericValue)
    )
}


/* =========================================================
   НОРМАЛИЗАЦИЯ НЕДЕЛЬНОГО ПРОГРЕССА

   Всегда возвращает массив из семи значений.
   ========================================================= */

function normalizeWeekProgress(
    weekProgress
) {
    return Array.from(
        {
            length: 7
        },
        (_, index) => {
            return Boolean(
                weekProgress?.[index]
            )
        }
    )
}


/* =========================================================
   ВЫЧИСЛИТЬ САМОЕ ВЫСОКОЕ ЗНАЧЕНИЕ СЕРИИ
   ========================================================= */

function getHighestHabitStreak() {
    return getHabits().reduce(
        (
            highestStreak,
            storedHabit
        ) => {
            const storedStreak =
                normalizePositiveInteger(
                    storedHabit.streak
                )

            return Math.max(
                highestStreak,
                storedStreak
            )
        },
        0
    )
}


/* =========================================================
   ПЕРЕКЛЮЧИТЬ ПОДТВЕРЖДЕНИЕ ПРИВЫЧКИ

   Первое нажатие:
   - completedToday становится true;
   - добавляется XP;
   - серия увеличивается;
   - сегодняшний день отмечается;
   - записывается completedAt.

   Повторное нажатие:
   - completedToday становится false;
   - XP возвращается;
   - серия уменьшается;
   - отметка сегодняшнего дня снимается;
   - completedAt очищается.
   ========================================================= */

export function toggleHabitConfirmationLocally(
    habitId
) {
    const habit = getHabitById(
        habitId
    )

    if (!habit) {
        console.warn(
            `Habits List Events: привычка "${habitId}" не найдена`
        )

        return null
    }

    const wasCompleted = Boolean(
        habit.completedToday
    )

    const xpReward =
        normalizePositiveInteger(
            habit.xpReward,
            5
        )

    const currentStreak =
        normalizePositiveInteger(
            habit.streak
        )

    const nextStreak = wasCompleted
        ? Math.max(
            0,
            currentStreak - 1
        )
        : currentStreak + 1

    const weekProgress =
        normalizeWeekProgress(
            habit.weekProgress
        )

    weekProgress[getTodayWeekIndex()] =
        !wasCompleted


    /* ---------------------------------------------------------
       ОБНОВЛЯЕМ ПРИВЫЧКУ
       --------------------------------------------------------- */

    const updatedHabit = updateHabit(
        habitId,
        {
            completedToday:
                !wasCompleted,

            streak:
                nextStreak,

            weekProgress,

            completedAt:
                wasCompleted
                    ? null
                    : new Date().toISOString()
        }
    )

    if (!updatedHabit) {
        console.warn(
            `Habits List Events: не удалось обновить привычку "${habitId}"`
        )

        return null
    }


    /* ---------------------------------------------------------
       ОБНОВЛЯЕМ ОБЩИЙ XP
       --------------------------------------------------------- */

    const statistics =
        getHabitsStatistics()

    const currentTotalXp =
        normalizePositiveInteger(
            statistics.totalXp
        )

    const nextTotalXp = wasCompleted
        ? Math.max(
            0,
            currentTotalXp - xpReward
        )
        : currentTotalXp + xpReward


    /* ---------------------------------------------------------
       ОБНОВЛЯЕМ ОБЩУЮ СТАТИСТИКУ
       --------------------------------------------------------- */

    setHabitsStatistics({
        totalXp:
            nextTotalXp,

        currentStreak:
            getHighestHabitStreak()
    })

    return updatedHabit
}


/* =========================================================
   СОХРАНИТЬ ПОЗИЦИЮ СПИСКА
   ========================================================= */

function saveHabitsListScroll() {
    const habitsList =
        getHabitsListElement()

    habitsListScrollTop =
        habitsList?.scrollTop || 0
}


/* =========================================================
   ВОССТАНОВИТЬ ПОЗИЦИЮ СПИСКА
   ========================================================= */

export function restoreHabitsListScroll() {
    const habitsList =
        getHabitsListElement()

    if (!habitsList) {
        return
    }

    requestAnimationFrame(() => {
        habitsList.scrollTop =
            habitsListScrollTop
    })
}


/* =========================================================
   ВОЗВРАТ ИЗ ДЕТАЛЕЙ

   onOpenHabitsPage должен:
   - заново отрисовать главную страницу;
   - подключить события главной страницы.
   ========================================================= */

function handleHabitDetailsBack(
    onOpenHabitsPage
) {
    if (
        typeof onOpenHabitsPage !==
        "function"
    ) {
        console.warn(
            "Habits List Events: не передан onOpenHabitsPage"
        )

        return
    }

    onOpenHabitsPage()

    restoreHabitsListScroll()
}


/* =========================================================
   ОТКРЫТЬ РЕДАКТИРОВАНИЕ ПРИВЫЧКИ

   Перед открытием формы:
   - получаем актуальную привычку из Store;
   - переносим редактируемые поля в черновик;
   - открываем Add Habit Page в режиме редактирования.

   При отмене:
   - возвращаемся в детали без изменений.

   После сохранения:
   - получаем обновлённую привычку из Store;
   - заново рисуем детальную страницу;
   - подключаем события.
   ========================================================= */

function openHabitEditPage(
    habitId,
    {
        onOpenHabitsPage = null
    } = {}
) {
    const habit = getHabitById(
        habitId
    )

    if (!habit) {
        console.warn(
            `Habits List Events: невозможно редактировать привычку "${habitId}"`
        )

        return
    }


    /* ---------------------------------------------------------
       ЗАПОЛНЯЕМ ЧЕРНОВИК ДАННЫМИ ПРИВЫЧКИ
       --------------------------------------------------------- */

    const editDraft =
        startHabitEditDraft(
            habit
        )

    if (!editDraft) {
        console.warn(
            `Habits List Events: не удалось создать черновик редактирования "${habitId}"`
        )

        return
    }


    /* ---------------------------------------------------------
       ОТКРЫВАЕМ ФОРМУ РЕДАКТИРОВАНИЯ
       --------------------------------------------------------- */

    openAddHabitPage({
        resetDraft: false,

        onOpenHabitsPage,

        onCancel: () => {
            refreshHabitDetails(
                habitId,
                {
                    onOpenHabitsPage
                }
            )
        },

        onHabitSaved: (
            savedHabit
        ) => {
            const savedHabitId =
                savedHabit?.id ||
                habitId

            refreshHabitDetails(
                savedHabitId,
                {
                    onOpenHabitsPage
                }
            )
        }
    })
}


/* =========================================================
   УДАЛИТЬ ПРИВЫЧКУ ИЗ ДЕТАЛЬНОЙ СТРАНИЦЫ

   После удаления:
   - выбранная привычка очищается в Store;
   - текущая серия пересчитывается;
   - накопленный XP сохраняется;
   - открывается главная страница привычек.

   XP не уменьшаем, потому что пользователь уже заработал
   его за выполненные действия.
   ========================================================= */

function handleHabitDetailsDelete(
    habitId,
    {
        onOpenHabitsPage = null
    } = {}
) {
    const habit = getHabitById(
        habitId
    )

    if (!habit) {
        console.warn(
            `Habits List Events: невозможно удалить привычку "${habitId}"`
        )

        return null
    }

    const removedHabit = removeHabit(
        habitId
    )

    if (!removedHabit) {
        console.warn(
            `Habits List Events: не удалось удалить привычку "${habitId}"`
        )

        return null
    }


    /* ---------------------------------------------------------
       ПЕРЕСЧИТЫВАЕМ ТЕКУЩУЮ СЕРИЮ

       getHighestHabitStreak() вызывается уже после удаления,
       поэтому удалённая привычка в расчёт не попадёт.
       --------------------------------------------------------- */

    setHabitsStatistics({
        currentStreak:
            getHighestHabitStreak()
    })


    /* ---------------------------------------------------------
       ВОЗВРАЩАЕМСЯ НА ГЛАВНУЮ СТРАНИЦУ
       --------------------------------------------------------- */

    if (
        typeof onOpenHabitsPage !==
        "function"
    ) {
        console.warn(
            "Habits List Events: привычка удалена, но не передан onOpenHabitsPage"
        )

        return removedHabit
    }

    onOpenHabitsPage()

    return removedHabit
}

/* =========================================================
   ПОДКЛЮЧИТЬ СОБЫТИЯ ДЕТАЛЬНОЙ СТРАНИЦЫ

   Используется:
   - после первого открытия;
   - после подтверждения;
   - после снятия подтверждения;
   - после редактирования;
   - после повторного рендера страницы.
   ========================================================= */

function initCurrentHabitDetailsEvents(
    habitId,
    {
        onOpenHabitsPage = null
    } = {}
) {
    initHabitDetailsEvents({
        onBack: () => {
            handleHabitDetailsBack(
                onOpenHabitsPage
            )
        },

        onConfirm: ({
            keepMenuOpen = false
        } = {}) => {
            handleHabitDetailsConfirmation(
                habitId,
                {
                    onOpenHabitsPage,
                    keepMenuOpen
                }
            )
        },

        onEdit: () => {
            openHabitEditPage(
                habitId,
                {
                    onOpenHabitsPage
                }
            )
        },

        onDelete: () => {
            openHabitDeleteConfirm({
                onDelete: () => {
                    handleHabitDetailsDelete(
                        habitId,
                        {
                            onOpenHabitsPage
                        }
                    )
                },

                onKeep: () => {
                    refreshHabitDetails(
                        habitId,
                        {
                            onOpenHabitsPage
                        }
                    )
                }
            })
        }
    })
}

/* =========================================================
   ПЕРЕРИСОВАТЬ ДЕТАЛЬНУЮ СТРАНИЦУ

   После изменения Store:
   - получает свежую привычку;
   - заново рисует детали;
   - заново подключает события;
   - при необходимости заново открывает меню.
   ========================================================= */

function refreshHabitDetails(
    habitId,
    {
        onOpenHabitsPage = null,
        keepMenuOpen = false
    } = {}
) {
    const updatedHabit = getHabitById(
        habitId
    )

    if (!updatedHabit) {
        console.warn(
            `Habits List Events: невозможно обновить детали привычки "${habitId}"`
        )

        return
    }

    renderHabitDetailsPage(
        updatedHabit
    )

    initCurrentHabitDetailsEvents(
        habitId,
        {
            onOpenHabitsPage
        }
    )


    /* ---------------------------------------------------------
       ВОЗВРАЩАЕМ МЕНЮ В ОТКРЫТОЕ СОСТОЯНИЕ

       renderHabitDetailsPage заменяет старый DOM,
       поэтому открываем уже новое меню.
       --------------------------------------------------------- */

    if (keepMenuOpen) {
        const root = getHabitsRoot()

        requestAnimationFrame(() => {
            openHabitDetailsMenu(root)
        })
    }
}
/* =========================================================
   ПОДТВЕРЖДЕНИЕ ИЗ ДЕТАЛЬНОЙ СТРАНИЦЫ

   Использует ту же функцию подтверждения,
   которая используется в карточке списка.
   ========================================================= */

/* =========================================================
   ПОДТВЕРЖДЕНИЕ ИЗ ДЕТАЛЬНОЙ СТРАНИЦЫ

   Использует ту же функцию подтверждения,
   которая используется в карточке списка.

   После обновления меню остаётся открытым.
   ========================================================= */

function handleHabitDetailsConfirmation(
    habitId,
    {
        onOpenHabitsPage = null,
        keepMenuOpen = false
    } = {}
) {
    const updatedHabit =
        toggleHabitConfirmationLocally(
            habitId
        )

    if (!updatedHabit) {
        return
    }

    refreshHabitDetails(
        habitId,
        {
            onOpenHabitsPage,
            keepMenuOpen
        }
    )
}
/* =========================================================
   ОТКРЫТЬ ДЕТАЛИ ПРИВЫЧКИ
   ========================================================= */

export function openHabitDetails(
    habitId,
    {
        onOpenHabitsPage = null
    } = {}
) {
    const selectedHabit = selectHabit(
        habitId
    )

    if (!selectedHabit) {
        console.warn(
            `Habits List Events: невозможно открыть привычку "${habitId}"`
        )

        return
    }

    saveHabitsListScroll()

    renderHabitDetailsPage(
        selectedHabit
    )

    initCurrentHabitDetailsEvents(
        habitId,
        {
            onOpenHabitsPage
        }
    )
}


/* =========================================================
   ПОВТОРНАЯ ИНИЦИАЛИЗАЦИЯ ОТКРЫТОЙ СТРАНИЦЫ ДЕТАЛЕЙ

   Используется, если общий initHabitsEvents был вызван,
   когда страница деталей уже находится в DOM.
   ========================================================= */

export function initOpenedHabitDetailsEvents({
    onOpenHabitsPage = null
} = {}) {
    const root = getHabitsRoot()

    if (!root) {
        return
    }

    const habitDetailsPage = root.querySelector(
        ".habit-details"
    )

    if (!habitDetailsPage) {
        return
    }

    const habitId =
        habitDetailsPage.dataset.habitId ||
        getSelectedHabit()?.id

    if (!habitId) {
        console.warn(
            "Habits List Events: у открытой страницы деталей отсутствует habitId"
        )

        return
    }

    initCurrentHabitDetailsEvents(
        habitId,
        {
            onOpenHabitsPage
        }
    )
}


/* =========================================================
   ОСТАНОВИТЬ СОБЫТИЕ КНОПКИ ПОДТВЕРЖДЕНИЯ

   Не позволяет нажатию на галочку открыть карточку.
   ========================================================= */

function stopConfirmEvent(event) {
    event.stopPropagation()
}


/* =========================================================
   СОБЫТИЯ ОДНОЙ КАРТОЧКИ
   ========================================================= */

function initSingleHabitCardEvents(
    card,
    {
        onOpenHabitsPage = null
    } = {}
) {
    const habitId =
        card.dataset.habitId

    if (!habitId) {
        return
    }

    const confirmButton = card.querySelector(
        '[data-action="confirm-habit"]'
    )


    /* ---------------------------------------------------------
       АНИМАЦИЯ НАЖАТИЯ
       --------------------------------------------------------- */

    addPressAnimation(card)
    addPressAnimation(confirmButton)


    /* ---------------------------------------------------------
       НЕ ДАЁМ ГАЛОЧКЕ ОТКРЫТЬ КАРТОЧКУ
       --------------------------------------------------------- */

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


    /* ---------------------------------------------------------
       ОТКРЫТИЕ ДЕТАЛЕЙ ПРИВЫЧКИ
       --------------------------------------------------------- */

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
                habitId,
                {
                    onOpenHabitsPage
                }
            )
        }
    )


    /* ---------------------------------------------------------
       ПОДТВЕРЖДЕНИЕ ПРИВЫЧКИ В СПИСКЕ
       --------------------------------------------------------- */

    confirmButton?.addEventListener(
        "click",
        (event) => {
            event.preventDefault()
            event.stopPropagation()

            const currentList =
                getHabitsListElement()

            const savedScrollTop =
                currentList?.scrollTop || 0

            const updatedHabit =
                toggleHabitConfirmationLocally(
                    habitId
                )

            if (!updatedHabit) {
                return
            }

            if (
                typeof onOpenHabitsPage !==
                "function"
            ) {
                console.warn(
                    "Habits List Events: привычка обновлена, но не передан onOpenHabitsPage"
                )

                return
            }

            onOpenHabitsPage({
                preserveScroll: true,
                scrollTop: savedScrollTop
            })
        }
    )
}


/* =========================================================
   ИНИЦИАЛИЗАЦИЯ СОБЫТИЙ СПИСКА

   onOpenHabitsPage передаётся из корневого habitsEvents.js.
   ========================================================= */

export function initHabitsListEvents({
    onOpenHabitsPage = null
} = {}) {
    const root = getHabitsRoot()

    if (!root) {
        console.warn(
            "Habits List Events: не найден #habits-v2-root"
        )

        return
    }

    const habitsList = root.querySelector(
        ".habits-v2-list"
    )

    if (!habitsList) {
        return
    }

    const habitCards = habitsList.querySelectorAll(
        ".habit-card[data-habit-id]"
    )

    habitCards.forEach((card) => {
        initSingleHabitCardEvents(
            card,
            {
                onOpenHabitsPage
            }
        )
    })
}


/* =========================================================
   СБРОС СОХРАНЁННОЙ ПРОКРУТКИ

   Можно использовать при выходе из раздела привычек.
   ========================================================= */

export function resetHabitsListScroll() {
    habitsListScrollTop = 0
}