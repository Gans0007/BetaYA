export function initProfileModal(){

// защита
if(document.querySelector(".profile-overlay")) return

const avatar = document.getElementById("player-avatar")
if(!avatar) return

// ==========================
// STATE
// ==========================

let profileState = {
    isOpen: false,
    range: "month",
    isLoading: false,
    requestId: 0
}

let profileData = null

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

            <div class="period-option" data-period="week">Еженедельно</div>
            <div class="period-option active" data-period="month">Ежемесячно</div>
            <div class="period-option" data-period="year">Ежегодно</div>
        </div>

        <div class="behavior-block">

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

            <div class="behavior-card">
                <div class="gauge">
                    <div class="gauge-semicircle">
                        <div class="gauge-arc"></div>
                        <div class="gauge-pointer"></div>
                    </div>

                    <div class="gauge-info">
                        <div class="gauge-value" data-value="0">0</div>
                        <div class="gauge-label">Нейтрально</div>
                    </div>
                </div>
            </div>

        </div>

        <div class="profile-section">
            <div class="section-title">Активность</div>
            <div class="heatmap-placeholder">Heatmap</div>
        </div>

        <div class="profile-section">
            <div class="section-title">Прогресс</div>
            <div class="graph-placeholder">Graph</div>
        </div>

    </div>

</div>
`

document.body.appendChild(overlay)

// ==========================
// CACHE DOM
// ==========================

const closeBtn = overlay.querySelector(".profile-close")

const nameEl = overlay.querySelector(".profile-name")
const subEl = overlay.querySelector(".profile-sub")

const donut = overlay.querySelector(".donut")
const completedEl = overlay.querySelector(".completed-val")
const missedEl = overlay.querySelector(".missed-val")

const pointer = overlay.querySelector(".gauge-pointer")
const valueEl = overlay.querySelector(".gauge-value")
const labelEl = overlay.querySelector(".gauge-label")

const options = overlay.querySelectorAll(".period-option")
const bg = overlay.querySelector(".switcher-bg")

// стартовая позиция (month = центр)
bg.style.transform = `translateX(100%)`

// ==========================
// SWITCHER
// ==========================

options.forEach((opt, index) => {
    opt.addEventListener("click", () => {

        // не дергаем повторно тот же range
        if(profileState.range === opt.dataset.period && profileData) return

        options.forEach(o => o.classList.remove("active"))
        opt.classList.add("active")

        profileState.range = opt.dataset.period
        bg.style.transform = `translateX(${index * 100}%)`

        loadProfile()
    })
})

// ==========================
// RENDER
// ==========================

function renderProfile(){

    if(!profileData || !profileData.user || !profileData.behavior){
        console.error("Profile data is invalid:", profileData)
        return
    }

    const { user, behavior } = profileData
    const { completed, missed, index } = behavior

    // ===== USER =====

    nameEl.innerText = user.nickname || "Player"
    subEl.innerText = user.league?.name || "—"

    // ===== DONUT =====

    const total = completed + missed || 1
    const percent = (completed / total) * 100

    donut.style.background = `conic-gradient(
        #22c55e 0% ${percent}%,
        #ef4444 ${percent}% 100%
    )`

    completedEl.innerText = completed
    missedEl.innerText = missed

    // ===== GAUGE =====

    const safeIndex = Math.max(0, Math.min(100, index))
    const angle = -90 + (safeIndex * 1.8)

    pointer.style.transform = `translateX(-50%) rotate(${angle}deg)`

    const prev = Number(valueEl.dataset.value || 0)
    valueEl.dataset.value = String(safeIndex)
    animateValue(valueEl, prev, safeIndex)

    if(safeIndex < 40) valueEl.style.color = "#ef4444"
    else if(safeIndex < 60) valueEl.style.color = "#facc15"
    else valueEl.style.color = "#22c55e"

    // ===== LABEL =====

    let label = "Баланс"

    if(safeIndex < 20) label = "Критическая лень"
    else if(safeIndex < 40) label = "Лень"
    else if(safeIndex < 60) label = "Баланс"
    else if(safeIndex < 80) label = "Настойчивость"
    else label = "Жесткая дисциплина"

    labelEl.innerText = label
}

// ==========================
// LOADING UI
// ==========================

function renderLoadingState(){
    completedEl.innerText = "..."
    missedEl.innerText = "..."
    valueEl.innerText = "..."
    labelEl.innerText = "Загрузка..."
    nameEl.innerText = "Загрузка..."
    subEl.innerText = "..."

    valueEl.style.color = ""
    donut.style.background = "conic-gradient(#2a2d35 0% 100%)"
    pointer.style.transform = "translateX(-50%) rotate(-90deg)"
}

function renderErrorState(){
    completedEl.innerText = "0"
    missedEl.innerText = "0"
    valueEl.innerText = "0"
    valueEl.dataset.value = "0"
    labelEl.innerText = "Ошибка загрузки"
    donut.style.background = "conic-gradient(#2a2d35 0% 100%)"
    pointer.style.transform = "translateX(-50%) rotate(-90deg)"
}

// ==========================
// LOADER
// ==========================

async function loadProfile(){

    if(profileState.isLoading) return

    profileState.isLoading = true
    profileState.requestId += 1

    const currentRequestId = profileState.requestId

    renderLoadingState()

    try{
        const res = await fetch("/api/profile",{
            method:"POST",
            headers:{ "Content-Type":"application/json"},
            body: JSON.stringify({
                initData: window.initData,
                range: profileState.range
            })
        })

        const data = await res.json()

        // если уже ушел новый запрос — этот игнорируем
        if(currentRequestId !== profileState.requestId) return

        if(!data || !data.user || !data.behavior){
            console.error("Invalid /api/profile response:", data)
            renderErrorState()
            return
        }

        profileData = data
        renderProfile()

    }catch(err){
        console.error("Profile load error:", err)

        if(currentRequestId === profileState.requestId){
            renderErrorState()
        }
    }finally{
        if(currentRequestId === profileState.requestId){
            profileState.isLoading = false
        }
    }
}

// ==========================
// OPEN
// ==========================

avatar.addEventListener("click", ()=>{

    if(profileState.isOpen) return

    profileState.isOpen = true

    renderLoadingState()

    overlay.classList.remove("hidden")

    setTimeout(()=>{
        overlay.classList.add("active")
    },10)

    document.body.style.overflow = "hidden"

    loadProfile()
})

// ==========================
// CLOSE
// ==========================

function closeModal(){

    if(!profileState.isOpen) return

    profileState.isOpen = false

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
    if(e.key === "Escape" && profileState.isOpen){
        closeModal()
    }
})

// ==========================
// UTILS
// ==========================

function animateValue(el, start, end, duration = 500){

    if(start === end){
        el.innerText = end
        return
    }

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
}