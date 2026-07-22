import { renderHabitsPage } from "./habits/habitsPage.js"

function initV2() {
    const dashboardPage = document.getElementById("dashboard-page")

    if (!dashboardPage) {
        console.error("V2: не найдена страница #dashboard-page")
        return
    }

    renderHabitsPage()
}

document.addEventListener("DOMContentLoaded", initV2)