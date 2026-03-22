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
// USER RENDER
// ==========================

function renderUser(user){

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