import { acceptChallenge } from "../api.js"

export function openChallengeBook(data){

    if(document.getElementById("challenge-book")) return

    const overlay = document.createElement("div")
    overlay.id = "challenge-book"
    overlay.className = "levels-overlay active"

    const desc =
        data.description?.[data.difficulty] ||
        data.description?.[String(data.difficulty)] ||
        data.description?.[1] ||
        "Описание скоро будет"

    overlay.innerHTML = `
        <div class="levels-modal">

            <div class="levels-header">
                <div class="levels-title">${data.title}</div>
                <div class="levels-close">✕</div>
            </div>

            <div class="levels-content">

                <div class="book-meta">
                    <div>📊 Сложность: ${data.difficulty} / 3</div>
                    <div>📅 ${data.days} дней</div>
                </div>

                <div class="book-desc">
                    ${desc}
                </div>

                <button class="take-btn">
                    ${data.isActive ? "✅ Уже активен" : "🚀 Взять челлендж"}
                </button>

            </div>

        </div>
    `

    document.body.appendChild(overlay)

    const btn = overlay.querySelector(".take-btn")

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
                    overlay.remove()

                    window.renderChallenges()

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
        overlay.remove()
    }

    overlay.querySelector(".levels-close").onclick = close

    overlay.addEventListener("click", (e)=>{
        if(e.target === overlay) close()
    })
}