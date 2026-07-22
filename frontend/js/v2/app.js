import { renderHabitsPage } from "./habits/habitsPage.js"

function initV2() {
    const habitsV2Page = document.getElementById("habits-v2-page")

    if (!habitsV2Page) {
        console.error("V2: не найдена страница #habits-v2-page")
        return
    }

    renderHabitsPage()
}

document.addEventListener("DOMContentLoaded", initV2)