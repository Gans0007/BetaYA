const userId = window.Telegram.WebApp.initDataUnsafe.user.id

export function openSettingsModal(){

if(document.querySelector(".settings-overlay")){
    const overlay = document.querySelector(".settings-overlay")
    overlay.classList.remove("hidden")
    setTimeout(() => overlay.classList.add("active"), 10)
    return
}

const overlay = document.createElement("div")
overlay.className = "settings-overlay hidden"

overlay.innerHTML = `

<div class="settings-modal">

    <div class="settings-header">
        <div class="settings-title">⚙️ Настройки</div>
        <div class="settings-close">✕</div>
    </div>

    <div class="settings-content">

        <div class="settings-block">
            <div class="settings-label">Тон уведомлений</div>
            <div class="settings-buttons">
                <button data-tone="friend">🤝</button>
                <button data-tone="gamer">🎮</button>
                <button data-tone="spartan">⚔️</button>
            </div>
        </div>

        <div class="settings-block">
            <div class="settings-label">Регион</div>
            <div class="settings-buttons">
                <button data-tz="Europe/Kyiv">🇺🇦</button>
                <button data-tz="Europe/Berlin">🇩🇪</button>
                <button data-tz="Europe/Warsaw">🇵🇱</button>
                <button data-tz="America/Vancouver">🇺🇸</button>
                <button data-tz="Europe/Moscow">🇷🇺</button>
            </div>
        </div>

        <div class="settings-block">
            <div class="settings-label">Публикация медиа</div>
            <button id="toggle-media">Переключить</button>
        </div>

    </div>

</div>

`

document.body.appendChild(overlay)

// =========================
// ОТКРЫТИЕ
// =========================

setTimeout(() => overlay.classList.add("active"), 10)

// =========================
// ЗАКРЫТИЕ
// =========================

const closeBtn = overlay.querySelector(".settings-close")

closeBtn.addEventListener("click", closeModal)

overlay.addEventListener("click", (e)=>{
    if(e.target === overlay){
        closeModal()
    }
})

function closeModal(){

    overlay.classList.remove("active")

    setTimeout(()=>{
        overlay.remove()   // 💥 ВОТ ЭТО ГЛАВНОЕ
    }, 250)

}

// =========================
// КНОПКИ (заглушки пока)
// =========================

overlay.querySelectorAll("[data-tone]").forEach(btn=>{

btn.addEventListener("click", async ()=>{

const tone = btn.dataset.tone

await fetch("/api/settings/tone", {
    method:"POST",
    headers:{"Content-Type":"application/json"},
    body: JSON.stringify({
        user_id: userId,
        tone: tone
    })
})

showToast("Тон обновлён")

})

})



overlay.querySelectorAll("[data-tz]").forEach(btn=>{

btn.addEventListener("click", async ()=>{

const tz = btn.dataset.tz

await fetch("/api/settings/timezone", {
    method:"POST",
    headers:{"Content-Type":"application/json"},
    body: JSON.stringify({
        user_id: userId,
        timezone: tz
    })
})

showToast("Регион обновлён")

})

})




toggleBtn.addEventListener("click", async ()=>{

await fetch("/api/settings/toggle_media", {
    method:"POST",
    headers:{"Content-Type":"application/json"},
    body: JSON.stringify({
        user_id: userId
    })
})

showToast("Настройка обновлена")

})

}


// =========================
// TOAST (reuse)
// =========================

function showToast(text){

let toast = document.querySelector(".custom-toast")

if(!toast){
toast = document.createElement("div")
toast.className = "custom-toast"
document.body.appendChild(toast)
}

toast.innerText = text

toast.classList.add("show")

setTimeout(()=>{
toast.classList.remove("show")
},2000)

}