import { renderHeatmap } from "../components/heatmap.js"
import { renderGraph } from "../components/graph.js"

let userProfileOverlay = null

export function initUserProfileModal(){

    if(userProfileOverlay) return

    userProfileOverlay = document.createElement("div")
    userProfileOverlay.className = "profile-overlay hidden"

    userProfileOverlay.innerHTML = `
    <div class="profile-modal">

        <div class="profile-modal-header">
            <div class="profile-header-left">
                <img id="external-avatar" class="profile-avatar" src="img/avatar/avatar_1.png">
                <div>
                    <div class="profile-name">...</div>
                    <div class="profile-sub">...</div>
                </div>
            </div>
            <div class="profile-close">✕</div>
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
                <div class="heatmap"></div>
            </div>

            <div class="profile-section">
                <div class="section-title">Прогресс</div>
                <canvas class="graph"></canvas>
            </div>

        </div>

    </div>
    `

    document.body.appendChild(userProfileOverlay)

    const closeBtn = userProfileOverlay.querySelector(".profile-close")
    const options = userProfileOverlay.querySelectorAll(".period-option")
    const bg = userProfileOverlay.querySelector(".switcher-bg")

    const state = {
        isOpen: false,
        isLoading: false,
        requestId: 0,
        userId: null,
        range: "month",
        cache: {}
    }

    bg.style.transform = `translateX(100%)`

    options.forEach((opt, index) => {
        opt.addEventListener("click", () => {

            if(!state.userId) return
            if(state.range === opt.dataset.period && state.isOpen) return

            options.forEach(o => o.classList.remove("active"))
            opt.classList.add("active")

            state.range = opt.dataset.period
            bg.style.transform = `translateX(${index * 100}%)`

            loadUserProfile()
        })
    })

    closeBtn.addEventListener("click", closeModal)

    userProfileOverlay.addEventListener("click", (e) => {
        if(e.target === userProfileOverlay){
            closeModal()
        }
    })

    document.addEventListener("keydown", (e) => {
        if(e.key === "Escape" && state.isOpen){
            closeModal()
        }
    })

    function closeModal(){
        if(!state.isOpen) return

        state.isOpen = false
        userProfileOverlay.classList.remove("active")

        setTimeout(() => {
            userProfileOverlay.classList.add("hidden")
        }, 250)

        document.body.style.overflow = ""
    }

    function renderLoadingState(){
        const nameEl = userProfileOverlay.querySelector(".profile-name")
        const subEl = userProfileOverlay.querySelector(".profile-sub")
        const avatarEl = userProfileOverlay.querySelector("#external-avatar")
        const donut = userProfileOverlay.querySelector(".donut")
        const completedEl = userProfileOverlay.querySelector(".completed-val")
        const missedEl = userProfileOverlay.querySelector(".missed-val")
        const pointer = userProfileOverlay.querySelector(".gauge-pointer")
        const valueEl = userProfileOverlay.querySelector(".gauge-value")
        const labelEl = userProfileOverlay.querySelector(".gauge-label")

        nameEl.innerText = "Загрузка..."
        subEl.innerText = "..."
        avatarEl.src = "img/avatar/avatar_1.png"

        completedEl.innerText = "..."
        missedEl.innerText = "..."
        valueEl.innerText = "..."
        valueEl.dataset.value = "0"
        labelEl.innerText = "Загрузка..."

        valueEl.style.color = ""
        donut.style.background = "conic-gradient(#2a2d35 0% 100%)"
        pointer.style.transform = "translateX(-50%) rotate(-90deg)"
    }

    function renderErrorState(){
        const nameEl = userProfileOverlay.querySelector(".profile-name")
        const subEl = userProfileOverlay.querySelector(".profile-sub")
        const donut = userProfileOverlay.querySelector(".donut")
        const completedEl = userProfileOverlay.querySelector(".completed-val")
        const missedEl = userProfileOverlay.querySelector(".missed-val")
        const pointer = userProfileOverlay.querySelector(".gauge-pointer")
        const valueEl = userProfileOverlay.querySelector(".gauge-value")
        const labelEl = userProfileOverlay.querySelector(".gauge-label")

        nameEl.innerText = "Ошибка"
        subEl.innerText = "Не удалось загрузить"

        completedEl.innerText = "0"
        missedEl.innerText = "0"
        valueEl.innerText = "0"
        valueEl.dataset.value = "0"
        labelEl.innerText = "Ошибка загрузки"

        donut.style.background = "conic-gradient(#2a2d35 0% 100%)"
        pointer.style.transform = "translateX(-50%) rotate(-90deg)"
    }

    function renderUserProfile(data){

        const nameEl = userProfileOverlay.querySelector(".profile-name")
        const subEl = userProfileOverlay.querySelector(".profile-sub")
        const avatarEl = userProfileOverlay.querySelector("#external-avatar")

        const donut = userProfileOverlay.querySelector(".donut")
        const completedEl = userProfileOverlay.querySelector(".completed-val")
        const missedEl = userProfileOverlay.querySelector(".missed-val")

        const pointer = userProfileOverlay.querySelector(".gauge-pointer")
        const valueEl = userProfileOverlay.querySelector(".gauge-value")
        const labelEl = userProfileOverlay.querySelector(".gauge-label")

        const heatmapContainer = userProfileOverlay.querySelector(".heatmap")
        const graphCanvas = userProfileOverlay.querySelector(".graph")

        if(!data || !data.user || !data.behavior){
            renderErrorState()
            return
        }

        const { user, behavior } = data
        const { completed, missed, index } = behavior

        nameEl.innerText = user.nickname || "Player"
        subEl.innerText = user.league?.name || "—"
        avatarEl.src = `img/avatar/${user.avatar || "avatar_1.png"}`

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

        renderHeatmap(heatmapContainer, data.heatmap || [])
        renderGraph(graphCanvas, data.graph || [])
    }

    async function loadUserProfile(){
        if(!state.userId || state.isLoading) return

        const cacheKey = `${state.userId}_${state.range}`

        // ⚡ если есть кеш — используем сразу
        if(state.cache[cacheKey]){
            renderUserProfile(state.cache[cacheKey])
            return
        }

        if(!state.userId || state.isLoading) return

        state.isLoading = true
        state.requestId += 1

        const currentRequestId = state.requestId

        if(!state.cache[cacheKey]){
            renderLoadingState()
        }

        try{
            const res = await fetch("/api/profile/view", {
                method: "POST",
                headers: { "Content-Type":"application/json" },
                body: JSON.stringify({
                    user_id: state.userId,
                    range: state.range
                })
            })

            const data = await res.json()

            if(data && data.user && data.behavior){
                state.cache[cacheKey] = data
            }

            if(Object.keys(state.cache).length > 50){
                state.cache = {}
            }

            if(currentRequestId !== state.requestId) return

            if(!data || !data.user || !data.behavior){
                renderErrorState()
                return
            }

            renderUserProfile(data)

        }catch(err){
            console.error("User profile load error:", err)

            if(currentRequestId === state.requestId){
                renderErrorState()
            }
        }finally{
            if(currentRequestId === state.requestId){
                state.isLoading = false
            }
        }
    }

    userProfileOverlay._openProfile = async function(userId){

        if(!userId) return

        state.userId = userId
        state.range = "month"
        state.isOpen = true
        state.isLoading = false

        options.forEach(o => o.classList.remove("active"))
        const monthOption = userProfileOverlay.querySelector('.period-option[data-period="month"]')
        if(monthOption) monthOption.classList.add("active")
        bg.style.transform = `translateX(100%)`

        userProfileOverlay.classList.remove("hidden")

        setTimeout(() => {
            userProfileOverlay.classList.add("active")
        }, 10)

        document.body.style.overflow = "hidden"

        await loadUserProfile()
    }
}

export async function openUserProfile(userId){

    if(!userProfileOverlay){
        initUserProfileModal()
    }

    if(!userProfileOverlay || !userProfileOverlay._openProfile) return

    await userProfileOverlay._openProfile(userId)
}

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