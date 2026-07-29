/* =========================================================
   HABIT DETAILS MENU

   Управляет выпадающим меню детальной страницы привычки.

   Отвечает за:
   - открытие;
   - закрытие;
   - переключение;
   - закрытие по клику вне меню;
   - закрытие по Escape;
   - очистку обработчиков при закрытии страницы.
   ========================================================= */


/* =========================================================
   ТЕКУЩЕЕ СОСТОЯНИЕ МЕНЮ
   ========================================================= */

let activeMenuState = null


/* =========================================================
   ПОЛУЧИТЬ ЭЛЕМЕНТЫ МЕНЮ
   ========================================================= */

function getHabitDetailsMenuElements(root) {
    if (!root) {
        return {
            menu: null,
            menuButton: null,
            menuWrapper: null
        }
    }

    return {
        menu: root.querySelector(
            ".habit-details__menu"
        ),

        menuButton: root.querySelector(
            '[data-action="toggle-habit-menu"]'
        ),

        menuWrapper: root.querySelector(
            ".habit-details__menu-wrapper"
        )
    }
}


/* =========================================================
   ОТКРЫТЬ МЕНЮ
   ========================================================= */

export function openHabitDetailsMenu(root) {
    const {
        menu,
        menuButton
    } = getHabitDetailsMenuElements(root)

    if (!menu || !menuButton) {
        return
    }

    menu.classList.add("is-open")

    menu.setAttribute(
        "aria-hidden",
        "false"
    )

    menuButton.setAttribute(
        "aria-expanded",
        "true"
    )
}


/* =========================================================
   ЗАКРЫТЬ МЕНЮ
   ========================================================= */

export function closeHabitDetailsMenu(root) {
    const {
        menu,
        menuButton
    } = getHabitDetailsMenuElements(root)

    if (!menu || !menuButton) {
        return
    }

    menu.classList.remove("is-open")

    menu.setAttribute(
        "aria-hidden",
        "true"
    )

    menuButton.setAttribute(
        "aria-expanded",
        "false"
    )
}


/* =========================================================
   ПЕРЕКЛЮЧИТЬ МЕНЮ
   ========================================================= */

export function toggleHabitDetailsMenu(root) {
    const {
        menu
    } = getHabitDetailsMenuElements(root)

    if (!menu) {
        return
    }

    const isOpen =
        menu.classList.contains("is-open")

    if (isOpen) {
        closeHabitDetailsMenu(root)
        return
    }

    openHabitDetailsMenu(root)
}


/* =========================================================
   УНИЧТОЖИТЬ МЕНЮ

   Удаляет все обработчики, которые были добавлены
   во время инициализации.
   ========================================================= */

export function destroyHabitDetailsMenu() {
    if (!activeMenuState) {
        return
    }

    const {
        root,
        menuButton,
        handleMenuButtonClick,
        handleDocumentClick,
        handleDocumentKeydown
    } = activeMenuState

    closeHabitDetailsMenu(root)

    menuButton.removeEventListener(
        "click",
        handleMenuButtonClick
    )

    document.removeEventListener(
        "click",
        handleDocumentClick
    )

    document.removeEventListener(
        "keydown",
        handleDocumentKeydown
    )

    activeMenuState = null
}


/* =========================================================
   ИНИЦИАЛИЗАЦИЯ МЕНЮ
   ========================================================= */

export function initHabitDetailsMenu(root) {
    destroyHabitDetailsMenu()

    const {
        menuButton,
        menuWrapper
    } = getHabitDetailsMenuElements(root)

    if (!menuButton || !menuWrapper) {
        return
    }

    const handleMenuButtonClick = (event) => {
        event.stopPropagation()

        toggleHabitDetailsMenu(root)
    }

    const handleDocumentClick = (event) => {
        if (
            !menuWrapper.contains(
                event.target
            )
        ) {
            closeHabitDetailsMenu(root)
        }
    }

    const handleDocumentKeydown = (event) => {
        if (event.key !== "Escape") {
            return
        }

        const menu =
            root.querySelector(
                ".habit-details__menu"
            )

        const isOpen =
            menu?.classList.contains(
                "is-open"
            )

        if (!isOpen) {
            return
        }

        closeHabitDetailsMenu(root)
        menuButton.focus()
    }

    menuButton.addEventListener(
        "click",
        handleMenuButtonClick
    )

    document.addEventListener(
        "click",
        handleDocumentClick
    )

    document.addEventListener(
        "keydown",
        handleDocumentKeydown
    )

    activeMenuState = {
        root,
        menuButton,
        handleMenuButtonClick,
        handleDocumentClick,
        handleDocumentKeydown
    }
}