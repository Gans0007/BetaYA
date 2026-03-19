import { calculateBehavior } from "../utils/calculations.js"

export function initProfileModal(){

// защита
if(document.querySelector(".profile-overlay")) return

const avatar = document.getElementById("player-avatar")
if(!avatar) return

let habitsData = []

// ==========================
// HTML
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
                <div class="profile-sub">...</div>
            </div>
        </div>
        <div class="profile-close">✕</div>
    </div>

    <!-- CONTENT -->
    <div class="profile-modal-content">
    <div class="period-switcher">
        <div class="switcher-bg"></div>

        <div class="period-option active" data-period="week">Еженедельно</div>
        <div class="period-option" data-period="month">Ежемесячно</div>
        <div class="period-option" data-period="year">Ежегодно</div>
    </div>

        <div class="behavior-block">

            <!-- LEFT: DONUT -->
            <div class="behavior-card">

                <div class="donut"></div>

                <div class="donut-legend">
                    <div class="legend-item green">
                        <span></span> Выполнено: <b class="completed-val">0</b>
                    </div>
                    <div class="legend-item red">
                        <span></span> Пропущено: <b class="missed-val">0</b>
                    </div>
                </div>

            </div>

            <!-- RIGHT: GAUGE -->
            <div class="behavior-card">

                <div class="gauge">

                    <div class="gauge-semicircle">
                        <div class="gauge-arc"></div>
                        <div class="gauge-pointer" id="gauge-pointer"></div>
                    </div>

                    <div class="gauge-info">
                        <div class="gauge-value">0</div>
                        <div class="gauge-label">Нейтрально</div>
                    </div>

                </div>

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
// UI UPDATE
// ==========================

function updateBehaviorUI(){

const { completed, missed, index } = calculateBehavior(habitsData, "month")

// ===== DONUT =====

const total = completed + missed || 1
const percent = (completed / total) * 100

// небольшой gap между секторами
const gap = 1.5
const greenEnd = Math.max(0, percent - gap)
const redStart = Math.min(100, percent + gap)

const donut = overlay.querySelector(".donut")
if(donut){
donut.style.background = `conic-gradient(
#22c55e 0% ${percent}%,
#ef4444 ${percent}% 100%
)`
}

overlay.querySelector(".completed-val").innerText = completed
overlay.querySelector(".missed-val").innerText = missed

// ===== GAUGE FINAL =====

const pointer = overlay.querySelector("#gauge-pointer")
const valueEl = overlay.querySelector(".gauge-value")
const labelEl = overlay.querySelector(".gauge-label")

const safeIndex = Math.max(0, Math.min(100, index))

// угол (180°)
const angle = -90 + (safeIndex * 1.8)

// стрелка
if(pointer){
pointer.style.transform = `translateX(-50%) rotate(${angle}deg)`
}

// ===== АНИМАЦИЯ ЧИСЛА =====

function animateValue(el, start, end, duration = 500){
let startTime = null

function step(timestamp){
if(!startTime) startTime = timestamp
const progress = Math.min((timestamp - startTime) / duration, 1)

const value = Math.floor(progress * (end - start) + start)
el.innerText = value

if(progress < 1){
requestAnimationFrame(step)
}
}

requestAnimationFrame(step)
}

if(valueEl){
const prev = parseInt(valueEl.innerText) || 0
animateValue(valueEl, prev, safeIndex)

// цвет
if(safeIndex < 40) valueEl.style.color = "#ef4444"
else if(safeIndex < 60) valueEl.style.color = "#facc15"
else valueEl.style.color = "#22c55e"
}

// ===== СТАТУС =====

let label = "Баланс"

if(safeIndex < 20) label = "Критическая лень"
else if(safeIndex < 40) label = "Лень"
else if(safeIndex < 60) label = "Баланс"
else if(safeIndex < 80) label = "Настойчивость"
else label = "Жесткая дисциплина"

if(labelEl){
labelEl.innerText = label
}

}

// ==========================
// OPEN
// ==========================

avatar.addEventListener("click", ()=>{

// ===== USER DATA =====
fetch("/api/user",{
method:"POST",
headers:{ "Content-Type":"application/json"},
body:JSON.stringify({ initData: window.initData })
})
.then(res => res.json())
.then(user => {

const nameEl = overlay.querySelector(".profile-name")
const subEl = overlay.querySelector(".profile-sub")

if(nameEl) nameEl.innerText = user.nickname || "Player"
if(subEl) subEl.innerText = user.league.name

})
.catch(err => {
console.error("User load error:", err)
})



overlay.classList.remove("hidden")

setTimeout(()=>{
overlay.classList.add("active")
},10)

document.body.style.overflow = "hidden"

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
// CLOSE
// ==========================

function closeModal(){

overlay.classList.remove("active")

setTimeout(()=>{
overlay.classList.add("hidden")
},250)

document.body.style.overflow = ""

}

closeBtn.addEventListener("click", closeModal)

overlay.addEventListener("click",(e)=>{
if(e.target === overlay){
closeModal()
}
})

document.addEventListener("keydown",(e)=>{
if(e.key === "Escape"){
closeModal()
}
})

}