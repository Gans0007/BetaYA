import { acceptChallenge } from "../api.js"

const difficultyTexts = {
    1: "Подходит для новичков",
    2: "Для тех, кто готов к дисциплине",
    3: "Только для самых дисциплинированных"
}

const conditionTexts = {
    1: "Формируй привычку постепенно",
    2: "При 2 пропущенных днях челлендж аннулируется",
    3: "Любой пропущенный день аннулирует челлендж"
}

export function openChallengeBook(data){

    if(document.getElementById("challenge-book")) return

    const overlay = document.createElement("div")
    overlay.id = "challenge-book"

    const difficulty = Number(data.difficulty) || 1

    const difficultyText = difficultyTexts[difficulty] || difficultyTexts[1]
    const conditionText = conditionTexts[difficulty] || conditionTexts[1]

    const desc =
        data.description?.[data.difficulty] ||
        data.description?.[String(data.difficulty)] ||
        data.description?.[1] ||
        "Описание скоро будет"

    overlay.innerHTML = `
        <div class="sheet-backdrop"></div>

        <div class="sheet">
            <div class="sheet-handle"></div>

            <div class="sheet-content">

                <div class="sheet-title">${data.title}</div>

                <div class="sheet-meta">

                    <div class="meta-item meta-level">
                        <div class="meta-icon meta-icon-level">
                            <img src="/img/nodes/hard_level.png"/>
                        </div>

                        <div class="meta-text">
                            <div class="meta-main">
                                Сложность: <span class="value">${difficulty} / 3</span>
                            </div>
                            <div class="meta-sub">${difficultyText}</div>
                        </div>
                    </div>

                    <div class="meta-item meta-days">
                        <div class="meta-icon meta-icon-days">
                            <img src="/img/nodes/level_days.png"/>
                        </div>

                        <div class="meta-text">
                            <div class="meta-main">
                                Длительность: <span class="value">${data.days} дней</span>
                            </div>
                            <div class="meta-sub">${conditionText}</div>
                        </div>
                    </div>

                </div>

                <div class="sheet-desc">
                    ${desc}
                </div>

                <button class="sheet-btn">
                    ${data.isActive ? "✅ Уже активен" : "🚀 Принять вызов"}
                </button>

            </div>
        </div>
    `

    document.body.appendChild(overlay)

    setTimeout(()=>{
        overlay.classList.add("active")
    }, 10)

    const btn = overlay.querySelector(".sheet-btn")

    if(data.isActive){
        btn.disabled = true
    }else{
        btn.onclick = async () => {

            btn.innerText = "⏳ Создание..."

            const res = await acceptChallenge(
                window.initData,
                data.id
            )

            if(res?.ok){
                btn.innerText = "✅ Активирован"

                setTimeout(()=>{
                    close()

                    window.renderChallenges()

                    if(window.renderDashboard){
                        window.renderDashboard()
                    }

                }, 500)

            }else if(res?.error === "already_active"){
                btn.innerText = "✅ Уже активен"
                btn.disabled = true
            }else{
                btn.innerText = "❌ Ошибка"
            }
        }
    }

    function close(){
        overlay.classList.remove("active")
        setTimeout(()=> overlay.remove(), 250)
    }

    overlay.querySelector(".sheet-backdrop").onclick = close
}