import { openLevelsPage } from "../modules/challenges.js"

export function renderChallengeCard(data){

    const div = document.createElement("div")
    div.className = "challenge-card"

    div.innerHTML = `
        <div class="challenge-card-left">

            <div class="challenge-module">
                Уровень ${data.module}, Раздел ${data.section}
            </div>

            <div class="challenge-title">
                ${data.title}
            </div>

        </div>

        <div class="challenge-card-right">
            <div class="challenge-btn">
                📘
            </div>
        </div>
    `

    // 🔥 КЛИК ПО КАРТОЧКЕ (НЕ ПО 📘)
    div.addEventListener("click", (e) => {
        if(e.target.closest(".challenge-btn")) return
        openLevelsPage()
    })

    return div
}