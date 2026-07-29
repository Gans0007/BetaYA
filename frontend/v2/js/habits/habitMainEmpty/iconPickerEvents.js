/* =========================================================
   ICON PICKER EVENTS

   Логика страницы выбора эмодзи.

   Отвечает за:
   - временный выбор эмодзи;
   - визуальное выделение выбранного эмодзи;
   - возврат без сохранения;
   - подтверждение выбранного эмодзи;
   - сохранение эмодзи в черновик привычки.
   ========================================================= */


import {
    getHabitDraftValue,
    setHabitDraftValue
} from "./habitsDraft.js"

import {
    addPressAnimation
} from "../habitsUtils.js"


/* =========================================================
   ПОЛУЧИТЬ КОРНЕВОЙ КОНТЕЙНЕР
   ========================================================= */

function getHabitsRoot() {
    return document.getElementById(
        "habits-v2-root"
    )
}


/* =========================================================
   СОБЫТИЯ СТРАНИЦЫ ВЫБОРА ЭМОДЗИ

   onBackToAddHabitPage:
   функция возвращения на страницу создания привычки.

   Возврат через стрелку:
   - не сохраняет временно выбранный эмодзи.

   Нажатие «Выбрать»:
   - сохраняет эмодзи в habitsDraft;
   - возвращает на страницу создания привычки.
   ========================================================= */

export function initIconPickerEvents({
    onBackToAddHabitPage = null
} = {}) {
    const root = getHabitsRoot()

    if (!root) {
        console.warn(
            "Icon Picker Events: не найден #habits-v2-root"
        )

        return
    }


    /* =====================================================
       ЭЛЕМЕНТЫ
       ===================================================== */

    const backButton = root.querySelector(
        '[data-action="close-icon-picker"]'
    )

    const confirmButton = root.querySelector(
        '[data-action="confirm-habit-icon"]'
    )

    const iconButtons = root.querySelectorAll(
        "[data-habit-icon]"
    )


    /* =====================================================
       ВРЕМЕННО ВЫБРАННЫЙ ЭМОДЗИ

       До нажатия кнопки «Выбрать» значение не записывается
       в основной черновик привычки.
       ===================================================== */

    let pendingIcon =
        getHabitDraftValue("icon") || "✱"


    /* =====================================================
       АНИМАЦИИ НАЖАТИЯ
       ===================================================== */

    addPressAnimation(backButton)
    addPressAnimation(confirmButton)

    iconButtons.forEach((button) => {
        addPressAnimation(button)
    })


    /* =====================================================
       ВОЗВРАТ БЕЗ СОХРАНЕНИЯ

       pendingIcon не записывается в habitsDraft.
       Остаётся прежняя подтверждённая иконка.
       ===================================================== */

    backButton?.addEventListener(
        "click",
        () => {
            if (
                typeof onBackToAddHabitPage ===
                "function"
            ) {
                onBackToAddHabitPage()
                return
            }

            console.warn(
                "Icon Picker Events: не передан onBackToAddHabitPage"
            )
        }
    )


    /* =====================================================
       ВРЕМЕННЫЙ ВЫБОР ЭМОДЗИ
       ===================================================== */

    iconButtons.forEach((button) => {
        button.addEventListener(
            "click",
            () => {
                iconButtons.forEach(
                    (iconButton) => {
                        iconButton.classList.remove(
                            "is-selected"
                        )

                        iconButton.setAttribute(
                            "aria-pressed",
                            "false"
                        )
                    }
                )

                button.classList.add(
                    "is-selected"
                )

                button.setAttribute(
                    "aria-pressed",
                    "true"
                )

                pendingIcon =
                    button.dataset.habitIcon ||
                    "✱"
            }
        )
    })


    /* =====================================================
       ПОДТВЕРЖДЕНИЕ ЭМОДЗИ

       Только после нажатия кнопки «Выбрать»
       сохраняем эмодзи в черновик привычки.
       ===================================================== */

    confirmButton?.addEventListener(
        "click",
        () => {
            setHabitDraftValue(
                "icon",
                pendingIcon
            )

            if (
                typeof onBackToAddHabitPage ===
                "function"
            ) {
                onBackToAddHabitPage()
                return
            }

            console.warn(
                "Icon Picker Events: иконка сохранена, но не передан onBackToAddHabitPage"
            )
        }
    )
}