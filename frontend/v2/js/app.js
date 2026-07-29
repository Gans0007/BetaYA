import {
    initHabitsEvents
} from "./habits/habitsEvents.js"


function initTelegramWebApp() {
    const telegram =
        window.Telegram?.WebApp

    if (!telegram) {
        console.warn(
            "Telegram WebApp API недоступен"
        )

        return
    }

    telegram.ready()
    telegram.expand()

    window.initData =
        telegram.initData
}


function initV2() {
    const habitsPage =
        document.getElementById(
            "habits-v2-page"
        )

    const habitsRoot =
        document.getElementById(
            "habits-v2-root"
        )

    if (!habitsPage) {
        console.error(
            "V2: не найдена страница #habits-v2-page"
        )

        return
    }

    if (!habitsRoot) {
        console.error(
            "V2: не найден контейнер #habits-v2-root"
        )

        return
    }

    initTelegramWebApp()
    initHabitsEvents()
}


document.addEventListener(
    "DOMContentLoaded",
    initV2
)