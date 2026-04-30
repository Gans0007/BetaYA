import { renderChallengePath } from "./challenge_path.js"
import { getChallenges } from "../api.js"

export function openLevelsPage(){

    // 🔥 если уже открыт — не создаём второй
    if(document.getElementById("levels-overlay")) return

    // 🔥 блокируем скролл фона
    document.body.style.overflow = "hidden"

    const overlay = document.createElement("div")
    overlay.id = "levels-overlay"

    overlay.innerHTML = `
        <div class="levels-modal">

            <div class="levels-header">
                <div class="levels-title">Уровни</div>
                <div class="levels-close">✕</div>
            </div>

            <div class="levels-content"></div>

        </div>
    `

    document.body.appendChild(overlay)

    const content = overlay.querySelector(".levels-content")

    const levels = [
        { name: "⚡ Перепрошивка", stars: 0 },
        { name: "Активность", stars: 10 },
        { name: "Фокус и энергия", stars: 22 },
        { name: "Самодисциплина", stars: 36 },
        { name: "Преодоление", stars: 52 },
        { name: "Для будущих предпринимателей", stars: 70 }
    ]

    const userStars = window.userStars || 0

    levels.forEach(level => {

        const locked = userStars < level.stars

        const div = document.createElement("div")
        div.className = "challenge-level-card"

        if(locked){
            div.classList.add("locked")
        }

        div.innerHTML = `
            <div class="level-left">
                <div class="level-title">${level.name}</div>
            </div>

            <div class="level-right">
                <div class="level-stars ${locked ? "locked" : ""}">
                    ${locked ? "🔒 " : ""}${level.stars} ⭐
                </div>
            </div>
        `

        content.appendChild(div)
    })

    // =========================
    // 🔥 ЗАКРЫТИЕ
    // =========================

    function closeOverlay(){
        overlay.remove()
        document.body.style.overflow = ""
    }

    // крестик
    overlay.querySelector(".levels-close").onclick = closeOverlay

    // клик по фону
    overlay.addEventListener("click", (e) => {
        if(e.target.id === "levels-overlay"){
            closeOverlay()
        }
    })
}
// =========================
// 🔥 ОСНОВНАЯ ЛОГИКА
// =========================

export async function renderChallenges(){

    const root = document.getElementById("challenges-root")
    const sticky = document.getElementById("challenge-sticky-card")

    if(!root) return

    root.innerHTML = "Загрузка..."

    const data = await getChallenges(window.initData)

    if(!data){
        root.innerHTML = "Ошибка загрузки"
        return
    }

    root.innerHTML = ""

    const modules = data.modules || []
    const challengeMap = []

    modules.forEach((module) => {

        if (!module.is_unlocked) {

            const lockCard = document.createElement("div")
            lockCard.className = "challenge-locked-card"

            lockCard.innerHTML = `
                <div class="locked-title">🔒 Уровень</div>
                <div class="locked-name">${module.level_name}</div>

                <div class="locked-desc">
                    Выполняй более сложные задания<br>
                    получай большие награды
                </div>

                <div class="locked-stars">
                    Нужно: ⭐ ${module.required_stars}
                </div>
            `

            root.appendChild(lockCard)
            return
        }

        module.challenges.forEach((challenge, index) => {

            const section = challenge.current_section

            const doneDays = challenge.progress?.done_days || 0
            const isActive = challenge.progress?.is_active

            const currentDay = isActive ? doneDays : 0

            const wrapper = document.createElement("div")
            wrapper.className = "challenge-block"

            const path = renderChallengePath({
                days: section.days,
                currentDay: currentDay
            })

            wrapper.appendChild(path)
            root.appendChild(wrapper)

            if(index < module.challenges.length - 1){

                const sep = document.createElement("div")
                sep.className = "challenge-separator"

                sep.innerHTML = `
                    <div class="challenge-sep-line"></div>
                    <div class="challenge-sep-text">
                        ${module.level_name}: ${challenge.title}
                    </div>
                    <div class="challenge-sep-line"></div>
                `

                root.appendChild(sep)

                challengeMap.push({
                    element: sep,
                    data: {
                        level: module.level_name,
                        title: challenge.title,
                        section: section.section
                    }
                })
            }

            if(index === module.challenges.length - 1){
                challengeMap.push({
                    element: wrapper,
                    data: {
                        level: module.level_name,
                        title: challenge.title,
                        section: section.section
                    }
                })
            }

        })
    })

    // =========================
    // 🔥 СТИКИ КАРТОЧКА
    // =========================

    function updateStickyCard(data){
        if(!sticky) return

        sticky.innerHTML = `
            <div class="challenge-card">
                <div class="challenge-card-left">

                    <div class="challenge-module">
                        ${data.level}, Раздел ${data.section}
                    </div>

                    <div class="challenge-title">
                        ${data.title}
                    </div>

                </div>

                <div class="challenge-card-right">
                    <div class="challenge-btn">📘</div>
                </div>
            </div>
        `

        // 🔥 ВОТ ОНО — КЛИК ПО КАРТОЧКЕ
        const card = sticky.querySelector(".challenge-card")

        if(card){
            card.addEventListener("click", (e) => {

                // ❗ не трогаем кнопку 📘
                if(e.target.closest(".challenge-btn")) return

                openLevelsPage()
            })
        }
    }

    const scrollContainer = document.querySelector("#challenges-page .page-content")

    function handleScroll(){

        if(!challengeMap.length) return

        const stickyEl = document.getElementById("challenge-sticky-card")
        const stickyBottom = stickyEl.getBoundingClientRect().bottom

        let current = challengeMap[0]

        challengeMap.forEach(item => {

            const rect = item.element.getBoundingClientRect()

            if(rect.top <= stickyBottom){
                current = item
            }

        })

        updateStickyCard(current.data)
    }

    if(scrollContainer){
        scrollContainer.removeEventListener("scroll", handleScroll)
        scrollContainer.addEventListener("scroll", handleScroll)
    }

    if(challengeMap.length){
        updateStickyCard(challengeMap[0].data)
    }
}