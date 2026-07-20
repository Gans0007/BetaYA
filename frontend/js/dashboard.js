import { renderHabits } from "./habits_components/habits.js"
import { renderWeek } from "./habits_components/calendar.js"
import { initNavigation } from "./navigation.js"
import { renderChatUser, renderReferrals } from "./chat.js"
import { initProfileModal } from "./components/profileModal.js"
import { initUserProfileModal, openUserProfile } from "./components/userProfileModal.js"
import { renderHeader } from "./header_components/header.js"

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


        // ==========================
        // USER
        // ==========================
        renderHeader(user)

        // инициализация модалки после появления аватарки
        initProfileModal()

        const habits = await habitsRes.json()
        const referrals = await refRes.json()


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

// 🔥 ВАЖНО: ДЕЛАЕМ ГЛОБАЛЬНОЙ
window.renderDashboard = loadDashboard

// ==========================
// ЛИГА (инфо окно)
// ==========================

function openLeagueInfo(){

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

    modal.querySelector(".league-close").onclick = () => modal.remove()
    modal.querySelector(".league-overlay").onclick = () => modal.remove()
}

window.openLeagueInfo = openLeagueInfo

// ==========================
// USER CLICK HANDLER
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
    initUserProfileModal()
    loadDashboard()
}

init()