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
                <div class="profile-sub">Бронза I</div>
            </div>
        </div>
        <div class="profile-close">✕</div>
    </div>

    <!-- CONTENT -->
    <div class="profile-modal-content">

        <div class="behavior-block">

            <!-- LEFT: DONUT -->
            <div class="behavior-card">

                <div class="donut">
                    <div class="donut-inner">
                        <span class="donut-text">0 / 0</span>
                    </div>
                </div>

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

                    <div class="gauge-arc"></div>
                    <div class="gauge-pointer" id="gauge-pointer"></div>

                    <div class="gauge-center">
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

const donut = overlay.querySelector(".donut")
if(donut){
donut.style.background = `conic-gradient(
#22c55e 0% ${percent}%,
#ef4444 ${percent}% 100%
)`
}

overlay.querySelector(".donut-text").innerText = `${completed} / ${missed}`
overlay.querySelector(".completed-val").innerText = completed
overlay.querySelector(".missed-val").innerText = missed

// ===== GAUGE =====

const pointer = overlay.querySelector("#gauge-pointer")
const valueEl = overlay.querySelector(".gauge-value")
const labelEl = overlay.querySelector(".gauge-label")

if(pointer){
const angle = -90 + (index * 1.8)
pointer.style.transform = `translate(-50%, -100%) rotate(${angle}deg)`
}

if(valueEl){
valueEl.innerText = index
}

// состояние
let label = "Нейтрально"

if(index < 20) label = "Макс. лень"
else if(index < 40) label = "Лень"
else if(index < 60) label = "Нейтрально"
else if(index < 80) label = "Настойчивость"
else label = "Экстрем. Настойчивость"

if(labelEl){
labelEl.innerText = label
}

}

// ==========================
// OPEN
// ==========================

avatar.addEventListener("click", ()=>{

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