import { renderChallengeCard } from "./challenge_card.js"
import { renderChallengePath } from "./challenge_path.js"
import { getChallenges } from "../api.js"

function initChallengesScrollGuard() {
    const scroller = document.querySelector("#challenges-page .page-content")
    if (!scroller) return

    if (scroller.dataset.scrollGuardInit === "1") return
    scroller.dataset.scrollGuardInit = "1"

    let startY = 0

    scroller.addEventListener("touchstart", (e) => {
        if (!e.touches || !e.touches.length) return

        startY = e.touches[0].clientY

        const maxScroll = scroller.scrollHeight - scroller.clientHeight
        if (maxScroll <= 0) return

        // 👇 уводим scroll на 1px от границ,
        // чтобы iOS/Telegram не схватывал жест сворачивания сразу
        if (scroller.scrollTop <= 0) {
            scroller.scrollTop = 1
        } else if (scroller.scrollTop >= maxScroll) {
            scroller.scrollTop = maxScroll - 1
        }
    }, { passive: true })

    scroller.addEventListener("touchmove", (e) => {
        if (!e.touches || !e.touches.length) return

        const maxScroll = scroller.scrollHeight - scroller.clientHeight
        if (maxScroll <= 0) return

        const currentY = e.touches[0].clientY
        const deltaY = currentY - startY

        const atTop = scroller.scrollTop <= 0
        const atBottom = scroller.scrollTop >= maxScroll

        // тянем вниз на самом верху
        if (atTop && deltaY > 0) {
            e.preventDefault()
        }

        // тянем вверх на самом низу
        if (atBottom && deltaY < 0) {
            e.preventDefault()
        }
    }, { passive: false })
}

export async function renderChallenges() {
    const root = document.getElementById("challenges-root")
    if (!root) return

    root.innerHTML = "Загрузка..."

    const data = await getChallenges(window.initData)

    if (!data) {
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

        if (index < challenges.length - 1) {
            const sep = document.createElement("div")
            sep.className = "challenge-separator"
            sep.innerText = "— Давай дальше, не останавливайся —"
            root.appendChild(sep)
        }
    })

    requestAnimationFrame(() => {
        initChallengesScrollGuard()
    })
}