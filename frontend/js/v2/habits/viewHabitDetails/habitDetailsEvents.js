import {
    addPressAnimation
} from "../habitsUtils.js"


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
        '[data-action="open-habit-menu"]'
    )


    /* =========================================================
       АНИМАЦИИ
       ========================================================= */

    addPressAnimation(backButton)
    addPressAnimation(menuButton)


    /* =========================================================
       ВОЗВРАТ К СПИСКУ
       ========================================================= */

    backButton?.addEventListener(
        "click",
        () => {
            if (typeof onBack === "function") {
                onBack()
            }
        }
    )


    /* =========================================================
       МЕНЮ

       Пока только заглушка.
       Реальную логику добавим, когда начнём меню.
       ========================================================= */

    menuButton?.addEventListener(
        "click",
        () => {
            console.log(
                "Открыть меню привычки"
            )
        }
    )
}