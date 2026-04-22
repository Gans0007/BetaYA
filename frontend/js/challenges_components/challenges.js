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
    const challengeMap = []

    modules.forEach((module) => {

        // ❌ убрали вывод "Перепрошивка"
        // (ты просил не показывать)

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

        // ✅ челленджи
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

            // 🔥 сохраняем позицию
            challengeMap.push({
                element: wrapper,
                data: {
                    level: module.level_name,
                    title: challenge.title,
                    section: section.section
                }
            })

        })

    })

    // =========================
    // 📌 STICKY CARD
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
    // 🧠 SCROLL (FIXED)
    // =========================

    const scrollContainer = document.querySelector("#challenges-page .page-content")

    function handleScroll(){

        if(!challengeMap.length) return

        let current = challengeMap[0]

        challengeMap.forEach(item => {

            const rect = item.element.getBoundingClientRect()

            // 🔥 момент переключения (под карточкой)
            if(rect.top <= 140){
                current = item
            }

        })

        updateStickyCard(current.data)
    }

    // 🔥 ВАЖНО: слушаем НЕ window
    scrollContainer.addEventListener("scroll", handleScroll)

    // старт
    if(challengeMap.length){
        updateStickyCard(challengeMap[0].data)
    }
}