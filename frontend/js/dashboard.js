import {getDashboard} from "./api.js"
import {renderHabits} from "./habits.js"
import {renderWeek} from "./calendar.js"
import {initNavigation} from "./navigation.js"

const tg = window.Telegram.WebApp
tg.expand()

const initData = tg.initData

async function loadDashboard(){

const data = await getDashboard(initData)

renderHabits(data.habits)

}

renderWeek()
loadDashboard()
initNavigation()

/* =========================
LOAD DASHBOARD
========================= */

export async function loadHabitsDashboard(initData){

const data = await getDashboard(initData)

/* ======================
XP BAR
====================== */

const xpText = document.getElementById("xp-text")
const xpFill = document.getElementById("xp-fill")

if(xpText && xpFill){

xpText.innerText = data.xp_current + " / " + data.xp_next

xpFill.style.width = data.xp_percent + "%"

}

/* ======================
LEAGUE
====================== */

const leagueText = document.getElementById("league-name")

if(leagueText){
leagueText.innerText = data.league
}

/* ======================
HABITS
====================== */

renderHabits(data.habits)

}