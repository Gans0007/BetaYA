import { renderChallengeCard } from "./challenge_card.js"
import { renderChallengePath } from "./challenge_path.js"
import { getChallenges } from "../api.js"

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

    // 🔥 карта для отслеживания скролла
    const challengeMap = []

    modules.forEach((module) => {

        const title = document.createElement("div")
        title.className = "challenge-module-title"
        title.innerText = module.level_name
        root.appendChild(title)

        // 🔒 закрытый уровень
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

        // ✅ открытый уровень
        module.challenges.forEach((challenge, index) => {

            const section = challenge.current_section

            const doneDays = challenge.progress?.done_days || 0
            const isActive = challenge.progress?.is_active

            let currentDay = isActive ? doneDays : 0

            const wrapper = document.createElement("div")
            wrapper.className = "challenge-block"

            const path = renderChallengePath({
                days: section.days,
                currentDay: currentDay
            })

            wrapper.appendChild(path)
            root.appendChild(wrapper)

            // 🔥 сохраняем для sticky логики
            challengeMap.push({
                element: wrapper,
                data: {
                    level: module.level_name,
                    title: challenge.title,
                    section: section.section
                }
            })

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
            }

        })

    })

    // =========================
    // 📌 STICKY CARD UPDATE
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
    }

    // =========================
    // 🧠 SCROLL LOGIC
    // =========================

    function handleScroll(){

        let current = challengeMap[0]

        challengeMap.forEach(item => {
            const rect = item.element.getBoundingClientRect()

            if(rect.top <= 120){
                current = item
            }
        })

        if(current){
            updateStickyCard(current.data)
        }
    }

    window.addEventListener("scroll", handleScroll)

    // стартовое состояние
    if(challengeMap.length){
        updateStickyCard(challengeMap[0].data)
    }

}