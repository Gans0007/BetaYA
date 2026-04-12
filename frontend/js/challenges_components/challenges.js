import { renderChallengeCard } from "./challenge_card.js"
import { renderChallengePath } from "./challenge_path.js"
import { getChallenges } from "../api.js"

function initChallengesScrollGuard() {
    const scroller = document.querySelector("#challenges-page .page-content")
    if (!scroller) return

    // не вешаем обработчики повторно
    if (scroller.dataset.scrollGuardInit === "1") return
    scroller.dataset.scrollGuardInit = "1"

    let startY = 0

    scroller.addEventListener("touchstart", (e) => {
        if (!e.touches || !e.touches.length) return
        startY = e.touches[0].clientY
    }, { passive: true })

    scroller.addEventListener("touchmove", (e) => {
        if (!e.touches || !e.touches.length) return

        const currentY = e.touches[0].clientY
        const deltaY = currentY - startY

        const scrollTop = scroller.scrollTop
        const maxScrollTop = scroller.scrollHeight - scroller.clientHeight

        const isAtTop = scrollTop <= 0
        const isAtBottom = scrollTop >= maxScrollTop - 1

        // тянем вниз, когда уже самый верх
        if (isAtTop && deltaY > 0) {
            e.preventDefault()
        }

        // тянем вверх, когда уже самый низ
        if (isAtBottom && deltaY < 0) {
            e.preventDefault()
        }
    }, { passive: false })
}

export async function renderChallenges(){

    const root = document.getElementById("challenges-root")
    if(!root) return

    initChallengesScrollGuard()

    root.innerHTML = "Загрузка..."

    const data = await getChallenges(window.initData)

    if(!data){
        root.innerHTML = "Ошибка загрузки"
        return
    }

    root.innerHTML = ""

    const { challenges, progress } = data

    challenges.forEach((challenge, index) => {

        challenge.sections.forEach(section => {

            const card = renderChallengeCard({
                module: 1,
                section: section.section,
                title: challenge.title,
                stars: section.stars
            })

            let currentDay = 0

            if (challenge.id === progress.challenge_id) {
                if (section.section < progress.section) {
                    currentDay = section.days
                } else if (section.section === progress.section) {
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

        if(index < challenges.length - 1){
            const sep = document.createElement("div")
            sep.className = "challenge-separator"
            sep.innerText = "— Давай дальше, не останавливайся —"
            root.appendChild(sep)
        }
    })
}