import { acceptChallenge } from "../api.js"

export function openChallengeBook(data){

    if(document.getElementById("challenge-book")) return

    const overlay = document.createElement("div")
    overlay.id = "challenge-book"

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
                        <img src="/img/nodes/hard_level.png"/>
                        <span>Сложность: ${data.difficulty} / 3</span>
                    </div>

                    <div class="meta-item meta-days">
                        <img src="/img/nodes/level_days.png"/>
                        <span>Длительность: ${data.days} дней </span>
                    </div>

                </div>

                <div class="sheet-desc">
                    ${desc}
                </div>

                <button class="sheet-btn">
                    ${data.isActive ? "✅ Уже активен" : "🚀 Взять челлендж"}
                </button>

            </div>
        </div>
    `

    document.body.appendChild(overlay)

    const sheet = overlay.querySelector(".sheet")

    // 🔥 запуск анимации
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

                    // обновляем челленджи
                    window.renderChallenges()

                    // 🔥 обновляем привычки
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