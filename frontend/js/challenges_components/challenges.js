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

            let currentDay = 0

            if (isActive) {
                currentDay = doneDays
            }

            const path = renderChallengePath({
                days: section.days,
                currentDay: currentDay
            })

            root.appendChild(card)
            root.appendChild(path)

            if(index < module.challenges.length - 1){
                const sep = document.createElement("div")
                sep.className = "challenge-separator"
                sep.innerText = "— Давай дальше, не останавливайся —"
                root.appendChild(sep)
            }

        })

    })

}