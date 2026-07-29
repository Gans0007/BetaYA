import {
    addPressAnimation
} from "../habitsUtils.js"


/* =========================================================
   DELETE HABIT CONFIRMATION

   Модальное окно подтверждения удаления привычки.

   Отвечает только за:
   - показ окна;
   - закрытие окна;
   - подтверждение удаления;
   - отмену удаления.
   ========================================================= */


let activeModal = null
let previousFocusedElement = null
let documentKeydownHandler = null


/* =========================================================
   ПОЛУЧИТЬ КОРНЕВОЙ КОНТЕЙНЕР
   ========================================================= */

function getHabitsRoot() {
    return document.getElementById(
        "habits-v2-root"
    )
}


/* =========================================================
   ЗАКРЫТЬ ОКНО
   ========================================================= */

export function closeHabitDeleteConfirm({
    restoreFocus = true
} = {}) {
    if (!activeModal) {
        return
    }

    const modal = activeModal

    modal.classList.remove(
        "is-visible"
    )

    document.body.classList.remove(
        "habit-delete-modal-open"
    )

    if (documentKeydownHandler) {
        document.removeEventListener(
            "keydown",
            documentKeydownHandler
        )

        documentKeydownHandler = null
    }

    window.setTimeout(() => {
        modal.remove()

        if (activeModal === modal) {
            activeModal = null
        }

        if (
            restoreFocus &&
            previousFocusedElement instanceof HTMLElement &&
            document.contains(previousFocusedElement)
        ) {
            previousFocusedElement.focus()
        }

        previousFocusedElement = null
    }, 220)
}


/* =========================================================
   ОТКРЫТЬ ОКНО
   ========================================================= */

export function openHabitDeleteConfirm({
    onDelete = null,
    onKeep = null
} = {}) {
    const root = getHabitsRoot()

    if (!root) {
        console.warn(
            "Habit Delete Confirm: не найден #habits-v2-root"
        )

        return
    }


    /* ---------------------------------------------------------
       УБИРАЕМ ПРЕДЫДУЩЕЕ ОКНО, ЕСЛИ ОНО ОСТАЛОСЬ
       --------------------------------------------------------- */

    closeHabitDeleteConfirm({
        restoreFocus: false
    })


    /* ---------------------------------------------------------
       СОХРАНЯЕМ ТЕКУЩИЙ ФОКУС
       --------------------------------------------------------- */

    previousFocusedElement =
        document.activeElement


    /* ---------------------------------------------------------
       СОЗДАЁМ МОДАЛЬНОЕ ОКНО
       --------------------------------------------------------- */

    const modal = document.createElement(
        "div"
    )

    modal.className =
        "habit-delete-confirm"

    modal.innerHTML = `
        <div
            class="habit-delete-confirm__backdrop"
            data-action="keep-habit"
        ></div>

        <section
            class="habit-delete-confirm__dialog"
            role="alertdialog"
            aria-modal="true"
            aria-labelledby="habit-delete-confirm-title"
        >
            <div
                class="habit-delete-confirm__icon"
                aria-hidden="true"
            >
                <span class="material-symbols-rounded">
                    delete
                </span>
            </div>

            <h2
                class="habit-delete-confirm__title"
                id="habit-delete-confirm-title"
            >
                Удалить безвозвратно привычку?
            </h2>

            <div class="habit-delete-confirm__actions">

                <button
                    class="
                        habit-delete-confirm__button
                        habit-delete-confirm__button--delete
                    "
                    type="button"
                    data-action="confirm-delete-habit"
                >
                    Удалить
                </button>

                <button
                    class="
                        habit-delete-confirm__button
                        habit-delete-confirm__button--keep
                    "
                    type="button"
                    data-action="keep-habit"
                >
                    Оставить
                </button>

            </div>
        </section>
    `

    root.appendChild(
        modal
    )

    activeModal = modal

    document.body.classList.add(
        "habit-delete-modal-open"
    )


    /* ---------------------------------------------------------
       ЭЛЕМЕНТЫ
       --------------------------------------------------------- */

    const dialog = modal.querySelector(
        ".habit-delete-confirm__dialog"
    )

    const deleteButton = modal.querySelector(
        '[data-action="confirm-delete-habit"]'
    )

    const keepButtons = modal.querySelectorAll(
        '[data-action="keep-habit"]'
    )


    /* ---------------------------------------------------------
       АНИМАЦИИ НАЖАТИЯ
       --------------------------------------------------------- */

    addPressAnimation(deleteButton)

    keepButtons.forEach((button) => {
        addPressAnimation(button)
    })


    /* ---------------------------------------------------------
       ПОДТВЕРДИТЬ УДАЛЕНИЕ
       --------------------------------------------------------- */

    deleteButton?.addEventListener(
        "click",
        () => {
            closeHabitDeleteConfirm({
                restoreFocus: false
            })

            if (typeof onDelete === "function") {
                onDelete()
            }
        }
    )


    /* ---------------------------------------------------------
       ОСТАВИТЬ ПРИВЫЧКУ
       --------------------------------------------------------- */

    keepButtons.forEach((button) => {
        button.addEventListener(
            "click",
            () => {
                closeHabitDeleteConfirm()

                if (typeof onKeep === "function") {
                    onKeep()
                }
            }
        )
    })


    /* ---------------------------------------------------------
       НЕ ЗАКРЫВАЕМ ОКНО ПРИ НАЖАТИИ НА САМ ДИАЛОГ
       --------------------------------------------------------- */

    dialog?.addEventListener(
        "click",
        (event) => {
            event.stopPropagation()
        }
    )


    /* ---------------------------------------------------------
       ЗАКРЫТИЕ ЧЕРЕЗ ESCAPE
       --------------------------------------------------------- */

    documentKeydownHandler = (
        event
    ) => {
        if (event.key !== "Escape") {
            return
        }

        event.preventDefault()

        closeHabitDeleteConfirm()

        if (typeof onKeep === "function") {
            onKeep()
        }
    }

    document.addEventListener(
        "keydown",
        documentKeydownHandler
    )


    /* ---------------------------------------------------------
       ПОКАЗЫВАЕМ С АНИМАЦИЕЙ
       --------------------------------------------------------- */

modal.classList.add(
    "is-visible"
)

deleteButton?.focus()
}