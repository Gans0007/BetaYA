import { renderPartners } from "./partners_components/partners.js"
import { renderChallenges } from "./challenges_components/challenges.js"

export function initNavigation(){

    const items = document.querySelectorAll(".nav-item")

    const pages = {
        dashboard: document.getElementById("dashboard-page"),
        challenges: document.getElementById("challenges-page"),
        chat: document.getElementById("chat-page"),
        leaderboard: document.getElementById("leaderboard-page"),
        partners: document.getElementById("partners-page")
    }

    const gamePages = ["dashboard", "challenges"]

    let activePage = document.querySelector(".page.active") || pages.dashboard

    function updateGameMode(pageName){
        if(gamePages.includes(pageName)){
            document.body.classList.add("game-mode")
        }else{
            document.body.classList.remove("game-mode")
        }
    }

    // 🚀 ФУНКЦИЯ РЕНДЕРА (универсальная)
    function renderPage(pageName){
        if(pageName === "partners"){
            renderPartners()
        }

        if(pageName === "challenges"){
            renderChallenges()
        }

        // сюда потом можно добавить:
        // if(pageName === "dashboard") renderDashboard()
    }

    // 🔁 КЛИКИ ПО НАВИГАЦИИ
    items.forEach(item => {
        item.addEventListener("click", () => {
            const pageName = item.dataset.page
            const nextPage = pages[pageName]

            if(!nextPage) return

            items.forEach(i => i.classList.remove("active"))
            item.classList.add("active")

            if(activePage){
                activePage.classList.remove("active")
            }

            nextPage.classList.add("active")
            activePage = nextPage

            updateGameMode(pageName)

            // 🔥 РЕНДЕР ПРИ ПЕРЕКЛЮЧЕНИИ
            renderPage(pageName)
        })
    })

    // 🎯 ОПРЕДЕЛЯЕМ СТАРТОВУЮ СТРАНИЦУ
    const startPageName = activePage?.id.replace("-page", "")

    updateGameMode(startPageName)

    // 🔥 РЕНДЕР ПРИ ПЕРВОЙ ЗАГРУЗКЕ (КЛЮЧЕВОЕ)
    renderPage(startPageName)
}