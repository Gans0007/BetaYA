import { openSettingsModal } from "./settingsModal.js"

export function renderPartners(){

const root = document.getElementById("partners-root")
if(!root) return

root.innerHTML = `

<div class="partners-container">

<h2 class="partners-title">В разработке</h2>

<div class="partners-buttons">

<button class="partners-btn" data-type="achievements">Достижения</button>
<button class="partners-btn" data-type="partners">Партнерка</button>
<button class="partners-btn">Настройки</button>

</div>

</div>

`

// =========================
// ОБРАБОТКА КНОПОК
// =========================

const buttons = root.querySelectorAll(".partners-btn")

buttons.forEach(btn => {

btn.addEventListener("click", () => {

const type = btn.dataset.type

if(type === "achievements"){
showToast("Выполняй задания — получай достижения")
}

if(type === "partners"){
showToast("Собирай свою банду и зарабатывай")
}

if(type === "settings"){
    openSettings()
}

})

})

}


// =========================
// TOAST
// =========================

function showToast(text){

let toast = document.querySelector(".custom-toast")

if(!toast){
toast = document.createElement("div")
toast.className = "custom-toast"
document.body.appendChild(toast)
}

toast.innerText = text

toast.classList.add("show")

setTimeout(() => {
toast.classList.remove("show")
}, 2000)

}