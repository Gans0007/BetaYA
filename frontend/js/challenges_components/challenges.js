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

    // 🔥 поддержка и нового API (modules) и старого (challenges)
    const modules = data.modules || [{
        level_name: "Челленджи",
        challenges: data.challenges || []
    }]

    const progress = data.progress || {}

    modules.forEach((module) => {

        // 🔥 заголовок уровня (модуля)
        const title = document.createElement("div")
        title.className = "challenge-module-title"
        title.innerText = module.level_name
        root.appendChild(title)

        module.challenges.forEach((challenge, index) => {

            challenge.sections.forEach(section => {

                const card = renderChallengeCard({
                    module: module.level_name,
                    section: section.section,
                    title: challenge.title,
                    stars: section.stars
                })

                let currentDay = 0

                // 🔥 определяем прогресс
                if (challenge.id === progress.challenge_id) {

                    if (section.section < progress.section) {
                        currentDay = section.days
                    } 
                    else if (section.section === progress.section) {
                        currentDay = progress.day
                    }

                }

                const path = renderChallengePath({
                    days: section.days,
                    currentDay: currentDay
                })

                root.appendChild(card)
                root.appendChild(path)
            })

            // 🔥 разделитель между челленджами
            if(index < module.challenges.length - 1){
                const sep = document.createElement("div")
                sep.className = "challenge-separator"
                sep.innerText = "— Давай дальше, не останавливайся —"
                root.appendChild(sep)
            }

        })

    })

}