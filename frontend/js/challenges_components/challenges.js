import { renderChallengePath } from "./challenge_path.js"
import { getChallenges } from "../api.js"
import { openChallengeBook } from "./challenge_book.js"

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

    modules.forEach(module => {

        if(!module.is_unlocked){
            const lock = document.createElement("div")
            lock.className = "challenge-locked-card"

            lock.innerHTML = `
                <div class="locked-title">🔒 Уровень</div>
                <div class="locked-name">${module.level_name}</div>
                <div class="locked-stars">⭐ ${module.required_stars}</div>
            `

            root.appendChild(lock)
            return
        }

        const title = document.createElement("div")
        title.className = "challenge-module-title"
        title.innerText = module.level_name

        root.appendChild(title)

        module.challenges.forEach(challenge => {

            const section = challenge.current_section

            const doneDays = challenge.progress?.done_days || 0
            const isActive = challenge.progress?.is_active
            const currentDay = isActive ? doneDays : 0

            const card = document.createElement("div")

            let stateClass = ""
            if(isActive) stateClass = "active"
            else if(doneDays >= section.days) stateClass = "done"

            card.className = `challenge-card ${stateClass}`

            const path = renderChallengePath({
                days: section.days,
                currentDay: currentDay
            })

            const dataForBook = {
                id: challenge.id,
                title: challenge.title,
                difficulty: challenge.difficulty,
                days: challenge.days,
                description: challenge.description,
                isActive: isActive
            }

            card.innerHTML = `
                <div class="challenge-title">${challenge.title}</div>
                <div class="challenge-sub">
                    ${section.days} дней • ⭐ ${section.section}
                </div>

                <div class="challenge-row">
                    <div class="challenge-path-wrapper"></div>

                    <div class="challenge-book-fixed">
                        <img src="/img/nodes/about_button.png"/>
                    </div>
                </div>
            `

            // вставляем путь внутрь
            card.querySelector(".challenge-path-wrapper").appendChild(path)

            // 📘
            card.querySelector(".challenge-book-fixed").onclick = (e)=>{
                e.stopPropagation()
                openChallengeBook(dataForBook)
            }

            root.appendChild(card)
        })
    })
}

window.renderChallenges = renderChallenges