import {loadHabitsDashboard} from "./habits.js"
import {renderWeek} from "./calendar.js"
import {initNavigation} from "./navigation.js"

const tg = window.Telegram.WebApp
tg.expand()

const initData = tg.initData

renderWeek()

loadHabitsDashboard(initData)

initNavigation()