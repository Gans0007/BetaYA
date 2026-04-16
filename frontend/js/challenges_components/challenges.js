import { renderChallengeCard } from "./challenge_card.js"
import { renderChallengePath } from "./challenge_path.js"
import { getChallenges } from "../api.js"

export async function renderChallenges(){

    const root = document.getElementById("challenges-root")
    if(!root) return

    root.innerHTML = "Загрузка..."

    const data = await getChallenges(window.initData)

    if(!data){
        root.innerHTML = "Ошибка загрузки"
        return
    }

    root.innerHTML = ""

    const modules = data.modules || []

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

            const card = renderChallengeCard({
                module: module.level_name,
                section: section.section,
                title: challenge.title,
                stars: section.stars
            })

            const doneDays = challenge.progress?.done_days || 0
            const isActive = challenge.progress?.is_active

            let currentDay = isActive ? doneDays : 0

            const path = renderChallengePath({
                days: section.days,
                currentDay: currentDay
            })

            root.appendChild(card)
            root.appendChild(path)

            if(index < module.challenges.length - 1){
                const sep = document.createElement("div")
                sep.className = "challenge-separator"
                sep.innerText = "— Давай дальше —"
                root.appendChild(sep)
            }

        })

    })

}