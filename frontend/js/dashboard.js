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

