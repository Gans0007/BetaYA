import { renderChallengePath } from "./challenge_path.js"
import { getChallenges } from "../api.js"
import { openChallengeBook } from "./challenge_book.js"

export async function openLevelsPage(){

    if(document.getElementById("levels-overlay")) return

    document.body.style.overflow = "hidden"

    // 🔥 1. СНАЧАЛА грузим данные
    let modules = []

    try{
        const data = await getChallenges(window.initData)
        modules = data?.modules || []
    }catch(err){
        console.error("Levels load error:", err)
    }

    // 🔥 2. ТОЛЬКО ПОТОМ создаём overlay
    const overlay = document.createElement("div")
    overlay.id = "levels-overlay"
    overlay.className = "levels-overlay hidden"

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

    // 🔥 3. сразу вставляем готовый контент
    modules.forEach(module => {

        const locked = !module.is_unlocked

        const div = document.createElement("div")
        div.className = "challenge-level-card"

        if(locked) div.classList.add("locked")

        div.innerHTML = `
            <div class="level-left">
                <div class="level-title">${module.level_name}</div>
            </div>

            <div class="level-right">
                <div class="level-stars ${locked ? "locked" : ""}">
                    ${locked ? "🔒 " : ""}${module.required_stars} ⭐
                </div>
            </div>
        `

        content.appendChild(div)
    })

    // 🔥 4. открываем как профиль
    overlay.classList.remove("hidden")

    setTimeout(() => {
        overlay.classList.add("active")
    }, 10)

    // 🔥 закрытие
    function close(){
        overlay.classList.remove("active")

        setTimeout(() => {
            overlay.remove()
        }, 250)

        document.body.style.overflow = ""
    }

    overlay.querySelector(".levels-close").onclick = close

    overlay.addEventListener("click", (e) => {
        if(e.target === overlay){
            close()
        }
    })

    document.addEventListener("keydown", function escHandler(e){
        if(e.key === "Escape"){
            close()
            document.removeEventListener("keydown", escHandler)
        }
    })
}

// =========================
// 🔥 ОСНОВНАЯ ЛОГИКА
// =========================

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

        // =========================
        // 🔒 LOCKED LEVEL
        // =========================
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

        // =========================
        // 🏷️ ЗАГОЛОВОК УРОВНЯ
        // =========================
        const title = document.createElement("div")
        title.className = "challenge-module-title"
        title.innerText = module.level_name

        root.appendChild(title)

        // =========================
        // 🎮 КАРТОЧКИ ЧЕЛЛЕНДЖЕЙ
        // =========================
        module.challenges.forEach(challenge => {

            const section = challenge.current_section

            const doneDays = challenge.progress?.done_days || 0
            const isActive = challenge.progress?.is_active
            const currentDay = isActive ? doneDays : 0

            const card = document.createElement("div")

            let stateClass = ""

            if(isActive){
                stateClass = "active"
            } else if(doneDays >= section.days){
                stateClass = "done"
            }

card.className = `challenge-card ${stateClass}`

            // 🔥 ПУТЬ
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
                <div class="challenge-card-header">
                    <div>
                        <div class="challenge-title">${challenge.title}</div>
                        <div class="challenge-sub">
                            ${section.days} дней • ⭐ ${section.section}
                        </div>
                    </div>

                    <div class="challenge-btn">📘</div>
                </div>
            `

            card.appendChild(path)

            // 📘
            card.querySelector(".challenge-btn").onclick = (e)=>{
                e.stopPropagation()
                openChallengeBook(dataForBook)
            }

            root.appendChild(card)
        })
    })
}

window.renderChallenges = renderChallenges