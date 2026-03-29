import { renderHabits } from "./habits.js"
import { renderWeek } from "./calendar.js"
import { initNavigation } from "./navigation.js"
import { renderChatUser, renderReferrals } from "./chat.js"
import { initProfileModal } from "./components/profileModal.js"
import { initUserProfileModal, openUserProfile } from "./components/userProfileModal.js"

const tg = window.Telegram.WebApp
tg.expand()
window.currentUserId = tg.initDataUnsafe?.user?.id

const initData = tg.initData

// ==========================
// LOAD DASHBOARD DATA
// ==========================

async function loadDashboard(){

try{

const [userRes, habitsRes, refRes] = await Promise.all([

fetch("/api/user",{
method:"POST",
headers:{ "Content-Type":"application/json"},
body:JSON.stringify({ initData })
}),

fetch("/api/habits",{
method:"POST",
headers:{ "Content-Type":"application/json"},
body:JSON.stringify({ initData })
}),

fetch("/api/referrals",{
method:"POST",
headers:{ "Content-Type":"application/json"},
body:JSON.stringify({ initData })
})

])

const user = await userRes.json()
window.currentUserAvatar = user.avatar || "avatar_1.png"

const habits = await habitsRes.json()
const referrals = await refRes.json()

// ==========================
// USER
// ==========================

renderUser(user)

// ==========================
// HABITS
// ==========================

renderHabits(habits.habits)

// ==========================
// CHAT
// ==========================

renderChatUser(user.xp_current)
renderReferrals(referrals.referrals)

}catch(err){

console.error("Dashboard load error:", err)

}

}

// ==========================
// ОБЬЯСНЕНИЕ К НАЖАТИЮ НА ЛИГУ
// ==========================
function openLeagueInfo(){

    // если уже есть — не создаем второй раз
    if(document.querySelector(".league-modal")) return

    const modal = document.createElement("div")
    modal.className = "league-modal"

    modal.innerHTML = `
        <div class="league-overlay"></div>

        <div class="league-content">

            <div class="league-close">✕</div>

            <div class="league-title">
                Как повышать ранг
            </div>

            <div class="league-text">
                ⚡ Собирай XP — подтверждая привычки<br><br>
                ⭐ Получай звезды — за завершение челленджей<br><br>
                🚀 Повышай уровень и двигайся по лигам
            </div>

        </div>
    `

    document.body.appendChild(modal)

    // закрытие
    modal.querySelector(".league-close").onclick = () => modal.remove()
    modal.querySelector(".league-overlay").onclick = () => modal.remove()
}

// ==========================
// USER RENDER
// ==========================

function renderUser(user){

window.refLink = user.ref_link || ""

// имя
const nameEl = document.getElementById("player-name")
if(nameEl){
nameEl.innerText = user.nickname || "Player"
}

// XP текст
const xpText = document.getElementById("xp-text")
if(xpText){
xpText.innerText = `${user.xp_current} / ${user.xp_next}`
}

// STARS текст
const starsText = document.getElementById("stars-text")

if(starsText){
    starsText.innerText = `${user.stars_current} / ${user.stars_next}`
}

// XP прогресс
const xpFill = document.getElementById("xp-fill")
if(xpFill){
xpFill.style.width = (user.xp_percent || 0) + "%"
}

// аватар
const avatar = document.getElementById("player-avatar")
if(avatar){
    avatar.src = `img/avatar/${user.avatar || "avatar_1.png"}`
}

// ==========================
// LEAGUE
// ==========================

const leagueText = document.getElementById("league-text")
const leagueIcon = document.getElementById("league-icon")

if(leagueText){
    leagueText.innerText = user.league?.name || "—"
}

if(leagueIcon){
    leagueIcon.src = user.league?.icon || ""
    leagueIcon.onclick = openLeagueInfo
}

}


// ==========================
// Ловим клики (ОБЩИЙ обработчик)
// ==========================

document.addEventListener("click", (e)=>{

    const el = e.target.closest("[data-user-id]")
    if(!el) return

    const userId = el.dataset.userId
    if(!userId) return

    if(Number(userId) === Number(window.currentUserId)){
        return
    }

    openUserProfile(userId)

})

// ==========================
// INIT APP
// ==========================

function init(){

renderWeek()
initNavigation()
initProfileModal()
initUserProfileModal()
loadDashboard()

}

init()