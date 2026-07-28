/* =========================================================
   HABITS EVENTS

   Главный контроллер раздела привычек.

   Отвечает за:
   - первоначальный запуск раздела;
   - рендер главной страницы;
   - открытие страницы создания привычки;
   - подключение событий пустой страницы;
   - подключение событий списка привычек;
   - повторную инициализацию открытых экранов.

   Логика отдельных частей находится в:

   habitMainEmpty/
   - addHabitEvents.js
   - iconPickerEvents.js

   habitMainList/
   - habitsListEvents.js

   viewHabitDetails/
   - habitDetailsEvents.js
   ========================================================= */


/* =========================================================
   РЕНДЕР ГЛАВНОЙ СТРАНИЦЫ
   ========================================================= */

import {
    renderHabitsPage
} from "./habitsPage.js"


/* =========================================================
   СОЗДАНИЕ ПРИВЫЧКИ
   ========================================================= */

import {
    openAddHabitPage,
    restoreDraftToAddHabitPage,
    initAddHabitPageEvents
} from "./habitMainEmpty/addHabitEvents.js"


/* =========================================================
   ВЫБОР ЭМОДЗИ
   ========================================================= */

import {
    initIconPickerEvents
} from "./habitMainEmpty/iconPickerEvents.js"


/* =========================================================
   СПИСОК ПРИВЫЧЕК И ДЕТАЛИ
   ========================================================= */

import {
    initHabitsListEvents,
    initOpenedHabitDetailsEvents
} from "./habitMainList/habitsListEvents.js"


/* =========================================================
   STORE
   ========================================================= */

import {
    getHabits,
    getHabitsStatistics
} from "./habitsStore.js"


/* =========================================================
   ОБЩИЕ УТИЛИТЫ
   ========================================================= */

import {
    addPressAnimation
} from "./habitsUtils.js"


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
   true  — восстановить положение списка;
   false — открыть страницу с начала.

   scrollTop:
   явное положение прокрутки, переданное из
   habitsListEvents.js после подтверждения привычки.
   ========================================================= */

function openHabitsPage({
    preserveScroll = false,
    scrollTop = null
} = {}) {
    const currentList = document.querySelector(
        ".habits-v2-list"
    )

    const savedScrollTop =
        scrollTop !== null
            ? Math.max(
                0,
                Number(scrollTop) || 0
            )
            : preserveScroll
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
   ОТКРЫТЬ НОВУЮ СТРАНИЦУ СОЗДАНИЯ

   resetDraft: true означает, что пользователь начинает
   создание новой привычки, а не возвращается из Emoji Picker.
   ========================================================= */

function openNewHabitPage() {
    openAddHabitPage({
        resetDraft: true,
        onOpenHabitsPage: openHabitsPage
    })
}


/* =========================================================
   ВЕРНУТЬСЯ ИЗ EMOJI PICKER В СОЗДАНИЕ

   Черновик не сбрасываем, чтобы сохранить:
   - название;
   - цвет;
   - размер;
   - ранее подтверждённую иконку.
   ========================================================= */

function openAddHabitPageFromIconPicker() {
    openAddHabitPage({
        resetDraft: false,
        onOpenHabitsPage: openHabitsPage
    })
}


/* =========================================================
   СОБЫТИЯ ГЛАВНОЙ СТРАНИЦЫ

   Работает и для:
   - пустой страницы;
   - страницы со списком привычек.
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
       СОБЫТИЯ СПИСКА И КАРТОЧЕК

       Если на странице пустое состояние и списка нет,
       initHabitsListEvents просто завершит работу.
       --------------------------------------------------------- */

    initHabitsListEvents({
        onOpenHabitsPage:
            openHabitsPage
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
       УЖЕ ОТКРЫТА СТРАНИЦА ДЕТАЛЕЙ
       --------------------------------------------------------- */

    const habitDetailsPage = root.querySelector(
        ".habit-details"
    )

    if (habitDetailsPage) {
        initOpenedHabitDetailsEvents({
            onOpenHabitsPage:
                openHabitsPage
        })

        return
    }


    /* ---------------------------------------------------------
       УЖЕ ОТКРЫТ ВЫБОР ЭМОДЗИ

       Эта проверка нужна, чтобы повторный вызов
       initHabitsEvents не закрыл Emoji Picker.
       --------------------------------------------------------- */

    const iconPickerPage = root.querySelector(
        ".habit-icon-picker"
    )

    if (iconPickerPage) {
        initIconPickerEvents({
            onBackToAddHabitPage:
                openAddHabitPageFromIconPicker
        })

        return
    }


    /* ---------------------------------------------------------
       УЖЕ ОТКРЫТА СТРАНИЦА СОЗДАНИЯ
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

       renderHabitsPage самостоятельно определит:
       - показать пустую страницу;
       - показать список привычек.
       --------------------------------------------------------- */

    openHabitsPage()
}