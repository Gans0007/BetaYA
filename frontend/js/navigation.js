import { renderPartners } from "./partners_components/partners.js"
import { renderChallenges } from "./challenges_components/challenges.js"

export function initNavigation(){

const items = document.querySelectorAll(".nav-item")

/* кешируем страницы один раз */

const pages = {
dashboard: document.getElementById("dashboard-page"),
challenges: document.getElementById("challenges-page"), // 🔥 ДОБАВИЛИ
chat: document.getElementById("chat-page"),
leaderboard: document.getElementById("leaderboard-page"),
partners: document.getElementById("partners-page")
}

const gameRoot = document.getElementById("game-root") // 🔥 ДОБАВИЛИ
const gamePages = ["dashboard", "challenges"] // 🔥 ДОБАВИЛИ

let activePage = pages.dashboard

items.forEach(item => {

item.addEventListener("click", () => {

const pageName = item.dataset.page

/* активная кнопка */

items.forEach(i => i.classList.remove("active"))
item.classList.add("active")

/* переключение страниц */

if(activePage){
activePage.classList.remove("active")
}

activePage = pages[pageName]

if(activePage){
activePage.classList.add("active")
}

/* 🔥 ПОКАЗ / СКРЫТИЕ HEADER */

if(gameRoot){
    if(gamePages.includes(pageName)){
        gameRoot.style.display = "block"
    }else{
        gameRoot.style.display = "none"
    }
}

/* старая логика НЕ трогаем */

if(pageName === "partners"){
    renderPartners()
}

if(pageName === "challenges"){
    renderChallenges()
}

})

})

}