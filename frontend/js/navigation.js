export function initNavigation(){

const items = document.querySelectorAll(".nav-item")

items.forEach(item => {

item.addEventListener("click", () => {

items.forEach(i => i.classList.remove("active"))

item.classList.add("active")

const page = item.dataset.page

navigate(page)

})

})

}

function navigate(page){

switch(page){

case "dashboard":
window.location.href = "index.html"
break

case "stats":
window.location.href = "stats.html"
break

case "leaderboard":
window.location.href = "leaderboard.html"
break

case "partners":
window.location.href = "partners.html"
break

}

}