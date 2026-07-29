import {
    addPressAnimation
} from "../habitsUtils.js"

import {
    initHabitDetailsMenu,
    closeHabitDetailsMenu,
    destroyHabitDetailsMenu
} from "./habitDetailsMenu.js"


/* =========================================================
   HABIT DETAILS EVENTS

   События детальной страницы привычки.

   Отвечает за:
   - возврат к списку привычек;
   - открытие меню;
   - подтверждение привычки;
   - снятие подтверждения привычки.
   ========================================================= */


/* =========================================================
   ИНИЦИАЛИЗАЦИЯ СОБЫТИЙ ДЕТАЛЬНОЙ СТРАНИЦЫ
   ========================================================= */

export function initHabitDetailsEvents({
    onBack = null,
    onConfirm = null
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


    /* =========================================================
       АНИМАЦИИ НАЖАТИЯ
       ========================================================= */

    addPressAnimation(backButton)
    addPressAnimation(menuButton)
    addPressAnimation(confirmButton)


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

       Сам файл не изменяет Store.

       Он только сообщает внешней логике,
       что пользователь нажал кнопку подтверждения.
       ========================================================= */

    confirmButton?.addEventListener(
        "click",
        (event) => {
            event.preventDefault()
            event.stopPropagation()

            closeHabitDetailsMenu(root)

            if (typeof onConfirm !== "function") {
                console.warn(
                    "Habit Details Events: не передан onConfirm"
                )

                return
            }

            onConfirm()
        }
    )
}