export function renderChallengeCard(data){

    const div = document.createElement("div")
    div.className = "challenge-card"

    div.innerHTML = `
        <div class="challenge-card-left">
            <div class="challenge-module">
                МОДУЛЬ ${data.module}, РАЗДЕЛ ${data.section}
            </div>

            <div class="challenge-title">
                ${data.title}
            </div>
        </div>

        <div class="challenge-card-right">
            📘
        </div>
    `

    return div
}