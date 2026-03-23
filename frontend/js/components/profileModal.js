import { renderHeatmap } from "../components/heatmap.js"
import { renderGraph } from "../components/graph.js"
import { initInfoTooltip } from "../components/infoTooltip.js"

const AVAILABLE_AVATARS = [
    "avatar_1.png",
    "avatar_2.png"
]

const PROFILE_INFO = {
    donut: "Показывает сколько привычек ты выполнил и сколько пропустил за выбранный период.",
    gauge: "Индекс дисциплины — рассчитывается на основе выполнения привычек.",
    heatmap: "Твоя активность по дням. Чем ярче — тем больше выполнено.",
    graph: "Динамика твоего прогресса со временем."
}

export function initProfileModal(){

    if(document.querySelector(".profile-overlay")) return

    const dashboardAvatar = document.getElementById("player-avatar")
    if(!dashboardAvatar) return

    let profileState = {
        isOpen: false,
        range: "month",
        isLoading: false,
        isSavingAvatar: false,
        requestId: 0,
        isAvatarPickerOpen: false
    }

    let profileData = null

    const overlay = document.createElement("div")
    overlay.className = "profile-overlay hidden"

    overlay.innerHTML = `
    <div class="profile-modal">

        <div class="profile-modal-header">
            <div class="profile-header-left">
                <div class="profile-avatar-wrap">
                    <img src="img/avatar/avatar_1.png" class="profile-avatar" id="profile-avatar-image">
                    <div class="profile-avatar-edit">Сменить</div>
                </div>
                <div>
                    <div class="profile-name">Player</div>
                    <div class="profile-sub">...</div>
                </div>
            </div>
            <div class="profile-close">✕</div>
        </div>

        <div class="avatar-picker hidden">
            <div class="avatar-picker-title">Выберите аватар</div>
            <div class="avatar-picker-grid">
                ${AVAILABLE_AVATARS.map(item => `
                    <button class="avatar-option" data-avatar="${item}" type="button">
                        <img src="img/avatar/${item}" alt="${item}">
                    </button>
                `).join("")}
            </div>
        </div>

        <div class="profile-modal-content">

            <div class="period-switcher">
                <div class="switcher-bg"></div>

                <div class="period-option" data-period="week">Еженедельно</div>
                <div class="period-option active" data-period="month">Ежемесячно</div>
                <div class="period-option" data-period="year">Ежегодно</div>
            </div>

<div class="behavior-block">

    <div class="behavior-card">
        <div class="card-header">
            <div class="section-title">Выполнение</div>
            <div class="info-btn" data-info="donut">i</div>
        </div>

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
        <div class="card-header">
            <div class="section-title">Индекс</div>
            <div class="info-btn" data-info="gauge">i</div>
        </div>

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
    <div class="card-header">
        <div class="section-title">Активность</div>
        <div class="info-btn" data-info="heatmap">i</div>
    </div>
    <div class="heatmap"></div>
</div>

<div class="profile-section">
    <div class="card-header">
        <div class="section-title">Прогресс</div>
        <div class="info-btn" data-info="graph">i</div>
    </div>
    <canvas class="graph"></canvas>
</div>

        </div>

    </div>
    `

    document.body.appendChild(overlay)
    initInfoTooltip(PROFILE_INFO)

    const closeBtn = overlay.querySelector(".profile-close")

    const nameEl = overlay.querySelector(".profile-name")
    const subEl = overlay.querySelector(".profile-sub")
    const profileAvatarEl = overlay.querySelector("#profile-avatar-image")
    const profileAvatarWrap = overlay.querySelector(".profile-avatar-wrap")
    const avatarPicker = overlay.querySelector(".avatar-picker")
    const avatarOptions = overlay.querySelectorAll(".avatar-option")

    const donut = overlay.querySelector(".donut")
    const completedEl = overlay.querySelector(".completed-val")
    const missedEl = overlay.querySelector(".missed-val")

    const pointer = overlay.querySelector(".gauge-pointer")
    const valueEl = overlay.querySelector(".gauge-value")
    const labelEl = overlay.querySelector(".gauge-label")
    const heatmapContainer = overlay.querySelector(".heatmap")
    const graphCanvas = overlay.querySelector(".graph")

    const options = overlay.querySelectorAll(".period-option")
    const bg = overlay.querySelector(".switcher-bg")

    bg.style.transform = `translateX(100%)`

    options.forEach((opt, index) => {
        opt.addEventListener("click", () => {
            if(profileState.range === opt.dataset.period && profileData) return

            options.forEach(o => o.classList.remove("active"))
            opt.classList.add("active")

            profileState.range = opt.dataset.period
            bg.style.transform = `translateX(${index * 100}%)`

            loadProfile()
        })
    })

    function getAvatarPath(fileName){
        return `img/avatar/${fileName || "avatar_1.png"}`
    }

    function updateAvatarEverywhere(fileName){
        const safeAvatar = fileName || "avatar_1.png"

        if(profileAvatarEl){
            profileAvatarEl.src = getAvatarPath(safeAvatar)
        }

        if(dashboardAvatar){
            dashboardAvatar.src = getAvatarPath(safeAvatar)
        }

        if(profileData && profileData.user){
            profileData.user.avatar = safeAvatar
        }

        highlightSelectedAvatar(safeAvatar)
    }

    function highlightSelectedAvatar(currentAvatar){
        avatarOptions.forEach(btn => {
            btn.classList.toggle("active", btn.dataset.avatar === currentAvatar)
        })
    }

    function toggleAvatarPicker(forceState = null){
        const nextState = typeof forceState === "boolean"
            ? forceState
            : !profileState.isAvatarPickerOpen

        profileState.isAvatarPickerOpen = nextState
        avatarPicker.classList.toggle("hidden", !nextState)
    }

    async function saveAvatar(newAvatar){
        if(profileState.isSavingAvatar) return
        if(!newAvatar) return
        if(!profileData || !profileData.user) return
        if(profileData.user.avatar === newAvatar) {
            toggleAvatarPicker(false)
            return
        }

        const previousAvatar = profileData.user.avatar || "avatar_1.png"

        profileState.isSavingAvatar = true
        updateAvatarEverywhere(newAvatar)

        try{
            const res = await fetch("/api/profile/avatar", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    initData: window.initData,
                    avatar: newAvatar
                })
            })

            const data = await res.json()

            if(!data || data.status !== "ok"){
                throw new Error(data?.message || "avatar_save_failed")
            }

            updateAvatarEverywhere(data.avatar || newAvatar)
            toggleAvatarPicker(false)

        }catch(err){
            console.error("Avatar save error:", err)
            updateAvatarEverywhere(previousAvatar)
        }finally{
            profileState.isSavingAvatar = false
        }
    }

    avatarOptions.forEach(btn => {
        btn.addEventListener("click", () => {
            saveAvatar(btn.dataset.avatar)
        })
    })

    profileAvatarWrap.addEventListener("click", () => {
        if(!profileState.isOpen) return
        toggleAvatarPicker()
    })

    function renderProfile(){

        if(!profileData || !profileData.user || !profileData.behavior){
            console.error("Profile data is invalid:", profileData)
            return
        }

        renderHeatmap(heatmapContainer, profileData.heatmap)

        const { user, behavior } = profileData
        const { completed, missed, index } = behavior

        nameEl.innerText = user.nickname || "Player"
        subEl.innerText = user.league?.name || "—"
        updateAvatarEverywhere(user.avatar || "avatar_1.png")

        const total = completed + missed || 1
        const percent = (completed / total) * 100

        donut.style.background = `conic-gradient(
            #22c55e 0% ${percent}%,
            #ef4444 ${percent}% 100%
        )`

        completedEl.innerText = completed
        missedEl.innerText = missed

        const safeIndex = Math.max(0, Math.min(100, index))
        const angle = -90 + (safeIndex * 1.8)

        pointer.style.transform = `translateX(-50%) rotate(${angle}deg)`

        const prev = Number(valueEl.dataset.value || 0)
        valueEl.dataset.value = String(safeIndex)
        animateValue(valueEl, prev, safeIndex)

        if(safeIndex < 40) valueEl.style.color = "#ef4444"
        else if(safeIndex < 60) valueEl.style.color = "#facc15"
        else valueEl.style.color = "#22c55e"

        let label = "Баланс"

        if(safeIndex < 20) label = "Критическая лень"
        else if(safeIndex < 40) label = "Лень"
        else if(safeIndex < 60) label = "Баланс"
        else if(safeIndex < 80) label = "Настойчивость"
        else label = "Жесткая дисциплина"

        labelEl.innerText = label

        renderGraph(graphCanvas, profileData.graph)
    }

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

    async function loadProfile(){

        if(profileState.isLoading) return

        profileState.isLoading = true
        profileState.requestId += 1

        const currentRequestId = profileState.requestId

        renderLoadingState()

        try{
            const res = await fetch("/api/profile", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    initData: window.initData,
                    range: profileState.range
                })
            })

            const data = await res.json()

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

    dashboardAvatar.addEventListener("click", () => {

        if(profileState.isOpen) return

        profileState.isOpen = true
        profileState.isAvatarPickerOpen = false
        avatarPicker.classList.add("hidden")

        renderLoadingState()

        overlay.classList.remove("hidden")

        setTimeout(() => {
            overlay.classList.add("active")
        }, 10)

        document.body.style.overflow = "hidden"

        loadProfile()
    })

    function closeModal(){

        if(!profileState.isOpen) return

        profileState.isOpen = false
        profileState.isAvatarPickerOpen = false
        avatarPicker.classList.add("hidden")

        overlay.classList.remove("active")

        setTimeout(() => {
            overlay.classList.add("hidden")
        }, 250)

        document.body.style.overflow = ""
    }

    closeBtn.addEventListener("click", closeModal)

    overlay.addEventListener("click", (e) => {
        if(e.target === overlay){
            closeModal()
        }
    })

    document.addEventListener("keydown", (e) => {
        if(e.key === "Escape" && profileState.isOpen){
            closeModal()
        }
    })

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