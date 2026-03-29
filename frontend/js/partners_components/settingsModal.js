const userId = window.Telegram.WebApp.initDataUnsafe.user.id

export function openSettingsModal(){

const existing = document.querySelector(".settings-overlay")

if(existing){
    existing.classList.remove("hidden")
    setTimeout(() => existing.classList.add("active"), 10)
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
            <button id="toggle-media">Загрузка...</button>
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
    setTimeout(()=> overlay.remove(), 250)
}

// =========================
// КНОПКИ
// =========================

const toneButtons = overlay.querySelectorAll("[data-tone]")
const tzButtons = overlay.querySelectorAll("[data-tz]")
const toggleBtn = overlay.querySelector("#toggle-media")

// =========================
// ТОН
// =========================

toneButtons.forEach(btn=>{
btn.addEventListener("click", async ()=>{

const tone = btn.dataset.tone

await fetch("/settings/tone", {
    method:"POST",
    headers:{"Content-Type":"application/json"},
    body: JSON.stringify({
        user_id: userId,
        tone: tone
    })
})

toneButtons.forEach(b=>b.classList.remove("active"))
btn.classList.add("active")

showToast("Тон обновлён")

})
})

// =========================
// TIMEZONE
// =========================

tzButtons.forEach(btn=>{
btn.addEventListener("click", async ()=>{

const tz = btn.dataset.tz

await fetch("/settings/timezone", {
    method:"POST",
    headers:{"Content-Type":"application/json"},
    body: JSON.stringify({
        user_id: userId,
        timezone: tz
    })
})

tzButtons.forEach(b=>b.classList.remove("active"))
btn.classList.add("active")

showToast("Регион обновлён")

})
})

// =========================
// TOGGLE MEDIA
// =========================

toggleBtn.addEventListener("click", async ()=>{

await fetch("/settings/toggle_media", {
    method:"POST",
    headers:{"Content-Type":"application/json"},
    body: JSON.stringify({
        user_id: userId
    })
})

toggleBtn.classList.toggle("active")

if(toggleBtn.classList.contains("active")){
    toggleBtn.innerText = "🟢 Включено"
}else{
    toggleBtn.innerText = "⚪ Выключено"
}

showToast("Настройка обновлена")

})

// =========================
// ЗАГРУЗКА НАСТРОЕК
// =========================

loadSettings(overlay)

}


// =========================
// LOAD SETTINGS
// =========================

async function loadSettings(overlay){

try{

const res = await fetch("/settings", {
    method:"POST",
    headers:{"Content-Type":"application/json"},
    body: JSON.stringify({
        user_id: userId
    })
})

const data = await res.json()

if(!data.ok) return

// ТОН
overlay.querySelectorAll("[data-tone]").forEach(btn=>{
    if(btn.dataset.tone === data.tone){
        btn.classList.add("active")
    }
})

// TIMEZONE
overlay.querySelectorAll("[data-tz]").forEach(btn=>{
    if(btn.dataset.tz === data.timezone){
        btn.classList.add("active")
    }
})

// MEDIA
const toggleBtn = overlay.querySelector("#toggle-media")

if(data.share_on){
    toggleBtn.classList.add("active")
    toggleBtn.innerText = "🟢 Включено"
}else{
    toggleBtn.innerText = "⚪ Выключено"
}

}catch(e){
console.error("SETTINGS LOAD ERROR", e)
}

}


// =========================
// TOAST
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