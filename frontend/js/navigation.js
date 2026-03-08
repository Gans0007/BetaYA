export function initNavigation(){

const items = document.querySelectorAll(".nav-item")
const pages = document.querySelectorAll(".page")

items.forEach(item => {

item.addEventListener("click", () => {

const page = item.dataset.page

/* активная иконка */

items.forEach(i => i.classList.remove("active"))
item.classList.add("active")

/* переключение страниц */

pages.forEach(p => p.classList.remove("active"))

const activePage = document.getElementById(page + "-page")

if(activePage){
activePage.classList.add("active")
}

/* фикс скролла */

const scroll = activePage?.querySelector(".page-content")

if(scroll){
scroll.scrollTop = 0
}

})

})

}