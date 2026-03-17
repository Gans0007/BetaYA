import { calculateBehavior } from "../utils/calculations.js"

export function initProfileModal(){

// ==========================
// ЗАЩИТА ОТ ПОВТОРНОЙ ИНИЦИАЛИЗАЦИИ
// ==========================
if(document.querySelector(".profile-overlay")) return

const avatar = document.getElementById("player-avatar")
if(!avatar) return

let habitsData = []

// ==========================
// СОЗДАЕМ MODAL HTML
// ==========================

const overlay = document.createElement("div")
overlay.className = "profile-overlay hidden"

overlay.innerHTML = `
<div class="profile-modal">

    <!-- HEADER -->
    <div class="profile-modal-header">
        <div class="profile-header-left">
            <img src="img/avatar/avatar_1.png" class="profile-avatar">
            <div>
                <div class="profile-name">Player</div>
                <div class="profile-sub">Бронза I</div>
            </div>
        </div>

        <div class="profile-close">✕</div>
    </div>

    <!-- CONTENT -->
    <div class="profile-modal-content">

        <!-- BEHAVIOR BLOCK -->
        <div class="behavior-block">

            <div class="behavior-left">
                <div class="donut-placeholder">0 / 0</div>
                <div class="behavior-label">Выполнено / Пропущено</div>
            </div>

            <div class="behavior-right">
                <div class="gauge-placeholder">0%</div>
                <div class="behavior-label">Настойчивость</div>
            </div>

        </div>

        <!-- HEATMAP -->
        <div class="profile-section">
            <div class="section-title">Активность</div>
            <div class="heatmap-placeholder">Heatmap</div>
        </div>

        <!-- GRAPH -->
        <div class="profile-section">
            <div class="section-title">Прогресс</div>
            <div class="graph-placeholder">Graph</div>
        </div>

    </div>

</div>
`

document.body.appendChild(overlay)

const closeBtn = overlay.querySelector(".profile-close")

// ==========================
// ОБНОВЛЕНИЕ UI
// ==========================

function updateBehaviorUI(){

const { completed, missed, index } = calculateBehavior(habitsData, "month")

const donut = overlay.querySelector(".donut-placeholder")
if(donut){
donut.innerText = `${completed} / ${missed}`
}

const gauge = overlay.querySelector(".gauge-placeholder")
if(gauge){
gauge.innerText = `${index}%`
}

}

// ==========================
// ОТКРЫТИЕ
// ==========================

avatar.addEventListener("click", ()=>{

overlay.classList.remove("hidden")

setTimeout(()=>{
overlay.classList.add("active")
},10)

document.body.style.overflow = "hidden"

// ==========================
// ЗАГРУЗКА HABITS
// ==========================

fetch("/api/habits",{
method:"POST",
headers:{ "Content-Type":"application/json"},
body:JSON.stringify({ initData: window.initData })
})
.then(res => res.json())
.then(data => {

habitsData = data.habits || []
updateBehaviorUI()

})
.catch(err => {
console.error("Habits load error:", err)
})

})

// ==========================
// ЗАКРЫТИЕ
// ==========================

function closeModal(){

overlay.classList.remove("active")

setTimeout(()=>{
overlay.classList.add("hidden")
},250)

document.body.style.overflow = ""

}

// крестик
closeBtn.addEventListener("click", closeModal)

// клик вне
overlay.addEventListener("click",(e)=>{
if(e.target === overlay){
closeModal()
}
})

// ESC (фикс!)
document.addEventListener("keydown",(e)=>{
if(e.key === "Escape"){
closeModal()
}
})

}