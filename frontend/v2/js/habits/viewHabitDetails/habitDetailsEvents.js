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
   ========================================================= */

export function initHabitDetailsEvents({
    onBack
} = {}) {
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
        '[data-action="toggle-habit-menu"]'
    )


    /* =========================================================
       АНИМАЦИИ
       ========================================================= */

    addPressAnimation(backButton)
    addPressAnimation(menuButton)


    /* =========================================================
       МЕНЮ
       ========================================================= */

    initHabitDetailsMenu(root)


    /* =========================================================
       ВОЗВРАТ К СПИСКУ
       ========================================================= */

    backButton?.addEventListener(
        "click",
        () => {
            destroyHabitDetailsMenu()

            if (typeof onBack === "function") {
                onBack()
            }
        }
    )
}