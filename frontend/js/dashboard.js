import {loadHabitsDashboard} from "./habits.js"
import {renderWeek} from "./calendar.js"
import {initNavigation} from "./navigation.js"
import {renderChatUser} from "./chat.js"

const tg = window.Telegram.WebApp
tg.expand()

const initData = tg.initData

async function loadDashboard(){

const [userRes, habitsRes, refRes, leaderboardRes] = await Promise.all([

fetch("/api/user",{
method:"POST",
headers:{ "Content-Type":"application/json"},
body:JSON.stringify({initData})
}),

fetch("/api/habits",{
method:"POST",
headers:{ "Content-Type":"application/json"},
body:JSON.stringify({initData})
}),

fetch("/api/referrals",{
method:"POST",
headers:{ "Content-Type":"application/json"},
body:JSON.stringify({initData})
}),

fetch("/api/leaderboard",{
method:"POST",
headers:{ "Content-Type":"application/json"},
body:JSON.stringify({initData})
})

])

const user = await userRes.json()
const habits = await habitsRes.json()
const referrals = await refRes.json()
const leaderboard = await leaderboardRes.json()

/* USER */

document.getElementById("player-name").innerText = user.nickname

document.getElementById("xp-text").innerText =
`${user.xp_current} / ${user.xp_next}`

document.getElementById("xp-fill").style.width =
user.xp_percent + "%"

/* HABITS */

loadHabitsDashboard(habits.habits)

/* CHAT USERS */

renderChatUser(referrals.referrals)

}

renderWeek()
loadDashboard()

initNavigation()