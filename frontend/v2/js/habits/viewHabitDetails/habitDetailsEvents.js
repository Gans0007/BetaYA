import {
    addPressAnimation
} from "../habitsUtils.js"

import {
    initHabitDetailsMenu,
    destroyHabitDetailsMenu
} from "./habitDetailsMenu.js"


/* =========================================================
   HABIT DETAILS EVENTS

   События детальной страницы привычки.

   Отвечает за:
   - возврат к списку привычек;
   - открытие меню;
   - подтверждение привычки;
   - снятие подтверждения привычки;
   - запуск редактирования привычки;
   - запуск удаления привычки.
   ========================================================= */


/* =========================================================
   ИНИЦИАЛИЗАЦИЯ СОБЫТИЙ ДЕТАЛЬНОЙ СТРАНИЦЫ
   ========================================================= */

export function initHabitDetailsEvents({
    onBack = null,
    onConfirm = null,
    onEdit = null,
    onDelete = null
} = {}) {
    const root = document.getElementById(
        "habits-v2-root"
    )

    if (!root) {
        console.warn(
            "Habit Details Events: не найден #habits-v2-root"
        )

        return
    }


    /* =========================================================
       ЭЛЕМЕНТЫ СТРАНИЦЫ
       ========================================================= */

    const backButton = root.querySelector(
        '[data-action="close-habit-details"]'
    )

    const menuButton = root.querySelector(
        '[data-action="toggle-habit-menu"]'
    )

    const confirmButton = root.querySelector(
        '[data-action="confirm-habit"]'
    )

    const editButton = root.querySelector(
        '[data-action="edit-habit"]'
    )

    const deleteButton = root.querySelector(
        '[data-action="delete-habit"]'
    )


    /* =========================================================
       АНИМАЦИИ НАЖАТИЯ
       ========================================================= */

    addPressAnimation(backButton)
    addPressAnimation(menuButton)
    addPressAnimation(confirmButton)
    addPressAnimation(editButton)
    addPressAnimation(deleteButton)


    /* =========================================================
       ИНИЦИАЛИЗАЦИЯ МЕНЮ
       ========================================================= */

    initHabitDetailsMenu(root)


    /* =========================================================
       ВОЗВРАТ К СПИСКУ
       ========================================================= */

    backButton?.addEventListener(
        "click",
        () => {
            destroyHabitDetailsMenu()

            if (typeof onBack !== "function") {
                console.warn(
                    "Habit Details Events: не передан onBack"
                )

                return
            }

            onBack()
        }
    )


    /* =========================================================
       ПОДТВЕРЖДЕНИЕ / СНЯТИЕ ПОДТВЕРЖДЕНИЯ
       ========================================================= */

    confirmButton?.addEventListener(
        "click",
        (event) => {
            event.preventDefault()
            event.stopPropagation()

            if (typeof onConfirm !== "function") {
                console.warn(
                    "Habit Details Events: не передан onConfirm"
                )

                return
            }

            onConfirm({
                keepMenuOpen: true
            })
        }
    )


    /* =========================================================
       РЕДАКТИРОВАНИЕ ПРИВЫЧКИ
       ========================================================= */

    editButton?.addEventListener(
        "click",
        (event) => {
            event.preventDefault()
            event.stopPropagation()

            destroyHabitDetailsMenu()

            if (typeof onEdit !== "function") {
                console.warn(
                    "Habit Details Events: не передан onEdit"
                )

                return
            }

            onEdit()
        }
    )


    /* =========================================================
       УДАЛЕНИЕ ПРИВЫЧКИ

       Здесь привычку не удаляем.
       Только передаём действие внешнему контроллеру.
       ========================================================= */

    deleteButton?.addEventListener(
        "click",
        (event) => {
            event.preventDefault()
            event.stopPropagation()

            destroyHabitDetailsMenu()

            if (typeof onDelete !== "function") {
                console.warn(
                    "Habit Details Events: не передан onDelete"
                )

                return
            }

            onDelete()
        }
    )
}