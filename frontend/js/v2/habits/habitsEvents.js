export function initHabitsEvents() {
    const addButton = document.querySelector(
        ".habits-v2-empty__add-button"
    )

    if (!addButton) {
        return
    }

    const press = () => {
        addButton.classList.add("is-pressed")
    }

    const release = () => {
        window.setTimeout(() => {
            addButton.classList.remove("is-pressed")
        }, 90)
    }

    addButton.addEventListener("touchstart", press, {
        passive: true
    })

    addButton.addEventListener("touchend", release, {
        passive: true
    })

    addButton.addEventListener("touchcancel", release, {
        passive: true
    })

    addButton.addEventListener("pointerdown", press)
    addButton.addEventListener("pointerup", release)
    addButton.addEventListener("pointercancel", release)
    addButton.addEventListener("pointerleave", release)
}