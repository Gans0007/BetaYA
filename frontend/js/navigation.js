import { renderPartners } from "./partners_components/partners.js"

export function initNavigation(){

const items = document.querySelectorAll(".nav-item")

/* кешируем страницы один раз */

const pages = {
dashboard: document.getElementById("dashboard-page"),
chat: document.getElementById("chat-page"),
leaderboard: document.getElementById("leaderboard-page"),
partners: document.getElementById("partners-page")
}

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

if(pageName === "partners"){
    renderPartners()
}

})

})

}